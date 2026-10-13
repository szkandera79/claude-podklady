#!/usr/bin/env python3
"""Výkonové mapy výrobce (../../R290 Helios Performance Curve/*.xls) → vykonove-mapy.json (REO označení).

Struktura: heating[water_temp][mode]{cap,pin,cop}[15 venkovních teplot], mode = max | min | std (std jen u RHX).
Chlazení a TUV stejně (cooling[water_temp][mode], dhw{amb,cap,pin,cop}).
"""
import glob
import json
import os
import re

import xlrd

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, '..', '..', 'R290 Helios Performance Curve')
NAME = {'06': 'RH06', '08': 'RH08', '10': 'RH10', '12': 'RH12', '14': 'RH14', '16': 'RH16',
        '20': 'RHX20 Pro', '30': 'RHX30 Pro'}


def num(v):
    try:
        return round(float(v), 4)
    except (TypeError, ValueError):
        return None                     # prázdné / „/“ = mimo pracovní rozsah


def parse_sheet(sh, amb_row=None):
    """Bloky „Water temp. outlet XX℃“ s řádky MAX/MIN/Standard × (výkon, příkon, COP)."""
    amb = None
    for r in range(sh.nrows):
        if 'Ambient' in str(sh.cell_value(r, 0)):
            amb = [num(sh.cell_value(r, c)) for c in range(3, sh.ncols)]
            amb = [a for a in amb if a is not None]
            break
    out, wt, mode = {}, None, None
    for r in range(sh.nrows):
        c0 = str(sh.cell_value(r, 0))
        m = re.search(r'outlet\s*(\d+)', c0)
        if m:
            wt = m.group(1)
            out[wt] = {}
        c1 = str(sh.cell_value(r, 1)).strip().lower()
        if c1:
            mode = {'max': 'max', 'min': 'min', 'standard': 'std'}.get(c1, c1)
        c2 = str(sh.cell_value(r, 2)).lower()
        key = 'cap' if 'capacity' in c2 else 'pin' if 'input' in c2 else 'cop' if ('cop' in c2 or 'eer' in c2) else None
        if wt and mode and key:
            vals = [num(sh.cell_value(r, c)) for c in range(3, 3 + len(amb))]
            out[wt].setdefault(mode, {})[key] = vals
    return amb, out


data = {}
for f in sorted(glob.glob(os.path.join(SRC, '*.xls'))):
    m = re.search(r'PW(\d\d)-DKXLRE(\d)', os.path.basename(f))
    size, ph = m.group(1), m.group(2)
    b = xlrd.open_workbook(f)
    title = str(b.sheets()[0].cell_value(0, 0))
    phases = sorted(set(re.findall(r'DKXLRE(\d)', title)) | {ph})
    sheets = {s.name.strip().lower(): s for s in b.sheets()}
    amb, heat = parse_sheet(sheets['heating'])
    camb, cool = parse_sheet(sheets['cooling'])
    d = sheets['dhw']
    dhw = {}
    if str(d.cell_value(1, 0)).strip().upper() in ('MAX', 'MIN', 'STANDARD'):   # RHX: MAX/MIN/Standard bloky
        mode = None
        for r in range(d.nrows):
            c0 = str(d.cell_value(r, 0)).strip().lower()
            vals = [v for v in (num(d.cell_value(r, c)) for c in range(2, d.ncols)) if v is not None]
            if c0 in ('max', 'min', 'standard'):
                mode = {'standard': 'std'}.get(c0, c0)
            if 'ambient' in c0:
                dhw['amb'] = vals
                continue
            c1 = str(d.cell_value(r, 1)).lower()
            k = 'cap' if 'capacity' in c1 else 'pin' if 'input' in c1 else 'cop' if 'cop' in c1 else None
            if k and mode:
                dhw.setdefault(mode, {})[k] = vals
        if 'max' in dhw:
            dhw.update(dhw['max'])                 # cap/pin/cop = MAX jako u RH
    for r in range(d.nrows if not dhw else 0):
        c0 = str(d.cell_value(r, 0)).lower()
        vals = [num(d.cell_value(r, c)) for c in range(1, d.ncols)]
        vals = [v for v in vals if v is not None]
        if 'ambient' in c0: dhw['amb'] = vals
        elif 'capacity' in c0: dhw['cap'] = vals
        elif 'input' in c0: dhw['pin'] = vals
        elif 'cop' in c0: dhw['cop'] = vals
    key = NAME[size] if size in ('20', '30') else f'{NAME[size]} {ph}F'
    data[key] = {'model': NAME[size], 'phases_in_source': [p + 'F' for p in phases], 'source': os.path.basename(f),
                 'heating': {'amb': amb, **heat}, 'cooling': {'amb': camb, **cool}, 'dhw': dhw}
json.dump(data, open(os.path.join(DIR, 'vykonove-mapy.json'), 'w'), ensure_ascii=False, indent=1)
for k, v in data.items():
    h = v['heating']
    print(k, v['phases_in_source'], 'W:', [w for w in h if w != 'amb'], 'módy:', list(h['35'].keys()),
          'amb', h['amb'][0], '…', h['amb'][-1], '| chlazení W:', [w for w in v['cooling'] if w != 'amb'], '| TUV body', len(v['dhw'].get('cop', [])))
