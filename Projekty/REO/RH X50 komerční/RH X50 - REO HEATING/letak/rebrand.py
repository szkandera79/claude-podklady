#!/usr/bin/env python3
"""Rebrand produktového letáku výrobce „R290 Commercial Heat Pump Series“ (2 strany 1207×825 pt, anglicky)
na REO HEATING RH X50 / RH X100. Sazba, texty a fotky jednotek zůstávají; mění se:
  • úvodní obrázek (levá polovina str. 1) → AI vizualizace RH X50 u výrobního podniku (z webu mobilních kotelen,
    rozšířená na výšku), aby nešel dohledat původní obrázek výrobce; rendery jednotek, stíny a efekty originálu pryč
  • energetický štítek výrobce → štítek RH X50 REO HEATING
  • logo výrobce v záhlaví obou stran (vektor) → logo REO HEATING; loga na jednotkách ve fotkách (vektor) → logo REO HEATING
  • nadpis „R290 / Commercial Series“ → „RH X50 · RH X100 / R290 Commercial Series“
  • tabulka parametrů: typ výrobce → RH X50 + nový sloupec RH X100 (data z návodu a listu parametrů výrobce)
  • metadata
    python3 rebrand.py   → REO-RH-X50-X100_letak-EN.pdf (na konci kontrola, že nezůstal odkaz na výrobce)
"""
import io, pathlib, re
import fitz
from PIL import Image

ROOT = pathlib.Path(__file__).parent
SRC = ROOT.parents[1] / "R290-Commercial-Heat-Pump-Series.pdf"          # zdroj výrobce (RH X50 komerční/)
OUT = ROOT / "REO-RH-X50-X100_letak-EN.pdf"
A = ROOT / "assets"
LABEL = ROOT.parent / "RH-X50-energeticky-stitek.pdf"
CAL = "/Applications/Microsoft Word.app/Contents/Resources/DFonts/Calibri.ttf"
BLUE = (0, 0x97 / 255, 0xE0 / 255)          # modrá nadpisů originálu
INK = (0x3E / 255, 0x39 / 255, 0x38 / 255)   # text tabulky
GRID = (0.787, 0.790, 0.791)

# RH X100: hodnoty v pořadí řádků tabulky (návod k použití, tab. 2.2 + list parametrů komerčních jednotek výrobce)
X100 = ["40.0~120", "9.0~29.5", "4.06~5.5", "2580",                   # TUV
        "35.2~92", "7.0~23.8", "3.86~5.02",                             # vytápění
        "25~66", "8.92~30.7", "2.15~2.8",                               # chlazení
        "A+++", "A++", "380V/3Ph/50-60Hz", "40", "64", "80", "22mm²", 'G2"', "≤85", "65",
        "11.6", "120", "745", "2510×979×1882", "2560*1030*2000", "IPX4", "I", "R290", "HIGHLY",
        "-25~43°C", "20~78°C(DHW )", "20~78°C(Heating)", "7~35°C(Cooling)"]


def redact(page, rects, text=True, graphics=False):
    for r in rects:
        page.add_redact_annot(fitz.Rect(r))
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                          graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED if graphics else fitz.PDF_REDACT_LINE_ART_NONE,
                          text=fitz.PDF_REDACT_TEXT_REMOVE if text else fitz.PDF_REDACT_TEXT_NONE)


def logo_png(white=False, tint=None):
    im = Image.open(A / ("logo-reo-heating-white.png" if white else "logo-reo-heating.png")).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    if tint:   # jednobarevně (jako původní šedý nápis na jednotce)
        a = im.getchannel("A")
        im = Image.new("RGBA", im.size, tint + (255,)); im.putalpha(a)
    buf = io.BytesIO(); im.save(buf, "PNG")
    return buf.getvalue(), im.width / im.height


def drop_xobjects(doc, page, names):
    for x in page.get_contents():
        st = doc.xref_stream(x)
        for n in names:
            st = st.replace(f"/{n} Do".encode(), b"")
        doc.update_stream(x, st)


def hero(doc):
    p = doc[0]
    im = Image.open(A / "hero-podnik-na-vysku.png").convert("RGB").resize((1418, 1924), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=92)
    p.replace_image(14, stream=buf.getvalue())
    # rendery jednotek, stíny, „teplo“ nad ventilátory a štítek výrobce — obrázek už jednotky obsahuje
    drop_xobjects(doc, p, ["Im19", "Fm30", "Fm41", "Im111", "Fm120", "Im127", "Im129", "Im132", "Im134", "Im136"])
    # vektorová loga a ikony Wi‑Fi, které ležely na renderech jednotek
    redact(p, [(181.2, 642.8, 211.3, 651.4), (411.9, 580.8, 437.0, 588.0),
               (155.5, 623.2, 167.2, 637.8), (324.6, 583.3, 336.3, 597.9)], text=False, graphics=True)
    # energetický štítek REO HEATING vlevo dole (vpravo by zakryl jednotky)
    lab = fitz.open(LABEL)[0]
    h = 75 * lab.rect.height / lab.rect.width
    box = fitz.Rect(30, 703 - h, 105, 703)
    p.draw_rect(box, color=None, fill=(1, 1, 1))
    p.show_pdf_page(box, fitz.open(LABEL), 0)


def logos(doc):
    dark, ratio = logo_png()
    for p in doc:   # záhlaví obou stran
        redact(p, [(1073.7, 37.9, 1163.4, 45.7)], text=False, graphics=True)
        h = 17
        p.insert_image(fitz.Rect(1163 - h * ratio, 41.8 - h / 2, 1163, 41.8 + h / 2), stream=dark)
    # loga na jednotkách ve fotkách vpravo (šedý vektor) → logo REO HEATING ve stejné šedi
    gray, ratio = logo_png(white=True, tint=(181, 181, 182))
    p = doc[0]
    for r in [(1068.1, 602.3, 1078.5, 605.0), (1025.7, 397.5, 1044.6, 402.4)]:
        R = fitz.Rect(r)
        redact(p, [R + (-0.5, -4, 0.5, 0.5)], text=False, graphics=True)
        w = R.width * 1.15; cx = (R.x0 + R.x1) / 2
        p.insert_image(fitz.Rect(cx - w / 2, R.y1 - w / ratio, cx + w / 2, R.y1), stream=gray)


def title(doc):
    p = doc[0]
    redact(p, [(674.2, 98.3, 747.0, 128.3), (674.2, 134.9, 918.2, 164.9)])
    p.insert_text((674.2, 122.0), "RH X50 · RH X100", fontsize=30, fontname="cal", fontfile=CAL, color=BLUE)
    p.insert_text((674.2, 158.6), "R290 Commercial Series", fontsize=30, fontname="cal", fontfile=CAL, color=BLUE)


def table(doc):
    p = doc[1]
    f = fitz.Font(fontfile=CAL)
    spans = [s for b in p.get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"]]
    vals = [s for s in spans if s["bbox"][0] >= 925 and 110 < s["bbox"][1] < 770 and s["text"].strip()]
    head = [s for s in vals if "PW150" in s["text"]][0]
    vals = [s for s in vals if s is not head]
    # řádky = skupiny hodnot se stejným účařím (≤ a číslo jsou dva spany)
    rows = []
    for s in sorted(vals, key=lambda s: (s["origin"][1], s["bbox"][0])):
        if rows and abs(rows[-1][0] - s["origin"][1]) < 2.5:
            rows[-1][1].append(s)
        else:
            rows.append([s["origin"][1], [s]])
    assert len(rows) == len(X100), (len(rows), len(X100))
    redact(p, [fitz.Rect(s["bbox"]) + (-0.3, -0.3, 0.3, 0.3) for s in vals + [head]])
    c1, c2 = (808.0 + 974.6) / 2, (974.6 + 1141.2) / 2
    put = lambda cx, y, t, sz, col: p.insert_text((cx - f.text_length(t, fontsize=sz) / 2, y), t, fontsize=sz,
                                                  fontname="cal", fontfile=CAL, color=col)
    hy = head["origin"][1]
    put(c1, hy, "RH X50", 10, BLUE); put(c2, hy, "RH X100", 10, BLUE)
    for (y, ss), v100 in zip(rows, X100):
        put(c1, y, "".join(s["text"] for s in ss).replace("\xa0", "").strip(), 9, INK)
        put(c2, y, v100, 9, INK)
    for y0, y1 in ((108.8, 124.5), (141.2, 211.2), (228.1, 280.6), (297.9, 756.7)):
        p.draw_line((974.6, y0), (974.6, y1), color=GRID, width=0.5)


def main():
    doc = fitz.open(SRC)
    hero(doc)
    logos(doc)
    title(doc)
    table(doc)
    doc.set_toc([])
    doc.del_xml_metadata()
    doc.set_metadata({"title": "RH X50 / RH X100 – R290 Commercial Series", "author": "REO HEATING",
                      "subject": "REO HEATING RH X50, RH X100 commercial heat pumps", "keywords": "REO HEATING, RH X50, RH X100, R290",
                      "creator": "REO HEATING", "producer": "REO HEATING"})
    doc.save(OUT, garbage=4, deflate=True, clean=True)
    print("PDF", OUT.name, round(OUT.stat().st_size / 1e6, 1), "MB")
    check(OUT)


def check(path):
    d = fitz.open(path)
    bad = re.compile(r"(?i)power\s*world|powerworld|\bPW\d|DKZLRS")
    txt = " ".join(p.get_text() for p in d)
    raw = b"".join(d.xref_stream(x) or b"" for x in range(1, d.xref_length()) if not d.xref_is_image(x))
    hits = bad.findall(txt) + bad.findall(str(d.metadata)) + re.findall(rb"(?i)powerworld|power world", raw)
    used = {n for p in d for n in re.findall(rb"/(\w+) Do", b"".join(d.xref_stream(x) for x in p.get_contents()))}
    print("kontrola: nálezy", hits or "žádné", "| štítek výrobce Im136 použit:", b"Im136" in used)


if __name__ == "__main__":
    main()
