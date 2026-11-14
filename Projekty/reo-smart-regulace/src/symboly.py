#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Knihovna symbolů schémat REO HEATING (převzato z reo-schemata-zapojeni/src/gen_schema_kuncice_tuv.py).
Globální seznam `o` sbírá SVG prvky; reset() začne nový list."""
import os, re, math
LOGO = os.path.expanduser("~/Claude/REO/logo/logo-reo-heating.svg")
RED, BLUE = "#D9342B", "#2468B3"
YEL = "#E3A71B"
TV, SV = "#E07B39", "#3BA3C9"
INK, GREY = "#22272A", "#6B7378"
GRN, GRNL = "#34A263", "#E9F6EE"
o = []
def reset():
    o.clear()
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

