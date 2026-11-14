#!/usr/bin/env python3
"""Sestaví index.html = Instalační standard v1.0 (metodika.template.html + CSS/skript z navod.template.html + logo).
Spuštění z kořene repozitáře: python3 reo-smart-regulace/src/build_metodika.py
Návod rev. 0 se dá znovu sestavit build.py do navod-rev0.html."""
import os, re
H = os.path.dirname(os.path.abspath(__file__))
nav = open(os.path.join(H, "navod.template.html"), encoding="utf-8").read()
css = nav[nav.index("<style>"):nav.index("</style>") + 8]
js = nav[nav.index("<script>"):]
logo = re.sub(r"<\?xml[^>]*\?>", "", open(os.path.expanduser("~/Claude/REO/logo/logo-reo-heating.svg"), encoding="utf-8").read()).strip()
t = open(os.path.join(H, "metodika.template.html"), encoding="utf-8").read()
t = t.replace("{{CSS}}", css).replace("{{LOGO}}", logo).replace("{{SCRIPT}}", js)
out = os.path.join(os.path.dirname(H), "index.html")
open(out, "w", encoding="utf-8").write(t)
print("zapsáno", out, len(t), "B")
