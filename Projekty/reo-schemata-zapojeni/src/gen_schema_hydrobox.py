#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Schéma hydraulického zapojení TČ REO RH030–RH060 s hydroboxem (hydraulickým modulem).

V1: pouze vytápění s AKU 100 l  ->  ../schema-hydrobox-aku.svg
V2: --tuv  vytápění s AKU 100 l + TUV  ->  ../schema-hydrobox-tuv.svg
Spuštění:  python3 reo-schemata-zapojeni/src/gen_schema_hydrobox.py [--tuv]
Podklad: návod k instalaci hydraulického modulu REO HEATING (RH-03H/S, RH-03H, RH-05H/S, RH-05H).
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.expanduser("~/Claude/REO/logo/logo-reo-heating.svg")

TUV = "--tuv" in sys.argv
W, H = 1400, (1350 if TUV else 1090)
RED, BLUE = "#D9342B", "#2468B3"      # výstup (topná) / vratka
YEL = "#E3A71B"                       # elektrické ovládání, signál
TV, SV = "#E07B39", "#3BA3C9"         # teplá / studená pitná voda
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

def mag_filter(x, y):
    """Magnetický filtr: těleso pod potrubím s magnetem a vypouštěním."""
    add(f'<g transform="translate({x},{y})">'
        f'<rect x="-13" y="-10" width="26" height="40" rx="6" fill="#fff" stroke="{INK}" stroke-width="2.2"/>'
        f'<path d="M-6,0 v12 a6,6 0 0 0 12,0 v-12" fill="none" stroke="{INK}" stroke-width="3"/>'
        f'<line x1="-6" y1="0" x2="-6" y2="5" stroke="{RED}" stroke-width="3"/>'
        f'<line x1="6" y1="0" x2="6" y2="5" stroke="{BLUE}" stroke-width="3"/>'
        f'<line x1="0" y1="30" x2="0" y2="38" stroke="{INK}" stroke-width="2.4"/>'
        f'<line x1="-6" y1="38" x2="6" y2="38" stroke="{INK}" stroke-width="2.6" stroke-linecap="round"/></g>')

def y_strainer(x, y):
    """Sítkový filtr (Y): šikmá komora se sítkem pod potrubím."""
    add(f'<g transform="translate({x},{y})">'
        f'<rect x="-14" y="-9" width="28" height="18" rx="4" fill="#fff" stroke="{INK}" stroke-width="2.2"/>'
        f'<path d="M-4,7 L12,30" stroke="{INK}" stroke-width="14" stroke-linecap="round"/>'
        f'<path d="M-4,7 L12,30" stroke="#fff" stroke-width="9" stroke-linecap="round"/>'
        f'<path d="M-2,10 L10,27" stroke="{GREY}" stroke-width="1.6" stroke-dasharray="2 2"/></g>')

def mix_valve(x, y, c=INK):
    """Trojcestný směšovací ventil s ruční / motorovou hlavicí (vstup zdola = obtok z vratky)."""
    add(f'<g transform="translate({x},{y})">'
        f'<path d="M-14,-9 L0,0 L-14,9 Z M14,-9 L0,0 L14,9 Z M-9,14 L0,0 L9,14 Z" fill="#fff" stroke="{c}" stroke-width="2.2" stroke-linejoin="round"/>'
        f'<line x1="0" y1="0" x2="0" y2="-14" stroke="{c}" stroke-width="2.2"/>'
        f'<circle cx="0" cy="-20" r="7" fill="#fff" stroke="{c}" stroke-width="2.2"/>'
        f'<path d="M-3,-20 h6" stroke="{c}" stroke-width="2"/></g>')

def three_way(x, y):
    """Trojcestný přepínací ventil s pohonem: vstup zleva, A doprava, B dolů."""
    add(f'<g transform="translate({x},{y})">'
        f'<path d="M-14,-9 L0,0 L-14,9 Z M14,-9 L0,0 L14,9 Z M-9,14 L0,0 L9,14 Z" fill="#fff" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>'
        f'<line x1="0" y1="0" x2="0" y2="-14" stroke="{INK}" stroke-width="2.2"/>'
        f'<rect x="-11" y="-34" width="22" height="20" rx="3" fill="#fff" stroke="{INK}" stroke-width="2.2"/>'
        f'<text x="0" y="-19" class="rs" text-anchor="middle">M</text></g>')

def check_valve(x, y, c=INK):
    """Zpětný ventil: trojúhelník ve směru proudění (doleva) + příčka."""
    add(f'<g transform="translate({x},{y})">'
        f'<path d="M8,-9 L-6,0 L8,9 Z" fill="#fff" stroke="{c}" stroke-width="2.2" stroke-linejoin="round"/>'
        f'<line x1="-8" y1="-10" x2="-8" y2="10" stroke="{c}" stroke-width="2.6"/></g>')

def tank_tuv(x, y, w, h):
    add(f'<defs><linearGradient id="tv" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="#F9C8A8"/><stop offset="0.55" stop-color="#F4ECE6"/>'
        f'<stop offset="1" stop-color="#BFE0EE"/></linearGradient></defs>')
    R(x, y, w, h, fill="url(#tv)", stroke=INK, sw=2.6, rx=40)
    T(x + w / 2 + 6, y + 58, "TUV", "tank", "middle")
    T(x + w / 2 + 6, y + 78, "zásobník", "ts", "middle")
    T(x + w / 2 + 6, y + 94, "se spirálou", "ts", "middle")
    # Mg anoda
    add(f'<line x1="{x + w - 16}" y1="{y + 24}" x2="{x + w - 16}" y2="{y + 130}" stroke="{GREY}" stroke-width="5" stroke-linecap="round"/>')

def tank100(x, y, w, h):
    add(f'<defs><linearGradient id="ak" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="#F7B9A6"/><stop offset="0.5" stop-color="#F3E3E6"/>'
        f'<stop offset="1" stop-color="#B9D1EE"/></linearGradient></defs>')
    R(x, y, w, h, fill="url(#ak)", stroke=INK, sw=2.6, rx=34)
    T(x + w / 2, y + h / 2 - 4, "AKU", "tank", "middle")
    T(x + w / 2, y + h / 2 + 18, "100 l", "tb", "middle")
    T(x + w / 2, y + h / 2 + 36, "topná voda", "tx", "middle")

def heater(x, y):
    """Elektrický průtokový dohřev: obdélník se spirálou na potrubí."""
    R(x - 16, y - 11, 32, 22, fill="#fff", stroke=INK, sw=2.2, rx=3)
    add(f'<path d="M{x - 11},{y + 4} ' + " ".join(f"l4,{-8 if k % 2 == 0 else 8}" for k in range(5)) + f'" fill="none" stroke="{RED}" stroke-width="2"/>')

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

logo(36, 22, 190)
T(256, 62, "Schéma hydraulického zapojení s hydroboxem", "ttl")
T(256, 92, "Vytápění s AKU nádrží 100 l a ohřev TUV" if TUV else "Pouze vytápění s AKU nádrží 100 l", "sub")
T(W - 36, 58, ("REO-SCH-H2" if TUV else "REO-SCH-H1") + " · RH030–RH060", "zone", "end")
T(W - 36, 78, "rev. 0 · 11/2026", "tx", "end")
add(f'<line x1="30" y1="118" x2="{W - 30}" y2="118" stroke="{GRN}" stroke-width="3"/>')

ZT, ZB = 140, (920 if TUV else 660)
ZX = 1140                                            # hranice obytných prostor
R(30, ZT, 390, ZB - ZT, fill="#F2F6F9", stroke=None, rx=10)
R(ZX, ZT, 1370 - ZX, ZB - ZT, fill="#FBF6EF", stroke=None, rx=10)
for xx in (420, ZX):
    add(f'<line x1="{xx}" y1="{ZT}" x2="{xx}" y2="{ZB}" stroke="{GREY}" stroke-width="2" stroke-dasharray="10 7"/>')
T(48, ZT + 26, "VENKU", "zone")
T(440, ZT + 26, "TECHNICKÁ MÍSTNOST", "zone")
T(ZX + 18, ZT + 26, "OBYTNÉ PROSTORY", "zone")
T(424, ZB - 12, "obvodová zeď", "tx")
WY0 = 800 if TUV else 552
R(46, WY0, 358, 92, fill="#FFF4DA", stroke="#E3A71B", sw=2, rx=8)
add(f'<path d="M66,{WY0 + 20} L80,{WY0 + 44} L52,{WY0 + 44} Z" fill="#E3A71B"/>')
T(66, WY0 + 41, "!", "num", "middle")
T(92, WY0 + 25, "R290 je hořlavý plyn", "lab")
T(92, WY0 + 44, "Separátor (4) s odvzdušněním patří VENKU hned", "tx")
T(92, WY0 + 60, "za jednotku — vzduch i případně uniklé chladivo", "tx")
T(92, WY0 + 76, "musí odejít do volného prostoru, nikdy ne do domu.", "tx")

# ---------------------------------------------------------------- potrubí
FY, RY = 330, 420                         # výstup / vratka u TČ
HX, HY, HW, HH = 450, 250, 130, 320       # hydrobox
TX, TY, TW, TH = 760, 320, 130, 240       # AKU 100 l
TIN, TOUT = TY + 45, TY + TH - 45         # 365 / 515
TOP = TX + TW / 2
BY_ = 390                                 # výstup B hydroboxu (TUV)

# TČ → hydrobox (výstup) a hydrobox → TČ (vratka)
P(f"M250,{FY} L{HX},{FY}", RED)
P(f"M{HX},{RY} L250,{RY}", BLUE)
# hydrobox
R(HX, HY, HW, HH, fill="#EEF1F3", stroke=INK, sw=2.6, rx=8)
T(HX + HW / 2, HY - 26, "HYDROBOX", "lab", "middle")
T(HX + HW / 2, HY - 10, "RH-03H(/S) · RH-05H(/S)", "tx", "middle")
P(f"M{HX},{FY} L{HX + HW},{FY}", RED, 4)                              # vnitřní výstup → A
P(f"M{HX + HW},{TOUT} L{HX + 20},{TOUT} L{HX + 20},{RY} L{HX},{RY}", BLUE, 4)   # vnitřní vratka
P(f"M{HX + 105},{FY + 14} L{HX + 105},{BY_} L{HX + HW},{BY_}", RED, 4)          # výstup B
heater(HX + 30, FY)
air_vent(HX + 66, FY)
three_way(HX + 105, FY)
pump(HX + 62, TOUT, ang=180)
P(f"M{HX + 100},{TOUT} L{HX + 100},{TOUT - 22}", BLUE, 3)
exp_vessel(HX + 100, TOUT - 48)
T(HX + HW / 2, HY + HH - 26, "+ filtr, pojistný", "tx", "middle")
T(HX + HW / 2, HY + HH - 12, "ventil 3 bar, jistič", "tx", "middle")
T(HX + HW - 6, FY - 8, "A", "rs", "end"); T(HX + HW - 6, BY_ - 8, "B", "rs", "end")

# hydrobox (A) → AKU
P(f"M{HX + HW},{FY} L720,{FY} L720,{TIN} L{TX},{TIN}", RED)
# AKU → magnetický filtr → hydrobox (vratka)
P(f"M{TX},{TOUT} L{HX + HW},{TOUT}", BLUE)
if TUV:
    valve(745, TOUT); valve(700, TOUT); mag_filter(668, TOUT); valve(636, TOUT)
    add(f'<circle cx="722" cy="{TOUT}" r="5" fill="{BLUE}"/>')
else:
    valve(712, TOUT); mag_filter(668, TOUT); valve(624, TOUT)
    # výstup B nevyužit — zaslepit
    add(f'<line x1="{HX + HW + 10}" y1="{BY_ - 10}" x2="{HX + HW + 10}" y2="{BY_ + 10}" stroke="{INK}" stroke-width="4"/>')
    P(f"M{HX + HW},{BY_} L{HX + HW + 10},{BY_}", RED, 4)
    T(HX + HW + 18, BY_ + 4, "B zaslepit (TUV nevyužito)", "tx")
valve(742, TIN)

# sekundár: AKU → radiátory → AKU (jako schéma 1, posunuto)
SX, RAD, RW = 1158, 1172, 130
PSX = 1072
P(f"M{TX + TW},{TIN} L{SX},{TIN} L{SX},{TIN + 100} L{RAD},{TIN + 100}", RED)
P(f"M{SX},{TIN} L{RAD},{TIN}", RED)
P(f"M{PSX},{TIN} L{PSX},{TIN - 92}", RED, 4)
P(f"M{RAD + RW},{TIN + 60} L1335,{TIN + 60} M{RAD + RW},{TIN + 160} L1335,{TIN + 160}", BLUE)
P(f"M1335,{TIN + 60} L1335,600 L970,600 L970,{TOUT} L{TX + TW},{TOUT}", BLUE)
arrow(520, FY - 0, 0, RED); arrow(400, RY, 180, BLUE)
arrow(1110, 600, 180, BLUE)

heat_pump(60, 285, h=200)
separator(350, FY); valve(285, FY); valve(290, RY); antifreeze(360, RY)
tank100(TX, TY, TW, TH)
air_vent(TOP, TY)
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
exp_vessel(PSX, TIN - 120)
add(f'<line x1="{TX + TW}" y1="450" x2="{TX + TW + 26}" y2="450" stroke="{INK}" stroke-width="2.6"/>')
gauge(TX + TW + 10, 450, "°C")
add(f'<path d="M{TX + TW + 26},442 L{TX + TW + 40},450 L{TX + TW + 26},458 Z" fill="#fff" stroke="{INK}" stroke-width="2"/>'
    f'<rect x="{TX + TW + 40}" y="444" width="9" height="12" rx="2" fill="{RED}"/>'
    f'<line x1="{TX + TW + 33}" y1="458" x2="{TX + TW + 33}" y2="486" stroke="{GREY}" stroke-width="2.2" stroke-dasharray="5 4"/>'
    f'<path d="M{TX + TW + 26},486 h14 l-4,8 h-6 Z" fill="#fff" stroke="{GREY}" stroke-width="1.8"/>')
drain_cock(TOP, TY + TH)
P(f"M950,{TIN + 14} L950,560 L970,560", BLUE, 4, dash="8 6")
mix_valve(950, TIN)
valve(982, TIN); pump(1022, TIN); valve(1120, TIN)
valve(1080, 600)
air_vent(SX, TIN)
radiator(RAD, TIN - 12, w=RW); radiator(RAD, TIN + 88, w=RW)
rad_vent(RAD + RW - 10, TIN - 12); rad_vent(RAD + RW - 10, TIN + 88)
thermostat(1295, 190)
receiver(890, 196)
P(f"M964,226 L1022,226 L1022,{TIN - 17}", YEL, 3)
waves(982, 182, 1)
waves(1289, 214, -1)
P("M1020,186 L1251,210", YEL, 1.6, dash="2 7")
T(1190, 190, "rádiový signál", "tx", "middle")
T(1014, 288, "napájení čerpadla 230 V", "tx", "end")
T(1014, 302, "spíná / rozpíná přijímač", "tx", "end")

if TUV:
    VX, VY, VW, VH = 740, 640, 130, 250
    SIN, SOUT = 700, 830
    P(f"M{HX + HW},{BY_} L600,{BY_} L600,{TOUT - 10} A10,10 0 0 0 600,{TOUT + 10} L600,{SIN} L{VX},{SIN}", RED)
    P(f"M{VX},{SOUT} L722,{SOUT} L722,{SIN + 10} A10,10 0 0 1 722,{SIN - 10} L722,{TOUT}", BLUE)
    tank_tuv(VX, VY, VW, VH)
    add(f'<path d="M{VX},{SIN} ' + " ".join(f"L{VX + (28 if k % 2 == 0 else 6)},{SIN + 10 + k * 12}" for k in range(10)) + f' L{VX},{SOUT}" fill="none" stroke="{RED}" stroke-width="3" stroke-linejoin="round"/>')
    valve(670, SIN); valve(722, 785, vert=True)
    arrow(640, SIN, 0, RED)
    add(f'<circle cx="{VX + 60}" cy="760" r="9" fill="#fff" stroke="{INK}" stroke-width="2"/>')
    T(VX + 60, 764, "T", "rs", "middle")
    P(f"M{VX + 51},760 L250,760 L250,470", YEL, 2.4, dash="7 5")
    add(f'<path d="M{VX + 70},{VY + VH - 40} ' + " ".join(f"l8,{-8 if k % 2 == 0 else 8}" for k in range(6)) + f'" fill="none" stroke="{RED}" stroke-width="2.6"/>')
    add(f'<line x1="{VX + VW}" y1="{VY + VH - 44}" x2="{VX + 118}" y2="{VY + VH - 44}" stroke="{INK}" stroke-width="2.4"/>')
    HW_, CW = 670, 860
    P(f"M{VX + VW},{HW_} L1300,{HW_}", TV, 5)
    add(f'<path d="M1300,{HW_ - 8} L1316,{HW_} L1300,{HW_ + 8} Z" fill="{TV}"/>')
    T(1300, HW_ - 16, "teplá voda do domu", "lab", "end")
    P(f"M1316,{CW} L{VX + VW},{CW}", SV, 5)
    T(1316, CW + 26, "studená voda z vodovodu", "lab", "end")
    valve(1110, CW); check_valve(1060, CW)
    P(f"M1000,{CW} L1000,{CW - 40}", SV, 4)
    exp_vessel(1000, CW - 70)
    add(f'<g transform="translate(940,{CW})"><line x1="0" y1="0" x2="0" y2="14" stroke="{INK}" stroke-width="2.6"/>'
        f'<path d="M-9,14 L9,14 L0,30 Z" fill="#fff" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>'
        f'<rect x="-6" y="30" width="12" height="8" rx="2" fill="{RED}"/>'
        f'<line x1="9" y1="22" x2="24" y2="22" stroke="{GREY}" stroke-width="2.2" stroke-dasharray="5 4"/>'
        f'<path d="M24,16 v14 l8,-3 v-8 Z" fill="#fff" stroke="{GREY}" stroke-width="1.8"/></g>')
    arrow(1220, CW, 180, SV)
    num(VX + VW / 2 + 6, VY - 20, 19); num(VX + 60, 790, 20); num(VX + VW + 26, VY + VH - 60, 21)
    num(1085, CW + 34, 22); num(1040, CW - 86, 24); num(906, CW + 34, 23)
    num(670, SIN + 36, 2); num(692, 792, 2)
    num(745, 548, 2); num(700, 548, 2); num(636, 548, 2)
else:
    num(712, 548, 2); num(624, 548, 2)

# ---------------------------------------------------------------- čísla
num(80, 262, 1);  T(101, 267, "REO RH030–RH060", "lab")
num(285, 370, 2); num(290, 458, 2); num(396, 458, 3); num(312, 252, 4)
num(HX + HW + 8, HY - 22, 18)
num(TX - 20, TY - 12, 5); num(742, 400, 2)
num(TOP + 28, TY - 40, 6)
num(PSX + 48, 290, 7)
num(TX + TW - 18, 482, 8)
num(PSX + 48, TIN - 132, 9)
num(1022, 412, 10)
num(926, 545, 17); T(926, 575, "volitelně", "tx", "middle")
num(668, TOUT + 64, 16)
num(876, 180, 11)
num(1340, 270, 12)
num(SX - 22, TIN - 40, 13)
num(1236, 570, 14)
num(TOP + 30, TY + TH + 22, 15)
T(155, 518, "venkovní jednotka", "tx", "middle")

lx, ly = (60, 560) if TUV else (450, 598)
leg = [(RED, "výstup — teplá voda", None), (BLUE, "vratka — ochlazená voda", None), (YEL, "elektrické ovládání / signál", "7 5")]
if TUV:
    leg += [(TV, "teplá užitková voda", None), (SV, "studená voda", None)]
for k, (c, lab, d) in enumerate(leg):
    yy = ly + k * 17
    ds = f' stroke-dasharray="{d}"' if d else ''
    add(f'<line x1="{lx}" y1="{yy}" x2="{lx + 34}" y2="{yy}" stroke="{c}" stroke-width="{5 if not d else 3}" stroke-linecap="round"{ds}/>')
    T(lx + 44, yy + 4, lab, "tx")

# ---------------------------------------------------------------- spodní část
BY = ZB + 30
R(30, BY, 700, 370, fill="#fff", stroke="#DDE3E6", sw=1.5, rx=10)
if TUV:
    T(52, BY + 32, "SOUČÁSTI TUV", "hd")
    T(250, BY + 32, "prvky 1–18 viz schéma s hydroboxem H1", "tx")
    parts = [
        (18, "Hydrobox — trojcestný ventil", "výstup A → AKU, výstup B → spirála TUV"),
        (19, "Zásobník TUV se spirálou", "výkon spirály ≥ jmenovitý výkon TČ"),
        (20, "Čidlo teploty TUV (T2)", "do jímky zásobníku, kabel k řídicí desce TČ"),
        (21, "Elektrická topná vložka (volitelně)", "dohřev a antilegionella"),
        (22, "Uzávěr + zpětný ventil studené vody", "na přívodu z vodovodu"),
        (23, "Pojistný ventil TUV", "bez uzávěru, výfuk do odpadu"),
        (24, "Expanzní nádoba TUV", "pro pitnou vodu"),
        (2, "Uzávěry spirály a u AKU", "AKU lze odpojit, TUV běží dál"),
    ]
    split, step = 8, 37
else:
    T(52, BY + 32, "SOUČÁSTI", "hd")
    parts = [
        (1, "Tepelné čerpadlo REO RH030–RH060", "venkovní monoblok, chladivo R290"),
        (2, "Uzavírací ventily", "u jednotky, u AKU a kolem filtru 16"),
        (3, "Protizámrazový ventil", "venku na vratce"),
        (4, "Separátor + bezpečnostní odvzdušnění", "venku na výstupu za uzávěrem"),
        (5, "Akumulační nádrž 100 l", "odděluje primár a topení"),
        (6, "Automatický odvzdušňovací ventil AKU", "na horním vývodu"),
        (7, "Pojistná skupina (ventil + manometr)", "za sekundárním čerpadlem"),
        (8, "Teploměr + pojistný ventil AKU", "společný vývod na plášti"),
        (9, "Expanzní nádoba topení", "nad pojistnou skupinou"),
        (10, "Sekundární oběhové čerpadlo", "napájení spíná přijímač 11"),
        (11, "Přijímač termostatu (relé 230 V)", "u čerpadla"),
        (12, "Bezdrátový pokojový termostat", "v obytné místnosti"),
        (13, "Odvzdušňovací ventil v nejvyšším bodě", "rozvod topení"),
        (14, "Radiátory s odvzdušňovacími ventilky", "otopná soustava"),
        (15, "Vypouštěcí kohout AKU", "na dně nádrže"),
        (16, "Magnetický filtr", "na vratce do hydroboxu mezi uzávěry"),
        (17, "Směšovací ventil (volitelně)", "podlahovka max. 40 °C, ideálně 35 °C"),
        (18, "Hydrobox", "čerpadlo primáru, dohřev 3 kW, 3c ventil, exp. 8 l"),
    ]
    split, step = 9, 34
for i, (n, a, b) in enumerate(parts):
    col, row = (0, i) if i < split else (1, i - split)
    x = 52 + col * 345
    y = BY + 62 + row * step
    num(x + 12, y, n)
    T(x + 34, y - 2, a, "ts")
    T(x + 34, y + 13, b, "tx")

R(750, BY, 620, 370, fill=GRNL, stroke=None, rx=10)
T(772, BY + 32, "JAK TO FUNGUJE", "hd")
how = [
    "Čerpadlo hydroboxu (18) žene vodu přes TČ (1); při mrazu pomáhá",
    "elektrický dohřev 3 kW. Výstup A vede ohřátou vodu do AKU (5).",
]
how += ([
    "Při požadavku na TUV přepne trojcestný ventil hydroboxu na výstup B",
    "do spirály zásobníku (19); teplotu hlídá čidlo T2 (20). TUV má přednost.",
] if TUV else [
    "Výstup B (TUV) je zaslepen. Topení řídí termostat (12) přes",
    "přijímač (11), který spíná napájení sekundárního čerpadla (10).",
])
for i, s_ in enumerate(how):
    T(772, BY + 62 + i * 21, s_, "ts")
T(772, BY + 164, "BEZPEČNOST A TIPY", "hd")
tips = [
    "• Hydrobox na nehořlavou stěnu; prostor 10–35 °C, vlhkost do 70 %.",
    "• Kolem hydroboxu prostor pro servis; kabely zespodu, rezerva 2 m.",
    "• Separátor (4) venku — odvzdušnění R290 nesmí ústit do domu.",
    "• Filtr (16) mezi dvěma uzávěry — čištění bez vypouštění.",
    "• Pojistné ventily bez uzávěru, výfuk viditelně do odpadu.",
]
tips += (["• Pojistný ventil TUV (23) a exp. nádoba (24) pro pitnou vodu."] if TUV else
         ["• Podlahové topení: směšovací ventil (17) — max. 40 °C."])
for i, s_ in enumerate(tips):
    T(772, BY + 190 + i * 21, s_, "ts")

T(30, H - 12, "Zjednodušené orientační schéma — podle návodu TČ RH030–RH060 a návodu k instalaci hydraulického modulu REO HEATING.", "tx")
T(W - 30, H - 12, "REO HEATING", "zone", "end")
add('</svg>')

dst = os.path.normpath(os.path.join(HERE, "..", "schema-hydrobox-tuv.svg" if TUV else "schema-hydrobox-aku.svg"))
open(dst, "w", encoding="utf-8").write("\n".join(o))
print("zapsáno:", dst)
