#!/usr/bin/env python3
"""Rebrand produktového katalogu výrobce (14 stran, dvojstrany 1207×825 pt, anglicky) na REO HEATING.
Obsah, fotky a sazba zůstávají; mění se jen značka:
  • logo výrobce v záhlaví (vektor) → logo REO HEATING; titulka: logo + název řady → „REO R290 Smart“
  • zadní strana: QR kódy, firma, adresy, web/e-mail výrobce → kontakty REO HEATING
  • fotky: nápis výrobce na jednotce (titulka, str. 8) → „REO HEATING“, energetický štítek, cloudová konzole
  • str. 10: popisek jednotky v FV schématu; str. 13–14: modely RHxx, z 1F tabulky jen RH06 (ostatní 1F se nenabízejí)
  • metadata, záložky, odkazy
    python3 rebrand.py   → REO-R290-Smart_catalogue-EN.pdf (na konci kontrola, že nezůstal odkaz na výrobce)
"""
import io, math, pathlib, re, sys
import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).parent
SRC = ROOT.parents[1] / "Power World Helios Pro Series Catalog.pdf"   # zdroj výrobce (mimo výstupy)
OUT = ROOT / "REO-R290-Smart_catalogue-EN.pdf"
KAT = ROOT.parent / "katalog" / "assets"
SUP = pathlib.Path("/System/Library/Fonts/Supplemental")
F_REG, F_BOLD, F_BLACK, F_BI = (str(SUP / n) for n in ("Arial.ttf", "Arial Bold.ttf", "Arial Black.ttf", "Arial Bold Italic.ttf"))
GREEN = (0x34 / 255, 0xA2 / 255, 0x63 / 255)
DARK = (0.243, 0.225, 0.221)            # tmavě šedá textů výrobce (#3E3938)
TBL = (0x23 / 255, 0x19 / 255, 0x16 / 255)


# ------------------------------------------------------------------ pomocné
def logos():
    """Logo REO HEATING: originál (na světlé pozadí) a varianta s bílým textem (na tmavé pozadí)."""
    im = Image.open(KAT / "logo-cut.png").convert("RGBA")
    a = np.array(im).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    grey = (np.abs(r - g) < 18) & (np.abs(g - b) < 18) & (a[..., 3] > 0)
    w = a.copy()
    w[grey, 0:3] = 255
    out = {}
    for k, arr in (("dark", a), ("white", w)):
        buf = io.BytesIO()
        Image.fromarray(arr.astype("uint8")).save(buf, "PNG")
        out[k] = buf.getvalue()
    return out, im.width / im.height


def put_logo(page, x1, yc, h, data, ratio):
    w = h * ratio
    page.insert_image(fitz.Rect(x1 - w, yc - h / 2, x1, yc + h / 2), stream=data)


def redact(page, rects, text=True, graphics=False, images=False, fill=None):
    for r in rects:
        page.add_redact_annot(fitz.Rect(r), fill=fill)
    page.apply_redactions(
        images=fitz.PDF_REDACT_IMAGE_REMOVE if images else fitz.PDF_REDACT_IMAGE_NONE,
        graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED if graphics else fitz.PDF_REDACT_LINE_ART_NONE,
        text=fitz.PDF_REDACT_TEXT_REMOVE if text else fitz.PDF_REDACT_TEXT_NONE)


def img_xref(page, w, h):
    for info in page.get_images(full=True):
        if info[2] == w and info[3] == h:
            return info[0], info[1]
    raise KeyError((w, h))


def inpaint_cols(a, box, thr=150, grow=2):
    """Odstraní světlý nápis v obdélníku: maska jasných pixelů, sloupcová interpolace mezi okolím nad/pod."""
    x0, y0, x1, y1 = box
    sub = a[y0:y1, x0:x1].astype(float)
    m = sub.mean(axis=2) > thr
    mm = m.copy()
    for _ in range(grow):
        mm[1:] |= mm[:-1].copy(); mm[:-1] |= mm[1:].copy()
        mm[:, 1:] |= mm[:, :-1].copy(); mm[:, :-1] |= mm[:, 1:].copy()
    H = sub.shape[0]
    for x in range(sub.shape[1]):
        col = mm[:, x]
        if not col.any():
            continue
        ys = np.where(col)[0]
        top, bot = max(ys.min() - 1, 0), min(ys.max() + 1, H - 1)
        ct, cb = sub[top, x].copy(), sub[bot, x].copy()
        for y in range(top + 1, bot):
            t = (y - top) / max(bot - top, 1)
            sub[y, x] = ct * (1 - t) + cb * t
    a[y0:y1, x0:x1] = sub.astype("uint8")
    return m


def bbox_of(mask, box):
    ys, xs = np.where(mask)
    return box[0] + xs.min(), box[1] + ys.min(), box[0] + xs.max(), box[1] + ys.max()


def unit_text(im, bb, angle=0.0, color=(214, 216, 220)):
    """Napíše „REO HEATING“ (tučná kurzíva) do prostoru po původním nápisu, zarovnáno vpravo, případně pootočeno."""
    x0, y0, x1, y1 = bb
    h = y1 - y0
    L = math.hypot(x1 - x0, h) if angle else (x1 - x0)
    cap = (h - abs(math.sin(math.radians(angle))) * (x1 - x0)) if angle else h
    size = int(cap * 1.32) + 1
    font = ImageFont.truetype(F_BI, size)
    tw = font.getlength("REO HEATING")
    pad = 8
    layer = Image.new("RGBA", (int(tw) + 2 * pad, size + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((pad, pad), "REO HEATING", font=font, fill=color + (235,))
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=True)
    # pravý dolní roh nápisu zhruba na místo původního konce
    px, py = int(x1 - layer.width + pad), int(y1 - layer.height + pad + 2)
    im.alpha_composite(layer, (px, py))


# ------------------------------------------------------------------ úpravy fotek
def fix_images(doc):
    # titulka: nápis na horní liště jednotky
    p = doc[0]
    x, _ = img_xref(p, 1655, 2244)
    pix = fitz.Pixmap(doc, x)
    a = np.array(Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB"))
    box = (1078, 1329, 1203, 1352)
    inpaint_cols(a, box, thr=100)
    im = Image.fromarray(a).convert("RGBA")
    unit_text(im, (1088, 1334, 1198, 1347), color=(222, 224, 228))   # rozměr původního nápisu
    buf = io.BytesIO(); im.convert("RGB").save(buf, "JPEG", quality=92)
    p.replace_image(x, stream=buf.getvalue())

    # str. 8 (pravá polovina dvojstrany 5): jednotka s ovladačem, nápis šikmo na horní liště
    p = doc[4]
    x, _ = img_xref(p, 1654, 2245)
    pix = fitz.Pixmap(doc, x)
    a = np.array(Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB"))
    box = (630, 1226, 775, 1276)
    m = inpaint_cols(a, box, thr=110)
    bb = bbox_of(m, box)
    im = Image.fromarray(a).convert("RGBA")
    unit_text(im, bb, angle=10.0, color=(205, 207, 212))
    buf = io.BytesIO(); im.convert("RGB").save(buf, "JPEG", quality=92)
    p.replace_image(x, stream=buf.getvalue())

    # str. 12: snímek cloudové konzole – čínský název výrobce v hlavičce
    p = doc[6]
    x, _ = img_xref(p, 728, 370)
    pix = fitz.Pixmap(doc, x)
    a = np.array(Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB"))
    inpaint_cols(a, (300, 4, 430, 30), thr=120)
    buf = io.BytesIO(); Image.fromarray(a).save(buf, "PNG")
    p.replace_image(x, stream=buf.getvalue())

    # str. 2: energetický štítek – jméno dodavatele
    p = doc[1]
    x, smask = img_xref(p, 529, 635)
    base = fitz.Pixmap(doc, x)
    rgb = np.array(Image.open(io.BytesIO(base.tobytes("png"))).convert("RGB"))
    alpha = np.array(Image.open(io.BytesIO(fitz.Pixmap(doc, smask).tobytes("png"))).convert("L"))
    alpha[148:186, 20:240] = 0            # text štítku = obrázek s maskou nad bílým vektorovým podkladem → zprůhlednit
    rgba = np.dstack([rgb, alpha])
    buf = io.BytesIO(); Image.fromarray(rgba).save(buf, "PNG")
    p.replace_image(x, stream=buf.getvalue())
    p.insert_text((686.5, 579.6), "REO HEATING", fontsize=8.6, fontname="ab", fontfile=F_BOLD, color=(0, 0, 0))


# ------------------------------------------------------------------ tabulky (str. 13–14)
def fix_tables(doc, src):
    p, sp = doc[7], src[7]
    spans = [s for b in sp.get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"]]
    C_LEFT = (212.5 + 546.6) / 2          # střed jediného sloupce hodnot (RH06)
    kill, move = [], []
    for s in spans:
        r = fitz.Rect(s["bbox"]); cx = (r.x0 + r.x1) / 2
        if r.x1 > 600 or r.y1 > 745 or r.y0 < 73:
            continue
        if r.y0 < 100:                                    # záhlaví tabulky
            if r.x0 > 212:
                kill.append(r)
            continue
        if r.x1 <= 212.6 or r.x0 < 72:                    # popisky řádků, podmínky měření
            continue
        if abs(cx - C_LEFT) < 4 and not s["text"].startswith("1328"):   # sloučené přes všechny sloupce (rozměr 3F ne)
            continue
        if 212.5 <= cx <= 268.1 or s["text"].strip() == "DN25":
            move.append(r)                                # hodnota RH06 (1F) → do středu
        kill.append(r)
    redact(p, kill)
    # svislé čáry mezi sloupci 1F modelů, které se nenabízejí
    redact(p, [(x - 0.8, 73, x + 0.8, 741) for x in (268.1, 323.8, 379.5, 435.2, 490.9)], text=False, graphics=True)
    for r in move:
        c = fitz.Rect(r.x0 - 0.6, r.y0 - 0.4, r.x1 + 0.6, r.y1 + 0.4)
        dx = C_LEFT - (r.x0 + r.x1) / 2
        p.show_pdf_page(c + (dx, 0, dx, 0), src, 7, clip=c)

    # názvy modelů v záhlaví obou tabulek
    def head(cx, name, phase):
        f = fitz.Font(fontfile=F_BOLD)
        for t, y, sz in ((name, 86.4, 7.2), (phase, 94.6, 6.6)):
            w = f.text_length(t, fontsize=sz)
            p.insert_text((cx - w / 2, y), t, fontsize=sz, fontname="ab", fontfile=F_BOLD, color=TBL)
    head(C_LEFT, "RH06", "(1-phase)")
    for s in spans:
        r = fitz.Rect(s["bbox"])
        if r.x0 > 603 and r.y0 < 100 and re.match(r"PW\d\d", s["text"]):
            cx = (r.x0 + r.x1) / 2
            redact(p, [r, fitz.Rect(cx - 28, r.y1 + 0.2, cx + 28, r.y1 + 9)])
            head(cx, s["text"].replace("PW", "RH"), "(3-phase)")


# ------------------------------------------------------------------ hlavní
def main():
    src = fitz.open(SRC)
    doc = fitz.open(SRC)
    LOGO, ratio = logos()

    # 1) logo výrobce v záhlaví stran 2–14 (vektor) → REO HEATING
    dark_bg = {2, 4}                      # dvojstrany s tmavým pozadím v záhlaví (černé pozadí)
    for i in range(1, 8):
        p = doc[i]
        redact(p, [(1073, 37.5, 1164, 46)], text=False, graphics=True)
        put_logo(p, 1163, 41.8, 19, LOGO["white" if i in dark_bg else "dark"], ratio)

    # 2) titulka – název řady výrobce je vyplněný přechody (shading) přes tmavé tvary → odstranit oboje
    p = doc[0]
    for x in p.get_contents():
        st = doc.xref_stream(x)
        for n in (b"/Sh71 sh", b"/Sh122 sh", b"/Sh126 sh"):
            st = st.replace(n, b"")
        doc.update_stream(x, st)
    redact(p, [(1036, 30, 1098, 55), (979, 60, 1147, 75),                 # logo
               (742, 184, 902, 271), (913, 184, 1055, 270), (995, 248, 1054, 265)],  # „H8 Helios Pro Series“
           text=False, graphics=True)
    put_logo(p, 1147, 52, 46, LOGO["white"], ratio)
    fb = fitz.Font(fontfile=F_BLACK)
    p.insert_text((744, 233), "REO R290", fontsize=47, fontname="ak", fontfile=F_BLACK, color=DARK)
    p.insert_text((744, 274), "Smart", fontsize=40, fontname="ak", fontfile=F_BLACK, color=GREEN)
    p.insert_text((744 + fb.text_length("Smart", fontsize=40) + 8, 274), "Series", fontsize=17,
                  fontname="ab", fontfile=F_BOLD, color=DARK)

    # 3) zadní strana: kontakty výrobce → REO HEATING
    redact(p, [(30, 40, 600, 712)], graphics=True, images=True, fill=(1, 1, 1))
    redact(p, [(480, 786, 600, 800)], fill=(1, 1, 1))
    for l in p.get_links():
        p.delete_link(l)
    put_logo(p, 42 + 52 * ratio, 82, 52, LOGO["dark"], ratio)
    qr = fitz.open(KAT / "qr-reoheating.svg")
    qpdf = fitz.open("pdf", qr.convert_to_pdf())
    p.show_pdf_page(fitz.Rect(500, 50, 575, 125), qpdf, 0)
    p.insert_text((509, 136), "reoheating.cz", fontsize=7.5, fontname="ar", fontfile=F_REG, color=DARK)
    T = lambda xy, t, sz=8.5, f=F_REG, c=DARK: p.insert_text(xy, t, fontsize=sz, fontname=("ab" if f == F_BOLD else "ar"), fontfile=f, color=c)
    T((41, 616), "REO HEATING", 16, F_BOLD)
    T((41, 634), "Heat pumps · Riva Trade s.r.o., ID No. 08864811", 9)
    T((41, 658), "Showroom, shop and warehouse:", 8.5, F_BOLD)
    T((41, 670), "Smetanova 555, 739 61 Třinec, Czech Republic · Mon–Fri 9:00–16:00", 8.5)
    T((41, 704), "Website: reoheating.cz", 8.5)
    T((170, 704), "E-mail: info@reoheating.cz", 8.5)
    T((312, 704), "Phone: +420 774 872 467", 8.5)
    T((520, 796), "REO HEATING · 10/2026", 7)

    # 4) str. 10: popisek jednotky ve schématu FV (otočený text)
    p = doc[5]
    redact(p, [(415, 195, 485, 245)])
    ang = math.degrees(math.atan2(0.48734, 0.87321))
    o = fitz.Point(415.68, 203.98)
    p.insert_text(o, "REO R290 Smart", fontsize=10, fontname="ab", fontfile=F_BOLD,
                  color=(0, 0x97 / 255, 0xE0 / 255), morph=(o, fitz.Matrix(-ang)))

    # 5) str. 12: logo výrobce v hlavičce cloudové konzole
    p = doc[6]
    redact(p, [(775, 159, 812.5, 163)], text=False, graphics=True)
    f = fitz.Font(fontfile=F_BOLD)
    t = "REO HEATING"
    p.insert_text((793.4 - f.text_length(t, fontsize=4.2) / 2, 162.5), t, fontsize=4.2, fontname="ab", fontfile=F_BOLD, color=(1, 1, 1))

    fix_images(doc)
    fix_tables(doc, src)

    doc.set_toc([])
    doc.del_xml_metadata()
    doc.set_metadata({"title": "REO R290 Smart – Product Catalogue", "author": "REO HEATING", "subject": "REO R290 Smart heat pumps",
                      "keywords": "REO HEATING, REO R290 Smart, heat pump, R290", "creator": "REO HEATING", "producer": "REO HEATING"})
    doc.save(OUT, garbage=4, deflate=True, clean=True)
    print("PDF", OUT, round(OUT.stat().st_size / 1e6, 1), "MB")
    check()


def check():
    d = fitz.open(OUT)
    bad = re.compile(r"(?i)power\s*world|powerworld|helios|\bPW\d|DKXL|派沃|H8\b")
    txt = " ".join(p.get_text() for p in d)
    meta = str(d.metadata) + str(d.get_toc())
    raw = b"".join(d.xref_stream(x) or b"" for x in range(1, d.xref_length()) if not d.xref_is_image(x))
    hits = bad.findall(txt) + bad.findall(meta) + re.findall(rb"(?i)powerworld|power world|helios", raw)
    links = [l.get("uri") for p in d for l in p.get_links()]
    print("kontrola: nálezy", hits or "žádné", "| odkazy", links or "žádné")


if __name__ == "__main__":
    main()
