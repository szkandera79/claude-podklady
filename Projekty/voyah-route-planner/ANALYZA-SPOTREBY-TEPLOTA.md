# Technická analýza: výpočet spotřeby, teplota a kalibrace

**Aplikace:** Voyah Smart Route Planner (PWA, Voyah Free 2023), stav k 1. 11. 2026.

**Jen diagnostika.** Kód ani nastavení se neměnily.

**Značení zdroje u každého závěru:**
- **[KÓD]** — ověřeno přímo ve zdrojovém kódu (soubor a řádek jsou uvedené).
- **[PŘEDPOKLAD]** — úsudek nebo odhad, který kód sám nedokládá.

Cesty jsou relativní k `frontend/src/`. Python verze v `backend/vrp/` slouží jen jako referenční a aplikace v telefonu ji nepoužívá. **[KÓD]** `core/models.ts:2`

---

## 1. Současný výpočet spotřeby

### 1.1 Vzorec

Trasa se rozdělí na úseky dlouhé zhruba 1 km. Každý úsek má typ silnice, rychlostní limit, převýšení, teplotu, protivítr a povrch. **[KÓD]** `data/routing.ts`

Energie jednoho úseku se počítá takto. **[KÓD]** `core/energy.ts:43–57`

```
E_úsek = [ c(v + protivítr) · d/100 · f_povrch  +  E_převýšení  +  P_HVAC(T) · t ]  ×  f_baterie(T)  ×  k_kalibrace(skupina, pásmo T)
```

**Spotřeba jízdou** (kWh/100 km), soubor `core/energy.ts:26–31`: **[KÓD]**
```
c(v) = a + b · v·|v|      (+ cityExtra, je-li úsek městský)
a = 9,43   b = 0,000997   cityExtra = 1,5
```
- Za v se dosazuje rychlost vůči vzduchu, tedy plánovaná rychlost plus protivítr.
- Koeficienty jsou proložené dvěma body: 17,5 kWh/100 km při 90 km/h a 25 kWh/100 km při 125 km/h, obojí v létě. **[KÓD]** komentář v `core/models.ts:129`
- Že tyto dva body odpovídají skutečnému Voyah Free, kód nedokládá. **[PŘEDPOKLAD]**

**Převýšení** (`core/energy.ts:50–52`): **[KÓD]**
- Do kopce: m·g·Δh / 0,9.
- Z kopce se vrací rekuperace s účinností 0,6.
- Hmotnost je 2 400 kg plus náklad z Nastavení.

**Přívěs** (`core/energy.ts:48`, `local/service.ts:103`): **[KÓD]**
- Přičítá se +10 kWh/100 km na dálnici a rychlostní silnici, +5 kWh/100 km jinde.
- Rychlost je omezená na 115 km/h.

### 1.2 Typy silnic a plánovaná rychlost

| Typ silnice (`RoadClass`) | Výchozí limit | Plánovaná rychlost (profil „standard“) |
|---|---|---|
| `dalnice` | 130 (PL 140) | 0,95 × limit = **123,5 km/h** |
| `rychlostni` | 110 | 104,5 km/h |
| `prvni_trida` | 90 | 85,5 km/h |
| `okresni` | 90 | 85,5 km/h |
| `mesto` | 50 | 0,7 × limit = **35 km/h** (+1,5 kWh/100 km) |

Zdroje a doplňky k tabulce:
- **[KÓD]** `data/routing.ts:15–16`, `core/energy.ts:10–24`
- Typ silnice se odvozuje z dat routeru: třída „motorway“, označení D/A/S/M, případně průměrná rychlost ≥ 95 / ≥ 70 / ≥ 45 km/h. **[KÓD]** `data/routing.ts:102`
- Limit na jiné než dálnici se stropuje na 1,1 × rychlost podle routeru. **[KÓD]** `data/routing.ts:25`
- **Profily:**
  - „eko“ = limit, nejvýš 110 na dálnici a 80 jinde.
  - „rychlý“ = plný limit.
  - Varianta plánu „Eko“ používá profil eko. **[KÓD]**

**Odpověď na otázku, zda aplikace rozlišuje typ silnice a rychlost:**
- **Ano.** Pět typů silnic, rychlost se dynamicky odvozuje z limitu a profilu jízdy a dosazuje se do kvadratické křivky. Jde tedy o dynamický výpočet z koeficientů, ne o pevnou hodnotu pro každý typ silnice. **[KÓD]**
- Rychlost „120 km/h na dálnici“ se dnes nedá zadat přímo. Profil „standard“ počítá na české dálnici se 123,5 km/h, „eko“ se 110 km/h. **[KÓD]**

### 1.3 Současné hodnoty pro 50 / 90 / 120 km/h

Vypočteno z výchozích koeficientů. Bez kalibrace, větru, převýšení a se suchou vozovkou.

| | 50 km/h, město (35 km/h¹) | 90 km/h | 120 km/h |
|---|---|---|---|
| **+20 °C** | 13,4 (12,2¹) | **17,5** | **23,8** |
| **0 °C** | 19,2 (19,8¹) | **21,6** | **27,8** |
| **−10 °C** | 23,0 (24,8¹) | **24,3** | **30,5** |

Hodnoty jsou v kWh/100 km.

¹ Město se v plánu počítá s limitem 50 × 0,7 = 35 km/h, takže skutečně použitá hodnota je ta v závorce. **[KÓD]**

---

## 2. Počasí a venkovní teplota

### 2.1 Odkud se teplota bere

- **Zdroj:** Open-Meteo, **hodinová předpověď** na 7 dní, vzorky po trase po 25 km. **[KÓD]** `data/weather.ts:6–22`
- **Načítané veličiny:** teplota ve 2 m, rychlost a směr větru, srážky, sněžení. **[KÓD]**
- **Hodina průjezdu:** odhaduje se z času odjezdu a z rychlosti 0,9 × limit, ne z plánované rychlosti modelu. **[KÓD]** `data/weather.ts:33, 43`
- **Čas odjezdu nelze zadat.** Žádost o plán (`PlanRequest`) pole pro odjezd nemá, takže se počítá vždy s odjezdem „teď“. U cesty plánované na zítřek se tak použije teplota pro dnešní hodiny. **[KÓD]** `types.ts:15–24`, `local/service.ts:256`
- **Výpadek počasí:** aplikace počítá s +20 °C bez větru a přidá upozornění do poznámek plánu. **[KÓD]** `data/weather.ts:24`, `core/models.ts:57`

### 2.2 Jak teplota vstupuje do výpočtu

Teplota se do výpočtu **opravdu promítá**, a to třemi cestami. **[KÓD]**

**1. Vytápění a klimatizace kabiny** (`core/energy.ts:33–37`):
```
T < 15 °C:   P_HVAC = 0,3 + 0,12 · (15 − T)   [kW]     (−10 °C → 3,3 kW; 0 °C → 2,1 kW)
T > 25 °C:   P_HVAC = 0,5 kW
jinak 0
```
- Násobí se dobou jízdy úsekem, proto je vliv v kWh/100 km tím větší, čím pomaleji auto jede. Ve městě je největší. **[KÓD]**

**2. Ztráty studené baterie** (`core/energy.ts:39`):
```
f_baterie = 1 + 0,006 · max(0, 15 − T)        (−10 °C → ×1,15; 0 °C → ×1,09)
```
- Násobí celou energii úseku, tedy jízdu, převýšení i vytápění. **[KÓD]**

**3. Pásmo kalibrace:** teplota určuje, který kalibrační faktor se použije (viz kap. 5). **[KÓD]**

**Další vlivy počasí:**
- **Vítr:** protivítr = rychlost větru × 0,6 × cos(úhel vůči směru jízdy). Přičítá se k rychlosti v členu b·v². **[KÓD]** `data/weather.ts:9–10`
- **Povrch:** sníh ×1,15, mokro ×1,05 (při srážkách ≥ 0,2 mm/h). Násobí jen spotřebu jízdou. **[KÓD]** `core/models.ts:150`, `data/weather.ts:11`

### 2.3 Co model nezohledňuje

- **Teplota baterie:** jako teplota baterie se bere teplota vzduchu. Neřeší se předehřev, zahřátí baterie po delší jízdě ani nabíjení. **[KÓD]**
  - Na dlouhé zimní dálnici proto model spotřebu nejspíš nadhodnocuje, protože se baterie zahřeje. **[PŘEDPOKLAD]**
- **Vliv mrazu na rychlost nabíjení:** funkce na to existuje (`batteryTempFactor`, 0,6× při −10 °C), ale parametr `batteryTempC` je vždy `null`, takže se nepoužije. Doba nabíjení v mrazu se tedy nepřepočítává. **[KÓD]** `core/charging.ts:11`, `core/models.ts:177`
- **Tepelné čerpadlo, vyhřívání sedadel, rozmrazování, odtávání po nočním parkování:** model je nerozlišuje. Jsou schované v lineární křivce HVAC. **[KÓD]**
  - Zda má Voyah Free 2023 tepelné čerpadlo, z kódu nelze zjistit. **[PŘEDPOKLAD]**
- **Hustota vzduchu** (studený vzduch má vyšší odpor) a **zimní pneumatiky:** model je nemá. **[KÓD]**
- **Zimní koeficienty:** samostatné „zimní koeficienty“ nejsou. Zimní složky jsou jen výše uvedené vzorce HVAC a f_baterie. Nastavení je označuje jako „předpoklady ke kalibraci“. **[KÓD]** `components/SettingsScreen.tsx:223`
  - Hodnoty 0,12 kW/°C, 0,3 kW a 0,006/°C nemají v kódu uvedený zdroj měření. **[PŘEDPOKLAD]**

---

## 3. Navrhované teplotní režimy a současné kalibrační pásmo

Kalibrace už dnes dělí teplotu do pěti pásem. **[KÓD]** `core/calibration.ts:7`

| Pásmo | Rozsah | Navržený režim |
|---|---|---|
| 0 | T < −5 °C | **Arktický** |
| 1 | −5 ≤ T < 5 °C | **Zimní** |
| 2 | 5 ≤ T < 15 °C | (přechodné) |
| 3 | 15 ≤ T < 25 °C | **Letní** |
| 4 | T ≥ 25 °C | (horko) |

Tři požadované režimy tedy **přesně odpovídají** existujícím pásmům 0, 1 a 3. To je hlavní předpoklad pro bezpečné rozšíření.

---

## 4. Automatický a ruční režim: proveditelnost

**Proveditelné bez zásahu do algoritmu plánování.** Teplota vstupuje do výpočtu jedinou proměnnou, `seg.tempC`. **[KÓD]** Z ní se odvozuje HVAC, f_baterie i pásmo kalibrace.

**Bezpečný princip proti dvojímu započtení:**
- Ruční režim **nebude přidávat další násobitel**. Jen **nahradí teplotu**, kterou model použije, reprezentativní hodnotou režimu.
  - Navrhuji: Letní +20 °C, Zimní 0 °C, Arktický −10 °C.
- Všechny tři teplotní vlivy se pak přepočítají konzistentně a kalibrace použije pásmo odpovídající režimu.
- Vítr a povrch (sníh nebo mokro) zůstanou z předpovědi. Nejsou to teplotní vlivy, takže se nic nezapočítá dvakrát.

**Kde přepis provést (návrh):**
- Ruční teplotu je lepší předat jako parametr modelu (např. `EnergyParams.tempOverrideC`) a v `segmentEnergy` použít `override ?? seg.tempC`. Nepřepisovat přímo `seg.tempC` v uložené trase.
- Uložená trasa si tak ponechá skutečnou předpověď. Ta je potřeba pro kalibraci (kap. 5.3) a pro případné zobrazení teplot.

**Další body návrhu:**
- **Výběr v UI:** volba se přidá do žádosti o plán vedle zaškrtávátka „přívěs“ (Auto / Léto / Zima / Arktický). Uloží se do plánu, takže ji převezme i přepočet během jízdy.
- **Rychlost výpočtu:** beze změny. Jedno porovnání na úsek. **[KÓD]** (náročnost `routeProfile` je lineární podle počtu úseků)

---

## 5. Kalibrace podle skutečné spotřeby

### 5.1 Jak funguje dnes

**[KÓD]** `core/calibration.ts`, `local/service.ts:338–360, 416–427`

1. **Spuštění:** během cesty uživatel zadává SoC a na konci zadá SoC v cíli. Při nabití (nárůst o více než 2 %) se uzavře jeden kalibrační úsek.
2. **Pozorování** se vytvoří, pokud úsek měří alespoň 20 km a SoC klesl. Ukládá:
   - km podle typu silnice,
   - **průměrnou teplotu** úseku z předpovědi,
   - predikovanou energii **základního modelu bez kalibrace**,
   - SoC na začátku a na konci,
   - čas.
3. **Poměr:** naměřeno = ΔSoC × 100 kWh. Poměr = naměřeno / predikce.
   - Pozorování s odchylkou větší než ±40 % se uloží, ale nezapočte.
   - Jízdy s přívěsem se nezapočítávají vůbec.
4. **Buňky:** jsou tři skupiny silnic (dálnice = dálnice + rychlostní; silnice = I. třída + okresní; město) × pět teplotních pásem = **15 buněk**. Každá buňka nese faktor k a váhu n.
5. **Aktualizace buňky:**
   ```
   k_nový = (n · k_starý + w · poměr) / (n + w),   w = naměřeno/10 kWh × podíl km té skupiny
   ```
   - Počáteční váha je 2, takže první jízdy kalibraci posunou jen částečně.
   - Celé pozorování spadne do **jednoho** pásma podle průměrné teploty. Jeden poměr se rozdělí do skupin silnic podle podílu km.
6. **Použití:** faktor buňky násobí celou energii úseku (`k_kalibrace` ve vzorci). Prázdná buňka má faktor 1. Kalibrace současně snižuje nejistotu modelu (výchozí ±8 %, minimum ±3 %), kterou používá „konzervativní“ plán.
7. **Krátkodobá korekce `k_trip`** (rozmezí 0,7–1,6):
   - Při zadání SoC během jízdy se plán na zbytek cesty přepočítá podle aktuální odchylky.
   - Dlouhodobou kalibraci nemění. **[KÓD]** `core/trip.ts`
8. **Uložení:** IndexedDB, klíč `calibration`. Obsahuje až 500 posledních pozorování. Je v záloze dat (Nastavení → export) a dá se smazat tlačítkem.

### 5.2 Odpovědi na otázky

- **Dá se kalibrace rozšířit o závislost na teplotě?** Kalibrace **už teplotně závislá je** (pět pásem). **[KÓD]**
- **Ovlivní zimní kalibrace léto?** **Ne.** Zimní jízdy mění jen buňky pásem 0 a 1, letní výpočet používá pásmo 3. **[KÓD]**
  - Opačná strana: zimní pásmo začíná bez dat (faktor 1). Letní zkušenost se do zimy nepřenáší. **[KÓD]**
  - Podzimní jízda s průměrem např. +4 °C už spadne do „zimního“ pásma. **[KÓD]**

### 5.3 Nedostatky kalibrace

1. **Pozorování se počítá s profilem z Nastavení, ne s profilem jízdy.** **[KÓD]** `local/service.ts:340`
   - Jede-li uživatel podle varianty „Eko“ (110 km/h) a v Nastavení má „standard“ (123,5 km/h), predikce bude vyšší než skutečnost. Kalibrace se pak chybně posune dolů.
2. **Teplota pozorování je předpověď z doby plánování, ne skutečnost.** **[KÓD]** Pokud se plánovalo den dopředu, může být výrazně jiná (viz 2.1, chybí čas odjezdu).
3. **Jedno pásmo na celé pozorování.**
   - Cesta z +6 °C v nížině do −6 °C na horách dostane průměr a jedno pásmo. **[KÓD]**
   - U dlouhých jízd přes pásma to kalibraci rozmazává. **[PŘEDPOKLAD]**
4. **Skupiny silnic se v rámci jedné jízdy nerozliší.**
   - Všechny skupiny dostanou stejný poměr. Faktory dálnice a města se od sebe oddělí až z různorodých jízd. **[KÓD]**
5. **Kalibrace je vázaná na verzi modelu.**
   - Faktor k = naměřeno / *starý* model. Pokud se změní základní hodnoty spotřeby, staré faktory nebudou sedět.
   - Uložená pozorování nemají trasu, takže je nelze přesně přepočítat. **[KÓD]**
   - Toto je **hlavní riziko** při zavádění nových hodnot.

---

## 6. Shrnutí nedostatků

| # | Nedostatek | Zdroj | Dopad |
|---|---|---|---|
| 1 | Zimní složky (0,12 kW/°C, 0,3 kW, 0,006/°C) nemají zdroj měření | KÓD (+ PŘEDPOKLAD o přesnosti) | Zimní spotřeba je odhad |
| 2 | Nelze zadat čas odjezdu, předpověď je vždy „od teď“ | KÓD | Špatná teplota u plánu dopředu |
| 3 | Teplota baterie = teplota vzduchu, bez zahřátí během jízdy | KÓD | Pravděpodobně nadhodnocení na dlouhých zimních jízdách (PŘEDPOKLAD) |
| 4 | Nabíjecí výkon v mrazu se nepočítá (`batteryTempC` = null) | KÓD | Podhodnocená doba nabíjení v zimě |
| 5 | Kalibrace porovnává s profilem z Nastavení, ne s variantou jízdy | KÓD | Chybný posun kalibrace u varianty Eko |
| 6 | Pozorování = 1 pásmo podle průměrné teploty z předpovědi | KÓD | Rozmazání u jízd přes pásma |
| 7 | Změna základních hodnot znehodnotí stávající kalibraci | KÓD | Riziko při zavádění nových hodnot |
| 8 | Nejde ručně zvolit teplotní podmínky | KÓD | Požadavek kap. 4 |
| 9 | Odhad hodiny průjezdu počítá s 0,9 × limit, ne s rychlostí modelu | KÓD | Malý časový posun teplot, zanedbatelné |

---

## 7. Doporučení pro integraci nových hodnot (9 kombinací)

Pořadí od nejmenšího zásahu:

**Krok A — Hodnoty jako cílová tabulka, model zůstává.**
- Devět hodnot (léto / zima / arktický × 50 / 90 / 120 km/h) se uloží jako referenční tabulka.
- Stávající koeficienty (`a`, `b`, `cityExtra`, `heatBaseKw`, `heatKwPerC`, `battTempCoef`) se **proloží** tak, aby model tabulku co nejlépe reprodukoval.
- Mění se jen čísla, ne vzorec. Plánovač, optimalizace zastávek, nabíjení i ceny zůstanou beze změny.
- Pokud se tabulka trefí s odchylkou do ±5 %, další zásah není potřeba.

**Krok B — Korekční tabulka, jen pokud krok A nestačí.**
- Model by měl pevný tvar (kvadratická jízda + vytápění ~1/v). Devět libovolných hodnot možná nepřesně reprodukuje. **[PŘEDPOKLAD]**
- V takovém případě se doplní korekční faktor `k_teplota(skupina silnic, T)`, interpolovaný mezi body tabulky. Násobil by se na stejném místě jako dnešní kalibrace, jen pod ní.
- Kalibrace z jízd zůstane jako poslední vrstva.

**Krok C — Ruční režim (kap. 4).**
- Parametr `tempOverrideC` a volba v plánu: Auto / Léto (+20 °C) / Zima (0 °C) / Arktický (−10 °C).
- Pozorování pro kalibraci se vždy počítá se **skutečnou předpovědí**, ne s ručním režimem. Ruční volba tak kalibraci nezkreslí.

**Krok D — Ochrana stávající kalibrace.**
1. Před změnou udělat export zálohy (funkce už v Nastavení je).
2. K pozorováním a buňkám přidat `modelVersion`.
3. Při změně základních hodnot přepočítat každou buňku: `k_nový = k_starý × E_starý_model / E_nový_model`. Počítá se ve středu pásma při typické rychlosti skupiny.
   - Tím se zachová to, co se už naměřilo, a faktory budou platit vůči novému modelu.
   - Přepočet je přibližný. Skutečná pozorování nemají uloženou trasu. **[KÓD]**
4. Současnou kalibraci nemazat.

**Krok E — Související opravy (doporučeno, nezávislé).**
- Pozorování počítat s profilem jízdy, ne s profilem z Nastavení (nedostatek 5).
- Volitelně čas odjezdu v plánu (nedostatek 2).
- Volitelně použít zimní nabíjecí faktor (nedostatek 4). Ten ale mění časy nabíjení, tak jen po schválení.

**Co zůstane beze změny:**
- algoritmus plánování a optimalizace zastávek (`core/optimizer.ts`),
- výpočty času a ceny nabíjení (`core/charging.ts`),
- rezervy SoC,
- meteorologická funkce (`data/weather.ts`),
- přívěs,
- krátkodobá korekce `k_trip`.

Rychlost výpočtu se nezmění, protože jde o konstantní práci na úsek.

**Podklady potřebné pro další fázi:**
1. Spotřeba Voyah Free pro 9 kombinací.
2. U každé hodnoty, zda platí „z baterie“ nebo „ze zásuvky“. Aplikace počítá **z baterie**; nabíjecí ztráty řeší zvlášť účinností 0,95.
3. Zda hodnoty platí po předehřátí auta, nebo při studeném startu.
