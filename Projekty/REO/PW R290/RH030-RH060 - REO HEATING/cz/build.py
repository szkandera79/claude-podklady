#!/usr/bin/env python3
"""Krok 3 české verze: vysází přeložené segmenty (cs/chunk_*.json) zpět do PDF.

Každý přeložený segment: redakce původních řádků (obrázky a čáry zůstávají) → vložení českého HTML
do „prostoru“ segmentu (insert_htmlbox, Arial, při nedostatku místa se písmo zmenší).
    python3 build.py            # česká verze
    python3 build.py --identity # test sazby: vloží zpět anglický originál
Výstup: ../RH030-RH060-navod-CZ_REO-HEATING.pdf
Zdroj: originál výrobce z 2022 (starší ovladač) – přeznačení modelů je součástí překladu.
"""
import glob
import html as htmllib
import json
import os
import re
import sys

import fitz

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, '..', '..', 'Power World R290 Heat Pump User Manual.pdf')
OUT = os.path.join(DIR, '..', 'RH030-RH060-navod-CZ_REO-HEATING.pdf')
LOGO = os.path.join(DIR, '..', 'logo-reo-heating.png')   # závazné logo od 22. 10. 2026 (REO/logo)
GREEN = (0x2E / 255, 0x6B / 255, 0x33 / 255)
COVER_LINE = 'RH030  ·  RH040  ·  RH050  ·  RH060'
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
    '3_9': ('', None, None),            # „NEBEZPEČÍ“ do rámečku → CAPTIONS
    '3_12': ('<b>VAROVÁNÍ –</b> Ke snížení rizika zranění nedovolte dětem výrobek používat, pokud nejsou neustále pod dohledem.',
             None, (86.6, 583.4, 559.3, 629.4)),
    '3_13': ('', None, None),
    '7_2': ('<b>Jednotky: mm</b>', 'right', (400, 239.5, 540, 262)),
    '8_5': ('<b>RH050 (1fázové / 3fázové)</b>', None, None),
    '10_0': ('<b>Rozpad dílů</b><br><b>RH030</b>', None, None),
    '11_0': ('<b>RH050 (1fázové / 3fázové)</b>', None, None),
    '21_1': ('<b>Obsluha tepelného čerpadla</b>', None, (250, 32.0, 559.3, 68.9)),
    '23_0': ('Run the curve', 'left', None),
    '24_4': ('◎Stiskněte', None, None),
    '24_5': ('na hlavní obrazovce – otevře se nastavení hodin (viz níže).<br>◎Stiskem data (sloupec Rok/Měsíc/Den) nebo času '
             '(sloupec Hodina:Minuta) se zobrazí klávesnice pro zadání hodnoty. Stiskem dne (sloupec Weekday) přepínáte Po–Ne.'
             '<br>◎Tlačítkem „CONFIRM“ uložíte a odejdete, tlačítkem „CANCEL“ odejdete bez uložení.', None, None),
    '29_47': ('0 – snížení frekvence po dosažení teploty<br>1 – bez snížení frekvence', 'left', (310, 391, 431, 447)),
    '29_50': ('', None, None),
    '29_60': ('1 Vytápění<br>2 Vytápění + chlazení<br>3 Vytápění + TUV<br>4 Vytápění + chlazení + TUV', 'left', None),
    '29_64': ('0 Přerušovaně<br>1 Trvale<br>2 Stop po dosažení teploty', 'left', None),
    '29_72': ('0 Bez startu<br>1 Auto<br>2 Ručně', 'left', None),
    '43_4': ('Porucha: při poruše zobrazí informace o poruše', 'left', (64, 241, 150, 300)),
    '43_2': ('Více: lze změnit název zařízení, zvolit umístění, zkontrolovat stav sítě, přidat sdílené uživatele, '
             'vytvořit skupinu zařízení, zobrazit informace o zařízení atd.', 'left', None),
}
CAPTIONS = [  # (strana, box, html, velikost, zarovnání, tučně)
    (3, (57.5, 426, 155.6, 453.5), 'NEBEZPEČÍ', 13.5, 'center', True),
    (3, (160, 432, 520, 448), '– Riziko úrazu elektrickým proudem.', 10.5, 'left', True),
]
# úpravy rastrových obrázků (xref → funkce v PIL): graf ekvitermní křivky, snímky aplikace s názvem Wi-Fi výrobce
FONT = os.path.join('/System/Library/Fonts/Supplemental', 'Arial.ttf')


def img_chart(im, D, F):
    D.rectangle((8, 80, 66, 112), fill='white')                       # „图表区“
    D.rectangle((10, 120, 36, 290), fill='white')                     # Target Temperature
    D.rectangle((230, 432, 440, 460), fill='white')                   # Ambition Temperature
    f = F(15)
    t = 'Venkovní teplota (°C)'
    D.text((337 - D.textlength(t, font=f) / 2, 436), t, fill=(89, 89, 89), font=f)
    from PIL import Image, ImageDraw
    t = 'Požadovaná teplota (°C)'
    w = int(D.textlength(t, font=f)) + 4
    lab = Image.new('RGB', (w, 20), 'white')
    ImageDraw.Draw(lab).text((2, 1), t, fill=(89, 89, 89), font=f)
    lab = lab.rotate(90, expand=True)
    im.paste(lab, (12, int(205 - lab.height / 2)))


def img_ssid(im, D, F):
    D.rectangle((225, 590, 880, 670), fill='white')
    D.text((240, 600), 'MojeWiFi', fill=(28, 28, 30), font=F(46))


def img_pass(im, D, F):
    D.rectangle((225, 0, 880, 55), fill='white')
    D.text((240, -4), 'heslo-wifi', fill=(28, 28, 30), font=F(46))


IMG_EDITS = {480: img_chart, 531: img_ssid, 532: img_pass}
# svislé popisky v obr. 2 (str. 14 originálu, text otočený o 90°)
FIG2 = {
    'Hot water tank': 'Zásobník TUV', 'Magnesiumrod': 'Mg anoda', 'sensor': 'čidlo',
    'Hot water outlet': 'Výstup teplé vody', 'Cold water inlet': 'Vstup studené vody', 'Limber hole': 'Odvodnění',
    'Safety valve': 'Pojistný ventil', 'Floor pipe': 'Podlah. topení', 'Radiator': 'Radiátor', 'Fan coil': 'Fancoil',
    '3-way valve': 'Trojcestný ventil', 'Water pump': 'Oběh. čerpadlo', 'Water tank': 'Akum. nádrž',
}
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
    for pno, rect, html, size, align, bold in CAPTIONS:
        box_html(doc[pno], rect, html, size, align=align, bold=bold)
    SP = json.load(open(os.path.join(DIR, 'nahradni-dily.json')))
    for pno, t in SP.items():
        spare_table(doc[int(pno)], t['left'], t['right'])

# 2c) svislé popisky v obr. 2, kódy BOM, titulka
if not IDENTITY:
    p = doc[15]
    labels = [(fitz.Rect(l['bbox']), sp) for b in p.get_text('dict')['blocks'] for l in b.get('lines', [])
              if l['dir'] == (0.0, -1.0) for sp in l['spans'] if sp['text'].strip() in FIG2]
    for r, sp in labels:
        p.add_redact_annot(r, fill=False)
    p.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
    for r, sp in labels:
        cs = FIG2[sp['text'].strip()]
        size = sp['size']
        # nový text začíná na stejném místě (dole) a nesmí přesáhnout původní délku víc než o 40 %
        size = min(size, size * 1.4 * r.height / max(arial.text_length(cs, size), 1))
        o = fitz.Point(sp['origin'])
        p.insert_text(o, cs, fontsize=size, fontname='arial', fontfile=os.path.join(FONTDIR, 'Arial.ttf'), rotate=90)

    # „Figure 2“ je v originále obrázek → překrýt a vysázet česky (svisle)
    p.draw_rect(fitz.Rect(478, 328, 518, 435), color=None, fill=(1, 1, 1))
    t = 'Obrázek 2'
    p.insert_text((509, 381.5 + arial.text_length(t, 20) / 2), t, fontsize=20, fontname='arial',
                  fontfile=os.path.join(FONTDIR, 'Arial.ttf'), rotate=90)

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
        'title': 'REO HEATING RH030 / RH040 / RH050 / RH060 — Návod k instalaci a obsluze',
        'author': 'REO HEATING',
        'subject': 'Invertorové tepelné čerpadlo vzduch–voda R290, návod k instalaci a obsluze',
        'keywords': 'RH030, RH040, RH050, RH060, REO HEATING, R290, tepelné čerpadlo',
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
    brand = re.compile(r'power\s*world|PW\s*0\d\d|DKZLRS|CP-RW', re.I)
    left = [i + 1 for i, p in enumerate(out) if brand.search(p.get_text())]
    meta = [k for k, v in out.metadata.items() if v and brand.search(v)]
    miss = [s['id'] for s in segments if s['id'] not in tr]
    print(f'odkazy na výrobce: strany {left or "žádné"} | metadata {meta or "žádná"} | nepřeloženo: {miss or "nic"}')
