#!/usr/bin/env python3
"""Sestaví index.html (artefakt) z navod.template.html + logo REO HEATING.
Spuštění z kořene repozitáře: python3 reo-smart-regulace/src/build.py
(předtím gen_schemata.py; PNG schémat volitelně src/render.sh)"""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
logo = open(os.path.expanduser("~/Claude/REO/logo/logo-reo-heating.svg"), encoding="utf-8").read()
logo = re.sub(r"<\?xml[^>]*\?>", "", logo).strip()
t = open(os.path.join(HERE, "navod.template.html"), encoding="utf-8").read().replace("{{LOGO}}", logo)
out = os.path.join(os.path.dirname(HERE), "navod-rev0.html")  # rev. 0 – reference
open(out, "w", encoding="utf-8").write(t)
print("zapsáno", out, len(t), "B")
