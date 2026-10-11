# RH X50 — produktový katalog (CZ + EN)

Rebrand anglického prospektu výrobce „R290 Commercial Heat Pump Series“ (~/Downloads) na
**REO HEATING / RH X50**. Katalog je znovu vysázený v paletě thermavera.cz (jako katalog nádrží),
bez jakékoli zmínky o původním výrobci a jeho typovém označení.

- `katalog.html` — zdroj (česky), 4 strany A4: obálka · vlastnosti · konstrukce · parametry.
- `build.py` — z češtiny vyrobí `katalog-en.html` (slovník EN) a obě PDF přes Chrome headless;
  kontroluje, že v EN nezůstala čeština a v PDF žádná stopa výrobce, a přepisuje metadata PDF.
- `RH-X50-katalog-CZ.pdf`, `RH-X50-katalog-EN.pdf` — **verze 1** (bílá obálka s jednou jednotkou).
- `RH-X50-katalog-v2-CZ.pdf`, `RH-X50-katalog-v2-EN.pdf` — **verze 2**: obálka se scénou z originálu
  (obloha, město, obě jednotky). Obálka je v `obalka-v2.html`, build jí nahradí obálku z `katalog.html`,
  strany 2–4 jsou shodné. Scéna `obrazky/obalka-scena.jpg` je vyrenderovaná z originálního PDF
  po odstranění všech vektorů a textu (loga POWER WORLD na jednotkách, ikony WIFI, nadpisy)
  a obrázku energetického štítku výrobce.
- `obrazky/` — fotky jednotky, ovladače, šasi a kompresoru vytažené z PDF (logo výrobce bylo
  v originále jen vektorovou vrstvou nad fotkami, fotky samotné jsou čisté).
- Artefakt: https://claude.ai/artifact/DLgU25cYodrY63seoi2HK4 (náhled stran + stažení PDF).

Záměrně vynecháno (verze 1): dvojitá jednotka z obálky originálu (je to větší model, ne X50) — ve verzi 2
je na přání uživatele ponechaná jako součást původní scény. Ve všech verzích chybí energetický
štítek (REO štítek má zatím nevyplněnou vnitřní hlučnost „00 dB“ — viz ../README.md).
Kompresor HIGHLY je uveden jako značka komponenty (není to výrobce jednotky).
