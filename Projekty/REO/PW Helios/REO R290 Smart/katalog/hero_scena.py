#!/usr/bin/env python3
"""Hero scéna pro katalog: ve scéně (venkovní jednotka + Watertank, assets/src/hero-scena-orig.webp)
nahradí starou jednotku jednotkou REO R290 Smart (assets/smart-cut.png). Výstup assets/hero-scena.png.
Dřevěný obklad za starou jednotkou se doplní posunem po sloupcích o násobek periody prken (perspektiva)."""
import pathlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

A = pathlib.Path(__file__).parent / "assets"
src = Image.open(A / "src/hero-scena-orig.webp").convert("RGB")
arr = np.asarray(src).copy()

# 1) doplnit obklad v oblasti staré jednotky (x 40–372, y 336–floor); jas srovnat podle okolí (vlevo/vpravo)
X0, X1, Y0, Y1 = 40, 372, 336, 820
per = lambda x: 32 + (x - 20) * 9 / 380     # perioda prken roste s x (perspektiva)
kk = lambda x: int(round(5 * per(x)))       # posun o 5 period
S = np.asarray(src).astype(float)
def gain(xa, xb, y):
    a = np.mean([S[y, x] for x in range(xa, xb)], 0)
    b = np.mean([S[y - kk(x), x] for x in range(xa, xb)], 0)
    return a / np.maximum(b, 1)
out = S.copy()
for y in range(Y0, Y1):
    gl, gr = gain(4, 36, y), gain(376, 436, y)
    for x in range(X0, X1):
        t = (x - 20) / (406 - 20)
        out[y, x] = S[y - kk(x), x] * ((1 - t) * gl + t * gr)
# měkký přechod na horní hraně
for i in range(8):
    y = Y0 + i; w = i / 8
    out[y, X0:X1] = w * out[y, X0:X1] + (1 - w) * S[y, X0:X1]
arr = np.clip(out, 0, 255).astype("uint8")
img = Image.fromarray(arr)

# podlaha – spodní část (pod linkou stěna/podlaha) vyplnit barvou podlahy vlevo
floor = lambda x: 700 + (x / 500) * 105     # linka stěna/podlaha (odhad ze snímku)
fl = np.asarray(img).copy()
ref = np.asarray(src)[760:838, 0:30].reshape(-1, 3).mean(0)
for x in range(X0 - 10, X1 + 4):
    for y in range(int(floor(x)), 838):
        fl[y, x] = ref * (0.97 + 0.03 * (y - 700) / 138)
img = Image.fromarray(fl.astype("uint8"))

# 2) stín a jednotka Smart
unit = Image.open(A / "smart-cut.png").convert("RGBA")
W = 452
unit = unit.resize((W, int(unit.height * W / unit.width)), Image.LANCZOS)
ux, uy = 18, 828 - unit.height
sh = Image.new("L", img.size, 0)
ImageDraw.Draw(sh).ellipse((ux + 10, 800, ux + W + 30, 846), fill=150)
sh = sh.filter(ImageFilter.GaussianBlur(14))
dark = Image.new("RGB", img.size, (40, 40, 42))
img = Image.composite(dark, img, sh)
img.paste(unit, (ux, uy), unit)
img.save(A / "hero-scena.png")
print("hero-scena.png", img.size, "unit at", ux, uy, unit.size)
