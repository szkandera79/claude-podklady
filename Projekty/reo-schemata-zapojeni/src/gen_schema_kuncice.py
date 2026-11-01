#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Schéma zapojení TČ REO HEATING pro kutily — Realizace Kunčice p. O. — krok 1: AKU 100 l + venkovní jednotka.

Vytváří ../schema-kuncice-aku100.svg (a PNG přes Chrome headless, viz README).
Spuštění:  python3 reo-schemata-zapojeni/src/gen_schema_kuncice.py
Styl: zjednodušené piktogramy + číslované popisky (vzor: REO/Fotky a schema).
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.expanduser("~/Claude/REO/logo/logo-reo-heating.svg")

W, H = 1400, 1090
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

# ------------------------------------------------------------------ doplňkové symboly
def air_vent(x, y):
    """Automatický odvzdušňovací ventil (plovákový) — nasazen nahoru na potrubí v bodě (x, y)."""
    add(f'<g transform="translate({x},{y})">'
        f'<line x1="0" y1="0" x2="0" y2="-10" stroke="{INK}" stroke-width="2.6"/>'
        f'<rect x="-8" y="-30" width="16" height="20" rx="3" fill="#fff" stroke="{INK}" stroke-width="2.2"/>'
        f'<circle cx="0" cy="-20" r="3.4" fill="{GREY}"/>'
        f'<path d="M0,-34 v-8 M-5,-46 l5,4 l5,-4" fill="none" stroke="{GREY}" stroke-width="1.8" stroke-linecap="round"/></g>')

def safety_valve(x, y, drain=40):
    """Pojistný (přetlakový) ventil na odbočce nahoru, výfuk do strany a dolů do odpadu."""
    add(f'<g transform="translate({x},{y})">'
        f'<line x1="0" y1="0" x2="0" y2="-14" stroke="{INK}" stroke-width="2.6"/>'
        f'<path d="M-9,-14 L9,-14 L0,-30 Z" fill="#fff" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>'
        f'<path d="M-4,-34 l5,-4 l-5,-4 l5,-4" fill="none" stroke="{INK}" stroke-width="1.8"/>'
        f'<line x1="9" y1="-20" x2="22" y2="-20" stroke="{INK}" stroke-width="2.2"/>'
        f'<line x1="22" y1="-20" x2="22" y2="{drain}" stroke="{GREY}" stroke-width="2.2" stroke-dasharray="5 4"/>'
        f'<path d="M14,{drain} h16 l-4,9 h-8 Z" fill="#fff" stroke="{GREY}" stroke-width="1.8"/></g>')

def gauge(x, y, label="bar"):
    """Manometr / teploměr — kruh s ručičkou na krátké odbočce."""
    add(f'<g transform="translate({x},{y})">'
        f'<line x1="0" y1="0" x2="0" y2="-10" stroke="{INK}" stroke-width="2.6"/>'
        f'<circle cx="0" cy="-23" r="13" fill="#fff" stroke="{INK}" stroke-width="2.2"/>'
        f'<line x1="0" y1="-23" x2="6" y2="-30" stroke="{RED}" stroke-width="2" stroke-linecap="round"/>'
        f'<text x="0" y="-15" class="g" text-anchor="middle">{label}</text></g>')

def drain_cock(x, y):
    """Vypouštěcí kohout dolů."""
    add(f'<g transform="translate({x},{y})">'
        f'<line x1="0" y1="0" x2="0" y2="12" stroke="{INK}" stroke-width="2.6"/>'
        f'<path d="M-8,12 L0,24 L8,12 Z" fill="#fff" stroke="{INK}" stroke-width="2"/>'
        f'<line x1="0" y1="18" x2="12" y2="18" stroke="{INK}" stroke-width="2.6" stroke-linecap="round"/></g>')

def rad_vent(x, y):
    """Ruční odvzdušňovací ventil radiátoru (malý šroubek nahoře)."""
    add(f'<g transform="translate({x},{y})"><rect x="-5" y="-12" width="10" height="12" fill="#fff" stroke="{INK}" stroke-width="2"/>'
        f'<path d="M0,-15 v-6 M-4,-24 l4,3 l4,-3" fill="none" stroke="{GREY}" stroke-width="1.6"/></g>')

def tank100(x, y, w, h):
    add(f'<defs><linearGradient id="ak" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="#F7B9A6"/><stop offset="0.5" stop-color="#F3E3E6"/>'
        f'<stop offset="1" stop-color="#B9D1EE"/></linearGradient></defs>')
    R(x, y, w, h, fill="url(#ak)", stroke=INK, sw=2.6, rx=34)
    T(x + w / 2, y + h / 2 - 4, "AKU", "tank", "middle")
    T(x + w / 2, y + h / 2 + 18, "100 l", "tb", "middle")
    T(x + w / 2, y + h / 2 + 36, "topná voda", "tx", "middle")

# ------------------------------------------------------------------ list
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
 .g{{fill:{GREY};font-size:7px}}
</style>''')
R(0, 0, W, H, fill="#fff", stroke=None)

# záhlaví
logo(36, 22, 190)
T(256, 62, "Schéma zapojení — AKU 100 l s venkovní jednotkou", "ttl")
T(256, 92, "Podle realizace Kunčice pod Ondřejníkem · krok 1: pouze vytápění", "sub")
T(W - 36, 58, "REO-SCH-K1 · RH030–RH060", "zone", "end")
T(W - 36, 78, "rev. 3 · 11/2026", "tx", "end")
add(f'<line x1="30" y1="118" x2="{W - 30}" y2="118" stroke="{GRN}" stroke-width="3"/>')

# zóny
ZT, ZB = 140, 660
R(30, ZT, 390, ZB - ZT, fill="#F2F6F9", stroke=None, rx=10)
R(1040, ZT, 330, ZB - ZT, fill="#FBF6EF", stroke=None, rx=10)
for xx in (420, 1040):
    add(f'<line x1="{xx}" y1="{ZT}" x2="{xx}" y2="{ZB}" stroke="{GREY}" stroke-width="2" stroke-dasharray="10 7"/>')
T(48, ZT + 26, "VENKU", "zone")
T(440, ZT + 26, "TECHNICKÁ MÍSTNOST (SKLEP)", "zone")
T(1060, ZT + 26, "OBYTNÉ PROSTORY", "zone")
T(424, ZB - 12, "obvodová zeď", "tx")
R(46, 552, 358, 92, fill="#FFF4DA", stroke="#E3A71B", sw=2, rx=8)
add(f'<path d="M66,572 L80,596 L52,596 Z" fill="#E3A71B"/>')
T(66, 593, "!", "num", "middle")
T(92, 577, "R290 je hořlavý plyn", "lab")
T(92, 596, "Separátor (4) s odvzdušněním patří VENKU hned", "tx")
T(92, 612, "za jednotku — vzduch i případně uniklé chladivo", "tx")
T(92, 628, "musí odejít do volného prostoru, nikdy ne do domu.", "tx")

# ---------------------------------------------------------------- potrubí
FY, RY = 330, 420                         # výstup / vratka u TČ
TX, TY, TW, TH = 640, 320, 130, 240       # AKU 100 l
TIN, TOUT = TY + 45, TY + TH - 45         # horní / spodní hrdla (365 / 515)
TOP = TX + TW / 2

# primár: TČ → AKU (výstup) a AKU → TČ (vratka)
P(f"M250,{FY} L560,{FY} L560,{TIN} L{TX},{TIN}", RED)
P(f"M{TX},{TOUT} L540,{TOUT} L540,{RY} L250,{RY}", BLUE)
# sekundár: AKU → radiátory → AKU
SX, RAD = 1080, 1130
PSX = 930                                 # stoupačka k pojistné skupině a expanzní nádobě (za čerpadlem)
P(f"M{TX + TW},{TIN} L{SX},{TIN} L{SX},{TIN + 100} L{RAD},{TIN + 100}", RED)
P(f"M{SX},{TIN} L{RAD},{TIN}", RED)
P(f"M{PSX},{TIN} L{PSX},{TIN - 92}", RED, 4)
P(f"M{RAD + 160},{TIN + 60} L1335,{TIN + 60} M{RAD + 160},{TIN + 160} L1335,{TIN + 160}", BLUE)
P(f"M1335,{TIN + 60} L1335,600 L850,600 L850,{TOUT} L{TX + TW},{TOUT}", BLUE)

arrow(510, FY, 0, RED); arrow(470, RY, 180, BLUE)
arrow(1060, TIN, 0, RED); arrow(1040, 600, 180, BLUE)

# ---------------------------------------------------------------- prvky
heat_pump(60, 285, h=200)
separator(350, FY)                                   # 4 separátor + velký bezp. odvzdušňovací ventil
valve(285, FY); valve(290, RY)                       # 2 uzávěry
antifreeze(360, RY)                                  # 3 protizámrazový ventil
tank100(TX, TY, TW, TH)
valve(605, TIN); valve(605, TOUT)                    # 2 uzávěry na vstupu / výstupu AKU (primár)
air_vent(TOP, TY)                                    # 6 odvzdušnění AKU
# 7 pojistná skupina (blok s pojistným ventilem a manometrem) na stoupačce za čerpadlem
R(PSX - 9, 290, 18, 30, fill="#F3E4B8", stroke=INK, sw=2.2, rx=3)
add(f'<line x1="{PSX - 9}" y1="305" x2="{PSX - 20}" y2="305" stroke="{INK}" stroke-width="2.4"/>'
    f'<circle cx="{PSX - 32}" cy="305" r="12" fill="#fff" stroke="{INK}" stroke-width="2.2"/>'
    f'<line x1="{PSX - 32}" y1="305" x2="{PSX - 26}" y2="298" stroke="{RED}" stroke-width="2" stroke-linecap="round"/>'
    f'<text x="{PSX - 32}" y="313" class="g" text-anchor="middle">bar</text>')
add(f'<line x1="{PSX + 9}" y1="305" x2="{PSX + 18}" y2="305" stroke="{INK}" stroke-width="2.4"/>'
    f'<path d="M{PSX + 18},297 L{PSX + 32},305 L{PSX + 18},313 Z" fill="#fff" stroke="{INK}" stroke-width="2"/>'
    f'<rect x="{PSX + 32}" y="299" width="9" height="12" rx="2" fill="{RED}"/>'
    f'<line x1="{PSX + 32}" y1="305" x2="{PSX + 32}" y2="334" stroke="{GREY}" stroke-width="2.2" stroke-dasharray="5 4"/>'
    f'<path d="M{PSX + 25},334 h14 l-4,8 h-6 Z" fill="#fff" stroke="{GREY}" stroke-width="1.8"/>')
exp_vessel(PSX, TIN - 120)                           # 9 expanzní nádoba nad pojistnou skupinou
# 8 teploměr + pojistný (přetlakový) ventil s červenou hlavou na společném vývodu z pláště AKU
add(f'<line x1="{TX + TW}" y1="450" x2="{TX + TW + 26}" y2="450" stroke="{INK}" stroke-width="2.6"/>')
gauge(TX + TW + 10, 450, "°C")
add(f'<path d="M{TX + TW + 26},442 L{TX + TW + 40},450 L{TX + TW + 26},458 Z" fill="#fff" stroke="{INK}" stroke-width="2"/>'
    f'<rect x="{TX + TW + 40}" y="444" width="9" height="12" rx="2" fill="{RED}"/>'
    f'<line x1="{TX + TW + 33}" y1="458" x2="{TX + TW + 33}" y2="486" stroke="{GREY}" stroke-width="2.2" stroke-dasharray="5 4"/>'
    f'<path d="M{TX + TW + 26},486 h14 l-4,8 h-6 Z" fill="#fff" stroke="{GREY}" stroke-width="1.8"/>')
drain_cock(TOP, TY + TH)                             # 15 vypouštění
valve(820, TIN); pump(870, TIN); valve(985, TIN)     # 10 sekundární čerpadlo
valve(960, 600)
air_vent(SX, TIN)                                    # 13 odvzdušnění v nejvyšším bodě
radiator(RAD, TIN - 12); radiator(RAD, TIN + 88)
rad_vent(RAD + 150, TIN - 12); rad_vent(RAD + 150, TIN + 88)
thermostat(1295, 190)
receiver(770, 196)

# čidlo AKU → řízení TČ
add(f'<circle cx="{TX + 22}" cy="482" r="9" fill="#fff" stroke="{INK}" stroke-width="2"/>')
T(TX + 22, 486, "T", "rs", "middle")
P(f"M{TX + 13},482 L250,482", YEL, 2.4, dash="7 5")
P(f"M844,226 L870,226 L870,{TIN - 17}", YEL, 3)
waves(862, 182, 1)
waves(1289, 214, -1)
P("M900,186 L1251,210", YEL, 1.6, dash="2 7")
T(1140, 192, "rádiový signál", "tx", "middle")

# ---------------------------------------------------------------- čísla
num(80, 262, 1);  T(101, 267, "REO RH030–RH060", "lab")
num(285, 370, 2); num(290, 458, 2)
num(396, 458, 3)
num(312, 252, 4)
num(TX - 20, TY - 12, 5)
num(605, 400, 2); num(605, 548, 2)
num(TOP + 28, TY - 40, 6)
num(PSX + 48, 290, 7)
num(TX + TW + 64, 432, 8)
num(PSX + 48, TIN - 132, 9)
num(870, 412, 10)
num(756, 180, 11)
num(1340, 270, 12)
num(SX - 26, TIN - 38, 13)
num(1210, 570, 14)
num(TOP + 30, TY + TH + 22, 15)
num(TX - 22, 450, 16)
T(155, 518, "venkovní jednotka", "tx", "middle")

# ---------------------------------------------------------------- spodní část
BY = 690
R(30, BY, 700, 370, fill="#fff", stroke="#DDE3E6", sw=1.5, rx=10)
T(52, BY + 32, "SOUČÁSTI", "hd")
parts = [
    (1, "Tepelné čerpadlo REO RH030–RH060", "venkovní monoblok, chladivo R290"),
    (2, "Uzavírací ventily", "u jednotky (výstup před separátorem, vratka) i u AKU"),
    (3, "Protizámrazový ventil", "venku na vratce — při mrazu a výpadku vypustí vodu"),
    (4, "Separátor + bezpečnostní odvzdušňovací ventil", "venku na výstupu = nejvyšší bod venkovní části"),
    (5, "Akumulační nádrž 100 l (topná voda)", "hydraulicky odděluje okruh TČ a okruh topení"),
    (6, "Automatický odvzdušňovací ventil AKU", "na horním vývodu nádrže"),
    (7, "Pojistná skupina (poj. ventil + manometr)", "na výstupu do topení za čerpadlem, výfuk do odpadu"),
    (8, "Teploměr + pojistný ventil AKU", "společný vývod na plášti, výfuk do odpadu"),
    (9, "Expanzní nádoba (topná)", "nad pojistnou skupinou, bez uzávěru"),
    (10, "Sekundární oběhové čerpadlo", "na výstupu z AKU do topení, s uzávěry"),
    (11, "Přijímač termostatu (relé 230 V)", "u čerpadla — spíná čerpadlo 10"),
    (12, "Bezdrátový pokojový termostat", "v obytné místnosti, 1,5 m nad podlahou"),
    (13, "Odvzdušňovací ventil v nejvyšším bodě", "na stoupačce / nejvyšším místě rozvodu"),
    (14, "Radiátory s odvzdušňovacími ventilky", "stávající otopná soustava"),
    (15, "Vypouštěcí kohout AKU", "na dně nádrže — vypouštění, odkalení"),
    (16, "Čidlo teploty AKU", "do jímky nádrže, kabel k řídicí jednotce TČ"),
]
for i, (n, a, b) in enumerate(parts):
    col, row = (0, i) if i < 8 else (1, i - 8)
    x = 52 + col * 345
    y = BY + 64 + row * 37
    num(x + 12, y, n)
    T(x + 34, y - 2, a, "ts")
    T(x + 34, y + 13, b, "tx")
lx, ly = 668, 616
for k, (c, lab, d) in enumerate([(RED, "výstup — teplá voda", None), (BLUE, "vratka — ochlazená voda", None),
                                  (YEL, "elektrické ovládání / signál", "7 5")]):
    yy = ly + k * 17
    ds = f' stroke-dasharray="{d}"' if d else ''
    add(f'<line x1="{lx}" y1="{yy}" x2="{lx + 34}" y2="{yy}" stroke="{c}" stroke-width="{5 if not d else 3}" stroke-linecap="round"{ds}/>')
    T(lx + 44, yy + 4, lab, "tx")

R(750, BY, 620, 370, fill=GRNL, stroke=None, rx=10)
T(772, BY + 32, "JAK TO FUNGUJE", "hd")
how = [
    "TČ (1) ohřívá topnou vodu v AKU 100 l (5) podle čidla (16) —",
    "samo se zapíná a vypíná, nezávisle na pokojovém termostatu.",
    "Termostat (12) pošle rádiem signál přijímači (11), ten zapne",
    "čerpadlo (10) a voda z AKU jde do radiátorů (14). Po dosažení",
    "teploty v místnosti termostat čerpadlo (10) zase vypne.",
]
for i, s in enumerate(how):
    T(772, BY + 62 + i * 21, s, "ts")
T(772, BY + 186, "BEZPEČNOST A TIPY", "hd")
tips = [
    "• Pojistné ventily (7, 8) bez uzávěru, výfuk viditelně do odpadu.",
    "• Mezi pojistnou skupinou (7) a exp. nádobou (9) žádný uzávěr.",
    "• Uzávěry u čerpadla (10) zavírat jen při servisu — přes ně",
    "\u00a0\u00a0\u00a0chrání pojistná skupina (7) i AKU a okruh TČ.",
    "• Odvzdušnění (4, 6, 13, 14) vždy v nejvyšších bodech potrubí.",
    "• Protizámrazový ventil (3) venku na vratce, výpustí dolů.",
    "• V místnosti s termostatem nechte hlavice radiátorů otevřené.",
    "• Tlak (studená soustava cca 1–1,5 bar) hlídat na manometru (7).",
]
for i, s in enumerate(tips):
    T(772, BY + 212 + i * 21, s, "ts")

T(30, H - 12, "Zjednodušené orientační schéma — dimenze potrubí, nastavení pojistného ventilu a velikost expanzní "
  "nádoby určete podle návodu k TČ a konkrétního domu.", "tx")
T(W - 30, H - 12, "REO HEATING", "zone", "end")
add('</svg>')

dst = os.path.normpath(os.path.join(HERE, "..", "schema-kuncice-aku100.svg"))
open(dst, "w", encoding="utf-8").write("\n".join(o))
print("zapsáno:", dst)
