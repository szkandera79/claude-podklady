#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Schéma elektrického zapojení TČ REO RH030–RH060 s hydroboxem (podle návodu hydraulického modulu, kap. 6).

V1: pouze vytápění s AKU  ->  ../schema-hydrobox-elektro.svg
V2: --tuv  s ohřevem TUV  ->  ../schema-hydrobox-elektro-tuv.svg
Spuštění:  python3 reo-schemata-zapojeni/src/gen_elektro_hydrobox.py [--tuv]
"""
import os, re, sys

TUV = "--tuv" in sys.argv                 # varianta 2: s ohřevem TUV (trojcestný ventil, čidlo T2, vložka)
DY = 80 if TUV else 0

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.expanduser("~/Claude/REO/logo/logo-reo-heating.svg")

W, H = 1400, 1310 + DY
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

PWR = "#5B4636"                       # silový kabel 230 / 400 V
COM = "#7A5BB5"                       # komunikační kabel ovladače

def box(x, y, w, h, title, sub=None, fill="#fff"):
    R(x, y, w, h, fill=fill, stroke=INK, sw=2.2, rx=6)
    T(x + w / 2, y + h / 2 + (-2 if sub else 5), title, "rs", "middle")
    if sub:
        T(x + w / 2, y + h / 2 + 13, sub, "tx", "middle")

def breaker(x, y, label, sub):
    """Jistič / chránič: obdélník se spínacím symbolem."""
    R(x, y, 120, 64, fill="#fff", stroke=INK, sw=2.2, rx=5)
    add(f'<path d="M{x + 18},{y + 46} L{x + 18},{y + 36} L{x + 34},{y + 20} M{x + 34},{y + 30} L{x + 34},{y + 46}" '
        f'fill="none" stroke="{INK}" stroke-width="2.2" stroke-linecap="round"/>')
    T(x + 46, y + 28, label, "rs")
    T(x + 46, y + 44, sub, "tx")

def terminal(x, y, lab, active=True):
    R(x, y, 30, 26, fill="#fff" if active else "#ECEFF1", stroke=INK if active else "#A9B2B7", sw=1.8, rx=3)
    T(x + 15, y + 18, lab, "rs" if active else "tx", "middle")

def motor_pump(x, y):
    add(f'<circle cx="{x}" cy="{y}" r="24" fill="#fff" stroke="{INK}" stroke-width="2.4"/>')
    T(x, y + 6, "M", "tb", "middle")
    add(f'<path d="M{x - 12},{y - 30} L{x + 12},{y - 30}" stroke="{INK}" stroke-width="2"/>')

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
 .lcd{{fill:{GRN};font-size:12px;font-weight:bold}}
 .rs{{fill:{INK};font-size:10.5px;font-weight:bold;letter-spacing:.6px}}
 .lab{{fill:{INK};font-size:13px;font-weight:bold}}
 .hd{{fill:{GRN};font-size:14px;font-weight:bold;letter-spacing:1.4px}}
</style>''')
R(0, 0, W, H, fill="#fff", stroke=None)
logo(36, 22, 190)
T(256, 62, "Schéma elektrického zapojení s hydroboxem", "ttl")
T(256, 92, ("Vytápění s AKU 100 l a ohřev TUV" if TUV else "Pouze vytápění s AKU 100 l") + " · jednotky a hydroboxy 1F i 3F", "sub")
T(W - 36, 58, ("REO-SCH-H2-E" if TUV else "REO-SCH-H1-E") + " · RH030–RH060", "zone", "end")
T(W - 36, 78, "rev. 0 · 11/2026", "tx", "end")
add(f'<line x1="30" y1="118" x2="{W - 30}" y2="118" stroke="{GRN}" stroke-width="3"/>')

ZT, ZB = 140, 700 + DY
ZX = 1080
R(30, ZT, 390, ZB - ZT, fill="#F2F6F9", stroke=None, rx=10)
R(ZX, ZT, 1370 - ZX, ZB - ZT, fill="#FBF6EF", stroke=None, rx=10)
for xx in (420, ZX):
    add(f'<line x1="{xx}" y1="{ZT}" x2="{xx}" y2="{ZB}" stroke="{GREY}" stroke-width="2" stroke-dasharray="10 7"/>')
T(48, ZT + 26, "VENKU", "zone")
T(440, ZT + 26, "TECHNICKÁ MÍSTNOST", "zone")
T(ZX + 18, ZT + 26, "OBYTNÉ PROSTORY", "zone")
T(424, ZB - 12, "obvodová zeď", "tx")

# ---------------------------------------------------------------- venkovní jednotka
UX, UY, UW, UH = 56, 196, 336, 400
R(UX, UY, UW, UH, fill="#F5F7F8", stroke=INK, sw=2.6, rx=12)
T(UX + 128, UY + 58, "1F 230 V", "rs")
for i, l in enumerate(("L", "N", "PE")):
    terminal(UX + 18 + i * 36, UY + 40, l)
for i, l in enumerate(("R", "S", "T", "N", "PE")):
    terminal(UX + 18 + i * 36, UY + 82, l, active=False)
T(UX + 200, UY + 100, "3F 400 V", "rs")
R(UX + 190, UY + 22, 128, 50, fill="#fff", stroke=INK, sw=2.2, rx=6)
T(UX + 254, UY + 42, "ŘÍDICÍ DESKA", "rs", "middle")
T(UX + 254, UY + 60, "čidla T2, T3, T8" if TUV else "čidla T3, T8", "tx", "middle")
T(UX + 18, UY + 140, "SVORKOVNICE PŘÍSLUŠENSTVÍ", "rs")
for i, n in enumerate("123456"):
    terminal(UX + 18 + i * 50, UY + 146, n, n in ("234" + ("1" if TUV else "")))
T(UX + 18, UY + UH - 56, "1 vložka TUV · 2 E-ohřev · 3 3c ventil · 4 N · 5–6 spínač", "tx")
T(UX + 18, UY + 240, "ČERPADLO HYDROBOXU", "rs")
R(UX + 18, UY + 250, 48, 26, fill="#fff", stroke=INK, sw=1.8, rx=3); T(UX + 42, UY + 268, "PUMP", "rs", "middle")
for i, l in enumerate(("PWM", "GND", "FB")):
    R(UX + 80 + i * 44, UY + 250, 40, 26, fill="#fff", stroke=INK, sw=1.8, rx=3)
    T(UX + 100 + i * 44, UY + 268, l, "rs", "middle")
T(UX + 18, UY + UH - 34, "VENKOVNÍ JEDNOTKA", "lab")
T(UX + 18, UY + UH - 16, "REO RH030–RH060 · napájení z hydroboxu", "tx")

# ---------------------------------------------------------------- hydrobox
BX, BY0, BW, BH = 480, 210, 280, 380
R(BX, BY0, BW, BH, fill="#EEF1F3", stroke=INK, sw=2.6, rx=8)
T(BX + 16, BY0 + 24, "HYDROBOX", "lab")
T(BX + 98, BY0 + 24, "RH-03H(/S) · RH-05H(/S)", "tx")
breaker(BX + 16, BY0 + 40, "JISTIČ Q", "s chráničem")
R(BX + 150, BY0 + 40, 114, 64, fill="#fff", stroke=INK, sw=2.2, rx=5)
T(BX + 207, BY0 + 60, "STYKAČ", "rs", "middle")
T(BX + 207, BY0 + 76, "→ dohřev 3 kW", "tx", "middle")
add(f'<path d="M{BX + 185},{BY0 + 92} ' + " ".join(f"l6,{-7 if k % 2 == 0 else 7}" for k in range(7)) + f'" fill="none" stroke="{RED}" stroke-width="2.2"/>')
T(BX + 16, BY0 + 128, "NAPÁJENÍ → TČ", "rs")
for i, l in enumerate(("L", "N", "PE")):
    terminal(BX + 16 + i * 36, BY0 + 136, l)
for i, l in enumerate(("R", "S", "T", "N", "PE")):
    terminal(BX + 16 + i * 36, BY0 + 170, l, active=False)
T(BX + 16, BY0 + 222, "ŘÍZENÍ Z JEDNOTKY (230 V)", "rs")
for i, l in enumerate(("1", "2", "3", "4")):
    terminal(BX + 16 + i * 36, BY0 + 230, l)
T(BX + 16, BY0 + 272, "1 ohřev · 2 čerpadlo · 3 ventil · 4 N", "tx")
T(BX + 16, BY0 + 296, "SIGNÁL ČERPADLA 0–12 V", "rs")
for i, l in enumerate(("PWM", "GND", "FB")):
    R(BX + 16 + i * 44, BY0 + 304, 40, 26, fill="#fff", stroke=INK, sw=1.8, rx=3)
    T(BX + 36 + i * 44, BY0 + 322, l, "rs", "middle")
motor_pump(BX + 242, BY0 + 250)
T(BX + 242, BY0 + 292, "čerpadlo", "tx", "middle")
R(BX + 222, BY0 + 315, 40, 30, fill="#fff", stroke=INK, sw=2.2, rx=4); T(BX + 242, BY0 + 335, "M", "tb", "middle")
T(BX + 242, BY0 + 360, "3c ventil", "tx", "middle")
# vnitřní propojení (zjednodušeně)
P(f"M{BX + 76},{BY0 + 72} L{BX + 150},{BY0 + 72}", PWR, 2)
# přívod z domovního rozvaděče
P(f"M{BX + 76},{BY0 - 50} L{BX + 76},{BY0 + 40}", PWR, 4)
add(f'<path d="M{BX + 69},{BY0 - 8} L{BX + 76},{BY0 + 4} L{BX + 83},{BY0 - 8} Z" fill="{PWR}"/>')
T(BX + 88, BY0 - 34, "přívod z domovního rozvaděče", "tx")
T(BX + 88, BY0 - 20, "(jištění dle typu hydroboxu)", "tx")

# ---------------------------------------------------------------- kabely hydrobox ↔ jednotka
# napájení: hydrobox L N PE → jednotka L N PE
P(f"M{BX},{BY0 + 149} L440,{BY0 + 149} L440,180 L{UX + 69},180 L{UX + 69},{UY + 40}", PWR, 4)
T(250, 174, "napájení TČ z hydroboxu · 1F 3 vodiče / 3F 5 vodičů", "tx", "middle")
# řízení 230 V: svorky 1–4 hydroboxu → jednotka 2 (E-ohřev), PUMP, 3, 4
CY = UY + 222
P(f"M{BX},{BY0 + 243} L432,{BY0 + 243} L432,{CY} L{UX + 42},{CY}", PWR, 2.6)
for xx in (UX + 83, UX + 133, UX + 183):
    P(f"M{xx},{CY} L{xx},{UY + 172}", PWR, 2)
P(f"M{UX + 42},{CY} L{UX + 42},{UY + 250}", PWR, 2)
T(UX + 238, CY - 4, "→ 2, 3, 4, PUMP", "tx")
# signál PWM / GND / FB
SY = UY + 300
P(f"M{BX},{BY0 + 317} L426,{BY0 + 317} L426,{SY} L{UX + 100},{SY}", YEL, 2.4, dash="7 5")
for i in range(3):
    P(f"M{UX + 100 + i * 44},{SY} L{UX + 100 + i * 44},{UY + 276}", YEL, 2, dash="4 3")
# komunikace ovladače
CX, CYO = 820, 470
P(f"M{UX + 318},{UY + 56} L{UX + 326},{UY + 56} L{UX + 326},620 L800,620 L800,{CYO + 35} L{CX},{CYO + 35}", COM, 3, dash="9 6")
T(600, 612, "komunikační kabel ovladače", "tx", "middle")
R(CX, CYO, 96, 70, fill="#2B3134", stroke=INK, sw=2.2, rx=8)
R(CX + 12, CYO + 12, 72, 30, fill="#3E8E5E", stroke=None, rx=3)
add(f'<text x="{CX + 48}" y="{CYO + 32}" text-anchor="middle" style="fill:#fff;font-size:12px;font-weight:bold">40 °C</text>')
T(CX + 48, CYO + 88, "kabelový ovladač TČ", "tx", "middle")

# ---------------------------------------------------------------- topení: přijímač → sekundární čerpadlo
PX, PY = 820, 230
R(PX, PY, 110, 70, fill="#fff", stroke=INK, sw=2.4, rx=6)
T(PX + 55, PY + 22, "PŘIJÍMAČ", "rs", "middle")
T(PX + 55, PY + 37, "relé 230 V", "tx", "middle")
T(PX + 55, PY + 58, "L  N  │  COM  NO", "tx", "middle")
add(f'<line x1="{PX + 110}" y1="{PY + 12}" x2="{PX + 124}" y2="{PY - 4}" stroke="{INK}" stroke-width="2.4" stroke-linecap="round"/>')
P(f"M{PX + 30},{PY - 40} L{PX + 30},{PY}", PWR, 3)
add(f'<path d="M{PX + 23},{PY - 12} L{PX + 30},{PY} L{PX + 37},{PY - 12} Z" fill="{PWR}"/>')
T(PX + 40, PY - 26, "230 V z dom. rozvaděče", "tx")
MX, MY = 1000, 400
P(f"M{PX + 55},{PY + 70} L{PX + 55},{MY} L{MX - 24},{MY}", PWR, 3)
motor_pump(MX, MY)
T(MX, MY + 44, "sekundární", "tx", "middle"); T(MX, MY + 58, "čerpadlo", "tx", "middle")
T(PX + 63, PY + 112, "spínaná fáze + N + PE", "tx")
thermostat(1210, 300)
waves(PX + 132, PY + 4, 1)
waves(1204, 324, -1)
P(f"M{PX + 166},{PY + 8} L1166,322", YEL, 1.6, dash="2 7")
T(1243, 372, "na baterie", "tx", "middle")

if TUV:
    P(f"M{UX + 318},{UY + 32} L{UX + 333},{UY + 32} L{UX + 333},{ZB - 60} L600,{ZB - 60}", YEL, 2.4, dash="7 5")
    R(600, ZB - 80, 160, 40, fill="#fff", stroke=INK, sw=2.2, rx=6)
    T(680, ZB - 62, "ČIDLO TUV T2", "rs", "middle"); T(680, ZB - 47, "jímka zásobníku TUV", "tx", "middle")
    P(f"M{UX + 18},{UY + 159} L{UX + 8},{UY + 159} L{UX + 8},{ZB - 30} L800,{ZB - 30}", GREY, 2.4, dash="5 4")
    R(800, ZB - 52, 200, 42, fill="#fff", stroke=GREY, sw=1.8, rx=6)
    T(900, ZB - 34, "STYKAČ → VLOŽKA TUV", "rs", "middle"); T(900, ZB - 19, "svorky 1 + 4 · volitelně", "tx", "middle")
    num(780, ZB - 60, 11); num(1020, ZB - 30, 12)

num(UX + 4, UY - 2, 1); num(UX + 4, UY + 160, 2)
num(BX + BW - 6, BY0 - 2, 3); num(BX + 140, BY0 + 46, 4); num(BX + 270, BY0 + 46, 5)
num(CX + 110, CYO + 14, 6); num(PX + 126, PY + 66, 7); num(MX + 40, MY - 24, 8); num(1290, 290, 9)
num(BX + 176, BY0 + 243, 10)

lx, ly = ZX + 20, ZB - 100
for k, (c, lab, d) in enumerate([(PWR, "silový / ovládací kabel 230 / 400 V", None), (COM, "komunikační kabel ovladače", "9 6"),
                                  (YEL, "signál (PWM, čidla, rádio)", "7 5"), (GREY, "volitelné", "5 4")]):
    yy = ly + k * 18
    ds = f' stroke-dasharray="{d}"' if d else ''
    add(f'<line x1="{lx}" y1="{yy}" x2="{lx + 34}" y2="{yy}" stroke="{c}" stroke-width="{4 if not d else 2.6}" stroke-linecap="round"{ds}/>')
    T(lx + 44, yy + 4, lab, "tx")

# ---------------------------------------------------------------- typy hydroboxu
TY0 = ZB + 22
T(30, TY0 + 14, "TYPY HYDROBOXU PODLE NÁVODU HYDRAULICKÉHO MODULU", "hd")
cols = [30, 200, 370, 520, 790, 1370]
heads = ["Hydrobox", "Napájení", "Jistič Q", "Pro jednotky", "Čerpadlo · vložka · exp. nádoba · pojistný ventil"]
rows = [["RH-03H/S", "230 V · 1F", "40 A", "RH030, RH040 (1F)", "výtlak 9 m · 3 kW / 230 V · 8 l · 3 bar"],
        ["RH-03H", "400 V · 3F", "25 A", "RH040 (3F)", "výtlak 9 m · 3 kW / 230 V · 8 l · 3 bar"],
        ["RH-05H/S", "230 V · 1F", "50 A", "RH050 (1F)", "výtlak 12 m · 3 kW / 230 V · 8 l · 3 bar"],
        ["RH-05H", "400 V · 3F", "32 A", "RH050, RH060 (3F)", "výtlak 12 m · 3 kW / 230 V · 8 l · 3 bar"]]
R(30, TY0 + 26, 1340, 28, fill=GRNL, stroke=None, rx=4)
for j, h in enumerate(heads):
    T(cols[j] + 12, TY0 + 45, h, "rs")
for i, r in enumerate(rows):
    yy = TY0 + 54 + i * 26
    add(f'<line x1="30" y1="{yy + 26}" x2="1370" y2="{yy + 26}" stroke="#DDE3E6" stroke-width="1.2"/>')
    for j, c in enumerate(r):
        T(cols[j] + 12, yy + 18, c, "ts")

BY = ZB + 210
R(30, BY, 700, 370, fill="#fff", stroke="#DDE3E6", sw=1.5, rx=10)
T(52, BY + 32, "SOUČÁSTI", "hd")
parts = [
    (1, "Venkovní jednotka — svorky napájení", "1F: L, N, PE · 3F: R, S, T, N, PE — z hydroboxu"),
    (2, "Svorkovnice jednotky + PUMP, PWM/GND/FB", "ovládání hydroboxu"),
    (3, "Hydrobox", "napájí jednotku, čerpadlo, dohřev, 3c ventil"),
    (4, "Jistič Q s chráničem (v hydroboxu)", "40 / 25 / 50 / 32 A dle typu"),
    (5, "Stykač + elektrický dohřev 3 kW", "spíná výstup E-ohřev jednotky"),
    (6, "Kabelový ovladač TČ", "komunikační kabel k řídicí desce"),
    (7, "Přijímač termostatu (relé 230 V)", "vlastní přívod 230 V"),
    (8, "Sekundární oběhové čerpadlo", "napájení spíná / rozpíná přijímač 7"),
    (9, "Bezdrátový pokojový termostat", "v obytné místnosti"),
    (10, "Svorky řízení 1–4 a signál čerpadla", "1 E-ohřev · 2 čerpadlo · 3 3c ventil · 4 N"),
]
if TUV:
    parts += [(11, "Čidlo teploty TUV (T2)", "do jímky zásobníku, k řídicí desce"),
              (12, "Stykač + topná vložka TUV (volitelně)", "ze svorek 1 + 4 jednotky")]
half = (len(parts) + 1) // 2
for i, (n, a, b) in enumerate(parts):
    col, row = (0, i) if i < half else (1, i - half)
    x = 52 + col * 345
    y = BY + 64 + row * 37
    num(x + 12, y, n)
    T(x + 34, y - 2, a, "ts")
    T(x + 34, y + 13, b, "tx")

R(750, BY, 620, 370, fill=GRNL, stroke=None, rx=10)
T(772, BY + 32, "JAK TO FUNGUJE", "hd")
how = [
    "Přívod ze sítě vede do jističe Q hydroboxu (3); z hydroboxu je napájena",
    "venkovní jednotka (1). Jednotka řídí hydrobox: výstupy E-ohřev, PUMP,",
    "3c ventil a N (230 V) a signál PWM / GND / FB pro otáčky čerpadla.",
    "Topení řídí samostatný okruh 230 V: termostat (9) → přijímač (7) → čerpadlo (8).",
] + (["TUV: deska podle čidla T2 (11) přepne 3c ventil hydroboxu."] if TUV else [])
for i, s_ in enumerate(how):
    T(772, BY + 62 + i * 21, s_, "ts")
T(772, BY + 190, "POŽADAVKY", "hd")
req = [
    "• Elektrické připojení hydroboxu zespodu, kabel s rezervou min. 2 m.",
    "• Přední kryt hydroboxu nesnímat za provozu — elektrické součásti.",
    "• Jednotka i hydrobox uzemněny; napětí ±10 % (návod TČ).",
    "• V zimě nevypínat napájení (ochrana proti zamrznutí).",
    "• Zapojení provádí osoba s odbornou kvalifikací dle ČSN / EN.",
]
for i, s_ in enumerate(req):
    T(772, BY + 216 + i * 21, s_, "ts")

T(30, H - 12, "Zjednodušené orientační schéma — podle návodu TČ RH030–RH060 a návodu hydraulického modulu (kap. 6). Průřezy kabelů dle proudu a délky.", "tx")
T(W - 30, H - 12, "REO HEATING", "zone", "end")
add('</svg>')

dst = os.path.normpath(os.path.join(HERE, "..", "schema-hydrobox-elektro-tuv.svg" if TUV else "schema-hydrobox-elektro.svg"))
open(dst, "w", encoding="utf-8").write("\n".join(o).replace("\\u00a0", " "))
print("zapsáno:", dst)
