#!/usr/bin/env python3
"""Úpravy obrázků z originální prezentace → media_out/ (stejné názvy jako v originálu, build.py je dosadí podle otisku).

- šablona (pozadí, loga) a infografika §14a / IoT diagram: převzato z ../prezentace/media_out (stejné obrázky)
- fotky jednotek: nápis výrobce na horní liště → REO HEATING
- infografika R290 (snímek 4): logo výrobce v ikoně IoT pryč, popisky česky
- tabulka ikon ovladače, legenda schématu, Modbus, SG schéma: popisky česky
- snímek IoT: název zařízení cizího zákazníka v náhledu portálu odstraněn
"""
import io
import os
import shutil
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from common import DIR, PREV, SRC

OUT = os.path.join(DIR, 'media_out')
os.makedirs(OUT, exist_ok=True)
z = zipfile.ZipFile(SRC)
load = lambda n: Image.open(io.BytesIO(z.read('ppt/media/' + n)))
SUP = '/System/Library/Fonts/Supplemental/'
F = {k: SUP + v for k, v in dict(arial='Arial.ttf', arialb='Arial Bold.ttf', narrowb='Arial Narrow Bold.ttf',
                                  narrow='Arial Narrow.ttf', times='Times New Roman.ttf').items()}
EXO = os.path.join(DIR, 'media', 'Exo2-Italic.ttf')


def save(img, name):
    path = os.path.join(OUT, name)
    if name.endswith('.png'):
        img.save(path, optimize=True)
    else:
        img.convert('RGB').save(path, quality=92)


# ---------------------------------------------------------------- 1) převzaté z prezentace RH06–RH16
for old, new in (('image1.jpeg', 'image1.jpeg'), ('image2.png', 'image2.png'), ('image3.png', 'image3.png'),
                 ('image31.png', 'image22.png'), ('image96.png', 'image81.png')):
    shutil.copyfile(os.path.join(PREV, 'media_out', old), os.path.join(OUT, new))


# ---------------------------------------------------------------- pomocné funkce
def tight_box(im, box, bg_thr=60):
    """Těsný obdélník pixelů, které se liší od převládající barvy (pozadí) v zadané oblasti."""
    a = np.asarray(im.convert('RGB').crop(box)).astype(int)
    ref = np.median(a.reshape(-1, 3), axis=0)
    mask = np.abs(a - ref).sum(2) > bg_thr
    ys, xs = np.nonzero(mask)
    if not len(xs):
        return None
    return box[0] + xs.min(), box[1] + ys.min(), box[0] + xs.max() + 1, box[1] + ys.max() + 1


def fill_vertical(im, box, gap=2):
    """Vymaže obsah obdélníku svislou interpolací mezi pixely nad a pod ním (lišty s přechodem)."""
    px = im.load()
    x0, y0, x1, y1 = box
    for x in range(x0, x1):
        a = np.mean([px[x, y0 - gap - k][:3] for k in range(2)], axis=0)
        b = np.mean([px[x, y1 + gap + k][:3] for k in range(2)], axis=0)
        for y in range(y0 - gap + 1, y1 + gap):
            t = (y - y0 + gap) / (y1 - y0 + 2 * gap)
            c = tuple(int(v) for v in a * (1 - t) + b * t)
            px[x, y] = c + ((px[x, y][3],) if im.mode == 'RGBA' else ())


def fill_horizontal(im, box, gap=2):
    """Vymaže obsah obdélníku vodorovnou interpolací mezi pixely vlevo a vpravo (ikony s přechodem)."""
    px = im.load()
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        a = np.array(px[x0 - gap, y][:3], float)
        b = np.array(px[x1 + gap, y][:3], float)
        for x in range(x0 - gap + 1, x1 + gap):
            t = (x - x0 + gap) / (x1 - x0 + 2 * gap)
            c = tuple(int(v) for v in a * (1 - t) + b * t)
            px[x, y] = c + ((px[x, y][3],) if im.mode == 'RGBA' else ())


def fit_font(path, text, w, h, size=None):
    """Největší písmo, kterým se text vejde do w × h (výška podle velkých písmen)."""
    s = size or int(h * 1.6)
    while s > 4:
        f = ImageFont.truetype(path, s)
        l, t, r, b = f.getbbox(text)
        if r - l <= w and b - t <= h:
            return f
        s -= 1
    return ImageFont.truetype(path, 5)


def put_text(im, box, text, font, fill, align='c', K=4, valign='c'):
    """Vysází text do obdélníku (K× převzorkování kvůli hladkým hranám malého písma)."""
    x0, y0, x1, y1 = box
    lines = text.split('\n')
    f = ImageFont.truetype(font.path, font.size * K)
    lh = int(f.size * 1.15)
    W, H = (x1 - x0) * K, (y1 - y0) * K
    layer = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(layer)
    total = lh * (len(lines) - 1) + (f.getbbox(lines[-1])[3] - f.getbbox(lines[0])[1])
    y = (H - total) // 2 - f.getbbox(lines[0])[1] if valign == 'c' else -f.getbbox(lines[0])[1]
    for ln in lines:
        l, t, r, b = f.getbbox(ln)
        x = {'c': (W - (r - l)) // 2 - l, 'l': -l, 'r': W - r}[align]
        d.text((x, y), ln, font=f, fill=255)
        y += lh
    layer = layer.resize((x1 - x0, y1 - y0), Image.LANCZOS)
    col = Image.new(im.mode, layer.size, fill if im.mode == 'RGB' else fill + (255,))
    im.paste(col, (x0, y0), layer)


def relabel(im, approx, text, font, fill, bg=None, pad=2, align='c', hmul=1.0, min_w=None):
    """Najde text v přibližné oblasti, vymaže ho (barva pozadí / bílá) a vysází nový ve stejném místě a výšce."""
    tb = tight_box(im, approx)
    x0, y0, x1, y1 = tb
    d = ImageDraw.Draw(im)
    if bg is None:
        bg = tuple(int(v) for v in np.median(np.asarray(im.convert('RGB').crop(approx)).reshape(-1, 3), axis=0))
    d.rectangle((x0 - pad, y0 - pad, x1 + pad, y1 + pad), fill=bg if im.mode == 'RGB' else bg + (255,))
    cx = (x0 + x1) / 2
    w = max(x1 - x0, min_w or 0)
    h = (y1 - y0) * hmul
    lines = text.split('\n')
    fnt = fit_font(font, max(lines, key=len), w, h if len(lines) == 1 else h / len(lines) * 0.8)
    cy = (y0 + y1) / 2
    ya, yb = int(cy - h / 2) - 3, int(cy + h / 2) + 4
    if align == 'l':
        box = (x0, ya, x0 + int(w) + 6, yb)
    else:
        box = (int(cx - w / 2) - 3, ya, int(cx + w / 2) + 3, yb)
    put_text(im, box, text, fnt, fill, align=align)


# ---------------------------------------------------------------- 2) fotky jednotek: nápis na horní liště
def bar_logo(name, box, light=(238, 238, 240), dark=(150, 150, 154)):
    """box = těsný obdélník původního nápisu (POWER WORLD) na liště."""
    im = load(name).convert('RGBA')
    fill_vertical(im, box)
    x0, y0, x1, y1 = box
    K = 8
    cap = (y1 - y0) * K
    font = ImageFont.truetype(EXO, 100)
    font.set_variation_by_axes([900])
    hb = font.getbbox('H')
    size = int(100 * cap / (hb[3] - hb[1]))
    font = ImageFont.truetype(EXO, size)
    font.set_variation_by_axes([900])
    text = 'REO HEATING'
    l, t, r, b = font.getbbox(text)
    mask = Image.new('L', (r - l + 8 * K, b - t + 8 * K), 0)
    ImageDraw.Draw(mask).text((4 * K - l, 4 * K - t), text, font=font, fill=255)
    mask = mask.crop(mask.getbbox())
    mask = mask.resize(((x1 - x0) * K, mask.height), Image.LANCZOS)          # stejná šířka jako původní nápis
    sh = 0.18                                                                   # dodatečný sklon (kurzíva)
    pad = int(mask.height * sh) + 2
    mask = mask.transform((mask.width + pad, mask.height), Image.AFFINE, (1, sh, -pad, 0, 1, 0),
                          resample=Image.BICUBIC)
    mask = mask.resize(((x1 - x0) + pad // K, y1 - y0), Image.LANCZOS)
    w, h = mask.size
    g = np.linspace(0, 1, w)[None, :] * np.ones((h, 1))
    rgb = np.array(light)[None, None, :] * (1 - g[..., None]) + np.array(dark)[None, None, :] * g[..., None]
    layer = Image.fromarray(np.dstack([rgb, np.asarray(mask, float)]).clip(0, 255).astype('uint8'))
    im.alpha_composite(layer, (x0 - pad // K // 2, y0))
    save(im.convert(load(name).mode), name)


bar_logo('image4.png', tight_box(load('image4.png'), (262, 18, 368, 32), 40), (205, 207, 212), (120, 120, 124))
bar_logo('image82.png', tight_box(load('image82.png'), (388, 16, 518, 31), 40), (232, 232, 234), (110, 110, 112))
bar_logo('image86.png', tight_box(load('image86.png'), (510, 12, 645, 28), 40), (232, 232, 234), (110, 110, 112))

# ---------------------------------------------------------------- 3) infografika R290 (image5) – zelená varianta
# velké R290: modrá → zelená (posun odstínu); štítky vpravo: zelené s bílým textem;
# dlaždice dole: bílé pozadí, zelený okraj, piktogram zeleně, popisek černě; modrý pás pod dlaždicemi pryč
GREEN_RGB = (46, 107, 51)
src = load('image5.png').convert('RGB')
px = src.load()
for x in range(175, 236):                       # logo výrobce v obláčku ikony IoT → bílá (= součást obláčku)
    for y in range(383, 397):
        r, g, b = px[x, y]
        if b > r + 25:
            px[x, y] = (255, 255, 255)
# popisky a hodnoty v dlaždicích: vymazat (interpolace podkladu) a vysázet česky bíle → pak se převezmou jako piktogram
for approx, t, fnt in (((440, 405, 522, 425), 'Třída ErP', F['narrowb']), ((580, 405, 663, 426), 'Výstup vody', F['narrowb']),
                       ((718, 405, 800, 428), 'Nízký hluk', F['narrowb']), ((595, 362, 634, 401), '75', F['narrowb']),
                       ((855, 345, 935, 392), '5,0', F['narrowb'])):
    tb = tight_box(src, approx, 150)
    x0, y0, x1, y1 = tb
    fill_horizontal(src, (x0 - 1, y0 - 1, x1 + 1, y1 + 1), gap=2)
    f = fit_font(fnt, t, x1 - x0 + 4, y1 - y0)
    put_text(src, (x0 - 6, y0 - 3, x1 + 6, y1 + 4), t, f, (255, 255, 255))
a = np.asarray(src).astype(float)
a_src = a
W5, H5 = src.size
out = np.full_like(a, 255.0)
# a) velké R290 (x < 900, y < 300): modré pixely → zelené se zachovaným jasem (stín zůstane tmavší)
reg = a[:300, :900]
mx, mn = reg.max(2), reg.min(2)
blue = (reg[..., 2] > reg[..., 0] + 40) & (mx > 40)
lum = 0.3 * reg[..., 0] + 0.59 * reg[..., 1] + 0.11 * reg[..., 2]          # jas původní modré
k = np.clip(lum / 110.0, 0.25, 1.35)[..., None]
green = np.array([52, 130, 58], float)[None, None, :] * k
alpha = np.clip((reg[..., 2] - reg[..., 0] - 20) / 60.0, 0, 1)[..., None]   # vyhlazené hrany písmen
out[:300, :900] = np.where(blue[..., None], green * alpha + 255 * (1 - alpha), 255)
img = Image.fromarray(out.clip(0, 255).astype('uint8'))
d = ImageDraw.Draw(img)
# b) štítky vpravo
for (y0, y1), t in zip(((30, 101), (117, 187), (204, 273)), ('VYTÁPĚNÍ', 'CHLAZENÍ', 'TUV')):
    d.rounded_rectangle((948, y0, 1182, y1), radius=8, fill=GREEN_RGB)
    f = fit_font(F['arial'], t, 200, 26)
    put_text(img, (948, y0, 1182, y1), t, f, (255, 255, 255))
# c) dlaždice
TILES = [(14, 117), (152, 256), (291, 394), (429, 533), (569, 673), (706, 810), (844, 948), (985, 1090), (1120, 1223)]
TY0, TY1 = 333, 440
LABELS = ['WI-FI', 'IoT', 'TEPELNÉ ČERPADLO', 'Třída ErP', 'Výstup vody', 'Nízký hluk', 'COP', None, None]
for (x0, x1), lab in zip(TILES, LABELS):
    t = a_src[TY0 + 6:TY1 - 5, x0 + 6:x1 - 5]
    tmx, tmn = t.max(2), t.min(2)
    sat = (tmx - tmn) / np.maximum(tmx, 1)
    glyph = (tmn > 175) & (sat < 0.16)                     # bílé písmo a piktogramy na barevném podkladu
    m = Image.fromarray((glyph * 255).astype('uint8'))
    d.rounded_rectangle((x0, TY0, x1, TY1), radius=14, fill=(255, 255, 255), outline=GREEN_RGB, width=4)
    if lab:                                                 # piktogram zeleně, popisek nově černě
        split = int(m.height * 0.66)
        top = Image.new('L', m.size, 0)
        top.paste(m.crop((0, 0, m.width, split)), (0, 0))
        img.paste(Image.new('RGB', m.size, GREEN_RGB), (x0 + 6, TY0 + 6), top)
        f = fit_font(F['arialb'], lab, x1 - x0 - 18, 15)
        put_text(img, (x0 + 5, TY0 + 6 + split, x1 - 5, TY1 - 6), lab, f, (25, 25, 25))
    else:                                                   # SG Ready, PV-Ready: celé logo zeleně
        img.paste(Image.new('RGB', m.size, GREEN_RGB), (x0 + 6, TY0 + 6), m)
d.rectangle((582, 352, 634, 404), fill=(255, 255, 255))        # „75“ výrazněji (původní 85 bylo tučné)
put_text(img, (578, 352, 638, 404), '75', ImageFont.truetype(F['arialb'], 38), GREEN_RGB)
save(img, 'image5.png')

# ---------------------------------------------------------------- 4) tabulka ikon ovladače (image34)
im = load('image34.png').convert('RGB')
a = np.asarray(im).astype(int).sum(2)
dark = a < 200
rows = [y for y in range(im.height) if dark[y].mean() > 0.7]
hdr = dark[rows[0] + 3 if rows[0] < 5 else 2:(rows[1] if rows[0] < 5 else rows[0]) - 2]   # záhlaví bez ikon
cols = [x for x in range(im.width) if hdr[:, x].mean() > 0.9]


def spans(lines, n):
    """Mezi sousedními čarami (shluky) → intervaly buněk."""
    groups = []
    for v in lines:
        if groups and v - groups[-1][-1] <= 2:
            groups[-1].append(v)
        else:
            groups.append([v])
    edges = [(g[0], g[-1]) for g in groups]
    if edges[0][0] > 3:
        edges.insert(0, (0, 0))
    if edges[-1][1] < n - 4:
        edges.append((n - 1, n - 1))
    return [(edges[i][1] + 1, edges[i + 1][0]) for i in range(len(edges) - 1)]


R, C = spans(rows, im.height), spans(cols, im.width)
LEFT = ['Vytápění', 'Ohřev TUV', 'Chlazení', 'Radiátor', 'Podlahové\nvytápění', 'Radiátor', 'Kompresor']
RIGHT = ['Režim\ndovolená', 'Tichý režim', 'Levná\nelektřina', 'Chod oběh.\nčerpadla', 'Externí\nzdroj tepla',
         'Porucha', 'Časovač']
d = ImageDraw.Draw(im)
for ci, data in ((1, ['Význam'] + LEFT), (3, ['Význam'] + RIGHT), (0, ['Ikona']), (2, ['Ikona'])):
    for ri, t in enumerate(data):
        (x0, x1), (y0, y1) = C[ci], R[ri]
        d.rectangle((x0 + 1, y0 + 1, x1 - 1, y1 - 1), fill=(255, 255, 255))
        bold = ri == 0
        f = ImageFont.truetype(SUP + ('Times New Roman Bold.ttf' if bold else 'Times New Roman.ttf'), 17)
        put_text(im, (x0 + 2, y0 + 1, x1 - 2, y1 - 1), t, f, (0, 0, 0))
save(im, 'image34.png')

# ---------------------------------------------------------------- 5) legenda hydraulického schématu (image29)
im = load('image29.png').convert('RGB')
a = np.asarray(im).astype(int).sum(2) < 200
rows = [y for y in range(im.height) if a[y].mean() > 0.7]
cols = [x for x in range(im.width) if a[:, x].mean() > 0.7]
R, C = spans(rows, im.height), spans(cols, im.width)
NAMES = ['Odvzdušňovací ventil', 'Pojistný ventil', 'Manometr', 'Teploměr', 'Rozdělovač', 'Trojcestný ventil',
         'Pryžová spojka', 'Dvoucestný ventil', 'Filtr Y', 'Kulový kohout', 'Oběhové čerpadlo', 'Zpětný ventil']
d = ImageDraw.Draw(im)
f = fit_font(F['arial'], 'Odvzdušňovací ventil', C[1][1] - C[1][0] - 10, 30)
f = ImageFont.truetype(F['arial'], min(f.size, 20))
for ri, t in enumerate(NAMES):
    (x0, x1), (y0, y1) = C[1], R[ri]
    d.rectangle((x0 + 1, y0 + 1, x1 - 1, y1 - 1), fill=(255, 255, 255))
    put_text(im, (x0 + 2, y0 + 1, x1 - 2, y1 - 1), t, f, (0, 0, 0))
save(im, 'image29.png')

# ---------------------------------------------------------------- 6) Modbus (image84, image85)
im = load('image84.png').convert('RGB')
W, H = im.size
G = (40, 40, 40)
for approx, t, *mw in (((40, 195, 200, 230), 'Řídicí systém', 150, 1.45), ((180, 40, 340, 90), 'Požadavek\nčtení / zápis'),
                  ((180, 205, 340, 235), 'Odpověď'), ((260, 430, 470, 470), 'Zařízení 1'),
                  ((470, 430, 680, 470), 'Zařízení 2'), ((680, 430, 890, 470), 'Zařízení 3')):
    relabel(im, approx, t, F['arial'], G, bg=(255, 255, 255), min_w=mw[0] if mw else 0,
            hmul=mw[1] if len(mw) > 1 else 1.0)
save(im, 'image84.png')
im = load('image85.jpeg').convert('RGB')
for approx, t, *mw in (((620, 138, 730, 172), 'Počítač'), ((85, 280, 200, 315), 'Monoblok'),
                       ((85, 425, 200, 460), 'Split'), ((278, 342, 326, 372), 'NEBO', 50),
                       ((438, 342, 488, 372), 'NEBO', 50), ((598, 342, 648, 372), 'NEBO', 50)):
    relabel(im, approx, t, F['arialb'], (60, 60, 60), bg=(255, 255, 255), min_w=mw[0] if mw else 0)
save(im, 'image85.jpeg')

# ---------------------------------------------------------------- 7) schéma SG (image23)
im = load('image23.png').convert('RGBA')
bgw = (255, 255, 255)
rgb = im.convert('RGB')
for approx, t in (((236, 258, 410, 322), 'Pozor: 230 V\nNedotýkat se'), ((440, 245, 610, 275), 'Kabel od sítě')):
    tb = tight_box(rgb, approx, 200)
    x0, y0, x1, y1 = tb
    ImageDraw.Draw(im).rectangle((x0 - 1, y0 - 1, x1 + 1, y1 + 1), fill=bgw + (255,))
    lines = t.split('\n')
    f = fit_font(F['arial'], max(lines, key=len), x1 - x0 + 10, (y1 - y0) / len(lines) * 0.78)
    put_text(im, (x0 - 6, y0 - 2, x1 + 8, y1 + 3), t, f, (20, 20, 20))
save(im, 'image23.png')

# ---------------------------------------------------------------- 8) hydraulické schéma aplikace (image30)
im = load('image30.png').convert('RGB')
for approx, t in (((115, 90, 390, 150), 'Napájení'), ((445, 115, 625, 185), 'Kotel'),
                  ((200, 30, 430, 68), 'Přívod studené vody')):
    relabel(im, approx, t, F['times'], (60, 60, 60), bg=(255, 255, 255), min_w=0)
for approx, t, col, fnt in (((248, 316, 334, 362), 'Stykač\nAC', (110, 110, 110), F['times']),
                            ((490, 314, 660, 344), 'Svorkovnice', (40, 230, 40), SUP + 'Courier New.ttf')):
    relabel(im, approx, t, fnt, col, bg=(255, 255, 255), min_w=0)
save(im, 'image30.png')

# ---------------------------------------------------------------- 9) náhled IoT portálu (image83): název zařízení zákazníka
im = load('image83.png').convert('RGB')
ImageDraw.Draw(im).rectangle((68, 22, 295, 58), fill=(255, 255, 255))
save(im, 'image83.png')
print('ok', sorted(os.listdir(OUT)))
