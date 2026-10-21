#!/usr/bin/env python3
"""Produktová brožura REO R290 Smart (A4, 8 stran) – přeznačení produktového katalogu výrobce (vydání 10/2025)
v designu katalogu REO HEATING (sdílí CSS, ikony a logo z ../katalog/build.py).
Nabízené modely: RH06 1F + RH08–RH16 3F (ostatní jednofázové verze se nenabízejí → vypuštěny).
Data = tabulky technických údajů z katalogu výrobce (orientační, rozhodující je typový štítek).
Fotky v assets/ = výřezy z katalogu výrobce bez loga (zkontrolováno), jednotka a hero = naše assets katalogu.
    python3 build.py   → REO-R290-Smart_brozura.html + .pdf (headless Chrome)
"""
import base64, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).parent
A = ROOT / "assets"
sys.path.insert(0, str(ROOT.parent / "katalog"))
import build as K  # noqa: E402  (katalog: CSS, ikony, logo, schéma FV)

ic, IC, FONTS, CHROME = K.ic, K.IC, K.FONTS, K.CHROME
IC.update({
 "fan":   "M12 12m-2 0a2 2 0 1 0 4 0 2 2 0 1 0-4 0 M12 10c0-4 1-7 4-7 2 0 3 2 2 4-1 1.5-3 2.5-6 3 M14 12c4 0 7 1 7 4 0 2-2 3-4 2-1.5-1-2.5-3-3-6 M12 14c0 4-1 7-4 7-2 0-3-2-2-4 1-1.5 3-2.5 6-3 M10 12c-4 0-7-1-7-4 0-2 2-3 4-2 1.5 1 2.5 3 3 6",
 "alert": "M10.3 3.9L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z M12 9v4 M12 17h.01",
 "clock": "M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z M12 6v6l4 2",
 "list":  "M8 6h13 M8 12h13 M8 18h13 M3 6h.01 M3 12h.01 M3 18h.01",
 "lang":  "M5 8l6 6 M4 14l6-6 2-3 M2 5h12 M7 2h1 M22 22l-5-10-5 10 M14 18h6",
 "hist":  "M3 12a9 9 0 1 0 3-6.7L3 8 M3 3v5h5 M12 7v5l4 2",
 "pipe":  "M4 6h10a4 4 0 0 1 4 4v10 M4 10h10 M14 20h8",
 "curve": "M3 3v18h18 M6 8c4 0 6 3 8 6s4 4 6 4",
 "limit": "M12 2v4 M12 18v4 M4.9 4.9l2.8 2.8 M16.3 16.3l2.8 2.8 M2 12h4 M18 12h4 M12 12l4-4",
})


def uri(name):
    p = A / name if (A / name).exists() else ROOT.parent / "katalog" / "assets" / name
    mime = {"png": "image/png", "jpg": "image/jpeg", "svg": "image/svg+xml"}[p.suffix[1:]]
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


LOGO, UNIT, QR, HERO = K.LOGO, K.UNIT, K.QR, K.HERO
FOOT = K.FOOT


def top(tag, n):
    return K.top(tag, n)


# ================================================================ DATA (tabulky výrobce, 10/2025)
# RH06 = jednofázová verze (230 V), RH08–RH16 = třífázové verze (400 V)
MOD = ["RH06 1F", "RH08 3F", "RH10 3F", "RH12 3F", "RH14 3F", "RH16 3F"]
SPEC = [
 ("sec", "Vytápění A7/W35 (jmenovitě)"),
 ("Topný výkon [kW]",            ["6,0", "8,0", "10,0", "12,0", "14,0", "16,0"]),
 ("Příkon [kW]",                 ["1,23", "1,64", "2,10", "2,47", "2,96", "3,40"]),
 ("COP",                         ["4,88", "4,89", "4,76", "4,86", "4,73", "4,70"]),
 ("sec", "Vytápění A7/W55 (jmenovitě)"),
 ("Topný výkon [kW]",            ["6,0", "8,0", "10,0", "12,0", "14,0", "16,0"]),
 ("Příkon [kW]",                 ["1,98", "2,63", "3,44", "3,99", "4,75", "5,46"]),
 ("COP",                         ["3,03", "3,04", "2,91", "3,01", "2,95", "2,93"]),
 ("sec", "Chlazení A35/W18 (jmenovitě)"),
 ("Chladicí výkon [kW]",         ["6,0", "8,0", "10,0", "12,0", "14,0", "16,0"]),
 ("Příkon [kW]",                 ["1,23", "1,64", "2,10", "2,48", "2,92", "3,37"]),
 ("EER",                         ["4,86", "4,88", "4,76", "4,84", "4,80", "4,75"]),
 ("sec", "Vytápění – rozsah modulace (A7/W35, voda 30/35 °C)"),
 ("Topný výkon [kW]",            ["3,4–8,5", "4,5–11,0", "5,2–12,9", "7,0–17,0", "7,6–19,3", "8,8–22,0"]),
 ("Příkon [kW]",                 ["0,66–1,99", "0,87–2,60", "1,03–3,08", "1,38–3,90", "1,50–4,62", "1,74–5,47"]),
 ("COP",                         ["4,27–5,13", "4,23–5,15", "4,19–5,05", "4,35–5,07", "4,18–5,07", "4,02–5,05"]),
 ("sec", "Ohřev teplé vody (A20, voda 15 → 55 °C)"),
 ("Topný výkon [kW]",            ["4,0–9,0", "5,2–11,5", "5,3–13,2", "6,6–17,5", "7,8–19,5", "8,8–22,5"]),
 ("Příkon [kW]",                 ["0,78–2,14", "1,04–2,76", "1,05–3,28", "1,37–3,98", "1,54–4,64", "1,75–5,55"]),
 ("COP",                         ["4,20–5,13", "4,17–5,05", "4,02–5,04", "4,39–4,81", "4,20–5,06", "4,05–5,03"]),
 ("Ohřev vody [l/h]",            ["194", "248", "284", "376", "419", "484"]),
 ("sec", "Chlazení – rozsah (A35, voda 12/7 °C · 23/18 °C)"),
 ("Výkon W7 [kW]",               ["2,4–6,0", "3,5–8,0", "4,0–9,8", "5,0–13,2", "5,6–14,5", "6,4–16,5"]),
 ("EER W7",                      ["3,01–3,51", "3,10–3,61", "2,72–3,22", "2,92–3,35", "2,90–3,35", "2,85–3,31"]),
 ("Výkon W18 [kW]",              ["3,5–8,0", "4,3–11,0", "4,8–12,5", "6,6–16,1", "7,0–17,5", "8,2–20,5"]),
 ("EER W18",                     ["4,25–5,25", "4,29–5,29", "4,17–5,11", "4,07–5,16", "4,05–5,15", "4,08–5,16"]),
 ("sec", "Elektro, hydraulika, rozměry"),
 ("Energetická třída 35 / 55 °C", "A+++ / A+++"),
 ("Napájení",                    ["230 V / 1f / 50 Hz", ("400 V / 3f / 50 Hz", 5)]),
 ("Max. příkon [kW]",            ["3,3", "4,5", "5,5", "6,3", "6,6", "8,1"]),
 ("Max. proud [A]",              ["15,1", "8,6", "10,4", "12,0", "12,5", "15,4"]),
 ("Přípojky vody",               [("DN25", 4), ("DN32", 2)]),
 ("Průtok vody [m³/h]",          ["1,46", "1,89", "2,24", "2,92", "3,32", "3,78"]),
 ("Tlaková ztráta max. [kPa]",   ["30", "35", "40", "43", "47", "52"]),
 ("Hmotnost netto [kg]",         ["116", "120", "138", "165", "170", "190"]),
 ("Rozměry Š×H×V [mm]",          ["1200×463×791", ("1328×470×1065", 5)]),
 ("Krytí / třída ochrany",       "IPX4 / I"),
 ("Chladivo",                    "R290 (propan)"),
 ("Výbava v jednotce",           "oběhové čerpadlo · záložní el. dohřev 3 kW · expanzní nádoba 6 l · pojistný ventil"),
 ("Provoz – venkovní teplota",   "−25 až 43 °C"),
 ("Teplota vody",                "vytápění 25–75 °C · teplá voda 25–75 °C · chlazení 5–30 °C"),
]


def spec_table():
    head = "".join(f"<th>{m.split()[0]}<small>{m.split()[1]}</small></th>" for m in MOD)
    rows = []
    for label, v in SPEC:
        if label == "sec":
            rows.append(f'<tr class="sec"><td colspan="7">{v}</td></tr>')
            continue
        if isinstance(v, str):
            cells = f'<td colspan="6">{v}</td>'
        else:
            cells = "".join(f'<td colspan="{c[1]}">{c[0]}</td>' if isinstance(c, tuple) else f"<td>{c}</td>" for c in v)
        rows.append(f"<tr><th>{label}</th>{cells}</tr>")
    return f'<table class="spec"><thead><tr><th>Model</th>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


# ================================================================ SVG
def svg_gwp4():
    data = [("R410A", 2088), ("R407C", 1774), ("R32", 675), ("R290", 3)]
    out = []
    for i, (n, v) in enumerate(data):
        y = 6 + i * 30
        w = max(5, v / 2088 * 230)
        c = "#34A263" if n == "R290" else "#B9C4BD"
        out.append(f'<text x="0" y="{y+16}" font-size="13" font-weight="800" fill="#123D25">{n}</text>'
                   f'<rect x="62" y="{y}" width="{w}" height="22" rx="5" fill="{c}"/>'
                   f'<text x="{62+w+8}" y="{y+16}" font-size="13" font-weight="800" fill="{"#26804B" if n == "R290" else "#3E4A43"}">'
                   f'{v:,}</text>'.replace(",", "&#8239;"))
    return ('<svg class="gwp" viewBox="0 0 360 126" xmlns="http://www.w3.org/2000/svg" font-family="Inter, sans-serif">'
            + "".join(out) + "</svg>")


def svg_curves():
    """Ekvitermní křivky: teplota vody podle venkovní teploty (ilustrační, 8 + 1 vlastní)."""
    W, H, x0, y0, pw, ph = 380, 210, 34, 12, 330, 160
    X = lambda t: x0 + (t + 20) / 40 * pw          # −20 … +20 °C
    Y = lambda w: y0 + ph - (w - 20) / 40 * ph      # 20 … 60 °C
    out = []
    for w in (20, 30, 40, 50, 60):
        out.append(f'<line x1="{x0}" x2="{x0+pw}" y1="{Y(w)}" y2="{Y(w)}" stroke="#E3EAE5"/>'
                   f'<text x="{x0-6}" y="{Y(w)+4}" text-anchor="end" font-size="10" fill="#7C8A82">{w}</text>')
    for t in (-20, -10, 0, 10, 20):
        out.append(f'<text x="{X(t)}" y="{y0+ph+15}" text-anchor="middle" font-size="10" fill="#7C8A82">{t}</text>')
    cols = ["#9FD5B4", "#86C9A0", "#6DBD8C", "#55B178", "#34A263", "#26804B", "#1E6A3D", "#123D25"]
    for i, c in enumerate(cols):
        hi, lo = 34 + i * 3.4, 25 + i * 0.9
        pts = " ".join(f"{X(t):.1f},{Y(hi - (hi - lo) * (t + 20) / 40):.1f}" for t in (-20, 20))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="2.4"/>')
    cust = f"{X(-20)},{Y(46)} {X(-5)},{Y(41)} {X(8)},{Y(33)} {X(20)},{Y(27)}"
    out.append(f'<polyline points="{cust}" fill="none" stroke="#D9622B" stroke-width="2.6" stroke-dasharray="6 4"/>')
    out.append(f'<text x="{X(-19)}" y="{Y(49.5)}" font-size="10.5" font-weight="700" fill="#D9622B">vlastní křivka</text>')
    out.append(f'<text x="{x0}" y="{y0-2}" font-size="9.5" fill="#7C8A82">voda °C</text>'
               f'<text x="{x0+pw}" y="{y0+ph+30}" text-anchor="end" font-size="9.5" fill="#7C8A82">venkovní teplota °C</text>')
    return (f'<svg class="curves" viewBox="0 0 {W} {H+12}" xmlns="http://www.w3.org/2000/svg" font-family="Inter, sans-serif">'
            + "".join(out) + "</svg>")


def svg_cloud():
    """Jednotka → ovladač → router → internet → mobil / servisní partner."""
    def node(x, label, sub, icon):
        return (f'<g transform="translate({x},0)"><rect x="0" y="16" width="104" height="70" rx="12" fill="#fff" stroke="#34A263" stroke-width="1.6"/>'
                f'<g transform="translate(40,26) scale(1)" fill="none" stroke="#34A263" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="{IC[icon]}"/></g>'
                f'<text x="52" y="66" text-anchor="middle" font-size="11.5" font-weight="800" fill="#123D25">{label}</text>'
                f'<text x="52" y="79" text-anchor="middle" font-size="9.5" fill="#5C6B62">{sub}</text></g>')
    arr = lambda x: f'<path d="M{x} 51 h18" stroke="#7C8A82" stroke-width="2"/><path d="M{x+16} 46 l7 5 -7 5z" fill="#7C8A82"/>'
    xs = [0, 130, 260, 390, 520]
    nodes = [("Jednotka", "REO R290 Smart", "box"), ("Ovladač 7″", "v domě", "phone"), ("Wi-Fi router", "domácí síť", "wifi"),
             ("Cloud", "přes internet", "web"), ("Mobil · servis", "vy i váš technik", "users")]
    return ('<svg class="cloud" viewBox="0 0 628 96" xmlns="http://www.w3.org/2000/svg" font-family="Inter, sans-serif">'
            + "".join(node(x, *n) for x, n in zip(xs, nodes)) + "".join(arr(x + 106) for x in xs[:-1]) + "</svg>")


# ================================================================ STRANY
COVER_IC = [("temp", "Vytápění"), ("snow", "Chlazení"), ("drop", "Teplá voda<br>až 75 °C"), ("cert", "A+++<br>35 i 55 °C")]

p1 = f"""
<section class="page cover">
  <div class="cv-glow"></div>
  <div class="cv-top"><img src="{LOGO}" alt="REO HEATING"><div class="qr"><img src="{QR}" alt="reoheating.cz"></div></div>
  <div class="cv-head">
    <div class="eyebrow">Plně invertorové tepelné čerpadlo vzduch–voda · monoblok</div>
    <h1>REO R290 <span>Smart</span></h1>
    <div class="cv-sub">Úsporné vytápění, chlazení a teplá voda v jednom</div>
  </div>
  <div class="hero b-hero"><img src="{HERO}" alt="REO R290 Smart">
    <div class="b-badges">{''.join(f'<div>{ic(k)}<span>{t}</span></div>' for k, t in COVER_IC)}</div>
    <div class="b-r290"><b>R290</b><span>přírodní chladivo</span></div>
  </div>
  <div class="b-pil">
    <div class="sun">{ic('sun')}<div><b>Topí přímo ze sluníčka</b><span>panely rovnou do jednotky – bez střídače a baterie</span></div></div>
    <div class="eff">{ic('eff')}<div><b>SCOP až 5,29</b><span>třída A+++ pro podlahu i radiátory</span></div></div>
    <div class="mit">{ic('cpu')}<div><b>Kompresor Mitsubishi&nbsp;Electric</b><span>invertorový, plynulá regulace výkonu</span></div></div>
  </div>
  <div class="b-mod">{''.join(f'<div><b>{m.split()[0]}</b><span>{kw} kW · {"230 V" if "1F" in m else "400 V"}</span></div>' for m, kw in zip(MOD, (6, 8, 10, 12, 14, 16)))}</div>
  <div class="cv-bot">
    <div><b>Produktová brožura</b><span>modely RH06 (230 V) a RH08–RH16 (400 V) · 6–16 kW</span></div>
    <div class="cv-web">reoheating.cz</div>
  </div>
</section>"""

ROOMS = [("topeni.jpg", "temp", "Vytápění", "Podlahové topení, radiátory i fancoily – jedna jednotka pro celý dům."),
         ("chlazeni.jpg", "snow", "Chlazení", "V létě dům příjemně ochladí přes fancoily nebo podlahu (s ochranou proti rosení)."),
         ("tuv.jpg", "drop", "Teplá voda", "Ohřev vody v zásobníku až na 75 °C, i pro pravidelnou dezinfekci.")]
p2 = f"""
<section class="page">
  {top('Chladivo a účinnost', 2)}
  <div class="eyebrow">Přírodní chladivo R290</div>
  <h2 class="ph">Šetrné k přírodě, připravené na budoucnost</h2>
  <div class="banner" style="background-image:url({uri('les.jpg')})">
    <div class="bn-k"><b>99 %</b><span>nižší GWP<br>než běžná chladiva</span></div>
  </div>
  <div class="two">
    <div class="card">
      <h3>{ic('leaf')} Chladivo R290 (propan)</h3>
      <p>R290 je přírodní a široce používané chladivo. Na rozdíl od R32, R407C nebo R410A má potenciál globálního oteplování
      (GWP) jen&nbsp;3 a nulový vliv na ozonovou vrstvu. Splňuje přísná pravidla EU pro chladiva i do budoucna.</p>
      {svg_gwp4()}
      <div class="sm">GWP – potenciál globálního oteplování (CO₂ = 1).</div>
    </div>
    <div class="card tint">
      <h3>{ic('cert')} Energetická třída A+++</h3>
      <p>Nejvyšší energetická třída <b>A+++ při 35 °C i 55 °C</b> – pro podlahové topení i radiátory.
      Vysoká účinnost i v létě: v režimu chlazení EER až 4,88 (A35/W18).</p>
      <div class="erp">
        <div class="erp-sc">{''.join(f'<i style="width:{30+i*9}%;background:{c}">{t}</i>' for i, (t, c) in enumerate([("A+++", "#1E8E3E"), ("A++", "#4BAA3A"), ("A+", "#9BC73B"), ("A", "#E6D82B"), ("B", "#F2B42B"), ("C", "#EC7A24"), ("D", "#D9322B")]))}</div>
        <div class="erp-v"><div><small>55 °C</small><b>A+++</b></div><div><small>35 °C</small><b>A+++</b></div></div>
      </div>
    </div>
  </div>
  <h3 class="h3s">{ic('home')} Jeden systém, tři funkce</h3>
  <div class="rooms">
    {''.join(f'<div class="room"><div class="ri" style="background-image:url({uri(f)})"><span>{ic(k)}{t}</span></div><p>{d}</p></div>' for f, k, t, d in ROOMS)}
  </div>
  <div class="foot">Energetická třída podle nařízení EU 811/2013 (průměrné klima). Údaje výrobce, orientační. {FOOT}</div>
</section>"""

p3 = f"""
<section class="page">
  {top('Výkon v každém počasí', 3)}
  <div class="eyebrow">Spolehlivě i v mrazu</div>
  <h2 class="ph">Až 75 °C na výstupu, provoz do −25 °C</h2>
  <div class="split">
    <div class="pimg" style="background-image:url({uri('zima-75.jpg')})"><div class="tagb heat">75 °C</div></div>
    <div>
      <h3>{ic('temp')} Teplá voda až 75 °C</h3>
      <p>Výstupní teplota vody až 75 °C. Jednotka si poradí s podlahovým topením i s radiátory ve starších domech
      a ohřeje teplou vodu bez elektrické spirály – i na teplotu pro dezinfekci zásobníku.</p>
      <h3 class="mt4">{ic('snow')} Provoz do −25 °C</h3>
      <p>Stabilní provoz při venkovních teplotách od −25 °C do 43 °C – topí celou zimu, v létě chladí.</p>
      <h3 class="mt4">{ic('shield')} Vyhřívaná vana proti zamrznutí</h3>
      <p>Vyhřívání spodní vany brání tvorbě ledu z kondenzátu. Jednotka spolehlivě pracuje i v dlouhých mrazech.</p>
    </div>
  </div>
  <div class="dark">
    <div class="dk-t">
      <div class="eyebrow" style="color:var(--sun)">Plně invertorová technologie DC</div>
      <h3>Výkon přesně podle potřeby domu</h3>
      <p>Invertorový kompresor <b>Mitsubishi Electric</b>, DC ventilátor i DC čerpadlo plynule mění výkon podle aktuální potřeby.
      Žádné zbytečné zapínání a vypínání – nižší spotřeba, delší životnost a stabilní teplota v domě i za mrazu.</p>
      <div class="dk-n"><div><b>−25 °C</b><span>spodní mez provozu</span></div><div><b>75 °C</b><span>max. teplota vody</span></div><div><b>až 5,15</b><span>COP při A7/W35</span></div></div>
    </div>
    <div class="dk-i" style="background-image:url({uri('kompresor.jpg')})"></div>
  </div>
  <h3 class="h3s">{ic('home')} Hodí se do nových i starších domů</h3>
  <div class="three fit">
    <div class="card"><b>35 °C</b><h4>Podlahové topení</h4><p>Nejvyšší účinnost – ideální pro novostavby a nízkoenergetické domy.</p></div>
    <div class="card"><b>55–75 °C</b><h4>Radiátory</h4><p>Náhrada kotle i ve starších domech bez nutnosti měnit otopná tělesa (podle výpočtu).</p></div>
    <div class="card"><b>7–18 °C</b><h4>Chlazení</h4><p>Fancoily nebo podlaha – v létě příjemný chlad z téhož zařízení.</p></div>
  </div>
  <div class="foot">Ilustrační vizualizace. COP v rozsahu modulace podle tabulky výrobce (A7/W35). {FOOT}</div>
</section>"""

QUIET = [("cpu", "Uzavřený prostor kompresoru", "s vlnitou pohltivou PU pěnou"),
         ("layers", "Trojvrstvá PU izolace", "na plechových panelech skříně"),
         ("fan", "Velkoúhlé 3D lopatky ventilátoru", "plynulé a tiché proudění vzduchu"),
         ("eff", "Vícerychlostní řízení ventilátoru", "otáčky podle skutečné potřeby"),
         ("quiet", "Dvoustupňový tichý režim", "pro den i noc, s časovým programem")]
p4 = f"""
<section class="page">
  {top('Odmrazování a hluk', 4)}
  <div class="eyebrow">Chytré odmrazování</div>
  <h2 class="ph">Odmrazí jen tehdy, když je to potřeba</h2>
  <div class="split r">
    <div>
      <p class="lead2">Inteligentní odmrazování průběžně vyhodnocuje teploty v několika bodech a dobu provozu. Námrazu na výparníku
      rozpozná sama a odmrazí ji rychlým přepnutím čtyřcestného ventilu – <b>jen když je to opravdu potřeba</b>.</p>
      <ul class="chk">
        <li>kratší odmrazovací cykly</li>
        <li>méně energie spotřebované na odmrazování</li>
        <li>stabilnější teplota topné vody i v mlhavém mrazivém počasí</li>
      </ul>
    </div>
    <div class="pimg" style="background-image:url({uri('odmrazovani.jpg')})"></div>
  </div>
  <div class="eyebrow mt6">Tichý provoz</div>
  <h2 class="ph">Pět opatření proti hluku</h2>
  <div class="quiet">
    <div class="q-k"><b>od 35</b><span>dB(A)*</span><small>akustický tlak<br>ve vzdálenosti 1 m</small></div>
    <div class="q-l">{''.join(f'<div><i>{n+1}</i>{ic(k)}<div><h4>{t}</h4><p>{d}</p></div></div>' for n, (k, t, d) in enumerate(QUIET))}</div>
    <div class="q-u"><img src="{UNIT}" alt="REO R290 Smart"></div>
  </div>
  <div class="card tint tip">
    <h3>{ic('pin')} Kam jednotku umístit</h3>
    <div class="two">
      <ul class="chk"><li>ne pod okna ložnic a do úzkých průchodů nebo rohů, kde se zvuk odráží</li>
      <li>na pevný podstavec s antivibračními patkami, výfuk vzduchu směrem od sousedů</li></ul>
      <ul class="chk"><li>dostatečný odstup od stěny pro sání vzduchu a údržbu</li>
      <li>odvod kondenzátu tak, aby v zimě nezamrzal</li></ul>
    </div>
  </div>
  <div class="foot">* Nejnižší hodnota řady (RH08, 1 m, podmínky ErP); hladiny akustického výkonu jednotlivých modelů uvádí datový list.
  Skutečná hlučnost závisí na místě instalace a odrazných plochách – umístění navrhujeme podle NV 272/2011 Sb. {FOOT}</div>
</section>"""

CTRL4 = [("layers", "Kaskáda až 8 jednotek", "řízení z jednoho ovladače, až 3 nezávislé teplotní zóny"),
         ("plug", "Chytré propojení", "Modbus pro řídicí systém budovy (BMS), připravenost na FV, řízení externího zdroje tepla"),
         ("chart", "Přehled o energii", "spotřeba elektřiny, vyrobené teplo, historie a export dat"),
         ("clock", "Automatika", "režim dovolená, časové programy, dezinfekce zásobníku, omezení příkonu")]
p5 = f"""
<section class="page">
  {top('Bezpečnost a řízení', 5)}
  <div class="eyebrow">Bezpečnost chladiva R290</div>
  <h2 class="ph">Dvoustupňová ochrana proti úniku chladiva</h2>
  <p class="lead2">Dva nezávislé mechanismy drží chladivo mimo vnitřní prostory domu. Jednotka stojí venku a chladivo do domu vůbec nevede.</p>
  <div class="two">
    <div class="card sf"><img src="{uri('senzor.jpg')}" alt=""><div><h3><i class="n">1</i>Snímač úniku chladiva</h3>
      <p>Při koncentraci 15 % dolní meze výbušnosti (LFL) spustí alarm, zastaví hlavní komponenty a ventilátorem udržuje minimální odvětrání jednotky.</p></div></div>
    <div class="card sf"><img src="{uri('ventil.jpg')}" alt=""><div><h3><i class="n">2</i>Mikrobublinový odvzdušňovací ventil</h3>
      <p>Pokud by chladivo proniklo do vodního okruhu, ventil ho automaticky vypustí ven – nedostane se potrubím do domu.</p></div></div>
  </div>
  <div class="two">
    <div class="card">
      <h3>{ic('curve')} Ekvitermní regulace</h3>
      <p>Vyberete křivku a o zbytek se postará regulace: teplotu vody sama upravuje podle venkovní teploty.
      <b>8 přednastavených a 1 vlastní křivka</b> pro topení i chlazení.</p>
      {svg_curves()}
    </div>
    <div class="card">
      <h3>{ic('pipe')} Přípojky na jednom místě</h3>
      <p>Vstup a výstup vody jsou přehledně spodem na boku jednotky – čistá montáž, snadný servis.</p>
      <div class="pimg sm2" style="background-image:url({uri('pripojky.jpg')})"></div>
    </div>
  </div>
  <h3 class="h3s">{ic('phone')} Dotykový ovladač 7″</h3>
  <div class="ctrl4">
    <div class="c4i"><img src="{uri('ovladac.jpg')}" alt="ovladač"><span>velký barevný kapacitní displej, přehledné menu</span></div>
    {''.join(f'<div>{ic(k)}<div><h4>{t}</h4><p>{d}</p></div></div>' for k, t, d in CTRL4)}
  </div>
  <div class="foot">Ekvitermní křivky v grafu jsou ilustrační. Displej ovladače je v angličtině, český návod popisuje všechny obrazovky. {FOOT}</div>
</section>"""

PV4 = [("sun", "Provoz ze sluníčka", "kompresor bere přednostně energii z panelů"),
       ("plug", "Méně elektřiny ze sítě", "co sluníčko nepokryje, doplní automaticky síť"),
       ("leaf", "Čistá energie", "nižší uhlíková stopa vytápění"),
       ("grid", "Běžné FV panely", "bez střídače, baterie a další elektroniky")]
p6 = f"""
<section class="page">
  {top('Topí přímo ze sluníčka', 6)}
  <div class="solar-h"><div class="sic">{ic('sun')}</div><div>
    <div class="eyebrow">Přímé napojení fotovoltaiky</div>
    <h2 class="ph">Topí přímo ze sluníčka</h2>
    <div class="sub">Bez střídače. Bez baterie. U velkých značek tohle nenajdete.</div></div></div>
  <div class="ilrow">
    {K.ILU}
    <div class="pv4">{''.join(f'<div>{ic(k)}<div><h4>{t}</h4><p>{d}</p></div></div>' for k, t, d in PV4)}</div>
  </div>
  <div class="card prin-c">
    <h3>{ic('eff')} Jak to funguje</h3>
    {K.svg_principle()}
  </div>
  <div class="two">
    <div class="card tint">
      <h3>{ic('sun')} SG Ready a FV Ready</h3>
      <p>Máte-li fotovoltaiku se střídačem, jednotka umí přes vstup SG Ready využít přebytky: při signálu zvýší teplotu
      teplé vody nebo akumulace a uloží levnou energii do tepla.</p>
    </div>
    <div class="card tint">
      <h3>{ic('limit')} Omezení příkonu</h3>
      <p>Nastavitelný limit příkonu jednotky a řízení podle externího signálu – jednotka se přizpůsobí jističi
      i požadavkům distribuční sítě, aniž by se vypínala.</p>
    </div>
  </div>
  <div class="card">
    <h3>{ic('grid')} Kolik panelů připojit</h3>
    <div class="pvt">
      <table class="mt"><tr><th>Model</th><th>Max. výkon FV</th><th>Orientačně (panely 500 Wp)</th></tr>
      {''.join(f'<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>' for a, b, c in K.PVT)}</table>
      <p class="sm">Panely v jednom řetězci. Napětí naprázdno řetězce musí i v mrazu zůstat pod 311 V (RH06 1F), resp. 537 V (3F) – přesný počet
      navrhneme podle typu panelu.</p>
    </div>
  </div>
  <div class="foot">Podíl energie ze slunce závisí na velikosti a orientaci panelů, počasí a ročním období – nejvíc od jara do podzimu,
  v zimě je výroba panelů nízká. Přímé napojení vyžaduje desku MPPT; počet panelů navrhneme podle modelu. {FOOT}</div>
</section>"""

APP8 = [("grid", "Přepínání režimů"), ("chart", "Spotřeba energie"), ("eff", "Sledování v reálném čase"), ("hist", "Historie provozu"),
        ("lang", "10 jazyků"), ("alert", "Automatická diagnostika poruch"), ("clock", "Časové programy"), ("list", "Provozní parametry")]
p7 = f"""
<section class="page">
  {top('Aplikace a dálkový dohled', 7)}
  <div class="eyebrow">Chytré ovládání</div>
  <h2 class="ph">Dům pod kontrolou odkudkoli</h2>
  <div class="appw">
    <div class="phone"><img src="{uri('aplikace.jpg')}" alt="aplikace"></div>
    <div>
      <p class="lead2">Jednotku připojíte přes Wi-Fi a ovládáte z mobilu aplikací <b>Smart Life</b>, <b>Tuya Smart</b> nebo <b>Huilian</b>
      (Android i iOS). Jednoduše nastavíte teplotu topení i teplé vody a vidíte, kolik jednotka spotřebovala.</p>
      <div class="app8">{''.join(f'<div>{ic(k)}<span>{t}</span></div>' for k, t in APP8)}</div>
    </div>
  </div>
  <div class="eyebrow mt6">Vzdálený dohled a servis</div>
  <h2 class="ph">Méně výjezdů, rychlejší pomoc</h2>
  <p class="lead2">Provozní data jednotky jsou přes zabezpečené připojení k dispozici vám i vašemu servisnímu technikovi. Ten vidí stav,
  parametry i hlášení poruch a často problém vyřeší na dálku – bez zbytečného výjezdu.</p>
  <div class="card tint">{svg_cloud()}</div>
  <div class="three">
    <div class="card">{ic('chart')}<h4>Přehled a statistiky</h4><p>Sběr a vyhodnocení provozních dat – spotřeba, výkon, účinnost.</p></div>
    <div class="card">{ic('wrench')}<h4>Správa zařízení</h4><p>Stav provozu, nastavení parametrů, diagnostika poruch a provozní záznam.</p></div>
    <div class="card">{ic('cpu')}<h4>Aktualizace na dálku</h4><p>Software řídicí desky lze aktualizovat vzdáleně, bez návštěvy technika.</p></div>
  </div>
  <div class="foot">Komunikace přes Wi-Fi (2,4 GHz). Vzdálený přístup servisu jen se souhlasem uživatele. Podrobný popis funkcí najdete v návodu. {FOOT}</div>
</section>"""

p8 = f"""
<section class="page">
  {top('Technické údaje', 8)}
  <div class="eyebrow">Technické údaje</div>
  <h2 class="ph">Modely REO R290 Smart</h2>
  {spec_table()}
  <div class="band b8">
    <div class="bl">
      <div class="eyebrow" style="color:var(--sun)">Chcete topit ze sluníčka?</div>
      <div class="ctah">Nezávaznou nabídku vám pošleme do 24 hodin.</div>
      <div class="contact">
        <span>{ic('mail','ci')}info@reoheating.cz</span><span>{ic('tel','ci')}+420 774 872 467</span>
        <span>{ic('web','ci')}reoheating.cz</span><span>{ic('pin','ci')}Smetanova 555, 739 61 Třinec</span>
      </div>
    </div>
    <div class="br"><div class="qr2"><img src="{QR}" alt="QR reoheating.cz"></div></div>
  </div>
  <div class="foot">Údaje výrobce jsou orientační, rozhodující jsou údaje na typovém štítku jednotky. Výkony podle EN 14511. Jednotka nenahrazuje
  vnitřní hydraulické zapojení (ventil pro teplou vodu, filtr, armatury, zásobník, příp. akumulace) – navrhujeme podle projektu. {FOOT}</div>
</section>"""

CSS = K.CSS + """
.h3s{margin-top:1mm}
.mt4{margin-top:3.5mm}.mt6{margin-top:5mm}
.b-hero{margin-top:5mm}
.b-badges{position:absolute;left:4mm;top:4mm;display:flex;gap:2.2mm}
.b-badges div{background:rgba(255,255,255,.94);border-radius:3mm;padding:2.2mm 1.5mm;width:20mm;text-align:center;box-shadow:0 1mm 3mm rgba(0,0,0,.15)}
.b-badges .ic{display:block;margin:0 auto 1mm;width:6mm;height:6mm}
.b-badges span{font-size:7pt;font-weight:700;line-height:1.15;color:var(--darker)}
.b-r290{position:absolute;right:5mm;bottom:5mm;width:24mm;height:24mm;border-radius:50%;background:var(--brand);color:#fff;
 display:flex;flex-direction:column;align-items:center;justify-content:center;border:1.2mm solid #fff;box-shadow:0 1mm 4mm rgba(0,0,0,.25)}
.b-r290 b{font-size:14pt;font-weight:800;line-height:1}.b-r290 span{font-size:6pt;font-weight:600;text-align:center;line-height:1.1;margin-top:.6mm}
.b-pil{position:relative;display:grid;grid-template-columns:repeat(3,1fr);gap:3mm;padding:5mm 10mm 0}
.b-pil>div{display:flex;gap:2.5mm;align-items:center;border-radius:4mm;padding:3.5mm 3.5mm}
.b-pil .ic{width:8.5mm;height:8.5mm}
.b-pil b{display:block;font-size:10.5pt;font-weight:800;line-height:1.15;margin-bottom:.8mm}
.b-pil span{font-size:7.6pt;line-height:1.3;display:block}
.b-pil .sun{background:var(--sun);color:var(--darker)}.b-pil .sun .ic{color:var(--darker)}
.b-pil .eff{background:var(--brand);color:#fff}.b-pil .eff .ic{color:#fff}
.b-pil .mit{background:var(--darker);color:#fff}.b-pil .mit .ic{color:var(--sun)}

.banner{height:62mm;border-radius:4mm;background-size:cover;background-position:center 40%;position:relative;margin-bottom:4mm}
.bn-k{position:absolute;left:5mm;bottom:5mm;background:var(--brand);color:#fff;border-radius:3.5mm;padding:3mm 5mm}
.bn-k b{display:block;font-size:24pt;font-weight:800;line-height:1}.bn-k span{font-size:8pt;line-height:1.25;display:block;margin-top:1mm}
.gwp{margin-top:3mm;max-width:88mm}
.erp{display:grid;grid-template-columns:1fr 34mm;gap:3mm;margin-top:3mm;align-items:start}
.erp-sc i{display:block;font-style:normal;color:#fff;font-size:7pt;font-weight:800;padding:.5mm 2mm;margin-bottom:.8mm;
 clip-path:polygon(0 0,calc(100% - 2.5mm) 0,100% 50%,calc(100% - 2.5mm) 100%,0 100%)}
.erp-v{display:grid;grid-template-columns:1fr 1fr;gap:2mm}
.erp-v div{text-align:center}.erp-v small{display:block;font-size:7.5pt;color:var(--muted);font-weight:700;margin-bottom:1mm}
.erp-v b{display:block;background:#123D25;color:#fff;font-size:10pt;font-weight:800;padding:2mm 0;
 clip-path:polygon(2.5mm 0,100% 0,100% 100%,2.5mm 100%,0 50%)}
.rooms{display:grid;grid-template-columns:repeat(3,1fr);gap:4mm}
.ri{height:52mm;border-radius:3.5mm;background-size:cover;background-position:center;position:relative;margin-bottom:2mm}
.ri span{position:absolute;left:2.5mm;top:2.5mm;background:#fff;border-radius:99px;padding:1.2mm 3mm 1.2mm 2mm;font-size:8.5pt;font-weight:800;
 color:var(--darker);display:flex;align-items:center;gap:1.2mm}
.ri .ic{width:4.5mm;height:4.5mm}
.room p{font-size:8.2pt;color:#33433A}

.split{display:grid;grid-template-columns:1fr 1fr;gap:6mm;align-items:stretch;margin-bottom:5mm}
.split .pimg{min-height:96mm}
.pimg{border-radius:4mm;background-size:cover;background-position:center;position:relative}
.pimg.sm2{height:44mm;margin-top:3mm}
.tagb{position:absolute;left:4mm;top:4mm;color:#fff;font-size:20pt;font-weight:800;padding:1.5mm 4mm;border-radius:3mm}
.tagb.heat{background:var(--heat)}
.dark{display:grid;grid-template-columns:1.1fr 1fr;background:#14181C;color:#fff;border-radius:4mm;overflow:hidden;margin-bottom:4mm}
.dk-t{padding:6mm}
.dk-t h3{color:#fff;font-size:14pt;margin:1.5mm 0 2.5mm}
.dk-t p{font-size:8.8pt;opacity:.9}.dk-t p b{color:var(--sun)}
.dk-i{background-size:cover;background-position:center}
.dk-n{display:grid;grid-template-columns:repeat(3,1fr);gap:2mm;margin-top:4mm}
.dk-n b{display:block;font-size:14pt;font-weight:800;color:var(--brand)}.dk-n span{font-size:7.2pt;opacity:.8}

.split.r{grid-template-columns:1fr 1fr}
.split.r .pimg{min-height:80mm}
.quiet{display:grid;grid-template-columns:34mm 1fr 52mm;gap:5mm;align-items:center}
.q-k{background:var(--brand);color:#fff;border-radius:4mm;padding:5mm 3mm;text-align:center}
.q-k b{display:block;font-size:22pt;font-weight:800;line-height:1}.q-k span{font-size:11pt;font-weight:800;display:block}
.q-k small{font-size:7pt;opacity:.9;display:block;margin-top:2mm;line-height:1.3}
.q-l>div{display:flex;gap:2.5mm;align-items:center;padding:1.8mm 0;border-bottom:1px solid var(--line)}
.q-l>div:last-child{border:0}
.q-l i{font-style:normal;flex:none;width:5.5mm;height:5.5mm;border-radius:50%;background:var(--light);color:var(--brand-600);font-size:7.5pt;font-weight:800;display:flex;align-items:center;justify-content:center}
.q-l h4{margin:0}.q-l p{font-size:7.8pt;color:var(--muted)}
.q-u img{width:100%;display:block}

.sf{display:flex;gap:3.5mm;align-items:flex-start}
.sf img{width:24mm;height:24mm;border-radius:3mm;object-fit:cover;flex:none}
.sf h3{font-size:9.6pt}.sf p{font-size:8.2pt}
i.n{font-style:normal;display:inline-flex;width:5mm;height:5mm;border-radius:50%;background:var(--brand);color:#fff;font-size:7.5pt;align-items:center;justify-content:center;flex:none}
.curves{display:block;width:100%;height:auto;margin-top:2mm}
.ctrl4{display:grid;grid-template-columns:1.1fr 1fr 1fr;gap:3mm 4mm}
.ctrl4>div{display:flex;gap:2.5mm;align-items:flex-start;border:1px solid var(--line);border-radius:3mm;padding:2.8mm 3mm}
.ctrl4 p{font-size:7.8pt;color:#33433A;line-height:1.35}
.c4i{grid-row:span 2;flex-direction:column;align-items:center!important;justify-content:center;background:#14181C;border:0!important}
.c4i img{width:44mm;border-radius:2mm}
.c4i span{font-size:7.6pt;color:#fff;opacity:.85;text-align:center;margin-top:2mm}

.ilrow{grid-template-columns:100mm 1fr}
.pv4>div{display:flex;gap:2.5mm;align-items:flex-start;padding:2mm 0;border-bottom:1px solid var(--line)}
.pv4>div:last-child{border:0}
.pv4 p{font-size:8pt;color:#33433A}

.appw{display:grid;grid-template-columns:42mm 1fr;gap:6mm;align-items:center;margin-bottom:2mm}
.phone{background:#14181C;border-radius:7mm;padding:2.5mm;box-shadow:0 2mm 6mm rgba(0,0,0,.2)}
.phone img{width:100%;display:block;border-radius:5mm}
.app8{display:grid;grid-template-columns:1fr 1fr;gap:2.5mm}
.app8 div{display:flex;gap:2mm;align-items:center;background:var(--tint);border-radius:2.5mm;padding:2.3mm 3mm;font-size:8.4pt;font-weight:700;color:var(--darker)}
.cloud{display:block;width:100%;height:auto}
.three{display:grid;grid-template-columns:repeat(3,1fr);gap:4mm}
.three .card .ic{margin-bottom:1.5mm}
.three p{font-size:8pt;color:#33433A}

table.spec{width:100%;border-collapse:collapse;font-size:6.8pt;margin-bottom:3mm}
.spec thead th{background:var(--brand);color:#fff;font-size:8.2pt;font-weight:800;padding:1.6mm 1mm;text-align:center}
.spec thead th:first-child{text-align:left;padding-left:2mm;border-radius:2mm 0 0 0}
.spec thead th:last-child{border-radius:0 2mm 0 0}
.spec thead small{display:block;font-size:6.6pt;font-weight:600;opacity:.9}
.spec td,.spec tbody th{padding:.42mm 1mm;border-bottom:1px solid var(--line);text-align:center;line-height:1.25}
.spec tbody th{text-align:left;font-weight:600;color:#33433A;padding-left:2mm;width:40mm}
.spec tr.sec td{background:var(--light);color:var(--brand-600);font-weight:800;text-align:left;padding:.6mm 2mm;font-size:7pt}
.band.b8{padding:3.5mm 6mm;margin-bottom:0}
.b-mod{position:relative;display:grid;grid-template-columns:repeat(6,1fr);gap:2.5mm;padding:4mm 10mm 0}
.b-mod div{border:1.5px solid var(--brand);border-radius:3mm;padding:2.2mm 1mm;text-align:center}
.b-mod b{display:block;font-size:11pt;font-weight:800;color:var(--darker)}.b-mod span{font-size:7pt;color:var(--muted)}
.fit .card b{display:block;font-size:15pt;font-weight:800;color:var(--heat);margin-bottom:1mm}
.fit .card:first-child b{color:var(--brand)}.fit .card:last-child b{color:#3B7DD8}
.tip{margin-top:5mm}.tip .two{gap:5mm}
.pvt .mt{font-size:8.3pt}
.b8 .ctah{font-size:13pt;margin:.8mm 0 2mm}
.b8 .qr2 img{width:19mm;height:19mm}
"""


def main():
    SLUG = "REO-R290-Smart_brozura"
    html = (f'<!doctype html><html lang="cs"><head><meta charset="utf-8"><title>REO R290 Smart – produktová brožura | REO HEATING</title>'
            f'{FONTS}<style>{CSS}</style></head><body>{p1+p2+p3+p4+p5+p6+p7+p8}</body></html>')
    out = ROOT / f"{SLUG}.html"
    out.write_text(html, encoding="utf-8")
    pdf = ROOT / f"{SLUG}.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=8000",
                    f"--print-to-pdf={pdf}", out.as_uri()], check=True, capture_output=True)
    print("PDF", pdf)


if __name__ == "__main__":
    main()
