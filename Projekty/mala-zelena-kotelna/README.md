# Malá zelená kotelna — 2 × REO RH060 (malé bytové domy)

Vzorová nabídka pro menší BD (tepelná ztráta ≈ 12–22 kW, typicky 6–10 bytů), odvozená z
`vzor-bytove-domy/` (stejná grafika, struktura i předpoklady výpočtu). Sestava: **2 × RH060 v kaskádě,
AKU 1 000 l (s el. patronou jako rezervou), TUV 1 000 l s topným hadem**. Modelový dům = ztráta 18 kW.

## Výkon RH060 (max., výkonová mapa — `REO/R290-datove-listy/src/data.js`)
| Bod | 1 × RH060 | COP | 2 × RH060 |
|---|---|---|---|
| A7/W55 | 20,4 kW | 3,03 | 40,8 kW |
| A−15/W45 | 11,8 kW | 2,08 | 23,6 kW |
| A−15/W55 | 11,4 kW | 1,78 | 22,8 kW |

Dům 18 kW při −15 °C/45 °C: kaskáda kryje 131 % (rezerva ≈ 5,6 kW na TUV), jedna jednotka sama do ≈ −8,5 °C,
příkon obou ≈ 11,4 kW.

## Soubory
- `nabidka.html` — nabídka (tisk / PDF z prohlížeče, 8 stran A4); interní blok se netiskne.
- `schema-kaskada.svg` ← `src/gen_schema.py`; vložení do nabídky `src/build_nabidka.py`:
  `python3 mala-zelena-kotelna/src/gen_schema.py && python3 mala-zelena-kotelna/src/build_nabidka.py`
- `src/model.py` — krytí ztráty + ekonomika (ÚT = ztráta × 2 000 h, TUV 70 %, SCOP 3,5/2,8, el. 3 500 Kč/MWh,
  servis 15 000 Kč). Čísla v sekcích 2, 5 a 12 přepsaná ručně.

## Otevřené body
1. **Ceny dodá uživatel** — vnitřní část kotelny a 2 × RH060. Pole `doplní se` (sekce 4, 5, 12) nahradit,
   do `model.py` zadat `PRICE_IN`, `PRICE_TC` a doplnit návratnost.
2. Splátky pro RH060 (sekce 6) zatím bez čísel.

## Artefakt „Malá zelená kotelna“
https://claude.ai/artifact/FP1LcxrM6Kn4XJaaHVnahK (soukromý, sdílí se přes Share). Stejné řešení jako u vzoru:
obsah `nabidka.html` bez interní poznámky + tlačítko **„Stáhnout nabídku v PDF“** (`capabilities: {"downloads": true}`,
PDF vložené jako base64 `PDF_B64`). Po každé změně nabídky: 1) vytisknout PDF headless Chromem (viz `vzor-bytove-domy/README.md`),
2) složit stránku artefaktu (title + style + `<div class="doc">…` + skript s PDF), 3) publikovat na stejnou URL.
Grafický design = „Zelená kotelna – vzor“ (`ThermaVera nabídky/Zelená kotelna - Thermavera.pdf`): karty sestav, odznaky, callouty.

