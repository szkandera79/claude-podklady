#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Schéma zapojení TČ REO HEATING pro kutily — Betonová patka venkovní jednotky (dle ručního nákresu, Kunčice).

Vytváří ../schema-kuncice-patka.svg (a PNG přes Chrome headless, viz README).
Spuštění:  python3 reo-schemata-zapojeni/src/gen_patka_kuncice.py
Styl: zjednodušené piktogramy + číslované popisky (vzor: REO/Fotky a schema).
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.expanduser("~/Claude/REO/logo/logo-reo-heating.svg")

W, H = 1400, 1012
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

CON = "#C9CDCF"                       # beton
S = 0.5                               # měřítko půdorysu: 1 mm = 0.5 px

def dim(x1, y1, x2, y2, text, off=0, vertical=False):
    """Kótovací čára s šipkami a textem uprostřed."""
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="1.4" '
        f'marker-start="url(#ar)" marker-end="url(#ar)"/>')
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    if vertical:
        add(f'<text x="{mx + off}" y="{my}" class="dm" text-anchor="middle" transform="rotate(-90 {mx + off} {my})">{esc(text)}</text>')
    else:
        T(mx, my + off, text, "dm", "middle")

def strip(x, y, w, h):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#hatch)" stroke="{INK}" stroke-width="2.4"/>')

add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
    f'font-family="Avenir Next, Arial, Helvetica, sans-serif">')
add(f'''<style>
 .ts{{fill:{INK};font-size:13px}}
 .tx{{fill:{GREY};font-size:11.5px}}
 .ttl{{fill:{INK};font-size:28px;font-weight:bold}}
 .sub{{fill:{GRN};font-size:18px;font-weight:bold}}
 .zone{{fill:{GREY};font-size:12px;font-weight:bold;letter-spacing:1.6px}}
 .num{{fill:#fff;font-size:14px;font-weight:bold}}
 .lab{{fill:{INK};font-size:13px;font-weight:bold}}
 .hd{{fill:{GRN};font-size:14px;font-weight:bold;letter-spacing:1.4px}}
 .dm{{fill:{INK};font-size:13px;font-weight:bold}}
</style>
<defs>
 <pattern id="hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
  <rect width="10" height="10" fill="{CON}"/><line x1="0" y1="0" x2="0" y2="10" stroke="#8E979B" stroke-width="1.4"/></pattern>
 <marker id="ar" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse">
  <path d="M0,1 L10,5 L0,9 Z" fill="{INK}"/></marker>
</defs>''')
R(0, 0, W, H, fill="#fff", stroke=None)
logo(36, 22, 190)
T(256, 62, "Betonová patka venkovní jednotky", "ttl")
T(256, 92, "Základ ze ztraceného bednění · REO RH030–RH060", "sub")
T(W - 36, 58, "REO-SCH-K1-P", "zone", "end")
T(W - 36, 78, "rev. 4 · 11/2026", "tx", "end")
add(f'<line x1="30" y1="118" x2="{W - 30}" y2="118" stroke="{GRN}" stroke-width="3"/>')

# ---------------------------------------------------------------- půdorys
R(30, 140, 760, 640, fill="#F7F9FA", stroke=None, rx=10)
T(52, 168, "PŮDORYS", "zone")
WY = 214                                    # líc stěny
add(f'<rect x="60" y="{WY - 22}" width="700" height="22" fill="url(#hatch)" stroke="none"/>')
add(f'<line x1="60" y1="{WY}" x2="760" y2="{WY}" stroke="{INK}" stroke-width="3"/>')
T(410, WY - 30, "STĚNA DOMU", "lab", "middle")
CX = 410
SY = WY + 400 * S                           # začátek ramen (odstup min. 400 mm)
SL, SW, AX = 500 * S, 200 * S, 700 * S      # délka ramene, šířka, osová vzdálenost
xl, xr = CX - AX / 2, CX + AX / 2
for xa in (xl, xr):
    add(f'<line x1="{xa}" y1="{WY + 20}" x2="{xa}" y2="{SY + SL + 70}" stroke="{GREY}" stroke-width="1.2" stroke-dasharray="16 5 3 5"/>')
    strip(xa - SW / 2, SY, SW, SL)
# obrys jednotky 1080 × 480 mm
UWp, UDp = 1080 * S, 480 * S
add(f'<rect x="{CX - UWp / 2}" y="{SY + (SL - UDp) / 2}" width="{UWp}" height="{UDp}" fill="none" stroke="{GRN}" '
    f'stroke-width="2.2" stroke-dasharray="9 6" rx="6"/>')
T(CX, SY + SL / 2 + 4, "obrys jednotky", "tx", "middle")
T(CX, SY + SL / 2 + 19, "1080 × 460–480 mm", "tx", "middle")
add(f'<path d="M{CX - 60},{SY - 18} h120" stroke="{BLUE}" stroke-width="2" marker-end="url(#ar)" transform="rotate(-90 {CX} {SY - 18})" opacity="0"/>')
T(CX, SY - 50, "sání vzduchu (zadní strana jednotky)", "tx", "middle")
for xx in (CX - 90, CX, CX + 90):
    add(f'<line x1="{xx}" y1="{SY - 14}" x2="{xx}" y2="{SY - 36}" stroke="{BLUE}" stroke-width="2" marker-end="url(#ar)"/>')
# kóty
dim(724, WY, 724, SY, "min. 400 mm", off=-10, vertical=True)
add(f'<text x="{724 + 16}" y="{(WY + SY) / 2}" class="tx" text-anchor="middle" transform="rotate(-90 {724 + 16} {(WY + SY) / 2})">doporučeno 500 mm</text>')
add(f'<line x1="{xr + SW / 2 + 4}" y1="{SY}" x2="734" y2="{SY}" stroke="{GREY}" stroke-width="1"/>')
dim(118, SY, 118, SY + SL, "min. 500 mm", off=-10, vertical=True)
add(f'<line x1="108" y1="{SY}" x2="{xl - SW / 2 - 4}" y2="{SY}" stroke="{GREY}" stroke-width="1"/>'
    f'<line x1="108" y1="{SY + SL}" x2="{xl - SW / 2 - 4}" y2="{SY + SL}" stroke="{GREY}" stroke-width="1"/>')
dim(xl, SY + SL + 50, xr, SY + SL + 50, "700 mm (osy ramen)", off=-8)
dim(xr - SW / 2, SY + SL + 22, xr + SW / 2, SY + SL + 22, "", off=-6)
T(xr + SW / 2 + 12, SY + SL + 27, "200 mm", "dm")
# popisek ramene
add(f'<line x1="{xr - SW / 2 + 14}" y1="{SY + 14}" x2="{xr - 70}" y2="{WY + 98}" stroke="{INK}" stroke-width="1.4"/>')
T(xr - 150, WY + 52, "rameno základny", "lab")
T(xr - 150, WY + 68, "ze ztraceného bednění", "ts")
T(xr - 150, WY + 84, "výška min. 300 mm", "ts")
num(xl, SY - 22, 1); num(xr, SY - 22, 1)

# ---------------------------------------------------------------- pohled zepředu
R(810, 140, 560, 640, fill="#F7F9FA", stroke=None, rx=10)
T(832, 168, "POHLED ZEPŘEDU", "zone")
E = 0.35
GY = 640                                    # úroveň terénu
EX = 1090
eh, ew, ea = 300 * E, 200 * E, 700 * E
top = GY - eh + 30 * E                      # rameno mírně zapuštěné pod terén
exl, exr = EX - ea / 2, EX + ea / 2
add(f'<rect x="830" y="{GY}" width="520" height="70" fill="#EFE7DA"/>')
add(f'<line x1="830" y1="{GY}" x2="1350" y2="{GY}" stroke="#8C7A5B" stroke-width="2.4"/>')
T(1346, GY + 20, "terén", "tx", "end")
add(f'<rect x="{exl}" y="{GY + 6}" width="{ea}" height="22" fill="#D8D2C4" stroke="none"/>')
T(EX, GY + 22, "štěrk", "tx", "middle")
for xa in (exl, exr):
    strip(xa - ew / 2, top, ew, GY + 30 * E - top)
# jednotka na antivibračních patkách
uw, uh = 1080 * E, 330
ub = top - 20
for xa in (exl, exr):
    add(f'<path d="M{xa - 18},{top} L{xa - 12},{ub} L{xa + 12},{ub} L{xa + 18},{top} Z" fill="#3A4042"/>')
ux = EX - uw / 2
R(ux, ub - uh, uw, uh, fill="#F5F7F8", stroke=INK, sw=2.6, rx=10)
fx, fy = ux + uw * 0.40, ub - uh / 2
for r in (118, 92, 66, 40):
    add(f'<circle cx="{fx}" cy="{fy}" r="{r}" fill="none" stroke="{INK}" stroke-width="{2.4 if r == 118 else 1.3}"/>')
add(f'<circle cx="{fx}" cy="{fy}" r="10" fill="{INK}"/>')
R(ux + uw - 70, ub - uh + 30, 44, 26, fill="#fff", stroke=INK, sw=2, rx=3)
T(EX, ub - uh - 12, "venkovní jednotka REO", "lab", "middle")
dim(1300, top, 1300, GY + 30 * E, "min. 300 mm", off=-10, vertical=True)
add(f'<line x1="{exr + ew / 2 + 4}" y1="{top}" x2="1310" y2="{top}" stroke="{GREY}" stroke-width="1"/>')
dim(exl, GY + 96, exr, GY + 96, "700 mm", off=-8)
T(exl + 40, top - 34, "", "tx")
num(exl, GY + 46, 1); num(exr, GY + 46, 1)
num(exr + 64, ub - 10, 2)

# ---------------------------------------------------------------- poznámky
NY = 800
T(52, NY + 6, "1  Ramena: tvárnice ztraceného bednění vyplněné betonem — šířka 200 mm, délka min. 500 mm, výška min. 300 mm, kolmo ke stěně, osově 700 mm.", "ts")
T(52, NY + 28, "2  Jednotka stojí na antivibračních patkách přišroubovaných do ramen. Odstup ramen od stěny min. 400 mm, doporučujeme 500 mm — volné sání vzduchu.", "ts")
T(52, NY + 50, "   Mezi rameny ponechte štěrkový podsyp — dno jednotky slouží jako vana na kondenzát a odtokové otvory musí zůstat volné.", "ts")
R(30, NY + 70, 1340, 106, fill="#FFF4DA", stroke="#E3A71B", sw=2, rx=8)
add(f'<path d="M54,{NY + 92} L68,{NY + 116} L40,{NY + 116} Z" fill="#E3A71B"/>')
T(54, NY + 113, "!", "num", "middle")
T(84, NY + 96, "Ochranná zóna R290: okna, dveře a světlíky min. 1 m od půdorysu jednotky, nad horní hranou min. 0,5 m (okno nad jednotkou je přípustné).", "lab")
T(84, NY + 116, "Doporučení: na straně výfuku vzduchu min. 3 m k oknům obytných místností, terasám a chodníkům a min. 3 m od sousedního pozemku (hluk, proudění).", "lab")
T(84, NY + 136, "V zóně nesmí být okna, dveře, sklepní světlíky a šachty, vpusti a kanalizace, větrací otvory ani zdroje vznícení (zásuvky, vypínače, svítidla).", "ts")
T(84, NY + 156, "R290 je těžší než vzduch — žádné prohlubně v zóně. Pevnou vzdálenost norma neuvádí; ČSN EN 378 a ČSN EN IEC 60335-2-40 ji svěřují výrobci.", "ts")
T(30, H - 12, "Orientační schéma — rozměry jsou minimální; únosnost a hloubku základu přizpůsobte podloží a hmotnosti jednotky (105–165 kg).", "tx")
T(W - 30, H - 12, "REO HEATING", "zone", "end")
add('</svg>')

dst = os.path.normpath(os.path.join(HERE, "..", "schema-kuncice-patka.svg"))
open(dst, "w", encoding="utf-8").write("\n".join(o))
print("zapsáno:", dst)
