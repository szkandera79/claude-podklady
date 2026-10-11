#!/usr/bin/env python3
"""Krok 1 české verze: z anglického originálu výrobce (2022) vytáhne odstavce / buňky tabulek k překladu.

PDF z Wordu/WPS má každý řádek jako samostatný blok → řádky se tu skládají do odstavců podle geometrie
(stejný sloupec, malá mezera, žádná čára tabulky mezi nimi). Pro každý odstavec se spočítá i
„prostor“, do kterého se smí český text rozlít (do nejbližší čáry / objektu vpravo a dole).

Výstup: segments.json + chunks/chunk_XX.json (id → HTML) pro překlad.
"""
import json
import os
import re

import fitz

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, '..', '..', 'Power World R290 Heat Pump User Manual.pdf')
WIRING = set()                              # schémata zapojení jsou v originále obrázky
TOC_PAGE = 2
NO_MERGE = {2}       # obsah
LIST_START = re.compile(r'^\s*(\d+\s*[.)、．]|\(\d+\)|（\d+）|\d+）|[a-zA-Z][.)]\s|[■•●◎※\-–—★*]|[A-L]\s{1,3}[A-Z]|\d+\.\d|Step\s*\d|Note|Tip|Remark)')
DOTS = re.compile(r'^(.*?)\s*\.{4,}\s*(-\s*\d+\s*-)\s*$')
MARGIN_R, MARGIN_B = 36, 42


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def is_bold(span):
    return 'Bold' in span['font'] or bool(span['flags'] & 16)


def segs(page):
    """Vodorovné a svislé úsečky (čáry tabulek) z vektorové grafiky."""
    hs, vs = [], []
    for d in page.get_drawings():
        for it in d['items']:
            if it[0] == 'l':
                p, q = it[1], it[2]
                if abs(p.y - q.y) < 1.0 and abs(p.x - q.x) > 4:
                    hs.append((p.y, min(p.x, q.x), max(p.x, q.x)))
                elif abs(p.x - q.x) < 1.0 and abs(p.y - q.y) > 4:
                    vs.append((p.x, min(p.y, q.y), max(p.y, q.y)))
            elif it[0] == 're':
                r = it[1]
                if r.height < 2 and r.width > 4:
                    hs.append(((r.y0 + r.y1) / 2, r.x0, r.x1))
                elif r.width < 2 and r.height > 4:
                    vs.append(((r.x0 + r.x1) / 2, r.y0, r.y1))
                elif r.width > 4 and r.height > 4:
                    hs += [(r.y0, r.x0, r.x1), (r.y1, r.x0, r.x1)]
                    vs += [(r.x0, r.y0, r.y1), (r.x1, r.y0, r.y1)]
    return hs, vs


def line_info(l):
    spans = [s for s in l['spans'] if s['text'].strip()]
    text = ''.join(s['text'] for s in l['spans']).strip()
    size = max(spans, key=lambda s: len(s['text']))['size']
    return {'bbox': fitz.Rect(l['bbox']), 'text': text, 'spans': l['spans'], 'size': size,
            'bold': all(is_bold(s) for s in spans)}


def hline_between(hs, a, b):
    """Leží mezi řádky a (nahoře) a b (dole) vodorovná čára, která je oba překrývá?"""
    x0, x1 = max(a['bbox'].x0, b['bbox'].x0), min(a['bbox'].x1, b['bbox'].x1)
    for y, sx0, sx1 in hs:
        if a['bbox'].y1 - 2 <= y <= b['bbox'].y0 + 2 and sx0 < x1 and sx1 > x0:
            return True
    return False


def span_html(spans):
    out = []
    for s in spans:
        t = esc(s['text'])
        out.append(f'<b>{t}</b>' if is_bold(s) and s['text'].strip() else t)
    return ''.join(out).strip()


doc = fitz.open(SRC)
segments = []
for pno, page in enumerate(doc):
    W, H = page.rect.width, page.rect.height
    hs, vs = segs(page)
    imgs = [fitz.Rect(i['bbox']) for i in page.get_image_info()]
    bullets = [d['rect'] for d in page.get_drawings() if d.get('fill') is not None
               and 1 < d['rect'].width < 10 and 1 < d['rect'].height < 10]

    def left_obst(L):
        """Odrážka / ikona těsně vlevo od začátku řádku (ve stejné výšce)."""
        b = L['bbox']
        for r in imgs + bullets:
            if b.x0 - 45 < r.x1 <= b.x0 + 1 and r.y0 < b.y1 - 2 and r.y1 > b.y0 + 2:
                return r
        return None
    lines = []
    for b in page.get_text('dict')['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            if l['dir'] != (1.0, 0.0) or not ''.join(s['text'] for s in l['spans']).strip():
                continue
            lines.append(line_info(l))
    lines.sort(key=lambda L: (round(L['bbox'].y0), L['bbox'].x0))
    # fragmenty jednoho řádku (WPS je občas rozdělí) → spojit, pokud mezi nimi není čára tabulky
    merged = []
    for L in sorted(lines, key=lambda L: (round(L['bbox'].y1 / 3), L['bbox'].x0)):
        M = merged[-1] if merged else None
        if (M and pno not in NO_MERGE and abs(M['bbox'].y1 - L['bbox'].y1) < 2 and 0 <= L['bbox'].x0 - M['bbox'].x1 < 3 * L['size']
                and abs(M['size'] - L['size']) < 1.2
                and not any(M['bbox'].x1 - 1 <= x <= L['bbox'].x0 + 1 and y0 <= L['bbox'].y1 and y1 >= L['bbox'].y0 for x, y0, y1 in vs)):
            M['spans'] = M['spans'] + [{'text': ' ', 'font': '', 'flags': 0, 'size': L['size'], 'color': 0}] + L['spans']
            M['text'] += ' ' + L['text']
            M['bbox'] |= L['bbox']
            M['bold'] = M['bold'] and L['bold']
        else:
            merged.append(L)
    lines = sorted(merged, key=lambda L: (round(L['bbox'].y0), L['bbox'].x0))

    # --- skládání řádků do odstavců ---
    paras = []
    for L in lines:
        target = None
        if pno not in NO_MERGE:
            for P in reversed(paras[-12:]):
                last = P['lines'][-1]
                a, b = last['bbox'], L['bbox']
                step = b.y0 - a.y0          # rozteč řádků (bboxy u CJK fontů bývají vysoké a překrývají se)
                ov = min(a.x1, b.x1) - max(a.x0, b.x0)
                if (0.6 * L['size'] < step < 1.95 * L['size'] and ov > 0.4 * min(a.width, b.width)
                        and abs(last['size'] - L['size']) < 1.2 and abs(a.x0 - b.x0) < max(a.width, b.width)
                        and not hline_between(hs, last, L)):
                    target = P
                    break
        if target:
            ob, pob = left_obst(L), left_obst(target['lines'][-1])
            if ob is not None and ob != pob:
                target = None                 # nová položka odrážky / text vedle ikony
            elif ob is None and pob is not None and pob.height > 1.5 * L['bbox'].height:
                target = None                 # konec textu vedle velké ikony
        if target:
            target['lines'].append(L)
        else:
            paras.append({'lines': [L]})

    rects = [fitz.Rect.__or__(fitz.Rect(P['lines'][0]['bbox']), fitz.Rect(P['lines'][-1]['bbox'])) for P in paras]
    for P, R in zip(paras, rects):
        for L in P['lines']:
            R |= L['bbox']
        P['rect'] = R

    for k, P in enumerate(paras):
        Ls, R = P['lines'], P['rect']
        plain = ' '.join(L['text'] for L in Ls)
        size = max(set(round(L['size'], 1) for L in Ls), key=lambda z: sum(len(L['text']) for L in Ls if round(L['size'], 1) == z))
        if not re.search(r'[A-Za-z]{3,}', plain) or size < 5.5 or (pno in WIRING and size < 9.5):
            continue
        sid = f'{pno}_{k}'
        if pno == TOC_PAGE:
            m = DOTS.match(plain)
            if m:
                segments.append({'id': sid, 'page': pno, 'rect': list(R), 'size': size, 'toc': True,
                                 'lines': [list(L['bbox']) for L in Ls],
                                 'bold': Ls[0]['bold'], 'origin': list(Ls[0]['spans'][0]['origin']),
                                 'pnum': m.group(2), 'html': esc(m.group(1))})
                continue

        # hranice buňky / volného prostoru
        ymid = (R.y0 + R.y1) / 2
        left_v = [x for x, y0, y1 in vs if y0 <= ymid <= y1 and x <= R.x0 + 1]
        right_v = [x for x, y0, y1 in vs if y0 <= ymid <= y1 and x >= R.x1 - 1]
        in_cell = bool(left_v and right_v) and (min(right_v) - max(left_v)) < W * 0.8
        obst_r = [Q['rect'].x0 for Q in paras if Q is not P and Q['rect'].x0 >= R.x1 - 1
                  and Q['rect'].y0 < R.y1 - 1 and Q['rect'].y1 > R.y0 + 1]
        obst_r += [im.x0 for im in imgs if im.x0 >= R.x1 - 1 and im.y0 < R.y1 and im.y1 > R.y0]
        right = min(right_v + [x - 4 for x in obst_r] + [W - MARGIN_R])
        right = max(right, R.x1)
        below = [Q['rect'].y0 for Q in paras if Q is not P and Q['rect'].y0 > R.y0 + 3
                 and Q['rect'].x0 < right and Q['rect'].x1 > R.x0]
        below += [im.y0 for im in imgs if im.y0 > R.y0 + 3 and im.x0 < right and im.x1 > R.x0]
        below += [y for y, x0, x1 in hs if y >= R.y1 - 2 and x0 < right and x1 > R.x0]
        bottom = max(min(below + [H - MARGIN_B]) - 0.5, R.y1)

        align = 'left'
        box = fitz.Rect(R.x0, R.y0, right, bottom)
        if in_cell:
            cl, cr = max(left_v), min(right_v)
            centers = [(L['bbox'].x0 + L['bbox'].x1) / 2 for L in Ls]
            if all(abs(c - (cl + cr) / 2) < 3 for c in centers) and R.x0 - cl > 3:
                align = 'center'
                box = fitz.Rect(cl + 1.5, R.y0, cr - 1.5, bottom)
            else:
                box = fitz.Rect(R.x0, R.y0, cr - 1.5, bottom)
        elif len(Ls) > 1 and R.width > 200:
            align = 'justify'

        # HTML se zachováním tučného písma a tvrdých zlomů (odrážky, krátké řádky)
        html = span_html(Ls[0]['spans'])
        for i in range(1, len(Ls)):
            prev, cur = Ls[i - 1], Ls[i]
            short = prev['bbox'].x1 < R.x1 - max(0.12 * R.width, 12)
            hard = LIST_START.match(cur['text']) or (short and prev['text'][-1:] in '.:;。：!?)）') \
                or (short and not in_cell and len(Ls) > 2)
            html += ('<br>' if hard else ' ') + span_html(cur['spans'])
        html = re.sub(r'</b>(\s*)<b>', r'\1', html)
        pitch = (Ls[-1]['bbox'].y0 - Ls[0]['bbox'].y0) / (len(Ls) - 1) if len(Ls) > 1 else size * 1.15
        col = max((s for L in Ls for s in L['spans']), key=lambda s: len(s['text']))['color']
        segments.append({'id': sid, 'page': pno, 'rect': list(R), 'box': list(box), 'size': size,
                         'lines': [list(L['bbox']) for L in Ls],
                         'lh': round(pitch / size, 3), 'align': align, 'color': col, 'html': html})

json.dump(segments, open(os.path.join(DIR, 'segments.json'), 'w'), ensure_ascii=False, indent=0)

import sys
if '--no-chunks' in sys.argv:
    sys.exit(0)
os.makedirs(os.path.join(DIR, 'chunks'), exist_ok=True)
for f in os.listdir(os.path.join(DIR, 'chunks')):
    os.remove(os.path.join(DIR, 'chunks', f))
chunk, n, k = {}, 0, 0
for s in segments:
    chunk[s['id']] = s['html']
    n += len(s['html'])
    if n > 13000:
        json.dump(chunk, open(os.path.join(DIR, 'chunks', f'chunk_{k:02d}.json'), 'w'), ensure_ascii=False, indent=1)
        chunk, n, k = {}, 0, k + 1
if chunk:
    json.dump(chunk, open(os.path.join(DIR, 'chunks', f'chunk_{k:02d}.json'), 'w'), ensure_ascii=False, indent=1)
    k += 1
print(f'segmentů: {len(segments)} | znaků: {sum(len(s["html"]) for s in segments)} | dávek: {k}')
