# 08 – Položkový rozpočet (rev1)

Ceny jsou v Kč bez DPH.

**Typ ceny:**
- **[N]** ověřená cena z nabídky dodavatele,
- **[Z]** údaj zadavatele,
- **[V]** předpokládaná velkoobchodní cena,
- **[O]** vlastní odhad (orientačně, k ověření poptávkou).

> **Stav:** nabídka dodavatele **CN26OV1321** (napojovací komponenty, hydraulika, elektrokotel) je přiložena v Mailu, ale soubor zatím nelze otevřít [CHYBÍ]. Položky označené ⟲ se po jejím přečtení nahradí cenami [N]. Do té doby platí odhady [O].
>
> Předchozí verze (rev0) žádný rozpočet neobsahovala. Rozpočet je proto nový, ne aktualizovaný.

## A. Technologie elektrické bivalence

| # | Položka | Množství | Cena | Typ |
|---|---|---|---|---|
| A1 | Elektrokotel / průtokový ohřívač 24 kW, 4 sekce po 6 kW, externí řízení stykači, STB, PV | 3 ks | 3 × 30 000 = 90 000 | ⟲ [O] |
| A1-alt | Protherm RAY 24 KE (kandidát ze zadání; externí řízení po 6 kW nedoloženo) | 3 ks | cena [CHYBÍ] | ⟲ |
| A2 | Čerpadlo P4 EC (≈ 3,6 m³/h, 3–5 m), zpětná klapka, průtokový spínač FS, vyvažovací ventil, uzávěry, teploměry | 1 sada | 30 000 | ⟲ [O] |
| A3 | Potrubí okruhu EK DN40, tvarovky, izolace, odbočky A–B na DN65 | 1 sada | 12 000 | ⟲ [O] |
| A4 | Rozvaděčová část EK: QF-EK 125 A, KM-EK0, 12 × stykač AC-1 25 A, 3 × jistič 40 A, svorky, kabeláž | 1 | 45 000 | [O] |
| A5 | Bezpečnostní řetězec: STB-AKU, proudové relé PR, tlačítko TOTAL STOP | 1 | 8 000 | [O] |
| A6 | Měření příkonu PM (Modbus) + 3 × MTP 200/5 A | 1 | 9 000 | [O] |
| A7 | PLC – rozšíření (12 DO, 4 AI, 4 DI) + programování bivalence, omezovače příkonu, alarmů, odzkoušení | 1 | 45 000 | [O] |
| | **Mezisoučet A** | | **≈ 239 000** | |

## B. Ostatní technologie kotelny (podklad pro odkup)

| # | Položka | Množství | Cena | Typ |
|---|---|---|---|---|
| B1 | Tepelné čerpadlo REO RH X50 (sklad) | 2 ks | 2 × 110 000 = 220 000 | [Z] |
| B2 | **Akumulační nádrž 1 000 l, jen pro topnou vodu** (bez výměníků a el. patron) – přednostně ze skladu; jinak nákup: **Allegro „Tepelný pufr 1000 l“ PS-00, nabídka 16343165815**, 24 018 Kč s DPH = 19 850 Kč bez DPH/ks + doprava od 1 800 Kč s DPH (≈ 1 490 Kč bez DPH) | 2 ks | 2 × (19 850 + 1 490) = **42 700** | [N]** |
| B3 | Deskový výměník VS-TČ 100 kW glykol/voda + náplň PG 35 % (≈ 200 l) | 1 | 52 000 | ⟲ [O] |
| B4 | Čerpadlo P2 EC 17 m³/h, 5 m + P1a/P1b k X50 (≈ 11 m³/h, 12–13 m, glykol) | 3 ks | 60 000 | ⟲ [O] |
| B5 | Hydraulika kotelny: potrubí DN65/DN80, armatury, filtr + magnetický odkalovač, expanze 200 l + 35 l, PV, manometry, izolace | 1 | 95 000 | ⟲ [O] |
| B6 | Obtok AKU V3 – 3cestný ventil DN65 s pohonem | 1 | 18 000 | ⟲ [O] |
| B7 | Kalorimetr MID na přívodu | 1 | 9 000 | [O] |
| B8 | Rozvaděč R-K silová část TČ: QS0 160 A, SPD T1+T2, 2 × 40 A + RCD typ B, AUX, skříň | 1 | 45 000 | [O] |
| B9 | PLC základ, HMI, 4G router, UPS 24 V, čidla (12 × Pt1000), tlaková čidla | 1 | 55 000 | [O] |
| B10 | Venkovní část: patky, antivibrační uložení, izolované glykolové potrubí DN80, prostupy | 1 | 40 000 | [O] |
| B11 | Projekt elektro, revize elektro, tlakové zkoušky, dokumentace pro předání a odkup | 1 | 35 000 | [O] |
| | **Mezisoučet B** | | **≈ 671 700** | |

\*\* Cena z veřejné nabídky Allegro k 19. 10. 2026 (prodejce wise_solution, odeslání z Polska, dodání ≈ 14 dní, „S fakturou s DPH“). Přepočet na cenu bez DPH 21 % je náš.

Parametry podle nabídky:
- **skutečný objem 843 l**,
- výška 199 cm, Ø 79 cm bez izolace / 96 cm s odnímatelnou izolací,
- max. 95 °C, 5 bar,
- 9 × 6/4″, možnost el. tělesa,
- třída B, výrobce neuveden.

Pokud budou nádrže ze skladu, platí skladová cena [Z].

Změna proti předchozí verzi rozpočtu: B2 60 000 [O] → 42 700 [N], mezisoučet B 689 000 → 671 700.

## C. Práce

| # | Položka | Cena | Typ |
|---|---|---|---|
| C1 | Montáž hydrauliky, elektro a uvedení do provozu (celkem) | **50 000** | [Z] |

## D. Varianta B – mobilní kotelna v kontejneru 20′ (místo instalace do stávající kotelny)

Ceny jsou převzaté z modelu `mobilni-kotelna-tc/src/model.py` [O]. X50 stojí vedle kontejneru, bez vzduchové komory.

| # | Položka | Cena | Typ |
|---|---|---|---|
| D1 | Kontejner 20′ (použitý, cargo worthy) | 60 000 | [O] |
| D2 | Technická místnost: zateplení, obklad, podlaha, větrání | 32 000 | [O] |
| D3 | Detektor R290, osvětlení, zásuvky, temperování | 22 000 | [O] |
| D4 | Nátěr, značení, bezpečnostní tabulky | 12 000 | [O] |
| D5 | Propojení s objektem: 2 × DN65 izolované (≈ 2 × 15 m), prostup | 45 000 | [O] |
| D6 | Doprava, usazení HDS, podkladní panely | 32 000 | [O] |
| | **Příplatek za kontejner** | **≈ 203 000** | |

## E. Souhrn

| | Stávající kotelna (A) | Kontejner (B) |
|---|---|---|
| A – elektrická bivalence | 239 000 | 239 000 |
| B – ostatní technologie vč. 2 × X50 | 671 700 | 671 700 |
| C – práce | 50 000 | 50 000 |
| D – kontejner | — | 203 000 |
| Rezerva 7 % [O] | 67 300 | 81 500 |
| **Celkem orientačně** | **≈ 1 028 000** | **≈ 1 245 000** |

**Pro odkup Alignem po 6 měsících:**
- Varianta A nevyžaduje přesun a je levnější.
- Kontejner má smysl jen tehdy, když se technologie do kotelny nevejde, nebo když je pravděpodobné, že se kotelna po pronájmu přesune jinam.
- Odkupní cenu je vhodné odvodit z položek B1–B11 + A, s odpočtem částí nájmu.
- Cena tepla ani výše nájmu nejsou známé, kalkulace odkupu je proto otevřená (09).

> Rozpočet je orientační, bez DPH. Nejde o nabídku. Neobsahuje úpravy objektu (stavební připravenost, přívod 3 × 160 A z hlavního rozvaděče objektu, případné bourací práce).
