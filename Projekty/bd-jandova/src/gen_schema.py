#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generátor koncepčního schématu kotelny BD Jandova 7, Ostrava-Zábřeh.

Vytváří ../schema-kotelny.svg — dvě varianty zdroje vedle sebe (A3 na šířku).
Spuštění:  python3 src/gen_schema.py
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




def panel(X, variant):
    def x(v): return X + v
    title = ("VARIANTA 1 — jedno tepelné čerpadlo + elektrická bivalence"
             if variant == 1 else
             "VARIANTA 2 — kaskáda dvou tepelných čerpadel")
    price = "1 350 000 Kč bez DPH" if variant == 1 else "1 600 000 Kč bez DPH"

    R(X, PT, PW, PH, fill="#FBFDFC", stroke="#DCE6DF", sw=1.5, rx=8)
    R(X, PT, PW, 42, fill=GRN, stroke=None, rx=0)
    add(f'<path d="M{X},{PT+8} a8,8 0 0 1 8,-8 h{PW-16} a8,8 0 0 1 8,8 v34 h-{PW} z" fill="{GRN}"/>')
    T(x(16), PT+27, title, "wt")
    T(x(PW-16), PT+27, price, "wts", "end")

    # hranice venkovní / strojovna
    add(f'<line x1="{x(20)}" y1="{PT+175}" x2="{x(795)}" y2="{PT+175}" '
        f'stroke="{INK}" stroke-width="2" stroke-dasharray="12 6"/>')
    T(x(792), PT+167, "VENKOVNÍ PROSTŘEDÍ", "zt", "end")
    T(x(792), PT+191, "STROJOVNA / KOTELNA", "zt", "end")

    Y = PT           # lokální posun svisle: souřadnice níže jsou absolutní v rámci panelu

    # ---- venkovní jednotky
    if variant == 1:
        R(x(55), 180, 200, 90, fill="#F4F8F5", sw=2.2, rx=8)
        T(x(155), 212, "TČ REO X50", "tb", "middle")
        T(x(155), 232, "vzduch / voda · 50 kW jmen.", "ts", "middle")
        T(x(155), 250, "25 kW při −15 °C / 55 °C", "ts", "middle")
    else:
        R(x(55), 180, 180, 90, fill="#F4F8F5", sw=2.2, rx=8)
        T(x(145), 210, "TČ 1 — REO X50", "tbs", "middle")
        T(x(145), 228, "50 kW jmen. · 25 kW", "ts", "middle")
        T(x(145), 245, "při −15 °C / 55 °C", "ts", "middle")
        T(x(145), 262, "priorita: vytápění", "tx", "middle")
        R(x(250), 180, 180, 90, fill="#F4F8F5", sw=2.2, rx=8)
        T(x(340), 210, "TČ 2 — REO X50", "tbs", "middle")
        T(x(340), 228, "50 kW jmen. · 25 kW", "ts", "middle")
        T(x(340), 245, "při −15 °C / 55 °C", "ts", "middle")
        T(x(340), 262, "priorita: TUV + záloha", "tx", "middle")

    # ---- nádrže
    tank(x(215), 390, 75, 230, "#EAF1EC", "AKU 1", "1 000 l")
    tank(x(305), 390, 75, 230, "#EAF1EC", "AKU 2", "1 000 l")
    P(f"M{x(290)},420 L{x(305)},420", INK, 4)
    P(f"M{x(290)},590 L{x(305)},590", INK, 4)

    for i, tx0 in enumerate((500, 590, 680)):
        tank(x(tx0), 390, 75, 230, "#FDF3EA", f"TUV {i+1}", "1 000 l")
    for a, b in ((575, 590), (665, 680)):
        P(f"M{x(a)},420 L{x(b)},420", INK, 4)
        P(f"M{x(a)},590 L{x(b)},590", INK, 4)

    # ---- topné hady v zásobnících TUV (nabíjení z okruhu TČ)
    for cx in (537, 627, 717):
        coil(x(cx), 440, 58)
    for a, b in ((566, 598), (656, 688)):
        P(f"M{x(a)},440 L{x(b)},440", RED, 3)

    # ---- výstupní bloky
    R(x(100), 690, 270, 68, fill="#EEF3F9", stroke=INK, sw=1.8, rx=8)
    T(x(235), 716, "ÚSTŘEDNÍ TOPENÍ OBJEKTU", "tbs", "middle")
    T(x(235), 736, "otopná soustava — 17 bytových jednotek", "tx", "middle")

    R(x(470), 690, 315, 68, fill="#FDF3EA", stroke=INK, sw=1.8, rx=8)
    T(x(627), 716, "ROZVOD TUV DO BYTŮ", "tbs", "middle")
    T(x(627), 736, "701 m³ / rok · včetně cirkulace", "tx", "middle")

    # ================= POTRUBÍ =================
    # --- vratná (primár) ---
    P(f"M{x(370)},620 L{x(370)},785 L{x(70)},785 L{x(70)},270", BLUE)
    if variant == 2:
        P(f"M{x(70)},330 L{x(370)},330 L{x(370)},270", BLUE)
        gap(x(120), 330, horiz=True)          # vratná TČ2 podbíhá topnou TČ1

    # --- sekundární okruhy (kreslí se před primárem kvůli křížení) ---
    # ÚT: z AKU 1 nahoře doleva a dolů
    P(f"M{x(252)},390 L{x(252)},345 L{x(185)},345 L{x(185)},690", RED)
    gap(x(185), 430)                          # ÚT podbíhá topnou primáru
    P(f"M{x(230)},690 L{x(230)},620", BLUE)   # vratná ÚT do spodku AKU 1

    # nabíjení TUV: AKU 2 -> topné hady v zásobnících -> AKU 2
    P(f"M{x(342)},390 L{x(342)},360 L{x(790)},360 L{x(790)},440 L{x(746)},440", RED)
    P(f"M{x(508)},440 L{x(470)},440 L{x(470)},530 L{x(380)},530", BLUE)
    gap(x(775), 360, horiz=True)              # nabíjecí okruh podbíhá výstup TUV

    # --- topná (primár) ---
    P(f"M{x(120)},270 L{x(120)},430 L{x(215)},430", RED)
    if variant == 2:
        P(f"M{x(320)},270 L{x(320)},305 L{x(120)},305", RED)

    # --- TUV sekundár ---
    P(f"M{x(537)},620 L{x(537)},655 L{x(452)},655", BLUE)
    add(f'<path d="M{x(462)},649 L{x(450)},655 L{x(462)},661 Z" fill="{BLUE}"/>')
    T(x(446), 659, "studená voda", "tx", "end")
    P(f"M{x(717)},390 L{x(717)},340 L{x(775)},340 L{x(775)},690", ORA)
    P(f"M{x(690)},690 L{x(690)},645 L{x(717)},645 L{x(717)},620", ORA2, 4, dash="9 6")

    # ================= ARMATURY =================
    U("chk", x(120), 350, 90)
    U("v",   x(120), 395, 90)
    U("pump", x(70), 480)
    U("flt",  x(70), 560)
    P(f"M{x(70)},350 L{x(46)},350", BLUE, 3)
    U("sv", x(44), 350, 180)
    P(f"M{x(70)},412 L{x(42)},412 L{x(42)},418", BLUE, 3)
    U("exp", x(42), 440)
    U("pump", x(430), 360)
    U("mix", x(185), 500)
    U("pump", x(185), 585)
    U("ts", x(252), 345)
    if variant == 2:
        U("chk", x(250), 305, 180)
        U("v", x(365), 330)

    # ================= BIVALENCE / KASKÁDA =================
    if variant == 1:
        for cx in (252, 342):
            spiral(x(cx), 555, 46)
        for cx in (537, 627, 717):
            spiral(x(cx), 555, 46)
        R(x(450), 180, 335, 90, fill="#FFF6E9", stroke="#DA8718", sw=1.8, rx=8)
        T(x(466), 203, "ELEKTRICKÁ BIVALENCE", "amb")
        T(x(466), 222, "Topné patrony přímo v akumulaci i v zásobnících TUV.", "ts")
        T(x(466), 239, "Kryjí špičky v nejchladnějších dnech a zastoupí zdroj", "ts")
        T(x(466), 256, "při odstávce — objekt zůstane vytápěn.", "ts")
    else:
        R(x(450), 180, 335, 90, fill="#fff", stroke="#DCE6DF", sw=1.5, rx=8)
        T(x(466), 203, "KASKÁDNÍ REGULACE", "tbs")
        T(x(466), 222, "TČ 1 přednostně vytápění, TČ 2 přednostně TUV.", "ts")
        T(x(466), 239, "Při deficitu výkonu nebo poruše jedné jednotky", "ts")
        T(x(466), 256, "převezme druhá celý provoz — objekt je vždy vytápěn.", "ts")

    T(x(785), 780, "Koncepční schéma — dimenze potrubí, armatury a rozsah MaR upřesní prováděcí projekt.", "tx", "end")



def bottom_combined():
    # =================================================================== PATA
    BY = 815

    # --- legenda ---
    R(30, BY, 550, 195, fill="#fff", stroke="#DCE6DF", sw=1.5, rx=8)
    T(48, BY+26, "LEGENDA", "tbs")
    leg = [(RED, "topná voda ze zdroje"), (BLUE, "vratná voda"),
           (ORA, "teplá užitková voda"), (ORA2, "cirkulace TUV")]
    for i, (c, lab) in enumerate(leg):
        yy = BY + 50 + i*24
        dsh = ' stroke-dasharray="9 6"' if c == ORA2 else ''
        add(f'<line x1="52" y1="{yy}" x2="94" y2="{yy}" stroke="{c}" stroke-width="5" '
            f'stroke-linecap="round"{dsh}/>')
        T(104, yy+4, lab, "ts")
    syms = [("pump", "oběhové čerpadlo"), ("chk", "zpětná klapka"),
            ("v", "uzávěr"), ("flt", "filtr"),
            ("exp", "expanzní nádoba"), ("sv", "pojistný ventil"),
            ("mix", "směšovací ventil"), ("ts", "teplotní čidlo")]
    for i, (sy, lab) in enumerate(syms):
        col, row = i % 4, i // 4
        sx = 290 + row*150
        sy_ = BY + 52 + col*26
        U(sy, sx, sy_)
        T(sx + 20, sy_ + 4, lab, "ts")
    coil(70, BY+152, 46)
    T(104, BY+156, "topný had v zásobníku TUV", "ts")
    spiral(70, BY+176, 40)
    T(104, BY+180, "elektrická topná patrona — jen varianta 1", "ts")

    # --- společné pro obě varianty ---
    R(600, BY, 520, 195, fill="#fff", stroke="#DCE6DF", sw=1.5, rx=8)
    T(618, BY+26, "SPOLEČNÉ PRO OBĚ VARIANTY", "tbs")
    spol = [
        "Akumulace 2 × 1 000 l — hydraulicky odděluje zdroj od otopné",
        "soustavy, zajišťuje průtok do ÚT a omezuje taktování čerpadla.",
        "Zásobníky TUV 3 × 1 000 l — kapacita pro ranní a večerní",
        "odběrové špičky 17 bytových jednotek (701 m³ TUV za rok).",
        "Ohřev TUV topnými hady přímo v zásobnících, nabíjenými",
        "z okruhu tepelného čerpadla přes nabíjecí čerpadlo.",
        "Kompletní strojovna: čerpadla, expanze, pojistné a uzavírací",
        "armatury, filtrace, měření teplot, regulace a vzdálený dohled.",
    ]
    for i, ln in enumerate(spol):
        T(618, BY + 52 + i*17, ln, "ts")

    # --- rozdíl variant ---
    R(1140, BY, 530, 195, fill="#fff", stroke="#DCE6DF", sw=1.5, rx=8)
    T(1158, BY+26, "V ČEM SE VARIANTY LIŠÍ", "tbs")
    rows = [("", "Varianta 1", "Varianta 2"),
            ("Tepelná čerpadla", "1 × REO X50", "2 × REO X50"),
            ("Výkon při −15 °C", "25 kW", "50 kW"),
            ("Krytí špiček", "elektrické patrony", "druhé čerpadlo"),
            ("Provoz při poruše", "jen elektřinou", "druhou jednotkou"),
            ("Cena bez DPH", "1 350 000 Kč", "1 600 000 Kč"),
            ("Prostá návratnost", "3,8 roku", "4,5 roku")]
    for i, (a, b, c) in enumerate(rows):
        yy = BY + 52 + i*19
        if i == 0:
            add(f'<rect x="1158" y="{yy-13}" width="494" height="19" fill="{GRN}"/>')
            T(1372, yy, b, "wts"); T(1522, yy, c, "wts")
        else:
            if i % 2 == 0:
                add(f'<rect x="1158" y="{yy-13}" width="494" height="19" fill="#F4F8F5"/>')
            T(1166, yy, a, "ts"); T(1372, yy, b, "ts"); T(1522, yy, c, "ts")

    T(30, 1022, "ThermaVera Energy · koncepční schéma k cenové nabídce · orientační podklad, nenahrazuje projektovou dokumentaci", "tx")
    T(W-30, 1022, "18. 9. 2026", "tx", "end")


def legend_single(bx, by, bw, variant):
    """Kompaktní vodorovná legenda pod jeden panel."""
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
        sx = bx + 260 + row*150
        yy = by + 48 + col*24
        U(sy, sx, yy)
        T(sx + 20, yy + 4, lab, "ts")
    coil(bx + 590, by + 50, 46)
    T(bx + 624, by + 54, "topný had v zásobníku TUV", "ts")
    if variant == 1:
        spiral(bx + 590, by + 76, 40)
        T(bx + 624, by + 80, "elektrická topná patrona", "ts")


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


SUB = "17 b.j. · tepelná ztráta 30 kW při −15 °C · ÚT 210 GJ + TUV 231 GJ / rok"

# --- přehledový list A3 s oběma variantami ---
def _combined():
    panel(PAX, 1)
    panel(PBX, 2)
    bottom_combined()

build("schema-kotelny.svg", 1700, 1040,
      "Kotelna BD Jandova 7, Ostrava-Zábřeh — koncepční schéma nabízených variant",
      SUB, "TV-BDJ-01 · rev. 0", _combined)

# --- jednotlivé varianty (do textu nabídky, čitelné na šířku A4) ---
for _v, _code, _nazev in ((1, "TV-BDJ-02", "varianta 1 — jedno tepelné čerpadlo s elektrickou bivalencí"),
                          (2, "TV-BDJ-03", "varianta 2 — kaskáda dvou tepelných čerpadel")):
    def _single(v=_v):
        panel(30, v)
        legend_single(30, 815, 815, v)
        T(30, 990, "ThermaVera Energy · koncepční schéma k cenové nabídce", "tx")
        T(845, 990, "18. 9. 2026", "tx", "end")
    build(f"schema-varianta-{_v}.svg", 875, 1005,
          "Kotelna BD Jandova 7 — koncepční schéma",
          "17 b.j. · tepelná ztráta 30 kW při −15 °C", f"{_code} · rev. 0", _single)
