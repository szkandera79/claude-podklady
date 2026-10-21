# Záznam změn rev0 → rev1 (19. 10. 2026)

- rev0 (`../README.md`, `../src/sestavy.py`, `../email-dornak-koncept.md`) zůstává **beze změny** jako archiv.
- Všechny změny jsou jen ve složce `rev1/`.

| # | Oblast | rev0 | rev1 | Důvod |
|---|---|---|---|---|
| Z1 | Zdroje | 2 × RH X50 bez bivalence (V4); V3 vyloučena | 2 × RH X50 + elektrická bivalence 72 kW (12 × 6 kW) | zadání rev1 |
| Z2 | Návrhový výkon | projektový odhad 88 kW hala + 17 kW administrativa; skutečná ztráta neznámá | **z měření MM Holz 2021–2025: 62 kW (−12 °C), 69 kW (−15 °C); návrh × 1,10 = 68 / 76 kW** | nový podklad: statistika dodávky tepla |
| Z3 | Umístění | kontejner 20′ (studie) | stávající kotelna (varianta A), kontejner jako varianta B | zadání rev1 + možný odkup Alignem |
| Z4 | Připojení | za výměník (doporučení rev0) | za výměník HV VS – potvrzeno | rozhodnutí z auditu |
| Z5 | Akumulace | AKU 1 000 l nebo 2 × 300 l | AKU 2 × 1 000 l **jen pro topnou vodu** (bez výměníků a patron), přednostně ze skladu; paralelně, čidla nahoře / uprostřed / dole | zadání rev1, upřesnění zadavatele 19. 10. |
| Z6 | Bivalence – zapojení | — | sériový dohřev přívodu za AKU (vstřikovací okruh, P4), obtok AKU V3 | audit: paralelní zapojení ohřívá vstup do TČ |
| Z7 | Max. teplota | 70 °C z X50 do −10 °C, 60 °C do −25 °C | max. 70 °C, ale TČ jen do 65/60 °C, 70 °C z EK; potřeba z měření 55–63 °C | výkonová mapa + měření |
| Z8 | TUV | ACV 320 ohřívaná z kaskády X50 | mimo projekt (zadání) – otevřeno O11 | zadání rev1 |
| Z9 | Elektro | 2 × X50: jistič 3 × 80 A | vyhrazený přívod 3 × 160 A, dynamické omezení EK, PR 150 A | zadání rev1; souběh 173 A > 160 A |
| Z10 | Glykol | doporučen (studie) | primár X50 s PG 35 % + deskový výměník – zachováno | návod X50 [D] |
| Z11 | Regulace | PLC kaskáda (studie) | kompletní algoritmus vč. bivalence, rotace, omezovače příkonu, režimů | zadání rev1 |
| Z12 | Rozpočet | žádný | nový položkový rozpočet A/B, práce 50 000 Kč [Z]; nabídka CN26OV1321 zatím nezapracována | zadání rev1 |
| Z13 | E‑mail p. Dorňákovi | koncept 2 × X50 + TUV | **neaktuální** – před odesláním přepracovat podle rev1 | rozpor se Z1, Z8 |
| Z14 | Rozpočet AKU | 2 × 30 000 [O] | 2 × 19 850 + doprava = 42 700 [N] (Allegro PS-00, skutečný objem 843 l) | nabídka dodaná zadavatelem 19. 10. |
| Z15 | TUV | mimo projekt (Z8) | **TUV zajištěna**: stávající ACV 320 l ohřívaná z topné vody přes stávající větev; PLC zvyšuje přívod na 65 °C, dezinfekce 70 °C z el. dohřevu | upřesnění zadavatele 19. 10. |
| Z16 | Připojení | za výměník HV VS (Z4) | **rev1-B (zadavatel 20. 10.): kotelna TČ napájí primár stávajícího výměníku HV VS, teplovod MM Holz zůstává připojen jako záloha (ruční přepnutí uzávěry, nikdy současně); TUV dál přes výměník.** Schéma `10-schema-zapojeni-vymenik.svg`. Dopad: ztráta 3–5 K na výměníku, tlakové oddělení od teplovodu (AKU max. 3 bar) | rozhodnutí zadavatele |
| Z17 | Glykol / výměník TČ | glykolový primár + deskový výměník VS-TČ (Z10) | **bez výměníku: RH X50 přímo do AKU, voda bez glykolu** + protimrazové ventily, záložní napájení čerpadel, topné kabely, alarm (zadavatel 21. 10.). Úspora ≈ 70–100 tis. Kč a 2–3 K; riziko zamrznutí při dlouhém výpadku proudu | rozhodnutí zadavatele |

Nové soubory:
- `00-audit.md` … `09-otevrene-body.md`,
- `04-hydraulicke-schema.svg`, `05-elektro-mar-schema.svg`,
- `src/rev1.py`, `src/dodavka_tepla.json`, `src/meteo_paskov.json`,
- `../podklady/dodavka-tepla-alignum-2006-2026.xlsx`.
