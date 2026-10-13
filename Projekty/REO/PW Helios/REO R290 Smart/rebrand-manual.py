#!/usr/bin/env python3
"""Rebranding návodu výrobce na řadu REO R290 Smart: PW06–PW16 / PW20 / PW30 → REO HEATING RH06–RH16 / RHX20 Pro / RHX30 Pro.

Spouštět odkudkoli:
    python3 "REO R290 Smart/rebrand-manual.py"

Co skript dělá:
  * modelové kódy PWxx-DKXLRE1-H8 / -DKXLRE3-H8 → RHxx (1-phase) / RHxx (3-phase),
    PW20 → RHX20 Pro, PW30 → RHX30 Pro (typový suffix výrobce se neuvádí; RHX20 Pro / RHX30 Pro jsou jen 3f),
  * „power world’s services“ v tabulkách chyb → „REO HEATING services“,
  * každý dotčený span se vyredaguje a vysází znovu (Helvetica = metricky Arial,
    Times Bold v nadpisech schémat), v tabulkách centrovaně na původní střed buňky,
  * titulka: šedý pruh → modelová řádka + logo REO HEATING,
  * záložky (osnova) a metadata PDF.
Výsledek: REO-R290-Smart_navod-EN.pdf
"""
import os
import re

import fitz

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, '..', 'aTechnical Manual Helios Residential and Commercial.pdf')
OUT = os.path.join(DIR, 'REO-R290-Smart_navod-EN.pdf')
LOGO = os.path.join(DIR, 'logo-reoheating.png')
GREEN = (0x2E / 255, 0x6B / 255, 0x33 / 255)
SERIES = 'REO R290 Smart'
COVER_LINE = SERIES                                   # zelený řádek pod nadpisem
MODELS_LINE = 'RH06 – RH16  ·  RHX20 Pro  ·  RHX30 Pro'          # modely pod logem
TABLE_PAGES = {9, 10, 11, 30}  # 0-based: specifikace + tabulka napájení → centrovat
BIG = {'20': 'RHX20 Pro', '30': 'RHX30 Pro'}


def rename(text):
    """Přepíše text spanu; vrací None, pokud se ho rebrand netýká."""
    new = text
    # celé kódy, i skupinové „PW08/10/12/14/16-DKXLRE1-H8“
    def full(m):
        nums, ph = m.group(1).split('/'), m.group(2)
        if all(n in BIG for n in nums):
            return '/'.join(BIG[n] for n in nums)
        return 'RH' + '/'.join(nums) + (f' ({ph}-phase)' if ph else '')
    new = re.sub(r'PW(\d{2}(?:/\d{2})*)-DKXLRE(\d)-H8', full, new)
    # rozdělené buňky tabulky: „PW06-DKXLR“ + „E1-H8“, „PW08-DKXLRE3“ + „-H8“
    new = re.sub(r'^PW(\d{2})-DKXL(?:R|RE\d)?$', lambda m: BIG.get(m.group(1), 'RH' + m.group(1)), new)
    new = re.sub(r'^(?:R?E(\d))?-?H8$', lambda m: f'{m.group(1) or 3}-phase', new)
    # holé kódy v tabulce napájení
    new = re.sub(r'^PW(\d{2})$', lambda m: BIG.get(m.group(1), 'RH' + m.group(1)), new)
    new = re.sub(r'power world’s', 'REO HEATING', new, flags=re.I)
    return None if new == text else new


def font_for(span):
    f = span['font']
    if 'Times' in f:
        return 'tibo' if 'Bold' in f else 'tiro'
    return 'hebo' if 'Bold' in f else 'helv'


doc = fitz.open(SRC)
jobs = []  # (strana, bbox, origin, nový text, font, velikost, barva, centrovat)
for pno, page in enumerate(doc):
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines', []):
            for s in line['spans']:
                new = rename(s['text'])
                if new is None:
                    continue
                c = s['color']
                rgb = ((c >> 16) / 255, ((c >> 8) & 255) / 255, (c & 255) / 255)
                jobs.append((pno, fitz.Rect(s['bbox']), fitz.Point(s['origin']), new,
                             font_for(s), s['size'], rgb, pno in TABLE_PAGES))

for pno, bbox, *_ in jobs:
    r = fitz.Rect(bbox.x0 + 0.3, bbox.y0 + 1.5, bbox.x1 - 0.3, bbox.y1 - 1.5)
    doc[pno].add_redact_annot(r, fill=False)
for pno in {j[0] for j in jobs}:
    doc[pno].apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                              graphics=fitz.PDF_REDACT_LINE_ART_NONE)
for pno, bbox, origin, new, font, size, rgb, center in jobs:
    if not new:
        continue
    x = origin.x
    if pno == 30:  # tabulka napájení: úzký sloupec modelu (≈ 52 pt) → „RHX20 Pro“ zmenšit, ať nepřeteče
        size = min(size, size * 46 / fitz.get_text_length(new, fontname=font, fontsize=size))
    if center:
        x = (bbox.x0 + bbox.x1) / 2 - fitz.get_text_length(new, fontname=font, fontsize=size) / 2
    doc[pno].insert_text((x, origin.y), new, fontname=font, fontsize=size, color=rgb)

# ---- titulka: šedý pruh (prázdné místo po značce výrobce) → modelová řádka + logo ----
cover = doc[0]
cover.draw_rect(fitz.Rect(55.0, 110.0, 347.0, 136.5), color=None, fill=(1, 1, 1))
# Arial Bold ze systému — base14 Helvetica neumí pomlčku „–“
cover.insert_text((56.6, 129.0), COVER_LINE, fontname='arialbd', fontsize=17.0, color=GREEN,
                  fontfile='/System/Library/Fonts/Supplemental/Arial Bold.ttf')
w = 112.0
cover.insert_image(fitz.Rect(56.6, 172.0, 56.6 + w, 172.0 + w * 582 / 1610), filename=LOGO)
cover.insert_text((56.6, 172.0 + w * 582 / 1610 + 22), MODELS_LINE, fontname='arialbd', fontsize=12.0,
                  color=(0.33, 0.33, 0.33), fontfile='/System/Library/Fonts/Supplemental/Arial Bold.ttf')

# ---- záložky ----
doc.set_toc([[lvl, rename(t) or t, p] for lvl, t, p in doc.get_toc()])

doc.set_metadata({
    'title': 'REO R290 Smart (RH06–RH16, RHX20 Pro, RHX30 Pro) — Operating Instruction Manual',
    'author': 'REO HEATING',
    'subject': 'DC inverter air-to-water heat pump R290, operating instruction manual',
    'keywords': 'REO R290 Smart, RH06, RH08, RH10, RH12, RH14, RH16, RHX20 Pro, RHX30 Pro, REO HEATING, R290, heat pump',
    'creator': 'REO HEATING',
    'producer': 'REO HEATING',
})
doc.del_xml_metadata()
doc.save(OUT, garbage=3, deflate=True)

# ---- kontrola ----
src, out = fitz.open(SRC), fitz.open(OUT)
norm = lambda t: re.sub(r'\s+', '', t)
problems = []
for i in range(src.page_count):
    exp = ''.join(norm(rename(s['text']) or s['text'])
                  for b in src[i].get_text('dict')['blocks'] for l in b.get('lines', []) for s in l['spans'])
    if i == 0:
        exp += norm(COVER_LINE) + norm(MODELS_LINE)
    if sorted(exp) != sorted(norm(out[i].get_text())):
        problems.append(i + 1)
brand = re.compile(r'power\s*world|PW\s*-?\d{2}|DKXL|H8\b', re.I)
left = [i + 1 for i, p in enumerate(out) if brand.search(p.get_text())]
meta = [k for k, v in out.metadata.items() if v and brand.search(v)]
toc = [t for t in out.get_toc() if brand.search(t[1])]
print(f'stran: {out.page_count} | nahrazených spanů: {len(jobs)}')
print(f'zbylé odkazy na výrobce: text {left or "žádné"} | metadata {meta or "žádná"} | záložky {toc or "žádné"}')
print(f'strany s odchylkou textu: {problems or "žádné"}')
print(f'uloženo: {OUT}')
