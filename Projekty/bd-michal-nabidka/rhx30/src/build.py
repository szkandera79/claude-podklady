#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Složí dva samostatné HTML dokumenty (nabídka rev. 1, podklad pro jednání společníků).

    python3 bd-michal-nabidka/rhx30/src/gen_schema.py && python3 bd-michal-nabidka/rhx30/src/build.py
Styl je společný (src/style.css). Schéma se do nabídky vkládá jako inline SVG
(Safari při tisku <img src=*.svg> nevykreslí — viz bd-jandova/README.md); vzor bd-jandova/rhx30/src/build.py.
"""
import os
import re

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(SRC, ".."))
DOCS = {"nabidka.body.html": "nabidka.html",
        "spolecnici.body.html": "podklad-spolecnici.html"}
ALT = "Koncepční schéma kotelny BD u Dolu Michal — kaskáda čtyř tepelných čerpadel RHX30 Pro s akumulací a zásobníky TUV"


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def main():
    css = read(os.path.join(SRC, "style.css"))
    svg = read(os.path.join(ROOT, "schema-rhx30.svg"))
    svg = svg.replace('<svg xmlns', f'<svg role="img" aria-label="{ALT}" xmlns', 1)
    for src, dst in DOCS.items():
        body = read(os.path.join(SRC, src))
        title = re.match(r"<!--TITLE:(.*?)-->", body).group(1)
        body = body.split("\n", 1)[1]
        body = re.sub(r"<!--SCHEMA:1-->.*?<!--/SCHEMA:1-->",
                      lambda _: f"<!--SCHEMA:1-->\n{svg}\n<!--/SCHEMA:1-->", body, flags=re.S)
        html = (f'<!DOCTYPE html>\n<html lang="cs">\n<head>\n<meta charset="UTF-8">\n'
                f'<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
                f"<title>{title}</title>\n<style>{css}</style>\n</head>\n<body>\n<div class=\"wrap\">\n"
                f"{body}\n</div><!-- /wrap -->\n</body>\n</html>\n")
        with open(os.path.join(ROOT, dst), "w", encoding="utf-8") as f:
            f.write(html)
        print("zapsáno:", dst)


if __name__ == "__main__":
    main()
