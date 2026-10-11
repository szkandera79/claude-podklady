#!/usr/bin/env python3
"""Úpravy obrázků z originální prezentace → media_out/ (stejné názvy, nahrazují se v balíčku)."""
import io
import os
import zipfile

from PIL import Image, ImageDraw, ImageFont

from common import DIR, SRC

OUT = os.path.join(DIR, 'media_out')
os.makedirs(OUT, exist_ok=True)
z = zipfile.ZipFile(SRC)
load = lambda n: Image.open(io.BytesIO(z.read('ppt/media/' + n)))
def logo_variants():
    """Logo REO HEATING (stejné jako v manuálu): bílé pozadí → průhlednost; bílá varianta pro tmavé pozadí."""
    src = Image.open(os.path.join(DIR, 'media', 'logo-reoheating.png')).convert('RGB')
    col = Image.new('RGBA', src.size)
    wht = Image.new('RGBA', src.size)
    cp, wp, sp = col.load(), wht.load(), src.load()
    for y in range(src.height):
        for x in range(src.width):
            r, g, b = sp[x, y]
            a = 255 - min(r, g, b)                 # čím tmavší/sytější, tím neprůhlednější
            a = min(255, int(a * 1.6))
            if a < 8:
                a = 0
            k = 255 - a if a else 0
            cp[x, y] = (min(255, int((r - k) * 255 / a)) if a else 0,
                        min(255, int((g - k) * 255 / a)) if a else 0,
                        min(255, int((b - k) * 255 / a)) if a else 0, a)
            wp[x, y] = (255, 255, 255, a)
    bb = col.getbbox()
    return col.crop(bb), wht.crop(bb)


LOGO, LOGO_W = logo_variants()
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
FONT_B = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'


def fit_logo(size, logo, pad=0.06):
    """Logo vycentrované do průhledného plátna stejného poměru stran jako původní obrázek (bez deformace)."""
    W, H = size[0] * 3, size[1] * 3
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    lw = int(W * (1 - 2 * pad))
    lh = int(lw * logo.height / logo.width)
    if lh > H * (1 - 2 * pad):
        lh = int(H * (1 - 2 * pad))
        lw = int(lh * logo.width / logo.height)
    canvas.paste(logo.resize((lw, lh), Image.LANCZOS), ((W - lw) // 2, (H - lh) // 2))
    return canvas


def save(img, name):
    path = os.path.join(OUT, name)
    if name.endswith('.png'):
        img.save(path, optimize=True)
    else:
        img.convert('RGB').save(path, quality=90)


# 1) loga v šabloně: titulní layout (image2, šedé na modrém pozadí) a obsahové layouty (image3, vpravo nahoře)
save(fit_logo(load('image2.png').size, LOGO_W), 'image2.png')
save(fit_logo(load('image3.png').size, LOGO), 'image3.png')

# 2) fotka jednotky (image26): nápis na čelní liště → svislá interpolace barvy lišty
im = load('image26.png').convert('RGB')
px = im.load()
x0, x1, y0, y1 = 428, 575, 101, 133
for y in range(y0, y1 + 1):                      # vodorovná interpolace mezi okraji (lišta má svislý gradient)
    a, b = px[x0 - 1, y], px[x1 + 1, y]
    for x in range(x0, x1 + 1):
        t = (x - x0 + 1) / (x1 - x0 + 2)
        px[x, y] = tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))
save(im, 'image26.png')

# 3) výkres jednotky (image22): modré logo na panelu → logo REO HEATING
im = load('image22.png').convert('RGBA')
px = im.load()
box = (500, 60, 905, 170)
bg = px[box[0] + 20, box[1] + 5]
for x in range(box[0], box[2]):
    for y in range(box[1], box[3]):
        r, g, b, a = px[x, y]
        if b > r + 40:                           # modré pixely loga
            px[x, y] = bg
lw = 200
logo = LOGO.resize((lw, int(lw * LOGO.height / LOGO.width)), Image.LANCZOS)
im.alpha_composite(logo, (box[0] + (box[2] - box[0] - lw) // 2 - 10, box[1] + 8))
save(im, 'image22.png')

# 4) image13: dvě fotky izolace s čínskými popisky → odříznout popisky (výšku tvaru upraví build.py)
im = load('image13.png').convert('RGB')
save(im.crop((0, 0, im.width, 515)), 'image13.png')
print('ok')

# 5) image31 (§14a EnWG): anglické popisky → česky (text vymazat podle pozadí a vysázet znovu, 2× rozlišení)
im = load('image31.png').convert('RGB')
im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
px = im.load()
S = 2
for (xa, xb) in ((0, 298), (712, 1029)):
    for y in range(0, im.height):
        a = px[min(xa * S, im.width - 1), y] if xa else px[0, y]
        b = px[min(xb * S - 1, im.width - 1), y]
        for x in range(xa * S, min(xb * S, im.width)):
            t = (x - xa * S) / max(1, (xb - xa) * S)
            px[x, y] = tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))
d = ImageDraw.Draw(im)
TITLE = (26, 140, 214)
BODY = (40, 130, 200)
ft, fb = ImageFont.truetype(FONT_B, 17 * S), ImageFont.truetype(FONT, 15 * S)
blocks = [  # (zarovnání, x, y titulku, titulek, řádky textu)
    ('r', 283, 54, 'ZABRAŇUJE PŘETÍŽENÍ SÍTĚ', ['Podporuje stabilitu místní sítě', 'omezením odběru ve špičce.']),
    ('l', 727, 54, 'BEZ VÝPADKŮ PROVOZU', ['Nepřetržitý provoz bez aktivace', 'bezpečnostního vypnutí.']),
    ('r', 283, 242, 'KONTROLA NÁKLADŮ', ['Chrání před dražšími tarify', 've špičce.']),
    ('l', 727, 242, 'PLYNULE A AUTOMATICKY', ['Inteligentní řízení příkonu', 'bez zásahu uživatele.']),
]
for al, x, y, title, lines in blocks:
    for k, (txt, f, col, yy) in enumerate([(title, ft, TITLE, y)] + [(l, fb, BODY, y + 30 + 24 * i) for i, l in enumerate(lines)]):
        w = d.textlength(txt, font=f)
        xx = x * S - w if al == 'r' else x * S
        d.text((xx, yy * S), txt, font=f, fill=col)
save(im, 'image31.png')
print('ok 31')

# 6) image1 (pozadí titulního a závěrečného snímku): modrá mapa světa → zelená REO HEATING (posun odstínu)
im = load('image1.jpeg').convert('RGB')
h, s, v = im.convert('HSV').split()
target = int(125 / 360 * 255)                      # zelená
h = h.point(lambda _: target)
s = s.point(lambda x: int(x * 0.62))
v = v.point(lambda x: int(x * 0.62))
save(Image.merge('HSV', (h, s, v)).convert('RGB'), 'image1.jpeg')
print('ok 1')

# 7) image96 (snímek 39, IoT diagram): drobný svislý nápis výrobce na boku miniatury jednotky → REO HEATING
im = load('image96.png').convert('RGB')
px = im.load()
for y in range(174, 207):                       # vymazat: interpolace barvy panelu mezi okraji nápisu
    a, b = px[152, y], px[161, y]
    for x in range(153, 161):
        t = (x - 152) / 9
        px[x, y] = tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))
K = 8                                          # vysázet ve 8× rozlišení, svisle shora dolů, a zmenšit
ft = ImageFont.truetype(FONT, 4 * K)
tw = int(ft.getlength('REO HEATING'))
txt = Image.new('L', (tw + 4, 5 * K), 0)
ImageDraw.Draw(txt).text((2, 0), 'REO HEATING', font=ft, fill=255)
txt = txt.rotate(-90, expand=True)
txt = txt.resize((max(1, txt.width // K), 29), Image.LANCZOS)
col = Image.new('RGB', txt.size, (185, 185, 188))
im.paste(col, (155, 176), txt.point(lambda v: int(v * 0.85)))
save(im, 'image96.png')
print('ok 96')
