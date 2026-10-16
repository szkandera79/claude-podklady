"""Generuje studie.html (fáze 1 – technická koncepce) z výpočtů ve vypocty.py.
Spuštění z kořene repozitáře: python3 mobilni-kotelna-tc/univerzalni/src/gen_studie.py
"""
from pathlib import Path
import vypocty as C

OUT = Path(__file__).parent.parent / "studie.html"


def f(x, d=1):
    if x is None:
        return "—"
    s = f"{x:,.{d}f}".replace(",", " ").replace(".", ",")
    return s.replace(" ", " ")


def table(head, rows, cls=""):
    h = "".join(f"<th>{c}</th>" for c in head)
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tw"><table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


def tag(t):
    return f'<span class="tag t{t}">{t}</span>'


D, Z, O, Q = tag("D"), tag("Z"), tag("O"), tag("?")

# ------------------------------------------------------------------ 2 jednotky
unit_rows = []
for m in ("RH050", "RH060", "RHX50"):
    u = C.UNITS[m]
    for w in (35, 45, 55):
        unit_rows.append([f"<b>{u['label']}</b>" if w == 35 else "", f"W{w}"] +
                         [f(C.cap(m, w, t)) for t in C.TEMPS] +
                         [f(C.cap(m, w, -15) / C.cap(m, 35, 7) * 100, 0) + " %"])
unit_tbl = table(["Jednotka", "Voda", "A+7", "A+2", "A−7", "A−15", "A−20", "A−15 / nominál"], unit_rows, "num")

hi_rows = [[f"W{w}"] + [f(C.cap("RHX50", w, t)) for t in C.TEMPS] for w in (60, 65, 70)]
hi_tbl = table(["RH X50, voda", "A+7", "A+2", "A−7", "A−15", "A−20"], hi_rows, "num")

par_rows = [[u["label"], u["pump"], u["conn"], f(u["flow"]) + (" " + D if m == "RHX50" else " " + O),
             f"{u['el_kw']:.0f} kW / {u['amp']} A " + (D if m == "RHX50" else O), u["brk"], f"{u['mass']} kg {D}", u["dims"]]
            for m, u in C.UNITS.items()]
par_tbl = table(["Jednotka", "Oběhové čerpadlo", "Připojení", "Jm. průtok m³/h", "Max. příkon / proud", "Jištění", "Hmotnost", "Rozměry mm"], par_rows)

# ------------------------------------------------------------------ 3 konfigurace
def mixs(mix):
    return " + ".join(f"{n} × {C.UNITS[m]['label']}" for m, n in mix.items())


cfg = C.config_rows()
cfg_rows = []
for r in cfg:
    for w in (45, 55):
        cells = []
        for t in C.TEMPS:
            tot, n1 = r["res"][(w, t)]
            cells.append(f"{f(tot)}<small>N−1&nbsp;{f(n1)}</small>")
        cfg_rows.append([f"<b>{r['code']}</b>" if w == 45 else "", (mixs(r["mix"]) + f"<small>{r['units']} ks ÚT + RH050 TUV · nominál {f(r['nom'])} kW</small>") if w == 45 else "",
                         f"W{w}"] + cells)
cfg_tbl = table(["", "Sestava (jen vytápění)", "Voda", "A+7", "A+2", "A−7", "A−15", "A−20"], cfg_rows, "num cfg")

# ------------------------------------------------------------------ 4 otopná tělesa
rad_rows = []
for dsg in C.RAD_DESIGNS:
    rad_rows.append([f"{dsg[0]}/{dsg[1]} °C"] + [f(C.radiator_factor(dsg, op) * 100, 0) + " %" if op[0] <= dsg[0] else "—" for op in C.RAD_OPER])
rad_tbl = table(["Návrh soustavy", "provoz 55/45", "50/42", "60/50 (jen X50)", "70/60 (jen X50)"], rad_rows, "num")

# ------------------------------------------------------------------ 5 odhad zátěže
load_rows = []
for gj in (300, 500, 800, 1200):
    ua, p = C.design_load_from_consumption(gj)
    load_rows.append([f"{gj} GJ", f(gj * 0.85 / 3.6, 0) + " MWh", f(ua, 2) + " kW/K", f"<b>{f(p, 0)} kW</b>",
                      f(p * 0.55, 0) + "–" + f(p * 0.7, 0) + " kW"])
load_tbl = table(["Roční odběr CZT", "z toho ÚT (85 %)", "Měrná ztráta H", "Výkon při −15 °C", "Hala jen temperovaná (orient.)"], load_rows, "num")

# ------------------------------------------------------------------ 6 hydraulika
flow_rows = []
for ld in C.LOADS:
    flow_rows.append([f"{ld} kW", f(C.flow_m3h(ld, 5)), f(C.flow_m3h(ld, 10)), f(C.flow_m3h(ld, 15))])
flow_tbl = table(["Výkon", "ΔT 5 K (primár TČ)", "ΔT 10 K", "ΔT 15 K"], flow_rows, "num")

hose_rows = []
for ld in C.LOADS:
    for dt in (5, 10):
        q = C.flow_m3h(ld, dt)
        row = [f"{ld} kW" if dt == 5 else "", f"ΔT {dt} K · {f(q)} m³/h"]
        for dn, d in C.HOSE_ID.items():
            v, _ = C.dp_pair(q, d, 10)
            parts = [f(C.dp_pair(q, d, L)[1], 0) for L in C.LENGTHS]
            cls = "bad" if v > 1.5 else ("warn" if v > 1.0 else "ok")
            row.append(f'<span class="{cls}">{f(v, 2)} m/s</span><small>{" / ".join(parts)} kPa</small>')
        hose_rows.append(row)
hose_tbl = table(["Výkon", "Průtok", "DN40 (vnitřní 40 mm)", "DN50 (50 mm)", "DN65 (65 mm)"], hose_rows, "num hose")

trunk_rows = []
for name, q in (("1 × RH X50", 10.32 * 1.15), ("2 × RH X50", 2 * 10.32 * 1.15), ("2 × RH060 + 3 × RH050", 1.15 * (2 * 3.8 + 3 * 2.5)),
                ("RH X50 + 2 × RH060", 1.15 * (10.32 + 2 * 3.8))):
    cells = []
    for d in (50, 65, 80):
        v, dp = C.dp_pair(q, d, 6, eps_mm=0.05, zeta=4)
        cls = "bad" if v > 1.5 else ("warn" if v > 1.1 else "ok")
        cells.append(f'<span class="{cls}">{f(v, 2)} m/s</span><small>{f(dp, 1)} kPa</small>')
    trunk_rows.append([name, f(q)] + cells)
trunk_tbl = table(["Primár (kmen rozdělovač → kontejner, 2 × 6 m)", "Průtok m³/h (+15 %)", "DN50", "DN65", "DN80"], trunk_rows, "num")

x50min = C.cap("RHX50", 45, 7, "MIN")
rh050min = C.cap("RH050", 45, 7, "MIN")
ve, vn = C.expansion(1300)

# ------------------------------------------------------------------ 8 TUV
tuv_rows = []
for vol in (300, 600, 900, 1000):
    e, _ = C.heat_time(vol, 1)
    tuv_rows.append([f"{vol} l", f(e, 1) + " kWh"] + [f(C.heat_time(vol, kw)[1], 1) + " h" for kw in (5.5, 7.6, 9.8, 13.7)])
tuv_tbl = table(["Objem 10 → 55 °C", "Energie", "5,5 kW", "7,6 kW (RH050 A−15/W55)", "9,8 kW (A−7/W55)", "13,7 kW (A+7/W55)"], tuv_rows, "num")

coil_rows = []
for tt in (15, 30, 40, 45, 50, 53):
    coil_rows.append([f"{tt} °C"] + [f(C.coil_power(tt, area=a, u=u), 1) for a, u in ((3.3, 300), (3.3, 500), (6.6, 400), (9.9, 400))])
coil_tbl = table(["Teplota v zásobníku", "1 × 3,3 m², U 300", "1 × 3,3 m², U 500", "2 × 3,3 m², U 400", "3 × 3,3 m², U 400"], coil_rows, "num")

# ------------------------------------------------------------------ 10 elektro
el_rows = []
for r in cfg:
    i = r["el"] * 1000 / (3 ** 0.5 * 400 * 0.95)
    brk = next(b for b in (32, 40, 50, 63, 80, 100, 125) if b >= i * 1.1)
    cable = {32: "5 × 6", 40: "5 × 10", 50: "5 × 10", 63: "5 × 16", 80: "5 × 25", 100: "5 × 35", 125: "5 × 50"}[brk]
    plug = "CEE 63 A" if brk <= 63 else "CEE 125 A"
    el_rows.append([f"<b>{r['code']}</b>", mixs(r["mix"]) + " + RH050 TUV", f(r["el"], 0) + " kW", f(i, 0) + " A", f"3 × {brk} A", cable + " mm² Cu", plug])
el_tbl = table(["", "Sestava", "Max. soudobý příkon", "Proud (cos φ 0,95)", "Hlavní jistič", "Kabel H07RN-F do 25 m", "Připojení"], el_rows, "num")

# ------------------------------------------------------------------ 11 kotvení
tank_rows = []
for name, me, mf, h, b in C.TANKS:
    fr = C.transport_forces(me)
    mt, ms = C.tip_check(me, h, b)
    tank_rows.append([name, f"{me} kg", f"{mf} kg", f(mf * C.G / 1000 / 3, 1) + " kN", f(fr["vpred"], 2) + " kN", f(fr["bok"], 2) + " kN",
                      f'<span class="{"bad" if mt > ms else "ok"}">{f(mt, 2)} / {f(ms, 2)} kNm</span>'])
tank_tbl = table(["Nádrž", "Prázdná " + O, "Plná", "Na 1 nohu (3 nohy, plná)", "Přeprava 0,8 g vpřed", "0,5 g bok", "Klopení / stabilita (prázdná)"], tank_rows, "num")

# ------------------------------------------------------------------ 12 hluk
noise_rows = []
for name, lw in (("RH050 (W55)", 59), ("RH060 (W55)", 62), ("RH X50 (W55)", 66), ("RH X50 max.", 77), ("2 × RH X50 max.", C.sum_db(77, 77)),
                 ("2 × RH060 + 3 × RH050 (W55)", C.sum_db(62, 62, 59, 59, 59))):
    noise_rows.append([name, f(lw, 0) + " dB"] + [f(C.lp(lw, r), 0) for r in (5, 10, 20, 30, 50)])
noise_tbl = table(["Zdroj (LWA)", "LWA", "5 m", "10 m", "20 m", "30 m", "50 m"], noise_rows, "num")

rmin, rmax = C.ratio_check()

# ================================================================== SVG
HYD_SVG = """
<svg viewBox="0 0 980 440" role="img" aria-label="Koncepční hydraulické schéma mobilní kotelny">
<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" class="f-ink"/></marker></defs>
<rect x="10" y="20" width="300" height="400" class="zone"/><text x="22" y="40" class="lbl">VENKU · rámy TČ</text>
<rect x="340" y="20" width="460" height="400" class="zone2"/><text x="352" y="40" class="lbl">KONTEJNER 20'</text>
<rect x="830" y="20" width="140" height="400" class="zone"/><text x="842" y="40" class="lbl">ZÁKAZNÍK</text>
<g class="unit"><rect x="30" y="62" width="74" height="46"/><text x="67" y="83">TČ 1</text><text x="67" y="99" class="s">RH X50</text></g>
<g class="unit"><rect x="30" y="132" width="74" height="46"/><text x="67" y="153">TČ 2</text><text x="67" y="169" class="s">RH X50 / RH060</text></g>
<g class="unit"><rect x="30" y="202" width="74" height="46"/><text x="67" y="223">TČ n</text><text x="67" y="239" class="s">rezerva N+1</text></g>
<g class="pipe-h"><path d="M104 74H170V300" /><path d="M104 144H170"/><path d="M104 214H170"/></g>
<g class="pipe-c"><path d="M104 96H200V330"/><path d="M104 166H200"/><path d="M104 236H200"/></g>
<g class="dev"><circle cx="128" cy="74" r="6"/><circle cx="128" cy="144" r="6"/><circle cx="128" cy="214" r="6"/></g>
<text x="118" y="60" class="s">K · UV · FV</text>
<rect x="160" y="290" width="50" height="50" class="hdr"/><text x="185" y="318" class="s c">rozdělovač</text>
<text x="22" y="372" class="s">K zpětná klapka · UV uzávěry · FV filtr</text>
<text x="22" y="388" class="s">každá větev: čerpadlo (X50), vypouštění, odvzdušnění</text>
<text x="22" y="404" class="s">primár: glykol 30–35 % (doporučeno, kap. 7)</text>
<path d="M210 300H390" class="pipe-h" marker-end="url(#ar)"/><path d="M390 330H210" class="pipe-c" marker-end="url(#ar)"/>
<text x="232" y="292" class="s">2 potrubí DN65–80</text>
<rect x="390" y="280" width="44" height="70" class="phe"/><text x="412" y="368" class="s c">VS1</text><text x="412" y="382" class="s c">glykol/voda</text>
<path d="M434 292H500V110H520" class="pipe-h"/><path d="M520 250H470V338H434" class="pipe-c"/>
<rect x="520" y="80" width="70" height="190" rx="30" class="tank"/><text x="555" y="170" class="c">AKU</text><text x="555" y="188" class="s c">600–1 000 l</text>
<text x="555" y="204" class="s c">hydr. oddělení</text>
<path d="M590 110H700" class="pipe-h"/><path d="M700 250H590" class="pipe-c"/>
<circle cx="640" cy="110" r="9" class="pump"/><text x="640" y="96" class="s c">Č sek.</text>
<rect x="700" y="90" width="40" height="180" class="phe2"/><text x="720" y="288" class="s c">VS2</text><text x="720" y="302" class="s c">volitelně</text>
<path d="M740 110H880" class="pipe-h" marker-end="url(#ar)"/><path d="M880 250H740" class="pipe-c" marker-end="url(#ar)"/>
<text x="770" y="100" class="s">hadice DN50–65</text>
<rect x="880" y="80" width="70" height="190" class="cust"/><text x="915" y="170" class="c">otopná</text><text x="915" y="186" class="c">soustava</text>
<rect x="400" y="60" width="58" height="34" class="dev2"/><text x="429" y="81" class="s c">EN + PV</text>
<g class="unit"><rect x="30" y="300" width="74" height="40" class="tuvunit"/><text x="67" y="318">TČ TUV</text><text x="67" y="332" class="s">RH050</text></g>
<path d="M104 312H130V410H620V395" class="pipe-t"/><path d="M104 328H120V418H660V395" class="pipe-tc"/>
<rect x="600" y="330" width="90" height="62" rx="18" class="tank"/><text x="645" y="358" class="c">TUV</text><text x="645" y="374" class="s c">2–3 × 300 l / 1 000 l</text>
<path d="M690 345H880" class="pipe-t" marker-end="url(#ar)"/><text x="760" y="338" class="s">TV · C · SV</text>
<path d="M540 300V330" class="pipe-x"/><text x="470" y="318" class="s">přepínací ventil ÚT→TUV (záloha, dezinfekce)</text>
</svg>"""

PLAN_SVG = """
<svg viewBox="0 0 640 320" role="img" aria-label="Půdorys kontejneru 20 stop, měřítko 1 px = 10 mm">
<rect x="20" y="30" width="590" height="235" class="cont"/>
<text x="20" y="20" class="s">vnitřní 5 898 × 2 352 mm · světlá výška 2 393 mm (HC 2 698 mm)</text>
<rect x="602" y="34" width="8" height="227" class="door"/><text x="575" y="290" class="s">dveře</text>
<circle cx="80" cy="90" r="50" class="tank"/><text x="80" y="88" class="c">AKU</text><text x="80" y="102" class="s c">1 000 l Ø 1 000</text>
<circle cx="167" cy="72" r="33" class="tank"/><circle cx="237" cy="72" r="33" class="tank"/><circle cx="307" cy="72" r="33" class="tank"/>
<text x="237" y="122" class="s c">TUV 3 × 300 l (Ø ≈ 650 s izolací)</text>
<circle cx="190" cy="90" r="50" class="future"/><text x="190" y="156" class="s c fut">budoucí TUV 1 000 l</text>
<rect x="30" y="35" width="320" height="10" class="frame"/><text x="360" y="44" class="s">zadní kotevní rám (svislé sloupky)</text>
<rect x="470" y="35" width="110" height="40" class="el"/><text x="525" y="60" class="c">rozvaděč</text>
<rect x="50" y="215" width="380" height="45" class="hyd"/><text x="240" y="242" class="c">hydraulická stěna: VS1, čerpadla, expanze, filtry, měření</text>
<rect x="440" y="225" width="100" height="35" class="pan"/><text x="490" y="247" class="s c">přípojný panel</text>
<path d="M30 170H595" class="aisle"/><text x="380" y="165" class="s">servisní ulička ≥ 800 mm</text>
<text x="20" y="300" class="s">Těžké nádrže u uzavřeného čela a nad příčníky podlahy; těžiště ≤ ± 10 % délky od středu</text>
</svg>"""

# ================================================================== HTML
CSS = """
:root{
/* Layout: technická zpráva — úzký sloupec textu, široké tabulky v posuvných rámech, zelená REO jen jako značka a stav */
--bg:#f6f8f6;--paper:#ffffff;--ink:#14201a;--muted:#55645c;--line:#d5ddd8;--accent:#26804b;--accent-soft:#e9f6ee;
--warn:#a35f00;--warn-soft:#fff3df;--bad:#b3261e;--bad-soft:#fdeceb;--ok:#26804b;
--hot:#c4472f;--cold:#2f6fb0;--tuv:#b07a12;
--f-display:"Barlow Condensed","Arial Narrow",sans-serif;--f-body:"IBM Plex Sans",system-ui,sans-serif;--f-mono:"IBM Plex Mono",ui-monospace,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0f1512;--paper:#161e1a;--ink:#e3ebe6;--muted:#9aaba1;--line:#2c3832;--accent:#5cc488;--accent-soft:#1b2c22;
--warn:#f0b35a;--warn-soft:#2e2414;--bad:#f2867e;--bad-soft:#331a19;--ok:#5cc488;--hot:#ef7d66;--cold:#6fa8e3;--tuv:#e0b04e;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0f1512;--paper:#161e1a;--ink:#e3ebe6;--muted:#9aaba1;--line:#2c3832;--accent:#5cc488;--accent-soft:#1b2c22;
--warn:#f0b35a;--warn-soft:#2e2414;--bad:#f2867e;--bad-soft:#331a19;--ok:#5cc488;--hot:#ef7d66;--cold:#6fa8e3;--tuv:#e0b04e;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font:15px/1.6 var(--f-body);padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:0 64px}
main{max-width:1040px;margin:0 auto}
header{padding-block:40px 24px;border-bottom:2px solid var(--ink);margin-bottom:8px}
.eyebrow{font:600 12px/1 var(--f-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--accent)}
h1{font:600 clamp(34px,6vw,56px)/1 var(--f-display);margin:10px 0 12px;text-wrap:balance;letter-spacing:.005em}
h2{font:600 28px/1.1 var(--f-display);margin:0 0 12px;text-wrap:balance;display:flex;gap:12px;align-items:baseline}
h2 .n{font:500 14px var(--f-mono);color:var(--accent)}
h3{font:600 17px/1.3 var(--f-body);margin:22px 0 8px}
p,li{max-width:70ch}
.lead{font-size:17px;color:var(--muted);max-width:68ch}
.meta{display:flex;flex-wrap:wrap;gap:8px 20px;font:13px var(--f-mono);color:var(--muted);margin-top:16px}
section{padding-block:28px;border-bottom:1px solid var(--line)}
nav.toc{display:flex;flex-wrap:wrap;gap:6px 14px;font:13px var(--f-mono);padding-block:14px}
nav.toc a{color:var(--muted);text-decoration:none}nav.toc a:hover,nav.toc a:focus-visible{color:var(--accent);text-decoration:underline}
a{color:var(--accent)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.tw{overflow-x:auto;margin:12px 0 6px;border:1px solid var(--line);background:var(--paper)}
table{border-collapse:collapse;width:100%;font-size:13.5px}
th{font:600 11.5px/1.3 var(--f-mono);text-transform:uppercase;letter-spacing:.04em;color:var(--muted);text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);background:var(--accent-soft);white-space:nowrap}
td{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
tr:last-child td{border-bottom:0}
table.num td{font-variant-numeric:tabular-nums}
table.num td:not(:first-child):not(:nth-child(2)){font-family:var(--f-mono);font-size:13px;white-space:nowrap}
table.cfg td:nth-child(2){font-family:var(--f-body);white-space:normal;min-width:190px}
table.cfg td:nth-child(3){font-family:var(--f-mono)}
td small{display:block;color:var(--muted);font:11.5px var(--f-mono);white-space:nowrap}
table.cfg td:nth-child(2) small{white-space:normal;font-family:var(--f-body)}
.cap{font-size:13px;color:var(--muted);margin:4px 0 0}
.tag{display:inline-block;font:600 10.5px/1 var(--f-mono);padding:3px 5px;border-radius:3px;vertical-align:1px;border:1px solid currentColor}
.tD{color:var(--accent)}.tZ{color:var(--cold)}.tO{color:var(--warn)}.t\\?{color:var(--bad)}
.ok{color:var(--ok)}.warn{color:var(--warn)}.bad{color:var(--bad);font-weight:600}
.verdict{display:grid;gap:10px;margin:8px 0 0;padding:0;list-style:none}
.verdict li{max-width:none;padding:12px 14px 12px 16px;background:var(--paper);border:1px solid var(--line);border-left:4px solid var(--line)}
.verdict li.r{border-left-color:var(--bad)}.verdict li.y{border-left-color:var(--warn)}.verdict li.g{border-left-color:var(--ok)}
.verdict b{display:block;margin-bottom:2px}
.risk td:first-child{font:600 12px var(--f-mono);white-space:nowrap}
.sev{font:600 11px var(--f-mono);padding:2px 6px;border-radius:3px;white-space:nowrap}
.sev.r{background:var(--bad-soft);color:var(--bad)}.sev.y{background:var(--warn-soft);color:var(--warn)}.sev.g{background:var(--accent-soft);color:var(--ok)}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr));gap:18px}
.grid2>*{min-width:0}
.box{background:var(--paper);border:1px solid var(--line);padding:14px 16px}
.box h3{margin-top:0}
.formula{font:13.5px var(--f-mono);background:var(--accent-soft);padding:8px 12px;display:block;margin:8px 0;overflow-x:auto;white-space:nowrap}
.fig{overflow-x:auto;background:var(--paper);border:1px solid var(--line);padding:10px;margin:12px 0}
.fig svg{min-width:720px;width:100%;height:auto;display:block}
.fig.plan svg{min-width:600px}
svg text{font:12px var(--f-body);fill:var(--ink)}svg text.s{font-size:10.5px;fill:var(--muted)}svg text.lbl{font:600 11px var(--f-mono);letter-spacing:.08em;fill:var(--muted)}
svg text.c{text-anchor:middle}svg .unit text{text-anchor:middle}svg text.fut{fill:var(--accent)}
.zone{fill:var(--bg);stroke:var(--line)}.zone2{fill:var(--accent-soft);stroke:var(--line)}
.unit rect{fill:var(--paper);stroke:var(--ink);stroke-width:1.4}.unit rect.tuvunit{stroke:var(--tuv)}
.pipe-h{fill:none;stroke:var(--hot);stroke-width:3}.pipe-c{fill:none;stroke:var(--cold);stroke-width:3}
.pipe-t{fill:none;stroke:var(--tuv);stroke-width:2.5}.pipe-tc{fill:none;stroke:var(--tuv);stroke-width:2.5;stroke-dasharray:6 4}
.pipe-x{fill:none;stroke:var(--muted);stroke-width:2;stroke-dasharray:3 3}
.dev circle{fill:var(--paper);stroke:var(--ink)}.hdr{fill:var(--paper);stroke:var(--ink);stroke-width:1.4}
.phe{fill:var(--paper);stroke:var(--accent);stroke-width:2}.phe2{fill:none;stroke:var(--muted);stroke-width:1.5;stroke-dasharray:5 4}
.tank{fill:var(--paper);stroke:var(--ink);stroke-width:1.4}.pump{fill:var(--paper);stroke:var(--ink);stroke-width:1.4}
.cust{fill:var(--bg);stroke:var(--ink)}.dev2{fill:var(--paper);stroke:var(--muted)}.f-ink{fill:var(--ink)}
.cont{fill:var(--paper);stroke:var(--ink);stroke-width:2}.door{fill:var(--muted)}.future{fill:none;stroke:var(--accent);stroke-width:1.5;stroke-dasharray:6 4}
.frame{fill:var(--muted)}.el{fill:var(--warn-soft);stroke:var(--warn)}.hyd{fill:var(--accent-soft);stroke:var(--accent)}.pan{fill:var(--bg);stroke:var(--ink)}
.aisle{stroke:var(--line);stroke-width:1;stroke-dasharray:4 4}
ol.check{padding-left:20px}ol.check li{margin:4px 0}
.cols{columns:2 320px;column-gap:28px}.cols>div{break-inside:avoid;margin-bottom:14px}
.cols h3{margin-top:0}
ul.tight li{margin:3px 0}
footer{padding-block:24px;color:var(--muted);font-size:13px}
@media (max-width:560px){h2{font-size:24px}body{font-size:14.5px}}
"""

RISKS = [
    ("R1", "r", "Nominální výkon ≠ výkon v mrazu",
     "RH050/RH060 dávají při A−15/W55 jen 51–52 % výkonu A7/W35, RH X50 50 %. Sestava „50 kW nominálně“ z RH0x dodá v mrazu ≈ 30 kW.",
     "Navrhovat a nabízet výhradně výkon při návrhové teplotě a skutečné teplotě vody; nominál uvádět jen informativně."),
    ("R2", "r", "Teplota topné vody u stávající soustavy CZT",
     "Soustavy navržené na 90/70 nebo 80/60 předají při 55/45 jen 41–52 % výkonu. Hala s teplovzdušnými jednotkami může být ještě citlivější.",
     "Na obhlídce zjistit typ a počet otopných těles a skutečnou teplotu v mrazu z historie CZT; u vysokoteplotních soustav jen RH X50 (do 70–75 °C) a s nižším výkonem."),
    ("R3", "r", "Voda bez glykolu ve venkovních jednotkách",
     "Návod RH X50 výslovně doporučuje glykol; protimrazová funkce jednotek funguje jen pod napětím a s běžícím čerpadlem. Mechanické protimrazové ventily chrání jen jednotku, ne rozdělovač a kmen; při dlouhém výpadku mohou vypustit velkou část soustavy.",
     "Doporučeno: glykolový primár (jednotky, rozdělovač, kmen) + deskový výměník VS1 v kontejneru. Varianta jen s vodou viz kap. 7 a vyžaduje přijetí zbytkového rizika."),
    ("R4", "r", "Redundance N+1 platí jen při malé zátěži",
     "2 × RH X50 = 49,6 kW při A−15/W55. Skutečná N+1 jen do ≈ 25 kW zátěže. Společné prvky (rozdělovač, kmen, VS1, AKU, rozvaděč, přívod) zůstávají jednoduchým místem poruchy.",
     "Nabízet „provozní rezervu za běžných teplot“, ne garantovanou N+1 v návrhovém mrazu; zdvojit čerpadla, nouzový režim jednotek bez kaskádového řízení."),
    ("R5", "r", "Neznámá tepelná ztráta a teplotní spád zákazníka",
     "Bez dat nelze rozhodnout mezi variantami A a B; výrobní hala může mít i přes temperování výkon násobně vyšší než administrativa.",
     "Výkon odvodit z fakturace CZT (kap. 5) a z obhlídky; do té doby nenabízet výkon ani teplotu."),
    ("R6", "y", "Smíšená kaskáda RH0x + RH X50",
     "RH X50 má nativní kaskádu až 8 jednotek (adresy, společné čidlo, RS485). U RH030–RH060 kaskáda doložena není (jen Wi‑Fi Tuya, parametry „jednotky online / řídicí adresa“). Smíšená kaskáda v jednom řízení výrobce je neověřená.",
     "Externí kaskádový regulátor (PLC) s povolením a žádanou teplotou pro každou jednotku; od výrobce vyžádat Modbus mapu RS485 pro obě řady."),
    ("R7", "y", "Elektrický příkon zákazníka",
     "2 × RH X50 + TUV = ≈ 47 kW, tj. hlavní jistič 3 × 80 A. Objekt dosud vytápěný CZT takovou rezervu často nemá.",
     "Na obhlídce zjistit hlavní jistič a rezervovaný příkon; regulace s omezením počtu běžících kompresorů podle dostupného proudu."),
    ("R8", "y", "Hluk RH X50",
     "LWA 66 dB při W55, až 77 dB při maximu. Dvě jednotky na plný výkon dávají ve 20 m ≈ 46 dB(A) – nad nočním limitem 40 dB pro chráněný venkovní prostor staveb.",
     "Zjistit vzdálenost nejbližší obytné zástavby; noční omezení výkonu, umístění, případně posouzení hlukovou studií."),
    ("R9", "y", "Legionella a teplota TUV",
     "RH050 ohřeje vodu přes výměník reálně na 50–53 °C (teplota vody z TČ max. 60–65 °C a výpočet přenosu výměníku). Termickou dezinfekci 65–70 °C sama nezvládne.",
     "Dezinfekce přes přepínací ventil z RH X50 (výstup až 78 °C) nebo malá elektrická vložka jen pro dezinfekci; pravidelný cyklus v regulaci."),
    ("R10", "y", "Přeprava a manipulace",
     "Nádrže se smí převážet jen vypuštěné včetně výměníků; zbytková voda v zimě zamrzne. Plná AKU 1 000 l zatíží každou nohu ≈ 3,8 kN – bodově do podlahy kontejneru nelze.",
     "Roznášecí rám na příčníky, kotvení dole i nahoře, přepravní postup s profouknutím výměníků; statické posouzení autorizovanou osobou."),
    ("R11", "y", "Rozměr nádrže 1 000 l vs. kontejner",
     "Klopná výška nádrže 1 000 l (Ø 790–1 000 × ≈ 2 050 mm) je 2,20–2,28 m; standardní kontejner má dveře ≈ 2,28 m a vnitřní výšku 2,39 m.",
     "Ověřit výkres nádrže; izolaci montovat až po usazení, případně kontejner High Cube."),
    ("R12", "g", "Ceny a podklady zadavatele",
     "Nová AKU 1 000 l za 5 000 Kč bez DPH je výrazně pod obvyklou cenou; tabulky RH050/RH060 mají v každém bodě konstantní poměr 1,48–1,50, jsou tedy pravděpodobně odvozené, ne měřené.",
     "Potvrdit, co cena AKU zahrnuje (izolace, nátrubky, tlak). Výkony RH0x ověřit protokolem nebo měřením jedné jednotky."),
]
risk_rows = [[code, f'<span class="sev {s}">{ {"r": "kritické", "y": "významné", "g": "k ověření"}[s] }</span>', f"<b>{t}</b><br>{d}", m] for code, s, t, d, m in RISKS]
risk_tbl = table(["", "Závažnost", "Riziko a důvod", "Opatření"], risk_rows, "risk")

HTML = f"""<title>Mobilní kotelna REO</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;600&display=swap">
<style>{CSS}</style>
<main>
<header>
<div class="eyebrow">REO HEATING · studie proveditelnosti · fáze 1 z 3</div>
<h1>Univerzální mobilní kotelna s tepelnými čerpadly</h1>
<p class="lead">Technická koncepce a kritická rizika pro opakovaně pronajímanou kotelnu 50–100 kW: výkonové konfigurace, hydraulika, ochrana proti zamrznutí, TUV, elektro, kontejner a kotvení. Rozpočet, cenová mapa pronájmů, ekonomika a smlouva navazují ve fázích 2 a 3 po rozhodnutí o konceptu.</p>
<div class="meta"><span>16. 10. 2026</span><span>podklad k rozhodnutí, ne prováděcí ani statický projekt</span>
<span>{D} dokument výrobce</span><span>{Z} zadavatel</span><span>{O} odborný odhad</span><span>{Q} nutno ověřit</span></div>
</header>
<nav class="toc" aria-label="Obsah">
<a href="#verdikt">Verdikt</a><a href="#rizika">Rizika</a><a href="#vykony">Výkony</a><a href="#konfigurace">Konfigurace</a><a href="#teplota">Teplota vody</a>
<a href="#zatez">Odhad zátěže</a><a href="#hydraulika">Hydraulika</a><a href="#mraz">Mráz</a><a href="#tuv">TUV</a><a href="#regulace">Regulace</a>
<a href="#elektro">Elektro</a><a href="#kontejner">Kontejner</a><a href="#hluk">Hluk</a><a href="#overit">Ověřit</a><a href="#obhlidka">Obhlídka</a><a href="#dalsi">Další postup</a>
</nav>

<section id="verdikt">
<h2><span class="n">00</span>Verdikt technického oponenta</h2>
<ul class="verdict">
<li class="r"><b>Varianta A z RH050/RH060 je pro 50–70 kW skutečného výkonu nevhodná.</b>Pro ≈ 50 kW při −15 °C nestačí ani 5 jednotek pro vytápění (47,6 kW při W45, 45,6 kW při W55) + 1 pro TUV — tedy 6 venkovních jednotek, 6 větví a 6 přívodů. Smysl má jen pro malé objekty do ≈ 30 kW nebo jako doplněk RH X50.</li>
<li class="g"><b>Jádrem flotily má být RH X50.</b>Ověřeno z výkonové tabulky výrobce: 49,3 kW při A7/W35, 24,8 kW při A−15/W55 a 20,8 kW při A−20/W55. Vaše hodnoty „50 / 25 kW“ odpovídají. RH X50 navíc umí výstup až 78 °C a nativní kaskádu.</li>
<li class="y"><b>Druhá RH X50 je hlavně výkonová, ne záložní.</b>2 × RH X50 = 49,6 kW při A−15/W55. Redundance N+1 platí jen při zátěži do ≈ 25 kW, tedy za běžných zimních teplot, ne v návrhovém mrazu.</li>
<li class="r"><b>Voda bez glykolu je u nehlídané pronajaté technologie nejslabší místo návrhu.</b>Doporučuji glykolový primár venku a deskový výměník v kontejneru; ztráta ≈ 2–3 K na výměníku stojí řádově 5–7 % COP, ale odstraní riziko zamrznutí jednotek, rozdělovače i kmene při výpadku proudu.</li>
<li class="y"><b>TUV pro ≈ 20 zaměstnanců je malá úloha.</b>Bez sprch ≈ 200–400 l/den, se sprchami po směně až ≈ 1 000 l/den. Stačí 2 × 300 l ze skladu, třetí jen při sprchách. RH050 ohřeje 600 l za ≈ 4 h i při −15 °C. Nová TUV 1 000 l za 65 000 Kč se pro první zakázku nevyplatí; rám ji ale má umožnit.</li>
<li class="y"><b>Rozhoduje teplota, kterou budova potřebuje.</b>Náhrada CZT znamená často radiátory 90/70 nebo 80/60. Při 55/45 dodají jen 41–52 % výkonu. Bez tohoto údaje z obhlídky nelze kotelnu ani nacenit.</li>
<li class="g"><b>Kontejner 20' je správná volba, 10' jen pro malou verzi.</b>10' (vnitřní ≈ 2,83 m) pojme AKU a 2 × TUV 300 l, ale bez servisního přístupu a bez možnosti 1 000 l TUV. Pro univerzální kotelnu 20', ideálně High Cube.</li>
</ul>
</section>

<section id="rizika">
<h2><span class="n">01</span>Kritická rizika</h2>
{risk_tbl}
</section>

<section id="vykony">
<h2><span class="n">02</span>Výkony jednotek: nominální vs. dostupný</h2>
<p>Topný výkon při maximálních otáčkách kompresoru (kW) podle výkonových tabulek výrobce {D}. Hodnoty zahrnují odtávání tak, jak je uvádí výrobce; u RH0x jde o tabulky dodané k datovým listům.</p>
{unit_tbl}
<p class="cap">„Nominál“ = A7/W35 při max. výkonu. Tabulky RH060 a RH050 mají v každém bodě poměr {f(rmin, 2)}–{f(rmax, 2)} — pravděpodobně jsou odvozené jedna z druhé {Q}.</p>
<h3>RH X50 při vyšších teplotách vody</h3>
{hi_tbl}
<p class="cap">RH030–RH060: vytápění do 70 °C, TUV do 65 °C {D}, výkonová data ale jen do W55. Pro W60–W65 nemáme od výrobce žádná čísla {Q}.</p>
<h3>Parametry pro návrh</h3>
{par_tbl}
<p class="cap">Elektrické hodnoty RH050/RH060 jsou odhad z tabulky příkonu; závazné jsou typové štítky {Q}. Ve skladu je potřeba rozlišit RH050 1f a 3f — 1fázové jednotky do třífázové kaskády nesymetricky zatěžují přívod.</p>
</section>

<section id="konfigurace">
<h2><span class="n">03</span>Výkonové konfigurace pro vytápění</h2>
<p>Součet výkonů jednotek pro vytápění (kW) a pod ním výkon po výpadku největší jednotky (N−1). Jednotka TUV se do vytápění nepočítá.</p>
{cfg_tbl}
<div class="grid2">
<div class="box"><h3>Varianta A — RH050 / RH060</h3>
<ul class="tight"><li><b>A1</b> „50 kW“ nominálně dá při −15 °C / W55 jen 30 kW.</li>
<li><b>A2</b> „70 kW“ nominálně dá 38 kW, N−1 27 kW.</li>
<li><b>A3</b> s 5 jednotkami pro ÚT dosáhne jen 47,6 kW při W45 a 45,6 kW při W55.</li>
<li>Výhoda: jemná modulace od ≈ 3 kW, levné náhradní jednotky, vestavěná čerpadla.</li>
<li>Nevýhoda: 6 větví, 6 přívodů, 6 × odtávání, kaskáda RH0x nedoložená, nejvyšší pracnost montáže na každé zakázce.</li></ul></div>
<div class="box"><h3>Varianta B — RH X50</h3>
<ul class="tight"><li><b>B1</b> stačí na ≈ 25 kW při −15 °C / W55 (např. jen administrativa).</li>
<li><b>B2</b> = 49,6 kW při −15 °C / W55, 66 kW při −7 °C. Pro první zákazníka pravděpodobná sestava.</li>
<li><b>B3</b> (X50 + 2 × RH060) dává podobný výkon jako B2, jemnější modulaci od ≈ 4 kW, ale nižší N−1 v mrazu (22,8 vs. 24,8 kW) a smíšené řízení.</li>
<li>Minimální výkon RH X50 je {f(x50min)} kW (A7/W45); v přechodném období bude cyklovat bez dostatečné akumulace (kap. 6).</li>
<li>Bez vestavěného čerpadla → vlastní čerpadlo a zpětná klapka v každé větvi.</li></ul></div>
</div>
<h3>Doporučení</h3>
<p>Flotilu stavět na RH X50 (B2 jako standard, B1 pro malé objekty). Pro TUV použít RH050 3f. Druhou RH X50 nepovažovat za rezervu, ale za druhý výkonový stupeň. Pokud je redundance v mrazu podmínkou zákazníka, nabídnout třetí jednotku (RH X50 nebo 2 × RH060) jako příplatkovou výbavu.</p>
</section>

<section id="teplota">
<h2><span class="n">04</span>Teplota topné vody u stávající soustavy</h2>
<p>Výkon otopných těles při nižší teplotě vody, vnitřní teplota 20 °C, exponent n = 1,3 {O}:</p>
<code class="formula">Φ / Φn = (ΔT_ln,provoz / ΔT_ln,návrh)^n,   ΔT_ln = (t_př − t_zp) / ln((t_př − t_i) / (t_zp − t_i))</code>
{rad_tbl}
<p>Budova, která v mrazu skutečně potřebovala 85–90 °C z CZT, se s tepelným čerpadlem při 55 °C nevytopí, i když má kotelna „dost kW“. Soustavy bývají předimenzované, proto rozhoduje skutečná teplota přívodu z historie výměníkové stanice v posledních mrazech, ne projektovaný spád. Hala, která je jen temperovaná na 12–15 °C, je na tom lépe (větší rozdíl teplot vzduch–voda).</p>
</section>

<section id="zatez">
<h2><span class="n">05</span>Odhad potřebného výkonu z odběru tepla</h2>
<p>Dokud neznáme tepelnou ztrátu, nejspolehlivější je zpětný přepočet z vyúčtování CZT (GJ za rok, ideálně měsíční hodnoty):</p>
<code class="formula">H = Q_ÚT / (D × 24 h),   P_návrh = H × (t_i − t_e)   · D ≈ 3 500 K·den, t_i = 19 °C, t_e = −15 °C, TUV ≈ 15 % odběru {O}</code>
{load_tbl}
<p class="cap">Měsíční odběry v nejchladnějším měsíci zpřesní výsledek nejvíc: P ≈ Q_měsíc / (dní × 24 h) × (t_i − t_e) / (t_i − t_e,měsíc).</p>
</section>

<section id="hydraulika">
<h2><span class="n">06</span>Hydraulické řešení</h2>
<div class="fig">{HYD_SVG}</div>
<p class="cap">Koncept. Primár: jednotky → venkovní rozdělovač → 2 potrubí → VS1 → AKU. Sekundár: AKU → zákazník, volitelně přes VS2. TUV: samostatná jednotka a okruh, přepínací ventil z ÚT jako záloha a pro dezinfekci.</p>
<div class="grid2">
<div class="box"><h3>Průtoky</h3>
<code class="formula">V̇ [m³/h] = P [kW] / (1,163 × ΔT [K])</code>
{flow_tbl}
<p class="cap">RH X50 jmenovitě 10,32 m³/h, tlaková ztráta jednotky až 80 kPa {D}; čerpadlo dimenzovat na 1,1–1,2 × jm. průtoku {D}.</p></div>
<div class="box"><h3>Kmen mezi rozdělovačem a kontejnerem</h3>
{trunk_tbl}
<p class="cap">Ocel / nerez, ε 0,05 mm, ζ = 4. Cíl ≤ 1,0–1,2 m/s. Pro 2 × RH X50 je kmen <b>DN80</b>, DN65 jen do ≈ 6 m.</p></div>
</div>
<h3>Je společný rozdělovač problém?</h3>
<p>Ne, pokud je navržen jako <b>nízkoztrátový</b> a každá větev má vlastní čerpadlo. Problém nastává, když:</p>
<ul class="tight">
<li>jednotky bez zpětné klapky — stojící jednotka se protéká zpětně a míchá přívod se zpátečkou. <b>Zpětná klapka v každé větvi je povinná.</b></li>
<li>kmen má vyšší ztrátu než větve — čerpadla jednotek se navzájem ovlivňují a malá jednotka (RH050 s vestavěným čerpadlem 9 m) nedosáhne průtoku. Proto kmen DN65–80 a AKU / VS1 jako hydraulický oddělovač.</li>
<li>pracuje jen jedna malá jednotka ve velkém objemu — teplota v rozdělovači reaguje pomalu, kaskádová regulace musí řídit podle čidla v AKU, ne podle výstupu jednotky.</li>
<li>průtok primáru je nižší než sekundáru — AKU pak míchá zpátečku do přívodu k zákazníkovi. Primární průtok ≥ 1,1 × sekundární, nebo regulovat sekundár podle teploty v AKU.</li>
</ul>
<h3>Akumulace a expanze</h3>
<code class="formula">V_min = P_min × t_běh / (c × ΔT) = {f(x50min)} kW × 600 s / (4,18 × 5 K) = {f(C.aku_min(x50min), 0)} l</code>
<p>Pro RH X50 na minimální výkon a 10 min běhu kompresoru je potřeba ≈ {f(C.aku_min(x50min), 0)} l (RH050: {f(C.aku_min(rh050min), 0)} l). Dvě skladové AKU 300 l (600 l) jsou pro jednu RH X50 na hraně, pro dvě a pro odtávání doporučuji AKU 1 000 l. Expanze vlastního okruhu kontejneru (≈ 1 300 l, 10 → 60 °C, p₀ 1,0 bar, pojistný ventil 3 bar): roztažnost ≈ {f(ve, 0)} l, nádoba ≈ {f(vn, 0)} l → <b>80 l</b> {O}. Glykolový primár má vlastní expanzi 25–35 l.</p>
<h3>Hadice k zákazníkovi</h3>
<p>Rychlost a tlaková ztráta přívod + zpátečka pro délky 5 / 10 / 20 / 30 m (hladká EPDM hadice, 2 rychlospojky na hadici, ζ = 8) {O}:</p>
{hose_tbl}
<p class="cap"><span class="ok">zeleně</span> ≤ 1,0 m/s, <span class="warn">oranžově</span> 1,0–1,5 m/s, <span class="bad">červeně</span> &gt; 1,5 m/s. Za AKU je ΔT dané soustavou zákazníka (obvykle 10–15 K), proto pro 50–70 kW stačí <b>DN50</b>, pro 100 kW a delší trasy <b>DN65</b>. DN40 jen do 50 kW a 10 m. Vlnovcové nerezové hadice mají ztrátu 2–3× vyšší.</p>
<h3>Vodní a TUV přípojky</h3>
<p>Studená voda DN25 (PE nebo pitná hadice s atestem), výstup TUV DN25, cirkulace DN20; všechny izolované, s uzávěry na panelu kontejneru. U pitné vody pouze materiály s atestem pro styk s pitnou vodou a zpětný ventil / oddělovač na přívodu {Q}.</p>
</section>

<section id="mraz">
<h2><span class="n">07</span>Ochrana proti zamrznutí</h2>
<div class="grid2">
<div class="box"><h3>M1 — jen voda (váš záměr)</h3>
<ul class="tight">
<li>Mechanické protimrazové ventily na přívodu i zpátečce každé jednotky, v nejnižším bodě, s volným odtokem (otevírají ≈ 3 °C, údaj výrobce ventilu {Q}).</li>
<li>Další ventily na nejnižších bodech rozdělovače a kmene — jednotky samotné nestačí.</li>
<li>Zpětné klapky tak, aby ventil nevypouštěl celou AKU a soustavu zákazníka: oddělit venkovní část motorovými uzávěry bez proudu zavřenými (NC).</li>
<li>Záložní zdroj (UPS) pro čerpadla primáru a regulaci, alarm výpadku a teploty přes vzdálený monitoring.</li>
<li>Jednotky trvale pod napětím (jejich vlastní protimrazová funkce), topné kabely na venkovním potrubí.</li>
<li><b>Zbytkové riziko:</b> při výpadku proudu na hodiny v mrazu ventily pouští vodu, automatické doplňování vypouští dál, bez doplňování klesne tlak a jednotky se nespustí. Po obnovení proudu je nutný výjezd servisu.</li></ul></div>
<div class="box"><h3>M2 — glykolový primár (doporučuji)</h3>
<ul class="tight">
<li>Jednotky, rozdělovač a kmen naplněné propylenglykolem 30–35 % (ochrana do −15 až −18 °C), ≈ 150–250 l {O}.</li>
<li>Deskový výměník VS1 v kontejneru; AKU, TUV a zákazník zůstávají na vodě.</li>
<li>Výpadek proudu, porucha čerpadla ani odstavení jednotky nehrozí zamrznutím. Při přepravě se primár nemusí vypouštět.</li>
<li>Ztráta: ≈ 2–3 K na VS1 a nižší tepelná kapacita směsi → ≈ 5–7 % COP, vyšší příkon čerpadel {O}.</li>
<li>Návod RH X50 glykol výslovně doporučuje {D}.</li>
<li>TUV jednotka RH050: buď také glykol a vlastní malý výměník, nebo M1 s ventily (malý objem, oddělená větev).</li></ul></div>
</div>
<p><b>Závěr:</b> samotné protimrazové ventily nepovažuji pro pronajímanou kotelnu bez trvalé obsluhy za dostatečně bezpečné řešení. Pokud zůstane M1, musí smlouva řešit odpovědnost za výpadek napájení na straně zákazníka a zákazník musí mít povinnost okamžitě hlásit výpadek.</p>
</section>

<section id="tuv">
<h2><span class="n">08</span>Příprava TUV</h2>
<div class="grid2">
<div class="box"><h3>Doba ohřevu</h3>
<code class="formula">t = V × 1,163 × (t₂ − t₁) / P</code>
{tuv_tbl}</div>
<div class="box"><h3>Přenos výměníku (kW)</h3>
<code class="formula">Q = U × A × ΔT_ln,  voda z TČ 60/55 °C</code>
{coil_tbl}
<p class="cap">U = 300–500 W/m²K pro hladkou trubkovou spirálu s přirozenou konvekcí {O}; přesné hodnoty a tlakovou ztrátu musí dát výkres výměníku.</p></div>
</div>
<p><b>Plocha 3,2–3,4 m² není limitem na začátku ohřevu, ale na jeho konci.</b> Při 60 °C z TČ dodá jeden výměník při 50 °C v zásobníku ≈ 7–12 kW, při 53 °C už jen ≈ 4–7 kW. RH050 (7,6 kW při −15 °C / W55) tedy zásobník ohřeje, ale rozumně jen na 50–53 °C. Při zapojení 2–3 zásobníků paralelně (Tichelmann) se plocha sčítá a cílová teplota se zvedne o 1–3 K. Sériové zapojení zvyšuje tlakovou ztrátu nad výtlak vestavěného čerpadla RH050 (9 m) {Q}.</p>
<p><b>RH050 a TUV 1 000 l:</b> ohřev 10 → 55 °C trvá 6,9 h při −15 °C a 3,8 h při +7 °C. Energeticky to zvládne, ale pouze s výměníkem ≥ 4 m² a teplotou vody z TČ ≥ 60 °C, kterou RH050 při nízkých venkovních teplotách nemá ve výkonových tabulkách doložitelnou.</p>
<p><b>Hygiena:</b> vyhláška č. 252/2004 Sb. požaduje teplotu teplé vody v místě odběru 50–70 °C {Q} ověřit aktuální znění. Navrhuji udržovat 55 °C, cirkulaci jen pokud ji objekt má, a týdenní termickou dezinfekci na 65–70 °C: buď přepnutím RH X50 na výměníky TUV (výstup až 78 °C {D}), nebo elektrickou vložkou 3 kW, která slouží jen k dezinfekci a jako nouzový ohřev TUV — nejde o bivalentní zdroj vytápění.</p>
<h3>Konfigurace nádrží</h3>
{table(["", "A — max. sklad", "B — AKU 1 000 + 2–3 × 300 TUV", "C — AKU 1 000 + TUV 1 000"], [
    ["Sestava", "AKU 2 × 300 (+ 500) l, TUV 3 × 300 l", "AKU 1 000 l nová, TUV 2–3 × 300 l sklad", "AKU 1 000 l + TUV 1 000 l nové"],
    ["Akumulace ÚT", "600–1 100 l, sériově / paralelně", "1 000 l, jedna nádoba", "1 000 l"],
    ["Výměník TUV", "3 × 3,3 = 9,9 m²", "6,6–9,9 m²", "dle výrobce, typicky 3–5 m² " + Q],
    ["Půdorys (s izolací)", "≈ 5 nádob, nejvíc místa", "4 nádoby", "2 nádoby, nejméně místa"],
    ["Hydraulika", "nejsložitější, mnoho přírub a vyvažování", "střední", "nejjednodušší"],
    ["Tepelné ztráty nádob", "≈ 6–7 kWh/den " + O, "≈ 5–6 kWh/den", "≈ 4–5 kWh/den"],
    ["Nové výdaje (zadavatel)", "0 Kč", "5 000 Kč " + Z + " " + Q, "70 000 Kč " + Z],
    ["Univerzálnost", "nízká", "dobrá, rám připraven na 1 000 l TUV", "dobrá, ale TUV 1 000 l pro malé odběry stagnuje"],
    ["Doporučení", "jen jako nouzová sestava", "<b>doporučeno pro první zakázku</b>", "až pro objekty se sprchami / velkým odběrem"],
])}
<p class="cap">Skladové zásobníky použité v pronájmu už nepůjdou prodat jako nové — tato ztráta hodnoty patří do ekonomiky ve fázi 2.</p>
</section>

<section id="regulace">
<h2><span class="n">09</span>Regulace, kaskáda a vzdálený dohled</h2>
<div class="grid2">
<div class="box"><h3>Co umí jednotky podle dokumentace</h3>
<ul class="tight">
<li><b>RH X50</b> {D}: kaskáda až 8 jednotek (adresa přepínači, společné čidlo výstupní teploty), port RS485, port čerpadla, výstup pro pomocný zdroj, SG/EVU vstupy, Wi‑Fi aplikace a IoT monitorovací platforma výrobce.</li>
<li><b>RH030–RH060</b> {D}: vestavěné čerpadlo, Wi‑Fi přes aplikaci Tuya/Smart Life, v parametrech „jednotky online“ a „řídicí adresa“. Kaskádové řízení ani Modbus protokol v návodu popsány nejsou {Q}.</li>
<li>Zda se RH0x připojí na stejnou IoT platformu jako RH X50, není doloženo {Q}.</li></ul></div>
<div class="box"><h3>Navržené řízení</h3>
<ul class="tight">
<li>Nadřazený kaskádový regulátor (PLC s Modbus RTU/TCP, 4G router) řídí podle teploty v AKU: povolení jednotek, žádané teploty, ekvitermní křivka.</li>
<li>Spínání podle potřeby výkonu s hysterezí a minimální dobou běhu; max. 4 starty/h na jednotku {D}.</li>
<li>Střídání podle provozních hodin, rezervní jednotka se přiřadí při deficitu (teplota v AKU klesá při všech běžících).</li>
<li>Při poruše: ztráta komunikace / alarm jednotky → okamžité povolení další.</li>
<li><b>Nouzový režim:</b> při výpadku PLC běží jednotky samostatně na pevnou žádanou teplotu z vlastního ovladače.</li>
<li>Omezení počtu kompresorů podle dostupného proudu zákazníka.</li></ul></div>
</div>
<p><b>Skutečná N+1</b> vyžaduje, aby zbylé jednotky pokryly návrhový výkon a aby nebyl jediný společný prvek bez zálohy. Rozdělovač, kmen, VS1, AKU a přívod budou vždy jednoduché; zálohovat lze čerpadla (zdvojené / sklad), regulaci (nouzový režim) a jednotky. Prakticky reálné je „N+1 do −5 až −7 °C“, ne do −15 °C.</p>
</section>

<section id="elektro">
<h2><span class="n">10</span>Elektrické připojení</h2>
{el_tbl}
<p class="cap">Soudobost 1,0 (v mrazu běží vše), +2 kW čerpadla, regulace, osvětlení a temperování kontejneru {O}. Kabel orientačně pro uložení na povrchu do 25 m; úbytek napětí a selektivitu jištění ověří projektant elektro {Q}.</p>
<ul class="tight">
<li>Rozvaděč: hlavní vypínač, přepěťová ochrana T1+T2, samostatné vývody pro každou jednotku s jističem a proudovým chráničem dle návodu jednotek, hlídač fází, UPS pro regulaci a primární čerpadla, 4G router.</li>
<li>Příprava pro podružné měření: místo na DIN liště a průvlaky pro elektroměr (MID, Modbus) a kalorimetry primáru i TUV.</li>
<li>R290 venku: rozvaděč, zásuvky ani větrací otvory kontejneru nesmí být v ochranné zóně jednotek; minimální odstupy dle návodu výrobce {Q}.</li>
</ul>
</section>

<section id="kontejner">
<h2><span class="n">11</span>Kontejner, uspořádání a kotvení</h2>
<div class="grid2">
<div class="box"><h3>10' — ekonomická varianta</h3>
<p>Vnitřní ≈ 2,83 × 2,35 m. Pojme AKU 1 000 l, 2 × TUV 300 l a hydraulickou stěnu, rozvaděč u dveří. Ulička pod 600 mm, výměna nádoby jen vyklopením ven, žádná rezerva pro 1 000 l TUV ani VS2. Vhodné jen pro B1 / malé objekty.</p></div>
<div class="box"><h3>20' — univerzální varianta (doporučuji)</h3>
<p>Vnitřní 5,90 × 2,35 m. Všechny konfigurace nádrží, servisní ulička ≥ 800 mm, místo pro VS1/VS2, skladovou polici a hadice na přepravu. Těžiště lze držet u středu. High Cube (světlá výška 2,70 m) odstraní problém klopné výšky nádrží 1 000 l.</p></div>
</div>
<div class="fig plan">{PLAN_SVG}</div>
<p class="cap">Koncepční půdorys 20'. Prostorový 3D model a výkresy rámů ve fázi 2 po potvrzení konfigurace nádrží.</p>
<h3>Konstrukční koncept kotvení</h3>
<ul class="tight">
<li><b>Svařovaný nosný rám</b> na podlaze z uzavřených profilů (např. 80 × 80 × 4) a U-profilů, přenáší zatížení na příčníky podlahy a spodní podélníky kontejneru, ne do překližky ani do vlnitých stěn (corten ≈ 1,6–2 mm).</li>
<li><b>Šroubované vyměnitelné konzole</b> pro každou nádrž: patky nádrží na roznášecí desky s drážkovými otvory (M12–M16), horní obvodový třmen nebo konzola do zadních kotevních bodů zásobníku napojená na svislé sloupky rámu.</li>
<li>Rozteč kotevních bodů navržena pro 3 × Ø 650 i 1 × Ø 1 000 — výměna bez svařování.</li>
<li>Rám napojit na rohové sloupky a horní podélníky jen přes šroubované spoje; svary na kontejneru a výřezy pro průchody posoudí statik.</li>
<li>Stavy zatížení: <b>provoz</b> (plné nádrže, svislé zatížení), <b>přeprava</b> (prázdné, 0,8 g vpřed, 0,5 g do stran a vzad dle ČSN EN 12195-1, svisle 1,0 g + rázy), <b>zdvih</b> jeřábem (dynamický součinitel 1,2–1,5, zvedání za rohové prvky, těžiště).</li>
</ul>
{tank_tbl}
<p class="cap">Hmotnosti a výšky těžiště prázdných nádrží jsou odhad {O} — nutné výkresy zásobníků. Prázdná nádrž se při brzdění 0,8 g bez kotvení převrátí (červeně), proto kotvení nahoře i dole.</p>
<p><b>Před výrobou musí posoudit autorizovaný statik / konstruktér:</b> nosný rám a jeho napojení na kontejner, kotvení nádrží pro přepravní zatížení, únosnost podlahy pod plnými nádržemi, oslabení kontejneru výřezy a průchodkami, způsob zdvihu soupravy s technologií (smí se kontejner zvedat s nádržemi uvnitř a do jaké hmotnosti), přepravní rámy venkovních jednotek (370 kg RH X50, těžiště ve výšce) a jejich kotvení na místě proti větru.</p>
</section>

<section id="hluk">
<h2><span class="n">12</span>Hluk venkovních jednotek</h2>
<code class="formula">L_pA = L_WA − 20 log r − 8 dB   (bodový zdroj nad odrazivou plochou, bez stínění)</code>
{noise_tbl}
<p class="cap">LWA z protokolů a dokumentace výrobce {D}; maximum RH X50 77 dB. Hygienický limit pro chráněný venkovní prostor staveb dle NV 272/2011 Sb. obvykle 50 dB den / 40 dB noc {Q}. Při obytné zástavbě do ≈ 40 m od RH X50 je nutné noční omezení výkonu nebo posouzení.</p>
</section>

<section id="overit">
<h2><span class="n">13</span>Předpoklady k ověření a potřebné dokumenty</h2>
<div class="cols">
<div><h3>Od výrobce jednotek</h3><ol class="check">
<li>Výkonová data RH050/RH060 pro W60–W65 a potvrzení, zda tabulky RH050/060 jsou měřené.</li>
<li>Typové štítky: max. proud a doporučené jištění RH050 (1f/3f) a RH060.</li>
<li>Jmenovitý průtok, tlaková ztráta a křivka vestavěného čerpadla RH050/RH060.</li>
<li>Modbus RTU mapa registrů RS485 pro RH X50 a pro řídicí jednotku RH0x.</li>
<li>Kaskáda RH0x: podporovaná, kolik jednotek, s jakým ovladačem.</li>
<li>Připojení RH0x na IoT platformu výrobce.</li>
<li>Souhlas s glykolem v RH0x a doporučená koncentrace; min. průtok při glykolu.</li>
<li>Odstupy R290 od otvorů, elektrických zařízení a kanalizace.</li>
<li>Hluk RH X50 při max. výkonu a v tichém režimu, spektrum.</li></ol></div>
<div><h3>K vlastním zásobníkům</h3><ol class="check">
<li>Výkres TUV 300 l: průměr s izolací, výška, klopná výška, poloha nožiček a zadních kotevních bodů, hmotnost prázdná.</li>
<li>Výměník: plocha, objem, materiál, tlaková ztráta při 2–3 m³/h, max. tlak.</li>
<li>AKU 300 l a 500 l: nátrubky, tlak, izolace, hmotnost.</li>
<li>Nová AKU 1 000 l za 5 000 Kč: co zahrnuje (izolace, nátrubky, tlak 3/6 bar, nová/použitá).</li>
<li>Nová TUV 1 000 l za 65 000 Kč: výrobce, plocha výměníku, vložka, rozměry.</li></ol>
<h3>Interně</h3><ol class="check">
<li>Kolik RH050 je skladem, 1f nebo 3f, stav té použité jednotky.</li>
<li>Které konfigurace chcete nabízet jako standard (B1/B2).</li>
<li>Zda přijímáte glykolový primár (M2).</li></ol></div>
</div>
</section>

<section id="obhlidka">
<h2><span class="n">14</span>Kontrolní seznam technické obhlídky</h2>
<div class="cols">
<div><h3>Potřeba tepla</h3><ol class="check">
<li>Vyúčtování CZT za 2–3 roky po měsících (GJ), podíl TUV.</li>
<li>Smluvní / rezervovaný výkon CZT, projekt výměníkové stanice.</li>
<li>Vytápěná plocha a objem: administrativa, hala (výška), požadované teploty a provozní doba.</li>
<li>Stav obálky, vrata haly (četnost otevírání), vzduchotechnika.</li>
<li>Zda lze v hale snížit teplotu nebo vytápět jen část.</li></ol></div>
<div><h3>Otopná soustava</h3><ol class="check">
<li>Projektovaný spád a skutečná teplota přívodu v posledních mrazech (záznam regulátoru VS).</li>
<li>Typ těles: radiátory, konvektory, teplovzdušné jednotky, podlahové; počet a výkon.</li>
<li>Objem soustavy, výška budovy, provozní tlak, expanze a pojistný ventil.</li>
<li>Oběhová čerpadla a jejich ovládání, směšovací okruhy, regulace.</li>
<li>Kvalita vody (kal, magnetit), poslední proplach; zda je nutný VS2.</li>
<li>Místo napojení: dimenze, uzávěry, vzdálenost od kontejneru, průchod zdí.</li></ol></div>
<div><h3>Teplá voda</h3><ol class="check">
<li>Počet osob na směnu, sprchy, kuchyňka, technologický odběr.</li>
<li>Špičkový odběr (po směně), stávající zásobník / ohřev v CZT.</li>
<li>Cirkulace TUV, délka rozvodu, tlak studené vody, tvrdost.</li>
<li>Místo napojení SV, TUV, C.</li></ol></div>
<div><h3>Elektro</h3><ol class="check">
<li>Hlavní jistič a rezervovaný příkon, typ sazby, odběrné místo.</li>
<li>Volná kapacita v rozvaděči, vzdálenost k místu kontejneru.</li>
<li>Typ přípojky (CEE 63/125 A), možnost dočasného navýšení příkonu u distributora.</li>
<li>Kvalita sítě, stávající odběry technologie haly ve špičce.</li></ol></div>
<div><h3>Umístění a doprava</h3><ol class="check">
<li>Plocha pro kontejner 20' + jednotky: rozměry, únosnost, rovinnost, odvodnění kondenzátu.</li>
<li>Příjezd pro HDS / hákový nosič, poloměr zatáčení, výška a hmotnost na komunikacích, stání jeřábu.</li>
<li>Volný prostor kolem jednotek (sání, výfuk vzhůru), sníh, padající led ze střechy.</li>
<li>Vzdálenost obytné zástavby, okna, noční provoz — hluk.</li>
<li>Zabezpečení proti vandalismu a krádeži, osvětlení.</li>
<li>Pokrytí 4G pro dálkový dohled.</li>
<li>Povolení: vlastnictví pozemku, dočasné umístění, požární a hygienické požadavky.</li></ol></div>
<div><h3>Provozní a smluvní</h3><ol class="check">
<li>Termín nutnosti tepla, předpokládaná doba nájmu, riziko prodloužení.</li>
<li>Kdo bude kontaktní osoba a kdo hlídá výpadky.</li>
<li>Pojištění objektu a možnost připojištění technologie.</li>
<li>Fotodokumentace všech míst napojení a trasy hadic.</li></ol></div>
</div>
</section>

<section id="dalsi">
<h2><span class="n">15</span>Další postup</h2>
<ol class="check">
<li><b>Rozhodnutí ke konceptu</b> (vy): B2 jako standard, glykolový primár M2, nádrže varianta B, kontejner 20' (HC?).</li>
<li><b>Fáze 2</b>: 3D koncept, výkresy rámů a seznam hutního materiálu, hydraulické schéma s dimenzemi a armaturami, položkový seznam komponent, konkrétní čeští dodavatelé s cenami (kontejnery, hadice, rychlospojky, čerpadla, VS1), investiční rozpočet.</li>
<li><b>Fáze 3</b>: cenová mapa pronájmů mobilních kotelen v ČR, ekonomika zakázky (nájem 50 / 70 / 90 tis. Kč, druhý a třetí pronájem), návrh nájemní smlouvy B2B ke kontrole advokátem.</li>
</ol>
</section>
<footer>Výpočty: <code>mobilni-kotelna-tc/univerzalni/src/vypocty.py</code> · generátor <code>gen_studie.py</code>. Výsledky jsou orientační a nenahrazují projektovou dokumentaci.</footer>
</main>
"""

OUT.write_text(HTML)
print("zapsáno", OUT, len(HTML))
