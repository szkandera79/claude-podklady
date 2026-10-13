#!/usr/bin/env python3
"""Krok 3 české verze: vysází přeložené segmenty (cs/chunk_*.json) zpět do PDF.

Každý přeložený segment: redakce původních řádků (obrázky a čáry zůstávají) → vložení českého HTML
do „prostoru“ segmentu (insert_htmlbox, Arial, při nedostatku místa se písmo zmenší).
    python3 build.py            # česká verze
    python3 build.py --identity # test sazby: vloží zpět anglický originál
Výstup: ../REO-R290-Smart_navod-CZ.pdf
"""
import glob
import html as htmllib
import json
import os
import re
import sys

import fitz

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, '..', 'REO-R290-Smart_navod-EN.pdf')
OUT = os.path.join(DIR, '..', 'REO-R290-Smart_navod-CZ.pdf')
FONTDIR = '/System/Library/Fonts/Supplemental'
IDENTITY = '--identity' in sys.argv
if IDENTITY:
    OUT = os.path.join(DIR, 'identity-test.pdf')

segments = json.load(open(os.path.join(DIR, 'segments.json')))
# překlady: 1. kolo (přemapované podle obsahu na aktuální id) + dopřeklad nových segmentů
tr = json.load(open(os.path.join(DIR, 'cs_v2_reused.json')))
tr.update(json.load(open(os.path.join(DIR, 'cs', 'chunk_09.json'))))
ICONS = json.load(open(os.path.join(DIR, 'icons.json')))          # ikony v řádcích textu
if not IDENTITY:
    tr.update(json.load(open(os.path.join(DIR, 'cs_icons.json'))))  # překlad se značkami {I1}…

# ruční úpravy sazby: id → (html, zarovnání, box) ; html '' = jen odstranit
OVERRIDE = {
    '0_3': ('DŮLEŽITÉ BEZPEČNOSTNÍ POKYNY<br>PŘEČTĚTE SI A DODRŽUJTE VŠECHNY POKYNY<br>TYTO POKYNY USCHOVEJTE',
            'center', (60, 719, 532, 776)),
    '54_6': ('Klikněte na ikonu ručního odmrazování „{I1}“.', None, (57, 687, 536, 712)), '54_7': ('', None, None),
    '60_5': ('', None, None),   # „“. Poté“ přesunuto do 60_4 za ikonu
    '96_4': ('', None, None), '96_5': ('', None, None), '96_6': ('', None, None),   # rozházené popisky → níže
}
CAPTIONS = [  # (strana, box, text) – popisky pod snímky aplikace na str. 96
    (96, (50, 578, 173, 616), 'Statistika spotřeby:<br>elektrická energie'),
    (96, (174, 578, 296, 616), 'Statistika spotřeby:<br>tepelný výkon'),
    (96, (298, 578, 419, 616), 'Statistika spotřeby:<br>účinnost'),
]
if not IDENTITY:
    for k, (h, a, b) in OVERRIDE.items():
        tr[k] = h

ICON_H = 1.7   # max. výška ikony v řádku (× velikost písma)

ARCH = fitz.Archive(FONTDIR)
FONTS = ("@font-face {font-family: A; src: url('Arial.ttf');}"
         "@font-face {font-family: A; src: url('Arial Bold.ttf'); font-weight: bold;}")


def plain(h):
    return htmllib.unescape(re.sub(r'<[^>]+>', '', h.replace('<br>', ' '))).strip()


doc = fitz.open(SRC)
todo = []
for s in segments:
    new = s['html'] if IDENTITY else tr.get(s['id'])
    if new is None or (not IDENTITY and new.strip() == s['html'].strip()):
        continue
    todo.append((s, new))

# 0) ikony: pixmapy si vzít před redakcí
def icon_pix(xref):
    pix = fitz.Pixmap(doc, xref)
    smask = doc.extract_image(xref).get('smask')
    if smask and not pix.alpha:
        pix = fitz.Pixmap(pix, fitz.Pixmap(doc, smask))
    if pix.colorspace and pix.colorspace.n > 3:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    return pix


moving = {} if IDENTITY else {s['id']: ICONS[s['id']]['icons'] for s, _ in todo if s['id'] in ICONS}
pixes = {ic['xref']: icon_pix(ic['xref']) for ics in moving.values() for ic in ics}

# 1) redakce původního textu
for s, _ in todo:
    page = doc[s['page']]
    for lb in s['lines']:
        r = fitz.Rect(lb)
        page.add_redact_annot(fitz.Rect(r.x0, r.y0 + r.height * 0.2, r.x1, r.y1 - r.height * 0.2), fill=False)
for pno in sorted({s['page'] for s, _ in todo}):
    doc[pno].apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
# … a pak odebrat přesouvané ikony z původních míst
for sid, ics in moving.items():
    page = doc[int(sid.split('_')[0])]
    for ic in ics:
        r = fitz.Rect(ic['bbox'])
        page.add_redact_annot(r + (1, 1, -1, -1), fill=False)
for pno in sorted({int(k.split('_')[0]) for k in moving}):
    doc[pno].apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)

# 2) sazba
arial = fitz.Font(fontfile=os.path.join(FONTDIR, 'Arial.ttf'))
arialb = fitz.Font(fontfile=os.path.join(FONTDIR, 'Arial Bold.ttf'))
shrunk, failed, placed = [], [], []
for s, new in todo:
    page = doc[s['page']]
    size = s['size']
    if s.get('toc'):
        f = arialb if s['bold'] else arial
        name = plain(new)
        R = fitz.Rect(s['rect'])
        y = s['origin'][1]
        wp = f.text_length(s['pnum'], size)
        x_end = R.x1 - wp
        wn = f.text_length(name, size)
        dot = f.text_length('.', size)
        n = max(3, int((x_end - (R.x0 + wn) - 4) / dot))
        tw = fitz.TextWriter(page.rect)
        tw.append((R.x0, y), name + ' ' + '.' * n, font=f, fontsize=size)
        tw.append((x_end, y), s['pnum'], font=f, fontsize=size)
        tw.write_text(page)
        continue
    if not new.strip():
        continue
    c = s['color']
    color = f'#{c:06x}'
    lh = min(max(s['lh'], 1.05), 1.6) if s['lh'] else 1.15
    ov = OVERRIDE.get(s['id'])
    align = ov[1] if ov and ov[1] else s['align']
    css = (FONTS + f"* {{font-family: A; font-size: {size:.2f}px; line-height: {lh:.3f}; color: {color};"
           f" margin: 0; padding: 0; text-align: {align};}} b {{font-weight: bold;}}")
    marks = []
    if s['id'] in moving:
        for k, ic in enumerate(moving[s['id']], 1):
            tag = f'qz{len(placed) + k}x'
            r0 = fitz.Rect(ic['bbox'])
            w = r0.width * min(1, ICON_H * size / r0.height)
            n = int((w + 2) / (0.278 * size)) + 1
            new = new.replace('{I%d}' % k, f'<span style="font-size:1px;color:#ffffff">{tag}</span>' + '&nbsp;' * n, 1)
            marks.append((tag, ic))
    first_x0 = s['lines'][0][0]
    indent = first_x0 - s['rect'][0] if s['id'] not in moving and first_x0 - s['rect'][0] > 3 else 0
    if indent:
        css += f' p, body, div {{text-indent: {indent:.1f}px;}}'
    box = fitz.Rect(ov[2] if ov and ov[2] else s['box'])
    # posun nahoru o rozdíl mezi horní hranou řádku a výškou písma (bbox řádku bývá vyšší)
    first = fitz.Rect(s['lines'][0])
    box.y0 = first.y0 + max(0, (first.height - size * lh) / 2)
    spare, scale = page.insert_htmlbox(box, new, css=css, archive=ARCH, scale_low=0.55)
    if spare < 0:
        spare, scale = page.insert_htmlbox(box, new, css=css, archive=ARCH, scale_low=0)
        failed.append((s['id'], round(scale, 2)))
    elif scale < 0.999:
        shrunk.append((s['id'], round(scale, 2)))
    for tag, ic in marks:
        hit = page.search_for(tag, clip=box + (-2, -2, 2, 2))
        if not hit:
            failed.append((s['id'], 'ikona?'))
            continue
        r0 = fitz.Rect(ic['bbox'])
        k = min(max(scale, 0.8), ICON_H * size * scale / r0.height)   # vysoké ikony zmenšit na ~výšku řádku
        w, h = r0.width * k, r0.height * k
        base = hit[0].y1
        cy = base - 0.33 * size * scale
        page.insert_image(fitz.Rect(hit[0].x1 + 1, cy - h / 2, hit[0].x1 + 1 + w, cy + h / 2), pixmap=pixes[ic['xref']])
        placed.append(hit[0])
        page.add_redact_annot(hit[0] + (0.1, 0.1, -0.1, -0.1), fill=False)
for pno in sorted({int(k.split('_')[0]) for k in moving}):
    doc[pno].apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)

# 2b) popisky + tabulky náhradních dílů (v originále vektorové křivky, ne text → překrýt novou tabulkou)
def box_html(page, rect, html, size, align='center', bold=False, valign=True):
    css = (FONTS + f"* {{font-family: A; font-size: {size}px; line-height: 1.15; margin: 0;"
           f" text-align: {align}; {'font-weight: bold;' if bold else ''}}}")
    r = fitz.Rect(rect)
    if valign:
        nl = html.count('<br>') + 1
        r.y0 += max(0, (r.height - nl * size * 1.15) / 2)
    page.insert_htmlbox(r, html, css=css, archive=ARCH, scale_low=0.4)


def spare_table(page, names_left, names_right):
    H, V = [], []
    for dr in page.get_drawings():
        for it in dr['items']:
            if it[0] == 'l' and abs(it[1].y - it[2].y) < 0.5 and abs(it[1].x - it[2].x) > 150:
                H.append(it[1].y)
            if it[0] == 'l' and abs(it[1].x - it[2].x) < 0.5 and abs(it[1].y - it[2].y) > 150:
                V.append((it[1].x, min(it[1].y, it[2].y), max(it[1].y, it[2].y)))
    cols = sorted({round(x, 1) for x, y0, y1 in V if y0 > 300})     # svislé čáry jen tabulky (ne rámu)
    top = min(y0 for x, y0, y1 in V if y0 > 300)
    bot = max(y1 for x, y0, y1 in V if y0 > 300)
    ys = []
    for y in sorted(y for y in H if top - 1 <= y <= bot + 1):
        if not ys or y - ys[-1] > 2:
            ys.append(y)
    rows = list(zip(ys[:-1], ys[1:]))
    assert len(rows) == len(names_left) + 1, (page.number, len(rows), len(names_left))
    right = max(it[2].x for dr in page.get_drawings() for it in dr['items']
                if it[0] == 'l' and abs(it[1].y - it[2].y) < 0.5 and top - 1 <= it[1].y <= bot + 1)
    x = cols[:4] + [right]
    for ri, (y0, y1) in enumerate(rows):
        for ci, name in ((0, 'Č.'), (1, 'Náhradní díl'), (2, 'Č.'), (3, 'Náhradní díl')) if ri == 0 else \
                ((1, names_left[ri - 1]), (3, names_right[ri - 1])):
            cell = fitz.Rect(x[ci] + 0.8, y0 + 0.8, x[ci + 1] - 0.8, y1 - 0.8)
            page.draw_rect(cell, color=None, fill=(1, 1, 1), overlay=True)
            if name:
                box_html(page, cell + (1, 0, -1, 0), name, 8.5, bold=(ri == 0))


if not IDENTITY:
    for pno, rect, html in CAPTIONS:
        box_html(doc[pno], rect, html, 8.0, valign=False)
    SP = json.load(open(os.path.join(DIR, 'nahradni-dily.json')))
    for pno, t in SP.items():
        spare_table(doc[int(pno)], t['left'], t['right'])

# 3) záložky + metadata
if not IDENTITY:
    heads = {}
    for s in segments:
        if s['id'] in tr:
            heads[re.sub(r'\s+', ' ', plain(s['html']))] = plain(tr[s['id']])
    toc = []
    for lvl, t, p in doc.get_toc():
        key = re.sub(r'\s+', ' ', t).strip()
        if key in heads:
            t = heads[key]
        else:
            parts = re.split(r'\s{3,}', t.strip())
            t = ' – '.join(heads.get(x.strip(), x.strip()) for x in parts)
        toc.append([lvl, t, p])
    doc.set_toc(toc)
    doc.set_metadata({
        'title': 'REO R290 Smart (RH06–RH16, RHX20 Pro, RHX30 Pro) — Návod k instalaci a obsluze',
        'author': 'REO HEATING',
        'subject': 'Invertorové tepelné čerpadlo vzduch–voda R290, návod k instalaci a obsluze',
        'keywords': 'REO R290 Smart, RH06, RH08, RH10, RH12, RH14, RH16, RHX20 Pro, RHX30 Pro, REO HEATING, R290, tepelné čerpadlo',
        'creator': 'REO HEATING', 'producer': 'REO HEATING'})
doc.save(OUT + '.tmp', garbage=4, deflate=True)   # garbage=4 sloučí stovky kopií Arialu
doc.close()
doc = fitz.open(OUT + '.tmp')
doc.subset_fonts()
doc.save(OUT, garbage=4, deflate=True, deflate_fonts=True)
os.remove(OUT + '.tmp')
print(f'vysázeno: {len(todo)} | zmenšeno (<100 %): {len(shrunk)} | nevešlo se ani na 55 %: {len(failed)}')
if failed:
    print('  ', failed[:40])
print(f'uloženo: {OUT}')
