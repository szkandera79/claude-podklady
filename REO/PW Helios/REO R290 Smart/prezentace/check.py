#!/usr/bin/env python3
"""Strukturální kontrola balíčku PPTX (náhrada validate.py, který potřebuje Python ≥ 3.10)."""
import posixpath
import re
import sys
import zipfile
from collections import Counter

from lxml import etree

f = sys.argv[1]
z = zipfile.ZipFile(f)
names = set(z.namelist())
problems = []
ct = z.read('[Content_Types].xml').decode()
defaults = set(re.findall(r'Extension="([^"]+)"', ct))
overrides = set(re.findall(r'PartName="([^"]+)"', ct))
for n in names:
    if n.endswith('/') or n == '[Content_Types].xml':
        continue
    ext = n.rsplit('.', 1)[-1].lower()
    if '/' + n not in overrides and ext not in {d.lower() for d in defaults}:
        problems.append(f'chybí content-type: {n}')
for o in overrides:
    if o[1:] not in names:
        problems.append(f'content-type na neexistující část: {o}')
for n in names:
    if not n.endswith('.rels'):
        continue
    base = posixpath.dirname(posixpath.dirname(n))
    src = posixpath.join(base, posixpath.basename(n)[:-5])
    rels = etree.fromstring(z.read(n))
    ids = set()
    for r in rels:
        ids.add(r.get('Id'))
        if r.get('TargetMode') == 'External':
            continue
        t = posixpath.normpath(posixpath.join(base, r.get('Target')))
        if t not in names:
            problems.append(f'{n}: cíl {r.get("Target")} neexistuje')
    if src in names and src.endswith('.xml'):
        x = z.read(src).decode('utf8')
        for rid in set(re.findall(r'r:(?:id|embed|link|pict)="(rId\d+)"', x)):
            if rid not in ids:
                problems.append(f'{src}: odkaz {rid} nemá relaci')
for n in sorted(names):
    if re.match(r'ppt/slides/slide\d+\.xml$', n):
        x = z.read(n).decode('utf8')
        etree.fromstring(x.encode())
        dup = [k for k, v in Counter(re.findall(r'<p:cNvPr id="(\d+)"', x)).items() if v > 1]
        if dup:
            problems.append(f'{n}: duplicitní ID tvarů {dup}')
print('\n'.join(problems) if problems else 'OK – žádné strukturální problémy')
