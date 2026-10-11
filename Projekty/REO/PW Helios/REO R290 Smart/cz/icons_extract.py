#!/usr/bin/env python3
"""Ikony vložené v řádcích textu: pro každý dotčený segment zapíše anglický text se značkami {I1}, {I2}…
na místě ikon + geometrii ikon → icons.json. Značky se pak doplní do českého překladu (cs_icons.json)."""
import json
import fitz
S = json.load(open('segments.json'))
d = fitz.open('../REO-R290-Smart_navod-EN.pdf')
out = {}
used = set()   # ikona přes dva řádky patří jen prvnímu segmentu
for s in S:
    if s.get('toc'):
        continue
    page = d[s['page']]
    imgs = [(fitz.Rect(x['bbox']), x['xref']) for x in page.get_image_info(xrefs=True)]
    raw = page.get_text('rawdict')
    icons, text = [], []
    for lb in s['lines']:
        L = fitz.Rect(lb)
        lic = sorted([(r, x) for r, x in imgs if r.height < 45 and r.width < 80 and r.intersects(L + (-8, 0, 8, 0))
                      and (r & (L + (-8, 0, 8, 0))).height > 0.3 * L.height and (s['page'], tuple(r)) not in used], key=lambda t: t[0].x0)
        used.update((s['page'], tuple(r)) for r, _ in lic)
        chars = [c for b in raw['blocks'] if b['type'] == 0 for l in b['lines'] for sp in l['spans'] for c in sp['chars']
                 if fitz.Rect(c['bbox']).intersects(L) and abs((c['bbox'][1] + c['bbox'][3]) / 2 - (L.y0 + L.y1) / 2) < L.height / 2]
        chars.sort(key=lambda c: c['bbox'][0])
        t, k = '', 0
        for c in chars:
            while k < len(lic) and c['bbox'][0] >= lic[k][0].x1 - 2:
                if not text and not t.strip():
                    k += 1            # ikona před začátkem odstavce (výstražný trojúhelník) zůstává na místě
                    continue
                icons.append({'xref': lic[k][1], 'bbox': list(lic[k][0]), 'line': list(L)})
                t += '{I%d}' % len(icons)
                k += 1
            t += c['c']
        while k < len(lic):
            icons.append({'xref': lic[k][1], 'bbox': list(lic[k][0]), 'line': list(L)})
            t += '{I%d}' % len(icons)
            k += 1
        text.append(t.strip())
    if icons:
        out[s['id']] = {'en': ' '.join(text), 'icons': icons}
json.dump(out, open('icons.json', 'w'), ensure_ascii=False, indent=1)
print(len(out), sum(len(v['icons']) for v in out.values()))
for k, v in list(out.items())[:8]:
    print(k, v['en'][:200])
