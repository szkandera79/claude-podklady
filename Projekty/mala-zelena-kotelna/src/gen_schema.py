#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generátor koncepčního schématu — malá zelená kotelna, 2 × RH060 v kaskádě.

Vytváří ../schema-kaskada.svg (na výšku, čitelné na šířku A4).
Spuštění:  python3 mala-zelena-kotelna/src/gen_schema.py
Pak:       python3 mala-zelena-kotelna/src/build_nabidka.py
Kreslení (helpery, symboly) převzato z vzor-bytove-domy/src/gen_schema.py.
"""
import os

W, H = 1700, 1040
PT, PH, PW = 110, 690, 815          # panel: top, height, width
PAX, PBX = 30, 855                  # levý okraj panelu A / B

RED   = "#D62828"   # topná (výstup ze zdroje)
BLUE  = "#1D4E89"   # vratná
ORA   = "#D9761C"   # TUV
ORA2  = "#E9A85F"   # cirkulace TUV
INK   = "#16201C"
GRN   = "#0F3D2E"
GRNB  = "#1E8F5B"

o = []
def add(s): o.append(s)

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def T(x, y, s, cls="t", anchor="start"):
    add(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{esc(s)}</text>')

def R(x, y, w, h, fill="#fff", stroke=INK, sw=2, rx=0):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ' stroke="none"'
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{st}/>')

def P(d, color, w=5, dash=None):
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<path class="pipe" d="{d}" fill="none" stroke-linecap="round" '
        f'stroke-linejoin="round" stroke="{color}" stroke-width="{w}"{ds}/>')

def gap(x, y, horiz=False, ln=18):
    """Bílé přerušení potrubí (křížení) — segment ve směru přerušované trubky."""
    if horiz:
        add(f'<line x1="{x-ln//2}" y1="{y}" x2="{x+ln//2}" y2="{y}" stroke="#fff" stroke-width="13"/>')
    else:
        add(f'<line x1="{x}" y1="{y-ln//2}" x2="{x}" y2="{y+ln//2}" stroke="#fff" stroke-width="13"/>')

def U(sym, x, y, rot=0):
    tr = f' transform="translate({x},{y}) rotate({rot})"' if rot else f' transform="translate({x},{y})"'
    add(f'<use href="#{sym}"{tr}/>')

def tank(x, y, w, h, fill, label, sub=None):
    R(x, y, w, h, fill=fill, sw=2.3, rx=32)
    T(x + w/2, y + h/2 - 2, label, "tbs", "middle")
    if sub:
        T(x + w/2, y + h/2 + 15, sub, "tx", "middle")

def coil(x, y, w):
    """Topný had (výměník) v zásobníku TUV — vinutí v barvě otopné vody."""
    n = 6
    step = w / n
    d = f"M{x-w/2},{y}"
    for k in range(n):
        up = -11 if k % 2 == 0 else 11
        d += f" l{step/2},{up} l{step/2},{-up}"
    add(f'<path d="{d}" fill="none" stroke="{RED}" stroke-width="2.6" '
        f'stroke-linejoin="round" stroke-linecap="round"/>')


def spiral(x, y, w):
    """Elektrická topná patrona v nádrži."""
    d = f"M{x-w/2},{y} l{w*0.14},-9 l{w*0.14},18 l{w*0.14},-18 l{w*0.14},18 l{w*0.14},-18 l{w*0.14},18 l{w*0.14},-9"
    add(f'<path d="{d}" fill="none" stroke="#DA8718" stroke-width="2.6" stroke-linejoin="round"/>')
    add(f'<line x1="{x-w/2-8}" y1="{y}" x2="{x-w/2}" y2="{y}" stroke="#DA8718" stroke-width="2.6"/>')
    add(f'<line x1="{x+w/2}" y1="{y}" x2="{x+w/2+8}" y2="{y}" stroke="#DA8718" stroke-width="2.6"/>')

# ---------------------------------------------------------------- hlavička

# ====================================================================== DOKUMENTY

def preamble(w, h, title, sub, code):
    """Rámeček, definice symbolů a záhlaví listu."""
    global W, H
    W, H = w, h
    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet" '
        f'font-family="Arial, Helvetica, sans-serif">')
    add('''<style>
     .pipe{fill:none;stroke-linecap:round;stroke-linejoin:round}
     .sym{fill:#fff;stroke:#16201C;stroke-width:2}
     .symk{fill:#16201C}
     .t{fill:#16201C;font-size:12px}
     .ts{fill:#16201C;font-size:11px}
     .tx{fill:#5F6B64;font-size:10.5px}
     .tb{fill:#16201C;font-size:15px;font-weight:bold}
     .tbs{fill:#16201C;font-size:12px;font-weight:bold}
     .wt{fill:#fff;font-size:13px;font-weight:bold}
     .wts{fill:#CFE6D9;font-size:12px;font-weight:bold}
     .eb{fill:#1E8F5B;font-size:12px;font-weight:bold;letter-spacing:2.4px}
     .zt{fill:#0F3D2E;font-size:11px;font-weight:bold;letter-spacing:1.2px}
     .ttl{fill:#0F3D2E;font-size:22px;font-weight:bold}
     .amb{fill:#8A5312;font-size:11px;font-weight:bold}
    </style>''')
    add('<defs>')
    add('<g id="v"><path class="sym" d="M-10,-7 L0,0 L-10,7 Z"/><path class="sym" d="M10,-7 L0,0 L10,7 Z"/></g>')
    add('<g id="chk"><path class="sym" d="M-10,-7 L9,0 L-10,7 Z"/>'
        '<line x1="10" y1="-8" x2="10" y2="8" stroke="#16201C" stroke-width="2.2"/></g>')
    add('<g id="pump"><circle class="sym" r="13"/><path class="symk" d="M-5,-6.5 L7,0 L-5,6.5 Z"/></g>')
    add('<g id="flt"><rect class="sym" x="-12" y="-10" width="24" height="20"/>'
        '<line x1="-12" y1="-10" x2="12" y2="10" stroke="#16201C" stroke-width="1.5"/>'
        '<line x1="-12" y1="10" x2="12" y2="-10" stroke="#16201C" stroke-width="1.5"/></g>')
    add('<g id="exp"><rect class="sym" x="-13" y="-22" width="26" height="40" rx="12"/>'
        '<line x1="-13" y1="-2" x2="13" y2="-2" stroke="#16201C" stroke-width="1.5"/></g>')
    add('<g id="sv"><path class="sym" d="M-9,-6 L0,0 L-9,6 Z"/>'
        '<path fill="none" stroke="#16201C" stroke-width="2" d="M0,0 L0,-9 L8,-9"/>'
        '<path fill="none" stroke="#5F6B64" stroke-width="1.3" d="M-3,-13 l6,3 l-6,3 l6,3"/></g>')
    add('<g id="mix"><path class="sym" d="M-10,-7 L0,0 L-10,7 Z"/><path class="sym" d="M10,-7 L0,0 L10,7 Z"/>'
        '<path class="sym" d="M-7,16 L0,0 L7,16 Z"/>'
        '<circle class="sym" cx="0" cy="-18" r="9"/>'
        '<text x="0" y="-14" text-anchor="middle" style="font-size:10px;fill:#16201C;font-weight:bold">M</text>'
        '<line x1="0" y1="-9" x2="0" y2="0" stroke="#16201C" stroke-width="1.6"/></g>')
    add('<g id="ts"><circle class="sym" r="9"/>'
        '<text x="0" y="4" text-anchor="middle" style="font-size:10px;fill:#16201C;font-weight:bold">T</text></g>')
    add('<marker id="ar" markerWidth="8" markerHeight="8" refX="5" refY="3" orient="auto">'
        '<path d="M0,0 L6,3 L0,6 Z" fill="#16201C"/></marker>')
    add('</defs>')

    R(0, 0, W, H, fill="#fff", stroke=None)
    R(14, 14, w-28, H-28, fill="none", stroke=INK, sw=2)

    # --------------------------------------------------------------- záhlaví
    T(36, 48, "THERMAVERA ENERGY", "eb")
    T(36, 78, title, "ttl")
    T(w-36, 48, code, "zt", "end")
    T(w-36, 72, sub, "tx", "end")
    add(f'<line x1="30" y1="94" x2="{w-30}" y2="94" stroke="{GRNB}" stroke-width="2.5"/>')




def box_unit(X0, n, sub1, sub2):
    """Venkovní jednotka TČ."""
    R(X0, 180, 175, 85, fill="#F4F8F5", stroke=INK, sw=2.2, rx=8)
    T(X0 + 87, 206, f"TČ {n} — REO RH060", "tbs", "middle")
    T(X0 + 87, 224, "11,8 kW při −15 °C / 45 °C", "ts", "middle")
    T(X0 + 87, 241, sub1, "tx", "middle")
    T(X0 + 87, 256, sub2, "tx", "middle")


def panel(X):
    def x(v): return X + v
    R(X, PT, PW, PH, fill="#FBFDFC", stroke="#DCE6DF", sw=1.5, rx=8)
    add(f'<path d="M{X},{PT+8} a8,8 0 0 1 8,-8 h{PW-16} a8,8 0 0 1 8,8 v34 h-{PW} z" fill="{GRN}"/>')
    T(x(16), PT+27, "MALÁ ZELENÁ KOTELNA — kaskáda 2 × REO RH060", "wt")
    T(x(PW-16), PT+27, "23,6 kW při −15 °C / 45 °C", "wts", "end")

    add(f'<line x1="{x(20)}" y1="283" x2="{x(795)}" y2="283" '
        f'stroke="{INK}" stroke-width="2" stroke-dasharray="12 6"/>')
    T(x(792), 172, "VENKOVNÍ PROSTŘEDÍ", "zt", "end")
    T(x(440), 316, "STROJOVNA / KOTELNA", "zt")

    # ---- venkovní jednotky: vratná v x0+30, topná v x0+80
    box_unit(x(40),  1, "střídají se v provozu", "a navzájem se zálohují")
    box_unit(x(230), 2, "střídají se v provozu", "a navzájem se zálohují")
    R(x(440), 180, 345, 85, fill="#fff", stroke="#DCE6DF", sw=1.5, rx=8)
    T(x(456), 204, "Dům s tepelnou ztrátou ≈ 18 kW při −15 °C", "tbs")
    T(x(456), 224, "2 jednotky: 23,6 kW → rezerva pro ohřev TUV", "ts")
    T(x(456), 241, "1 jednotka sama pokryje dům do cca −8 °C", "ts")
    T(x(456), 257, "A7/W55: 20,4 kW na jednotku", "tx")

    # ---- nádrže
    tank(x(215), 390, 130, 230, "#EAF1EC", "AKU", "1 000 l · otopná voda")
    tank(x(500), 390, 90, 230, "#FDF3EA", "TUV", "1 000 l")
    coil(x(545), 440, 62)
    spiral(x(280), 555, 60)

    # ---- výstupní bloky
    R(x(100), 690, 270, 68, fill="#EEF3F9", stroke=INK, sw=1.8, rx=8)
    T(x(235), 716, "ÚSTŘEDNÍ TOPENÍ OBJEKTU", "tbs", "middle")
    T(x(235), 736, "stávající otopná soustava domu", "tx", "middle")
    R(x(470), 690, 315, 68, fill="#FDF3EA", stroke=INK, sw=1.8, rx=8)
    T(x(627), 716, "ROZVOD TUV DO BYTŮ", "tbs", "middle")
    T(x(627), 736, "zásobník 1 000 l · s cirkulací", "tx", "middle")

    # ================= POTRUBÍ =================
    # --- vratná (primár): hlavní větev + sběrač k jednotkám
    P(f"M{x(330)},620 L{x(330)},785 L{x(70)},785 L{x(70)},265", BLUE)
    P(f"M{x(70)},330 L{x(260)},330 L{x(260)},265", BLUE)
    gap(x(120), 330, horiz=True)                   # vratná podbíhá topnou TČ1
    gap(x(260), 305)                               # vratná TČ2 podbíhá topný sběrač

    # --- sekundár ÚT a nabíjení TUV
    P(f"M{x(252)},390 L{x(252)},345 L{x(185)},345 L{x(185)},690", RED)
    gap(x(185), 430)
    P(f"M{x(230)},690 L{x(230)},620", BLUE)
    P(f"M{x(320)},390 L{x(320)},360 L{x(640)},360 L{x(640)},440 L{x(576)},440", RED)
    P(f"M{x(514)},440 L{x(470)},440 L{x(470)},530 L{x(345)},530", BLUE)

    # --- topná (primár)
    P(f"M{x(120)},265 L{x(120)},430 L{x(215)},430", RED)
    P(f"M{x(310)},265 L{x(310)},305 L{x(120)},305", RED)

    # --- TUV sekundár
    P(f"M{x(525)},620 L{x(525)},655 L{x(452)},655", BLUE)
    add(f'<path d="M{x(462)},649 L{x(450)},655 L{x(462)},661 Z" fill="{BLUE}"/>')
    T(x(446), 659, "studená voda", "tx", "end")
    P(f"M{x(565)},390 L{x(565)},335 L{x(720)},335 L{x(720)},690", ORA)
    gap(x(565), 360)
    P(f"M{x(565)},390 L{x(565)},335", ORA)
    P(f"M{x(670)},690 L{x(670)},650 L{x(570)},650 L{x(570)},620", ORA2, 4, dash="9 6")

    # ================= ARMATURY =================
    U("chk", x(120), 370, 90)
    U("v",   x(120), 405, 90)
    U("pump", x(70), 480)
    U("flt",  x(70), 560)
    P(f"M{x(70)},360 L{x(46)},360", BLUE, 3)
    U("sv", x(44), 360, 180)
    P(f"M{x(70)},412 L{x(42)},412 L{x(42)},418", BLUE, 3)
    U("exp", x(42), 440)
    U("pump", x(430), 360)
    U("mix", x(185), 500)
    U("pump", x(185), 585)
    U("ts", x(252), 345)
    U("chk", x(310), 285, 90)

    T(x(785), 782, "Koncepční schéma — detaily upřesní prováděcí projekt.", "tx", "end")


def legend(bx, by, bw):
    R(bx, by, bw, 152, fill="#fff", stroke="#DCE6DF", sw=1.5, rx=8)
    T(bx+18, by+25, "LEGENDA", "tbs")
    leg = [(RED, "topná voda ze zdroje"), (BLUE, "vratná voda"),
           (ORA, "teplá užitková voda"), (ORA2, "cirkulace TUV")]
    for i, (c, lab) in enumerate(leg):
        yy = by + 48 + i*24
        dsh = ' stroke-dasharray="9 6"' if c == ORA2 else ''
        add(f'<line x1="{bx+22}" y1="{yy}" x2="{bx+64}" y2="{yy}" stroke="{c}" stroke-width="5" '
            f'stroke-linecap="round"{dsh}/>')
        T(bx+74, yy+4, lab, "ts")
    syms = [("pump", "oběhové čerpadlo"), ("chk", "zpětná klapka"),
            ("v", "uzávěr"), ("flt", "filtr"),
            ("exp", "expanzní nádoba"), ("sv", "pojistný ventil"),
            ("mix", "směšovací ventil"), ("ts", "teplotní čidlo")]
    for i, (sy, lab) in enumerate(syms):
        col, row = i % 4, i // 4
        sx = bx + 250 + row*140
        yy = by + 48 + col*24
        U(sy, sx, yy)
        T(sx + 20, yy + 4, lab, "ts")
    coil(bx + 560, by + 48, 40)
    T(bx + 590, by + 52, "topný had v zásobníku TUV", "ts")
    spiral(bx + 560, by + 72, 36)
    T(bx + 590, by + 76, "el. patrona — dokrytí špiček", "ts")
    T(bx + 542, by + 104, "Ohřev TUV topným hadem přímo", "ts")
    T(bx + 542, by + 120, "z okruhu tepelných čerpadel", "tx")


def build(path, w, h, title, sub, code, body):
    global o
    o = []
    preamble(w, h, title, sub, code)
    body()
    add('</svg>')
    dst = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", path))
    with open(dst, "w", encoding="utf-8") as f:
        f.write("\n".join(o))
    print("zapsáno:", dst)



def _sheet():
    panel(30)
    legend(30, 815, 815)
    T(30, 990, "ThermaVera Energy · koncepční schéma k nabídce malé zelené kotelny", "tx")
    T(845, 990, "rev. 0 · 10/2026", "tx", "end")


build("schema-kaskada.svg", 875, 1005,
      "Malá zelená kotelna pro bytový dům",
      "tepelná ztráta do ≈ 24 kW · 2 × REO RH060 v kaskádě", "TV-MALA-BD-01 · rev. 0", _sheet)
