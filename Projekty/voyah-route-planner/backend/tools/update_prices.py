"""Denní kontrola ceníků (launchd na Macu): stáhne každý zdroj z ceniky.json, vytáhne z něj cenové údaje
(řádky s „Kč“) a porovná jejich otisk s minulým.

- beze změny  → zdroj i jeho položky dostanou dnešní datum ověření,
- změna       → položky zůstanou se starým datem a stavem „zdroj změněn — ověřit“ (ceny se samy nepřepisují),
                upozornění v macOS; nové ceny doplní člověk/Claude do ceniky_zdroj.py,
- nedostupný  → nic se nemění (údaje časem zestárnou → v aplikaci „neověřeno / staré“).

Pak: kopie do sestavené aplikace (dist) a nasazení na Netlify, je-li v ~/.config/voyah-route-planner/.env
NETLIFY_AUTH_TOKEN a NETLIFY_SITE_ID (scripts/deploy-netlify.sh). Log: ~/Library/Logs/voyah-ceniky.log
Spuštění: python3 backend/tools/update_prices.py [--bez-nasazeni]
Z launchd (bez přístupu do iCloud Drive) běží kopie skriptu nad nasazovanou složkou:
  python3 ~/.local/share/voyah-route-planner/bin/update_prices.py --data ~/voyah-netlify/data/ceniky.json --deploy-dir ~/voyah-netlify
"""
import datetime as dt
import hashlib
import io
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV = Path.home() / ".config/voyah-route-planner/.env"
LATEST = Path.home() / ".local/share/voyah-route-planner/ceniky-latest.json"   # poslední stav kontroly (mimo iCloud)


def arg(name: str):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else None


DATA = Path(arg("--data") or ROOT / "frontend/public/data/ceniky.json").expanduser()
DEPLOY_DIR = arg("--deploy-dir")
UA = "Mozilla/5.0 (Macintosh) voyah-route-planner/1.0 (osobni kontrola ceniku)"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.read()
    except Exception:          # LibreSSL v systémovém Pythonu 3.9 → záloha přes curl
        return subprocess.run(["curl", "-sfL", "-A", UA, "--max-time", "40", url], check=True, capture_output=True).stdout


def text_of(raw: bytes, kind: str) -> str:
    if kind == "pdf" or raw[:4] == b"%PDF":
        import pypdf
        return "\n".join(p.extract_text() or "" for p in pypdf.PdfReader(io.BytesIO(raw)).pages)
    t = raw.decode("utf-8", "ignore")
    t = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", t)
    import html
    return html.unescape(re.sub(r"<[^>]+>", " ", t))


def fingerprint(text: str) -> str:
    """Otisk jen cenových údajů (čísla u „Kč“, minuty, kW) — změna vzhledu stránky nevadí."""
    t = re.sub(r"\s+", " ", text)
    facts = sorted(set(re.findall(r"\d+(?:[.,]\d+)?\s*(?:Kč(?:/kWh|/min)?|minut\w*|kW|hod\w*)", t)))
    return hashlib.sha256("|".join(facts).encode()).hexdigest()[:16] if facts else ""


def notify(msg: str):
    subprocess.run(["osascript", "-e", f'display notification "{msg}" with title "Voyah trasy – ceníky"'], check=False)


def main():
    today = dt.date.today().isoformat()
    data = json.loads(DATA.read_text())
    changed = []
    for sid, src in data["sources"].items():
        try:
            fp = fingerprint(text_of(fetch(src["url"]), src.get("kind", "html")))
        except Exception as e:
            print(f"{today} {sid}: nedostupné ({e})")
            continue
        if not fp:
            print(f"{today} {sid}: v dokumentu nenalezeny ceny — beze změny")
            continue
        if src.get("fingerprint") in (None, fp):
            src.update(fingerprint=fp, checked=today)
            for en in data["entries"]:
                if en["source"] == sid and en["status"] in ("ověřeno", "zdroj změněn — ověřit") and src.get("changed") is None:
                    en["verified"] = today
            print(f"{today} {sid}: beze změny")
        else:
            src.update(changed=today, new_fingerprint=fp)
            for en in data["entries"]:
                if en["source"] == sid and en["status"] == "ověřeno":
                    en["status"] = "zdroj změněn — ověřit"
            changed.append(src["name"])
            print(f"{today} {sid}: ZMĚNA zdroje → ověřit")
    data["checked"] = today
    text = json.dumps(data, ensure_ascii=False, indent=1)
    DATA.write_text(text)
    LATEST.parent.mkdir(parents=True, exist_ok=True)
    LATEST.write_text(text)
    if changed:
        notify(f"Změnil se ceník: {', '.join(changed)[:180]}. Požádejte Clauda o aktualizaci cen.")
    if "--bez-nasazeni" in sys.argv:
        return
    if DEPLOY_DIR:
        deploy_dir(Path(DEPLOY_DIR).expanduser())
    else:
        subprocess.run([str(ROOT / "scripts/deploy-netlify.sh")], check=False)


def env(name: str) -> str:
    for line in ENV.read_text().splitlines() if ENV.exists() else []:
        if line.startswith(name + "="):
            return line.split("=", 1)[1].strip()
    return ""


def deploy_dir(folder: Path):
    """Nasazení hotové složky (jen se změnil ceniky.json → bez nového sestavení)."""
    token, site = env("NETLIFY_AUTH_TOKEN"), env("NETLIFY_SITE_ID")
    if not (token and site):
        print("Netlify token není nastaven — ceník aktualizován jen lokálně")
        return
    r = subprocess.run(["npx", "-y", "netlify-cli@17.38.1", "deploy", "--prod", "--dir", str(folder), "--site", site,
                        "--message", f"ceníky {dt.date.today()}"], env={**__import__("os").environ, "NETLIFY_AUTH_TOKEN": token},
                       capture_output=True, text=True)
    print("nasazeno" if r.returncode == 0 else f"nasazení selhalo: {r.stderr[-300:]}")


if __name__ == "__main__":
    main()
