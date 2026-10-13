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
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()

data_js = (SRC / "data.js").read_text()
sheet_js = (SRC / "sheet.js").read_text()
compare_js = (SRC / "compare.js").read_text()
sheet_css = (SRC / "sheet.css").read_text()
models = [(k, n, n.replace(" ", "-")) for k, n in
          re.findall(r"^  (RH[A-Z0-9]+): \{ name:'([^']+)'", data_js, re.M)]

def assets_js(labels):
    return "const ASSETS = " + json.dumps({
        "logo": data_uri(SRC / "assets/logo-reoheating.png"),
        # modely bez štítku (zatím nedodán výrobcem) se prostě přeskočí
        "labels": {f"label-{k}.png": data_uri(SRC / f"assets/label-{k}.png") for k in labels
                   if (SRC / f"assets/label-{k}.png").exists()},
    }) + ";"

# --- kontrola měřítek: žádná hodnota nesmí přesáhnout osu grafu (jinak by se křivka tiše ořízla)
CHECK_JS = """
%s
let bad = [];
for (const [key, M] of Object.entries(MODELS)) {
  const pages = [[M.D, [35,45,55], M.yCap, [1,7,1]]];
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

# --- artefakt (PDF k tisku vložené jako base64, stahují se přes capability `downloads`)
def pdfs_js():
    out = {}
    # artefakt REO R290 = jen domovní řada (RHX30 Pro / RH X50 a jejich srovnání SCOP do něj nepatří)
    for key, name, slug in [m for m in models if not m[0].startswith("RHX")]:
        f = ROOT / "pdf" / (f"{slug}_REO-HEATING.pdf" if key == "_cmp" else f"{slug}_Heating_REO-HEATING.pdf")
        if f.exists():
            out[key] = {"file": f.name, "size": f.stat().st_size,
                        "b64": base64.b64encode(f.read_bytes()).decode()}
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
(ROOT / "index.html").write_text(index)
print("HTML index.html", f"{len(index)/1e6:.2f} MB")
