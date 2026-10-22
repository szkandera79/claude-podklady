"""Závazné logo REO HEATING pro dokumenty (dodáno uživatelem 22. 10. 2026 jako PNG 292×140).

Překresleno do vektoru: šedá a zelená střecha s komínky, žluté okno 2×2, žluté slunce,
pod tím nápis „REO HEATING“ (Avenir Next Medium převedený na křivky).
Výstup: logo-reo-heating.svg (+ varianta -white pro tmavé podklady). PNG renderuje build.sh.
Spuštění: python3 build_logo.py   (vyžaduje fonttools)
"""
import math, os
from fontTools.ttLib import TTCollection
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = os.path.dirname(os.path.abspath(__file__))
GREY, GREEN, YELLOW, INK = "#838383", "#50854D", "#F0C246", "#363533"

# souřadnice v rastru předlohy 292×140 px
ROOF_W = 7.2
grey_roof = [(73.5, 76.5), (112, 37.3), (128.5, 53)]
green_roof = [(117.5, 73.5), (161, 32.2), (205, 75.5)]
grey_chimney = (86, 44.5, 6, 14)      # x, y, w, h
green_chimney = (181, 39.5, 6.2, 14)
window = (152, 54, 17.6, 16.6, 1.6)   # x, y, w, h, mezera
sun_c, sun_r, ray_in, ray_out, rays = (213, 44.5), 8.9, 10.9, 17.4, 12

TEXT, TEXT_X0, TEXT_X1, CAP_TOP, BASELINE = "REO HEATING", 31, 281.5, 88, 116.3


def text_path():
    font = TTCollection('/System/Library/Fonts/Avenir Next.ttc').fonts[5]  # Medium
    gs, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font['hmtx']
    cap = font['OS/2'].sCapHeight or 708
    s = (BASELINE - CAP_TOP) / cap
    names = [cmap[ord(ch)] for ch in TEXT]
    adv = [hmtx[n][0] for n in names]
    # mezery mezi písmeny dorovnané tak, aby nápis zabral stejnou šířku jako v předloze
    first_lsb = hmtx[names[0]][1]
    last_glyph_w = gs[names[-1]].width
    natural = sum(adv[:-1]) + last_glyph_w - first_lsb
    track = ((TEXT_X1 - TEXT_X0) / s - natural) / (len(TEXT) - 1)
    pen = SVGPathPen(gs)
    x = -first_lsb
    for n, a in zip(names, adv):
        tp = TransformPen(pen, (s, 0, 0, -s, TEXT_X0 + x * s, BASELINE))
        gs[n].draw(tp)
        x += a + track
    return pen.getCommands()


def roof(P, w):
    """Obrys tlusté lomené čáry (3 body) jako polygon: ostrá špička, konce kolmé na čáru."""
    def off(a, b, d):
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy)
        nx, ny = -dy / L * d, dx / L * d
        return (a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny)
    def cross(l1, l2):
        (x1, y1), (x2, y2) = l1; (x3, y3), (x4, y4) = l2
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    a, b, c = P; h = w / 2
    L1, L2 = off(a, b, h), off(b, c, h)
    R1, R2 = off(a, b, -h), off(b, c, -h)
    poly = [L1[0], cross(L1, L2), L2[1], R2[1], cross(R1, R2), R1[0]]
    return 'M' + ' L'.join(f'{x:.2f} {y:.2f}' for x, y in poly) + ' Z'


def sun():
    cx, cy = sun_c
    out = [f'<circle cx="{cx}" cy="{cy}" r="{sun_r}"/>']
    for k in range(rays):
        a = math.radians(k * 360 / rays - 90)
        h = math.radians(15.5)
        p = [(cx + ray_in * math.cos(a - h), cy + ray_in * math.sin(a - h)),
             (cx + ray_out * math.cos(a), cy + ray_out * math.sin(a)),
             (cx + ray_in * math.cos(a + h), cy + ray_in * math.sin(a + h))]
        out.append('<path d="M' + ' L'.join(f'{x:.2f} {y:.2f}' for x, y in p) + ' Z"/>')
    return ''.join(out)


def svg(text_col, grey_col):
    pts = lambda P: ' '.join(f'{x},{y}' for x, y in P)
    x, y, w, h, g = window
    cw, ch = (w - g) / 2, (h - g) / 2
    win = ''.join(f'<rect x="{x + i * (cw + g):.2f}" y="{y + j * (ch + g):.2f}" width="{cw:.2f}" height="{ch:.2f}"/>'
                  for i in (0, 1) for j in (0, 1))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="24 22 264 101" role="img" aria-label="REO HEATING">
  <path d="{roof(grey_roof, ROOF_W)}" fill="{grey_col}"/>
  <path d="{roof(green_roof, ROOF_W)}" fill="{GREEN}"/>
  <rect x="{grey_chimney[0]}" y="{grey_chimney[1]}" width="{grey_chimney[2]}" height="{grey_chimney[3]}" fill="{grey_col}"/>
  <rect x="{green_chimney[0]}" y="{green_chimney[1]}" width="{green_chimney[2]}" height="{green_chimney[3]}" fill="{GREEN}"/>
  <g fill="{YELLOW}">{win}{sun()}</g>
  <path d="{text_path()}" fill="{text_col}"/>
</svg>
'''


if __name__ == '__main__':
    open(os.path.join(HERE, 'logo-reo-heating.svg'), 'w').write(svg(INK, GREY))
    open(os.path.join(HERE, 'logo-reo-heating-white.svg'), 'w').write(svg('#FFFFFF', '#C9C9C9'))
    print('ok')
