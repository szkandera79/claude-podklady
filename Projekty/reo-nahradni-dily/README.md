# Náhradní díly RH030–RH060 (interní ceník)

Nákupní ceník náhradních dílů výrobce k řadě REO RH030–RH060 (R290), ceny v **USD/ks** + přepočet na Kč bez cla a DPH i s clem (výchozí 2,5 %, upravitelné) a DPH 21 %.
Zdroj: `REO/PW R290/Spare Part List - revised.pdf` (26. 10. 2026; strana = model). Starší `Spare Part List.xlsx` je nahrazen.

| Soubor | Obsah |
|---|---|
| `data/nahradni-dily-rh030-rh060.json` | export 98 položek (RH030, RH040, RH050 3F, RH060) (kód BOM, název, specifikace, ks, USD) |
| `nahradni-dily.html` | artefakt: záložky modelů, hledání, skupiny dílů, srovnání modelů, kurz přepisovatelný |
| `src/export_json.py`, `src/build_html.py` | PDF → JSON → HTML |

Build: `python3 reo-nahradni-dily/src/export_json.py && python3 reo-nahradni-dily/src/build_html.py`
Kurz: konstanta `RATE` v `build_html.py` (ČNB 23. 10. 2026 = 21,741 Kč/USD).

## Pozor v datech
- RH050 se nabízí **jen ve 3F** (BOM CP-RW0500126); strana RH050 1F (CP-RW0500125) se při exportu vynechává.
- Clo 2,5 % je výchozí odhad (dle HS kódu dílu upravit), DPH 21 % z ceny vč. cla; doprava není zahrnuta.
- Interní podklad (nákupní ceny) — nešířit zákazníkům; v materiálech pro zákazníky neuvádět výrobce.
