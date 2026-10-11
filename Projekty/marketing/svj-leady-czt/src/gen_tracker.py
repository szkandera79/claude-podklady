#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vygeneruje `tracker.html` — sledovač leadů SVJ pro publikování jako artefakt.

Kontakty se berou z `kontakty-davka-*.csv` (zdroj pravdy zůstává v repu).
Stav oslovování si stránka ukládá sama do sdílené databáze artefaktu,
takže je vidět ze všech zařízení; CSV se kvůli stavu needitují.

Spuštění ze složky src/:  python3 gen_tracker.py
Publikování:              artefakt z ../tracker.html (capabilities: db, downloads)
"""
import csv, json, pathlib

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent

def num(s):
    return float(s.replace("\xa0", "").replace(" ", "").replace(",", ".")) if s else None

leads = []
for f in sorted(ROOT.glob("kontakty-davka-*.csv")):
    with open(f, encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh, delimiter=";"):
            leads.append({
                "id": r["ico"],
                "poradi": int(r["poradi_dle_ceny_tepla"]),
                "cena": num(r["cena_tepla"]),
                "nazev": r["nazev_organizace"],
                "ico": r["ico"],
                "adresa": r["adresa_domu"],
                "sidlo": r["sidlo_organizace"],
                "web": r["web"],
                "email": r["email"],
                "tel": r["telefon"],
                "typ": r["typ_kontaktu"],
                "overeni": r["stav_overeni"],
                "poznamka": r["poznamka"],
                "davka": f.stem.split("-")[-1],
            })
leads.sort(key=lambda l: l["poradi"])

tpl = (HERE / "tracker.template.html").read_text()
out = tpl.replace("/*LEADS*/", "const LEADS = " + json.dumps(leads, ensure_ascii=False) + ";")
(ROOT / "tracker.html").write_text(out)
print(f"tracker.html — {len(leads)} leadů, {sum(1 for l in leads if l['email'] or l['tel'] or l['web'])} s kontaktem")
