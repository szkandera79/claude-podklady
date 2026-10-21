# REO R290 Smart – přímé připojení FV panelů (pracovní podklad)

Stav 2026-10-21. Zdroj: odpověď výrobce „Direct PV Drive – Point-by-Point Response“ (21. 10. 2026),
prezentace CZ str. 15 a 41–43, ERP report. Výrobce **nepublikuje**: max. Isc, rozsah MPPT, počet MPPT vstupů,
reakci na kolísání FV, specifikaci desky MPPT, požadavky na DC jištění, samostatný manuál.

## Nabízené varianty
- RH06 – **pouze 1F** (ERP report a štítky: 1F 6/8/10 kW, 3F 8–16 kW)
- RH08–RH16 – nabízíme **jen 3F**; RHX20 Pro / RHX30 Pro – 3F
- Deska MPPT je **volitelná** u všech modelů (nutno objednat), nastavení DIP SW4.2.

## Limity výrobce (odpověď 21. 10.)
| Model | Tvrdý limit Uoc stringu | Okno Uoc | Imax | Pmax = max. kWp |
|---|---|---|---|---|
| RH06 1F | **< 311 V** | 200–400 V | 13 A | 3,5 kW |
| RH08 3F | **< 537 V** | 250–600 V | 13 A | 4,5 kW |
| RH10–16 3F | **< 537 V** | 250–600 V | 13 A | 5,5 kW |
| RHX20 Pro / RHX30 Pro | **< 537 V** | 250–600 V | **20 A** | 11 kW |

- 311 V = 220 V × √2, 537 V = 380 V × √2 → špičkové napětí usměrněné sítě na DC sběrnici; FV nesmí být nad ním.
- **Předimenzování výrobce nedoporučuje** – pole dimenzovat na Pmax.
- Hybrid: FV + síť se sčítají na DC straně (ne přepínání); z FV jen kompresor (> 80 % příkonu jednotky),
  ventilátory, čerpadla a řízení vždy ze sítě. Přechod automatický.
- Výrobce uvádí „max. 6 ks (1F) / 10 ks (3F) při Uoc panelu 50 V“ – **bez teplotní korekce**.
  10 × 50 V = 500 V při 25 °C, ale v mrazu ~570 V > 537 V → takto NEnavrhovat.

## Výpočet
Uoc stringu při −25 °C = n × Voc(STC) × 1,14 (β = 0,28 %/K, ΔT = 50 K).

| Model | Panely 500 Wp | kWp | Podmínka: Voc panelu (STC) |
|---|---|---|---|
| RH06 1F | **6 ks** | 3,0 | Voc ≤ 45,5 V |
|  | jinak **5 ks** | 2,5 | Voc ≤ 54,5 V (prakticky všechny) |
| RH08 3F | **9 ks** | 4,5 | Voc ≤ 52,3 V |
| RH10–16 3F | **10 ks** | 5,0 | Voc ≤ 47,1 V |
|  | jinak **9 ks** | 4,5 | Voc ≤ 52,3 V |
| RHX20/30 Pro | **1 × 10 ks** | 5,0 | Voc ≤ 47,1 V; 2 stringy jen s panely Imp ≤ 10 A |

- Minimum: RH06 5 ks, 3F 7 ks (spodní mez okna 200/250 V v létě).
- RH06 a 3F RH08–16: vždy **1 string** (13 A). Panel musí mít **Imp ≤ 13 A**.
- RHX Pro: 2 paralelní stringy po 10 ks = 10 kWp jen pokud součet proudů ≤ 20 A
  (běžné 500Wp panely mají Imp ~12,5–13 A → 2 stringy = 25 A, nad limitem).

## Stále otevřené (výrobce „not published“)
- max. zkratový proud Isc (500Wp panely mají Isc 13,5–15 A > 13 A)
- je 20 A u RHX celkový proud nebo na string; počet MPPT vstupů
- doporučené DC jištění → navrhujeme dle ČSN 33 2000-7-712 (odpojovač, SPD DC, pojistky dle počtu stringů)
- str. 42 prezentace (RH10–16 1F) obsahuje 3F schéma
