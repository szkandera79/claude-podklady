#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Graf krytí výkonu pro nabídku BD Michal → graf-vykon.svg + inline do nabidka.html.
Spouštět z kořene repa: python3 bd-michal-nabidka/src/gen_chart.py"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from model import cap35, cap55, load, LOSS, TUV_RATE, T_DES

BASE = Path(__file__).parent.parent
W, H = 1160, 470
G = dict(ink='#1b2420', mut='#5d6b64', line='#d8ded9', acc='#1E8F5B', acc2='#0F3D2E',
         amber='#DA8718', amberbg='#FFF6E9', red='#C0392B', bg='#fbfdfb')
o = []
add = o.append


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def txt(x, y, s, size=12, fill=G['ink'], anchor='start', weight='normal'):
    add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
        f'font-weight="{weight}">{esc(s)}</text>')


# ---------- panel 1: topná křivka ----------
X0, Y0, PW, PH = 58, 62, 560, 330
TMIN, TMAX, KWMAX = -18, 13, 110
px = lambda t: X0 + (TMAX - t) / (TMAX - TMIN) * PW
py = lambda k: Y0 + PH - k / KWMAX * PH

add(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>')
txt(X0 - 14, 30, 'Krytí výkonu podle venkovní teploty', 15, G['acc2'], weight='bold')
txt(X0 - 14, 48, 'potřeba domu proti výkonu kaskády RH X50 při ohřevu topné vody na 35 °C', 11.5, G['mut'])
add(f'<rect x="{X0}" y="{Y0}" width="{PW}" height="{PH}" fill="{G["bg"]}" stroke="{G["line"]}"/>')
for k in range(0, KWMAX + 1, 20):
    y = py(k)
    add(f'<line x1="{X0}" y1="{y:.1f}" x2="{X0+PW}" y2="{y:.1f}" stroke="{G["line"]}" stroke-width="1"/>')
    txt(X0 - 8, y + 4, str(k), 11, G['mut'], 'end')
for t in range(TMIN, TMAX + 1, 5):
    x = px(t)
    add(f'<line x1="{x:.1f}" y1="{Y0+PH}" x2="{x:.1f}" y2="{Y0+PH+5}" stroke="{G["mut"]}" stroke-width="1"/>')
    txt(x, Y0 + PH + 19, f'{t}', 11, G['mut'], 'middle')
txt(X0 + 8, Y0 + 16, 'kW', 11, G['mut'])
txt(X0 + PW, Y0 + PH + 36, 'venkovní teplota [°C]', 11, G['mut'], 'end')

ts = [TMIN + i * 0.5 for i in range(int((TMAX - TMIN) / 0.5) + 1)]
for n, col, dash, lab in ((3, G['acc'], '', '3× RH X50'), (2, '#2f6fb0', '', '2× RH X50'), (1, G['mut'], '4 3', '1× RH X50')):
    pts = [(t, n * cap35(t)) for t in ts if n * cap35(t) <= KWMAX]
    d = ' '.join(f'{"M" if i==0 else "L"}{px(t):.1f},{py(v):.1f}' for i, (t, v) in enumerate(pts))
    add(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="2.6" stroke-dasharray="{dash}"/>')
    txt(px(TMIN) + 8, py(n * cap35(TMIN)) + 4, lab, 11.5, col, 'start', 'bold')
d = ' '.join(f'{"M" if i==0 else "L"}{px(t):.1f},{py(load(t)):.1f}' for i, t in enumerate(ts))
add(f'<path d="{d}" fill="none" stroke="{G["red"]}" stroke-width="2.6"/>')
d = ' '.join(f'{"M" if i==0 else "L"}{px(t):.1f},{py(load(t)+TUV_RATE):.1f}' for i, t in enumerate(ts))
add(f'<path d="{d}" fill="none" stroke="{G["red"]}" stroke-width="1.8" stroke-dasharray="5 4"/>')
txt(px(-1), py(load(-1)) - 10, 'potřeba vytápění', 11.5, G['red'], 'middle', 'bold')
txt(px(-1), py(load(-1) + TUV_RATE) + 26, '+ průměr TUV', 11, G['red'], 'middle')
# bod −15
add(f'<line x1="{px(T_DES):.1f}" y1="{Y0}" x2="{px(T_DES):.1f}" y2="{Y0+PH}" stroke="{G["amber"]}" stroke-width="1.6" stroke-dasharray="4 4"/>')
txt(px(T_DES) - 6, Y0 + PH - 10, 'návrhová −15 °C', 11, G['amber'], 'end', 'bold')
for n, col in ((2, '#2f6fb0'), (3, G['acc'])):
    add(f'<circle cx="{px(T_DES):.1f}" cy="{py(n*cap35(T_DES)):.1f}" r="4" fill="{col}"/>')
    txt(px(T_DES) - 9, py(n * cap35(T_DES)) - 7, f'{n*cap35(T_DES):.1f} kW', 11, col, 'end', 'bold')
add(f'<circle cx="{px(T_DES):.1f}" cy="{py(LOSS):.1f}" r="4" fill="{G["red"]}"/>')
txt(px(T_DES) - 9, py(LOSS) + 16, f'{LOSS:.0f} kW', 11, G['red'], 'end', 'bold')

# ---------- panel 2: sloupce při −15 °C ----------
BX, BY, BW, BH = 700, 62, 400, 330
add(f'<rect x="{BX}" y="{BY}" width="{BW}" height="{BH}" fill="{G["bg"]}" stroke="{G["line"]}"/>')
txt(BX, 30, 'Výkon na vytápění při −15 °C', 15, G['acc2'], weight='bold')
txt(BX, 48, 'tři provozní situace, tepelná ztráta domu 53 kW', 11.5, G['mut'])
c35 = cap35(T_DES)
groups = [('Běžný provoz', 2 * c35, 3 * c35), ('Souběh s ohřevem TUV', c35, 2 * c35), ('Výpadek jedné jednotky', c35, 2 * c35)]
gw = BW / len(groups)
scale = lambda k: k / KWMAX * (BH - 60)
yb = BY + BH - 34
for i, (lab, a, b) in enumerate(groups):
    cx = BX + i * gw + gw / 2
    for j, (v, col, nm) in enumerate(((a, '#2f6fb0', 'A'), (b, G['acc'], 'B'))):
        x = cx - 40 + j * 42
        h = scale(v)
        add(f'<rect x="{x:.1f}" y="{yb-h:.1f}" width="34" height="{h:.1f}" fill="{col}" rx="3"/>')
        txt(x + 17, yb - h - 6, f'{v:.0f}', 11.5, col, 'middle', 'bold')
        txt(x + 17, yb + 14, nm, 11, G['mut'], 'middle', 'bold')
    for k, line in enumerate(lab.split(' ', 1) if len(lab) > 16 else [lab]):
        txt(cx, yb + 30 + k * 13, line, 10.5, G['mut'], 'middle')
yl = yb - scale(LOSS)
add(f'<line x1="{BX+8}" y1="{yl:.1f}" x2="{BX+BW-8}" y2="{yl:.1f}" stroke="{G["red"]}" stroke-width="2" stroke-dasharray="6 4"/>')
txt(BX + 130, yl - 7, '53 kW', 11, G['red'], 'middle', 'bold')
txt(BX + BW, 30, 'A = 2× RH X50', 11.5, '#2f6fb0', 'end', 'bold')
txt(BX + BW, 46, 'B = 3× RH X50', 11.5, G['acc'], 'end', 'bold')

# ---------- pásek s poznámkou ----------
add(f'<rect x="{X0-14}" y="{H-52}" width="{W-2*(X0-14)}" height="40" rx="8" fill="{G["amberbg"]}" stroke="#f0d3bf"/>')
txt(X0 + 2, H - 34, 'Souběh s ohřevem TUV: u varianty A zbývá na vytápění jediná jednotka (30,9 kW) — chybějící výkon do 53 kW dokryjí patrony 2 × 11 kW.', 11.5, '#8A5312')
txt(X0 + 2, H - 18, 'U varianty B topí i během ohřevu TUV dvě jednotky (61,8 kW), takže elektrická bivalence zůstává jen doplňková.', 11.5, '#8A5312')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="Segoe UI, system-ui, -apple-system, Helvetica Neue, Arial, sans-serif">\n  '
       + '\n  '.join(o) + '\n</svg>\n')
(BASE / 'graf-vykon.svg').write_text(svg, encoding='utf-8')
print('zapsáno graf-vykon.svg')

nab = BASE / 'nabidka.html'
if nab.exists():
    t = nab.read_text(encoding='utf-8')
    a, b = '<!--GRAF-->', '<!--/GRAF-->'
    if a in t and b in t:
        t = t[:t.index(a) + len(a)] + '\n' + svg + t[t.index(b):]
        nab.write_text(t, encoding='utf-8')
        print('graf vložen do nabidka.html')
