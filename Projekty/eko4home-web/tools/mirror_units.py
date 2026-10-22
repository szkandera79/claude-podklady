"""Zrcadlí jednotky Smart/RHX (stejný úhel jako RH030–RH060): starý (zrcadlový) nápis se rozmaže z okolí lišty
a vepíše se nový čitelný „REO HEATING“ ve sklonu lišty."""
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
IMG = Path(__file__).resolve().parent.parent / 'assets/img'
FONT = '/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf'

def fix(src, dst, x0, x1, top0, bot0, slope, size, color, letter=0):
    im = Image.open(IMG/src).convert('RGBA'); W, H = im.size
    m = np.asarray(im.transpose(Image.FLIP_LEFT_RIGHT)).astype(float).copy()
    # zrcadlové sloupce; v originále text v sloupci x zabírá řádky top0+slope*(x-x0) … bot0+slope*(x-x0)
    for xo in range(x0 - 3, x1 + 4):
        xm = W - 1 - xo
        t = int(round(top0 + slope * (xo - x0))) - 2
        b = int(round(bot0 + slope * (xo - x0))) + 2
        for c in range(4):
            col = m[:, xm, c]
            col[t:b + 1] = np.linspace(col[t - 1], col[b + 1], b - t + 1)
    out = Image.fromarray(m.clip(0, 255).astype('uint8'))
    # nový text
    f = ImageFont.truetype(FONT, size)
    txt = 'REO HEATING'
    bb = f.getbbox(txt); tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pad = int(abs(slope) * tw) + 4
    layer = Image.new('RGBA', (tw + 6, th + 2 * pad + 6), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((3 - bb[0], pad + 3 - bb[1]), txt, font=f, fill=color, spacing=letter)
    # v zrcadle lišta stoupá doprava → posun obsahu nahoru s rostoucím x
    layer = layer.transform(layer.size, Image.AFFINE, (1, 0, 0, abs(slope), 1, 0), resample=Image.BICUBIC) if slope else layer
    mx_left = W - 1 - x1
    ytop_left = top0 + slope * (x1 - x0)          # horní hrana textu u levého (zrcadlového) konce
    out.alpha_composite(layer, (mx_left + 4, int(round(ytop_left - pad + 1))))
    out.save(IMG/dst); print(dst)

fix('smart.png', 'smart-m.png', 404, 545, 90, 110, 0.065, 20, (208, 208, 210, 245))
fix('rhx-pro-alpha.png', 'rhx-pro-m.png', 262, 364, 15, 30, 0.0, 15, (120, 122, 128, 235))
