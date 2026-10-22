"""Odstranění názvu Wi‑Fi sítě výrobce („pwwm“) ze snímků aplikace v návodu RH X50 / RH X100.

Snímky obrazovky v kap. 6 (str. 49 a 50) ukazují připojení k Wi‑Fi síti pojmenované po výrobci.
Text se v rastru přemaluje barvou pozadí a nahradí neutrálním „MyWiFi“ (Helvetica, stejná velikost).
Souřadnice jsou v pixelech obrázku: (x0, y0, x1, y1) oblasti textu a účaří.
"""
import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT = '/System/Library/Fonts/Helvetica.ttc'
NEW = 'MyWiFi'

# digest prvních 10 hex znaků obrázku → (oblast textu, účaří, velikost písma v px)
EN = {'942fc3adb8': ((58, 160, 113, 181), 175, 15),   # str. 49 „Enter Wi‑Fi Information“
      'ac5c8f7064': ((53, 339, 107, 359), 353, 15)}   # str. 50 „Select 2.4 GHz Wi‑Fi Network“
CZ = {'c167b65282': ((60, 159, 114, 180), 174, 15),   # str. 49 (sloučený snímek)
      'e94c63ec1c': ((38, 306, 90, 326), 320, 13)}    # str. 50 (zmenšený snímek)


def _fix(pix, box, base, size):
    if pix.alpha or pix.n - pix.alpha != 3:
        pix = fitz.Pixmap(fitz.csRGB, pix)
        if pix.alpha:
            pix = fitz.Pixmap(pix, 0)
    img = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    a = np.asarray(img).astype(int)
    x0, y0, x1, y1 = box
    region = a[y0:y1, x0:x1]
    bg = tuple(int(v) for v in np.median(region.reshape(-1, 3), axis=0))
    fg = tuple(int(v) for v in region.reshape(-1, 3)[region.reshape(-1, 3).sum(1).argmin()])
    d = ImageDraw.Draw(img)
    d.rectangle(box, fill=bg)
    d.text((x0 + 2, base), NEW, font=ImageFont.truetype(FONT, size), fill=fg, anchor='ls')
    return img


def fix_document(doc, table, tmpdir):
    """Najde obrázky podle digestu a nahradí je opravenou verzí. Vrací počet nahrazených."""
    import os
    done = set()
    for page in doc:
        for info in page.get_image_info(xrefs=True, hashes=True):
            key = info['digest'].hex()[:10]
            if key in table and info['xref'] not in done:
                box, base, size = table[key]
                img = _fix(fitz.Pixmap(doc, info['xref']), box, base, size)
                path = os.path.join(tmpdir, f'ssid_{info["xref"]}.png')
                img.save(path)
                page.replace_image(info['xref'], filename=path)
                done.add(info['xref'])
    return len(done)
