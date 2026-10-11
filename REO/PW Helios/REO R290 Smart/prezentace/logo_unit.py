#!/usr/bin/env python3
"""Fotka jednotky (orig. ppt/media/image6.png, snímky 3 a 15): nápis POWER WORLD na čelní liště → REO HEATING.
Lišta se v oblasti nápisu zrekonstruuje (svislá interpolace v rámci lišty + zrno), nový nápis se vysází
písmem Exo 2 Black Italic (OFL, nejbližší tvarově), se stejnou výškou, sklonem, kurzívou a kovovým přechodem.
Výstup: media_out/image6.png
"""
import io
import math
import os
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from common import DIR, SRC

im = Image.open(io.BytesIO(zipfile.ZipFile(SRC).read('ppt/media/image6.png'))).convert('RGBA')
a = np.asarray(im).astype(float)
SLOPE = 0.109                                  # sklon lišty (dy/dx)
TOP = lambda x: 971.7 + SLOPE * (x - 1870)     # horní hrana písmen
BOT = lambda x: 1010.0 + SLOPE * (x - 1856.7)  # dolní hrana písmen
X0, X1 = 1846, 2292
rng = np.random.default_rng(7)

# 1) vyčistit lištu
for x in range(X0, X1):
    ya, yb = int(TOP(x)) - 6, int(math.ceil(BOT(x))) + 3
    ca, cb = a[ya - 2:ya, x, :3].mean(0), a[yb + 1:yb + 3, x, :3].mean(0)
    for y in range(ya, yb + 1):
        t = (y - ya) / (yb - ya)
        a[y, x, :3] = ca * (1 - t) + cb * t + rng.normal(0, 1.6)
clean = Image.fromarray(np.clip(a, 0, 255).astype('uint8'), 'RGBA')

# 2) nový nápis – vysázet rovně ve 4× rozlišení, pak zkosit/natočit a zmenšit
K = 4
CAP = 38 * K
font = ImageFont.truetype(os.path.join(DIR, 'media', 'Exo2-Italic.ttf'), 100)
font.set_variation_by_axes([900])
bb = font.getbbox('H')
size = int(100 * CAP / (bb[3] - bb[1]))
font = ImageFont.truetype(os.path.join(DIR, 'media', 'Exo2-Italic.ttf'), size)
font.set_variation_by_axes([900])
TEXT = 'REO HEATING'
l, t, r, b = font.getbbox(TEXT)
W, H = r - l + 40 * K, b - t + 40 * K
mask = Image.new('L', (W, H), 0)
ImageDraw.Draw(mask).text((20 * K - l, 20 * K - t), TEXT, font=font, fill=255)
# šířka jako originál (≈ 420 px), mírně užší písmo stejně jako na fotce
target_w = 425 * K
bx = mask.getbbox()
mask = mask.crop(bx)
mask = mask.resize((target_w, mask.height), Image.LANCZOS)
# kovový přechod: vlevo bílá, vpravo šedá (jako originál) + jemné svislé stínování
w, h = mask.size
gx = np.linspace(242, 150, w)[None, :]
gy = np.linspace(1.0, 0.9, h)[:, None]
lum = np.clip(gx * gy, 0, 255)
fill = np.dstack([lum, lum, lum * 1.01, np.asarray(mask, float)]).clip(0, 255).astype('uint8')
txt = Image.fromarray(fill, 'RGBA')
# tmavší lem (ražba)
edge = mask.filter(ImageFilter.MaxFilter(5))
shadow = Image.new('RGBA', mask.size, (40, 40, 42, 0))
shadow.putalpha(edge.point(lambda v: int(v * 0.55)))
layer = Image.alpha_composite(shadow, txt)
# geometrie: dodatečné zkosení (originál má výraznější kurzívu) a sklon lišty
SHEAR = 0.16
pad = int(h * SHEAR) + 4
layer = layer.transform((w + pad, h), Image.AFFINE, (1, SHEAR, -pad + 2, 0, 1, 0), resample=Image.BICUBIC)
layer = layer.resize(((w + pad) // K, h // K), Image.LANCZOS)
lw, lh = layer.size
ang = math.degrees(math.atan(SLOPE))
layer = layer.rotate(-ang, resample=Image.BICUBIC, expand=True)
# umístění: levý horní roh písmen na začátku původního nápisu
x_left = 1858
cx = x_left + lw / 2
cy = (TOP(cx) + BOT(cx)) / 2
out = clean.copy()
out.alpha_composite(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)))
os.makedirs(os.path.join(DIR, 'media_out'), exist_ok=True)
out.save(os.path.join(DIR, 'media_out', 'image6.png'), optimize=True)
print('ok', layer.size)
