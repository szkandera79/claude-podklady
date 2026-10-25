#!/usr/bin/env python3
"""Spare Part List.xlsx (REO/PW R290) → ../data/nahradni-dily-rh030-rh060.json
Spuštění: python3 reo-nahradni-dily/src/export_json.py"""
import json, os, openpyxl
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "REO", "PW R290", "Spare Part List.xlsx")
MODELS = {  # list → (id, název, fáze, výkon dle kódu)
    "030": ("RH030", "RH030", "1F", 8), "040": ("RH040", "RH040", "1F", 12),
    # list „050 S“ (RH050 1F) vyřazen — RH050 se nabízí jen ve 3F
    "050 3 phase": ("RH050", "RH050", "3F", 15),
    "060": ("RH060", "RH060", "3F", 22)}
wb = openpyxl.load_workbook(SRC, data_only=True)
out = []
for sheet, (mid, name, ph, kw) in MODELS.items():
    ws = wb[sheet]; rows = list(ws.iter_rows(values_only=True))
    bom, variant = rows[1][0], rows[1][1]
    parts = [dict(code=r[0], name=r[1], spec=(r[2] or "").strip(), qty=r[4], usd=r[5])
             for r in rows[2:] if r[0]]
    out.append(dict(id=mid, model=name, phase=ph, kw=kw, bom=bom, variant=variant, parts=parts))
dst = os.path.normpath(os.path.join(HERE, "..", "data", "nahradni-dily-rh030-rh060.json"))
os.makedirs(os.path.dirname(dst), exist_ok=True)
json.dump(dict(source="REO/PW R290/Spare Part List.xlsx", currency="USD", models=out),
          open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("zapsáno:", dst, sum(len(m["parts"]) for m in out), "položek")
