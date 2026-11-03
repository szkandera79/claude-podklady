# RH X50 / RH X100 — prezentace (rebrand + překlad)

Věrný rebrand a český překlad prezentace výrobce „R290 Commercial Heat Pump Introduction“
(`../../R290 Commercial Heat Pump Introduction 20250411.pdf`, 60 snímků 960×540 pt) na **REO HEATING RH X50 / RH X100**.
Sazba, fotky a schémata zůstávají; mění se značka a jazyk.

- `prezentace.py extract` → `cz/segments.json` + `cz/en.json` (texty k překladu)
- překlad: `cz/cs_1.json` (str. 1–25), `cs_2.json` (26–45), `cs_3.json` (46–60); `""` = text odstranit,
  `\n` = řádky tabulky na místa původních řádků, `{IKONA}` = mezera pro ikonu tlačítka; ruční úpravy sazby v `cz/override.json`
- `prezentace.py build` → `REO-RH-X50-X100_prezentace-CZ.pdf` (+ kontrola odkazů na výrobce)
- `prezentace.py build en` → `REO-RH-X50-X100_presentation-EN.pdf`: anglický originál jen s rebrandem; přepsané úseky
  (typy, značka, Wi‑Fi, překlepy, zmírněné úspory na str. 9) v `en/en_fix.json`
- Obě verze jsou v artefaktu Manuály https://claude.ai/artifact/2DUqsPohBnVWECCKqTdYYu (sekce RH X50, `rh-x50/`)

Rebrand: logo v záhlaví i na titulce → logo REO HEATING; fotka sídla výrobce na oddělovacích snímcích →
AI vizualizace z letáku (`../letak/assets/hero-podnik-na-vysku.png`); titulek a „Děkujeme!“ (rastry) česky;
schéma kaskády „PW 150“ → „RH X50“; Wi‑Fi „pwwm“ ve snímku aplikace → „MyWiFi“; ikony vložených příloh výrobce
(str. 42, 48, 49, 59) odstraněny; PW150/PW300-DKZLRS-E → RH X50 / RH X100; „Power World“ → REO HEATING; metadata.
Tvrzení o úsporách 50 % / 75 % (str. 9) zmírněno na „u vhodných projektů orientačně“.

Zůstává anglicky (rastrové obrázky): popisky v hydraulických a elektrických schématech (str. 7, 8, 14, 16, 21, 22,
27, 28, 31, 32, 38, 42), tabulky parametrů na str. 51 a 52, displej ovladače a aplikace (ovladač je anglický).
Na fotkách zůstávají cizí značky příslušenství (zásobník, manometr) – nejde o výrobce TČ.
