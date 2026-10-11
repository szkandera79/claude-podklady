#!/usr/bin/env python3
"""Generuje logo REO HEATING (domek se sluncem + hranatý nápis) do SVG.
Nápis je kreslený vektorově — systémové písmo se vzoru neblíží."""
import math

W, C = 17, 14          # síla tahu / zkosení rohu, cap height = 100
def poly(p): return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in p) + " Z"

G = {}
G['R'] = (56, [poly([(C,0),(42,0),(56,C),(56,38),(44,50),(56,100),(36,100),(27,57),(17,57),(17,100),(0,100),(0,C)]),
               poly([(17,19),(39,19),(39,38),(17,38)])])
G['E'] = (48, [poly([(C,0),(48,0),(48,W),(W,W),(W,41),(41,41),(41,58),(W,58),(W,83),(48,83),(48,100),
                     (C,100),(0,100-C),(0,C)])])
G['O'] = (60, [poly([(C,0),(60-C,0),(60,C),(60,100-C),(60-C,100),(C,100),(0,100-C),(0,C)]),
               poly([(W+8,W),(60-W-8,W),(60-W,W+8),(60-W,100-W-8),(60-W-8,100-W),(W+8,100-W),
                     (W,100-W-8),(W,W+8)])])
G['H'] = (58, [poly([(C,0),(W,0),(W,41),(58-W,41),(58-W,0),(58-C,0),(58,C),(58,100-C),(58-C,100),
                     (58-W,100),(58-W,59),(W,59),(W,100),(C,100),(0,100-C),(0,C)])])
G['A'] = (60, [poly([(19,0),(41,0),(60,100),(42,100),(38,84),(22,84),(18,100),(0,100)]),
               poly([(30,24),(37,66),(23,66)])])
G['T'] = (52, [poly([(0,0),(52,0),(52,W),(34,W),(34,100),(18,100),(18,W),(0,W)])])
G['N'] = (58, [poly([(0,0),(18,0),(40,60),(40,0),(58,0),(58,100),(40,100),(18,40),(18,100),(0,100)])])
G['G'] = (60, [poly([(C,0),(60-C,0),(60,C),(60,100-C),(60-C,100),(C,100),(0,100-C),(0,C)]),
               poly([(W,W),(75,W),(75,44),(31,44),(31,61),(60-W,61),(60-W,100-W),(W,100-W)])])
G['I'] = (18, [poly([(0,0),(18,0),(18,100),(0,100)])])

def wordmark(text, gap=9, space=26):
    d, x = [], 0
    for ch in text:
        if ch == ' ':
            x += space; continue
        w, paths = G[ch]
        # obrys i protilehlé počítadlo musí být JEDEN <path>, jinak even-odd nevykrojí díru
        d.append(f'<path d="{" ".join(paths)}" transform="translate({x:.1f},0)"/>')
        x += w + gap
    return "\n    ".join(d), x - gap

marks, wmw = wordmark('REO HEATING')
SC = 980 / wmw

CX, CY, R1, R2, HALF = 486, 44, 32, 58, 10
rays = []
for k in range(8):
    a = math.radians(k * 45)
    tip = (CX + R2*math.cos(a), CY + R2*math.sin(a))
    b1 = (CX + R1*math.cos(a - math.radians(HALF)), CY + R1*math.sin(a - math.radians(HALF)))
    b2 = (CX + R1*math.cos(a + math.radians(HALF)), CY + R1*math.sin(a + math.radians(HALF)))
    rays.append("M {:.1f} {:.1f} L {:.1f} {:.1f} L {:.1f} {:.1f} Z".format(*b1, *tip, *b2))
rays = " ".join(rays)

H = 240 + 100 * SC
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 {H:.0f}" role="img" aria-label="REO HEATING">
  <g transform="translate(74.3,-8.7) scale(1.453)">
    <g fill="none" stroke-linecap="butt" stroke-linejoin="miter" stroke-miterlimit="6">
      <path d="M40 142 L40 98 L150 18 L252 96" stroke="#8A8C8E" stroke-width="26"/>
      <path d="M218 100 L320 22 L422 100 L422 142 L218 142 Z" stroke="#3E9B45" stroke-width="26"/>
    </g>
    <rect x="296" y="56" width="48" height="48" fill="#F7C838"/>
    <path d="M320 56 L320 104 M296 80 L344 80" stroke="#3E9B45" stroke-width="8"/>
    <circle cx="{CX}" cy="{CY}" r="28" fill="#F7C838"/>
    <path d="{rays}" fill="#F7C838"/>
  </g>
  <text x="978" y="212" text-anchor="end" fill="#8A8C8E"
        font-family="'Avenir Next','Helvetica Neue',Helvetica,Arial,sans-serif"
        font-weight="700" font-size="36" letter-spacing="4">S.R.O.</text>
  <g fill="#3A3B39" fill-rule="evenodd" transform="translate(0,240) scale({SC:.4f})">
    {marks}
  </g>
</svg>
'''
open('logo-reoheating.svg', 'w').write(svg)
open('logo-reoheating-white.svg', 'w').write(
    svg.replace('#8A8C8E', '#FFFFFF').replace('#3A3B39', '#FFFFFF'))
print('nápis', wmw, '→ scale', round(SC, 3))
