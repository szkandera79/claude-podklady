#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Topná (výkonová) křivka kaskády 2× / 3× RH X50 při W55 proti potřebě domu.

Generuje topna-krivka.svg a vloží ho inline do nabidka.html mezi <!--KRIVKA--> … <!--/KRIVKA-->
(inline SVG kvůli tisku — viz README BD Jandova). Spouštět z kořene repa:
    python3 porovnani-x50-2-3/src/gen_chart.py
"""
import re
from pathlib import Path
from model import AMB, W55, load, bivalence

ROOT = Path(__file__).resolve().parent.parent
W, H = 760, 400
ML, MR, MT, MB = 56, 150, 18, 46
X0, X1, Y0, Y1 = -20, 15, 0, 160
GREEN, DARK, GREY, AMBER = "#1E8F5B", "#0F3D2E", "#8A968F", "#DA8718"


def px(t):
    return ML + (t - X0) / (X1 - X0) * (W - ML - MR)


def py(v):
    return MT + (1 - (v - Y0) / (Y1 - Y0)) * (H - MT - MB)


def path(points):
    return "M" + " L".join(f"{px(t):.1f},{py(v):.1f}" for t, v in points)


pts = [(t, c) for t, c in zip(AMB, W55["cap"]) if X0 <= t <= X1]
s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
     f'font-family="Segoe UI,system-ui,-apple-system,Helvetica,Arial,sans-serif" font-size="12">',
     f'<rect width="{W}" height="{H}" fill="#fff"/>']
for v in range(0, Y1 + 1, 20):
    s.append(f'<line x1="{ML}" x2="{W-MR}" y1="{py(v):.1f}" y2="{py(v):.1f}" stroke="#e3e9e5"/>')
    s.append(f'<text x="{ML-8}" y="{py(v)+4:.1f}" text-anchor="end" fill="#5d6b64">{v}</text>')
for t in range(X0, X1 + 1, 5):
    s.append(f'<line x1="{px(t):.1f}" x2="{px(t):.1f}" y1="{MT}" y2="{H-MB}" stroke="#eef2ef"/>')
    s.append(f'<text x="{px(t):.1f}" y="{H-MB+18}" text-anchor="middle" fill="#5d6b64">{t}</text>')
s.append(f'<line x1="{px(-15):.1f}" x2="{px(-15):.1f}" y1="{MT}" y2="{H-MB}" stroke="{AMBER}" stroke-dasharray="4 4"/>')
s.append(f'<text x="{px(-15)+4:.1f}" y="{H-MB-8}" fill="{AMBER}" font-weight="600">návrhová −15 °C</text>')
s.append(f'<text x="{(ML+W-MR)/2:.1f}" y="{H-8}" text-anchor="middle" fill="#1b2420">Venkovní teplota (°C)</text>')
s.append(f'<text transform="translate(16,{(MT+H-MB)/2:.1f}) rotate(-90)" text-anchor="middle" fill="#1b2420">Topný výkon (kW)</text>')

# potřeba domu (vytápění) pro 55 / 65 / 75 kW
HALO = 'stroke="#fff" stroke-width="4" paint-order="stroke"'
for loss in (55, 65, 75):
    s.append(f'<path d="{path([(X0, load(loss, X0)), (X1, load(loss, X1))])}" fill="none" '
             f'stroke="{GREY}" stroke-width="1.6" stroke-dasharray="6 5"/>')
for loss in (55, 65, 75):
    t = -4.5
    s.append(f'<text x="{px(t):.1f}" y="{py(load(loss, t))+4:.1f}" fill="#5d6b64" font-size="11" {HALO}>ztráta {loss} kW</text>')

# kaskády
for n, col, lab in ((3, DARK, "3× RH X50 · varianta B"), (2, GREEN, "2× RH X50 · varianta A")):
    p = [(t, n * c) for t, c in pts]
    s.append(f'<path d="{path(p)}" fill="none" stroke="{col}" stroke-width="3"/>')
    for t, v in p:
        s.append(f'<circle cx="{px(t):.1f}" cy="{py(v):.1f}" r="3" fill="{col}"/>')
    s.append(f'<text x="{px(X1)+8:.1f}" y="{py(p[-1][1])+4:.1f}" fill="{col}" font-weight="700">{lab.split(" · ")[1]}</text>')

# body bivalence varianty A
for loss in (55, 65, 75):
    tb = bivalence(loss, 2)
    if tb is not None:
        s.append(f'<circle cx="{px(tb):.1f}" cy="{py(load(loss, tb)):.1f}" r="5.5" fill="#fff" stroke="{AMBER}" stroke-width="2.5"/>')

# legenda (volné místo vlevo nahoře)
lx, ly = px(-19.3), py(155)
s.append(f'<rect x="{lx-8:.1f}" y="{ly-6:.1f}" width="232" height="86" rx="8" fill="#fff" stroke="#d8ded9"/>')
items = [(DARK, "line", "Varianta B · 3× RH X50 (W55)"), (GREEN, "line", "Varianta A · 2× RH X50 (W55)"),
         (GREY, "dash", "Potřeba tepla na vytápění"), (AMBER, "dot", "Bod bivalence varianty A")]
for i, (col, kind, lab) in enumerate(items):
    y = ly + 12 + i * 19
    if kind == "line":
        s.append(f'<line x1="{lx:.1f}" x2="{lx+24:.1f}" y1="{y-4:.1f}" y2="{y-4:.1f}" stroke="{col}" stroke-width="3"/>')
    elif kind == "dash":
        s.append(f'<line x1="{lx:.1f}" x2="{lx+24:.1f}" y1="{y-4:.1f}" y2="{y-4:.1f}" stroke="{col}" stroke-width="1.6" stroke-dasharray="6 5"/>')
    else:
        s.append(f'<circle cx="{lx+12:.1f}" cy="{y-4:.1f}" r="5" fill="#fff" stroke="{col}" stroke-width="2.5"/>')
    s.append(f'<text x="{lx+32:.1f}" y="{y:.1f}" fill="#1b2420">{lab}</text>')
s.append("</svg>")
svg = "\n".join(s)

(ROOT / "topna-krivka.svg").write_text(svg, encoding="utf-8")
html_p = ROOT / "nabidka.html"
html = html_p.read_text(encoding="utf-8")
html, k = re.subn(r"<!--KRIVKA-->.*?<!--/KRIVKA-->", lambda m: f"<!--KRIVKA-->\n{svg}\n<!--/KRIVKA-->", html, flags=re.S)
html_p.write_text(html, encoding="utf-8")
print("svg ok, vloženo:", k)
