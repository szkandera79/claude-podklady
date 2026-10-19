# 01 – Technická zpráva, revize 1

**Akce:** náhrada dodávky tepla z teplovodu MM Holz kotelnou s tepelnými čerpadly – objekt Alignum s.r.o., Paskov – Žabeň (výroba palet; hala 1 182 m² + administrativa).
**Objednatel poptávky:** Mayr-Melnhof Holz Paskov s.r.o., Ing. Alan Dorňák.
**Stupeň:** koncepční návrh pro rozhodnutí. Nejde o prováděcí projekt; prováděcí dokumentaci zpracuje autorizovaná osoba.
**Revize:** rev1, 19. 10. 2026. Změny proti rev0 viz `ZMENY.md`.

## 1. Podklady

- **[P]** DSP ÚT „Výroba palet Paskov“ (ESL a.s., 01/2005): technická zpráva, půdorys 1.NP, výměníková stanice. Soubory `../podklady/`.
- **[P]** Statistika dodávky tepla MM Holz → Alignum 2006–2026, měsíčně: `../podklady/dodavka-tepla-alignum-2006-2026.xlsx`.
- **[D]** RH X50: návod k použití (tech. údaje, pomocný zdroj tepla), výkonová mapa výrobce (W35–W75).
- **[O]** Denní teploty Paskov 2007–2026 (Open-Meteo / ERA5), výpočty `src/rev1.py`.
- **Zadání rev1:**
  - 2 × RH X50 v kaskádě,
  - 3 × elektrokotel 24 kW (stupně po 6 kW),
  - AKU 2 × 1 000 l,
  - max. přívod 70 °C,
  - přívod 3 × 160 A,
  - TUV mimo projekt.
- **Rozhodnutí z auditu** (`00-audit.md`, 19. 10. 2026):
  - připojení za výměník HV VS,
  - sériový elektrický dohřev,
  - bilance hala + administrativa,
  - chybějící údaje označit.

## 2. Potřeba tepla

| | Hodnota |
|---|---|
| Projektový výkon (z průtoků čerpadel) | hala 88 kW (80/60 °C, 20 °C) + administrativa 17 kW (75/60 °C) = 105 kW [P, O] |
| **Skutečná potřeba z měření 2021–2025** | **62 kW při −12 °C, 69 kW při −15 °C** (denní průměr, bez TUV), H = 2,25 kW/K, otopná hranice 15,5 °C, R² 0,96 |
| **Návrhový výkon** (× 1,10) | **68 kW při −12 °C**, kontrola 76 kW při −15 °C a 83 kW při −18 °C (rekord v datech) |
| Roční teplo na vytápění | 112–147 MWh (2021–2025) |

Projektových 88 kW **není** tepelná ztráta objektu. Skutečná potřeba je ≈ 60–65 % projektu. Podrobně v `02-vykonova-bilance.md`.

## 3. Koncepce

- **Zdroj 1 (priorita):**
  - 2 × REO RH X50, kaskáda řízená PLC, venku na patkách,
  - primár s propylenglykolem 35 % [D: návod požaduje nemrznoucí směs pod 0 °C],
  - deskový výměník VS-TČ 100 kW.
- **Akumulace:** 2 × 1 000 l jen pro topnou vodu (bez výměníků a el. patron), přednostně ze skladu, paralelně (Tichelmann), čidla nahoře, uprostřed a dole. AKU slouží zároveň jako hydraulický oddělovač.
- **Zdroj 2 – elektrická bivalence a záloha:**
  - 72 kW = 3 bloky × 4 stupně po 6 kW,
  - **zapojená sériově na přívodu za AKU** jako vstřikovací okruh s čerpadlem P4,
  - dohřívá jen přívod, ne AKU, takže vstup do TČ zůstává chladný,
  - pracuje i samostatně (nouzový režim, obtok AKU V3).
- **Připojení:** na sekundár za výměníkovou stanicí HV VS (DN65), před rozdělovač RS Kombi modul 100.
  - HV VS zůstává osazena a uzavřena, aby šlo vrátit se k teplovodu.
  - Stávající čerpadla větví (hala, administrativa) zůstávají.
- **Teploty:**
  - ekviterm T_req = 38 − 1,4 × T_e, max. 70 °C,
  - z měření vychází potřeba 55 °C při −12 °C a 59 °C při −15 °C (`03`),
  - TČ pracují do 65 °C (do −12 °C), resp. 60 °C (pod −12 °C), pro tyto rozsahy má výrobce data,
  - **70 °C zajišťuje elektrický dohřev, ne TČ.**
- **TUV (upřesnění zadavatele 19. 10.):** TUV se připravuje ve stávajícím nepřímotopném zásobníku ACV Smart Line 320 l z topné vody (větev TUV na RS Kombi, čerpadlo DAB A 50/180 XM). Kotelna ji proto zajišťuje automaticky.
  - Během ohřevu TUV regulace zvýší přívod na 65 °C.
  - 1× týdně proběhne dezinfekce 70 °C, kterou zajistí elektrický dohřev (06, kap. 2a).
  - Průměrná potřeba TUV a ztrát ≈ 3,6 kW (31 MWh/rok, ze základu regrese) je v bilanci krytá s rezervou. Krátkodobé špičky dobíjení zásobníku pokryje AKU.

## 4. Výkon RH X50 při 70 °C [D – výkonová mapa výrobce, ne certifikace]

| Bod | Výkon / 1 ks | COP |
|---|---|---|
| A7/W70 | 32,3 kW | 2,00 |
| A2/W70 | 29,9 kW | 1,80 |
| A−7/W70 | 24,2 kW | 1,40 |
| A−10/W70 | 21,9 kW | 1,25 |
| A−12/W70 | **mapa neuvádí** | — |
| A−15/W70 | **mapa neuvádí** | — |

- Certifikace (KEYMARK) [C] pokrývá jen W35/W55.
- Návod uvádí výstup „20–78 °C“ a v textu „při −25 °C až 65 °C“. Výkonová mapa ale má W65 až od −12 °C a W70 až od −10 °C. **Schopnost dosáhnout 70 °C neznamená jmenovitý výkon při 70 °C**: při −10 °C dává jednotka 21,9 kW, tedy 44 % nominálu.
- Max. vstupní teplota vody do X50 **[CHYBÍ]**.
- Max. příkon X50: **20 kW / 32 A, jistič 40 A** [D]. Hodnota 33,6 kW pro dvě jednotky ze zadání není doložena.

## 5. Bilance a bivalence

- **Bod bivalence:** ≈ −9,6 °C (TČ při 55 °C).
- **Deficit:** při −12 °C 14 kW, při −15 °C 26 kW, při −18 °C 38 kW → max. 7 stupňů EK.
- **Elektřina:** pokrývá < 1 % ročního tepla. Bivalence je pojistka, ne energetický zdroj.
- **Výpadek jedné X50:** X50 + EK pokryjí potřebu do −19,6 °C.
- **Výpadek obou X50:** EK 72 kW pokryjí potřebu do −13,5 °C.
  - **72 kW nepokrývá projektových 88 kW** (resp. 105 kW), pokud by je objekt potřeboval.
  - Pod −13,5 °C při poruše obou TČ: řízené omezení (administrativa přednostně, hala 15 °C).

## 6. Elektro

- Vyhrazený přívod 3 × 160 A.
- Souběh max. (X50 64 A + EK 104 A + pomocné 5 A) = **173 A > 160 A** → dynamické omezení EK podle měření fázových proudů je **povinné**:
  - trvale ≤ 136 A, krátkodobě ≤ 152 A / 60 s,
  - při 150 A odpojení EK (PLC + nezávislé proudové relé),
  - TČ se neodpojují.
- Reálně: −18 °C ≈ 111 A, nouzový režim ≈ 109 A.
- Funkční schéma: `05-elektro-mar-schema.svg`.

## 7. Hydraulika, řízení, stavy

- Hydraulika: `04-hydraulika.md` a `04-hydraulicke-schema.svg`. Obsahuje srovnání paralelního a sériového dohřevu, průtoky, tlakové ztráty, expanzi (200 l voda + 35 l glykol [O]) a armatury.
- Algoritmus PLC: `06-algoritmus-plc.md` (ekviterm, lead / lag TČ, kaskáda 12 × 6 kW s integrálem deficitu, omezovač příkonu, režimy).
- Provozní a poruchové stavy: `07-provozni-stavy.md` (8 scénářů + nezávislé ochrany).

## 8. Úpravy na stávající soustavě (u klienta)

- Ověřit prostor kotelny pro 2 × AKU 1 000 l (klopná výška ≈ 2,3 m). Jinak varianta kontejner.
- Čerpadlo haly DAB A 50/180 XM:
  - při 70/55 °C je potřeba ≈ 4,6 m³/h (dnes 3,8 m³/h),
  - z měřené potřeby vychází nižší teplota a stávající průtok pravděpodobně stačí,
  - ověřit křivku a stupeň čerpadla.
- Přepočet stávající expanze Reflex N 32/3 na celou soustavu včetně AKU (objem soustavy [CHYBÍ]).
- Přívod 3 × 160 A z hlavního rozvaděče objektu: projekt elektro, selektivita [CHYBÍ].

## 9. Odprodej po pronájmu

Alignum zvažuje po ≈ 6 měsících provozu kotelnu odkoupit. Proto:
- **výchozí umístění ve stávající kotelně** (varianta A), rozebíratelné provedení (příruby, samostatná skříň R-K, flexibilní připojení X50),
- kompletní dokumentace skutečného provedení, revize a záznamy z PLC (výroba tepla TČ / EK zvlášť) jako podklad pro předání,
- kontejner (varianta B) jen pokud se technologie do kotelny nevejde, nebo pokud je odkup nejistý.

Orientační rozpočet: A ≈ 1,05 mil. Kč, B ≈ 1,26 mil. Kč bez DPH, viz `08-rozpocet.md`. Nabídka dodavatele CN26OV1321 zatím nezapracována [CHYBÍ].

## 10. Otevřené body

Viz `09-otevrene-body.md`.
