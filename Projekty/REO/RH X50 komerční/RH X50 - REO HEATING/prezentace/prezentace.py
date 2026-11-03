#!/usr/bin/env python3
"""Česká prezentace REO HEATING „Komerční tepelné čerpadlo R290“ (RH X50 / RH X100) – věrný rebrand a překlad
prezentace výrobce „R290 Commercial Heat Pump Introduction“ (60 snímků 960×540 pt, aktualizace 11. 4. 2025).
Sazba, fotky a schémata zůstávají; mění se značka a jazyk:
  • logo výrobce v záhlaví (rastr) → logo REO HEATING; titulka a závěr → bílé logo REO HEATING
  • fotka sídla výrobce (oddělovací snímky) → AI vizualizace RH X50 u podniku (jako na letáku)
  • titulek „R290 Commercial Heat Pump“ a „Thanks!“ (rastr) → česky
  • schéma kaskády (str. 37): „PW 150“ → „RH X50“, popisky česky; snímek aplikace (str. 40): Wi‑Fi „pwwm“ → „MyWiFi“
  • ikony příloh výrobce (str. 42, 48, 49, 59) odstraněny – přílohy v PDF nejsou
  • typy PW150-/PW300-DKZLRS-E → RH X50 / RH X100 (v překladu), metadata
    python3 prezentace.py extract   → cz/segments.json (odstavce s pozicí a stylem)
    (překlad: cz/cs.json  {id: "český text"}; "" = text odstranit; značky [[k|…]] = úsek v jiném stylu)
    python3 prezentace.py build     → REO-RH-X50-X100_prezentace-CZ.pdf (+ kontrola odkazů na výrobce)
Texty na displeji ovladače a v aplikaci zůstávají anglicky (ovladač je anglický).
"""
import io, json, math, pathlib, re, sys
import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).parent
SRC = ROOT.parents[1] / "R290 Commercial Heat Pump Introduction 20250411.pdf"   # zdroj výrobce (RH X50 komerční/)
OUT = ROOT / "REO-RH-X50-X100_prezentace-CZ.pdf"
CZ = ROOT / "cz"
A = ROOT.parent / "letak" / "assets"
SUP = pathlib.Path("/System/Library/Fonts/Supplemental")
CAL = pathlib.Path("/Applications/Microsoft Word.app/Contents/Resources/DFonts")
FONTS = {
    "tr": SUP / "Times New Roman.ttf", "trb": SUP / "Times New Roman Bold.ttf",
    "cal": CAL / "Calibri.ttf", "calb": CAL / "Calibrib.ttf",
    "ar": SUP / "Arial.ttf", "arb": SUP / "Arial Bold.ttf",
}
HELV = "/System/Library/Fonts/Helvetica.ttc"
NOFILL = dict(fill=False)


# ───────────────────────── rebrand obrázků ─────────────────────────

def pil(doc, xref):
    pix = fitz.Pixmap(doc, xref)
    if pix.alpha:
        pix = fitz.Pixmap(pix, 0)
    if pix.n != 3:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def png(im):
    buf = io.BytesIO(); im.save(buf, "PNG"); return buf.getvalue()


def jpg(im):
    buf = io.BytesIO(); im.convert("RGB").save(buf, "JPEG", quality=90); return buf.getvalue()


def logo_on(size, white=False, pad=0.08):
    """Logo REO HEATING vycentrované do plátna o rozměru size (průhledné pro bílé, jinak na bílém)."""
    lg = Image.open(A / ("logo-reo-heating-white.png" if white else "logo-reo-heating.png")).convert("RGBA")
    lg = lg.crop(lg.getchannel("A").getbbox())
    W, H = size
    s = min(W * (1 - 2 * pad) / lg.width, H * (1 - 2 * pad) / lg.height)
    lg = lg.resize((round(lg.width * s), round(lg.height * s)), Image.LANCZOS)
    can = Image.new("RGBA", size, (255, 255, 255, 0 if white else 255))
    can.alpha_composite(lg, ((W - lg.width) // 2, (H - lg.height) // 2))
    return can


def ink_bbox(im, box, thr=140):
    a = np.asarray(im.convert("L").crop(box)) < thr
    ys, xs = np.where(a)
    return (box[0] + xs.min(), box[1] + ys.min(), box[0] + xs.max() + 1, box[1] + ys.max() + 1)


def kaskada(im):
    """Str. 37: v rámečcích jednotek „PW 150“ → „RH X50“ (svisle), nádrž a TUV česky."""
    d = ImageDraw.Draw(im)
    boxes = [(93, 22, 195, 212), (315, 22, 417, 212), (537, 22, 640, 212), (742, 22, 845, 212),
             (30, 462, 133, 655), (271, 462, 373, 655), (528, 462, 632, 650), (751, 462, 855, 650), (973, 462, 1077, 650)]
    f = ImageFont.truetype(SUP / "Arial.ttf", 27)
    for b in boxes:
        x0, y0, x1, y1 = ink_bbox(im, (b[0] + 6, b[1] + 6, b[2] - 6, b[3] - 6))
        d.rectangle((x0 - 2, y0 - 2, x1 + 2, y1 + 2), fill="white")
        t = Image.new("RGBA", (200, 40), (255, 255, 255, 0))
        ImageDraw.Draw(t).text((100, 20), "RH X50", font=f, fill="black", anchor="mm")
        t = t.rotate(-90, expand=True)
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        im.paste(t, (cx - t.width // 2, cy - t.height // 2), t)
    # „3t buffer tank“ v kruhu, „DHW“ pod zásobníkem, drobné popisky potrubí
    def relabel(box, lines, size, font="Arial.ttf", anchor_x=None):
        x0, y0, x1, y1 = ink_bbox(im, box)
        d.rectangle((x0 - 1, y0 - 1, x1 + 1, y1 + 1), fill="white")
        fnt = ImageFont.truetype(SUP / font, size)
        h = size * 1.15
        top = (y0 + y1) / 2 - h * len(lines) / 2
        for i, ln in enumerate(lines):
            if anchor_x == "l":
                d.text((x0, top + h * (i + .5)), ln, font=fnt, fill="black", anchor="lm")
            else:
                d.text(((x0 + x1) / 2, top + h * (i + .5)), ln, font=fnt, fill="black", anchor="mm")
    relabel((1195, 295, 1290, 390), ["Akumulační", "nádrž", "3 m³"], 17)
    relabel((1245, 672, 1300, 700), ["TUV"], 22, "Arial Bold.ttf")
    relabel((1195, 104, 1265, 117), ["přívod studené vody"], 9)
    relabel((1470, 317, 1600, 330), ["Do otopné soustavy"], 9, anchor_x="l")
    relabel((1418, 395, 1555, 408), ["Vratná voda z otopné soustavy"], 9, anchor_x="l")
    return im


def wifi(im):
    """Str. 40, snímek aplikace: síť „pwwm“ a heslo → neutrální."""
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(HELV, 31)
    for box, base, t in (((153, 849, 250, 876), 868, "MyWiFi"), ((153, 969, 357, 1003), 994, "heslo1234")):
        d.rectangle(box, fill="white")
        d.text((box[0] + 2, base), t, font=f, fill=(25, 25, 25), anchor="ls")
    return im


def text_image(size, text, font, color=(255, 255, 255)):
    """Bílý nápis (Times) na průhledném plátně – náhrada rastrového titulku."""
    W, H = size
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    s = H
    while True:
        fnt = ImageFont.truetype(font, s)
        l, t, r, b = d.textbbox((0, 0), text, font=fnt)
        if r - l <= W * .98 and b - t <= H * .9:
            break
        s -= 2
    d.text((W / 2, H / 2), text, font=fnt, fill=color + (255,), anchor="mm")
    return im


def rebrand(doc):
    p1 = doc[0]
    # záhlaví všech snímků + titulka/závěr
    doc[1].replace_image(28, stream=jpg(logo_on((351, 166))))
    p1.replace_image(10, stream=png(logo_on((864, 408), white=True)))
    # fotka sídla výrobce na oddělovacích snímcích → vizualizace RH X50 (výřez na poměr originálu)
    hero = Image.open(A / "hero-podnik-na-vysku.png").convert("RGB")
    W, H = 1204, 1944
    s = max(W / hero.width, H / hero.height)
    hero = hero.resize((math.ceil(hero.width * s), math.ceil(hero.height * s)), Image.LANCZOS)
    x = int((hero.width - W) * .55)
    doc[1].replace_image(30, stream=jpg(hero.crop((x, 0, x + W, H))))
    # titulek titulky (dva rastry) → jeden český, závěr „Thanks!“ → „Děkujeme!“
    p1.replace_image(17, stream=png(Image.new("RGBA", (8, 8), (0, 0, 0, 0))))
    p1.replace_image(19, stream=png(Image.new("RGBA", (8, 8), (0, 0, 0, 0))))
    p1.insert_image(fitz.Rect(70, 236, 890, 304), stream=png(text_image((2460, 204), "Komerční tepelné čerpadlo R290", str(FONTS["tr"]))))
    doc[59].replace_image(401, stream=png(text_image((844, 196), "Děkujeme!", str(FONTS["tr"]))))
    # schéma kaskády, snímek Wi‑Fi
    doc[36].replace_image(272, stream=png(kaskada(pil(doc, 272))))
    doc[39].replace_image(281, stream=jpg(wifi(pil(doc, 281))))
    # ikony vložených příloh výrobce (náhled OLE) – v PDF nejsou, pryč
    for pn, xref in ((41, 294), (47, 345), (48, 351), (58, 397)):
        doc[pn].delete_image(xref)


# ───────────────────────── překlad textů ─────────────────────────

def fkey(font, flags):
    f = font.lower()
    bold = bool(flags & 16) or "bold" in f
    if "times" in f:
        return "trb" if bold else "tr"
    if "calibri" in f:
        return "calb" if bold else "cal"
    return "arb" if bold else "ar"


def style(s):
    return (fkey(s["font"], s["flags"]), round(s["size"], 1), s["color"])


def lines_of(page):
    out = []
    for b in page.get_text("dict")["blocks"]:
        if b["type"]:
            continue
        for l in b["lines"]:
            sp = [s for s in l["spans"] if s["text"].strip()]
            if sp:
                out.append({"dir": l["dir"], "bbox": l["bbox"], "spans": sp})
    return out


def group(lines):
    """Řádky → odstavce: stejný směr a velikost, navazují pod sebou, překrývají se vodorovně, stejný levý okraj."""
    paras = []
    for l in sorted(lines, key=lambda l: (round(l["bbox"][1]), l["bbox"][0])):
        sz = max(s["size"] for s in l["spans"])
        for p in paras:
            q = p[-1]
            qs = max(s["size"] for s in q["spans"])
            gap = l["bbox"][1] - q["bbox"][3]
            ov = min(l["bbox"][2], q["bbox"][2]) - max(l["bbox"][0], q["bbox"][0])
            if (abs(l["dir"][0] - 1) < 1e-3 and abs(q["dir"][0] - 1) < 1e-3 and abs(sz - qs) < 0.6
                    and -2 < gap < 0.6 * sz and ov > 0.25 * min(l["bbox"][2] - l["bbox"][0], q["bbox"][2] - q["bbox"][0])
                    and abs(l["bbox"][0] - q["bbox"][0]) < 25):
                p.append(l)
                break
        else:
            paras.append([l])
    return paras


def extract():
    doc = fitz.open(SRC)
    segs = []
    for pn, page in enumerate(doc):
        for k, para in enumerate(group(lines_of(page))):
            spans = [s for l in para for s in l["spans"]]
            text = " ".join("".join(s["text"] for s in l["spans"]).strip() for l in para)
            if not re.search(r"[A-Za-z]{2,}", text):
                continue
            cnt = {}
            for s in spans:
                cnt[style(s)] = cnt.get(style(s), 0) + len(s["text"])
            main = max(cnt, key=cnt.get)
            alts, marked = [], []
            for l in para:
                parts = []
                for s in l["spans"]:
                    st = style(s)
                    if st == main or not s["text"].strip():
                        parts.append(s["text"])
                    else:
                        if st not in alts:
                            alts.append(st)
                        parts.append(f"[[{alts.index(st)}|{s['text'].strip()}]]")
                marked.append("".join(parts).strip())
            en = " ".join(marked)
            en = re.sub(r"\]\]\s*\[\[(\d+)\|", lambda m: " " if False else f"]] [[{m.group(1)}|", en)
            xs0 = [l["bbox"][0] for l in para]; xs1 = [l["bbox"][2] for l in para]
            bb = fitz.Rect(min(xs0), min(l["bbox"][1] for l in para), max(xs1), max(l["bbox"][3] for l in para))
            cx = [(a + b) / 2 for a, b in zip(xs0, xs1)]
            align = "left"
            if len(para) > 1 and max(xs0) - min(xs0) > 3:
                align = "center" if max(cx) - min(cx) < 3 else ("right" if max(xs1) - min(xs1) < 3 else "left")
            segs.append({"id": f"p{pn+1}_{k:03d}", "page": pn, "bbox": [round(v, 2) for v in bb],
                         "dir": para[0]["dir"], "origin": para[0]["spans"][0]["origin"],
                         "nlines": len(para), "align": align, "style": main, "alts": alts,
                         "spans": [[round(v, 2) for v in s["bbox"]] for s in spans], "en": en})
    CZ.mkdir(exist_ok=True)
    (CZ / "segments.json").write_text(json.dumps(segs, ensure_ascii=False, indent=1), encoding="utf-8")
    # stručný seznam k překladu
    (CZ / "en.json").write_text(json.dumps({s["id"]: s["en"] for s in segs}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(segs), "segmentů →", CZ / "segments.json", sum(len(s["en"]) for s in segs), "znaků")


def css_style(st):
    k, size, color = st
    return f"font-family:{k};font-size:{size}px;color:#{color:06x};font-weight:normal;line-height:1.15"


def load_cs():
    cs = {}
    for f in sorted(CZ.glob("cs*.json")):
        cs.update(json.loads(f.read_text(encoding="utf-8")))
    return cs


def build():
    segs = json.loads((CZ / "segments.json").read_text(encoding="utf-8"))
    cs = load_cs()
    over = json.loads((CZ / "override.json").read_text(encoding="utf-8")) if (CZ / "override.json").exists() else {}
    doc = fitz.open(SRC)
    rebrand(doc)
    arch = fitz.Archive()
    for f in FONTS.values():
        arch.add((f.read_bytes(), f.name))
    css = "".join(f"@font-face{{font-family:{k};src:url('{p.name}');}}" for k, p in FONTS.items()) + "*{margin:0;padding:0}"
    missing = [s["id"] for s in segs if s["id"] not in cs]
    if missing:
        print("chybí překlad:", len(missing), missing[:15])
    segs_by_id = {s["id"]: s for s in segs}
    by_page = {}
    for s in segs:
        if cs.get(s["id"]) is not None:
            by_page.setdefault(s["page"], []).append(s)
    for pn, items in by_page.items():
        page = doc[pn]
        for s in items:
            rot = abs(s["dir"][0] - 1) > 1e-3
            for r in s["spans"]:
                rr = fitz.Rect(r)
                page.add_redact_annot(rr if rot else fitz.Rect(rr.x0 + .3, rr.y0 + rr.height * .3, rr.x1 - .3, rr.y1 - rr.height * .3), **NOFILL)
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
        for s in items:
            t = cs[s["id"]]
            o = over.get(s["id"], {})
            if not t:
                continue
            r = fitz.Rect(s["bbox"])
            for m in o.get("merge", []):
                r |= fitz.Rect(segs_by_id[m]["bbox"])
            r = fitz.Rect(r.x0 + o.get("dx0", 0), r.y0 + o.get("dy0", 0), r.x1 + o.get("dx1", 0), r.y1 + o.get("dy1", 0))
            k, size, color = s["style"]
            size = o.get("size", size)
            dx, dy = s["dir"]
            if abs(dx - 1) > 1e-3:          # otočený text (jednořádkový)
                plain = re.sub(r"\[\[\d+\|(.*?)\]\]", r"\1", t)
                ang = math.degrees(math.atan2(dy, dx))
                org = fitz.Point(s["origin"])
                page.insert_text(org, plain, fontsize=size, fontname=k, fontfile=str(FONTS[k]),
                                 color=tuple(((color >> sh) & 255) / 255 for sh in (16, 8, 0)), morph=(org, fitz.Matrix(-ang)))
                continue

            def rep(m):
                a = s["alts"][int(m.group(1))]
                return f'<span style="{css_style(a)}">{m.group(2)}</span>'
            body = re.sub(r"\[\[(\d+)\|(.*?)\]\]", rep, t.replace("&", "&amp;").replace("<", "&lt;")).replace("\n", "<br>")
            align = o.get("align", s["align"])
            html = f'<div style="{css_style((k, size, color))};text-align:{align}">{body}</div>'
            g = o.get("grow", 2)
            box = fitz.Rect(r.x0 - 1, r.y0 - 1, r.x1 + g, r.y1 + max(2, size * .4) + o.get("growy", 0))
            if align == "right":
                box.x0 -= g + 1; box.x1 = r.x1 + 1
            if align == "center":
                box.x0 -= g
            spare, scale = page.insert_htmlbox(box, html, css=css, archive=arch, scale_low=0.5)
            if scale < 0.75 or spare < 0:
                print(f"  {s['id']}: zmenšeno {scale:.2f}  „{t[:50]}“")
    doc.set_metadata({"title": "Komerční tepelné čerpadlo R290 – RH X50 / RH X100", "author": "REO HEATING",
                      "subject": "Prezentace: popis, instalace, ovládání, uvedení do provozu a chybové kódy RH X50 / RH X100",
                      "keywords": "REO HEATING, RH X50, RH X100, tepelné čerpadlo, R290", "creator": "REO HEATING", "producer": ""})
    doc.del_xml_metadata()
    doc.save(OUT, garbage=4, deflate=True, clean=True)
    print("PDF", OUT, round(OUT.stat().st_size / 1e6, 1), "MB")
    check()


def check():
    doc = fitz.open(OUT)
    bad = re.compile(r"(?i)power\s*world|powerworld|\bPW\s?\d|DKZLRS|pwwm|派沃|870092")
    hits = [(i + 1, m.group()) for i, p in enumerate(doc) for m in bad.finditer(p.get_text())]
    meta = [v for v in doc.metadata.values() if v and bad.search(str(v))]
    raw = [x for x in range(1, doc.xref_length()) if doc.xref_is_stream(x) is False and bad.search(doc.xref_object(x) or "")]
    left = [(i + 1, w[4]) for i, p in enumerate(doc) for w in p.get_text("words")
            if re.fullmatch(r"(?i)(the|and|of|is|to|with|unit|water|pump|heat|please|click|setting)", w[4])]
    print("odkazy na výrobce:", hits or "žádné", meta or "", raw or "")
    print("zbylá angličtina (ukázka):", left[:25], len(left))


if __name__ == "__main__":
    {"extract": extract, "build": build, "check": check}[sys.argv[1]]()
