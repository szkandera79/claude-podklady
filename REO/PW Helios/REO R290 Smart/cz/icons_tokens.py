#!/usr/bin/env python3
"""Doplní značky {I1}, {I2}… do českého překladu odstavců s ikonami → cs_icons.json (klíče = id v segments.json).

Zdroj: cs_icons_byhtml.json (anglické HTML → čeština se značkami; ruční doladění z 1. kola, viz cs_icons_v1.json),
pro nové segmenty se značka vloží před první zavírací uvozovku."""
import json
import re

new = json.load(open('segments.json'))
I = json.load(open('icons.json'))
tr = json.load(open('cs_v2_reused.json'))
tr.update(json.load(open('cs/chunk_09.json')))
bh = json.load(open('cs_icons_byhtml.json'))
H = {s['id']: s['html'] for s in new}
MANUAL = {'60_4': ('„<br>při', '„{I1}“. Poté při')}   # ikona na konci řádku, pokračování v 60_5 (vypuštěno v build.py)
out = {}
for k, v in I.items():
    cs = bh.get(H[k])
    if k in MANUAL:
        cs = tr[k].replace(*MANUAL[k])
    elif not cs:
        t = tr[k].rstrip()
        cs = t + '{I1}' if t.endswith('„') else t.replace('„ a ', '„{I1}“ a ', 1) if '„ a ' in t \
            else t.replace('“', '{I1}“', 1)
    n = len(v['icons'])
    if cs.count('{I') == n - 1 and cs.rstrip().endswith('„'):
        cs = cs.rstrip() + '{I%d}' % n          # ikona na konci řádku (nově zachycená tolerancí)
    assert sorted(re.findall(r'\{I\d+\}', cs)) == sorted('{I%d}' % (i + 1) for i in range(len(v['icons']))), k
    out[k] = cs
json.dump(out, open('cs_icons.json', 'w'), ensure_ascii=False, indent=1)
print('ok', len(out))
