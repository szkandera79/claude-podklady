# REO R290 Smart – přímé připojení FV panelů (pracovní podklad)

Stav 2026-10-13. Zdroj: prezentace CZ str. 15 (tabulka FV), str. 41–43 (schémata), ERP report a energetické štítky výrobce.
**Předběžné – napěťové a proudové limity čekají na potvrzení výrobcem.**

## Nabízené varianty
- RH06 – **pouze 1F** (ERP report: „single phase 6/8/10 kW, 3 phase 8/10/12/14/16 kW“; štítek PW06 existuje jen jednofázový)
- RH08–RH16 – nabízíme **jen 3F**

## Limity výrobce
| Model | Uoc (tabulka) | Uoc (schéma) | Imax | Pmax DC |
|---|---|---|---|---|
| RH06 1F | 200–400 V | max 310 V | 13 A | 3,5 kW |
| RH08 3F | 250–600 V | < 550 V | 13 A | 4,5 kW |
| RH10–16 3F | 250–600 V | < 550 V | 13 A | 5,5 kW |

Návrhový limit = nižší hodnota ze schématu (310 V / 550 V), dokud výrobce nepotvrdí vyšší.

## Výpočet
Uoc stringu při −25 °C = n × Voc(STC) × (1 + |β| × 50 K); β = 0,28 %/K (konzervativně).
Panel 500 Wp: Voc 41–49 V dle typu → Voc za mrazu 46,7–55,9 V.

| Model | Doporučeno (500 Wp) | Podmínka | Uoc za mrazu | Nikdy víc než |
|---|---|---|---|---|
| RH06 1F | **5 ks = 2,5 kWp** | Voc ≤ 54 V | ≤ 280 V | 6 ks jen při Voc ≤ 45 V (308 V) |
| RH08 3F | **9 ks = 4,5 kWp** | Voc ≤ 53 V | ≤ 503 V | 9 ks (= Pmax) |
| RH10–16 3F | **10 ks = 5,0 kWp** | Voc ≤ 48 V | ≤ 551 V (při 49 V) | 11 ks jen při Voc ≤ 43 V a potvrzení 600 V |

Minimum: RH06 5 ks, 3F 7 ks (spodní mez 200/250 V v létě).
Vždy 1 string, žádné paralelní řazení (Imax 13 A).

## Otevřené body pro výrobce
- platí 310/550 V (schéma) nebo 400/600 V (tabulka)?
- je 13 A limit provozního proudu, nebo i zkratového Isc? (panely 500 Wp mají Isc 13,5–15 A)
- str. 42 prezentace (RH10–16 1F) obsahuje 3F schéma
- RHX30/40 v tabulce FV chybí
