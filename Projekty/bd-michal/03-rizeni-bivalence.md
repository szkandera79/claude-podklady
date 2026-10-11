# Nadřazené řízení bivalence — kotelna BD Michal (Ostrava-Michálkovice)

**Dokument:** TV-BDM-03 · **Stupeň:** koncept pro programátora MaR · **Rev.:** 0
**Předmět:** funkční specifikace nadřazeného řízení zdroje tepla — kaskáda 2× TČ, elektrická
bivalence bez pevné bivalentní teploty, priorita TUV, využití přebytků FVE, chování při poruchách,
mapa Modbus, seznam I/O, stavový automat a matice priorit.

> **Charakter podkladu.** Funkční (logická) specifikace, ne projekt MaR a ne razítkovaná
> dokumentace. Adresy registrů jsou strukturní návrh — konkrétní adresy, škálování a bity
> stavových slov převzít z dokumentace dodaných jednotek. Výkony, objemy a nastavení parametrů
> ověřit proti skutečné tepelné ztrátě, odběrovému diagramu TUV a rezervovanému příkonu.

---

## 1. Osazení a vstupní předpoklady

| Prvek | Předpoklad | Poznámka / ověřit |
|---|---|---|
| TČ1, TČ2 | 2× vzduch/voda, á ~50 kW, kaskáda, Modbus TCP | výkon při návrhové −15 °C a topné vodě 45 °C |
| Tepelná ztráta objektu | 53 kW při −15 °C | z PENB č. 530077.2 / DPS |
| Akumulace ÚT (AKU) | 1 000 l, stratifikovaná | viz §1.1 — kritické pro taktování |
| Zásobník TUV | 3 000 l | ~154 kWh/den potřeby TUV (PENB 56,33 MWh/rok) |
| Bivalence ÚT | topné tyče v AKU, návrh 2× 9 kW (3+3+3 kW), z toho 1× SSR modulovaná | volitelně jiná skladba, logika je parametrická |
| Bivalence TUV | topné tyče v TUV, návrh 2× 7,5 kW, z toho 1× SSR modulovaná | nutná i pro legionellu (TČ 65 °C nedosáhne) |
| FVE | 46 kWp, 4× SolaX X3-Hybrid-G4-8.0, baterie 40,8 kWh | výroba ~48 MWh/rok |
| Otopná soustava | podlahové vytápění, max. přívod 35 °C, směšovací ventil | 9 rozdělovačů (3 bloky × 3 podlaží) |
| Řízení | PLC jako nadřazený regulátor, Modbus TCP master | typ PLC upřesní projekt MaR |

### 1.1 Tři konstrukční poznámky, které mají vliv na logiku

**a) Akumulace 1 000 l je na 100 kW zdroje malá.** Tepelná kapacita nádrže je
1,163 kWh/K, tedy při využitelném rozdílu 8 K jen ~9,3 kWh. Jedno TČ na 50 kW ji nabije
za ~11 minut. Logika proto **nesmí stát na spínání „on/off" podle nádrže** — musí primárně
modulovat výkon TČ na teplotu AKU a používat širokou hysterezi a minimální doby běhu.
Doporučení k projednání: zvětšit akumulaci na 1 500–2 000 l, nebo počítat s trvale otevřenou
minimální otopnou plochou (referenční okruh bez zónového ventilu) jako odběrem pro doběh.

**b) Blokování HDO nádrž nepřeklene.** Pokud bude sazba s blokováním (D/C 57d), znamená
blokace 1 h při −15 °C výpadek ~53 kWh, zatímco AKU nese ~9 kWh. Překlenutí zajistí jen
tepelná setrvačnost stavby (podlahovka to zvládne s poklesem vnitřní teploty), nikoli nádrž.
Ověřit sazbu a časy blokování; logika s blokací počítá (signál `DI_HDO`) a před blokací
provede přednabití AKU i TUV.

**c) Elektrická bivalence není aditivní k plnému výkonu TČ.** Při −15 °C má kaskáda
elektrický příkon řádově 40–50 kW; s topnými tyčemi (33 kW v návrhu výše) by špička
přesáhla 80 kW nad rámec domovní spotřeby. **Omezovač příkonu (§9) je proto povinná
součást logiky, ne doplněk.**

Krytí ztráty samotnými topnými tyčemi (režim výpadku obou TČ, návrh 33 kW):

| Venkovní teplota | Potřeba ÚT (lin. model 53 kW / −15 °C) | Krytí 33 kW |
|---|---|---|
| +5 °C | 23 kW | 100 % |
| −2 °C | 33 kW | 100 % (mez plného komfortu) |
| −10 °C | 45 kW | 73 % |
| −15 °C | 53 kW | 62 % |

Pod cca −2 °C je nouzový elektrický provoz jen částečný → v tomto stavu se aktivuje útlum
a přednost TUV/protizámrazu (§8.2).

---

## 2. Regulační veličiny — co se počítá, ne co se spíná

Bivalence se **nespouští podle pevné venkovní teploty**. Rozhoduje **výkonový deficit**
potvrzený v čase. K tomu se počítají čtyři veličiny.

### 2.1 Žádaná teplota akumulace (ekvitermní)

```
T_sp_AKU = max( f_ekv(T_e_filtr), T_min_AKU )        [°C]
f_ekv(T_e) = T_base + k_ekv · (T_int_ref − T_e)
```

- `T_e_filtr` — venkovní teplota, klouzavý průměr 30 min (potlačí sluneční špičky na čidle).
- Default: `T_base = 28 °C`, `k_ekv = 0,32`, `T_int_ref = 20 °C`, `T_min_AKU = 26 °C`,
  limit `T_max_AKU = 45 °C` (podlahovka + ochrana COP).
- Korekce: útlum (`−T_utlum`, default 2 K, časový program), posun z HMI (±3 K),
  posun z modulu FVE (§7), posun v nouzovém režimu (§8.2).

### 2.2 Dostupný výkon zdroje `P_pot`

```
P_pot = Σ (přes běžící a povolené TČ) P_max_i(T_e, T_out_sp) · k_derate_i
```

- `P_max_i(T_e, T_out)` — výkonová křivka jednotky, uložená v PLC jako 2D tabulka
  (interpolace, venkovní teplota × teplota výstupu). Zadá se z podkladů výrobce.
- `k_derate_i` — korekční koeficient (0,7–1,0), učený z **měřeného** výkonu (§3):
  klouzavý poměr měřeného a tabulkového výkonu při 100 % modulaci. Řeší zanesení výparníku,
  stárnutí, chybný podklad. Omezit rychlost změny (max ±0,02/den) a logovat.
- Jednotka v defrostu nebo v poruše se do `P_pot` nezapočítává.

### 2.3 Okamžitý požadovaný výkon `P_load`

Primárně z měření (§3), doplňkově z bilance nádrže:

```
P_load = P_zdroj_měř − C_AKU · dT_AKU_stř/dt
C_AKU  = V_AKU[l] · 1,163 / 1000        [kWh/K]   → pro 1 000 l = 1,163 kWh/K
```

`dT/dt` počítat z klouzavého okna 5 min, výstup filtrovat (PT1, τ = 120 s), jinak je derivace
šumová. Při nedostupném měření průtoku použít zálohu: `P_load = P_pot · modulace_prům`.

### 2.4 Deficit a jeho integrál

```
P_def   = P_load_req − P_pot                              [kW]     (kladné = chybí výkon)
E_def   = ∫ max(0, T_sp_AKU − T_AKU_top) dt               [K·min]  (integrátor odchylky)
```

`E_def` se **nuluje**, jakmile `T_AKU_top ≥ T_sp_AKU − 0,5 K`, a **zmrazí** (nepřičítá se)
během defrostu, během blokace HDO, během přednostního nabíjení TUV a v režimu FVE.
Tím se zabrání spuštění bivalence kvůli jevu, který není nedostatkem výkonu zdroje.

---

## 3. Měření skutečného tepelného výkonu (průtok + ΔT)

**Doporučeno, a ne jen pro diagnostiku — je to vstup regulace.** Bez měřeného výkonu je
`P_load` jen odhad z tabulek a bivalence se rozhoduje podle teplot, tedy pozdě a nepřesně.

```
P [kW] = V̇ [m³/h] · k_med · ΔT [K]
k_med  = ρ · c_p / 3600
       ≈ 1,15   voda 40–50 °C
       ≈ 1,05   30 % etylenglykol (primár, pokud bude nemrznoucí směs)
```

`k_med` udělat parametrem, zvlášť pro primární a sekundární okruh.

### 3.1 Kde měřit

| Měřicí místo | Snímače | Účel |
|---|---|---|
| **M1 — primár (společný)** | průtokoměr F1 + TS10 přívod / TS11 zpátečka | celkový výkon kaskády, `P_zdroj_měř`, `k_derate` |
| **M2 — nabíjení TUV** | průtokoměr F2 + TS12/TS13 | výkon do TUV, energie TUV, oddělení TUV od ÚT v bilanci |
| **M3 — distribuce ÚT** | průtokoměr F3 + TS4 přívod / TS5 zpátečka | odběr objektu, `P_load` pro ÚT, kontrola proti součtu bytových kalorimetrů |
| (volitelně) **M4 — per TČ** | průtok z regulátoru TČ (Modbus) + jeho čidla | výkon a COP jednotlivé jednotky, rotace podle práce, ne jen hodin |

Doporučené provedení M1–M3: **kalorimetr v MID provedení** s Modbus/M-Bus výstupem
(fakturačně použitelné, jedno zařízení místo tří signálů, integrovaná energie kWh).
Ultrazvukový průtokoměr preferovat před lopatkovým (bez pohyblivých částí, měří i malé průtoky).

### 3.2 Co se z měření získá

- **Regulace:** reálný `P_load`, reálný `P_pot` (přes `k_derate`), tedy deficit, který
  odpovídá skutečnosti → bivalence spíná později a méně často.
- **COP/SPF v reálném čase:** `COP_i = P_tep_i / P_el_i` (elektroměr na jednotku, §5.2).
  Denní, měsíční a sezónní SPF včetně a bez bivalence — podklad pro vyhodnocení provozu.
- **Diagnostika:** pokles `k_derate` = zanesený výparník / nedostatek chladiva / špatný defrost;
  nízké ΔT při plném průtoku = přeběh přes obtok, špatně nastavená čerpadla; nulový průtok
  při běhu čerpadla = uzavřená armatura, vzduch, zanesený filtr.
- **Detekce defrostu** i bez příznaku z Modbusu (záporný nebo nulový výkon při běžícím kompresoru).
- **Kontrola bilance:** `M1 ≈ M2 + M3 + ztráty`; trvalá odchylka > 10 % = alarm měření.

### 3.3 Plausibilita

Výkon počítat jen když `V̇ > V̇_min` (default 1 m³/h) a `|ΔT| > 0,3 K`; jinak `P = 0`.
Při `ΔT < 0` po dobu > 60 s mimo defrost → alarm (obrácený průtok / záměna čidel).

---

## 4. Kaskádování a rotace

### 4.1 Základní pravidla

| Parametr | Default | Poznámka |
|---|---|---|
| `t_min_run` | 10 min | minimální doba běhu kompresoru |
| `t_min_stop` | 8 min | minimální doba klidu |
| `n_start_max` | 3 /h | max. startů kompresoru za hodinu |
| `t_stage_up` | 10 min | vedoucí jednotka na ≥ 95 % než se přidá druhá |
| `t_stage_dn` | 10 min | podmínka odstavení druhé jednotky |
| `mod_min` | 30 % | minimální modulace jednotky |

### 4.2 Přidání druhé jednotky (HEAT_1 → HEAT_2)

Všechny podmínky současně:

1. `mod_TČ_lead ≥ 95 %` nepřetržitě `t_stage_up` (10 min), **a**
2. `T_AKU_top < T_sp_AKU − 2 K`, **a**
3. `dT_AKU_top/dt < +0,05 K/min` (nádrž se nedobíjí), **a**
4. `P_def > P_def_stage` (default 8 kW), **a**
5. druhá jednotka je povolená, bez poruchy, po `t_min_stop`, a nemá překročený `n_start_max`.

Zrychlený start (bez čekání na `t_stage_up`): požadavek TUV s prioritou (§6.1),
protizámraz, nebo pokles `T_AKU_top` pod `T_sp − 6 K`.

### 4.3 Odstavení druhé jednotky (HEAT_2 → HEAT_1)

`(P_load < 0,55 · P_max_1(T_e)) ` po dobu `t_stage_dn`, **nebo** `T_AKU_top ≥ T_sp + 2 K`,
**a zároveň** běžela minimálně `t_min_run`. Odstavuje se **následující** jednotka
(ne vedoucí), aby se neztratila rozehřátá kaskáda.

### 4.4 Rotace vedoucí jednotky

- Kritérium: **motohodiny** kompresoru, a pokud je k dispozici měření (§3.1 M4), i **dodaná
  energie**. Rotace při `|h_TČ1 − h_TČ2| > 50 h` nebo periodicky po `168 h` provozu.
- Provede se **jen v okamžiku přechodu do STANDBY** nebo při běhu jediné jednotky bez
  požadavku TUV; nikdy ne přepnutím za běhu.
- Startovací pořadí ukládat do retentivní paměti (přežije výpadek napájení).
- Jednotka s aktivní poruchou nebo v ručním režimu se z rotace vyřazuje a doba se jí nezapočítává.
- Protikorozní / protizatuhávací běh: jednotka bez provozu > 168 h se na 10 min spustí
  (i mimo topnou sezónu), stejně tak čerpadla (týdenní protočení 60 s).

### 4.5 Koordinace odmrazování (defrost)

- Defrosty TČ1 a TČ2 **nesmí běžet současně** — druhé jednotce se odmrazování oddálí
  (blokace přes Modbus, případně dočasným zvýšením žádané teploty výparníku, dle možností
  jednotky). Pokud jednotka defrost vyžádá tvrdě, PLC to akceptuje a pouze zablokuje druhou.
- Po dobu defrostu: `E_def` zmrazit, druhá jednotka smí jít na 100 %, bivalence **se nespouští**
  (defrost je krátkodobý jev, ne deficit), čerpadlo primáru běží.
- Počet defrostů/24 h je sledovaná diagnostická veličina (> 12/den = alarm nízké priority).

---

## 5. Bivalence pro vytápění — podmínky spuštění a útlumu

### 5.1 Povolení (HEAT_2 → HEAT_BIV)

Bivalence se povolí **jen** při splnění všech podmínek:

| # | Podmínka | Default |
|---|---|---|
| B1 | obě dostupné jednotky běží na `≥ 95 %` nepřetržitě | `t_full = 15 min` |
| B2 | `T_AKU_top < T_sp_AKU − ΔT_biv` nepřetržitě | `ΔT_biv = 4 K`, `t_dev = 10 min` |
| B3 | `dT_AKU_top/dt ≤ +0,05 K/min` (soustava se nezotavuje) | — |
| B4 | `E_def ≥ E_biv` | `E_biv = 60 K·min` |
| B5 | žádná blokáda: HDO, servisní režim, omezovač příkonu bez rezervy, aktivní defrost | — |

Zkratky (přeskočení B1/B4) platí jen pro: **protizámraz**, **poruchu TČ (§8)**,
**legionellu (§6.3)** a **ruční vynucení z HMI**.

### 5.2 Regulace výkonu bivalence

- Řídicí veličina: `P_biv_req = clamp( P_def_filtr , 0 , P_biv_max )`, kde `P_biv_max`
  dává **omezovač příkonu (§9)**, ne jmenovitý výkon tyčí.
- Realizace: nejprve **modulovaná tyč (SSR / 0–10 V)** do 100 %, teprve pak stupňové tyče
  po `t_step = 3 min`. Stupně nikdy nespínat současně (proudový ráz, blikání).
- Regulátor: PI na odchylku `T_sp_AKU − T_AKU_top`, `Kp = 4 kW/K`, `Ti = 600 s`,
  antiwindup na `P_biv_max`.

### 5.3 Odstavení

- Odstavovat po jednom stupni s odstupem `t_step_off = 3 min` při
  `T_AKU_top ≥ T_sp_AKU − 1 K` po dobu 5 min, **nebo** při `P_def ≤ 0` po dobu 10 min.
- Po vypnutí posledního stupně **blokace opětovného zapnutí `t_biv_lock = 20 min`**
  (kromě zkratek dle §5.1). Zabrání kmitání bivalence.
- Denní počítadlo energie bivalence: `E_biv_den`. Překročení `E_biv_den_max`
  (default 30 kWh/den mimo poruchový režim) = alarm nízké priority „nadměrná bivalence" —
  signalizuje poddimenzovaný zdroj, chybnou křivku nebo poruchu TČ bez hlášení.

---

## 6. TUV — priorita, bivalence, legionella

### 6.1 Normální nabíjení TUV z TČ

- Čidla: `TS7` (horní, měřicí komfort) a `TS8` (dolní, měřicí nabití).
- Start nabíjení: `TS7 < T_TUV_on` (default 45 °C) **nebo** `TS8 < T_TUV_on − 8 K`.
- Konec: `TS8 ≥ T_TUV_sp` (default 52 °C) nebo vypršení `t_dhw_max`.
- Priorita TUV: přepne kaskádu na okruh TUV (přepínací ventil / nabíjecí čerpadlo),
  žádaná teplota výstupu TČ = `T_TUV_sp + 5 K`, ale max. dle limitu jednotky.
- **Ochrana vytápění:** priorita TUV smí trvat max. `t_dhw_max = 60 min`; poté
  povinný návrat do ÚT minimálně na `t_heat_min = 20 min`, ledaže `TS7 < T_TUV_crit` (40 °C).
  Při venkovní teplotě < −8 °C zkrátit `t_dhw_max` na 35 min.
- 3 000 l pokryje ~154 kWh denní potřeby; nabíjení 50 kW z 45 na 52 °C trvá ~35 min.
  Nabíjení preferenčně plánovat mimo ranní špičku ÚT a do okna přebytku FVE (§7).

### 6.2 Bivalence TUV

Topné tyče v zásobníku se povolí, pokud nastane kterákoli podmínka:

| # | Spouštěč | Chování |
|---|---|---|
| D1 | `TS7 < T_TUV_crit` (40 °C) a TČ nabíjí déle než 20 min bez vzestupu ≥ 1 K | dohřev horní zóny, výkon dle omezovače |
| D2 | doba nabíjení > `t_dhw_max` a `TS8 < T_TUV_sp − 5 K` | dohřev, souběžně s TČ |
| D3 | rychlý odběr: `dTS7/dt < −0,8 K/min` po 5 min | dohřev horní zóny (špička) |
| D4 | TČ nedostupné (§8.1, §8.2) | tyče jsou jediný zdroj TUV |
| D5 | legionella (§6.3) | řízeno programem |
| D6 | přebytek FVE (§7) | řízeno modulem FVE, nezvyšuje `E_def` |

Termostatický směšovací ventil na výstupu (ochrana proti opaření, 45–50 °C) je hardwarová
ochrana, na logice nezávislá — v regulaci se s ním nepočítá jako s regulačním prvkem.

### 6.3 Legionella

- Program 1× týdně (default neděle 13:00, tedy do okna FVE), cíl `T_leg = 65 °C` na `TS8`,
  výdrž `t_leg_hold = 60 min`.
- Postup: TČ předehřeje na svoje maximum (typicky 52–55 °C), zbytek dotopí **tyče**.
  TČ se při dosažení svého limitu z okruhu odstaví (nesmí jít do vysokotlaké ochrany).
- Během programu je vytápění potlačeno (kromě protizámrazu); pokud `T_e < −8 °C`,
  program se odloží o 24 h (max. 2 odklady, pak proběhne bez ohledu na počasí).
- Neúspěšné dokončení do 4 h = alarm střední priority (hygienický požadavek).
- Cirkulace TUV: během programu běží trvale, aby se prohřála i cirkulační větev
  (jinak je dezinfekce zásobníku bez efektu na rozvod). Mimo program řízena časovým
  programem + `TS9` (zpátečka cirkulace, udržovat ≥ 50 °C).

---

## 7. Režim přebytku FVE — samostatný algoritmus

Modul běží **paralelně** k hlavnímu automatu. Nezasahuje do jeho stavů, pouze:
(a) posouvá žádané teploty, (b) uvolňuje samostatnou větev řízení topných tyčí,
(c) nikdy nezvyšuje `E_def` (jeho energie se nepočítá jako bivalence).

### 7.1 Pořadí využití přebytku — nejdřív TČ, potom tyče

Toto je zásadní a bývá to udělané špatně. Topná tyč dělá z 1 kWh elektřiny 1 kWh tepla,
tepelné čerpadlo 3–4 kWh. Přebytek se proto **prioritně** ukládá zvýšením žádaných teplot
pro TČ, a teprve zbytek, který TČ nedokáže spotřebovat, jde do tyčí.

| Priorita | Akce | Cílová hodnota |
|---|---|---|
| 1 | nabít baterii FVE | `SOC ≥ SOC_min` (default 80 %) — řídí měnič, PLC jen čte |
| 2 | TUV přes TČ | `T_TUV_sp_pv = 55 °C` (místo 52) |
| 3 | AKU přes TČ | `T_sp_AKU_pv = T_sp_AKU + 5 K`, max. 45 °C |
| 4 | TUV přes tyč (SSR modulace) | do `T_TUV_pv_max = 60 °C` (částečně plní i dezinfekci) |
| 5 | AKU přes tyč (SSR modulace) | do `T_AKU_pv_max = 45 °C` |

### 7.2 Podmínky a regulace

```
Aktivace:   P_export ≥ P_pv_on (2 kW) po t_pv_on (60 s)  AND  SOC ≥ SOC_min
Deaktivace: P_export < P_pv_off (0,3 kW) po t_pv_off (120 s)
            OR SOC < SOC_min − 10 %
            OR cíl dosažen  OR  P_pv < 3 kW (večer)  OR  aktivní alarm / omezovač příkonu
Modulace:   PI regulátor udržuje P_export ≈ P_reserve (default 0,2 kW)
            výstup 0–100 % na SSR, Kp = 8 %/kW, Ti = 30 s
```

- `P_export` číst **na předávacím místě** (fakturační elektroměr nebo měnič — hodnota
  „feed-in"), ne na střídači; jinak modul „přetahuje" domovní spotřebu.
- Hystereze a zpoždění jsou nutné — bez nich SSR kmitá s oblačností.
- V zimě je přebytek malý; modul má hlavní přínos v přechodných obdobích a v létě
  (TUV zdarma). Roční přínos vyhodnocovat z odděleného počítadla `E_pv_do_tepla`.
- **Kolize s bivalencí:** je-li aktivní HEAT_BIV (skutečný deficit), modul FVE se potlačí —
  tyče řídí bivalenční regulátor a přebytek se do nich propíše automaticky tím,
  že odběr sníží export.

---

## 8. Poruchové režimy

### 8.1 Porucha jedné jednotky (FAULT_1TC)

- Detekce: chybový bit v Modbus stavovém slově, **nebo** ztráta komunikace > 60 s,
  **nebo** jednotka povolena a `P_tep_i ≈ 0` déle než 15 min mimo defrost.
- Chování: zdravá jednotka převezme provoz jako vedoucí, `P_pot` se sníží na polovinu →
  **kritéria bivalence se plní dřív, žádná změna logiky není potřeba** (to je hlavní přednost
  deficitního řízení oproti pevné bivalentní teplotě).
- Zmírnění podmínek: `t_full` zkrátit na 8 min, `E_biv` na 30 K·min.
- Rotace se pozastaví, poškozená jednotka se z `P_pot` a z rotace vyřadí.
- Autoreset: max. 3 pokusy / 24 h s odstupem 30 min; poté trvalá blokace do ručního potvrzení.
- Alarm střední priority, notifikace servisu, provoz pokračuje bez zásahu uživatele.

### 8.2 Porucha obou jednotek (FAULT_2TC — nouzový elektrický provoz)

- Bivalence běží **jako jediný zdroj**, bez podmínek B1–B4 (jen omezovač příkonu).
- Úsporná opatření (kvůli ceně i příkonu):
  - `T_sp_AKU` snížit o `2 K`, `T_max_AKU` omezit na 38 °C,
  - `T_TUV_sp` snížit na 45 °C, legionella odložena,
  - cirkulace TUV přepnuta na intervalový provoz (10 min/h),
  - časový útlum prohlouben o 1 K.
- Priorita: **protizámraz > TUV na 45 °C > vytápění**; pod cca −2 °C nelze držet plný komfort
  (viz §1.1) — HMI to musí uživateli zobrazit jako informaci, ne jako poruchu vytápění.
- Alarm vysoké priority, okamžitá notifikace.

### 8.3 Ostatní poruchy

| Porucha | Detekce | Reakce |
|---|---|---|
| Čidlo mimo rozsah / zkrat | `< −45 °C` nebo `> 130 °C` u Pt1000 | náhradní hodnota (poslední platná 15 min, pak konstanta), degradovaný režim, alarm |
| Výpadek `TS_venkovní` | jako výše | `T_e` fixně `−5 °C` (bezpečná strana), pevná žádaná AKU 35 °C |
| Ztráta průtoku | hlídač průtoku / `V̇ < V̇_min` při běžícím čerpadle 60 s | odstavit zdroj do okruhu, alarm vysoké priority |
| Pokles tlaku | `PS1/PS2 < p_min` | zablokovat zdroj i čerpadla, alarm vysoké priority |
| Havarijní termostat tyče | DI (bezpečnostní obvod, HW) | HW odpojení stykače tyčí; PLC jen hlásí, nesmí obcházet |
| Zaplavení jímky | DI plovák | odstavit čerpadla a tyče, alarm vysoké priority |
| Ztráta komunikace Modbus (jednotka) | timeout 3× 5 s | přechod na **nouzové HW řízení**: beznapěťový kontakt „povolení" + interní regulátor jednotky s pevnou žádanou teplotou; alarm |
| Ztráta komunikace (elektroměr / FVE) | timeout 30 s | modul FVE se vypne, omezovač příkonu přejde na konzervativní pevný limit |
| Nesoulad bilance měření | `\|M1 − (M2+M3)\| > 10 %` po 24 h | alarm nízké priority (diagnostika) |

---

## 9. Omezovač příkonu (hlídač hlavního jističe)

Trvale aktivní modul, nadřazený všem ostatním:

```
P_total = P_import (fakturační elektroměr, 15min klouzavé maximum + okamžitá hodnota)
P_biv_max = clamp( P_limit − P_total_bez_tyčí − P_rezerva , 0 , P_tyče_inst )
```

- `P_limit` — dle rezervovaného příkonu / hlavního jističe (**doplnit ze skutečnosti**),
  `P_rezerva` default 5 kW pro domovní spotřebu.
- Pořadí omezování při hrozícím překročení: **1)** stupňové tyče (okamžitě, po jedné),
  **2)** modulovaná tyč na 0, **3)** omezení výkonu TČ přes Modbus (`power limit` registr),
  **4)** teprve pak odstavení jedné jednotky kaskády.
- Sledovat i **čtvrthodinové maximum** (pokud je součástí sazby) — omezovač musí umět
  „srazit" tyče, aby maximum neposkočilo.

---

## 10. Stavový automat

Architektura: **jeden sekvenční automat zdroje** + tři **paralelní moduly**
(FVE, omezovač příkonu, bezpečnost/diagnostika), které zapisují do žádaných hodnot a limitů.
Vytápění, TUV a FVE se nemodelují jako výlučné stavy jednoho automatu — to vede
k nekonečné matici přechodů.

### 10.1 Stavy

| ID | Stav | Popis | Zdroje |
|---|---|---|---|
| S0 | `OFF_SERVICE` | vypnuto / servisní režim (ruční ovládání z HMI) | dle ručního zadání |
| S1 | `STANDBY` | bez požadavku, čerpadla stojí, protizámraz hlídá | — |
| S2 | `HEAT_1` | vytápění, vedoucí TČ moduluje | 1× TČ |
| S3 | `HEAT_2` | vytápění, kaskáda | 2× TČ |
| S4 | `HEAT_BIV` | kaskáda + topné tyče AKU | 2× TČ + tyče |
| S5 | `DHW` | priorita TUV, kaskáda nabíjí zásobník | 1–2× TČ |
| S6 | `DHW_BIV` | nabíjení TUV + tyče v zásobníku | TČ + tyče |
| S7 | `LEGIONELLA` | týdenní dezinfekce, cirkulace trvale | TČ + tyče |
| S8 | `DEFROST_HOLD` | jedna jednotka v defrostu, druhá kryje | 1× TČ (+ AKU) |
| S9 | `FAULT_1TC` | provoz s jednou jednotkou, snížené prahy bivalence | 1× TČ (+ tyče) |
| S10 | `FAULT_2TC` | nouzový elektrický provoz, útlum | tyče |
| S11 | `FROST_PROTECT` | protizámraz (`T_AKU < 8 °C` nebo `T_zpátečka < 8 °C`) | cokoli dostupné |
| S12 | `SHUTDOWN_SAFE` | bezpečné odstavení (tlak, průtok, zaplavení, hav. termostat) | žádné |

### 10.2 Přechody (výběr rozhodujících)

| Z | Do | Podmínka |
|---|---|---|
| S1 | S2 | `T_AKU_top < T_sp_AKU − 2 K` a uplynul `t_min_stop` |
| S2 | S3 | podmínky §4.2 (1–5) |
| S3 | S2 | podmínky §4.3 |
| S3 | S4 | podmínky B1–B5 §5.1 |
| S4 | S3 | poslední stupeň tyčí vypnut (§5.3) → `t_biv_lock` |
| S2/S3 | S5 | požadavek TUV (§6.1) a priorita TUV povolena |
| S5 | S6 | některá z podmínek D1–D3 §6.2 |
| S5 | S2/S3 | `TS8 ≥ T_TUV_sp` nebo `t_dhw_max` vypršel |
| ∗ | S7 | časový program legionelly (mimo S10, S12) |
| S2/S3/S4 | S8 | příznak defrost z kterékoli jednotky |
| S8 | zpět | konec defrostu + `t_defrost_settle = 3 min` |
| ∗ | S9 | porucha 1 jednotky (§8.1) |
| S9 | S10 | porucha i druhé jednotky |
| S9 | předchozí | porucha kvitována a jednotka hlásí OK po dobu 5 min |
| ∗ | S11 | `T_AKU_bot < 8 °C` nebo `T_ÚT_zpátečka < 8 °C` |
| ∗ | S12 | kterákoli havarijní podmínka §8.3 (vysoká priorita) |
| S12 | S1 | příčina odstraněna **a** ruční kvitace z HMI |

Pravidla: **S12 přebíjí vše**, pak S11, pak S10/S9, pak S7, pak S5/S6, pak S2–S4.
Každý přechod respektuje `t_min_run` / `t_min_stop` kompresorů, kromě S11 a S12.

### 10.3 Matice priorit požadavků

| Priorita | Požadavek | Přebíjí | Omezení |
|---|---|---|---|
| 1 | Bezpečnost (hav. termostat, zaplavení, tlak, průtok) | vše | HW obvod nezávislý na PLC |
| 2 | Protizámraz | vše kromě 1 | pouští i tyče bez podmínek B1–B4 |
| 3 | Omezovač příkonu | 4–9 (limituje je) | nikdy nesnižuje pod protizámraz |
| 4 | TUV pod kritickou mezí (`TS7 < 40 °C`) | vytápění | max. `t_dhw_max` |
| 5 | Legionella (v okně programu) | vytápění, komfort TUV | odklad při `T_e < −8 °C` |
| 6 | Vytápění dle ekvitermy | 7–9 | `T_max_AKU` |
| 7 | Komfortní dohřev TUV (na `T_TUV_sp`) | 8–9 | ustupuje 6 při deficitu |
| 8 | FVE přebytek → TUV | 9 | jen `SOC ≥ SOC_min` |
| 9 | FVE přebytek → AKU | — | jen `SOC ≥ SOC_min`, `T ≤ 45 °C` |

---

## 11. Seznam čidel a I/O

### 11.1 Analogové vstupy (AI)

| Ozn. | Veličina | Typ | Umístění |
|---|---|---|---|
| TS1 | AKU horní | Pt1000 | jímka horní třetina |
| TS2 | AKU střed | Pt1000 | jímka střed (pro `dT/dt` a bilanci) |
| TS3 | AKU dolní | Pt1000 | jímka spodní třetina |
| TS4 | ÚT přívod za směšováním | Pt1000 | příložné/jímka |
| TS5 | ÚT zpátečka | Pt1000 | jímka |
| TS6 | Venkovní teplota | Pt1000 | severní fasáda, mimo přímé slunce a odvod vzduchu TČ |
| TS7 | TUV horní | Pt1000 | zásobník, komfortní zóna |
| TS8 | TUV dolní | Pt1000 | zásobník, nabíjecí zóna |
| TS9 | Cirkulace TUV — zpátečka | Pt1000 | před napojením do zásobníku |
| TS10 | Primár přívod (do AKU) | Pt1000 | pár k F1 |
| TS11 | Primár zpátečka | Pt1000 | pár k F1 |
| TS12 | TUV nabíjení — přívod | Pt1000 | pár k F2 |
| TS13 | TUV nabíjení — zpátečka | Pt1000 | pár k F2 |
| PS1 | Tlak primár | 4–20 mA, 0–6 bar | — |
| PS2 | Tlak ÚT | 4–20 mA, 0–6 bar | — |
| F1 | Průtok primár | Modbus/M-Bus (kalorimetr) nebo 4–20 mA | §3.1 |
| F2 | Průtok nabíjení TUV | Modbus/M-Bus nebo 4–20 mA | §3.1 |
| F3 | Průtok distribuce ÚT | Modbus/M-Bus nebo 4–20 mA | §3.1 |

**AI celkem: 13× Pt1000 + 2× tlak (+ 0–3 průtoky, pokud ne po sběrnici) → 15–18, rezerva 20 %.**

### 11.2 Digitální vstupy (DI)

| Ozn. | Signál |
|---|---|
| DI1 | HDO / signál blokování dodavatele |
| DI2 | Havarijní termostat topných tyčí AKU (bezpečnostní obvod) |
| DI3 | Havarijní termostat topných tyčí TUV |
| DI4 | Hlídač průtoku primár |
| DI5 | Zaplavení technické místnosti (plovák jímky) |
| DI6 | Souhrnná porucha rozvaděče (jističe, chrániče, přepěťová ochrana) |
| DI7 | Zpětná vazba stykače tyčí AKU |
| DI8 | Zpětná vazba stykače tyčí TUV |
| DI9 | Porucha čerpadla primár 1 |
| DI10 | Porucha čerpadla primár 2 |
| DI11 | Porucha čerpadla ÚT |
| DI12 | Porucha čerpadla nabíjení TUV |
| DI13 | Nouzové zastavení kotelny (STOP tlačítko) |
| DI14 | Souhrnná porucha FVE (beznapěťový kontakt střídače) |

**DI celkem: 14, rezerva 20 %.**

### 11.3 Digitální výstupy (DO)

| Ozn. | Akční člen |
|---|---|
| DO1, DO2 | Povolení TČ1 / TČ2 (beznapěťově, záloha při výpadku Modbusu) |
| DO3–DO5 | Stupně topné tyče AKU (3 kW / 3 kW / 3 kW) |
| DO6 | Stykač modulované tyče AKU (bezpečnostní odpojení SSR) |
| DO7, DO8 | Stupně topné tyče TUV |
| DO9 | Stykač modulované tyče TUV |
| DO10 | Čerpadlo primár 1 |
| DO11 | Čerpadlo primár 2 |
| DO12 | Čerpadlo ÚT |
| DO13 | Čerpadlo nabíjení TUV |
| DO14 | Čerpadlo cirkulace TUV |
| DO15 | Přepínací ventil ÚT/TUV (pokud v provedení s ventilem) |
| DO16 | Souhrnná porucha (relé, vstup do EPS/dohledu) |

**DO celkem: 16, rezerva 20 %.**

### 11.4 Analogové výstupy (AO)

| Ozn. | Akční člen |
|---|---|
| AO1 | SSR modulované tyče AKU, 0–10 V |
| AO2 | SSR modulované tyče TUV, 0–10 V |
| AO3 | Směšovací ventil ÚT, 0–10 V (nebo 3bodově přes 2 DO) |
| AO4 | Čerpadlo ÚT — řízení otáček, 0–10 V |

**AO celkem: 4, rezerva 20 %.**

### 11.5 Poznámky k instalaci čidel

- `TS6` musí být mimo proud vzduchu z výparníků TČ, jinak ekviterma reaguje na vlastní zdroj.
- Čidla pro měření výkonu (`TS10/11`, `TS12/13`) volit **párovaná** (tolerance třídy A),
  jinak je chyba ΔT při 3 K rozdílu větší než měřená veličina.
- Všechna teplotní čidla do jímek s teplovodivou pastou; příložná jen kde jinak nelze,
  a pak s izolací přes čidlo.
- Vedení Pt1000 stíněné, 3vodičové, odděleně od silových tras.

---

## 12. Modbus — co číst, co zapisovat

Adresy níže jsou **strukturní návrh**; skutečné adresy, škálování a význam bitů převzít
z dokumentace dodaných zařízení. Doporučená perioda čtení: 2 s (jednotky, měniče),
5 s (elektroměry), 10 s (kalorimetry). Timeout 5 s, 3 pokusy, pak porucha komunikace.

### 12.1 Přehled zařízení na sběrnici

| Unit ID | Zařízení | Protokol |
|---|---|---|
| 1, 2 | TČ1, TČ2 — regulátor jednotky | Modbus TCP |
| 10 | Elektroměr — celkový odběr objektu (předávací místo) | Modbus TCP / RTU→GW |
| 11, 12 | Elektroměr TČ1, TČ2 | Modbus RTU → gateway |
| 13 | Elektroměr topné tyče (AKU + TUV zvlášť, nebo 2 přístroje) | Modbus RTU → gateway |
| 20 | FVE — SolaX X3-Hybrid (master střídač / datalogger) | Modbus TCP |
| 30–32 | Kalorimetry M1, M2, M3 | Modbus / M-Bus → gateway |
| 40 | Rozvaděč tyčí / regulátor SSR (pokud inteligentní) | Modbus RTU |
| 50 | PLC jako **server** pro HMI a cloud | Modbus TCP |

### 12.2 Tepelné čerpadlo — čtení (FC 03/04)

| Ofset | Veličina | Typ | Jedn. |
|---|---|---|---|
| +0 | Stavové slovo (bity: běh, kompresor, defrost, TUV režim, blokace) | UINT16 | bitové |
| +1 | Chybový kód | UINT16 | — |
| +2 | Teplota výstupu (kondenzátor) | INT16 | 0,1 °C |
| +3 | Teplota vstupu (zpátečka) | INT16 | 0,1 °C |
| +4 | Venkovní teplota (čidlo jednotky) | INT16 | 0,1 °C |
| +5 | Teplota výparníku | INT16 | 0,1 °C |
| +6 | Modulace kompresoru | UINT16 | % |
| +7 | Průtok jednotkou | UINT16 | 0,1 m³/h |
| +8 | Okamžitý tepelný výkon (pokud jednotka poskytuje) | UINT16 | 0,1 kW |
| +9 | Elektrický příkon | UINT16 | 0,1 kW |
| +10 | COP (pokud poskytuje) | UINT16 | 0,01 |
| +11–12 | Motohodiny kompresoru | UINT32 | h |
| +13–14 | Počet startů kompresoru | UINT32 | — |
| +15 | Počet defrostů za 24 h | UINT16 | — |
| +16 | Tlak sání / výtlaku | UINT16 | 0,1 bar |

**Hodnoty z jednotky nepovažovat za měření.** Vlastní výkon a COP (§3) se počítají z M1 a
z elektroměrů; údaje jednotky slouží k porovnání a diagnostice.

### 12.3 Tepelné čerpadlo — zápis (FC 06/16)

| Ofset | Veličina | Typ | Poznámka |
|---|---|---|---|
| +100 | Povolení / zákaz provozu | UINT16 | 0/1, doplněk k HW kontaktu |
| +101 | Žádaná teplota výstupu | INT16 | 0,1 °C |
| +102 | Režim (topení / TUV / pohotovost) | UINT16 | — |
| +103 | Omezení elektrického příkonu | UINT16 | % nebo 0,1 kW — vstup omezovače §9 |
| +104 | Blokace defrostu (dočasná) | UINT16 | koordinace §4.5 |
| +105 | Tichý režim (noční) | UINT16 | akustika k sousedům |
| +106 | Watchdog / heartbeat z PLC | UINT16 | inkrement 1 s; jednotka při výpadku → bezpečný stav |

### 12.4 Elektroměry (ID 10–13)

Činný výkon [W], činná energie [Wh, UINT32], proud po fázích, napětí po fázích,
u předávacího místa navíc **odběr a dodávka odděleně** (`P_import`, `P_export`) a
čtvrthodinové maximum. `P_export` z ID 10 je vstupem modulu FVE (§7).

### 12.5 FVE — SolaX X3-Hybrid (ID 20)

| Veličina | Použití |
|---|---|
| Okamžitý výkon FV pole [W] | informace, predikce konce okna |
| Výkon do/z baterie [W] (znaménkově) | rozlišení nabíjení / vybíjení |
| SOC baterie [%] | podmínka `SOC ≥ SOC_min` §7 |
| Výkon do/ze sítě [W] | kontrolní hodnota k ID 10 |
| Denní / celková výroba [Wh] | reporting |
| Stavové a chybové slovo | alarm, blokace modulu FVE |

Při 4 střídačích číst **agregát z masteru / dataloggeru**; pokud agregace není spolehlivá,
sčítat jednotlivě a jako referenci pro regulaci použít vždy elektroměr ID 10.

### 12.6 Kalorimetry M1–M3 (ID 30–32)

Okamžitý výkon [kW], průtok [m³/h], přívod/zpátečka [°C], kumulovaná energie [kWh],
objem [m³], chybové slovo. Kumulovaná energie je základ měsíčních reportů a výpočtu SPF.

### 12.7 PLC jako Modbus server (ID 50) — pro HMI a cloud

Zde adresy definujeme my (holding registry, ofsety od 0):

| Reg. | Veličina | Typ | Jedn. |
|---|---|---|---|
| 0 | Aktuální stav automatu (S0–S12) | UINT16 | enum |
| 1 | Substav / důvod (kód) | UINT16 | enum |
| 2 | `T_sp_AKU` (žádaná) | INT16 | 0,1 °C |
| 3–7 | TS1, TS2, TS3, TS4, TS6 | INT16 | 0,1 °C |
| 8–10 | TS7, TS8, TS9 | INT16 | 0,1 °C |
| 11 | `P_load` (měřený) | INT16 | 0,1 kW |
| 12 | `P_pot` (dostupný) | INT16 | 0,1 kW |
| 13 | `P_def` (deficit) | INT16 | 0,1 kW |
| 14 | `E_def` (integrátor) | UINT16 | K·min |
| 15 | `P_biv_akt` / `P_biv_max` | 2× UINT16 | 0,1 kW |
| 17 | Vedoucí jednotka (1/2) | UINT16 | — |
| 18, 19 | `k_derate` TČ1, TČ2 | UINT16 | 0,001 |
| 20 | Režim FVE aktivní + stupeň | UINT16 | bitové |
| 21 | `P_export` | INT16 | 0,1 kW |
| 22 | SOC baterie | UINT16 | % |
| 23–26 | COP TČ1, COP TČ2, COP okamžité, SPF (den) | UINT16 | 0,01 |
| 27–30 | Denní energie: TČ teplo / TČ elektřina / bivalence / FVE do tepla | UINT32 | 0,1 kWh |
| 31 | Alarmové slovo 1 (vysoká priorita) | UINT16 | bitové |
| 32 | Alarmové slovo 2 (střední / nízká) | UINT16 | bitové |
| 100+ | Zapisovatelné parametry (§13) — chráněné heslem na HMI | různé | — |

---

## 13. Parametry (nastavitelné, s výchozími hodnotami)

| Parametr | Default | Rozsah | Význam |
|---|---|---|---|
| `T_base`, `k_ekv` | 28 °C, 0,32 | — | ekvitermní křivka AKU |
| `T_min_AKU`, `T_max_AKU` | 26 / 45 °C | 20–50 | meze žádané AKU |
| `t_min_run`, `t_min_stop` | 10 / 8 min | 5–20 | ochrana kompresoru |
| `n_start_max` | 3 /h | 2–6 | max. startů |
| `t_stage_up`, `t_stage_dn` | 10 / 10 min | 5–30 | kaskádování |
| `P_def_stage` | 8 kW | 3–20 | práh pro 2. jednotku |
| `t_full` | 15 min | 5–60 | podmínka B1 |
| `ΔT_biv`, `t_dev` | 4 K / 10 min | 2–8 / 5–30 | podmínka B2 |
| `E_biv` | 60 K·min | 20–200 | podmínka B4 |
| `t_biv_lock` | 20 min | 5–60 | blokace po vypnutí bivalence |
| `t_step`, `t_step_off` | 3 / 3 min | 1–10 | odstup stupňů tyčí |
| `T_TUV_on`, `T_TUV_sp`, `T_TUV_crit` | 45 / 52 / 40 °C | — | TUV |
| `t_dhw_max`, `t_heat_min` | 60 / 20 min | 20–120 / 10–60 | ochrana vytápění |
| `T_leg`, `t_leg_hold` | 65 °C / 60 min | 60–70 | legionella |
| `SOC_min` | 80 % | 50–95 | práh pro režim FVE |
| `P_pv_on`, `P_pv_off` | 2 / 0,3 kW | — | hystereze FVE |
| `T_TUV_pv_max`, `T_AKU_pv_max` | 60 / 45 °C | — | cíle režimu FVE |
| `P_limit`, `P_rezerva` | **doplnit** / 5 kW | — | omezovač příkonu |
| `Δh_rotace`, `t_rotace` | 50 / 168 h | — | rotace vedoucí jednotky |
| `k_med_prim`, `k_med_sek` | 1,05 / 1,15 | 1,00–1,20 | konstanta výpočtu výkonu |

---

## 14. Alarmy

| Priorita | Alarm | Reakce systému |
|---|---|---|
| Vysoká | Havarijní termostat, zaplavení, pokles tlaku, ztráta průtoku | `SHUTDOWN_SAFE`, okamžitá notifikace, ruční kvitace |
| Vysoká | Porucha obou TČ | `FAULT_2TC`, notifikace |
| Vysoká | Protizámraz aktivní > 30 min | notifikace |
| Střední | Porucha jednoho TČ | `FAULT_1TC`, notifikace servisu |
| Střední | Ztráta komunikace Modbus (TČ, elektroměr předávacího místa) | nouzové HW řízení / konzervativní limit |
| Střední | Legionella nedokončena do 4 h | opakovat další den, hlásit |
| Střední | TUV pod `T_TUV_crit` déle než 60 min | — |
| Nízká | Bivalence > `E_biv_den_max` za den | diagnostika |
| Nízká | `k_derate < 0,8` | podezření na zanesení / chladivo |
| Nízká | Defrostů > 12/24 h | diagnostika |
| Nízká | Nesoulad bilance měření > 10 % | kontrola měření |
| Nízká | Čidlo mimo rozsah (jednotlivé) | náhradní hodnota |

Každý alarm: časové razítko vzniku, kvitace a zániku; archiv min. 12 měsíců.

---

## 15. Archivace a vyhodnocení

Trendy vzorkovat 1 min (teploty, výkony, modulace, stavy), archivovat 1 rok lokálně a
do cloudu. Denní agregace: dodané teplo ÚT/TUV, spotřeba TČ, spotřeba bivalence, spotřeba
z FVE, COP/SPF, motohodiny a starty jednotlivých jednotek, počet defrostů, čas ve stavech.

**Kontrolní ukazatele prvního roku provozu** (podklad pro seřízení, ne garance):
podíl energie z bivalence na celkovém teple (cíl pod 5 % mimo poruchové stavy),
SPF soustavy, počet startů kompresoru za den (cíl pod 10), podíl vlastní spotřeby FVE.

---

## 16. Co je potřeba doplnit ze skutečnosti

1. **Rezervovaný příkon / hlavní jistič** a sazba (včetně časů blokování HDO) → `P_limit`, §9, §1.1b.
2. **Typ a výkonové křivky TČ** při −15 až +15 °C a výstupu 30–50 °C → tabulka pro `P_pot`.
3. **Modbus dokumentace jednotek** (mapa registrů, bity stavového slova) → §12.2, §12.3.
4. **Skladba topných tyčí** (počet, výkony, stupně vs. modulace) → §5.2, §11.3.
5. **Potvrzení objemů** AKU 1 000 l a TUV 3 000 l vůči taktování a odběrovému diagramu → §1.1a.
6. **Odběrový diagram TUV** (27 b.j.) pro nastavení `t_dhw_max` a cílových teplot.
7. **Typ PLC a HMI**, rozsah I/O karet dle §11 + rezerva.
8. Rozhodnutí, zda primár poběží s nemrznoucí směsí → `k_med_prim`.
