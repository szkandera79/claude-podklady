# Náhradní díly RH030–RH060 (interní ceník)

Nákupní ceník náhradních dílů výrobce k řadě REO RH030–RH060 (R290), ceny v **USD/ks** + přepočet na Kč bez cla a DPH i s clem (výchozí 2,5 %, upravitelné) a DPH 21 %.
Zdroj: `REO/PW R290/Spare Part List.xlsx` (listy 030, 040, 050 S, 050 3 phase, 060).

| Soubor | Obsah |
|---|---|
| `data/nahradni-dily-rh030-rh060.json` | export všech 118 položek (kód BOM, název, specifikace, ks, USD) |
| `nahradni-dily.html` | artefakt: záložky modelů, hledání, skupiny dílů, srovnání modelů, kurz přepisovatelný |
| `src/export_json.py`, `src/build_html.py` | xlsx → JSON → HTML |

Build: `python3 reo-nahradni-dily/src/export_json.py && python3 reo-nahradni-dily/src/build_html.py`
Kurz: konstanta `RATE` v `build_html.py` (ČNB 23. 10. 2026 = 21,741 Kč/USD).

## Pozor v datech
- List „050 3 phase“ = kopie RH040 (stejný BOM CP-RW0400086 i díly) → ověřit u dodavatele.
- Interní podklad (nákupní ceny) — nešířit zákazníkům; v materiálech pro zákazníky neuvádět výrobce.
