#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vloží schéma kaskády do nabidka.html jako inline SVG (idempotentně).

Inline místo <img>: Safari při tisku SVG z <img> nevykreslí (viz bd-jandova/README.md).
Spouštět po každém `python3 src/gen_schema.py`.
"""
import os
import re

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
HTML = os.path.join(ROOT, "nabidka.html")
ALT = ("Koncepční schéma modulární kaskády jednoho až čtyř tepelných čerpadel REO X50 "
       "s akumulací a zásobníky TUV")


def main():
    with open(os.path.join(ROOT, "schema-kaskada.svg"), encoding="utf-8") as f:
        svg = f.read()
    svg = svg.replace('<svg xmlns', f'<svg role="img" aria-label="{ALT}" xmlns', 1)
    with open(HTML, encoding="utf-8") as f:
        html = f.read()
    blok = f"<!--SCHEMA:1-->\n{svg}\n<!--/SCHEMA:1-->"
    html, n = re.subn(r"<!--SCHEMA:1-->.*?<!--/SCHEMA:1-->", lambda _: blok, html, count=1, flags=re.S)
    if not n:
        raise SystemExit("CHYBA: v nabidka.html chybí značky <!--SCHEMA:1-->")
    with open(HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print("zapsáno:", HTML)


if __name__ == "__main__":
    main()
