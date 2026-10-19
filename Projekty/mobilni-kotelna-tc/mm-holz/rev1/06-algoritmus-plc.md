# 06 – Algoritmus nadřazeného řízení PLC (rev1)

- Výchozí hodnoty parametrů jsou návrh [O]. Doladí se při uvádění do provozu podle trendů.
- Všechny parametry jsou nastavitelné z HMI a vzdáleně (úroveň servis).
- Označení čidel a akčních členů odpovídá `04-hydraulicke-schema.svg` a `05-elektro-mar-schema.svg`.

## 1. Vstupní veličiny

- **T_e:** venkovní teplota, filtrovaná, průměr 60 min. Pro ochranné funkce okamžitá hodnota.
- **T_top, T_mid, T_bot:** AKU 1 (AKU 2 kontrolně).
- **T_S1:** výstup AKU. **T_EK:** výstup elektrokotlů. **T_S2:** přívod do soustavy. **T_R:** zpátečka.
- **dT_mid/dt:** gradient T_mid v K/10 min, klouzavý.
- **Stav TČ1/TČ2:** připraven / běží / odtávání / porucha / blokace.
  - Dostupný výkon P_TČ,dost se počítá z mapy výrobce pro T_e a aktuální výstup. Mapa W55/W60/W65 je uložena v PLC jako tabulka.
- **I_L1..3:** fázové proudy z PM. **I_max** = max(I_L1, I_L2, I_L3). **cos φ, P** celkem.
- **Stav EK:** stupně zapnuto/vypnuto, STB, FS, KM-EK0, motohodiny a počty sepnutí po stupních.

## 2. Požadovaná teplota přívodu (ekviterm)

```
T_req = clamp( 38 − 1,4 × T_e + ΔT_korekce , 30 °C , T_max )      T_max = 70 °C (nastavitelné ≤ 70)
```

| T_e | +10 | +5 | 0 | −5 | −10 | −12 | −15 | −18 |
|---|---|---|---|---|---|---|---|---|
| T_req | 30 | 31 | 38 | 45 | 52 | 54,8 | 59 | 63,2 |

- Křivka vychází z naměřené potřeby (02) a přepočtu sahar (03). Rezerva 1,10 je v ní obsažena.
- **ΔT_korekce:**
  - ranní / náběhová korekce +3 K po útlumu, max. 60 min,
  - ruční korekce ±10 K.
- Útlum: provoz je třísměnný, výchozí stav **bez útlumu**. O víkendu hala volitelně 15 °C (ΔT −6 K).
- Nad otopnou hranicí (T_e,60min > 15,5 °C, nastavitelné) vytápění vypnuto. Čerpadla se protáčejí 1× denně 2 min.

## 2a. Ohřev TUV (stávající zásobník ACV 320 l)

- **Požadavek na ohřev TUV:** signál ze stávající regulace TUV (chod čerpadla větve TUV nebo kontakt termostatu zásobníku). Rozhraní **[CHYBÍ]**, ověřit na obhlídce. Náhrada: vlastní čidlo v jímce zásobníku.
- **Během požadavku:** T_req,TUV = max(T_req, 65 °C) a T_AKU,set = 62 °C (TČ do 65 °C), max. 90 min.
  - Zda má TUV přednost před vytápěním, řídí stávající regulace.
- **Dezinfekce:** 1× týdně (neděle 2:00) T_req = 70 °C na 60 min.
  - Teplotu nad možnosti TČ dodá elektrický dohřev.
  - Při dezinfekci se blokace EK nad −5 °C neuplatní.
  - Proudový limit platí.
- **Léto (vytápění vypnuto):** TČ pracují jen pro TUV, AKU nabíjená na 62 °C, jedna TČ (rotace).

## 3. Tepelná čerpadla (priorita)

**Žádaná teplota AKU pro TČ:**

```
T_AKU,set = min( T_req + 2 K , T_TČ,max(T_e) − 3 K )
T_TČ,max = 65 °C pro T_e ≥ −12 °C ; 60 °C pro T_e < −12 °C       (rozsah výkonové mapy [D])
```

- Předání žádané do X50:
  - Modbus, pokud dodá výrobce mapu registrů [CHYBÍ],
  - jinak pevná žádaná teplota 65 °C nastavená v jednotce a PLC jen povoluje chod podle T_AKU,set.
- **Řízené čidlo:** T_mid pro zapínání, T_bot pro vypínání. Nabíjení končí, až je nabitá i spodní část.
- **Lead / lag:** vedoucí jednotka se střídá každých 168 h provozu, nebo při poruše okamžitě.

**Zapnutí vedoucí TČ:**
- T_mid < T_AKU,set − 3 K
- a uplynula min. doba vypnutí 10 min.

**Zapnutí druhé TČ (výkonový deficit TČ):**
- vedoucí běží ≥ 15 min
- a T_mid < T_AKU,set − 5 K
- a dT_mid/dt < +0,3 K/10 min.

**Vypnutí:**
- druhá TČ: T_bot > T_AKU,set − 2 K
- vedoucí TČ: T_bot > T_AKU,set − 1 K
- min. doba chodu 10 min.

**Omezení cyklování:**
- max. 4 starty/h na jednotku [D], v PLC nastaveno 3/h,
- min. chod 10 min, min. stání 10 min,
- odtávání: blokace přepínání lead / lag po dobu odtávání + 5 min.

**Ochrana vstupu TČ:**
- T_bot > T_vstup,max − 2 K → blokace TČ a alarm. T_vstup,max **[CHYBÍ]**, předběžně 60 °C [O].
- Kontrola: T_R > 60 °C trvale 10 min → alarm „vysoká zpátečka“.

**Čerpadlo P2:**
- běží, když běží alespoň jedna TČ, s doběhem 3 min,
- otáčky řídí na Δt (T1 − T_bot) = 5 K, min. 30 %.

## 4. Elektrický dohřev – kaskáda 12 × 6 kW

**Uspořádání:**
- 3 bloky EK1–EK3, každý 4 stupně po 6 kW. Stupně jsou 3fázové, odporové, symetrické.
- Pořadí stupňů je rotační seznam s 12 pozicemi. Rotace jednou za 24 h podle motohodin: nejméně zatížený stupeň jde dopředu.
- Bloky se střídají tak, aby zátěž byla rozložená (1.1, 2.1, 3.1, 1.2 …).

**Uvolnění dohřevu E_EN (všechny podmínky současně):**
1. Režim „bivalentní“ (TČ v provozu), nebo „nouzový“ (obě TČ v poruše či blokaci).
2. V bivalentním režimu:
   - obě dostupné TČ běží ≥ 20 min (běží i druhá),
   - a T_S2 < T_req − 2 K trvale ≥ 15 min,
   - a dT_mid/dt ≤ +0,2 K/10 min (TČ deficit nedohánějí),
   - a T_e,60min < T_biv,povol = −5 °C (nastavitelné).
   - Nad −5 °C se dohřev v bivalentním režimu nepovolí vůbec. Výjimkou je nouzový režim.
3. FS průtok O4 OK, STB OK, KM-EK0 sepnut, P4 běží ≥ 60 s.
4. Proudová rezerva dovolí alespoň 1 stupeň (kap. 5).

**Krátkodobý pokles se ignoruje.** Integrál deficitu `D = ∫ (T_req − 1 K − T_S2)⁺ dt` [K·min]:

- **Přidání stupně:**
  - D ≥ 30 K·min a od posledního přidání uplynulo ≥ 5 min,
  - po přidání se D nuluje.
- **Odebrání stupně:**
  - T_S2 > T_req + 1 K trvale 3 min, nebo T_EK > 80 °C (okamžitě),
  - mezi odebráními ≥ 2 min.
- **Min. doba sepnutí stupně:** 3 min.
- **Min. doba vypnutí stupně:** 5 min.
- **Max. 6 sepnutí za hodinu na stupeň.** Při překročení se stupeň vyřadí z rotace na 60 min.
- **Odtávání TČ:** během odtávání se nové stupně nepřidávají. Pokles T_S2 při odtávání je krátkodobý a pokryje ho AKU.
- **Úplné vypnutí dohřevu:**
  - D = 0 a T_S2 ≥ T_req po dobu 15 min, nebo
  - T_e,60min > T_biv,povol + 2 K (bivalentní režim).
- P4 má doběh 3 min po vypnutí posledního stupně.

**Omezení teploty:**
- T_EK ≤ 80 °C (regulační), STB 85 °C (hardware),
- T_S2 ≤ T_max + 3 K → odebírat stupně.

## 5. Dynamické řízení elektrického příkonu

| Parametr | Hodnota |
|---|---|
| Jmenovitý přívod | 3 × 160 A |
| I_lim,trvale | 136 A (85 %) |
| I_lim,krátce | 152 A po dobu ≤ 60 s |
| I_shed | 150 A |
| Proud stupně EK | 8,7 A (6 kW, 400 V, cos φ 1) |
| Rezerva pro rozběh / odchylky | 10 A (náběh čerpadel, start kompresorů – X50 jsou invertorové, rozběh měkký [O]) |

**Postup:**
- PLC každých 200 ms vyhodnotí I_max.
- Povolený počet stupňů: `N_povol = floor( (I_lim,trvale − 10 A − (I_max − I_EK,aktuální)) / 8,7 A )`
- I_EK,aktuální = sepnuté stupně × 8,7 A (kontrolováno měřením).
- **Prioritní odpojování:**
  1. Stupně EK v opačném pořadí rotace.
  2. TČ se kvůli proudu nevypínají (mají prioritu).
  3. Kdyby po odpojení všech EK přesto I_max > 136 A po 60 s (cizí spotřebiče na přívodu – přívod má být vyhrazený): omezit TČ2 a alarm.
- **I_max ≥ 150 A:** okamžitě odpojit stupně EK po jednom každých 200 ms, dokud I_max < 136 A.
- **Hardware:** proudové relé PR (nastaveno 150 A, zpoždění 2 s) rozpojí KM-EK0. Nezávislé na PLC.
- **Nesymetrie fází > 15 A:** alarm (porucha sekce EK nebo jednofázová zátěž).
- **cos φ < 0,9:** jen alarm. Odporové EK mají cos φ ≈ 1, X50 invertorové ≈ 0,95 [O].

## 6. Režimy

| Režim | Popis |
|---|---|
| **0 Vypnuto / léto** | jen protáčení čerpadel a protimrazová ochrana kotelny |
| **1 Monovalentní TČ** | T_e nad bodem bivalence (≈ −9,6 °C při W55), EK blokovány |
| **2 Bivalentní** | TČ na max. dostupném výkonu + EK podle kap. 4 a 5 |
| **3 Nouzový EK** | obě TČ nedostupné. EK jako samostatný zdroj, otevřít V3 (obtok AKU) pro rychlý náběh, T_req beze změny. Při nedostatku výkonu priority: administrativa → hala (kap. 7, scénář 2) |
| **4 Ruční / servis** | přímé ovládání z HMI s časovým omezením 60 min, bezpečnostní řetězce zůstávají aktivní |

Přechod 1 ↔ 2 je automatický podle podmínek kap. 4. Do režimu 3 se přejde po potvrzené poruše obou TČ (porucha > 5 min nebo blokace). Zpět se vrací automaticky po 30 min stabilního chodu TČ: stupně EK se odebírají po 1 za 5 min.

## 7. Alarmy a hlášení (výběr)

- **A1 – porucha TČ1 / TČ2:** SMS servisu, přepnutí lead / lag.
- **A2 – obě TČ v poruše:** SMS servisu + odpovědné osobě Alignum, režim 3.
- **A3 – porucha čidla:** mimo rozsah nebo skok > 10 K/10 s. Náhradní strategie podle `07-provozni-stavy.md`.
- **A4 – proud:** I_max > 136 A po 60 s nebo zásah PR.
- **A5 – průtok:** FS O4 / porucha P2 / P4 / tlak soustavy < 1,0 bar nebo > 2,7 bar.
- **A6 – přehřátí:** T_top > 80 °C, T_EK > 82 °C, zásah STB.
- **A7 – kotelna:** teplota < 5 °C, dveře rozvaděče, výpadek sítě (UPS).
- **Záznam:** všechny veličiny 1 min po dobu 12 měsíců, výkon a energie TČ / EK zvlášť (podklad pro vyúčtování a odkup).
