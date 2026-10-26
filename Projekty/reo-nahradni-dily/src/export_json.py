#!/usr/bin/env python3
"""Spare Part List - revised.pdf (REO/PW R290) → ../data/nahradni-dily-rh030-rh060.json
Spuštění: python3 reo-nahradni-dily/src/export_json.py
Každá strana PDF = jeden model; RH050 1F (A2) se nenabízí → vynechán."""
import json, os, re, fitz

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_NAME = "Spare Part List - revised.pdf"
SRC = os.path.join(HERE, "..", "..", "REO", "PW R290", SRC_NAME)
MODELS = {  # BOM jednotky → (id, název, fáze, výkon dle kódu)
    "CP-RW0300114": ("RH030", "RH030", "1F", 8),
    "CP-RW0400086": ("RH040", "RH040", "1F", 12),
    "CP-RW0500126": ("RH050", "RH050", "3F", 15),
    "CP-RW0600061": ("RH060", "RH060", "3F", 22),
    # CP-RW0500125 = RH050 1F — neděláme
}
CODE = re.compile(r"^\d{6}-\d{4}$")
PRICE = re.compile(r"^(?:US\$)?\s*([\d,]+\.\d{2})\s*$")

def parse_page(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    i = lines.index("Unit price") + 1
    bom, variant = lines[i], lines[i + 1]
    parts, i = [], i + 2
    while i < len(lines):
        code, name = lines[i], lines[i + 1]
        assert CODE.match(code), (bom, code)
        i += 2
        spec, qty = [], None
        while not PRICE.match(lines[i]):
            l = lines[i]
            if l == "Pcs":
                pass
            elif l.endswith(" Pcs"):
                spec.append(l[:-4])
            elif re.fullmatch(r"\d+", l) and (lines[i - 1] == "Pcs" or lines[i - 1].endswith(" Pcs")):
                qty = int(l)
            else:
                spec.append(l)
            i += 1
        usd = float(PRICE.match(lines[i]).group(1).replace(",", ""))
        parts.append(dict(code=code, name=name, spec=" ".join(spec).strip(), qty=qty, usd=usd))
        i += 1
    return bom, variant, parts

out = []
for page in fitz.open(SRC):
    bom, variant, parts = parse_page(page.get_text())
    if bom not in MODELS:
        print("vynecháno:", bom, variant)
        continue
    mid, name, ph, kw = MODELS[bom]
    out.append(dict(id=mid, model=name, phase=ph, kw=kw, bom=bom, variant=variant, parts=parts))
dst = os.path.normpath(os.path.join(HERE, "..", "data", "nahradni-dily-rh030-rh060.json"))
os.makedirs(os.path.dirname(dst), exist_ok=True)
json.dump(dict(source=f"REO/PW R290/{SRC_NAME}", currency="USD", models=out),
          open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("zapsáno:", dst, sum(len(m["parts"]) for m in out), "položek")
