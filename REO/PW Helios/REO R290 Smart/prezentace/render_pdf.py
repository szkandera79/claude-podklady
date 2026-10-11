#!/usr/bin/env python3
"""PPTX → PDF bez PowerPointu/LibreOffice: náhled macOS Quick Look (HTML) → Google Chrome (tisk do PDF).

    python3 render_pdf.py vstup.pptx výstup.pdf

Quick Look ukládá vektorové tvary jako PDF přílohy, které Chrome v <img> nezobrazí → převedou se na PNG.
Fidelita odpovídá náhledu v macOS (Finder / mezerník); písma, tabulky i obrázky sedí, drobné odchylky
od PowerPointu jsou možné u efektů (stíny, přechody).
"""
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

import fitz

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
CSS = ('<style>@page{size:960px 540px;margin:0} @media print{body{margin:0;background:#fff}'
       ' div.slide{margin:0 !important;-webkit-box-shadow:none !important;break-after:page}}</style>')


def render(src, out):
    work = tempfile.mkdtemp(prefix='ql_')
    # Quick Look si drží mezipaměť podle cesty souboru → vykreslovat vždy z kopie s jedinečným jménem
    fresh = os.path.join(work, f'deck_{os.getpid()}_{int(time.time() * 1000)}.pptx')
    shutil.copyfile(src, fresh)
    subprocess.run(['qlmanage', '-r', 'cache'], capture_output=True)
    subprocess.run(['qlmanage', '-p', '-o', work, fresh], capture_output=True, check=True)
    d = glob.glob(os.path.join(work, '*.qlpreview'))[0]
    for f in glob.glob(os.path.join(d, 'Attachment*.pdf')):
        try:
            page = fitz.open(f)[0]
            z = max(1, min(4, 1200 / max(page.rect.width, 1)))
            page.get_pixmap(matrix=fitz.Matrix(z, z), alpha=True).save(f[:-4] + '.pdfimg.png')
        except Exception:
            pass
    html = open(os.path.join(d, 'Preview.html'), encoding='utf8').read()
    html = re.sub(r'(Attachment\d+)\.pdf', r'\1.pdfimg.png', html.replace('</head>', CSS + '</head>', 1))
    open(os.path.join(d, 'print.html'), 'w', encoding='utf8').write(html)
    raw = out + '.raw.pdf'
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
                    '--virtual-time-budget=30000', f'--print-to-pdf={raw}', 'file://' + os.path.join(d, 'print.html')],
                   capture_output=True, check=True)
    return raw


if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]
    raw = render(src, out)
    doc = fitz.open(raw)
    doc.set_metadata({'title': 'REO HEATING R290 – tepelná čerpadla RH06–RH16', 'author': 'REO HEATING',
                      'subject': 'Konstrukce a hlavní funkce tepelných čerpadel vzduch–voda R290',
                      'keywords': 'REO HEATING, RH06, RH08, RH10, RH12, RH14, RH16, R290',
                      'creator': 'REO HEATING', 'producer': 'REO HEATING'})
    doc.save(out, garbage=4, deflate=True)
    os.remove(raw)
    print(out, fitz.open(out).page_count, 'stran')
