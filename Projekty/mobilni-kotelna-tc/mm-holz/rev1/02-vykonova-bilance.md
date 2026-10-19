# 02 – Výkonová bilance kotelny (rev1)

Všechna čísla pocházejí z `src/rev1.py`. Značení: [P] podklady klienta, [D] výrobce, [O] vlastní výpočet nebo odhad.

## 1. Skutečná potřeba tepla z měření MM Holz (nový podklad rev1)

**Zdroj [P]:** `podklady/dodavka-tepla-alignum-2006-2026.xlsx`
- měsíční odečty dodávky tepla z teplovodu MM Holz za 2006–2026 (R. Míček),
- zahrnují vytápění i TUV,
- 2017–2018: měření nefunkční, nové měřidlo od 30. 11. 2018 → roky vyřazeny.

**Venkovní teploty [O]:** denní průměry pro Paskov (Open-Meteo, reanalýza ERA5), `src/meteo_paskov.json`.

**Metoda [O]:** měsíční regrese

`Q_měsíc = základ × dny + H × Σ (t_b − t_den)⁺ × 24 h`

Hledala se teplota otopné hranice t_b, při které je shoda s měřením nejlepší.

| Období | Otopná hranice t_b | Měrná potřeba H | Základ (TUV + ztráty) | R² | P při −12 °C | P při −15 °C |
|---|---|---|---|---|---|---|
| **2021–2025 (návrh)** | **15,5 °C** | **2,254 kW/K** | 3,6 kW | 0,962 | **62,0 kW** | **68,7 kW** |
| 2019–2025 | 15,5 °C | 2,251 kW/K | 3,8 kW | 0,960 | 61,9 kW | 68,7 kW |
| 2007–2026 bez 2017–18 | 14,0 °C | 2,579 kW/K | 3,7 kW | 0,927 | 67,1 kW | 74,8 kW |
| 2009–2016 | 13,0 °C | 2,936 kW/K | 3,2 kW | 0,940 | 73,4 kW | 82,2 kW |

**Závěry:**
- Výkon P je **denní průměr** potřeby na vytápění bez TUV. Pro návrh se přidává rezerva **×1,10** na ranní náběh, vítr a hodinová minima [O].
- Spotřeba se po roce 2016 snížila o ≈ 20 % (provoz, regulace, úpravy objektu – příčina **[CHYBÍ]**). Starší roky slouží jako horní mez, návrh vychází z let 2021–2025.
- Roční odběr 2019–2025: 140–193 MWh (vč. TUV). Na vytápění připadá podle regrese 112–147 MWh/rok.
- Nejchladnější den v datech: denní průměr −18,1 °C (4. 2. 2012). Za 2019–2026 nejnižší průměr −12,7 °C (9. 1. 2024).
- **Projektová hodnota ≈ 105 kW** (hala 88 kW + administrativa 17 kW, z průtoků čerpadel) je přibližně **1,6× vyšší** než skutečnost. Pro návrh se nepoužívá, slouží jen k ověření otopných těles.

## 2. Návrhový výkon

| Venkovní teplota (denní průměr) | Potřeba z měření | ×1,10 (návrh) |
|---|---|---|
| +5 °C | 23,6 kW | 26,0 kW |
| 0 °C | 34,9 kW | 38,4 kW |
| −5 °C | 46,2 kW | 50,8 kW |
| −10 °C | 57,5 kW | 63,2 kW |
| **−12 °C (výpočtová dle projektu)** | **62,0 kW** | **68,2 kW** |
| −15 °C | 68,7 kW | 75,6 kW |
| −18 °C (rekord 2012) | 75,5 kW | 83,0 kW |

**Návrhový výkon vytápění: 68 kW při −12 °C, s kontrolou na 76 kW při −15 °C.** TUV není součástí projektu.

## 3. Pokrytí zdroji

TČ = 2 × RH X50, max. otáčky, výkonová mapa [D]. EK = elektrická bivalence po 6 kW, max. 72 kW. Proud = TČ + EK + pomocné spotřebiče.

| t_e | Potřeba ×1,10 | TČ W55 | TČ W60 | Deficit (při W55) | Stupně EK | Celkový proud |
|---|---|---|---|---|---|---|
| +5 | 26,0 | 79,4 | 70,0 | 0 | 0 | 82 A* |
| 0 | 38,4 | 75,2 | 64,8 | 0 | 0 | 78 A* |
| −5 | 50,8 | 71,0 | 59,4 | 0 | 0 | 74 A* |
| −7 | 55,8 | 66,2 | 57,0 | 0 | 0 | 69 A* |
| −10 | 63,2 | 62,0 | 53,2 | 1,2 | 1 (6 kW) | 74 A |
| −12 | 68,2 | 54,4 | 50,8 | 13,8 | 3 (18 kW) | 84 A |
| −15 | 75,6 | 49,6 | 44,4 | 26,0 | 5 (30 kW) | 99 A |
| −18 | 83,0 | 44,8 | 38,2 | 38,2 | 7 (42 kW) | 111 A |

\* Proud TČ při max. otáčkách. Při částečném výkonu je skutečně nižší.

**Bod bivalence:**
- **≈ −9,6 °C** při výstupu z TČ 55 °C,
- ≈ −7,3 °C při 60 °C.

Mapa X50 při vyšší teplotě vody dává méně výkonu. Regulace proto drží teplotu z TČ co nejnižší (kap. 06).

**Energie [O]:** simulace po dnech 2021–2025, bez rezervy 1,10. TČ konzervativně při COP max. otáček a W55.

| Rok | Teplo ÚT | Elektřina TČ | SPF TČ | Teplo z EK |
|---|---|---|---|---|
| 2021 | 147,4 MWh | 64,8 MWh | 2,27 | 0,41 MWh (0,3 %) |
| 2022 | 131,7 MWh | 56,8 MWh | 2,32 | 0 |
| 2023 | 120,5 MWh | 51,6 MWh | 2,33 | 0 |
| 2024 | 111,6 MWh | 47,6 MWh | 2,34 | 0,34 MWh (0,3 %) |
| 2025 | 128,7 MWh | 55,3 MWh | 2,33 | 0 |

**Elektrická bivalence je energeticky zanedbatelná (< 1 %).** Její smysl je spolehlivost: pokrytí extrémních mrazů a záloha při poruše TČ. SPF je spodní odhad. Při ekvitermní teplotě (ve většině sezóny 35–50 °C) a částečném výkonu bude vyšší.

## 4. Dimenzování bivalence

| Požadavek | Potřebný výkon EK | 48 kW (2 × 24) | **72 kW (3 × 24)** |
|---|---|---|---|
| Bivalentní provoz při −15 °C (×1,10) | 26 kW | ano | ano |
| Bivalentní provoz při −18 °C | 38 kW | ano | ano |
| Výpadek 1 × X50: X50 (W55) + EK | — | pokryje do −14,1 °C | pokryje do **−19,6 °C*** |
| **Výpadek obou X50: jen EK** | 68–76 kW | jen do −3,8 °C | do **−13,5 °C** (s rezervou 1,10), do −16,4 °C bez rezervy |

\* Proudový limit při běžící jedné X50 dovolí 11 stupňů (66 kW).

**Doporučení:**
- Bivalenci **72 kW (12 × 6 kW) ponechat.**
  - 48 kW stačí pro bivalentní provoz, ale ne jako samostatný zdroj.
  - 72 kW pokryje při poruše obou TČ celou potřebu do ≈ −13,5 °C (projektová výpočtová teplota je −12 °C).
- Pod −13,5 °C a při poruše obou TČ: řízené omezení (hala 15 °C, prioritně administrativa). Viz scénář 2 v `07-provozni-stavy.md`.
- **72 kW nepokrývá projektových 88 kW (resp. 105 kW).** Kdyby objekt takový výkon skutečně potřeboval, samotná elektřina by stačila jen do ≈ −4 °C. Měření ukazuje, že tuto potřebu nemá. Riziko se změní při změně provozu (např. vyšší teplota v hale).

## 5. Elektrický příkon (přívod 3 × 160 A)

| | Proud na fázi |
|---|---|
| 2 × RH X50 max. (návod [D]) | 64 A |
| 12 stupňů EK × 8,7 A | 104 A |
| Čerpadla, PLC, ostatní [O] | 5 A |
| **Teoretický součet** | **173 A > 160 A** |
| Trvalý limit regulace (85 %) | 136 A |
| Krátkodobý limit (95 %, ≤ 60 s) | 152 A |
| Okamžité odpojení všech stupňů EK | 150 A |

**Skutečné stavy:**
- Při −18 °C ≈ 111 A, v nouzovém režimu bez TČ ≈ 109 A. Obojí je pod limitem.
- Při plném proudu obou X50 (64 A) dovolí limit jen **7 stupňů (42 kW)**. To na −18 °C stačí.
- Omezovač příkonu proto v běžném provozu prakticky nezasahuje, ale musí existovat.

**Hodnota 33,6 kW** pro dvě X50 (zadání) není doložena. Návod uvádí max. **20 kW / 32 A** na jednotku. Mapa při W55–W70 dává 16–18 kW příkonu na jednotku.
