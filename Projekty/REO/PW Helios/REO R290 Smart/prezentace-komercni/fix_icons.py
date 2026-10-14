#!/usr/bin/env python3
"""Ikony vložené v textu („[ikona]“): po překladu se slova posunou → ikony přesunout do mezer, které PowerPoint
skutečně vysázel. Postup: export PDF z PowerPointu → najít mezery mezi „ a “ → posunout obrázky → uložit.

    python3 fix_icons.py      # upraví REO-HEATING-…-CZ.pptx na místě
"""
import os
import re

import fitz
from pptx import Presentation
from pptx.util import Emu

from export_pdf import export

DIR = os.path.dirname(os.path.abspath(__file__))
PPTX = os.path.join(DIR, 'REO-R290-Smart_RHX20-RHX30-Pro_prezentace-CZ.pptx')
TMP = os.path.join(DIR, '_icons_check.pdf')
SLIDES = (22, 28, 29, 31)       # snímky s ikonami v řádku textu (po vložení snímku 5)
EMU_PER_PT = 12700                   # PDF z PowerPointu: 960 × 540 pt = 13,333 × 7,5 in


def gaps(page):
    """Mezery mezi „ a “ (jen mezery uvnitř) → středy (x, y) v bodech, v pořadí čtení."""
    out = []
    for b in page.get_text('rawdict')['blocks']:
        for l in b.get('lines', []):
            chars = [c for s in l['spans'] for c in s['chars']]
            for i, c in enumerate(chars):
                if c['c'] != '„':
                    continue
                j = i + 1
                while j < len(chars) and chars[j]['c'].isspace():
                    j += 1
                if j < len(chars) and chars[j]['c'] == '“' and j - i > 2:
                    x0, x1 = c['bbox'][2], chars[j]['bbox'][0]
                    y0, y1 = l['bbox'][1], l['bbox'][3]
                    out.append(((x0 + x1) / 2, (y0 + y1) / 2))
    return sorted(out, key=lambda p: (round(p[1] / 6), p[0]))


export(PPTX, TMP)
doc = fitz.open(TMP)
prs = Presentation(PPTX)
moved = []
for sno in SLIDES:
    g = gaps(doc[sno - 1])
    pics = [sh for sh in prs.slides[sno - 1].shapes
            if sh.shape_type == 13 and sh.width < Emu(500000) and sh.height < Emu(500000)]
    pics.sort(key=lambda sh: (round(sh.top / 120000), sh.left))      # pořadí čtení jako v originálu
    if len(g) != len(pics):
        print(f'snímek {sno}: mezer {len(g)}, ikon {len(pics)} – přeskočeno')
        continue
    for (cx, cy), sh in zip(g, pics):
        sh.left = int(cx * EMU_PER_PT - sh.width / 2)
        sh.top = int(cy * EMU_PER_PT - sh.height / 2)
        moved.append(sno)
prs.save(PPTX)
os.remove(TMP)
print('přesunuté ikony na snímcích:', moved)
