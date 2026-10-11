#!/usr/bin/env python3
"""Zrcadlo pracovních složek z ~/Claude do repozitáře claude-podklady (jen texty).

Co dělá:
- zkopíruje textové soubory (md, html, py, json, csv, …) z vybraných složek,
- z PDF, Word, Excel a PowerPoint vytáhne text do souboru „<název>.txt“,
- vynechá fotky, videa, node_modules, .git a vše, co vypadá jako tajný údaj
  (.env, klíče, tokeny — kontroluje se název i obsah),
- smaže ze zrcadla soubory, které ve zdroji už nejsou,
- vytvoří README.md s přehledem a odešle změny na GitHub (git commit + push).

Spuštění:  python3 -I ~/Developer/ClaudeVoiceCZ/scripts/sync_podklady.py [--bez-push]
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

HOME = Path.home()
SRC_ROOT = HOME / "Claude"
MIRROR = HOME / "Developer" / "claude-podklady"
PDF2TXT = HOME / "Developer" / "ClaudeVoiceCZ" / "tools" / "bin" / "pdf2txt"
FOLDERS = ["Projekty", "REO", "banner-generator", "BD Michal Claude", "ThermaVera nabídky"]

TEXT_EXT = {".md", ".txt", ".html", ".htm", ".py", ".ts", ".js", ".mjs", ".css", ".json", ".csv",
            ".yaml", ".yml", ".toml", ".sh", ".swift", ".php", ".xml", ".plist", ".sql"}
EXTRACT_EXT = {".pdf", ".docx", ".doc", ".rtf", ".xlsx", ".pptx"}
SKIP_DIRS = {"node_modules", ".git", ".wrangler", "build", "DerivedData", "__pycache__", ".claude", "dist", "thermavera-web-dist"}
MAX_TEXT_BYTES = 1_000_000
# Názvy souborů, které nikdy nesmí ven
SECRET_NAME = re.compile(r"(^\.env)|(\.local$)|secret|credential|\.pem$|\.key$|\.p12$|app-token|Secrets\.xcconfig$", re.I)
# Vzory tajných údajů v obsahu (klíče Anthropic, Google, GitHub, OpenAI, AWS, privátní klíče)
SECRET_CONTENT = re.compile(
    r"sk-ant-[A-Za-z0-9]{3,}-[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{30,}|github_pat_[A-Za-z0-9_]{30,}|ghp_[A-Za-z0-9]{30,}"
    r"|sk-(proj-)?[A-Za-z0-9]{32,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----"
)

STATE_FILE = MIRROR / ".sync-state.json"


def log(msg):
    print(msg, flush=True)


def extract_pdf(p: Path) -> str:
    r = subprocess.run([str(PDF2TXT), str(p)], capture_output=True, timeout=120)
    return r.stdout.decode("utf-8", "replace")


def extract_textutil(p: Path) -> str:
    r = subprocess.run(["textutil", "-convert", "txt", "-stdout", str(p)], capture_output=True, timeout=120)
    return r.stdout.decode("utf-8", "replace")


def _xml_texts(data: bytes, tag: str) -> list:
    root = ET.fromstring(data)
    return [el.text for el in root.iter() if el.tag.endswith(tag) and el.text]


def extract_xlsx(p: Path) -> str:
    out = []
    with zipfile.ZipFile(p) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root:
                shared.append("".join(t.text or "" for t in si.iter() if t.tag.endswith("}t")))
        sheets = sorted(n for n in z.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml$", n))
        for name in sheets:
            out.append(f"--- list {name.split('/')[-1].replace('.xml', '')} ---")
            root = ET.fromstring(z.read(name))
            for row in root.iter():
                if not row.tag.endswith("}row"):
                    continue
                cells = []
                for c in row:
                    v = next((x.text for x in c if x.tag.endswith("}v")), None)
                    if v is None:
                        t = "".join(x.text or "" for x in c.iter() if x.tag.endswith("}t"))
                        v = t or None
                    elif c.get("t") == "s":
                        try:
                            v = shared[int(v)]
                        except (ValueError, IndexError):
                            pass
                    if v:
                        cells.append(v)
                if cells:
                    out.append(" | ".join(cells))
    return "\n".join(out)


def extract_pptx(p: Path) -> str:
    out = []
    with zipfile.ZipFile(p) as z:
        slides = sorted((n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)),
                        key=lambda n: int(re.findall(r"\d+", n)[-1]))
        for i, name in enumerate(slides, 1):
            texts = _xml_texts(z.read(name), "}t")
            if texts:
                out.append(f"--- snímek {i} ---\n" + "\n".join(texts))
    return "\n".join(out)


def extract(p: Path) -> str:
    ext = p.suffix.lower()
    if ext == ".pdf":
        return extract_pdf(p)
    if ext in (".docx", ".doc", ".rtf"):
        return extract_textutil(p)
    if ext == ".xlsx":
        return extract_xlsx(p)
    if ext == ".pptx":
        return extract_pptx(p)
    return ""


def fingerprint(p: Path) -> str:
    st = p.stat()
    return f"{st.st_size}:{int(st.st_mtime)}"


def main():
    push = "--bez-push" not in sys.argv
    if not (MIRROR / ".git").is_dir():
        sys.exit(f"Chybí repozitář {MIRROR} (git init).")
    state = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}
    new_state, wanted = {}, set()
    stats = {"text": 0, "extrahováno": 0, "přeskočeno (tajné)": 0, "přeskočeno (velké/prázdné)": 0, "chyba": 0}

    for folder in FOLDERS:
        src = SRC_ROOT / folder
        if not src.exists():
            sys.exit(f"❌ Složka {folder} není dostupná — synchronizace zastavena, nic se nemaže.")
        def walk_error(err):
            raise SystemExit(f"❌ Nelze číst {err.filename}: {err.strerror} — synchronizace zastavena, nic se nemaže.")

        try:
            next(os.scandir(src))
        except StopIteration:
            pass
        except OSError as e:
            sys.exit(f"❌ Nelze číst složku {folder}: {e} — synchronizace zastavena, nic se nemaže.")
        for dirpath, dirnames, filenames in os.walk(src, followlinks=True, onerror=walk_error):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.endswith(".nosync") and not d.startswith(".")]
            for fn in filenames:
                if fn.startswith(".") or fn.startswith("~$"):
                    continue
                p = Path(dirpath) / fn
                rel = p.relative_to(SRC_ROOT)
                ext = p.suffix.lower()
                if ext not in TEXT_EXT and ext not in EXTRACT_EXT:
                    continue
                if SECRET_NAME.search(fn):
                    stats["přeskočeno (tajné)"] += 1
                    continue
                target_rel = rel if ext in TEXT_EXT else rel.with_name(rel.name + ".txt")
                key = str(target_rel)
                fp = fingerprint(p)
                dst = MIRROR / target_rel
                if state.get(key) == fp and dst.exists():
                    new_state[key] = fp
                    wanted.add(key)
                    continue
                try:
                    if ext in TEXT_EXT:
                        if p.stat().st_size > MAX_TEXT_BYTES:
                            stats["přeskočeno (velké/prázdné)"] += 1
                            continue
                        content = p.read_text("utf-8", errors="replace")
                    else:
                        content = extract(p)
                        if len(content.strip()) < 20:
                            stats["přeskočeno (velké/prázdné)"] += 1
                            continue
                        content = f"[Text vytažený z {rel.name}]\n\n" + content
                        content = content[:MAX_TEXT_BYTES]
                except Exception as e:  # noqa: BLE001 — jeden vadný soubor nesmí zastavit synchronizaci
                    log(f"⚠️  {rel}: {e}")
                    stats["chyba"] += 1
                    continue
                if SECRET_CONTENT.search(content):
                    log(f"🔒 {rel}: obsahuje vzor klíče/tokenu — vynechávám")
                    stats["přeskočeno (tajné)"] += 1
                    continue
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text(content, "utf-8")
                new_state[key] = fp
                wanted.add(key)
                stats["text" if ext in TEXT_EXT else "extrahováno"] += 1

    # Pojistka: když by zmizela víc než čtvrtina zrcadla, jde spíš o chybu přístupu než o skutečné mazání.
    existing = [p for f in FOLDERS if (MIRROR / f).exists() for p in (MIRROR / f).rglob("*") if p.is_file()]
    to_remove = [p for p in existing if str(p.relative_to(MIRROR)) not in wanted]
    if existing and len(to_remove) > max(20, len(existing) // 4) and "--povolit-mazani" not in sys.argv:
        sys.exit(f"❌ Synchronizace by smazala {len(to_remove)} z {len(existing)} souborů — zastaveno pro jistotu. "
                 "Pokud je to záměr, spusťte s --povolit-mazani.")

    # Smazat ze zrcadla soubory, které ve zdroji už nejsou
    removed = 0
    for folder in FOLDERS:
        base = MIRROR / folder
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and str(p.relative_to(MIRROR)) not in wanted:
                p.unlink()
                removed += 1
    for p in sorted(MIRROR.rglob("*"), reverse=True):
        if p.is_dir() and ".git" not in p.parts and not any(p.iterdir()):
            p.rmdir()

    write_readme()
    STATE_FILE.write_text(json.dumps(new_state, ensure_ascii=False, indent=0))
    log("Souhrn: " + ", ".join(f"{k} {v}" for k, v in stats.items()) + f", smazáno {removed}")

    git = ["git", "-C", str(MIRROR)]
    subprocess.run(git + ["add", "-A"], check=True)
    if subprocess.run(git + ["diff", "--cached", "--quiet"]).returncode == 0:
        log("Beze změn.")
        return
    # Poslední pojistka: žádný tajný vzor ve stage
    staged = subprocess.run(git + ["diff", "--cached"], capture_output=True, text=True, errors="replace").stdout
    if SECRET_CONTENT.search(staged):
        subprocess.run(git + ["reset", "-q"])
        sys.exit("❌ Ve změnách byl nalezen vzor tajného údaje — nic neodesláno.")
    subprocess.run(git + ["commit", "-q", "-m", f"Synchronizace podkladů {datetime.now():%Y-%m-%d %H:%M}"], check=True)
    log("✓ Commit vytvořen.")
    if push:
        r = subprocess.run(git + ["push", "-q", "origin", "HEAD"], capture_output=True, text=True)
        log("✓ Odesláno na GitHub." if r.returncode == 0 else f"❌ Push selhal: {r.stderr.strip()[:300]}")


def write_readme():
    lines = ["# Podklady (zrcadlo ~/Claude)", "",
             "Automaticky generované textové zrcadlo pracovních složek z Macu pro hlasového asistenta.",
             "Obsahuje jen texty; z PDF, Wordu, Excelu a PowerPointu je vytažený text do souborů `*.txt`.",
             "Fotky, videa a tajné údaje se nezrcadlí. **Needitovat ručně** — přepíše se při další synchronizaci.", "",
             f"Poslední synchronizace: {datetime.now():%d. %m. %Y %H:%M}", "", "## Složky", ""]
    descr = {
        "Projekty": "repozitář Projekty — web ThermaVera, nabídky pro bytové domy, porovnání TČ, marketing, Claude Voice (rozcestník: Projekty/CLAUDE.md)",
        "REO": "značka REO HEATING — návody, datové listy, katalogy, letáky, web reoheating",
        "banner-generator": "generátor reklamních bannerů (ThermaVera / REO HEATING)",
        "BD Michal Claude": "podklady k bytovému domu Michal (PDF, smlouvy)",
        "ThermaVera nabídky": "nabídky ThermaVera (PDF, Word)",
    }
    for f in FOLDERS:
        if (MIRROR / f).exists():
            n = sum(1 for p in (MIRROR / f).rglob("*") if p.is_file())
            lines.append(f"- `{f}/` — {descr.get(f, '')} ({n} souborů)")
    (MIRROR / "README.md").write_text("\n".join(lines) + "\n", "utf-8")
    (MIRROR / "CLAUDE.md").write_text("Rozcestník: viz README.md. Projekty mají vlastní `Projekty/CLAUDE.md`.\n", "utf-8")


if __name__ == "__main__":
    main()
