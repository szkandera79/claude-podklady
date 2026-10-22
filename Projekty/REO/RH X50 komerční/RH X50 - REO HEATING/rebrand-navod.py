#!/usr/bin/env python3
"""Rebranding návodu k použití: Power World PW150/PW300 → REO HEATING RH X50 / RH X100.

Spouštět ze složky `RH X50 komerční` (kde leží zdrojové PDF od výrobce):
    python3 "RH X50 - REO HEATING/rebrand-navod.py"

Co skript dělá:
  * nahradí modelové kódy v textové vrstvě (redakce + vysázení náhrady v Helvetice,
    která je metricky shodná s Arialem použitým v originále),
  * na titulku doplní modelovou řádku a logo REO HEATING,
  * přepíše metadata PDF.
Výsledek: RH X50 - REO HEATING/RH-X50-navod-k-pouziti.pdf
"""
import os
import re
import sys

import fitz

SRC = 'PW_R290_Commercial_Heat_Pump_Technical_Manual_20250520 cs.pdf'
DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(DIR, 'RH-X50-navod-k-pouziti.pdf')
LOGO = os.path.join(DIR, 'logo-reo-heating.png')  # závazné logo od 22. 10. 2026 (REO/logo)

MAP = {'PW150-DKZLRS-E': 'RH X50', 'PW300-DKZLRS-E': 'RH X100'}
GREEN = (0x2E / 255, 0x6B / 255, 0x33 / 255)
# vlevo/nahoře/dole s přesahem, vpravo o kus dovnitř — jinak redakce spolkne
# znak, který na kód těsně navazuje (např. dvojtečku za názvem modelu)
PAD = (-0.4, -0.4, -0.6, 0.4)

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
                    # zachovej případné závorky kolem kódu, např. „(PW150-DKZLRS-E)“
                    needle, repl = (f'({old})', f'({new})') if f'({old})' in span['text'] else (old, new)
                    font = 'hebo' if 'Bold' in span['font'] else 'helv'
                    for rect in page.search_for(needle, clip=fitz.Rect(span['bbox']) + (-2, -2, 2, 2)):
                        jobs.append((pno, fitz.Rect(rect), repl, font, span['size']))

# nadpis 2.3 je zalomený: „ Rozměry PW150-“ / „DKZLRS-E“ na dalším řádku
page = doc[10]
jobs.append((10, fitz.Rect(page.search_for('PW150-', clip=fitz.Rect(76, 33, 172, 47))[0]), 'RH X50', 'hebo', 11.5))
jobs.append((10, fitz.Rect(56.6, 69.5, 114.0, 82.3), '', 'hebo', 11.5))
# šedý pruh na titulce = prázdný placeholder po značce výrobce
jobs.append((0, fitz.Rect(55.8, 106.2, 346.0, 130.8), 'RH X50  ·  RH X100', 'hebo', 17.0))

for pno, rect, _, _, _ in jobs:
    doc[pno].add_redact_annot(rect + PAD, fill=(1, 1, 1))
for pno in {j[0] for j in jobs}:
    doc[pno].apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
for pno, rect, new, font, size in jobs:
    if not new:
        continue
    color = GREEN if pno == 0 else (0, 0, 0)
    y = rect.y0 + size * 0.80 if pno == 0 else rect.y1 - size * 0.215
    doc[pno].insert_text((rect.x0, y), new, fontname=font, fontsize=size, color=color)

_pix = fitz.Pixmap(LOGO)
LOGO_RATIO = _pix.width / _pix.height   # nové logo ≈ 2,62 : 1
w = 104.0   # nové logo je vyšší (2,62:1) — užší, aby nenaráželo na výkres pod ním
doc[0].insert_image(fitz.Rect(56.6, 158.0, 56.6 + w, 158.0 + w / LOGO_RATIO), filename=LOGO)

doc.set_metadata({
    'title': 'RH X50 / RH X100 — návod k použití',
    'author': 'REO HEATING',
    'subject': 'DC invertorové tepelné čerpadlo vzduch–voda R290, návod k použití',
    'keywords': 'RH X50, RH X100, REO HEATING, R290, tepelné čerpadlo',
    'creator': 'REO HEATING',
    'producer': 'REO HEATING',
})
doc.save(OUT, garbage=3, deflate=True)

# ---- kontrola proti originálu ----
src, out = fitz.open(SRC), fitz.open(OUT)
norm = lambda t: re.sub(r'\s+', '', t)
problems = []
for i in range(src.page_count):
    expected = norm(src[i].get_text())
    for old, new in MAP.items():
        expected = expected.replace(old, norm(new))
    got = norm(out[i].get_text())
    if i == 0:
        expected += norm('RH X50  ·  RH X100')
    if sorted(expected) != sorted(got):      # pořadí čtení se posunem textu mění, obsah ne
        problems.append(i)
leftover = [i for i, p in enumerate(out) if re.search(r'PW\s*\d{2,3}', p.get_text())]
print(f'stran: {out.page_count} | nahrazení: {len(jobs)} | zbylé kódy PW: {leftover or "žádné"}')
print(f'poškozené strany: {problems or "žádné"}')
print(f'uloženo: {OUT}')
