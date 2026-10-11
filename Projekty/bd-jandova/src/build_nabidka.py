#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vloží schémata variant přímo do nabidka.html jako inline SVG.

Důvod: Safari (a tisk přes macOS Quartz) nevykreslí SVG vložené přes <img src>,
schéma pak v PDF úplně chybí. Inline <svg> se vytiskne spolehlivě a nabídka je
navíc soběstačná — dá se poslat jako jediný soubor.

Skript je idempotentní: při opakovaném spuštění obsah mezi značkami přepíše.
Spouštět po každém `python3 src/gen_schema.py`.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
HTML = os.path.join(ROOT, "nabidka.html")

ALT = {
    1: "Koncepční schéma varianty 1 — jedno tepelné čerpadlo REO X50 s elektrickou "
       "bivalencí, akumulace 2 × 1 000 l a zásobníky TUV 3 × 1 000 l",
    2: "Koncepční schéma varianty 2 — kaskáda dvou tepelných čerpadel REO X50, "
       "akumulace 2 × 1 000 l a zásobníky TUV 3 × 1 000 l",
}


def nacti_svg(n):
    """Vrátí SVG varianty n s ID prefixovanými, ať se dva výkresy v jednom
    dokumentu nepřebíjejí (duplicitní id by <use href> svedlo na první výskyt)."""
    with open(os.path.join(ROOT, f"schema-varianta-{n}.svg"), encoding="utf-8") as f:
        svg = f.read()
    svg = re.sub(r'id="([^"]+)"', rf'id="s{n}-\1"', svg)
    svg = re.sub(r'href="#([^"]+)"', rf'href="#s{n}-\1"', svg)
    # rozměry řídí CSS, atributy nechceme jako pevnou šířku
    svg = svg.replace('<svg xmlns', f'<svg role="img" aria-label="{ALT[n]}" xmlns', 1)
    return svg


def main():
    with open(HTML, encoding="utf-8") as f:
        html = f.read()

    for n in (1, 2):
        blok = f"<!--SCHEMA:{n}-->\n{nacti_svg(n)}\n<!--/SCHEMA:{n}-->"
        znacky = re.compile(rf"<!--SCHEMA:{n}-->.*?<!--/SCHEMA:{n}-->", re.S)
        if znacky.search(html):
            html = znacky.sub(lambda _: blok, html, count=1)
            print(f"varianta {n}: aktualizováno")
        else:
            img = re.compile(rf'<img src="schema-varianta-{n}\.svg".*?>', re.S)
            if not img.search(html):
                raise SystemExit(f"CHYBA: v nabidka.html nenalezen <img> ani značky pro variantu {n}")
            html = img.sub(lambda _: blok, html, count=1)
            print(f"varianta {n}: vloženo místo <img>")

    with open(HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print("zapsáno:", HTML)


if __name__ == "__main__":
    main()
