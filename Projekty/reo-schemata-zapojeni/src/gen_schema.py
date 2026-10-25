#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Schéma zapojení TČ REO HEATING pro kutily — Varianta 1: pouze vytápění s AKU.

Vytváří ../schema-varianta-1.svg (a PNG přes Chrome headless, viz README).
Spuštění:  python3 reo-schemata-zapojeni/src/gen_schema.py
Styl: zjednodušené piktogramy + číslované popisky (vzor: REO/Fotky a schema).
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.expanduser("~/Claude/REO/logo/logo-reo-heating.svg")

W, H = 1400, 1000
RED, BLUE = "#D9342B", "#2468B3"      # výstup (topná) / vratka
YEL = "#E3A71B"                       # elektrické ovládání, signál
INK, GREY = "#22272A", "#6B7378"
GRN, GRNL = "#34A263", "#E9F6EE"      # zelená REO HEATING

o = []
def add(s): o.append(s)
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
def T(x, y, s, cls="t", anchor="start"):
    add(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{esc(s)}</text>')
def R(x, y, w, h, fill="#fff", stroke=INK, sw=2, rx=0, extra=""):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{st}{extra}/>')
def P(d, c, w=6, dash=None):
    ds = f' stroke-dasharray="{dash}"' if dash else ''
    add(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}" '
        f'stroke-linecap="round" stroke-linejoin="round"{ds}/>')
def arrow(x, y, ang, c):
    """Šipka směru proudění na potrubí (ang: 0 vpravo, 90 dolů, 180 vlevo, 270 nahoru)."""
    dx, dy = (0, -17) if ang in (0, 180) else (-17, 0)
    add(f'<path d="M-8,-7 L7,0 L-8,7 Z" fill="{c}" transform="translate({x + dx},{y + dy}) rotate({ang})"/>')
def num(x, y, n):
    add(f'<circle cx="{x}" cy="{y}" r="13" fill="{GRN}"/>')
    T(x, y + 5, str(n), "num", "middle")

# ------------------------------------------------------------------ symboly
def valve(x, y, vert=False, c=INK):
    """Uzavírací kulový ventil: dva trojúhelníky + páčka."""
    rot = 90 if vert else 0
    add(f'<g transform="translate({x},{y}) rotate({rot})">'
        f'<path d="M-12,-9 L0,0 L-12,9 Z M12,-9 L0,0 L12,9 Z" fill="#fff" stroke="{c}" stroke-width="2.2" stroke-linejoin="round"/>'
        f'<line x1="0" y1="0" x2="0" y2="-15" stroke="{c}" stroke-width="2.2"/>'
        f'<line x1="-8" y1="-15" x2="8" y2="-15" stroke="{c}" stroke-width="3" stroke-linecap="round"/></g>')

def antifreeze(x, y):
    """Protizámrazový ventil: těleso ventilu, výpust dolů, vločka."""
    add(f'<g transform="translate({x},{y})">'
        f'<rect x="-15" y="-11" width="30" height="22" rx="4" fill="#fff" stroke="{INK}" stroke-width="2.2"/>'
        f'<line x1="0" y1="11" x2="0" y2="26" stroke="{INK}" stroke-width="2.6"/>'
        f'<path d="M-5,24 L0,32 L5,24 Z" fill="{INK}"/>')
    for a in (0, 60, 120):
        add(f'<line x1="-7" y1="0" x2="7" y2="0" stroke="{BLUE}" stroke-width="2" stroke-linecap="round" transform="rotate({a})"/>')
    add('</g>')

def separator(x, y):
    """Separátor vzduchu a nečistot s automatickým odvzdušněním a pojistným ventilem."""
    add(f'<g transform="translate({x},{y})">'
        f'<rect x="-17" y="-30" width="34" height="62" rx="10" fill="#fff" stroke="{INK}" stroke-width="2.2"/>'
        f'<path d="M-9,-14 h18 M-9,-4 h18 M-9,6 h18 M-9,16 h18" stroke="#B9C2C7" stroke-width="2"/>'
        # automatický odvzdušňovací ventil nahoře
        f'<rect x="-6" y="-46" width="12" height="16" rx="2" fill="#fff" stroke="{INK}" stroke-width="2"/>'
        f'<path d="M0,-50 v-8 M-5,-62 l5,4 l5,-4" fill="none" stroke="{GREY}" stroke-width="1.8" stroke-linecap="round"/>'
        # odkalení dole
        f'<line x1="0" y1="32" x2="0" y2="42" stroke="{INK}" stroke-width="2.4"/>'
        f'<line x1="-6" y1="42" x2="6" y2="42" stroke="{INK}" stroke-width="2.6" stroke-linecap="round"/>'
        # pojistný ventil vpravo
        f'<line x1="17" y1="-18" x2="30" y2="-18" stroke="{INK}" stroke-width="2.4"/>'
        f'<path d="M30,-26 L42,-18 L30,-10 Z" fill="#fff" stroke="{INK}" stroke-width="2"/>'
        f'<path d="M42,-18 v14" stroke="{INK}" stroke-width="2.2"/>'
        f'<path d="M34,-30 l4,-3 l-4,-3 l4,-3" fill="none" stroke="{GREY}" stroke-width="1.6"/>'
        '</g>')

def pump(x, y, ang=0):
    add(f'<g transform="translate({x},{y})"><circle r="17" fill="#fff" stroke="{INK}" stroke-width="2.4"/>'
        f'<path d="M-7,-9 L10,0 L-7,9 Z" fill="{INK}" transform="rotate({ang})"/></g>')

def exp_vessel(x, y):
    add(f'<g transform="translate({x},{y})">'
        f'<rect x="-22" y="-28" width="44" height="56" rx="20" fill="#F3F5F6" stroke="{INK}" stroke-width="2.2"/>'
        f'<line x1="-22" y1="0" x2="22" y2="0" stroke="{INK}" stroke-width="1.6"/></g>')

def heat_pump(x, y, w=190, h=180):
    R(x, y, w, h, fill="#F5F7F8", stroke=INK, sw=2.6, rx=12)
    cx, cy = x + 72, y + h / 2
    for r in (58, 46, 34, 22):
        add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{INK}" stroke-width="{2.4 if r == 58 else 1.4}"/>')
    for a in range(0, 360, 30):
        add(f'<line x1="{cx}" y1="{cy}" x2="{cx + 58}" y2="{cy}" stroke="{INK}" stroke-width="1.2" '
            f'transform="rotate({a} {cx} {cy})"/>')
    add(f'<circle cx="{cx}" cy="{cy}" r="8" fill="{INK}"/>')
    R(x + w - 50, y + 26, 34, 22, fill="#fff", stroke=INK, sw=2, rx=3)
    add(f'<line x1="{x + w - 33}" y1="{y + 62}" x2="{x + w - 33}" y2="{y + h - 26}" stroke="{GREY}" stroke-width="2"/>')
    R(x + 16, y + h, 26, 10, fill=INK, stroke=None)
    R(x + w - 42, y + h, 26, 10, fill=INK, stroke=None)

def tank(x, y, w, h):
    add(f'<defs><linearGradient id="ak" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="#F7B9A6"/><stop offset="0.5" stop-color="#F3E3E6"/>'
        f'<stop offset="1" stop-color="#B9D1EE"/></linearGradient></defs>')
    R(x, y, w, h, fill="url(#ak)", stroke=INK, sw=2.6, rx=46)
    T(x + w / 2, y + h / 2 - 8, "AKU", "tank", "middle")
    T(x + w / 2, y + h / 2 + 14, "akumulační", "ts", "middle")
    T(x + w / 2, y + h / 2 + 30, "nádrž", "ts", "middle")

def radiator(x, y, w=160, h=74):
    R(x, y, w, h, fill="#fff", stroke=INK, sw=2.4, rx=8)
    for k in range(1, 11):
        xx = x + k * w / 11
        add(f'<line x1="{xx}" y1="{y + 10}" x2="{xx}" y2="{y + h - 10}" stroke="{INK}" stroke-width="2.2" stroke-linecap="round"/>')

def thermostat(x, y):
    R(x, y, 66, 52, fill="#fff", stroke=INK, sw=2.4, rx=10)
    R(x + 9, y + 9, 48, 22, fill=GRNL, stroke=GRN, sw=1.5, rx=3)
    T(x + 33, y + 25, "21 °C", "lcd", "middle")
    add(f'<circle cx="{x + 23}" cy="{y + 41}" r="3.4" fill="{INK}"/><circle cx="{x + 43}" cy="{y + 41}" r="3.4" fill="{INK}"/>')

def waves(x, y, side):
    """Rádiové vlny; side=-1 otevřené doleva, +1 doprava."""
    for r in (10, 19, 28):
        a0, a1 = (150, 210) if side < 0 else (-30, 30)
        import math
        x0, y0 = x + r * math.cos(math.radians(a0)), y + r * math.sin(math.radians(a0))
        x1, y1 = x + r * math.cos(math.radians(a1)), y + r * math.sin(math.radians(a1))
        sweep = 0 if side < 0 else 1
        add(f'<path d="M{x0:.1f},{y0:.1f} A{r},{r} 0 0 {sweep} {x1:.1f},{y1:.1f}" fill="none" '
            f'stroke="{YEL}" stroke-width="3" stroke-linecap="round"/>')

def receiver(x, y):
    R(x, y, 74, 44, fill="#fff", stroke=INK, sw=2.4, rx=6)
    T(x + 37, y + 20, "PŘIJÍMAČ", "rs", "middle")
    T(x + 37, y + 34, "relé", "tx", "middle")
    add(f'<line x1="{x + 74}" y1="{y + 10}" x2="{x + 88}" y2="{y - 6}" stroke="{INK}" stroke-width="2.4" stroke-linecap="round"/>')

# ------------------------------------------------------------------ list
def logo(x, y, w):
    svg = open(LOGO, encoding="utf-8").read()
    inner = re.sub(r"^<svg[^>]*>|</svg>\s*$", "", svg.strip())
    h = w * 101 / 264
    add(f'<svg x="{x}" y="{y}" width="{w}" height="{h:.1f}" viewBox="24 22 264 101">{inner}</svg>')

add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
    f'font-family="Avenir Next, Arial, Helvetica, sans-serif">')
add(f'''<style>
 .t{{fill:{INK};font-size:14px}}
 .ts{{fill:{INK};font-size:13px}}
 .tx{{fill:{GREY};font-size:11.5px}}
 .tb{{fill:{INK};font-size:15px;font-weight:bold}}
 .ttl{{fill:{INK};font-size:28px;font-weight:bold}}
 .sub{{fill:{GRN};font-size:18px;font-weight:bold}}
 .zone{{fill:{GREY};font-size:12px;font-weight:bold;letter-spacing:1.6px}}
 .num{{fill:#fff;font-size:14px;font-weight:bold}}
 .tank{{fill:{INK};font-size:24px;font-weight:bold}}
 .lcd{{fill:{GRN};font-size:12px;font-weight:bold}}
 .rs{{fill:{INK};font-size:10.5px;font-weight:bold;letter-spacing:.6px}}
 .lab{{fill:{INK};font-size:13px;font-weight:bold}}
 .hd{{fill:{GRN};font-size:14px;font-weight:bold;letter-spacing:1.4px}}
</style>''')
R(0, 0, W, H, fill="#fff", stroke=None)

# záhlaví
logo(36, 22, 190)
T(256, 62, "Schéma zapojení tepelného čerpadla", "ttl")
T(256, 92, "Varianta 1 — pouze vytápění s akumulační nádrží", "sub")
T(W - 36, 58, "REO-SCH-V1 · RH030–RH060", "zone", "end")
T(W - 36, 78, "rev. 0 · 10/2026", "tx", "end")
add(f'<line x1="30" y1="118" x2="{W - 30}" y2="118" stroke="{GRN}" stroke-width="3"/>')

# zóny
ZT, ZB = 140, 650
R(30, ZT, 390, ZB - ZT, fill="#F2F6F9", stroke=None, rx=10)
R(960, ZT, 410, ZB - ZT, fill="#FBF6EF", stroke=None, rx=10)
for xx in (420, 960):
    add(f'<line x1="{xx}" y1="{ZT}" x2="{xx}" y2="{ZB}" stroke="{GREY}" stroke-width="2" stroke-dasharray="10 7"/>')
T(48, ZT + 26, "VENKU", "zone")
T(440, ZT + 26, "TECHNICKÁ MÍSTNOST", "zone")
T(1000, ZT + 26, "OBYTNÉ PROSTORY", "zone")
T(424, ZB - 12, "obvodová zeď", "tx")
# varování R290 ve venkovní zóně
R(46, 540, 358, 92, fill="#FFF4DA", stroke="#E3A71B", sw=2, rx=8)
add(f'<path d="M66,560 L80,584 L52,584 Z" fill="#E3A71B"/>')
T(66, 581, "!", "num", "middle")
T(92, 565, "R290 je hořlavý plyn", "lab")
T(92, 584, "Separátor (4) patří VENKU hned za jednotku —", "tx")
T(92, 600, "vzduch i případně uniklé chladivo musí odejít", "tx")
T(92, 616, "do volného prostoru, nikdy ne do domu.", "tx")

# ---------------------------------------------------------------- potrubí
FY, RY = 300, 390            # výstup / vratka u TČ
TX, TY, TW, TH = 640, 220, 140, 360   # AKU
TIN, TOUT = TY + 50, TY + TH - 50     # horní / spodní hrdla AKU (270 / 530)

# primár: TČ → AKU (výstup)
P(f"M250,{FY} L560,{FY} L560,{TIN} L{TX},{TIN}", RED)
# primár: AKU → TČ (vratka)
P(f"M{TX},{TOUT} L540,{TOUT} L540,{RY} L250,{RY}", BLUE)
P(f"M590,{TOUT} L590,580", BLUE, 4)          # odbočka k expanzní nádobě
# sekundár: AKU → radiátory
P(f"M{TX + TW},{TIN} L1020,{TIN} L1020,420 L1070,420", RED)
P(f"M1020,{TIN + 8} L1070,{TIN + 8}", RED)
# sekundár: radiátory → AKU
P(f"M1230,{TIN + 70} L1280,{TIN + 70} M1230,486 L1280,486", BLUE)
P(f"M1280,{TIN + 70} L1280,580 L820,580 L820,{TOUT} L{TX + TW},{TOUT}", BLUE)

# šipky směru
arrow(510, FY, 0, RED); arrow(470, RY, 180, BLUE)
arrow(990, TIN, 0, RED); arrow(1000, 580, 180, BLUE)

# ---------------------------------------------------------------- prvky
heat_pump(60, 255, h=200)
valve(372, FY); valve(290, RY)                     # 2 – uzávěry u venkovní jednotky
antifreeze(360, RY)                                 # 3 – protizámrazový ventil na vratce
separator(298, FY)                                  # 4 – separátor venku hned za jednotkou (vzduch + R290)
tank(TX, TY, TW, TH)
exp_vessel(590, 605)
valve(830, TIN); pump(885, TIN); valve(940, TIN)    # 7 – sekundární čerpadlo
valve(900, 580)
radiator(1070, TIN - 12); radiator(1070, 412)
thermostat(1250, 190)
receiver(848, 164)

# čidlo AKU → řízení TČ
add(f'<circle cx="{TX + 22}" cy="448" r="9" fill="#fff" stroke="{INK}" stroke-width="2"/>')
T(TX + 22, 452, "T", "rs", "middle")
P(f"M{TX + 13},448 L250,448", YEL, 2.4, dash="7 5")
# přijímač → čerpadlo (230 V)
P(f"M885,208 L885,{TIN - 17}", YEL, 3)
waves(940, 158, 1)
waves(1244, 214, -1)
P("M975,168 L1206,208", YEL, 1.6, dash="2 7")
T(1100, 210, "bezdrátový signál", "tx", "middle")

# ---------------------------------------------------------------- čísla + krátké popisky
num(80, 232, 1);  T(101, 237, "REO RH030–RH060", "lab")
num(372, 340, 2); num(290, 428, 2)
num(396, 428, 3)
num(298, 212, 4)
num(TX + TW / 2, 202, 5)
num(548, 612, 6)
num(885, 312, 7)
num(818, 186, 8)
num(1283, 270, 9)
num(1150, 512, 10)
num(TX + 22, 478, 11)
T(155, 488, "venkovní jednotka", "tx", "middle")

# ---------------------------------------------------------------- spodní část
BY = 680
R(30, BY, 660, 290, fill="#fff", stroke="#DDE3E6", sw=1.5, rx=10)
T(52, BY + 32, "SOUČÁSTI", "hd")
parts = [
    (1, "Tepelné čerpadlo REO RH030–RH060", "venkovní jednotka (monoblok), chladivo R290"),
    (2, "Uzavírací ventily", "u venkovní jednotky na výstupu i vratce"),
    (3, "Protizámrazový ventil Caleffi", "na vratce, venku — při mrazu a výpadku vypustí vodu"),
    (4, "Separátor s odvzdušněním a poj. ventilem", "venku hned za jednotkou — únik vzduchu i R290"),
    (5, "Akumulační nádrž (AKU)", "odděluje okruh TČ a okruh topení"),
    (6, "Expanzní nádoba", "vyrovnává roztažnost vody"),
    (7, "Sekundární oběhové čerpadlo", "s uzávěry, žene vodu z AKU do topení"),
    (8, "Přijímač termostatu (relé)", "zapíná a vypíná čerpadlo 7"),
    (9, "Bezdrátový termostat", "v obytné místnosti, cca 1,5 m nad podlahou"),
    (10, "Radiátory / otopná soustava", "stávající topení v domě"),
    (11, "Čidlo teploty AKU", "připojené k řídicí jednotce TČ"),
]
for i, (n, a, b) in enumerate(parts):
    col, row = (0, i) if i < 6 else (1, i - 6)
    x = 52 + col * 330
    y = BY + 64 + row * 37
    num(x + 12, y, n)
    T(x + 34, y - 2, a, "ts")
    T(x + 34, y + 13, b, "tx")
# legenda barev
lx, ly = 668, 616
for k, (c, lab, d) in enumerate([(RED, "výstup — teplá voda", None), (BLUE, "vratka — ochlazená voda", None),
                                  (YEL, "elektrické ovládání / signál", "7 5")]):
    yy = ly + k * 17
    ds = f' stroke-dasharray="{d}"' if d else ''
    add(f'<line x1="{lx}" y1="{yy}" x2="{lx + 34}" y2="{yy}" stroke="{c}" stroke-width="{5 if not d else 3}" stroke-linecap="round"{ds}/>')
    T(lx + 44, yy + 4, lab, "tx")

R(710, BY, 660, 290, fill=GRNL, stroke=None, rx=10)
T(732, BY + 32, "JAK TO FUNGUJE", "hd")
how = [
    "Tepelné čerpadlo (1) ohřívá vodu v akumulační nádrži (5). Teplotu",
    "hlídá čidlo (11) — TČ se samo zapíná a vypíná.",
    "Bezdrátový termostat (9) v obýváku pošle signál přijímači (8),",
    "ten zapne čerpadlo (7) a teplá voda z AKU jde do radiátorů (10).",
    "Po dosažení nastavené teploty termostat čerpadlo (7) vypne.",
]
for i, s in enumerate(how):
    T(732, BY + 62 + i * 21, s, "ts")
T(732, BY + 186, "TIPY PRO MONTÁŽ", "hd")
tips = [
    "• Uzávěry (2) dejte co nejblíž venkovní jednotce — kvůli servisu.",
    "• Protizámrazový ventil (3) patří venku na vratku, výpustí dolů.",
    "• Separátor (4) venku hned za jednotkou, svisle, odvzdušnění nahoru.",
    "• V místnosti s termostatem nechte hlavice radiátorů otevřené.",
]
for i, s in enumerate(tips):
    T(732, BY + 212 + i * 19, s, "ts")

T(30, H - 12, "Zjednodušené orientační schéma — dimenze potrubí, objem AKU a velikost expanzní nádoby "
  "určete podle návodu k TČ a konkrétního domu.", "tx")
T(W - 30, H - 12, "REO HEATING", "zone", "end")
add('</svg>')

dst = os.path.normpath(os.path.join(HERE, "..", "schema-varianta-1.svg"))
open(dst, "w", encoding="utf-8").write("\n".join(o))
print("zapsáno:", dst)
