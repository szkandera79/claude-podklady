# Audit akustické dokumentace — REO R290 RH030 / RH040 / RH050 / RH060

Interní auditní podklad (15. 10. 2026). Cíl: zjistit, jaké akustické údaje máme k řadě RH030–RH060
(výrobce Power World, typy PW030/040/050/060-DKZLRS-E), čím jsou doloženy a co chybí pro akustický
výpočet konkrétní instalace. **Nic z tohoto dokumentu není garance hlučnosti.** Hodnoty jsou přebrány
1 : 1 z dokumentů, nic není dopočteno ani doplněno odhadem.

Pojmy: **LWA** = hladina akustického výkonu (vlastnost zdroje, nezávisí na vzdálenosti) ·
**LpA** = hladina akustického tlaku (závisí na vzdálenosti a prostředí) ·
**L̄p(ST)** = časově průměrovaná hladina akustického tlaku *průměrovaná přes měřicí plochu* ve vzdálenosti d
(veličina měřicí metody EN 12102-1, nikoli tlak v jednom bodě 1 m před jednotkou ve volném prostoru).

---

## 0. Přiřazení typů a prověřené dokumenty

| REO | Typ výrobce | Napájení | Doklad přiřazení |
|---|---|---|---|
| RH030-PW8-A2 | PW030-DKZLRS-E/S | 1F 230 V | štítek `~/Downloads/单相PW030-DKZLRS-ES-Label.pdf` s. 1 (REO HEATING RH030-PW8-A2, LWA 58) |
| RH040-PW12-A2 | PW040-DKZLRS-E/S | 1F 230 V | štítek `~/Downloads/PW040-DKZLRS-ES label.pdf` s. 1 (RH040-PW12-A2, LWA 61) |
| RH050-PW15-A3 | PW050-DKZLRS-E (3F); existuje i PW050-DKZLRS-E/S (1F) | 3F 400 V | štítek `~/Downloads/三相PW050-DKZLRS-E-Label.pdf` s. 1 (RH050-PW15-A3, LWA 59) |
| RH060-PW22-A3 | PW060-DKZLRS-E | 3F 400 V | štítek `~/Downloads/PW060-DKZLRS-E-Label_.pdf` s. 1 (PW060-DKZLRS-E, LWA 62) |

Přiřazení REO ↔ PW je odvozeno ze shody hodnot (štítek, formulář 811/2013, protokol). **Formální doklad
výrobce o totožnosti REO typu s typem PW (OEM/rebrand prohlášení) v podkladech není** — viz kap. 4.

**Prověřené zdroje s akustickými údaji** (kompletní sken PDF/XLSX/DOCX v `~/Claude/REO`, `~/Downloads`,
`~/Claude/PW Obchodní` na klíčová slova dB / noise / sound / hluk / akust / LWA / 12102):

| Zkr. | Dokument | Typ | Akustika |
|---|---|---|---|
| **P1** | TÜV SÜD Technical Report **64.181.23.00497.01 Rev.00**, 9. 5. 2023 — PW030 & PW050-DKZLRS-E/S (1F), 30 s. — `~/Downloads/Power World PW030 & PW050 ERP report Single Phase 64.181.23.00497.01 Rev.00.pdf` | laboratorní protokol | s. 1, 3, 17–20 |
| **P2** | TÜV SÜD Technical Report **64.181.23.00422.02 Rev.00**, 19. 5. 2023 — PW040-DKZLRS-E/S (1F), 19 s. — `~/Downloads/Power World PW040 ERP report Single Phase  64.181.23.00422.02 Rev.00.pdf` | laboratorní protokol | s. 1, 3, 4, 11–12 |
| P2′ | TÜV SÜD 64.181.23.00422.01 Rev.00, 11. 1. 2023 (nahrazen P2) — `~/Downloads/R290 ERP report PW040-DKZLRS-ES.pdf` | protokol (nahrazený) | s. 11–12, EN 12102-1:2017 |
| **P3** | TÜV SÜD Technical Report **64.181.23.00458.01 Rev.00**, 9. 5. 2023 — PW050 + PW060-DKZLRS-E (3F), 30 s. — `~/Claude/REO/PW R290/3 Phase PW050+PW060 ERP Report 64.181.23.00458.01 Rev.00.pdf` (7 identických kopií, stejné MD5) | laboratorní protokol | s. 1, 3, 17–20 |
| K1 | KEYMARK certifikát 041-K032-10, PW060-DKZLRS-E, BRE Global, 30. 6. 2023 – 29. 6. 2033 — `~/Downloads/POWER_WORLD_Keymark_for_PW060-DKZLRS-E.pdf` | certifikát | s. 1: základ EN 12102:2017; **hodnoty neuvádí** (odkaz na databázi KEYMARK) |
| S1–S4 | Energetické štítky 811/2013 (viz tabulka výše) | štítek | s. 1: jedna hodnota LWA venkovní |
| F1 | Formuláře EU 811/2013 v `~/Claude/REO/REO datové listy/RH0x0.xlsx` (listy Avg.35C / Avg.55C, buňka C32) a `RH0x0 35C/55C SCOP.pdf` s. 1 | deklarace (informace o výrobku) | LWA indoors/outdoors |
| F2 | Formulář výrobce `~/Downloads/EU Regulation 811 2013(Avg.33C&55C)(PW040-DKZLRS-E S).xlsx`, C32 | deklarace | 60 / 61 dB — **rozpor s P2** |
| C1 | Ceník Power World, Quotation DGPW-20230221-02S, 21. 2. 2023 — `~/Claude/REO/PW R290/Power World R290 Heat Pump Price List.pdf` | katalog | s. 1 „Noise dB(A)“ |
| C2 | Power World R290 Heat Pump User Manual — `~/Claude/REO/PW R290/Power World R290 Heat Pump User Manual.pdf` | návod | s. 7 (tištěná „5“) „Noise dB(A)“ |
| C3 | Návod REO CZ — `~/Claude/REO/PW R290/RH030-RH060 - REO HEATING/RH030-RH060-navod-CZ_REO-HEATING.pdf` | návod | s. 7 „Hlučnost dB(A)“; s. 25–26 tichý režim |
| C4 | `~/Claude/REO/Nabídky/Katalog REO.pdf` | katalog | s. 5, s. 7 |
| C5 | `~/Claude/REO/Nabídky/Cenová nabídka REO R290.pdf` | obchodní nabídka | s. 1, 2, 8 („46 dB“) |
| C6 | `~/Claude/REO/Nabídky/REO-R290 9_26 .pdf` | obchodní nabídka | s. 3 „Hlučnost dB(A)“ |
| C7 | `~/Claude/REO/R290-datove-listy/pdf/REO-R290-srovnani_REO-HEATING.pdf` (náš srovnávací list) | vlastní odvozený dokument | s. 2 |

**Vyřazeno jako netýkající se R290 řady:** `Keymark_PW040.pdf` (041-K032-02 je typ **PW040-DKZLRS-A**, EVI, R32),
`ERP_report_PW030_and_PW040.pdf` (TÜV 64.181.21.03197.02 — typy **-A, chladivo R32**, LWA 62–67 dB),
`PW030-DKZLRS-e_ttok.pdf` (štítek PW030-DKZLRS-**A**, LWA 53). Tyto hodnoty **nelze** použít pro RH030–RH060.
Technické listy SVT (`RH0x0 technický list SVT.pdf`) a prohlášení o shodě akustické údaje neobsahují.

---

## 1. Výsledky analýzy podle modelů (A–F)

Společné podmínky všech měření v P1–P3 (s. 17–20 resp. 11–12): prostředí **polobezodrazová místnost**
(hemi-anechoic), 14 měřicích pozic, třída přesnosti „Class A“ (dle protokolu), ochrana mikrofonu proti větru „Sponge“,
nastavení regulace „according to user manual“, LWA indoors „--“ (monoblok, jen venkovní). Měření hluku provedla
**CVC Testing Technology Co., Ltd., Guangzhou** (P1–P3 s. 3, odd. 2.2 „For Noise tests“), protokol vydal a schválil
**TÜV SÜD Certification and Testing (China), Guangzhou Branch** (s. 4). Protokoly výslovně uvádějí, že jde
o výsledek **jednorázové zkoušky jednoho vzorku** (s. 1).

### RH030 (PW030-DKZLRS-E/S, 1F) — zdroj P1

| Režim | Venkovní vzduch DB/WB | Voda vstup/výstup | Kompresor | Ventilátor | Průtok | **LWA** | **L̄p(ST)** | d | Str. |
|---|---|---|---|---|---|---|---|---|---|
| nízkoteplotní (35 °C) | 7 / 6 °C | 30 / 35 °C | 48 Hz | 400 ot/min | 0,86 m³/h | **58** | **44** | 1,0 m | P1 s. 17 |
| středněteplotní (55 °C) | 7 / 6 °C | 47 / 55 °C | 52 Hz | 400 ot/min | 0,54 m³/h | **58** | **44** | 1,0 m | P1 s. 18 |

### RH040 (PW040-DKZLRS-E/S, 1F) — zdroj P2 (shodné hodnoty i v nahrazeném P2′)

| Režim | Vzduch | Voda | Kompresor | Ventilátor | Průtok | **LWA** | **L̄p(ST)** | d | Str. |
|---|---|---|---|---|---|---|---|---|---|
| 35 °C | 7 / 6 °C | 30 / 35 °C | 53 Hz | 400 ot/min | 1,20 m³/h | **57** | **43** | 1,0 m | P2 s. 11 |
| 55 °C | 7 / 6 °C | 47 / 55 °C | 58 Hz | 400 ot/min | 0,75 m³/h | **61** | **47** | 1,0 m | P2 s. 12 |

### RH050 (PW050-DKZLRS-E, 3F) — zdroj P3; pro 1F variantu PW050-DKZLRS-E/S zdroj P1

| Varianta / režim | Vzduch | Voda | Kompresor | Ventilátor | Průtok | **LWA** | **L̄p(ST)** | d | Str. |
|---|---|---|---|---|---|---|---|---|---|
| 3F, 35 °C | 7 / 6 °C | 30 / 35 °C | 50 Hz | 400 ot/min | 1,55 m³/h | **59** | **44** | 1,0 m | P3 s. 17 |
| 3F, 55 °C | 7 / 6 °C | 47 / 55 °C | 56 Hz | 400 ot/min | 0,98 m³/h | **59** | **45** | 1,0 m | P3 s. 18 |
| 1F, 35 °C | 7 / 6 °C | 30 / 35 °C | 50 Hz | 400 ot/min | 1,55 m³/h | 60 | 45 | 1,0 m | P1 s. 19 |
| 1F, 55 °C | 7 / 6 °C | 47 / 55 °C | 56 Hz | 400 ot/min | 0,97 m³/h | 60 | 46 | 1,0 m | P1 s. 20 |

### RH060 (PW060-DKZLRS-E, 3F) — zdroj P3

| Režim | Vzduch | Voda | Kompresor | Ventilátor | Průtok | **LWA** | **L̄p(ST)** | d | Str. |
|---|---|---|---|---|---|---|---|---|---|
| 35 °C | 7 / 6 °C | 30 / 35 °C | 48 Hz | 400 ot/min | 2,24 m³/h | **60** | **45** | 1,0 m | P3 s. 19 |
| 55 °C | 7 / 6 °C | 47 / 55 °C | 54 Hz | 400 ot/min | 1,29 m³/h | **62** | **46** | 1,0 m | P3 s. 20 |

### Normy uvedené v dokladech (E) a stav doložení (F)

| Doklad | Norma pro hluk | Doloženo protokolem? |
|---|---|---|
| P1, P2, P3 | **EN 12102-1:2022** (P1/P3 s. 1 „Test specification“; P2 s. 1 a s. 4 — P2 nahrazuje P2′ právě kvůli aktualizaci na EN 12102-1:2022) | **ANO** — akreditovaná třetí strana (TÜV SÜD / CVC) |
| P2′ | EN 12102-1:2017 (s. 1) | ano, ale nahrazený protokol |
| K1 (jen RH060) | EN 12102:2017 jako „testing basis“ (s. 1) | certifikát je; **dílčí datový list KEYMARK s hodnotami nemáme** |
| S1–S4, F1 | žádná norma neuvedena; hodnoty se shodují s P1–P3 | převzaté z protokolu (dohledatelné) |
| C1–C6 | **žádná norma, veličina, vzdálenost ani podmínky** | **NE — pouze katalogové** |

Na str. 2 protokolů P1–P3 je v části „Declared parameters“ uvedeno **„Sound power level dB(A): N/A“** — výrobce
k zkoušce **nedeklaroval** vlastní hodnotu akustického výkonu, nelze tedy porovnat deklaraci s měřením.

### Katalogové údaje bez normy, vzdálenosti a podmínek — ⚠ výslovné upozornění

| Model | C1 ceník s. 1 / C2 návod s. 7 / C3 návod CZ s. 7 „Noise/Hlučnost dB(A)“ | C4 katalog REO s. 7 | C5 nabídka | 
|---|---|---|---|
| RH030 | ≤ 47 | ≤ 47 | „46 dB“ (s. 1, 2, 8 „Tiché jako šepot“) — bez rozlišení modelu |
| RH040 | ≤ 50 | ≤ 50 | dtto |
| RH050 | ≤ 52 (1F i 3F) | ≤ 52 | dtto |
| RH060 | ≤ 53 | ≤ 53 | dtto |

U těchto hodnot **není uvedeno, zda jde o LWA nebo LpA**, v jaké vzdálenosti, při jakém provozním bodě ani podle
jaké normy. Řádově odpovídají spíše akustickému tlaku, ale **jsou o 1–7 dB vyšší než L̄p(ST) z protokolů**, takže
je nelze s protokoly ztotožnit — **neověřeno**. Katalog C4 s. 5 navíc uvádí „méně než 47 dB(A)“ pro celou řadu,
což odporuje vlastní tabulce C4 s. 7 (≤ 50–53). Nabídka C5 „46 dB“ nemá oporu v žádném podkladu výrobce
a **nesmí se používat jako akustický údaj** (doporučení: z nabídky odstranit nebo nahradit „LWA 58–62 dB dle
EN 12102-1, A7/W55“).

### Zjištěné rozpory

1. **RH040, 35 °C:** formulář výrobce F2 uvádí LWA **60** dB, protokol P2 s. 11 i P2′ s. 11 **57** dB; náš RH040.xlsx
   (F1) uvádí 57. Ke štítku se použije 55 °C hodnota 61 (shodná všude). Nutné potvrzení od výrobce.
2. **RH050 1F vs. 3F:** 1F varianta je o 1 dB hlasitější (60/60 vs. 59/59). REO RH050-PW15-A3 = 3F → platí 59.
   Pokud se dodává i 1F provedení, musí mít vlastní údaje (P1 s. 19–20).
3. **C7 (náš srovnávací list) s. 2:** sloupec „Tlak v 1 m“ přebírá L̄p(ST) z protokolů — to je *plošný průměr na
   měřicí ploše*, ne bodová hodnota 1 m ve volném poli. Výpočet odstupu 3–10 m je v listu korektně označen jako
   orientační; vstupem do výpočtu má být vždy **LWA**, ne „tlak v 1 m“.
4. **Prohlášení o shodě** (`REO datové listy/REO R290 Prohlášení o shodě 2.PDF`, 26. 6. 2023) uvádí EN 14511-1 až 4:2005
   a zrušená NV (17/2003, 18/2003…), EN 12102-1 neuvádí — mimo rozsah auditu hluku, ale doporučuji aktualizovat.

---

## 2. Ověření norem a předpisů

### Požadavky na VÝROBCE (výrobek uváděný na trh)

| Předpis | Co požaduje | Stav u RH030–RH060 |
|---|---|---|
| **Nařízení Komise (EU) 813/2013** (ekodesign), příloha II bod 3 | Max. LWA od 26. 9. 2015: jmenovitý výkon ≤ 6 kW: 60 vnitřní / **65 venkovní**; 6–12 kW: 65 / **70**; 12–30 kW: 70 / **78**; 30–70 kW: 80 / 88 dB(A) | Měřené LWA 57–62 dB → s rezervou pod limity (RH030–RH060 spadají do pásma 6–12 nebo 12–30 kW dle Prated). Informace o výrobku musí obsahovat LWA vnitřní/venkovní (formuláře F1 ho mají). |
| **Nařízení (EU) 811/2013** (štítek) | LWA na štítku | S1–S4: 58 / 61 / 59 / 62 dB ✔ |
| **ČSN EN 12102-1:2022** | Metoda stanovení **akustického výkonu** TČ (podmínky provozu, měřicí metody přes ISO 3741/3744/3745/9614) — **neurčuje žádné limity** a neřeší hluk v konkrétním místě | P1–P3 podle 12102-1:2022 ✔ |
| **ČSN EN 14511-1 až 4:2022** | Zkušební podmínky a výkon/COP (A7/W35, A7/W55 …); akustiku sama neřeší, dává jmenovité provozní body, při kterých se dle 12102-1 hluk měří | P1–P3 ✔ (EN 14511-3:2022) |
| EN 14825:2022 | SCOP, částečné zatížení | P1–P3 ✔ |
| Revize ekodesignu (náhrada 813/2013) | Návrh Komise (Ares(2025)10453861, konzultace do 26. 12. 2025) — přísnější požadavky a hlukovou škálu na štítku. **K dnešku nemám potvrzeno přijetí ani konečné limity — neověřeno**, sledovat Úřední věstník EU. | — |

### Požadavky na KONKRÉTNÍ INSTALACI (provozovatel / projektant)

| Předpis | Obsah (ověřeno na zakonyprolidi.cz, znění od 1. 7. 2023) |
|---|---|
| **Zákon 258/2000 Sb.** (§ 30) | Provozovatel zdroje hluku zajistí, aby hluk nepřekračoval hygienické limity; dozor KHS. |
| **NV 272/2011 Sb.**, § 12 odst. 1, 3 + příloha 3 | Chráněný venkovní prostor staveb: základní hladina **50 dB** LAeq,T, korekce noc **−10 dB → 40 dB**; den = 8 souvislých nejhlučnějších hodin (LAeq,8h), **noc = nejhlučnější 1 hodina (LAeq,1h)**. |
| NV 272/2011, § 12 odst. 3 | **Hluk s tónovými složkami: další korekce −5 dB** (tj. noc **35 dB**). Proto je údaj o tónových složkách pro TČ zásadní. |
| NV 272/2011, § 11 | Chráněný vnitřní prostor staveb (hluk pronikající zvenčí, i z TČ na vlastním domě): základ 40 dB + korekce přílohy 2; tónová korekce −5 dB; noc nejhlučnější hodina. |
| Metodická pomůcka MMR (12/2022, ve spolupráci s MZ) | TČ vzduch/voda = výrobek dle zákona 22/1997 Sb.; dodatečná instalace na stávající stavbu je stavební úpravou; **vlastník odpovídá za plnění limitů NV 272/2011**; TČ je stacionární zdroj hluku. Pozn.: pomůcka cituje starý stavební zákon 183/2006 Sb.; promítnutí do zákona 283/2021 Sb. (účinný od 1. 7. 2024) **jsem neověřil**. |
| Nový stavební záměr | Je-li TČ součástí nové stavby / změny stavby v povolovacím řízení, KHS vydává závazné stanovisko; v praxi požaduje hlukovou studii, popř. měření ve zkušebním provozu (podmínky stanoví místně příslušná KHS). |
| Občanský zákoník 89/2012 Sb., § 1013 | Imise hluku nad míru přiměřenou místním poměrům — soukromoprávní riziko i při splnění limitů. |
| Dotace (NZÚ) | Konkrétní akustický požadavek programu NZÚ 2026 na TČ **jsem nedohledal — neověřeno**. |

**Rozlišení:** výrobce prokazuje **LWA** výrobku (813/2013, 811/2013, EN 12102-1). Splnění limitu u souseda
(LAeq v chráněném venkovním / vnitřním prostoru) je **vždy věcí konkrétní instalace** a z katalogového ani
z protokolového LWA ho nelze garantovat — závisí na počtu jednotek (u BD kaskáda 2–4 ks), vzdálenosti, odrazech,
provozním režimu v noční hodině a tónové složce.

---

## 3. Výstupní tabulka

LWA = venkovní jednotka. L̄p(ST) = průměr přes měřicí plochu v d = 1 m, polobezodrazový prostor (EN 12102-1).

| Model | LWA [dB(A)] | LpA [dB(A)] | Vzdálenost | Provozní podmínky | Norma | Zdroj dokumentu (strana) |
|---|---|---|---|---|---|---|
| RH030 | 58 | 44 (L̄p(ST)) | 1,0 m | A7/6, W30→35, komp. 48 Hz, vent. 400 ot/min, 0,86 m³/h | EN 12102-1:2022 | P1 TÜV 64.181.23.00497.01, s. 17 |
| RH030 | 58 | 44 (L̄p(ST)) | 1,0 m | A7/6, W47→55, 52 Hz, 400 ot/min, 0,54 m³/h | EN 12102-1:2022 | P1, s. 18 |
| RH030 | 58 | — | — | neuvedeno (štítek 811/2013) | neuvedena | S1 štítek s. 1; F1 RH030.xlsx C32, RH030 35C SCOP.pdf s. 1 |
| RH030 | — | „≤ 47“ ⚠ neurčená veličina | ⚠ neuvedeno | ⚠ neuvedeno | ⚠ neuvedena | C1 s. 1; C2 s. 7; C3 s. 7; C4 s. 7 |
| RH040 | 57 | 43 (L̄p(ST)) | 1,0 m | A7/6, W30→35, 53 Hz, 400 ot/min, 1,20 m³/h | EN 12102-1:2022 | P2 TÜV 64.181.23.00422.02, s. 11 |
| RH040 | 61 | 47 (L̄p(ST)) | 1,0 m | A7/6, W47→55, 58 Hz, 400 ot/min, 0,75 m³/h | EN 12102-1:2022 | P2, s. 12 |
| RH040 | 61 | — | — | neuvedeno (štítek) | neuvedena | S2 štítek s. 1 |
| RH040 | **60** ⚠ rozpor | — | — | „Avg. 35 °C“ | neuvedena | F2 formulář výrobce, C32 |
| RH040 | — | „≤ 50“ ⚠ | ⚠ | ⚠ | ⚠ | C1 s. 1; C2 s. 7; C3 s. 7; C4 s. 7 |
| RH050 (3F) | 59 | 44 (L̄p(ST)) | 1,0 m | A7/6, W30→35, 50 Hz, 400 ot/min, 1,55 m³/h, 400 V | EN 12102-1:2022 | P3 TÜV 64.181.23.00458.01, s. 17 |
| RH050 (3F) | 59 | 45 (L̄p(ST)) | 1,0 m | A7/6, W47→55, 56 Hz, 400 ot/min, 0,98 m³/h | EN 12102-1:2022 | P3, s. 18 |
| RH050 (1F) | 60 / 60 | 45 / 46 | 1,0 m | jako výše, 230 V | EN 12102-1:2022 | P1, s. 19 / s. 20 |
| RH050 | 59 | — | — | neuvedeno (štítek) | neuvedena | S3 štítek s. 1 |
| RH050 | — | „≤ 52“ ⚠ | ⚠ | ⚠ | ⚠ | C1 s. 1; C2 s. 7; C3 s. 7; C4 s. 7 |
| RH060 | 60 | 45 (L̄p(ST)) | 1,0 m | A7/6, W30→35, 48 Hz, 400 ot/min, 2,24 m³/h | EN 12102-1:2022 | P3, s. 19 |
| RH060 | 62 | 46 (L̄p(ST)) | 1,0 m | A7/6, W47→55, 54 Hz, 400 ot/min, 1,29 m³/h | EN 12102-1:2022 | P3, s. 20 |
| RH060 | 62 | — | — | neuvedeno (štítek) | neuvedena | S4 štítek s. 1; F1 RH060.pdf s. 1 |
| RH060 | (v DB KEYMARK) | — | — | — | EN 12102:2017 | K1 certifikát 041-K032-10, s. 1 — hodnoty nemáme |
| RH060 | — | „≤ 53“ ⚠ | ⚠ | ⚠ | ⚠ | C1 s. 1; C2 s. 7; C3 s. 7; C4 s. 7 |
| celá řada | — | „46 dB“ / „< 47 dB(A)“ ⚠ | ⚠ | ⚠ | ⚠ | C5 s. 1, 2, 8; C4 s. 5 — **bez opory, nepoužívat** |

---

## 4. Chybějící podklady

| Podklad | RH030 | RH040 | RH050 | RH060 |
|---|---|---|---|---|
| Oficiální protokol měření LWA | ✔ P1 | ✔ P2 | ✔ P3 (3F), P1 (1F) | ✔ P3 |
| Měření podle EN 12102-1 | ✔ :2022 | ✔ :2022 | ✔ :2022 | ✔ :2022 |
| Datový list KEYMARK s LWA | ✘ (certifikát pro R290 -E nenalezen) | ✘ (nalezen jen R32 -A) | ✘ | ✘ certifikát ano, datový list ne |
| Akustika při **maximálním výkonu** (max. otáčky kompresoru a ventilátoru) | ✘ | ✘ | ✘ | ✘ |
| Akustika při **nízkých venkovních teplotách** (A2, A−7, A−10, A−15) | ✘ | ✘ | ✘ | ✘ |
| **Noční / tichý režim** („Silent“, „Tichý čas“ — C3 s. 25–26) — LWA a omezení výkonu | ✘ | ✘ | ✘ | ✘ |
| Režim „Powerful“ (výkonný) | ✘ | ✘ | ✘ | ✘ |
| **Oktávové / třetinooktávové spektrum** LWA | ✘ | ✘ | ✘ | ✘ |
| **Tónové složky** (pro korekci −5 dB dle NV 272/2011) | ✘ | ✘ | ✘ | ✘ |
| Směrovost (výfuk vs. sání vs. boky) | ✘ | ✘ | ✘ | ✘ |
| Hluk při odtávání (defrost), náběh kompresoru, LAmax | ✘ | ✘ | ✘ | ✘ |
| Vztah provozního bodu měření k max. frekvenci kompresoru (% výkonu) | ✘ | ✘ | ✘ | ✘ |
| Nejistota měření (dB) | ✘ | ✘ (jen zmínka o „decision rule“, P2 s. 3) | ✘ | ✘ |
| Vibrace / doporučené silentbloky (přenos do konstrukce) | jen obecně (C3 s. 14) | dtto | dtto | dtto |
| Prohlášení výrobce o totožnosti REO RHxxx = PW0x0-DKZLRS-E | ✘ | ✘ | ✘ | ✘ |

Poznámka k provoznímu bodu: protokoly uvádějí kompresor 48–58 Hz a ventilátor 400 ot/min při průtocích vody
nižších než jmenovité oběhové průtoky z ceníku C1 s. 1 (např. RH060 2,24 m³/h vs. 3,79 m³/h). To naznačuje
**částečné zatížení**, nikoli maximální výkon — maximální frekvenci kompresoru však žádný dokument neuvádí,
proto je tento závěr **neověřený**.

---

## 5. Závěrečné hodnocení

### Společné pro všechny čtyři modely

- **A) Dostatečnost pro akustický výpočet:** **Částečně.** Pro *orientační* výpočet šíření hluku při jmenovitém bodě
  A7/W55 (nejhlasitější doložený stav) ano — máme LWA z akreditované laboratoře podle EN 12102-1:2022.
  Pro **průkazné posouzení noční doby** (limit 40 dB, resp. 35 dB s tónovou korekcí, nejhlučnější hodina)
  **ne**: chybí LWA při nízkých teplotách / max. výkonu (to je typicky noční zimní provoz), spektrum
  a tónové složky. Akustik bude muset pracovat s přirážkou nebo požadovat data.
- **B) Pouze katalogové:** všechny hodnoty „≤ 47 / 50 / 52 / 53 dB(A)“ (C1–C4), „46 dB“ a „méně než 47 dB(A)“ (C4, C5),
  údaj 60 dB v F2 (RH040). Bez veličiny, vzdálenosti, podmínek a normy → **neověřené**.
- **C) Doložené měřením:** pouze LWA a L̄p(ST) při A7/6 °C a W35 + W55 v tabulkách kap. 1 (P1–P3).
  Hodnoty na štítcích S1–S4 a ve formulářích F1 jsou s protokoly shodné, tedy jimi podložené.
- **D) Vyžádat od Power World:**
  1. Datové listy **KEYMARK** (záznam v databázi) pro PW030/040/050/060-DKZLRS-E včetně LWA; potvrzení,
     zda certifikace -E řady (R290) existuje i pro 030/040/050.
  2. Protokol(y) **LWA dle EN 12102-1 při maximálních otáčkách** kompresoru a ventilátoru a **při A2, A−7, A−10/−15 °C**
     (W35 i W55), resp. tabulku LWA v závislosti na frekvenci kompresoru / otáčkách ventilátoru.
  3. LWA v režimu **Silent / tichý čas** a v režimu **Powerful**, včetně omezení výkonu a max. otáček v tichém režimu.
  4. **Oktávové (63 Hz–8 kHz), ideálně třetinooktávové spektrum** LWA pro výše uvedené body.
  5. Vyjádření k **tónovým složkám** (kompresor, ventilátor, invertor) — měření dle ISO 1996-2 nebo alespoň 1/3-okt. spektrum.
  6. Maximální frekvenci kompresoru a max. otáčky ventilátoru; poměr výkonu v měřeném bodě k max. výkonu.
  7. Vysvětlení rozporu RH040 35 °C (57 vs. 60 dB) a deklarovanou hodnotu LWA s tolerancí (v protokolech „N/A“).
  8. Původ a definici katalogových hodnot ≤ 47–53 dB(A) (veličina, vzdálenost, podmínky, norma).
  9. Písemné potvrzení, že RH030-PW8-A2 / RH040-PW12-A2 / RH050-PW15-A3 / RH060-PW22-A3 jsou konstrukčně totožné s testovanými PW typy.
  10. Hluk při odtávání a LAmax, směrovost, nejistotu měření.
- **E) Co potřebuje akustický specialista pro konkrétní instalaci (doplní dodavatel/projektant):**
  počet a typ jednotek a jejich vzájemná poloha (kaskáda), přesné umístění (zem / střecha / fasáda, výška,
  orientace výfuku), odrazivé plochy v okolí (stěny, kouty, zídky), situace s nejbližšími chráněnými venkovními
  prostory staveb a okny obytných místností (vzdálenosti, výšky podlaží), vlastní objekt (okna nad jednotkou),
  provozní režim v noční době (výkon potřebný při výpočtové teplotě, nabíjení TUV v noci, nastavení tichého režimu),
  stávající hlukové pozadí, způsob uložení (silentbloky, základ, kotvení ke konstrukci, pružné připojení potrubí),
  zamýšlená protihluková opatření (clona, kryt), případně požadavky místně příslušné KHS.

### Specifika jednotlivých modelů

| Model | A) Dostatečné pro výpočet | Nejhlasitější doložený stav | Specifické poznámky |
|---|---|---|---|
| **RH030** | orientačně ano; noc ne | LWA 58 (W35 = W55) | Stejná hodnota 35/55 °C při různé frekvenci (48/52 Hz) — ověřit u výrobce. |
| **RH040** | orientačně ano; noc ne | LWA 61 @ W55 | **Rozpor 57 vs. 60 dB (35 °C)** mezi protokolem P2 a formulářem F2. Katalog „≤ 50“ nejvyšší relativní odchylka. |
| **RH050** | orientačně ano; noc ne | LWA 59 (3F) / 60 (1F) | Rozlišovat 1F a 3F provedení — liší se o 1 dB. |
| **RH060** | orientačně ano; noc ne | LWA 62 @ W55 | Jediný s certifikátem KEYMARK R290 (041-K032-10) — vyžádat datový list z databáze. Nejvyšší výkon → v kaskádách BD rozhodující. |

### Doporučení pro naše dokumenty
1. V nabídkách a katalozích REO nahradit „46 dB“, „méně než 47 dB(A)“ a „≤ 47–53 dB(A)“ údajem
   **„Akustický výkon LWA 58 / 61 / 59 / 62 dB(A) (EN 12102-1, A7/W55, protokol TÜV SÜD)“**.
2. Akustický tlak uvádět jen s označením „průměr na měřicí ploše v 1 m dle EN 12102-1“, nikdy jako hodnotu
   „u souseda“ nebo „v 1 m volném poli“.
3. U každé instalace u BD (kaskády) počítat s akustickým posouzením; nikdy nedeklarovat splnění limitu NV 272/2011
   bez výpočtu.

---

## Zdroje k předpisům
- NV 272/2011 Sb., aktuální znění: https://www.zakonyprolidi.cz/cs/2011-272
- Nařízení Komise (EU) 813/2013, příloha II (limity LWA): https://legislation.gov.uk/eur/2013/813/annex/II/division/3/adopted?view=plain ; konsolidované znění https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:02013R0813-20170109
- Návrh revize ekodesignu (Ares(2025)10453861): https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=PI_COM:Ares(2025)10453861 ; konzultace EK 1. 12. 2025: https://energy.ec.europa.eu/news/ecodesign-and-energy-labelling-commission-consults-revised-rules-space-and-water-heaters-2025-12-01_en
- MMR, Metodická pomůcka pro umístění, povolení a užívání TČ vzduch/voda (12/2022): https://hluk.nrl.cz/Content/files/Metodicke-navody/metodicka-pomucka-pro-umistenipovoleni-a-uzivani-tc.pdf
- KHS Středočeského kraje, pokyny pro projektanty RD: https://khsstc.cz/pokyny-pro-stavebniky-zpracovatele-projektove-dokumentace-rd/
- EN 12102-1:2022 (vydána 27. 7. 2022, nahradila EN 12102-1:2017): https://genorma.com/en/standards/en-12102-1-2022

Texty norem ČSN EN 12102-1 a EN 14511 nemáme k dispozici v plném znění — popis jejich obsahu výše je obecný
(rozsah normy), nikoli citace konkrétních článků.
