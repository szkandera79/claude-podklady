#!/usr/bin/env python3
"""Datové listy REO R290 Smart (Heating 35–55 °C + vysokoteplotní provoz 60–75 °C), A4, anglicky
(stejně jako datové listy REO R290). Vzhled a vykreslení sdílí s ../../../R290-datove-listy/src (sheet.js, sheet.css).

Data: ../data/vykonove-mapy.json (z výkonových map výrobce, parse_maps.py).
    python3 build.py           # HTML + PDF
    python3 build.py --no-pdf
Výstupy: print/*.html, pdf/<model>_Heating_REO-R290-Smart.pdf
"""
import base64, json, math, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).parent
SHARED = (ROOT / '..' / '..' / '..' / 'R290-datove-listy' / 'src').resolve()
DATA = json.load(open(ROOT / '..' / 'data' / 'vykonove-mapy.json'))
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700'
         '&family=Poppins:wght@500;600&display=swap" rel="stylesheet">')

# prodávané provedení → zdroj mapy (1F a 3F mají u stejné velikosti shodná data; RH14 3F mapu zatím nemáme)
SHEETS = [
    ('RH06',   'RH06 1F',   'RH06 1F'),
    ('RH08',   'RH08 3F',   'RH08 3F'),
    ('RH10',   'RH10 3F',   'RH10 1F'),
    ('RH12',   'RH12 3F',   'RH12 3F'),
    ('RH14',   'RH14 3F',   'RH14 1F'),
    ('RH16',   'RH16 3F',   'RH16 3F'),
    ('RHX20',  'RHX20 Pro', 'RHX20 Pro'),
    ('RHX30',  'RHX30 Pro', 'RHX30 Pro'),
]


def r(vals, d):
    return [None if v is None else round(v, d) for v in vals]


def block(src, temps):
    out = {}
    for w in temps:
        out[w] = {m.upper(): {'cap': r(src[str(w)][m]['cap'], 2), 'inp': r(src[str(w)][m]['pin'], 2),
                              'cop': r(src[str(w)][m]['cop'], 2)} for m in ('max', 'min')}
    return out


def axis(blocks, key, step, floor0=True):
    v = [x for b in blocks for w in b.values() for m in w.values() for x in m[key] if x is not None]
    lo = 0 if floor0 else math.floor(min(v) / step) * step
    hi = math.ceil(max(v) / step + 1e-9) * step
    return [lo, hi, step]


models = {}
for key, name, src_key in SHEETS:
    h = DATA[src_key]['heating']
    D, DHi = block(h, [35, 45, 55]), block(h, [60, 65, 70, 75])
    cmax = max(x for b in (D, DHi) for w in b.values() for m in w.values() for x in m['cap'] if x is not None)
    step = 1 if cmax <= 12 else 2 if cmax <= 24 else 5
    models[key] = {'name': name, 'erp': name, 'label': None, 'amb': h['amb'],
                   'yCap': axis([D], 'cap', step), 'yCop': axis([D], 'cop', 1, False),
                   'yCapHi': axis([DHi], 'cap', step), 'yCopHi': axis([DHi], 'cop', 0.5, False),
                   'D': D, 'DHi': DHi}

data_js = ('// REO R290 Smart — výkonová data z výkonových map výrobce (generováno build.py z ../data/vykonove-mapy.json)\n'
           'const AMB = [-25,-20,-15,-12,-10,-7,-5,0,2,5,7,10,12,15,21];\n'
           'const MODELS = ' + json.dumps(models) + ';\n')
sheet_js = (SHARED / 'sheet.js').read_text()
sheet_css = (SHARED / 'sheet.css').read_text()
logo = 'data:image/png;base64,' + base64.b64encode((SHARED / 'assets' / 'logo-reoheating.png').read_bytes()).decode()
assets_js = 'const ASSETS = ' + json.dumps({'logo': logo, 'labels': {}}) + ';'

(ROOT / 'print').mkdir(exist_ok=True)
(ROOT / 'pdf').mkdir(exist_ok=True)
for key, name, _ in SHEETS:
    slug = name.replace(' ', '-')
    html = f"""<!-- {name} — datový list REO R290 Smart (Heating), A4. Generováno build.py -->
<meta charset="utf-8">
<title>{name} Heating — REO R290 Smart</title>
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
{assets_js}
document.fonts.ready.then(() => renderSheet(document.getElementById('sheet'), '{key}', ASSETS));
</script>
"""
    out = ROOT / 'print' / f'{slug}_REO-R290-Smart.html'
    out.write_text(html)
    if '--no-pdf' not in sys.argv:
        pdf = ROOT / 'pdf' / f'{slug}_Heating_REO-R290-Smart.pdf'
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
                        '--virtual-time-budget=8000', f'--print-to-pdf={pdf}', out.as_uri()],
                       check=True, capture_output=True)
        print('PDF', pdf.name)
for k, m in models.items():
    print(k, 'osy', m['yCap'], m['yCop'], m['yCapHi'], m['yCopHi'])
