#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vloží do analyza.html grafy a tabulky z keymark_model.py (značky <!--X-->…<!--/X-->):
CENY (cenová mapa), G35 / G55 (COP při jednotné zátěži, KEYMARK), GSEZ (sezónní COP podle režimu),
SCEN (náklady 15 let: velikost × teplotní spád), TARIF (citlivost na cenu elektřiny).
Spouštět z kořene repa:
    python3 porovnani-x50-rh060/src/keymark_model.py && python3 porovnani-x50-rh060/src/gen_doc.py
"""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import keymark_model as km

R = json.loads((HERE / "results2.json").read_text())
ORDER = ["X50", "X40", "X20", "RH060"]
CLS = {"X50": "x", "X40": "h", "X20": "g", "RH060": "r"}
NAME = {u: km.U[u]["name"] for u in ORDER}
fmt = lambda v: f"{v:,.0f}".replace(",", " ")
dec = lambda v, d=2: f"{v:.{d}f}".replace(".", ",")
tag = lambda u: f'<span class="tag {CLS[u]}">{NAME[u]}</span>'

# ------------------------------------------------------------------ čárový graf COP(Tj)
def line_chart(w, title):
    W, H, L, T, PW, PH = 640, 290, 46, 34, 548, 210
    xs = [-15, -10, -7, 2, 7, 12]
    ymax = 10 if w == 35 else 8
    X = lambda t: L + (t + 15) / 27 * PW
    Y = lambda v: T + PH - v / ymax * PH
    o = [f'<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="{title}">',
         f'<text x="{L}" y="{T-14}" class="ct">{title}</text>']
    for v in range(0, ymax + 1, 2):
        o.append(f'<line x1="{L}" x2="{L+PW}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" class="grid"/>')
        o.append(f'<text x="{L-8}" y="{Y(v)+4:.1f}" class="tick" text-anchor="end">{v}</text>')
    for t in xs:
        o.append(f'<text x="{X(t):.1f}" y="{T+PH+18}" class="tick" text-anchor="middle">{t:+d}'.replace("-", "−") + "</text>")
    o.append(f'<text x="{L+PW/2}" y="{T+PH+38}" class="tick" text-anchor="middle">venkovní teplota Tj (°C) · zátěž klesá se stoupající teplotou</text>')
    for u in ORDER:
        pts = [(X(t), Y(km.cop_at(u, w, t))) for t in [-10, -7, 2, 7, 12]]
        ext = [(X(-15), Y(km.cop_at(u, w, -15))), pts[0]]
        o.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in ext)}" class="ln {CLS[u]} dash" fill="none"/>')
        o.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" class="ln {CLS[u]}" fill="none"/>')
        for x, y in pts:
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" class="dot {CLS[u]}"/>')
    o.append("</svg>")
    return "\n".join(o)


# ------------------------------------------------------------------ sloupcový graf sezónních COP
def bar_chart():
    groups = [("35/30", 35), ("45/38", 45), ("55/45", 55), ("65/50", 65), ("TUV 55 °C", "tuv")]
    W, H, L, T, PW, PH = 700, 280, 40, 24, 640, 210
    ymax = 5
    Y = lambda v: T + PH - v / ymax * PH
    gw = PW / len(groups)
    bw = (gw - 22) / 4
    o = [f'<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="Sezónní COP podle teplotního režimu">']
    for v in range(0, ymax + 1):
        o.append(f'<line x1="{L}" x2="{L+PW}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" class="grid"/>')
        o.append(f'<text x="{L-8}" y="{Y(v)+4:.1f}" class="tick" text-anchor="end">{v}</text>')
    for gi, (lab, key) in enumerate(groups):
        gx = L + gi * gw + 11
        for ui, u in enumerate(ORDER):
            v = R["units"][u]["cop_dhw"] if key == "tuv" else R["units"][u]["scop_cz"][str(key)]
            x = gx + ui * bw
            o.append(f'<rect x="{x:.1f}" y="{Y(v):.1f}" width="{bw-3:.1f}" height="{Y(0)-Y(v):.1f}" rx="2" class="bar {CLS[u]}"/>')
            o.append(f'<text x="{x+(bw-3)/2:.1f}" y="{Y(v)-5:.1f}" class="val" text-anchor="middle">{dec(v,1)}</text>')
        o.append(f'<text x="{gx+2*bw:.1f}" y="{T+PH+20}" class="tick" text-anchor="middle">{lab}</text>')
    o.append("</svg>")
    return "\n".join(o)


# ------------------------------------------------------------------ cenová mapa
def price_table():
    rows = ['<table><thead><tr><th>Model</th><th class="n">Ceník</th><th class="n">Nákup Kč<br>bez DPH</th>'
            '<th class="n">Max. výkon<br>A7/W35</th><th class="n">Kč/kW<br>A7/W35</th>'
            '<th class="n">Výkon<br>A−15/W35</th><th class="n">Výkon<br>A−15/W55</th><th class="n">Kč/kW<br>A−15/W55</th>'
            '<th class="n">Výkon<br>A−15/W65</th><th class="n">Kč/kW<br>A−15/W65</th></tr></thead><tbody>']
    lst = {"X50": "US$ 4 800", "X40": "3 680 €", "X20": "2 940 €", "RH060": "US$ 2 398"}
    for u in ORDER:
        d = km.U[u]
        c = d["cap15"]
        est = "≈ " if u == "X20" else ""
        est65 = "" if u in ("X50", "X40") else "≈ "
        rows.append(f'<tr><td>{tag(u)}</td><td class="n">{lst[u]}</td><td class="n">{fmt(round(d["price"], -2))}</td>'
                    f'<td class="n">{dec(d["maxA7"],1)} kW</td><td class="n">{fmt(d["price"]/d["maxA7"])}</td>'
                    f'<td class="n">{est}{dec(c[35],1)} kW</td><td class="n">{est}{dec(c[55],1)} kW</td>'
                    f'<td class="n"><strong>{fmt(d["price"]/c[55])}</strong></td>'
                    f'<td class="n">{est65}{dec(c[65],1)} kW</td><td class="n">{fmt(d["price"]/c[65])}</td></tr>')
    rows.append('<tr><td><span class="tag o">RH070*</span></td><td class="n">US$ 2 530</td>'
                f'<td class="n">{fmt(round(2530*km.FX["USD"], -2))}</td><td class="n">24,0 kW</td>'
                f'<td class="n">{fmt(2530*km.FX["USD"]/24)}</td><td class="n" colspan="5">bez výkonové mapy a certifikace — neporovnáváno</td></tr>')
    rows.append("</tbody></table>")
    return "\n".join(rows)


# ------------------------------------------------------------------ scénáře
def scen_table():
    LAB = {35: "35/30 podlahové", 45: "45/38 zateplený dům, radiátory", 55: "55/45 běžné radiátory",
           65: "65/50 nezateplený dům, velký spád"}
    rows = ['<table class="scen"><thead><tr><th>Tepelná ztráta</th>' +
            "".join(f'<th class="n">{tag(u)}</th>' for u in ORDER) + '</tr></thead><tbody>']
    for w in (35, 45, 55, 65):
        rows.append(f'<tr class="grp"><td colspan="5">Teplotní spád {LAB[w]}</td></tr>')
        for loss in (25, 50, 75, 100, 150):
            g = {r["unit"]: r for r in R["scen"] if r["loss"] == loss and r["tw"] == w}
            ok = [u for u in ORDER if not g[u]["over"]]
            best = min(ok, key=lambda u: g[u]["tco15"])
            cells = []
            for u in ORDER:
                r = g[u]
                d = r["tco15"] - g[best]["tco15"]
                cls = ' class="n bestc"' if u == best else ' class="n"'
                sub = "nejnižší" if u == best else f"+{dec(100*d/g[best]['tco15'],1)} %"
                if r["over"]:
                    sub = "nad 8 ks"
                cells.append(f'<td{cls}><b>{dec(r["tco15"]/1e6,2)}</b> <span class="k">{r["n"]}×</span><br>'
                             f'<span class="d">{sub}</span></td>')
            rows.append(f'<tr><td>{loss} kW</td>{"".join(cells)}</tr>')
    rows.append("</tbody></table>")
    return "\n".join(rows)


def tariff_table():
    rows = ['<table><thead><tr><th>Cena elektřiny</th>' + "".join(f'<th class="n">{tag(u)}</th>' for u in ORDER) + "</tr></thead><tbody>"]
    for t in R["sens"]["tariff"]:
        best = min(ORDER, key=lambda u: t[u])
        rows.append(f'<tr><td>{dec(t["tariff"],0)} Kč/kWh</td>' + "".join(
            f'<td class="n{" win" if u == best else ""}">{dec(t[u]/1e6,2)} mil.</td>' for u in ORDER) + "</tr>")
    rows.append("</tbody></table>")
    return "\n".join(rows)


html = HERE.parent / "analyza.html"
s = html.read_text()
for k, frag in (("CENY", price_table()), ("G35", line_chart(35, "Vytápění na 35 °C (nízkoteplotní)")),
                ("G55", line_chart(55, "Vytápění na 55 °C (ekvitermní křivka do 55 °C)")),
                ("GSEZ", bar_chart()), ("SCEN", scen_table()), ("TARIF", tariff_table())):
    s = re.sub(rf"<!--{k}-->.*?<!--/{k}-->", f"<!--{k}-->\n{frag}\n<!--/{k}-->", s, flags=re.S)
html.write_text(s)
print("vloženo do", html)
