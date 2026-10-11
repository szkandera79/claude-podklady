#!/usr/bin/env python3
"""Vytáhne odstavce k překladu → segments.json + chunks/chunk_XX.json ({id: text})."""
import json
import os
import re

from common import *

prs = Presentation(SRC)
seg = {}
for sno, slide in enumerate(prs.slides, 1):
    if sno in REBUILT:
        continue
    for n, p, _ in iter_paragraphs(slide):
        t = to_tagged(p)
        if not re.search(r'[A-Za-z]{2,}', t):
            continue
        seg[f'{sno}_{n}'] = rename_models(t)
json.dump(seg, open(os.path.join(DIR, 'segments.json'), 'w'), ensure_ascii=False, indent=1)
os.makedirs(os.path.join(DIR, 'chunks'), exist_ok=True)
chunk, size, k = {}, 0, 0
for key, t in seg.items():
    chunk[key] = t
    size += len(t)
    if size > 9000:
        json.dump(chunk, open(os.path.join(DIR, 'chunks', f'chunk_{k:02d}.json'), 'w'), ensure_ascii=False, indent=1)
        chunk, size, k = {}, 0, k + 1
if chunk:
    json.dump(chunk, open(os.path.join(DIR, 'chunks', f'chunk_{k:02d}.json'), 'w'), ensure_ascii=False, indent=1)
    k += 1
print(len(seg), sum(map(len, seg.values())), k)
