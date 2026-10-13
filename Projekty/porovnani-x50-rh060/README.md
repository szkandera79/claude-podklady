# Jednotky pro kaskády bytových domů — RH X50 / RHX30 Pro / RHX20 Pro / RH060

Interní technicko-ekonomické srovnání (27. 9. 2026, verze 4 — s výkonovou mapou RHX30 Pro). Artefakt: https://claude.ai/artifact/2AcWz8XpzRdwie36GZCuKY
(republikovat z `analyza.html` přes parametr `url`).

## Základ srovnání
- Certifikované body KEYMARK (EN 14825/14511, stejná zkušebna, 14. 8. 2026) — COP při Tj −10/−7/+2/+7/+12 °C
  při stejné relativní zátěži, W35 a W55. Přepočet na české klima (výpočtová −15 °C), režimy 35/30, 45/38, 55/45, 65/50.
- RHX30 Pro: výkonová mapa výrobce (~/Claude/REO/PW Helios/…Performance curve.xls); RHX20 Pro odvozena z ní × 0,69; W65 u RH060/X20 odhad.
- TUV 55 °C: 50 % ohřev studené vody (ceníkové body A7/A20) + 50 % cirkulace (jmenovitý bod A7/W55).
- Nákupní ceny EXW (~/Claude/PW Obchodní, faktury 2023/2025): X50 US$ 4 800, RH060 US$ 2 398; X30 3 680 €, X20 2 940 € (ceník 2026), RH060 US$ 2 398 (ceník 10/2024); kurz ČNB 23. 9. 2026.
- X30 / X20 = pracovní názvy (výrobní řada 20/30 kW). Původní výrobce ani typová označení se ve výstupech neuvádějí.

## Soubory
- `src/keymark_model.py` → `src/results2.json` (data jednotek, SCOP CZ, scénáře 25–150 kW × 4 režimy, citlivost na tarif)
- `src/gen_doc.py` → vloží cenovou mapu, grafy a tabulky do `analyza.html`

    python3 porovnani-x50-rh060/src/keymark_model.py && python3 porovnani-x50-rh060/src/gen_doc.py

## Otevřené body
1. RHX30 Pro: mapa (−10/W55 21,8 kW) vs. KEYMARK (26,8 kW) — ověřit měřením; X20 bez mapy.
2. Data W65 pro X30/X20/RH060; RH070 bez mapy i certifikace.
3. Podíl cirkulace TUV a COP ohřevu TUV jsou předpoklady.
4. RH060: starší protokol ErP (2023) uvádí SCOP 4,69/3,55 a COP 4,63; aktuální KEYMARK 4,80/3,89 a 4,67.
