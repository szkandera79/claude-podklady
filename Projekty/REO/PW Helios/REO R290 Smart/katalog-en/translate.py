#!/usr/bin/env python3
"""Česká verze přeznačeného katalogu: texty se přesázejí do stejného PDF (fotky, grafika a rozvržení zůstávají).
    python3 translate.py extract   → cz/segments.json (odstavce s pozicí a stylem; texty k překladu)
    (překlad: cz/cs.json  {id: "český text"}; značky [[k|…]] = úsek v jiném stylu, zachovat)
    python3 translate.py build     → REO-R290-Smart_katalog-CZ.pdf (+ kontrola)
Vstup je anglický výstup rebrand.py. Texty v obrázcích (displej, aplikace, konzole) zůstávají anglicky – displej je anglický.
"""
import json, math, pathlib, re, sys
import fitz

ROOT = pathlib.Path(__file__).parent
EN = ROOT / "REO-R290-Smart_catalogue-EN.pdf"
OUT = ROOT / "REO-R290-Smart_katalog-CZ.pdf"
CZ = ROOT / "cz"
SUP = pathlib.Path("/System/Library/Fonts/Supplemental")
CAL = pathlib.Path("/Applications/Microsoft Word.app/Contents/Resources/DFonts")   # Calibri z Office
FONTS = {  # náhrada podmnožinových fontů originálu fonty s českými znaky
    "cal": CAL / "Calibri.ttf", "calb": CAL / "Calibrib.ttf",
    "ar": SUP / "Arial.ttf", "arb": SUP / "Arial Bold.ttf", "ark": SUP / "Arial Black.ttf", "imp": SUP / "Impact.ttf",
}


def fkey(font, flags):
    f = font.lower()
    bold = bool(flags & 16) or any(k in f for k in ("bold", "-h", "-b", "heavy", "black", "extrabold"))
    if "calibri" in f:
        return "calb" if bold else "cal"
    if "impact" in f:
        return "imp"
    if "heavy" in f or "black" in f:
        return "ark"
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
    """Řádky → odstavce: stejný směr, stejná velikost, navazují pod sebou a překrývají se vodorovně."""
    paras = []
    for l in sorted(lines, key=lambda l: (round(l["bbox"][1]), l["bbox"][0])):
        sz = max(s["size"] for s in l["spans"])
        for p in paras:
            q = p[-1]
            qs = max(s["size"] for s in q["spans"])
            gap = l["bbox"][1] - q["bbox"][3]
            ov = min(l["bbox"][2], q["bbox"][2]) - max(l["bbox"][0], q["bbox"][0])
            if (abs(l["dir"][0] - 1) < 1e-3 and abs(q["dir"][0] - 1) < 1e-3 and abs(sz - qs) < 0.6
                    and -2 < gap < 0.75 * sz and ov > 0.25 * min(l["bbox"][2] - l["bbox"][0], q["bbox"][2] - q["bbox"][0])
                    and abs(l["bbox"][0] - q["bbox"][0]) < 40):
                p.append(l)
                break
        else:
            paras.append([l])
    return paras


def extract():
    doc = fitz.open(EN)
    segs = []
    for pn, page in enumerate(doc):
        for k, para in enumerate(group(lines_of(page))):
            spans = [s for l in para for s in l["spans"]]
            text = " ".join("".join(s["text"] for s in l["spans"]).strip() for l in para)
            if not re.search(r"[A-Za-z]{2,}", text):
                continue
            # převažující styl a úseky v jiném stylu
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
            xs0 = [l["bbox"][0] for l in para]; xs1 = [l["bbox"][2] for l in para]
            bb = fitz.Rect(min(xs0), min(l["bbox"][1] for l in para), max(xs1), max(l["bbox"][3] for l in para))
            cx = [(a + b) / 2 for a, b in zip(xs0, xs1)]
            align = "left"
            if len(para) > 1 and max(xs0) - min(xs0) > 3:
                align = "center" if max(cx) - min(cx) < 3 else ("right" if max(xs1) - min(xs1) < 3 else "left")
            segs.append({"id": f"p{pn+1}_{k:03d}", "page": pn, "bbox": [round(v, 2) for v in bb],
                         "dir": para[0]["dir"], "origin": para[0]["spans"][0]["origin"],
                         "nlines": len(para), "align": align, "style": main, "alts": alts,
                         "spans": [[round(v, 2) for v in s["bbox"]] for s in spans],
                         "en": " ".join(marked)})
    CZ.mkdir(exist_ok=True)
    (CZ / "segments.json").write_text(json.dumps(segs, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(segs), "segmentů →", CZ / "segments.json")


def css_style(st):
    k, size, color = st
    return (f"font-family:{k};font-size:{size}px;color:#{color:06x};"
            f"font-weight:normal;line-height:1.18")


def subtitle(page):
    """Titulka: podtitul je ve vektorech (bílé písmo se stínem) → nahradit českým."""
    page.add_redact_annot(fitz.Rect(739, 279, 1056, 302))
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED,
                          text=fitz.PDF_REDACT_TEXT_NONE)
    t = "Plně invertorové tepelné čerpadlo monoblok"
    f = fitz.Font(fontfile=str(FONTS["arb"]))
    sz = min(16.5, 312 / f.text_length(t, fontsize=1))
    for off, col in ((0.9, (0.2, 0.2, 0.2)), (0, (1, 1, 1))):
        page.insert_text((741 + off, 296.5 + off), t, fontsize=sz, fontname="arb", fontfile=str(FONTS["arb"]), color=col)


def build():
    segs = json.loads((CZ / "segments.json").read_text(encoding="utf-8"))
    cs = json.loads((CZ / "cs.json").read_text(encoding="utf-8"))
    over = json.loads((CZ / "override.json").read_text(encoding="utf-8")) if (CZ / "override.json").exists() else {}
    doc = fitz.open(EN)
    arch = fitz.Archive()
    for f in FONTS.values():
        arch.add((f.read_bytes(), f.name))
    css = "".join(f"@font-face{{font-family:{k};src:url(\'{p.name}\');}}" for k, p in FONTS.items()) + "*{margin:0;padding:0}"
    missing = [s["id"] for s in segs if s["id"] not in cs]
    if missing:
        print("chybí překlad:", missing[:20], len(missing))
    segs_by_id = {s["id"]: s for s in segs}
    by_page = {}
    for s in segs:
        if s["id"] in cs and cs[s["id"]] is not None:
            by_page.setdefault(s["page"], []).append(s)
    for pn, items in by_page.items():
        page = doc[pn]
        for s in items:
            rot = abs(s["dir"][0] - 1) > 1e-3
            for r in s["spans"]:
                rr = fitz.Rect(r)
                page.add_redact_annot(rr if rot else fitz.Rect(rr.x0 + .3, rr.y0 + rr.height * .3, rr.x1 - .3, rr.y1 - rr.height * .3))
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
        if pn == 0:
            subtitle(page)
        for s in items:
            t = cs[s["id"]]
            if not t:                       # text přesunutý do jiného segmentu (sloučené řádky)
                continue
            o = over.get(s["id"], {})
            r = fitz.Rect(s["bbox"])
            for m in o.get("merge", []):
                r |= fitz.Rect(segs_by_id[m]["bbox"])
            r = fitz.Rect(r.x0 + o.get("dx0", 0), r.y0 + o.get("dy0", 0), r.x1 + o.get("dx1", 0), r.y1 + o.get("dy1", 0))
            k, size, color = s["style"]
            size = o.get("size", size)
            if pn == 7 and s["nlines"] == 1 and "grow" not in o:     # tabulka: popisek smí do konce sloupce popisků
                lim = 212.5 if r.x0 < 600 else 807.5
                if r.x1 < lim:
                    o = {**o, "grow": lim - r.x1 - 1.5}
            dx, dy = s["dir"]
            if abs(dx - 1) > 1e-3:          # otočený text (jednořádkový)
                plain = re.sub(r"\[\[\d+\|(.*?)\]\]", r"\1", t)
                ang = math.degrees(math.atan2(dy, dx))
                org = fitz.Point(s["origin"])
                page.insert_text(org, plain, fontsize=size, fontname=k, fontfile=str(FONTS[k]),
                                 color=fitz.pdfcolor_from_int(color) if hasattr(fitz, "pdfcolor_from_int") else tuple(((color >> sh) & 255) / 255 for sh in (16, 8, 0)),
                                 morph=(org, fitz.Matrix(-ang)))
                continue

            def rep(m):
                a = s["alts"][int(m.group(1))]
                return f'<span style="{css_style(a)}">{m.group(2)}</span>'
            body = re.sub(r"\[\[(\d+)\|(.*?)\]\]", rep, t.replace("&", "&amp;")).replace("\n", "<br>")
            align = o.get("align", s["align"])
            html = f'<div style="{css_style((k, size, color))};text-align:{align}">{body}</div>'
            # na šířku necháme rezervu; na výšku podle počtu řádků originálu
            box = fitz.Rect(r.x0 - 1, r.y0 - 1, r.x1 + o.get("grow", 2), r.y1 + max(2, size * .4))
            if align == "right":
                box.x0 -= o.get("grow", 2) + 1; box.x1 = r.x1 + 1
            if align == "center":
                g = o.get("grow", 2); box.x0 -= g; box.x1 = r.x1 + g
            spare, scale = page.insert_htmlbox(box, html, css=css, archive=arch, scale_low=0.55)
            if scale < 0.8 or spare < 0:
                print(f"  {s['id']}: zmenšeno {scale:.2f}  „{t[:50]}“")
    doc.set_metadata({**doc.metadata, "title": "REO R290 Smart – produktový katalog", "subject": "Tepelná čerpadla REO R290 Smart",
                      "keywords": "REO HEATING, REO R290 Smart, tepelné čerpadlo, R290"})
    doc.save(OUT, garbage=4, deflate=True, clean=True)
    print("PDF", OUT, round(OUT.stat().st_size / 1e6, 1), "MB")
    left = [s["id"] for s in segs if s["id"] not in cs]
    print("nepřeloženo:", len(left))


if __name__ == "__main__":
    {"extract": extract, "build": build}[sys.argv[1]]()
