# MM Holz / Alignum Paskov — mobilní kotelna (návrh sestavy)

Poptávka: Ing. Alan Dorňák, Mayr-Melnhof Holz Paskov s.r.o. (16. 10. 2026). Vytápěný objekt je firma **Alignum**
(sousední areál, „Výroba palet Paskov“, k. ú. Paskov, Žabeň). Dnes ho zásobuje teplovod 95 °C / 0,5 MPa
přes výměníkovou stanici HV VS 200 kW. Návrh vychází ze studie `../univerzalni/` (Mobilní kotelna REO HEATING – návrh).
Výpočty jsou v `src/sestavy.py` a podklady klienta v `podklady/` (DSP ÚT, ESL a.s., 01/2005).

## Z podkladů klienta
| Okruh | Projekt | Odvozený výkon |
|---|---|---|
| Výrobní hala 1 182 m², projekt 20 °C, požadavek ≈ 17 °C | 5 × teplovzdušná jednotka SAHARA W3634, **80/60 °C**, čerpadlo DAB A 50/180 XM 3,8 m³/h | ≈ 88 kW (projekt); při 17 °C ≈ 80 kW |
| Administrativa (5 kanceláří, šatny, WC) | desková tělesa Korado Radik VK, **75/60 °C**, ekvitermní směšovač ESBE, DAB VA 35/130 1 m³/h | ≈ 17 kW |
| TUV (12 zaměstnanců × 3 směny) | zásobník ACV Smart Line 320 l, větev 3,15 m³/h | přednostní ohřev |

- Výpočtová venkovní teplota podle projektu je **−12 °C**.
- Výkony jsou odvozené z průtoků čerpadel. Jsou to projektové hodnoty z roku 2005, skutečná potřeba bývá nižší.
- Tepelná ztráta objektu není známa.

## Varianty ze skladu a elektrický příkon
Sklad: několik RH050, 2 × RH060, 2 × RH X50. Výkony v kW při max. otáčkách podle výkonových map výrobce, výpočtová teplota −12 °C.

**Strop daný otopnými tělesy.** Stávající tělesa (5 × Sahara pro halu 17 °C, radiátory administrativy) předají:
- při vodě 55/45 °C nejvýše ≈ **68 kW**,
- při 60/50 °C ≈ 79 kW,
- při 70/60 °C ≈ 101 kW.

Zdroj nad 68 kW má proto smysl jen s vyšší teplotou vody, kterou umí jen RH X50.

| | Sestava | Ks | Nominál A7/W35 | −12 °C / W55 | Po výpadku největší jednotky | −15 °C / W55 | Pokryje zátěž 50 / 60 / 70 kW do | Voda 60–70 °C |
|---|---|---|---|---|---|---|---|---|
| **V1** | 2 × RH060 + 4 × RH050 | 6 | 103 | 59,2 | 46,6 | 53,2 | −14 / −11,5 / −9 °C | ne (max. 55 °C) |
| **V2** | 2 × RH060 + 5 × RH050 | 7 | 118 | 67,7 | 55,1 | 60,8 | −16,5 / −13,5 / −11 °C | ne |
| **V3** | 1 × RH X50 + 2 × RH060 + 2 × RH050 | 5 | 123 | 69,4 | 42,2 | 62,8 | −17 / −14 / −11,5 °C | jen X50 (TUV, dezinfekce) |
| **V4** | 2 × RH X50 | 2 | 99 | 54,4 | 27,2 | 49,6 | −13 / −11 / −9 °C | ano, celá kaskáda |
| **V5** | 2 × RH X50 + 2 × RH060 | 4 | 143 | 79,6 | 52,4 | 72,4 | −19 / −16 / −14 °C | jen X50 |

**Elektrický příkon**

| | Max. příkon | Max. proud | Hlavní jistič | Přívod Cu H07RN-F do 25 m | Zásuvka | Skutečný příkon při −12 °C / W55 |
|---|---|---|---|---|---|---|
| **V1** | 37 kW | 60 A | **3 × 63 A** | 5 × 16 mm² | CEE 63 A | ≈ 32 kW |
| **V2** | 42 kW | 68 A | **3 × 80 A** | 5 × 25 mm² | CEE 125 A | ≈ 37 kW |
| **V3** | 47 kW | 76 A | **3 × 80 A** | 5 × 25 mm² | CEE 125 A | ≈ 41 kW |
| **V4** | 42 kW | 68 A | **3 × 80 A** | 5 × 25 mm² | CEE 125 A | ≈ 37 kW |
| **V5** | 57 kW | 92 A | **3 × 100 A** | 5 × 35 mm² | CEE 125 A | ≈ 50 kW |

Předpoklady výpočtu příkonu:
- RH X50: max. 20 kW / 32 A, jistič 40 A s chráničem (návod výrobce).
- RH060 a RH050: počítáno 7,5 kW / 12 A a 5 kW / 8 A na jednotku. Jde o odhad z max. příkonu ve výkonové mapě (6,8 a 4,5 kW) plus ventilátor a čerpadlo. Návod uvádí jen napájení 380 V / 3f, **max. proud ověřit na typovém štítku**.
- Ke každé variantě je přičteno +2 kW / 3,5 A na čerpadla, PLC a temperování kontejneru.
- Soudobost je 1,0, protože v mrazu běží všechny jednotky.
- **RH050 musí být třífázové**. Jednofázová RH050 by jednu fázi zatížila ≈ 23 A a rozhodila symetrii.
- Každá jednotka má v rozvaděči kontejneru vlastní jistič a chránič: RH050 C16, RH060 C20, RH X50 40 A.

**Rozhodnutí (16. 10. 2026):** klientovi se nabízí **V4 (2 × RH X50)**, V3 je vyloučena. E‑mail: `email-dornak-koncept.md`.

**Hodnocení**
- **V3 – vyloučena.**
  - Výkon 69 kW při −12 °C / W55 přesně odpovídá tomu, co tělesa při 55 °C předají.
  - Jedna RH X50 obslouží TUV a týdenní dezinfekci 65–70 °C.
  - Pět venkovních jednotek, jistič 3 × 80 A.
  - Druhá RH X50 zůstane volná pro další pronájem.
- **V1 / V2 – jen malé jednotky.**
  - Nejnižší jistič (V1 3 × 63 A), jemná modulace od ≈ 6 kW a dobrá záloha.
  - Kaskáda ale dá nejvýše 55 °C. Pro TUV je nutný elektrický dohřev nebo vložka pro dezinfekci (ACV Smart Line – ověřit).
  - 6–7 jednotek znamená nejvíc hadic, nejvíc odtávání a nejvíc místa.
  - Kaskáda RH0x není výrobcem doložena, řízení zajistí PLC.
- **V4 – 2 × RH X50.**
  - Jediná varianta, která dá do sítě 60–70 °C, tedy blízko projektovým 80/60 °C.
  - Při 55 °C má ale nejméně výkonu a po výpadku jedné jednotky zbude jen 27 kW.
- **V5 – rezerva pro případ, že skutečná zátěž vyjde nad 70 kW.**
  - Plný výkon využije jen s vodou 60–65 °C z X50. Pro RH060 nad 55 °C nejsou data.

Rozhodne skutečná spotřeba tepla z měření MM Holz:
- do ≈ 60 kW při −12 °C: V1, nebo V3 s rezervou,
- 60–70 kW: V3 nebo V2,
- nad 70 kW: V5 a provoz haly na 60–65 °C.

## RH X50: do jaké venkovní teploty dá 60 a 70 °C
Platí pro kaskádu 2 × RH X50, nominálně 98,6 kW (A7/W35). Skutečný výkon podle výkonové mapy výrobce:

| Výstupní voda | −20 °C | −15 °C | −12 °C | −10 °C | −7 °C | 0 °C | +7 °C | Nejnižší venkovní teplota pro danou vodu |
|---|---|---|---|---|---|---|---|---|
| **55 °C** | 41,6 | 49,6 | 54,4 | 62,0 | 66,2 | 75,2 | 83,4 | −25 °C (mapa) |
| **60 °C** | 34,0 | 44,4 | 50,8 | 53,2 | 57,0 | 64,8 | 74,4 | **−25 °C** (při −25 °C jen 23,4 kW) |
| 65 °C | — | — | 46,8 | 50,2 | 55,4 | 61,8 | 68,4 | −12 °C |
| **70 °C** | — | — | — | 43,8 | 48,4 | 57,4 | 64,6 | **−10 °C** |
| 75 °C | — | — | — | — | — | 47,6 | 54,0 | −5 °C |

Hodnoty jsou v kW pro celou kaskádu při max. výkonu. Pro zbytek mapy výrobce neudává data, proto pod uvedenou teplotou
nelze danou výstupní teplotu nabízet. COP při 70 °C / −10 °C je 1,25, při 60 °C / −12 °C 1,42.

**Do nabídky:**
- 70 °C na výstupu do venkovní teploty **−10 °C** (≈ 44 kW).
- 60 °C do **−25 °C** (≈ 51 kW při −12 °C, ≈ 44 kW při −15 °C).
- Pod −10 °C kaskáda automaticky přechází na 60–65 °C.

RH050/RH060 70 °C nedají (doporučené maximum je 60 °C a data mají jen do W55), proto pro vysokoteplotní okruh nejsou vhodné.

## Kde je limit: otopná tělesa, ne zdroj
Jednotky Sahara jsou navržené na 80/60 °C. Výkon teplovzdušných jednotek klesá přibližně úměrně rozdílu střední teploty vody
a vzduchu v hale (17 °C). Údaje typu jednotky je ještě potřeba ověřit.

| Voda | Výkon jednotek Sahara | Stačí na projektovou ztrátu haly do |
|---|---|---|
| 55/45 °C | 66 % ≈ 58 kW | −4 °C |
| 60/50 °C | 76 % ≈ 67 kW | −7 °C |
| 65/55 °C | 86 % ≈ 76 kW | −10,5 °C |
| 70/60 °C | ≈ 96 % ≈ 85 kW | celý rozsah |

**Při projektové zátěži** (hala 80 kW při 17 °C + administrativa 17 kW):
- 2 × RH X50 pokryjí vytápění do ≈ −4 °C (W55).
- Pod touto teplotou hala nedosáhne 17 °C.

**Při skutečné zátěži 50–60 kW** (pravděpodobné, projekty bývají předimenzované) 2 × RH X50 pokryjí vytápění do −11 až −13 °C.
Zda sestava stačí, proto rozhodne skutečná spotřeba tepla. MM Holz jako dodavatel tepla ji má změřenou.

**Rozšíření ze skladu, když nebude stačit:** + 2 × RH060 jako nízkoteplotní stupeň (55 °C).
- Kaskáda dá 79,6 kW při −12 °C / W55.
- Odpovídá to zhruba výkonu, který jednotky Sahara při 55–60 °C převezmou.
- Odběr se zvýší na ≈ 57 kW / 87 A.

## Řešení
- **Kontejner 20′** podle studie: glykolový primár, deskový výměník, AKU (1 000 l nebo 2 × 300 l ze skladu na hraně),
  oběhová čerpadla X50, PLC kaskáda, vzdálený dohled. Samostatná TUV jednotka a zásobníky v kontejneru **nejsou potřeba**.
- **Připojení:** na sekundár výměníkové stanice (potrubí DN65 mezi HV VS a rozdělovačem RS Kombi modul 100).
  HV VS se uzavře a stávající rozdělovač i čerpadla větví zůstanou. Připojení na primár (teplovod) je jednodušší,
  ale ztráta ≈ 5 K na výměníku stojí výkon i COP.
- **Regulace:** ekviterm 55 °C → 70 °C (do −10 °C), pod −10 °C 60–65 °C. Při ohřevu TUV 60–65 °C a týdenní dezinfekce 70 °C
  přes stávající větev ACV 320 l.
- **Čerpadlo haly** (DAB A 50/180 XM): při nižším spádu je potřeba vyšší průtok. Ověřit 3. rychlostní stupeň, případně ho vyměnit.
- **Elektro:** podle varianty 3 × 63 A až 3 × 100 A (tabulka výše). Doporučená V3: **3 × 80 A, CEE 125 A, kabel 5 × 25 mm²**.

## Otevřené body (doplnit od klienta)
1. Spotřeba tepla Alignum z měření MM Holz (GJ po měsících za 2–3 roky, ideálně max. hodinový výkon v mrazu).
2. Skutečná teplota teplovodu / sekundáru v mrazech, nastavení ekvitermu.
3. Typový list SAHARA W3634 (výkon při 80/60 a nižších teplotách, počet stupňů ventilátoru).
4. Volný příkon: jistič, vzdálenost rozvaděče, umístění kontejneru (výfuk X50 nahoru ≥ 2 m volno, hluk v areálu).
5. Interně: počet RH050 skladem a zda jde o 3f (BOM RH-RW0500111), typové štítky RH050/RH060 (max. proud).
6. Doba pronájmu (sezóna / trvale) → ekonomika ve fázi 2.
