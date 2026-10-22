#!/usr/bin/env python3
"""Build datových listů REO R290 (RH030/RH040/RH050/RH060).

Výstupy:
  print/<model>_REO-HEATING.html  – samostatná A4 stránka (2 strany), vše inline
  pdf/<model>_Heating_REO-HEATING.pdf – tisk přes headless Chrome
  index.html                      – artefakt: přepínač modelů, oba listy + štítek

Spuštění:  python3 build.py        (bez PDF: python3 build.py --no-pdf)
"""
import base64, json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700'
         '&family=Poppins:wght@500;600&display=swap" rel="stylesheet">')

def data_uri(p):
    mime = "image/svg+xml" if p.suffix == ".svg" else "image/png"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()

data_js = (SRC / "data.js").read_text()

# --- REO R290 Smart (RH06–RH16) + RHX20 Pro: výkonové mapy výrobce (../PW Helios/REO R290 Smart/data)
import math
SMART_JSON = json.load(open(ROOT.parent / "PW Helios" / "REO R290 Smart" / "data" / "vykonove-mapy.json"))
# klíč, název, zdroj mapy (1F/3F stejné velikosti mají shodnou mapu; RH14 3F zatím z RH14 1F),
# hluk L_WA / tlak 1 m (35/55 °C) dle EU 811/2013 a technického listu výrobce 10/2026
SMART = [
    ("RH06",  "RH06 1F",   "RH06 1F",   "smart", (52, 53, 38, 38)),
    ("RH08",  "RH08 3F",   "RH08 3F",   "smart", (50, 50, 35, 34)),
    ("RH10",  "RH10 3F",   "RH10 1F",   "smart", (54, 55, 39, 40)),
    ("RH12",  "RH12 3F",   "RH12 3F",   "smart", (55, 55, 40, 40)),
    ("RH14",  "RH14 3F",   "RH14 1F",   "smart", (56, 55, 41, 40)),
    ("RH16",  "RH16 3F",   "RH16 3F",   "smart", (55, 56, 39, 41)),
    ("RHX20", "RHX20 Pro", "RHX20 Pro", "com",   (50, 56, 35, 40)),
]

def _block(src, temps):
    rd = lambda v, d: [None if x is None else round(x, d) for x in v]
    return {w: {m.upper(): {"cap": rd(src[str(w)][m]["cap"], 2), "inp": rd(src[str(w)][m]["pin"], 2),
                            "cop": rd(src[str(w)][m]["cop"], 2)} for m in ("max", "min")} for w in temps}

def _axis(blocks, key, step, floor0=True):
    v = [x for b in blocks for w in b.values() for m in w.values() for x in m[key] if x is not None]
    lo = 0 if floor0 else math.floor(min(v) / step) * step
    return [lo, math.ceil(max(v) / step + 1e-9) * step, step]

extra = {}
for key, name, src_key, grp, (l35, l55, p35, p55) in SMART:
    h = SMART_JSON[src_key]["heating"]
    D, DHi = _block(h, [35, 45, 55]), _block(h, [60, 65, 70, 75])
    cmax = max(x for b in (D, DHi) for w in b.values() for m in w.values() for x in m["cap"] if x is not None)
    step = 1 if cmax <= 12 else 2 if cmax <= 24 else 5
    extra[key] = {"name": name, "erp": name, "grp": grp, "cls": ["A+++", "A+++"],
                  "label": f"label-{key}.png" if (SRC / f"assets/label-{key}.png").exists() else None,
                  "noise": {"lwa35": l35, "lwa55": l55, "lp35": p35, "lp55": p55, "label": l55},
                  "amb": h["amb"], "yCap": _axis([D], "cap", step), "yCop": _axis([D], "cop", 1, False),
                  "yCapHi": _axis([DHi], "cap", step), "yCopHi": _axis([DHi], "cop", 0.5, False),
                  "D": D, "DHi": DHi}
data_js += "\n// REO R290 Smart + RHX20 Pro (generováno build.py z výkonových map)\nObject.assign(MODELS, " + json.dumps(extra) + ");\n"
sheet_js = (SRC / "sheet.js").read_text()
compare_js = (SRC / "compare.js").read_text()
sheet_css = (SRC / "sheet.css").read_text()
models = [(k, n, n.replace(" ", "-")) for k, n in
          re.findall(r"^  (RH[A-Z0-9]+): \{ name:'([^']+)'", data_js, re.M)]
models += [(k, n, n.replace(" ", "-")) for k, n, *_ in SMART]

def assets_js(labels):
    return "const ASSETS = " + json.dumps({
        "logo": data_uri(SRC / "assets/logo-reo-heating.svg"),  # závazné logo od 22. 10. 2026 (../logo)
        # modely bez štítku (zatím nedodán výrobcem) se prostě přeskočí
        "labels": {f"label-{k}.png": data_uri(SRC / f"assets/label-{k}.png") for k in labels
                   if (SRC / f"assets/label-{k}.png").exists()},
    }) + ";"

# --- kontrola měřítek: žádná hodnota nesmí přesáhnout osu grafu (jinak by se křivka tiše ořízla)
CHECK_JS = """
%s
let bad = [];
for (const [key, M] of Object.entries(MODELS)) {
  const pages = [[M.D, [35,45,55], M.yCap, M.yCop || [1,7,1]]];
  if (M.DHi) pages.push([M.DHi, [60,65,70,75], M.yCapHi, M.yCopHi]);
  for (const [D, temps, yCap, yCop] of pages)
    for (const w of temps) for (const m of ['MAX','MIN'])
      for (const [k, ax] of [['cap', yCap], ['cop', yCop]]) {
        const v = D[w][m][k].filter(x => x != null);
        if (Math.min(...v) < ax[0] || Math.max(...v) > ax[1])
          bad.push(`${M.name} ${w}°C ${m} ${k}: ${Math.min(...v)}–${Math.max(...v)} mimo osu ${ax[0]}–${ax[1]}`);
      }
}
if (bad.length) { console.error(bad.join("\\n")); process.exit(1); }
"""
r = subprocess.run(["node", "-e", CHECK_JS % data_js], capture_output=True, text=True)
if r.returncode:
    sys.exit("Chybné měřítko grafu:\n" + r.stderr.strip())

# --- tiskové stránky + PDF
(ROOT / "print").mkdir(exist_ok=True)
(ROOT / "pdf").mkdir(exist_ok=True)
for key, name, slug in models:
    html = f"""<!-- {name} — datový list REO R290 (Heating + energetický štítek), A4. Generováno build.py -->
<meta charset="utf-8">
<title>{name} Heating — REO HEATING</title>
{FONTS}
<style>
@page {{ size: A4 portrait; margin: 0; }}
html,body {{ margin:0; padding:0; background:#fff; }}
{sheet_css}
.sheet .page {{ break-after: page; }}
</style>
<div class="sheet" id="sheet"></div>
<script>{data_js}
{sheet_js}
{assets_js([key])}
document.fonts.ready.then(() => renderSheet(document.getElementById('sheet'), '{key}', ASSETS));
</script>
"""
    out = ROOT / "print" / f"{slug}_REO-HEATING.html"
    out.write_text(html)
    if "--no-pdf" not in sys.argv:
        pdf = ROOT / "pdf" / f"{slug}_Heating_REO-HEATING.pdf"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--virtual-time-budget=8000", f"--print-to-pdf={pdf}", out.as_uri()],
                       check=True, capture_output=True)
        print("PDF ", pdf.name)

# --- srovnávací list (SCOP + hlučnost), 2 strany A4
CMP = "REO-R290-srovnani"
cmp_html = f"""<!-- Srovnání SCOP a hlučnosti REO R290, A4. Generováno build.py -->
<meta charset="utf-8">
<title>REO R290 — srovnání SCOP a hlučnosti | REO HEATING</title>
{FONTS}
<style>
@page {{ size: A4 portrait; margin: 0; }}
html,body {{ margin:0; padding:0; background:#fff; }}
{sheet_css}
.sheet .page {{ break-after: page; }}
</style>
<div class="sheet" id="sheet"></div>
<script>{data_js}
{compare_js}
{assets_js([])}
document.fonts.ready.then(() => renderCompare(document.getElementById('sheet'), ASSETS));
</script>
"""
cmp_out = ROOT / "print" / f"{CMP}_REO-HEATING.html"
cmp_out.write_text(cmp_html)
if "--no-pdf" not in sys.argv:
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=8000", f"--print-to-pdf={ROOT / 'pdf' / (CMP + '_REO-HEATING.pdf')}",
                    cmp_out.as_uri()], check=True, capture_output=True)
    print("PDF ", CMP + "_REO-HEATING.pdf")

# --- artefakt: PDF k tisku se publikují jako samostatné soubory artefaktu (pdf/…), stránka je stahuje fetch()
def pdfs_js():
    out = {}
    for key, name, slug in models + [("_cmp", "srovnání", "REO-R290-srovnani")]:
        f = ROOT / "pdf" / (f"{slug}_REO-HEATING.pdf" if key == "_cmp" else f"{slug}_Heating_REO-HEATING.pdf")
        if f.exists():
            out[key] = {"file": f.name, "path": "pdf/" + f.name, "size": f.stat().st_size}
    return "const PDFS = " + json.dumps(out) + ";"

tpl = (SRC / "index.template.html").read_text()
index = (tpl.replace("/*SHEET_CSS*/", sheet_css)
            .replace("/*DATA_JS*/", data_js)
            .replace("/*SHEET_JS*/", sheet_js)
            .replace("/*ASSETS_JS*/", assets_js([k for k, _, _ in models]))
            .replace("/*PDFS_JS*/", pdfs_js()))
# návod k instalaci a obsluze (publikuje se jako samostatný soubor artefaktu navody/…)
MAN = ROOT.parent / "PW R290" / "RH030-RH060 - REO HEATING" / "RH030-RH060-navod-CZ_REO-HEATING.pdf"
(ROOT / "navody").mkdir(exist_ok=True)
if MAN.exists():
    (ROOT / "navody" / MAN.name).write_bytes(MAN.read_bytes())
    index = index.replace("/*MAN_SIZE*/", f"{MAN.stat().st_size/1e6:.1f} MB".replace(".", ","))
# prezentace RHX20 Pro / RHX30 Pro (lehké komerční použití)
PRES = ROOT.parent / "PW Helios" / "REO R290 Smart" / "prezentace-komercni" / "REO-R290-Smart_RHX20-RHX30-Pro_prezentace-CZ.pdf"
if PRES.exists():
    (ROOT / "navody" / PRES.name).write_bytes(PRES.read_bytes())
    index = index.replace("/*PRES_SIZE*/", f"{PRES.stat().st_size/1e6:.1f} MB".replace(".", ","))
(ROOT / "index.html").write_text(index)
print("HTML index.html", f"{len(index)/1e6:.2f} MB")
