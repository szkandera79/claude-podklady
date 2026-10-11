#!/usr/bin/env python3
"""Rebranding energetického štítku: POWER WORLD / PW150-DKZLRS-E → REO HEATING / RH X50.

Spouštět ze složky `RH X50 komerční`:
    python3 "RH X50 - REO HEATING/rebrand-stitek.py"

Štítek je regulovaný formát (nařízení EU 811/2013) — rozvržení, třídy, čísla ani
piktogramy se nesmí měnit. Skript proto nepřekresluje nic z grafiky: přepisuje
přímo textové operátory v content streamu, takže zbytek stránky zůstane bit-to-bit
stejný. (Cesta přes fitz redakce zde nefunguje — poškodí sousední čísla výkonů,
protože jsou sázená kombinací několika subsetových fontů.)

Označení modelu bylo v originále složené ze tří fontů (F2 CID + F3 + F2); nahrazuje
se jediným řetězcem ve fontu F1 (Calibri), zarovnaným na původní pravou hranu.
"""
import os
import sys

import fitz

SRC = 'PW150-DKZLRS-E Energy label.pdf'
DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(DIR, 'RH-X50-energeticky-stitek.pdf')

XREF_CONTENT = 7       # content stream stránky
XREF_CALIBRI = 10      # zabudovaný Calibri = font F1
RIGHT_EDGE = 260.8     # pravá hrana původního označení modelu
ORIGIN_X = 26.76       # posun textového bloku (cm operátor)

OLD_MODEL = """/F2 11 Tf 156.478 .101 Td
<0057007403ED> Tj
/F3 11 Tf 21.054 0 Td
(5)Tj
/F2 11 Tf 5.577 0 Td
<03EC03720018003C007F003E005A005E0372001C> Tj
"""

if not os.path.exists(SRC):
    sys.exit(f'Nenalezen zdroj: {SRC} — spusť skript ze složky „RH X50 komerční“.')

doc = fitz.open(SRC)
stream = doc.xref_stream(XREF_CONTENT).decode('latin-1')

tmp_font = os.path.join(DIR, '_calibri.ttf')
open(tmp_font, 'wb').write(doc.extract_font(XREF_CALIBRI)[3])
width = fitz.Font(fontfile=tmp_font).text_length('RH X50', 11)
os.remove(tmp_font)

assert stream.count(OLD_MODEL) == 1 and stream.count('(POWER WORLD)Tj') == 1, 'jiná verze zdrojového PDF'
stream = stream.replace(OLD_MODEL, '/F1 11 Tf %.3f .101 Td\n(RH X50)Tj\n' % (RIGHT_EDGE - ORIGIN_X - width))
stream = stream.replace('(POWER WORLD)Tj', '(REO HEATING)Tj')

doc.update_stream(XREF_CONTENT, stream.encode('latin-1'))
doc.set_metadata({
    'title': 'RH X50 — energetický štítek',
    'author': 'REO HEATING',
    'subject': 'Energetický štítek podle nařízení (EU) 811/2013',
    'keywords': 'RH X50, REO HEATING, energetický štítek',
    'creator': 'REO HEATING',
    'producer': 'REO HEATING',
})
doc.save(OUT, garbage=3, deflate=True)

text = fitz.open(OUT)[0].get_text()
assert 'POWER' not in text.upper() and 'PW150' not in text, 'zůstala značka výrobce'
for value in ('26', '27', '28', '29', '66', 'A++', 'A+++', '811/2013'):
    assert value in text, f'chybí hodnota {value} — grafika byla poškozena'
print(f'uloženo: {OUT}')
