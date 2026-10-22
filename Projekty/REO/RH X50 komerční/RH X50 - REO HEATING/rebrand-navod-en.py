#!/usr/bin/env python3
"""Rebranding anglického návodu výrobce: PW150/PW300 → REO HEATING RH X50 / RH X100.

Spouštět ze složky `RH X50 komerční` (kde leží zdrojové PDF od výrobce):
    python3 "RH X50 - REO HEATING/rebrand-navod-en.py"

Postup stejný jako u české verze (rebrand-navod.py): náhrada modelových kódů v textové vrstvě,
modelová řádka a logo REO HEATING na titulce, oprava snímků aplikace (název Wi‑Fi výrobce),
záložky a metadata. Výsledek: RH X50 - REO HEATING/RH-X50-operating-manual-EN.pdf
"""
import os
import re
import sys
import tempfile

import fitz

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ssid_fix  # noqa: E402

SRC = 'PW_R290_Commercial_Heat_Pump_Technical_Manual_20250520.pdf'
DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(DIR, 'RH-X50-operating-manual-EN.pdf')
LOGO = os.path.join(DIR, 'logo-reo-heating.png')  # závazné logo REO HEATING (REO/logo)

MAP = {'PW150-DKZLRS-E': 'RH X50', 'PW300-DKZLRS-E': 'RH X100'}
GREEN = (0x34 / 255, 0xA2 / 255, 0x63 / 255)   # zelená REO HEATING #34A263
PAD = (-0.4, -0.4, -0.6, 0.4)
COVER_LINE = 'RH X50  ·  RH X100'

if not os.path.exists(SRC):
    sys.exit(f'Nenalezen zdroj: {SRC} — spusť skript ze složky „RH X50 komerční“.')

doc = fitz.open(SRC)
jobs = []  # (index strany, obdélník, nový text, font, velikost)

for pno, page in enumerate(doc):
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines', []):
            for span in line['spans']:
                for old, new in MAP.items():
                    if old not in span['text']:
                        continue
                    needle, repl = (f'({old})', f'({new})') if f'({old})' in span['text'] else (old, new)
                    font = 'hebo' if 'Bold' in span['font'] else 'helv'
                    for rect in page.search_for(needle, clip=fitz.Rect(span['bbox']) + (-2, -2, 2, 2)):
                        jobs.append((pno, fitz.Rect(rect), repl, font, span['size'], span['origin'][1]))

# šedý pruh na titulce = prázdné místo po značce výrobce → modelová řádka
jobs.append((0, fitz.Rect(55.8, 111.5, 346.0, 135.4), COVER_LINE, 'hebo', 18.0, None))

for pno, rect, *_ in jobs:
    r = rect + PAD
    if pno:   # horní okraj o pětinu níž — jinak zasáhne řádek nad kódem (str. 25: „Wiring Diagram“)
        r.y0 = rect.y0 + rect.height * 0.2
    doc[pno].add_redact_annot(r, fill=(1, 1, 1))
for pno in {j[0] for j in jobs}:
    doc[pno].apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
for pno, rect, new, font, size, base in jobs:
    color = GREEN if pno == 0 else (0, 0, 0)
    y = rect.y0 + size * 0.85 if base is None else base   # účaří původního textu
    doc[pno].insert_text((rect.x0, y), new, fontname=font, fontsize=size, color=color)

_pix = fitz.Pixmap(LOGO)
w = 104.0
doc[0].insert_image(fitz.Rect(56.6, 168.0, 56.6 + w, 168.0 + w * _pix.height / _pix.width), filename=LOGO)

with tempfile.TemporaryDirectory() as tmp:
    n_img = ssid_fix.fix_document(doc, ssid_fix.EN, tmp)
    doc.set_toc(doc.get_toc())  # záložky výrobce neobsahují značku ani kódy — ponechány
    doc.set_metadata({
        'title': 'RH X50 / RH X100 — Operating Instruction Manual',
        'author': 'REO HEATING',
        'subject': 'DC inverter air-to-water heat pump R290, operating instruction manual',
        'keywords': 'RH X50, RH X100, REO HEATING, R290, heat pump',
        'creator': 'REO HEATING',
        'producer': 'REO HEATING',
    })
    doc.del_xml_metadata()
    doc.save(OUT, garbage=3, deflate=True)

# ---- kontrola proti originálu ----
src, out = fitz.open(SRC), fitz.open(OUT)
norm = lambda t: re.sub(r'\s+', '', t)
problems = []
for i in range(src.page_count):
    expected = norm(src[i].get_text())
    for old, new in MAP.items():
        expected = expected.replace(old, norm(new))
    if i == 0:
        expected += norm(COVER_LINE)
    if sorted(expected) != sorted(norm(out[i].get_text())):
        problems.append(i + 1)
leftover = [i + 1 for i, p in enumerate(out) if re.search(r'PW\s*\d{2,3}|DKZLRS|power\s*world', p.get_text(), re.I)]
meta = [v for v in out.metadata.values() if v and re.search(r'PW|power', v, re.I)]
print(f'stran: {out.page_count} | nahrazení textu: {len(jobs)} | opravené snímky: {n_img}')
print(f'zbylé odkazy na výrobce: {leftover or "žádné"} | metadata: {meta or "čistá"} | záložky: {len(out.get_toc())}')
print(f'strany s odchylkou textu: {problems or "žádné"}')
print(f'uloženo: {OUT}')
