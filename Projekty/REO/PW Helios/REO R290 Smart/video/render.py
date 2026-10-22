"""Rebrand videa REO R290 Smart: snímek po snímku nahradí logo, titulky a infografiky (CZ).
Použití: python render.py <scratch> [--preview t1,t2,...]"""
import sys, os, subprocess, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = sys.argv[1]
FF = f"{S}/ffmpeg"
SRC = f"{S}/src/in.mp4"
ST = f"{S}/still"
# logo REO HEATING (závazné od 22. 10. 2026, kopie z ~/Claude/REO/logo/logo-reo-heating.png)
LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo-reo-heating.png")
W, H = 1920, 1080
FPS = 60000 / 1001
AV = "/System/Library/Fonts/Avenir Next.ttc"
IDX = {"bold": 0, "demi": 2, "medium": 5, "regular": 7, "heavy": 8, "demiit": 3, "boldit": 1}
_fc = {}


def F(w, size):
    k = (w, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(AV, size, index=IDX[w])
    return _fc[k]


GREEN = (92, 168, 64)
BLUE = (30, 136, 208)


def ramp(t, t0, t1, fi=0.25, fo=0.25):
    if t < t0 or t > t1:
        return 0.0
    a = 1.0
    if fi > 0:
        a = min(a, (t - t0) / fi)
    if fo > 0:
        a = min(a, (t1 - t) / fo)
    return max(0.0, min(1.0, a))


def still(t):
    return Image.open(f"{ST}/s{t}.png").convert("RGB")


def tw(text, font):
    b = font.getbbox(text)
    return b[2] - b[0]


def text(d, xy, s, font, fill, anchor="la", shadow=None):
    if shadow:
        x, y = xy
        d.text((x + 2, y + 2), s, font=font, fill=shadow, anchor=anchor)
    d.text(xy, s, font=font, fill=fill, anchor=anchor)


def inpaint_cols(img, box, pad=3):
    """vyplní obdélník lineární interpolací mezi řádkem nad a pod (hladká pozadí)"""
    a = np.asarray(img).astype(float).copy()
    x0, y0, x1, y1 = box
    top = a[y0 - pad, x0:x1]
    bot = a[y1 + pad, x0:x1]
    n = y1 - y0
    for i in range(n):
        f = i / max(1, n - 1)
        a[y0 + i, x0:x1] = top * (1 - f) + bot * f
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def inpaint_rows(img, box, pad=3):
    a = np.asarray(img).astype(float).copy()
    x0, y0, x1, y1 = box
    l = a[y0:y1, x0 - pad]
    r = a[y0:y1, x1 + pad]
    n = x1 - x0
    for i in range(n):
        f = i / max(1, n - 1)
        a[y0:y1, x0 + i] = l * (1 - f) + r * f
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def rrect_mask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255)
    return m


def zoom(img, z):
    if abs(z - 1) < 1e-4:
        return img
    w, h = img.size
    nw, nh = int(w * z), int(h * z)
    big = img.resize((nw, nh), Image.BILINEAR)
    l, t = (nw - w) // 2, (nh - h) // 2
    return big.crop((l, t, l + w, t + h))


def paste_a(base, layer, alpha, xy=(0, 0)):
    """vloží RGBA vrstvu s globální průhledností"""
    if alpha <= 0:
        return base
    if alpha < 1:
        l = layer.copy()
        l.putalpha(l.getchannel("A").point(lambda v: int(v * alpha)))
        layer = l
    base.paste(layer, xy, layer)
    return base


# ---------------------------------------------------------------- logo
logo = Image.open(LOGO).convert("RGBA")
logo = logo.crop(logo.getbbox())                       # bez průhledného okraje
LH = 90
logo_s = logo.resize((int(logo.width * LH / logo.height), LH), Image.LANCZOS)
PL = (34, 26, 34 + max(334, logo_s.width + 40), 138)  # deska přes logo výrobce (45–355 × 40–125)
plate = Image.new("RGBA", (PL[2] - PL[0], PL[3] - PL[1]), (0, 0, 0, 0))
pm = rrect_mask(*plate.size, 18)
white = Image.new("RGBA", plate.size, (255, 255, 255, 255))
plate.paste(white, (0, 0), pm)
plate.alpha_composite(logo_s, ((plate.width - logo_s.width) // 2, (plate.height - logo_s.height) // 2))
shadow = Image.new("RGBA", (plate.width + 40, plate.height + 40), (0, 0, 0, 0))
sm = Image.new("L", shadow.size, 0)
sm.paste(pm.point(lambda v: v * 70 // 255), (20, 24))
shadow.putalpha(sm.filter(ImageFilter.GaussianBlur(10)))
LOGO_LAYER = Image.new("RGBA", (plate.width + 40, plate.height + 40), (0, 0, 0, 0))
LOGO_LAYER.alpha_composite(shadow)
LOGO_LAYER.alpha_composite(plate, (20, 20))
LOGO_XY = (PL[0] - 20, PL[1] - 20)

# ---------------------------------------------------------------- titulky (spodní lišta)
CAPS = [
    # (od, do, titulek, podtitulek, pravý okraj originálu)
    (0.0, 4.15, "REO R290 Smart", "Tepelné čerpadlo vzduch–voda · REO HEATING", 900),
    (4.15, 9.95, "Integrovaný záložní dohřev 3 kW", "a pojistná výbava přímo v jednotce", 730),
    (9.95, 15.2, "Design bez viditelných šroubů", None, 570),
    (18.13, 21.45, "Přírodní chladivo R290 · GWP 3", None, 690),
    (21.45, 31.15, "Energetická třída A+++", "SCOP až 5,29 (35 °C)", 1070),
    (31.15, 34.6, "Výstupní voda až 75 °C", None, 680),
    (34.6, 37.5, "Inteligentní odtávání", None, 630),
    (37.5, 43.1, "6stupňové odhlučnění", "od 35 dB(A) ve vzdálenosti 1 m", 690),
    (43.1, 53.65, "Kompresor Mitsubishi Electric", "Řídicí deska ovládá čerpadla, ventily i další zdroje tepla", 570),
    (53.65, 59.55, "Snadná instalace i servis", None, 830),
    (59.55, 65.15, "Chytré ovládání přes aplikaci", "Dálková regulace a automatický provoz", 700),
    (65.15, 72.05, "Regulace tří teplotních zón", None, 890),
    (72.05, 79.45, "Dvoustupňová ochrana proti úniku chladiva", None, 760),
    (79.45, 83.6, "Kaskáda až 8 jednotek", None, 660),
    (83.6, 90.1, "8 přednastavených + 1 vlastní ekvitermní křivka", None, 1045),
    (90.1, 93.85, "Topí přímo ze sluníčka", "Fotovoltaika připojená přímo k jednotce", 690),
    (93.85, 100.3, "Topí přímo ze sluníčka", "Co sluníčko nepokryje, doplní síť", 985),
    (100.3, 105.72, "REO R290 Smart: účinné, tiché a chytré", "Topí přímo ze sluníčka.", 1275),
]
CY0, CY1, CX0 = 860, 990, 128


def caption_layer(title, sub, right):
    ft, fs = F("demi", 46), F("medium", 29)
    w = tw(title, ft)
    if sub:
        w = max(w, tw(sub, fs))
    pw = max(w + 92, right - CX0 + 40)
    ph = CY1 - CY0
    lay = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, 9, ph - 1), 4, fill=GREEN + (255,))
    if sub:
        text(d, (40, 26), title, ft, (255, 255, 255), shadow=(0, 0, 0))
        text(d, (41, 82), sub, fs, (214, 236, 205), shadow=(0, 0, 0))
    else:
        text(d, (40, ph // 2), title, ft, (255, 255, 255), anchor="lm", shadow=(0, 0, 0))
    return lay, pw


CAP_LAYERS = [caption_layer(c[2], c[3], c[4]) for c in CAPS]


def frosted(frame, box, r=16, dark=150, blur=14):
    x0, y0, x1, y1 = box
    reg = frame.crop(box)
    sm = reg.resize((max(1, reg.width // 6), max(1, reg.height // 6)), Image.BILINEAR)
    sm = sm.filter(ImageFilter.GaussianBlur(blur / 6)).resize(reg.size, Image.BILINEAR)
    sm = Image.blend(sm, Image.new("RGB", reg.size, (12, 18, 14)), dark / 255)
    return sm, rrect_mask(reg.width, reg.height, r)


TALL = {"Energetická třída A+++", "Výstupní voda až 75 °C"}


def draw_caption(frame, t):
    for (t0, t1, title, *_), (lay, pw) in zip(CAPS, CAP_LAYERS):
        a = ramp(t, t0 - 0.12, t1 + 0.12, 0.2, 0.2)
        if a <= 0:
            continue
        top = 806 if title in TALL else CY0
        box = (CX0, top, CX0 + pw, CY1)
        fr, m = frosted(frame, box)
        if a < 1:
            m = m.point(lambda v: int(v * a))
        frame.paste(fr, box[:2], m)
        paste_a(frame, lay, a, (CX0, CY0))


# ---------------------------------------------------------------- vzorník panelů (10–15 s)
def swatch_img(w, h):
    im = Image.new("RGB", (w, h), (24, 25, 27))
    d = ImageDraw.Draw(im)
    for y in range(6, h - 4, 7):
        d.line((6, y, w - 7, y), fill=(44, 46, 49), width=3)
    m = rrect_mask(w, h, 4)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(im, (0, 0), m)
    return out


SW = [(198, 338, 336, 447), (352, 338, 495, 447)]
SW_LAYERS = [swatch_img(b[2] - b[0], b[3] - b[1]) for b in SW]
PANEL_BOX = (188, 612, 820, 742)


def panel_text_layer():
    lay = Image.new("RGBA", (PANEL_BOX[2] - PANEL_BOX[0], PANEL_BOX[3] - PANEL_BOX[1]), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    text(d, (28, 22), "Různé varianty panelů", F("demi", 38), (255, 255, 255), shadow=(0, 0, 0))
    text(d, (28, 70), "s možností přizpůsobení", F("demi", 38), (255, 255, 255), shadow=(0, 0, 0))
    return lay


PANEL_LAYER = panel_text_layer()


def draw_swatches(frame, t):
    a = ramp(t, 9.95, 15.2, 0.3, 0.05)
    if a <= 0:
        return
    for b, l in zip(SW, SW_LAYERS):
        paste_a(frame, l, a, b[:2])
    fr, m = frosted(frame, PANEL_BOX, dark=120)
    m = m.point(lambda v: int(v * a))
    frame.paste(fr, PANEL_BOX[:2], m)
    paste_a(frame, PANEL_LAYER, a, PANEL_BOX[:2])


# ---------------------------------------------------------------- nápis na horní liště jednotky (68.4–71.94)
def topbar_layer():
    s = still(69.5)
    box = (725, 196, 900, 258)
    patch = s.crop(box)
    a = np.asarray(patch).astype(float)
    # text je světle šedý na černé liště → nahradit tmavou barvou lišty
    lum = a.mean(axis=2)
    base = np.median(a[lum < 60], axis=0)
    mask = (lum > 70)
    mimg = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.5))
    fill = Image.new("RGB", patch.size, tuple(int(v) for v in base))
    patch.paste(fill, (0, 0), mimg)
    # nový nápis REO HEATING (jen text — úzká horní lišta)
    txt = Image.new("RGBA", (260, 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(txt)
    d.text((130, 30), "REO HEATING", font=F("boldit", 22), fill=(150, 152, 156, 255), anchor="mm")
    txt = txt.rotate(4.5, resample=Image.BICUBIC, center=(130, 30))
    out = patch.convert("RGBA")
    out.alpha_composite(txt, (box[2] - box[0]) // 2 - 130 + 2 and (0, 0) or (0, 0))
    return out, box


def _topbar():
    s = still(69.5)
    box = (725, 196, 900, 258)
    patch = s.crop(box)
    a = np.asarray(patch).astype(float)
    lum = a.mean(axis=2)
    base = np.median(a[lum < 60], axis=0)
    mimg = Image.fromarray(((lum > 70) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.5))
    patch.paste(Image.new("RGB", patch.size, tuple(int(v) for v in base)), (0, 0), mimg)
    out = patch.convert("RGBA")
    txt = Image.new("RGBA", out.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(txt)
    d.text((out.width // 2 + 4, out.height // 2 - 1), "REO HEATING", font=F("boldit", 21), fill=(158, 160, 164, 255), anchor="mm")
    txt = txt.rotate(4.0, resample=Image.BICUBIC)
    out.alpha_composite(txt)
    return out, box


TOPBAR, TOPBAR_BOX = _topbar()


def draw_topbar(frame, t):
    if 68.40 <= t < 71.95:
        frame.paste(TOPBAR, TOPBAR_BOX[:2], TOPBAR)


# ---------------------------------------------------------------- popisky přípojek (49–53.65), sledování polohy
TRACK = json.load(open(f"{S}/build/track.json")) if os.path.exists(f"{S}/build/track.json") else {}


def interp_box(key, t):
    pts = TRACK.get(key)
    if not pts:
        return None
    ts = [p[0] for p in pts]
    if t < ts[0] - 0.9 or t > ts[-1] + 0.05:
        return None
    t = min(max(t, ts[0]), ts[-1])
    for (ta, *ba), (tb, *bb) in zip(pts, pts[1:]):
        if ta <= t <= tb:
            f = (t - ta) / max(1e-6, tb - ta)
            return [ba[i] * (1 - f) + bb[i] * f for i in range(4)] + [ba[4] * (1 - f) + bb[4] * f]
    p = pts[0] if t <= ts[0] else pts[-1]
    return list(p[1:5]) + [0.0 if t < ts[0] else p[5]]


def draw_ports(frame, t):
    for key, lines in (("left", ["Kabelové průchodky"]), ("right", ["Výstup vody", "Vstup vody"])):
        b = interp_box(key, t)
        if not b:
            continue
        x0, y0, x1, y1, alpha = b
        box = (int(x0) - 8, int(y0) - 6, int(x1) + 8, int(y1) + 6)
        frame.paste(inpaint_cols(frame, box, 2).crop(box), box[:2])
        if alpha <= 0.05:
            continue
        lh = (y1 - y0) / len(lines)
        fnt = F("demi", int(lh * 0.86))
        lay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        for i, s in enumerate(lines):
            if key == "left":
                d.text((x1, y0 + lh * (i + 0.5)), s, font=fnt, fill=BLUE + (255,), anchor="rm")
            else:
                d.text((x0, y0 + lh * (i + 0.5)), s, font=fnt, fill=(120, 190, 240, 255), anchor="lm")
        paste_a(frame, lay, min(1, alpha))


# ---------------------------------------------------------------- PROČ R290 (15.2–18.13)
def why_layer():
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    # šipka
    ar = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ar).polygon([(822, 445), (1062, 445), (1062, 740), (1190, 740), (942, 1005), (694, 740), (822, 740)], fill=(0, 225, 245, 150))
    lay.alpha_composite(ar)
    sh = (0, 40, 60)
    text(d, (W // 2, 250), "PROČ R290?", F("heavy", 150), (255, 255, 255), "mm", sh)
    text(d, (W // 2, 362), "Lepší volba pro váš domov", F("demi", 44), (255, 255, 255), "mm", sh)
    L, R = 380, 1515
    text(d, (L, 500), "Snížení GWP", F("demi", 72), (255, 255, 255), "mm", sh)
    text(d, (L, 580), "(potenciálu globálního oteplování)", F("medium", 32), (255, 255, 255), "mm", sh)
    text(d, (L, 700), "o 672", F("bold", 110), (255, 255, 255), "mm", sh)
    text(d, (L, 830), "oproti chladivu R32", F("medium", 40), (255, 255, 255), "mm", sh)
    text(d, (R, 500), "Volba R290", F("demi", 72), (255, 255, 255), "mm", sh)
    text(d, (R, 580), "pro tepelné čerpadlo", F("medium", 36), (255, 255, 255), "mm", sh)
    text(d, (R, 700), "99,7 %", F("bold", 110), (255, 255, 255), "mm", sh)
    text(d, (R, 815), "menší dopad", F("medium", 40), (255, 255, 255), "mm", sh)
    text(d, (R, 863), "na globální oteplování", F("medium", 40), (255, 255, 255), "mm", sh)
    return lay


WHY = why_layer()


def draw_why(frame, t):
    a = ramp(t, 15.2, 18.13, 0.08, 0.0)
    if a <= 0:
        return frame
    sm = frame.resize((W // 10, H // 10), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2)).resize((W, H), Image.BILINEAR)
    sm = Image.blend(sm, Image.new("RGB", (W, H), (5, 40, 55)), 0.25)
    out = Image.blend(frame, sm, a)
    return paste_a(out, WHY, a)


# ---------------------------------------------------------------- únik chladiva (72.05–79.45), pravá část
def leak_layers():
    base = still(72.3)
    full = still(78.9)
    right = base.crop((560, 0, W, H)).convert("RGBA")
    m = Image.new("L", right.size, 0)
    dm = ImageDraw.Draw(m)
    dm.rectangle((780 - 560, 0, right.width, right.height), fill=255)
    dm.rectangle((655 - 560, 640, right.width, 990), fill=255)
    right.putalpha(m.filter(ImageFilter.GaussianBlur(14)))
    sq = []
    for bx in [(760, 170, 1125, 535), (1365, 170, 1730, 535)]:
        c = full.crop(bx).convert("RGBA")
        m = Image.new("L", c.size, 0)
        ImageDraw.Draw(m).rounded_rectangle((6, 6, c.width - 7, c.height - 7), 30, fill=255)
        c.putalpha(m.filter(ImageFilter.GaussianBlur(3)))
        sq.append((c, bx[:2]))
    t1 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    t2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ft, fb = F("demi", 36), F("medium", 31)
    d = ImageDraw.Draw(t1)
    d.text((942, 573), "SNÍMAČ ÚNIKU CHLADIVA", font=ft, fill=(255, 255, 255), anchor="mm")
    # první řádek s barevným „15 % LFL“
    parts = [("Při ", (235, 235, 235)), ("15 % LFL", (255, 222, 0)), (" spustí alarm,", (235, 235, 235))]
    tot = sum(tw(p, fb) for p, _ in parts)
    x = 942 - tot / 2
    for p, c in parts:
        d.text((x, 662), p, font=fb, fill=c, anchor="lm")
        x += tw(p, fb) + (8 if p.endswith(" ") else 0) * 0
    for i, s in enumerate(["automaticky zastaví klíčové", "komponenty a ponechá", "minimální větrání."]):
        d.text((942, 712 + i * 50), s, font=fb, fill=(235, 235, 235), anchor="mm")
    d = ImageDraw.Draw(t2)
    d.text((1548, 573), "ODVZDUŠŇOVACÍ VENTIL", font=ft, fill=(255, 255, 255), anchor="mm")
    for i, s in enumerate(["Automaticky vypustí chladivo,", "které by proniklo do vodního okruhu,", "aby se nedostalo do místnosti;", "provoz zůstává bezpečný."]):
        d.text((1548, 662 + i * 50), s, font=fb, fill=(235, 235, 235), anchor="mm")
    return right, sq, t1, t2


LEAK = leak_layers()


LEAK_CACHE = {}


def draw_leak(frame, t):
    if 78.78 <= t < 79.27 and "f" in LEAK_CACHE:
        # vlastní přechod: přiblížení na ventil místo originálu s anglickým textem
        f = (t - 78.78) / 0.49
        z = 1 + 1.4 * f * f
        c = LEAK_CACHE["f"]
        cx, cy = 1548, 420
        w, h = W / z, H / z
        l = min(max(cx - w / 2, 0), W - w)
        tp = min(max(cy - h / 2, 0), H - h)
        frame.paste(c.crop((int(l), int(tp), int(l + w), int(tp + h))).resize((W, H), Image.BILINEAR))
        return
    if not (72.05 <= t < 79.45):
        return
    right, sq, t1, t2 = LEAK
    z = 1 + 0.02 * (t - 72.05) / 7.4
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lay.alpha_composite(right, (560, 0))
    a1 = ramp(t, 72.55, 99, 0.45, 0)
    a2 = ramp(t, 73.55, 99, 0.45, 0)
    for (c, xy), a in zip(sq, (a1, a2)):
        paste_a(lay, c, a, xy)
    paste_a(lay, t1, ramp(t, 72.8, 99, 0.4, 0))
    paste_a(lay, t2, ramp(t, 73.8, 99, 0.4, 0))
    lay = zoom(lay, z)
    frame.paste(lay, (0, 0), lay)
    if t < 78.78:
        LEAK_CACHE["f"] = frame.copy()


# ---------------------------------------------------------------- ekvitermní křivky (83.6–90.1)
def curves_layers():
    s = still(89.5)
    base = inpaint_cols(s, (190, 260, 1800, 1000), 6)
    chart = s.crop((205, 275, 1025, 800))
    cx, cy = 205, 275
    for b in [(380, 300, 850, 340), (625, 732, 935, 772), (884, 425, 935, 632)]:
        bb = (b[0] - cx, b[1] - cy, b[2] - cx, b[3] - cy)
        chart = inpaint_cols(chart, bb, 3)
    d = ImageDraw.Draw(chart)
    d.text((615 - cx, 320 - cy), "Vysokoteplotní křivky – vytápění, režim 1", font=F("medium", 27), fill=(235, 235, 235), anchor="mm")
    d.text((928 - cx, 752 - cy), "Venkovní teplota (°C)", font=F("medium", 26), fill=(235, 235, 235), anchor="rm")
    for i in range(8):
        d.text((888 - cx, 435 + i * 26.8 - cy), f"Křivka {i + 1}", font=F("regular", 12), fill=(220, 220, 220), anchor="lm")
    chart = chart.convert("RGBA")
    pills = []
    texts = [["8 přednastavených + 1 vlastní", "křivka pro topení i chlazení"], ["Automaticky upraví cílovou", "teplotu vody"], ["Pro každé místní klima"]]
    for (y0, y1), lines in zip([(320, 460), (470, 608), (618, 756)], texts):
        p = s.crop((1130, y0, 1770, y1))
        yy0, yy1 = 18, p.height - 18
        p = inpaint_rows(p, (1272 - 1130, yy0 + 8, 1712 - 1130, yy1 - 8), 2)
        pa = p.convert("RGBA")
        d = ImageDraw.Draw(pa)
        fnt = F("medium", 31)
        mid = p.height / 2
        for i, l in enumerate(lines):
            d.text((1284 - 1130, mid + (i - (len(lines) - 1) / 2) * 43), l, font=fnt, fill=(255, 255, 255), anchor="lm")
        m = Image.new("L", p.size, 255)
        g = np.ones((p.height, p.width))
        g[:, :12] = np.linspace(0, 1, 12)
        g[:, -12:] = np.linspace(1, 0, 12)
        pa.putalpha(Image.fromarray((g * 255).astype(np.uint8)))
        pills.append((pa, (1130, y0)))
    return base, chart, (cx, cy), pills


CURVES = curves_layers()


def draw_curves(frame, t):
    if not (83.6 <= t < 90.1):
        return frame
    base, chart, cxy, pills = CURVES
    lay = base.convert("RGBA")
    paste_a(lay, chart, ramp(t, 83.7, 99, 0.4, 0), cxy)
    for (p, xy), ts in zip(pills, (84.7, 85.7, 86.7)):
        paste_a(lay, p, ramp(t, ts, 99, 0.4, 0), xy)
    lay = zoom(lay.convert("RGB"), 1 + 0.03 * (t - 83.6) / 6.5)
    a = ramp(t, 83.6, 90.1, 0.15, 0)
    return Image.blend(frame, lay, a)


# ---------------------------------------------------------------- FV schéma (90.1–93.85)
def pv_layer():
    s = still(91.5)
    a = np.asarray(s).astype(float)
    # bílé pozadí — vymazat anglické texty (seznam, štítky)
    wipe = [(340, 200, 790, 840), (1225, 290, 1555, 345)]
    im = s.copy()
    d = ImageDraw.Draw(im)
    for b in wipe:
        d.rectangle(b, fill=(255, 255, 255))
    # šikmé štítky: maska modrého písma v pásu podél textu
    arr = np.asarray(im).astype(int)
    yy, xx = np.mgrid[0:H, 0:W]
    tot = np.zeros((H, W), bool)
    for (xa, ya), (xb, yb), th in [((1072, 192), (1182, 252), 22), ((1668, 552), (1778, 616), 22), ((1030, 748), (1232, 866), 30)]:
        dx, dy = xb - xa, yb - ya
        L = (dx * dx + dy * dy) ** 0.5
        u = ((xx - xa) * dx + (yy - ya) * dy) / L
        v = np.abs((xx - xa) * dy - (yy - ya) * dx) / L
        tot |= (u > -6) & (u < L + 6) & (v < th)
    blue = (arr[..., 2] - arr[..., 0] > 60) & (arr[..., 0] < 120)
    mm = Image.fromarray(((tot & blue) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))
    im.paste(Image.new("RGB", (W, H), (255, 255, 255)), (0, 0), mm)
    d = ImageDraw.Draw(im)
    items = [("TOPÍ ZE SLUNÍČKA", "Energie z panelů pohání", "přímo kompresor"),
             ("NIŽŠÍ ÚČTY", "Méně elektřiny", "odebrané ze sítě"),
             ("ČISTÁ ENERGIE", "Menší uhlíková stopa", "díky sluníčku"),
             ("SNADNÉ PŘIPOJENÍ", "Panely přímo k jednotce,", "bez střídače a baterie")]
    for i, (h, l1, l2) in enumerate(items):
        y = 228 + i * 163.5
        d.text((354, y), h, font=F("demi", 30), fill=BLUE, anchor="lm")
        d.text((356, y + 50), l1, font=F("medium", 27), fill=(40, 140, 210), anchor="lm")
        d.text((356, y + 86), l2, font=F("medium", 27), fill=(40, 140, 210), anchor="lm")
    d.text((1238, 318), "REO R290 Smart", font=F("demi", 32), fill=BLUE, anchor="lm")

    def rot(s_, ang, xy, size=22):
        t_ = Image.new("RGBA", (440, 240), (0, 0, 0, 0))
        ImageDraw.Draw(t_).text((220, 120), s_, font=F("demi", size), fill=BLUE + (255,), anchor="mm")
        t_ = t_.rotate(ang, resample=Image.BICUBIC)
        im.paste(t_, (xy[0] - 220, xy[1] - 120), t_)
    rot("FV panely", -27, (1128, 222))
    rot("Rozvodná síť", -24, (1724, 586))
    rot("DŮM A BAZÉN", -30, (1128, 803), 30)
    return im


PV = pv_layer()


def draw_pv(frame, t):
    if not (90.1 <= t < 93.95):
        return frame
    lay = zoom(PV, 1 + 0.02 * (t - 90.1) / 3.8)
    a = ramp(t, 90.1, 93.95, 0.3, 0.4)
    return Image.blend(frame, lay, a)


# ---------------------------------------------------------------- řízení odběru (93.85–100.3)
def grid_layer():
    s = still(97)
    im = s
    for b in [(170, 355, 625, 470), (240, 630, 625, 712), (1255, 355, 1720, 470), (1255, 630, 1720, 745), (195, 880, 1000, 945)]:
        im = inpaint_cols(im, b, 4)
    d = ImageDraw.Draw(im)
    hf, bf = F("demi", 29), F("medium", 26)
    blocks = [((612, 372), "rs", "SMART GRID READY", ["Reaguje na signály", "distribuční sítě"]),
              ((1270, 372), "ls", "DOPLNĚNÍ ZE SÍTĚ", ["Co sluníčko nepokryje,", "vezme jednotka ze sítě"]),
              ((612, 650), "rs", "NIŽŠÍ ÚČTY", ["Méně elektřiny ze sítě,", "víc energie ze sluníčka"]),
              ((1270, 650), "ls", "AUTOMATICKY", ["Řízení výkonu", "bez zásahu uživatele"])]
    for (x, y), anc, h, ls in blocks:
        a_ = "rm" if anc == "rs" else "lm"
        d.text((x, y), h, font=hf, fill=BLUE, anchor=a_)
        for i, l in enumerate(ls):
            d.text((x, y + 44 + i * 36), l, font=bf, fill=(40, 140, 210), anchor=a_)
    return im


GRID = grid_layer()


def draw_grid(frame, t):
    if not (93.5 <= t < 100.25):
        return frame
    lay = zoom(GRID, 1 + 0.02 * (t - 93.85) / 6.4)
    a = ramp(t, 93.5, 100.25, 0.4, 0.0)
    return Image.blend(frame, lay, a)


# ---------------------------------------------------------------- závěrečná karta
def end_card():
    im = Image.new("RGB", (W, H), (244, 245, 243))
    g = np.linspace(0, 1, H)[:, None, None]
    a = np.asarray(im).astype(float) * (1 - 0.06 * g)
    im = Image.fromarray(a.astype(np.uint8)).convert("RGBA")
    lg = logo.resize((int(logo.width * 230 / logo.height), 230), Image.LANCZOS)
    im.alpha_composite(lg, ((W - lg.width) // 2, 250))
    d = ImageDraw.Draw(im)
    d.text((W // 2, 590), "REO R290 Smart", font=F("demi", 66), fill=(70, 72, 74), anchor="mm")
    d.text((W // 2, 668), "Tepelné čerpadlo, které topí ze sluníčka", font=F("medium", 38), fill=GREEN, anchor="mm")
    d.text((W // 2, 790), "www.reoheating.cz", font=F("medium", 32), fill=(110, 112, 114), anchor="mm")
    return im.convert("RGB")


END = end_card()


def draw_end(frame, t):
    a = ramp(t, 105.55, 999, 0.5, 0)
    if a <= 0:
        return frame
    return Image.blend(frame, END, a)


# ---------------------------------------------------------------- hlavní smyčka
def process(frame, t):
    frame = draw_why(frame, t)
    frame = draw_curves(frame, t)
    frame = draw_pv(frame, t)
    frame = draw_grid(frame, t)
    draw_leak(frame, t)
    draw_swatches(frame, t)
    draw_topbar(frame, t)
    draw_ports(frame, t)
    if not (15.2 <= t < 18.13):
        draw_caption(frame, t)
    if t < 106.1:
        frame.paste(LOGO_LAYER, LOGO_XY, LOGO_LAYER)
    frame = draw_end(frame, t)
    return frame


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "--preview":
        os.makedirs(f"{S}/prev", exist_ok=True)
        for ts in sys.argv[3].split(","):
            t = float(ts)
            raw = subprocess.run([FF, "-v", "error", "-ss", ts, "-i", SRC, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
            fr = Image.frombytes("RGB", (W, H), raw[: W * H * 3])
            process(fr, t).save(f"{S}/prev/p{ts}.jpg", quality=88)
        sys.exit()
    dec = subprocess.Popen([FF, "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, bufsize=W * H * 3 * 4)
    enc = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "60000/1001", "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", f"{S}/build/video_cz.mp4"], stdin=subprocess.PIPE)
    n = 0
    while True:
        raw = dec.stdout.read(W * H * 3)
        if len(raw) < W * H * 3:
            break
        t = n / FPS
        fr = process(Image.frombytes("RGB", (W, H), raw), t)
        enc.stdin.write(fr.tobytes())
        n += 1
        if n % 600 == 0:
            print(f"{t:.1f}s", flush=True)
    enc.stdin.close()
    enc.wait()
    print("frames", n)
