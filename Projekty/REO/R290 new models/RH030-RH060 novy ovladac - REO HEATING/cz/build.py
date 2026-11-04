#!/usr/bin/env python3
"""Krok 3 české verze: vysází přeložené segmenty (cs/chunk_*.json) zpět do PDF.

Každý přeložený segment: redakce původních řádků (obrázky a čáry zůstávají) → vložení českého HTML
do „prostoru“ segmentu (insert_htmlbox, Arial, při nedostatku místa se písmo zmenší).
    python3 build.py            # česká verze
    python3 build.py --identity # test sazby: vloží zpět anglický originál
Výstup: ../RH030-RH060-navod-CZ_REO-HEATING.pdf
Zdroj: originál výrobce z 2024 (novější ovladač, „New Version Software“) – přeznačení modelů je součástí překladu.
"""
import glob
import html as htmllib
import json
import os
import re
import sys

import fitz

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, '..', '..', 'Power World New Version Software R290 Heat Pump.pdf')
OUT = os.path.join(DIR, '..', 'RH030-RH060-novy-ovladac-navod-CZ_REO-HEATING.pdf')
LOGO = os.path.join(DIR, '..', 'logo-reo-heating.png')   # závazné logo od 22. 10. 2026 (REO/logo)
GREEN = (0x2E / 255, 0x6B / 255, 0x33 / 255)
COVER_LINE = 'RH030 – RH060  ·  novější ovladač'
FONTDIR = '/System/Library/Fonts/Supplemental'
IDENTITY = '--identity' in sys.argv
if IDENTITY:
    OUT = os.path.join(DIR, 'identity-test.pdf')

segments = json.load(open(os.path.join(DIR, 'segments.json')))
tr = {}
for f in sorted(glob.glob(os.path.join(DIR, 'cs', 'chunk_*.json'))):
    tr.update(json.load(open(f)))
for k, v in tr.items():
    v = v.replace('╋', '+').replace('výrobce nebo', 'dodavatele nebo').replace('kontaktujte výrobce', 'kontaktujte dodavatele')
    tr[k] = re.sub(r'"([^"<>]*)"', r'„\1“', v).replace('”', '“')
ICONS = json.load(open(os.path.join(DIR, 'icons.json')))          # ikony v řádcích textu
if not IDENTITY:
    tr.update(json.load(open(os.path.join(DIR, 'cs_icons.json'))))  # překlad se značkami {I1}…

# ruční úpravy sazby: id → (html, zarovnání, box) ; html '' = jen odstranit
OVERRIDE = {
    '0_2': ('DŮLEŽITÉ BEZPEČNOSTNÍ POKYNY<br>PŘEČTĚTE SI A DODRŽUJTE VŠECHNY POKYNY<br>TYTO POKYNY USCHOVEJTE',
            'center', (60, 688, 535, 760)),
    '0_3': ('Verze: 1.0 · česká verze 11/2026', None, None),
    '0_4': ('', None, None),
    '3_9': ('', None, None),
    '3_10': ('Elektrické napájení výrobku musí instalovat osoba s odbornou kvalifikací v elektrotechnice v souladu s platnými předpisy a normami ČSN / EN a místními předpisy. Nesprávná instalace vytváří elektrické nebezpečí, které může způsobit smrt nebo vážné zranění uživatelů, instalačních techniků či dalších osob úrazem elektrickým proudem a také škodu na majetku. Přečtěte si a dodržujte konkrétní pokyny v tomto návodu.', None, (130.2, 470.8, 559.3, 581.1)),
    '3_11': ('', None, None),
    '3_12': ('<b>VAROVÁNÍ –</b> Ke snížení rizika zranění nedovolte dětem výrobek používat, pokud nejsou neustále pod dohledem.', None, (86.6, 581.4, 559.3, 627.3)),
    '3_13': ('', None, None),
    '8_2': ('<b>Jednotky: mm</b>', 'right', (400, 219.7, 540, 240)),
    '9_0': ('<b>RH040 (1fázové)  ·  RH040 (3fázové)</b>', None, None),
    '9_5': ('<b>RH050 (1fázové)  ·  RH050 (3fázové)</b>', None, None),
    '10_0': ('<b>RH055 / RH060 (1fázové)  ·  RH055 / RH060 (3fázové)</b>', None, None),
    '10_6': ('<b>RH070 (1fázové)  ·  RH070 (3fázové)</b>', None, None),
    '11_1': ('<b>RH030 (1fázové)  ·  RH040 (1fázové)  ·  RH040 (3fázové)</b>', None, None),
    '12_0': ('<b>RH050 (1fázové)  ·  RH050 (3fázové)</b>', None, None),
    '13_0': ('<b>RH055 / RH060 / RH070 (1fázové)  ·  RH055 / RH060 / RH070 (3fázové)</b>', None, None),
}
CAPTIONS = [  # (strana, box, html, velikost, zarovnání, tučně)
    (3, (59.5, 427.5, 153.8, 452), 'NEBEZPEČÍ', 13.5, 'center', True),
    (3, (162, 432, 540, 448), '– Riziko úrazu elektrickým proudem.', 11, 'left', True),
]
FONT = os.path.join('/System/Library/Fonts/Supplemental', 'Arial.ttf')
FONTB = os.path.join('/System/Library/Fonts/Supplemental', 'Arial Bold.ttf')


def _repl(D, F, box, text, size, xy=None, center=False, fill=(0, 0, 0)):
    D.rectangle(box, fill='white')
    f = F(size)
    lines = text.split('\n')
    lh = size * 1.18
    y0 = (box[1] + box[3]) / 2 - lh * len(lines) / 2 if center else xy[1]
    for i, t in enumerate(lines):
        x = (box[0] + box[2]) / 2 - D.textlength(t, font=f) / 2 if center else xy[0]
        D.text((x, y0 + i * lh), t, fill=fill, font=f)


def img_cascade(im, D, F):
    """Schéma kaskády: kód ovladače výrobce „PW58330“ pryč, popisky česky."""
    _repl(D, F, (28, 352, 308, 488), 'Kabelový\novladač', 40, center=True)
    D.rectangle((25, 349, 311, 491), outline=(60, 60, 60), width=2)
    _repl(D, F, (48, 92, 160, 136), 'Hlavní řídicí\ndeska', 17, xy=(50, 92))
    _repl(D, F, (386, 94, 500, 116), 'Podřízená deska 1', 16, xy=(388, 95))
    D.rectangle((718, 94, 832, 116), fill='white')   # v PDF je přes obrázek textová vrstva „Slave board 7“ (19_2)
    for box in ((30, 280, 228, 326), (345, 258, 524, 304)):
        _repl(D, F, (box[0], box[1], box[2], box[3]), 'Komunikační\nvedení (2 vodiče)', 17, xy=(box[0] + 2, box[1] + 1))
    _repl(D, F, (472, 346, 684, 366), 'Nastavení DIP', 15, center=True)
    for i, t in enumerate(['Hlavní'] + [f'Podř. {k}' for k in range(1, 8)]):
        y = 389 + i * 21.2
        _repl(D, F, (472, y, 508, y + 14), t, 9, xy=(473, y + 1))


def img_wifi_list(im, D, F):
    """Snímek telefonu: sítě „pwjsb“ / „PWAB“ (výrobce) → neutrální názvy."""
    _repl(D, F, (28, 558, 300, 588), 'Soused-WiFi', 22, xy=(30, 560), fill=(28, 28, 30))
    _repl(D, F, (28, 632, 300, 662), 'Domov-5G', 22, xy=(30, 634), fill=(28, 28, 30))


def img_wifi_pass(im, D, F):
    """Snímek aplikace: síť a heslo „pwjsb…“ (výrobce) → neutrální."""
    _repl(D, F, (225, 585, 880, 672), 'MojeWiFi', 46, xy=(238, 598), fill=(28, 28, 30))
    _repl(D, F, (225, 765, 880, 852), 'heslo-wifi', 46, xy=(238, 778), fill=(28, 28, 30))


IMG_EDITS = {184: img_cascade, 394: img_wifi_list, 399: img_wifi_pass}
# svislé popisky v obr. 2 a 3 (str. 16 a 17 PDF, text otočený o 90°)
FIG2 = {
    'Hot water tank': 'Zásobník TUV', 'Magnesiumrod': 'Mg anoda', 'sensor': 'čidlo',
    'Hot water outlet': 'Výstup teplé vody', 'Cold water inlet': 'Vstup studené vody', 'Limber hole': 'Odvodnění',
    'Safety valve': 'Pojistný ventil', 'Floor pipe': 'Podlah. topení', 'Radiator': 'Radiátor', 'Fan coil': 'Fancoil',
    '3-way valve': 'Trojcestný ventil', 'Water pump': 'Oběh. čerpadlo', 'Water tank': 'Akum. nádrž',
}
FIG_PAGES = {16: ('Obrázek 2', 170), 17: ('Obrázek 3', 174)}   # strana → (popisek, xref obrázku „Figure n“)
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

# 0b) anotace zvýrazňovače z originálu pryč
for page in doc:
    for an in list(page.annots()):
        page.delete_annot(an)

# 1) redakce původního textu
for s, _ in todo:
    page = doc[s['page']]
    for lb in s['lines']:
        r = fitz.Rect(lb)
        page.add_redact_annot(fitz.Rect(r.x0, r.y0 + r.height * 0.2, r.x1, r.y1 - r.height * 0.2), fill=False)
for pno in sorted({s['page'] for s, _ in todo}):
    doc[pno].apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
# zvýrazňovač z originálu (žluté / červené pozadí textu ve WPS) → bílé, text se vysází nad něj
HILITE = [(1.0, 1.0, 0.0), (1.0, 0.004, 0.004), (0.0, 0.502, 0.0)]
if not IDENTITY:
    for page in doc:
        rects = [dr['rect'] for dr in page.get_drawings() if dr.get('fill') and dr['rect'].height < 25
                 and any(all(abs(a - b) < 0.002 for a, b in zip(dr['fill'], h)) for h in HILITE)]
        if not rects:
            continue
        # text, který zůstal (nepřekládaný: kódy, čísla), se pod bílou překryje → po překrytí ho vrátit
        keep = [sp for bl in page.get_text('dict')['blocks'] for l in bl.get('lines', []) if l['dir'] == (1.0, 0.0)
                for sp in l['spans'] if sp['text'].strip() and any(fitz.Rect(sp['bbox']).intersects(r) for r in rects)]
        for r in rects:
            page.draw_rect(r + (-0.6, -0.6, 0.6, 0.6), color=None, fill=(1, 1, 1), overlay=True)
        for sp in keep:
            bold = 'Bold' in sp['font'] or bool(sp['flags'] & 16)
            c = sp['color']
            page.insert_text(sp['origin'], sp['text'], fontsize=sp['size'],
                             fontname='arialbd' if bold else 'arial',
                             fontfile=os.path.join(FONTDIR, 'Arial Bold.ttf' if bold else 'Arial.ttf'),
                             color=((c >> 16 & 255) / 255, (c >> 8 & 255) / 255, (c & 255) / 255))
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
    for pno, rect, html, size, align, bold in CAPTIONS:
        box_html(doc[pno], rect, html, size, align=align, bold=bold)
    SP = json.load(open(os.path.join(DIR, 'nahradni-dily.json')))
    for pno, t in SP.items():
        spare_table(doc[int(pno)], t['left'], t['right'])

# 2c) svislé popisky v obr. 2, kódy BOM, titulka
if not IDENTITY:
    for pno, (ftxt, fx) in FIG_PAGES.items():
        p = doc[pno]
        labels = [(fitz.Rect(l['bbox']), sp) for b in p.get_text('dict')['blocks'] for l in b.get('lines', [])
                  if l['dir'] == (0.0, -1.0) for sp in l['spans'] if sp['text'].strip() in FIG2]
        for r, sp in labels:
            p.add_redact_annot(r, fill=False)
        p.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
        for r, sp in labels:
            cs = FIG2[sp['text'].strip()]
            size = sp['size']
            size = min(size, size * 1.4 * r.height / max(arial.text_length(cs, size), 1))
            p.insert_text(fitz.Point(sp['origin']), cs, fontsize=size, fontname='arial',
                          fontfile=os.path.join(FONTDIR, 'Arial.ttf'), rotate=90)
        # „Figure n“ je v originále obrázek → překrýt a vysázet česky (svisle, tučně)
        fr = next(fitz.Rect(x['bbox']) for x in p.get_image_info(xrefs=True) if x['xref'] == fx)
        p.draw_rect(fr + (-2, -2, 2, 2), color=None, fill=(1, 1, 1))
        fs = 20
        p.insert_text(((fr.x0 + fr.x1) / 2 + fs * 0.36, (fr.y0 + fr.y1) / 2 + arialb.text_length(ftxt, fs) / 2), ftxt,
                      fontsize=fs, fontname='arialbd', fontfile=os.path.join(FONTDIR, 'Arial Bold.ttf'), rotate=90)

    # interní kódy BOM výrobce CP-RW… → RH-RW… (stejně jako na štítku REO)
    p = doc[6]
    bom = [(fitz.Rect(sp['bbox']), sp) for b in p.get_text('dict')['blocks'] for l in b.get('lines', [])
           for sp in l['spans'] if sp['text'].strip().startswith('CP-RW')]
    for r, sp in bom:
        p.add_redact_annot(r + (0.3, 1.2, -0.3, -1.2), fill=False)
    p.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
    for r, sp in bom:
        t = sp['text'].strip().replace('CP-RW', 'RH-RW')
        x = (r.x0 + r.x1) / 2 - arial.text_length(t, sp['size']) / 2
        p.insert_text((x, sp['origin'][1]), t, fontsize=sp['size'], fontname='arial',
                      fontfile=os.path.join(FONTDIR, 'Arial.ttf'))

    # titulka: šedý pruh → modelová řada + logo REO HEATING
    cover = doc[0]
    cover.draw_rect(fitz.Rect(55.5, 110.6, 346.5, 135.8), color=None, fill=(1, 1, 1))
    cover.insert_text((56.6, 129.0), COVER_LINE, fontname='arialbd', fontsize=17.0, color=GREEN,
                      fontfile=os.path.join(FONTDIR, 'Arial Bold.ttf'))
    w = 112.0
    lp = fitz.Pixmap(LOGO)
    cover.insert_image(fitz.Rect(56.6, 172.0, 56.6 + w, 172.0 + w * lp.height / lp.width), filename=LOGO)

    # rastrové obrázky
    import io
    from PIL import Image, ImageDraw, ImageFont
    for xref, fn in IMG_EDITS.items():
        im = Image.open(io.BytesIO(doc.extract_image(xref)['image'])).convert('RGB')
        fn(im, ImageDraw.Draw(im), lambda sz: ImageFont.truetype(FONT, sz))
        buf = io.BytesIO()
        im.save(buf, 'JPEG', quality=92)
        pno = next(p.number for p in doc if any(x[0] == xref for x in p.get_images()))
        doc[pno].replace_image(xref, stream=buf.getvalue())

# 3) záložky (podle obsahu na str. 3: „- n -“ = strana n + 2 v PDF) + metadata
if not IDENTITY:
    toc, chap = [], None
    for s in segments:
        if s['page'] != 2 or s['id'] not in tr:
            continue
        t = plain(tr[s['id']])
        if not s.get('toc'):
            if t.startswith('Kapitola'):
                chap = t                   # „Kapitola 1“ + následující „Úvod“ → jedna položka 1. úrovně
            continue
        pg = int(re.sub(r'\D', '', s['pnum'])) + 2
        if chap:
            toc.append([1, f'{chap} – {t}', pg])
            chap = None
        else:
            toc.append([2 if toc else 1, t, pg])
    doc.set_toc(toc)
    doc.set_metadata({
        'title': 'REO HEATING RH030–RH060 (novější ovladač) — Návod k instalaci a obsluze',
        'author': 'REO HEATING',
        'subject': 'Invertorové tepelné čerpadlo vzduch–voda R290, návod k instalaci a obsluze',
        'keywords': 'RH030, RH040, RH050, RH055, RH060, RH070, novější ovladač, REO HEATING, R290, tepelné čerpadlo',
        'creator': 'REO HEATING', 'producer': 'REO HEATING'})
    doc.del_xml_metadata()
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

# 4) kontrola: nezůstal odkaz na výrobce ani nepřeložený segment
if not IDENTITY:
    out = fitz.open(OUT)
    brand = re.compile(r'power\s*world|PW\s*0\d\d|PW58330|DKZLRS|CP-RW|pwjsb', re.I)
    left = [i + 1 for i, p in enumerate(out) if brand.search(p.get_text())]
    meta = [k for k, v in out.metadata.items() if v and brand.search(v)]
    miss = [s['id'] for s in segments if s['id'] not in tr]
    print(f'odkazy na výrobce: strany {left or "žádné"} | metadata {meta or "žádná"} | nepřeloženo: {miss or "nic"}')
