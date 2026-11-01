#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Schéma zapojení TČ REO HEATING pro kutily — Kunčice — schéma elektrického zapojení (pouze vytápění s AKU 100 l).

Vytváří ../schema-kuncice-elektro.svg (a PNG přes Chrome headless, viz README).
Spuštění:  python3 reo-schemata-zapojeni/src/gen_schema_kuncice_elektro.py
Styl: zjednodušené piktogramy + číslované popisky (vzor: REO/Fotky a schema).
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.expanduser("~/Claude/REO/logo/logo-reo-heating.svg")

W, H = 1400, 1270
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
T(256, 62, "Schéma elektrického zapojení", "ttl")
T(256, 92, "Pouze vytápění s AKU nádrží 100 l · jednotky 1F i 3F dle návodu", "sub")
T(W - 36, 58, "REO-SCH-K1-E · RH030–RH060", "zone", "end")
T(W - 36, 78, "rev. 1 · 11/2026", "tx", "end")
add(f'<line x1="30" y1="118" x2="{W - 30}" y2="118" stroke="{GRN}" stroke-width="3"/>')

ZT, ZB = 140, 660
R(30, ZT, 390, ZB - ZT, fill="#F2F6F9", stroke=None, rx=10)
R(1040, ZT, 330, ZB - ZT, fill="#FBF6EF", stroke=None, rx=10)
for xx in (420, 1040):
    add(f'<line x1="{xx}" y1="{ZT}" x2="{xx}" y2="{ZB}" stroke="{GREY}" stroke-width="2" stroke-dasharray="10 7"/>')
T(48, ZT + 26, "VENKU", "zone")
T(440, ZT + 26, "TECHNICKÁ MÍSTNOST (SKLEP)", "zone")
T(1060, ZT + 26, "OBYTNÉ PROSTORY", "zone")
T(424, ZB - 12, "obvodová zeď", "tx")

# ---------------------------------------------------------------- venkovní jednotka
UX, UY, UW, UH = 56, 196, 336, 340
R(UX, UY, UW, UH, fill="#F5F7F8", stroke=INK, sw=2.6, rx=12)
# napájecí svorky (vlevo nahoře, kabel přichází shora)
T(UX + 128, UY + 58, "1F 230 V", "rs")
for i, l in enumerate(("L", "N", "PE")):
    terminal(UX + 18 + i * 36, UY + 40, l)
for i, l in enumerate(("R", "S", "T", "N", "PE")):
    terminal(UX + 18 + i * 36, UY + 82, l, active=False)
T(UX + 200, UY + 100, "3F 400 V", "rs")
T(UX + 18, UY + 124, "napájení podle modelu — viz tabulka níže", "tx")
# řídicí deska (vpravo nahoře)
R(UX + 190, UY + 22, 128, 64, fill="#fff", stroke=INK, sw=2.2, rx=6)
T(UX + 254, UY + 42, "ŘÍDICÍ DESKA", "rs", "middle")
T(UX + 254, UY + 58, "vestavěné čerpadlo,", "tx", "middle")
T(UX + 254, UY + 73, "čidla vody T3, T8", "tx", "middle")
# svorkovnice příslušenství 1–6
T(UX + 18, UY + 140, "SVORKOVNICE PŘÍSLUŠENSTVÍ (všechny modely)", "rs")
names = [("1", "TUV", False), ("2", "E-ohřev", False), ("3", "3c. ventil", False),
         ("4", "N", True), ("5", "spínač", True), ("6", "COM", True)]
for i, (n, nm, act) in enumerate(names):
    x = UX + 18 + i * 50
    terminal(x, UY + 146, n, act)
    T(x + 15, UY + 188, nm, "tx", "middle")
T(UX + 18, UY + 210, "1–3 využije schéma 2 (TUV), nyní volné", "tx")
# volitelný externí spínač na 5–6
P(f"M{UX + 233},{UY + 196} L{UX + 233},{UY + 232} M{UX + 283},{UY + 196} L{UX + 283},{UY + 232}", GREY, 2, dash="5 4")
R(UX + 200, UY + 232, 116, 46, fill="#fff", stroke=GREY, sw=1.8, rx=5)
add(f'<path d="M{UX + 214},{UY + 266} L{UX + 230},{UY + 252} M{UX + 236},{UY + 266} h12" stroke="{GREY}" stroke-width="2" fill="none"/>')
T(UX + 284, UY + 252, "ext. spínač", "tx", "middle")
T(UX + 284, UY + 268, "volitelně", "tx", "middle")
T(UX + 18, UY + UH - 34, "VENKOVNÍ JEDNOTKA", "lab")
T(UX + 18, UY + UH - 16, "REO RH030–RH060", "tx")

# ---------------------------------------------------------------- rozvaděč TČ
RX, RY_, RW, RH = 470, 230, 250, 320
R(RX, RY_, RW, RH, fill="#FFFDF6", stroke=INK, sw=2.6, rx=8)
T(RX + 16, RY_ + 26, "ROZVADĚČ TČ", "lab")
T(RX + 16, RY_ + 42, "(na fotkách „R.AC TČ“)", "tx")
def brk(x, y, label, sub, w=110):
    R(x, y, w, 64, fill="#fff", stroke=INK, sw=2.2, rx=5)
    add(f'<path d="M{x + 16},{y + 46} L{x + 16},{y + 36} L{x + 30},{y + 20} M{x + 30},{y + 30} L{x + 30},{y + 46}" '
        f'fill="none" stroke="{INK}" stroke-width="2.2" stroke-linecap="round"/>')
    T(x + 42, y + 28, label, "rs")
    T(x + 42, y + 44, sub, "tx")
brk(RX + 70, RY_ + 54, "CHRÁNIČ", "2P / 4P", w=120)
brk(RX + 12, RY_ + 170, "JISTIČ TČ", "1P / 3P")
T(RX + 80, RY_ + 256, "3F: + ochrana proti", "tx")
T(RX + 80, RY_ + 270, "výpadku fáze", "tx")
brk(RX + 128, RY_ + 170, "JISTIČ", "čerpadlo")
P(f"M{RX + 130},{RY_ + 118} L{RX + 130},{RY_ + 142} M{RX + 67},{RY_ + 142} L{RX + 183},{RY_ + 142} "
  f"M{RX + 67},{RY_ + 142} L{RX + 67},{RY_ + 170} M{RX + 183},{RY_ + 142} L{RX + 183},{RY_ + 170}", PWR, 3)
# přívod z domovního rozvaděče shora
P(f"M{RX + 130},{RY_ - 40} L{RX + 130},{RY_ + 54}", PWR, 4)
add(f'<path d="M{RX + 123},{RY_ - 4} L{RX + 130},{RY_ + 8} L{RX + 137},{RY_ - 4} Z" fill="{PWR}"/>')
T(RX + 142, RY_ - 22, "přívod z hlavního", "tx")
T(RX + 142, RY_ - 8, "domovního rozvaděče", "tx")

# ---------------------------------------------------------------- kabely
# napájení TČ: jistič TČ → přes zeď → shora na svorky L N PE
P(f"M{RX + 67},{RY_ + 234} L{RX + 67},{RY_ + 270} L440,{RY_ + 270} L440,182 L{UX + 69},182 L{UX + 69},{UY + 40}", PWR, 4)
T(250, 176, "napájecí kabel TČ v chráničce · 1F 3 vodiče / 3F 5 vodičů", "tx", "middle")
# jistič čerpadla → přijímač
PX, PY = 800, 220
R(PX, PY, 110, 70, fill="#fff", stroke=INK, sw=2.4, rx=6)
T(PX + 55, PY + 22, "PŘIJÍMAČ", "rs", "middle")
T(PX + 55, PY + 37, "relé 230 V", "tx", "middle")
T(PX + 55, PY + 58, "L  N  │  COM  NO", "tx", "middle")
add(f'<line x1="{PX + 110}" y1="{PY + 12}" x2="{PX + 124}" y2="{PY - 4}" stroke="{INK}" stroke-width="2.4" stroke-linecap="round"/>')
P(f"M{RX + 238},{RY_ + 202} L770,{RY_ + 202} L770,{PY + 35} L{PX},{PY + 35}", PWR, 3)
# přijímač (kontakt NO) → sekundární čerpadlo
MX, MY = 975, 410
P(f"M{PX + 55},{PY + 70} L{PX + 55},{MY} L{MX - 24},{MY}", PWR, 3)
motor_pump(MX, MY)
T(MX, MY + 44, "sekundární", "tx", "middle")
T(MX, MY + 58, "čerpadlo", "tx", "middle")
T(PX + 63, PY + 110, "spínaná fáze", "tx")
T(PX + 63, PY + 125, "+ N + PE", "tx")
# komunikační kabel: řídicí deska → kabelový ovladač (spodem)
CX, CY = 820, 500
P(f"M{UX + 318},{UY + 54} L{UX + UW - 10},{UY + 54} L{UX + UW - 10},620 L{CX + 48},620 L{CX + 48},{CY + 70}", COM, 3, dash="9 6")
T(620, 612, "komunikační kabel ovladače", "tx", "middle")
R(CX, CY, 96, 70, fill="#2B3134", stroke=INK, sw=2.2, rx=8)
R(CX + 12, CY + 12, 72, 30, fill="#3E8E5E", stroke=None, rx=3)
add(f'<text x="{CX + 48}" y="{CY + 32}" text-anchor="middle" style="fill:#fff;font-size:12px;font-weight:bold">40 °C</text>')
T(CX + 48, CY + 60, "", "tx", "middle")
T(CX + 108, CY + 40, "kabelový", "tx")
T(CX + 108, CY + 55, "ovladač TČ", "tx")
# termostat
thermostat(1210, 300)
waves(PX + 132, PY + 4, 1)
waves(1204, 324, -1)
P(f"M{PX + 166},{PY + 8} L1166,322", YEL, 1.6, dash="2 7")
T(1090, 250, "rádiový signál", "tx", "middle")
T(1243, 372, "na baterie", "tx", "middle")

# ---------------------------------------------------------------- čísla
num(UX + 4, UY - 2, 1)
num(UX + 4, UY + 160, 2)
num(RX + RW - 4, RY_ + 70, 3)
num(RX + 196, RY_ + 54, 4)
num(RX + 8, RY_ + 166, 5)
num(RX + 242, RY_ + 166, 6)
num(CX + 108, CY + 14, 7)
num(PX + 126, PY + 66, 8)
num(MX + 40, MY - 24, 9)
num(1290, 290, 10)
num(UX + 186, UY + 256, 11)

# legenda
lx, ly = 1060, 560
for k, (c, lab, d) in enumerate([(PWR, "silový kabel 230 / 400 V", None), (COM, "komunikační kabel ovladače", "9 6"),
                                  (YEL, "rádiový signál termostatu", "2 7"), (GREY, "volitelné", "5 4")]):
    yy = ly + k * 18
    ds = f' stroke-dasharray="{d}"' if d else ''
    add(f'<line x1="{lx}" y1="{yy}" x2="{lx + 34}" y2="{yy}" stroke="{c}" stroke-width="{4 if not d else 2.6}" stroke-linecap="round"{ds}/>')
    T(lx + 44, yy + 4, lab, "tx")

# ---------------------------------------------------------------- varianty napájení dle návodu
TY0 = 682
T(30, TY0 + 14, "VARIANTY NAPÁJENÍ PODLE NÁVODU RH030–RH060 (str. 17–19)", "hd")
cols = [30, 390, 545, 690, 820, 1100, 1370]
heads = ["Model (schéma výrobce)", "Napájení", "Svorky jednotky", "Proudový chránič", "Jistič TČ", "Napájecí kabel"]
rows = [["RH030, RH040 (803004-2772), RH050-1F (803004-2787)", "230 V · 1F · 50 Hz", "L · N · PE", "2pólový", "1pólový, 1,5× provozní proud (štítek)", "3 vodiče L, N, PE"],
        ["RH050-3F, RH060 (803004-3000)", "400 V · 3F · 50 Hz", "R · S · T · N · PE", "4pólový", "3pólový + ochrana proti výpadku fáze", "5 vodičů L1–L3, N, PE"]]
R(30, TY0 + 26, 1340, 30, fill=GRNL, stroke=None, rx=4)
for j, h in enumerate(heads):
    T(cols[j] + 12, TY0 + 46, h, "rs")
for i, r in enumerate(rows):
    yy = TY0 + 56 + i * 34
    add(f'<line x1="30" y1="{yy + 34}" x2="1370" y2="{yy + 34}" stroke="#DDE3E6" stroke-width="1.2"/>')
    for j, c in enumerate(r):
        T(cols[j] + 12, yy + 22, c, "ts")
T(30, TY0 + 146, "Svorky příslušenství 1–6 jsou u všech modelů stejné: výstupy 1 (vložka TUV), 2 (elektrokotel), 3 (trojcestný ventil) spínají 230 V proti N na svorce 4; 5–6 = vstup externího spínače. "
  "Napětí ±10 %, při startu min. 90 % jmenovitého.", "tx")

# ---------------------------------------------------------------- spodní část
BY = 870
R(30, BY, 700, 370, fill="#fff", stroke="#DDE3E6", sw=1.5, rx=10)
T(52, BY + 32, "SOUČÁSTI", "hd")
parts = [
    (1, "Venkovní jednotka — svorky napájení", "1F: L, N, PE 230 V · 3F: R, S, T, N, PE 400 V"),
    (2, "Svorkovnice příslušenství 1–6", "1 vložka TUV · 2 elektrokotel · 3 trojc. ventil"),
    (3, "Rozvaděč TČ", "samostatný přívod pro tepelné čerpadlo"),
    (4, "Proudový chránič", "povinný u hlavního vypínače jednotky"),
    (5, "Jistič TČ", "1,5× provozní proud dle štítku; 3F i hlídání fází"),
    (6, "Jistič 230 V pro čerpadlo a přijímač", "samostatný okruh sekundáru"),
    (7, "Kabelový ovladač TČ", "na zdi v technické místnosti"),
    (8, "Přijímač termostatu (relé)", "napájení 230 V, kontakt spíná čerpadlo 9"),
    (9, "Sekundární oběhové čerpadlo", "napájení spíná / rozpíná přijímač 8"),
    (10, "Bezdrátový pokojový termostat", "v hydraulickém schématu č. 12"),
    (11, "Externí spínač zap / vyp (volitelně)", "na svorky 5 a 6 (COM) jednotky"),
]
for i, (n, a, b) in enumerate(parts):
    col, row = (0, i) if i < 6 else (1, i - 6)
    x = 52 + col * 345
    y = BY + 64 + row * 37
    num(x + 12, y, n)
    T(x + 34, y - 2, a, "ts")
    T(x + 34, y + 13, b, "tx")

R(750, BY, 620, 370, fill=GRNL, stroke=None, rx=10)
T(772, BY + 32, "JAK TO FUNGUJE", "hd")
how = [
    "Tepelné čerpadlo (1) se řídí samo: vestavěným čerpadlem a čidlem",
    "vratné vody ohřívá AKU. Ovladač (7) slouží k nastavení a hlášení.",
    "Topení řídí samostatný okruh 230 V: termostat (10) → přijímač (8)",
    "→ sekundární čerpadlo (9). Oba okruhy jsou na sobě nezávislé.",
]
for i, s in enumerate(how):
    T(772, BY + 62 + i * 21, s, "ts")
T(772, BY + 164, "POŽADAVKY Z NÁVODU", "hd")
req = [
    "• Samostatný přívod, napětí v toleranci ±10 %, jednotka uzemněna",
    "\\u00a0\\u00a0\\u00a0— ochranný vodič nesmí být připojen na N.",
    "• Jistič (ne nožový vypínač) na 1,5× provozní proud dle štítku.",
    "• Hlavní vypínač s proudovým chráničem, min. 1,4 m nad podlahou.",
    "• V zimě nevypínat napájení (ochrana proti zamrznutí); před",
    "\\u00a0\\u00a0\\u00a0sezónou nechat jednotku min. 12 h pod napětím.",
    "• Zapojení provádí osoba s odbornou kvalifikací dle ČSN / EN.",
]
for i, s in enumerate(req):
    T(772, BY + 190 + i * 21, s, "ts")

T(30, H - 12, "Zjednodušené orientační schéma — průřezy kabelů a hodnoty jističů určete podle typového štítku jednotky, "
  "návodu a platných norem.", "tx")
T(W - 30, H - 12, "REO HEATING", "zone", "end")
add('</svg>')

dst = os.path.normpath(os.path.join(HERE, "..", "schema-kuncice-elektro.svg"))
open(dst, "w", encoding="utf-8").write("\n".join(o).replace("\\u00a0", " "))
print("zapsáno:", dst)
