#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sekce „Pokyny k instalaci“ na pracovní stránce ../kuncice/index.html (artefakt S9apdYbzv8x7RiMdabc8xK).

- vytiskne každé schéma (SVG) do samostatného PDF  -> ../kuncice/pdf/<kód>.pdf
- zkopíruje čtyři PDF pokynů z ../pokyny/            -> ../kuncice/pdf/
- vytvoří náhledy schémat                            -> ../kuncice/nahledy/<kód>.jpg
- vloží sekci mezi <!-- POKYNY:START --> a <!-- POKYNY:END --> a tlačítka stažení (capability downloads)
- vytiskne celou stránku do PDF                      -> ../kuncice/pdf/REO-popis-instalace-Kuncice.pdf
Před spuštěním: vygenerovat schémata a pokyny (build_pokyny.py).
Spuštění:  python3 reo-schemata-zapojeni/src/build_rozcestnik.py
"""
import html, os, re, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
PAGE = os.path.join(ROOT, "kuncice", "index.html")
PDF_DIR = os.path.join(ROOT, "kuncice", "pdf")
THUMB_DIR = os.path.join(ROOT, "kuncice", "nahledy")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PAGE_PDF = "REO-popis-instalace-Kuncice.pdf"
e = html.escape

GUIDES = [
    ("V1", "Vytápění s AKU 100 l", "bez hydroboxu", "REO-pokyny-instalace-V1-AKU.pdf", "https://claude.ai/artifact/B1kNm4rR3A56NZ8vBEAeGU"),
    ("V2", "Vytápění s AKU 100 l a ohřev TUV", "bez hydroboxu", "REO-pokyny-instalace-V2-AKU-TUV.pdf", "https://claude.ai/artifact/DC42DpVfQhRrkwxdTvX1xN"),
    ("H1", "Vytápění s hydroboxem a AKU 100 l", "s hydroboxem", "REO-pokyny-instalace-H1-hydrobox-AKU.pdf", "https://claude.ai/artifact/5xTBM8VtwMfQqVpwBtn4wE"),
    ("H2", "Hydrobox, AKU 100 l a ohřev TUV", "s hydroboxem", "REO-pokyny-instalace-H2-hydrobox-AKU-TUV.pdf", "https://claude.ai/artifact/4p9rJAKaMWSNYJ7jrqTTJW"),
]

# (skupina, kód, název, zdrojové SVG)
SCHEMAS = [
    ("Bez hydroboxu", "REO-SCH-K1", "Hydraulika — pouze vytápění s AKU", "schema-kuncice-aku100.svg"),
    ("Bez hydroboxu", "REO-SCH-K2", "Hydraulika — AKU a ohřev TUV", "schema-kuncice-tuv.svg"),
    ("Bez hydroboxu", "REO-SCH-K1-E", "Elektro — pouze vytápění s AKU", "schema-kuncice-elektro.svg"),
    ("Bez hydroboxu", "REO-SCH-K2-E", "Elektro — AKU a ohřev TUV", "schema-kuncice-elektro-tuv.svg"),
    ("S hydroboxem", "REO-SCH-H1", "Hydraulika — hydrobox a AKU", "schema-hydrobox-aku.svg"),
    ("S hydroboxem", "REO-SCH-H2", "Hydraulika — hydrobox, AKU a TUV", "schema-hydrobox-tuv.svg"),
    ("S hydroboxem", "REO-SCH-H1-E", "Elektro — hydrobox a AKU", "schema-hydrobox-elektro.svg"),
    ("S hydroboxem", "REO-SCH-H2-E", "Elektro — hydrobox, AKU a TUV", "schema-hydrobox-elektro-tuv.svg"),
    ("Společné", "REO-SCH-K1-P", "Betonová patka venkovní jednotky", "schema-kuncice-patka.svg"),
]

CSS = """
/* POKYNY:CSS */
.guides { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; }
.guide { background:var(--surface); border:1px solid var(--line); border-radius:6px; padding:16px 18px; display:grid; gap:8px; min-width:0; }
.guide .code { font:700 12.5px/1 var(--display); letter-spacing:.1em; color:var(--accent); }
.guide h3 { font-size:17px; }
.guide .sub { color:var(--muted); font-size:14px; }
.acts { display:flex; flex-wrap:wrap; gap:8px 14px; align-items:center; }
.dlb { font:700 13.5px/1 var(--display); color:#fff; background:var(--accent); border:0; border-radius:6px; padding:9px 14px; cursor:pointer; }
.dlb:hover { filter:brightness(1.08); } .dlb:focus-visible { outline:3px solid var(--accent-soft); outline-offset:2px; }
.dlb:disabled { opacity:.6; cursor:progress; }
.acts a { color:var(--accent); font-weight:600; font-size:14.5px; }
.sgrid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; }
.scard { background:var(--surface); border:1px solid var(--line); border-radius:6px; overflow:hidden; display:grid; grid-template-rows:auto 1fr; min-width:0; }
.scard img { display:block; width:100%; aspect-ratio:14/10; object-fit:cover; object-position:top; background:#fff; border-bottom:1px solid var(--line); }
.scard .b { padding:12px 14px; display:grid; gap:8px; align-content:start; }
.scard .code { font:700 12px/1 var(--display); letter-spacing:.08em; color:var(--muted); }
.sgroup { font:700 13px/1 var(--display); letter-spacing:.1em; text-transform:uppercase; color:var(--muted); margin-top:6px; }
.dlstat { color:var(--muted); font-size:14px; min-height:1.2em; }
.nodl .dlb { display:none; }
@media (max-width:860px) { .sgrid { grid-template-columns:repeat(2,minmax(0,1fr)); } }
@media (max-width:620px) { .guides, .sgrid { grid-template-columns:1fr; } }
@media print { .dlb, .dlstat, .acts a { display:none !important; } .schema img { min-width:0 !important; } .schema { overflow:visible; border:0; }
  body { padding:0; font-size:11pt; } figure, .guide, .scard, .note, tr { break-inside:avoid; } }
/* POKYNY:CSS-END */
"""

JS = """<script>
(async () => {
  const stat = document.getElementById("dlstat");
  const dl = window.claude && window.claude.use ? await window.claude.use("downloads") : null;
  if (!dl) { document.body.classList.add("nodl"); return; }
  document.querySelectorAll(".dlb[data-file]").forEach(btn => {
    btn.addEventListener("click", async () => {
      btn.disabled = true; stat.textContent = "Připravuji " + btn.dataset.name + "…";
      try {
        const r = await fetch(btn.dataset.file);
        if (!r.ok) throw { code: "missing" };
        await dl.save({ filename: btn.dataset.name, data: await r.blob() });
        stat.textContent = "Uloženo: " + btn.dataset.name;
      } catch (err) {
        const c = err && err.code;
        stat.textContent = c === "declined" ? "Stažení zrušeno." : c === "rate_limited" ? "Chvíli počkejte a zkuste znovu." : "PDF se nepodařilo stáhnout.";
        if (c === "unavailable" || c === "not_granted") document.body.classList.add("nodl");
      } finally { btn.disabled = false; }
    });
  });
})();
</script>"""


def chrome_pdf(src_html, out_pdf):
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={out_pdf}",
                    "file://" + src_html], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def schema_pdfs():
    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(THUMB_DIR, exist_ok=True)
    tmp = os.path.join(PDF_DIR, "_wrap.html")
    for _, code, _, svg in SCHEMAS:
        src = os.path.join(ROOT, svg)
        vb = re.search(r'viewBox="0 0 (\d+) (\d+)"', open(src, encoding="utf-8").read(2000))
        w, h = int(vb.group(1)), int(vb.group(2))
        open(tmp, "w", encoding="utf-8").write(
            f'<!doctype html><meta charset="utf-8"><style>@page{{size:{w}px {h}px;margin:0}}html,body{{margin:0}}'
            f'img{{display:block;width:{w}px;height:{h}px}}</style><img src="file://{src}">')
        chrome_pdf(tmp, os.path.join(PDF_DIR, code + ".pdf"))
        png = src[:-4] + ".png"
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "78", "-Z", "640", png,
                        "--out", os.path.join(THUMB_DIR, code + ".jpg")], check=True, stdout=subprocess.DEVNULL)
    os.remove(tmp)
    for g in GUIDES:
        shutil.copyfile(os.path.join(ROOT, "pokyny", g[3]), os.path.join(PDF_DIR, g[3]))


def btn(file, name, label="Stáhnout PDF"):
    return f'<button type="button" class="dlb" data-file="pdf/{e(file)}" data-name="{e(name)}">{e(label)}</button>'


def section():
    out = ['<!-- POKYNY:START -->', '<section id="pokyny">', '  <span class="eyebrow">Pokyny k instalaci</span>',
           '  <h2>Pokyny k instalaci a schválená schémata</h2>',
           '  <p>Všechny dokumenty a schémata zapojení REO RH030–RH060 na jednom místě. Každý lze stáhnout jako PDF.</p>',
           '  <div class="acts">' + btn(PAGE_PDF, PAGE_PDF, "Stáhnout tuto stránku v PDF") + '</div>',
           '  <h3>Pokyny k instalaci</h3>', '  <div class="guides">']
    for code, title, sub, pdf, url in GUIDES:
        out.append(f'    <div class="guide"><span class="code">{e(code)} · {e(sub)}</span><h3>{e(title)}</h3>'
                   f'<span class="sub">patka, hydraulika, elektro 1F/3F, soupis, uvedení do provozu, první spuštění</span>'
                   f'<div class="acts">{btn(pdf, pdf)}<a href="{e(url)}" target="_blank" rel="noopener">Otevřít artefakt</a></div></div>')
    out.append('  </div>')
    out.append('  <h3>Schémata zapojení</h3>')
    group = None
    for g, code, title, _ in SCHEMAS:
        if g != group:
            if group is not None:
                out.append('  </div>')
            out.append(f'  <div class="sgroup">{e(g)}</div>')
            out.append('  <div class="sgrid">')
            group = g
        out.append(f'    <div class="scard"><img src="nahledy/{e(code)}.jpg" alt="Náhled schématu {e(code)}" loading="lazy">'
                   f'<div class="b"><span class="code">{e(code)}</span><strong>{e(title)}</strong>'
                   f'<div class="acts">{btn(code + ".pdf", code + ".pdf")}</div></div></div>')
    out += ['  </div>', '  <p class="dlstat" id="dlstat" role="status"></p>', '</section>', '<!-- POKYNY:END -->']
    return "\n".join(out)


def inject():
    s = open(PAGE, encoding="utf-8").read()
    s = re.sub(r"/\* POKYNY:CSS \*/.*?/\* POKYNY:CSS-END \*/\n", "", s, flags=re.S)
    s = s.replace("</style>", CSS.lstrip("\n") + "</style>", 1)
    block = section()
    if "<!-- POKYNY:START -->" in s:
        s = re.sub(r"<!-- POKYNY:START -->.*?<!-- POKYNY:END -->", lambda m: block, s, flags=re.S)
    else:
        s = s.replace("</header>", "</header>\n\n" + block, 1)
    s = re.sub(r"<script>\n\(async \(\) => \{\n  const stat = .*?</script>\n?", "", s, flags=re.S)
    s = s.replace("<footer>", JS + "\n\n<footer>", 1)
    open(PAGE, "w", encoding="utf-8").write(s)


if __name__ == "__main__":
    schema_pdfs()
    inject()
    chrome_pdf(PAGE, os.path.join(PDF_DIR, PAGE_PDF))
    print("hotovo:", PAGE)
    for f in sorted(os.listdir(PDF_DIR)):
        print("  pdf/" + f, os.path.getsize(os.path.join(PDF_DIR, f)) // 1024, "kB")
