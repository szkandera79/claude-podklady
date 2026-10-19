# MM Holz / Alignum — revize 1: audit před zapracováním nové koncepce

Datum: 19. 10. 2026.
Výchozí stav (rev0):
- `../README.md` – varianta V4 2 × RH X50 schválená, V3 vyloučená,
- `../email-dornak-koncept.md` – koncept e‑mailu, neodeslán,
- `../src/sestavy.py` – výpočty.

Nové zadání (rev1): 2 × RH X50 + 3 × elektrokotel 24 kW, AKU 2 × 1 000 l ve stávající kotelně, max. přívod 70 °C, bez TUV, přívod 3 × 160 A.

Značení zdrojů:
- **[D]** deklarováno výrobcem (návod, výkonová mapa),
- **[C]** certifikováno (KEYMARK),
- **[P]** projekt klienta (DSP ESL 2005),
- **[O]** vlastní výpočet nebo odhad,
- **[CHYBÍ]** údaj, který podklady neobsahují.

## 1. Rozpory nového zadání s podklady

| # | Nové zadání | Podklady | Dopad |
|---|---|---|---|
| R1 | Původní spád **85/60 °C** | Hala **80/60 °C**, administrativa **75/60 °C** [P]; primár teplovodu 95 °C | Spád 85/60 se v podkladech nevyskytuje. Je potřeba ověřit, odkud pochází. |
| R2 | Návrhový výkon **≈ 88 kW** | 88 kW je **náš odhad z rev0**: čerpadlo haly 3,8 m³/h × ΔT 20 K [O]. Jde **jen o halu**. Administrativa má dalších ≈ 17 kW (1 m³/h × 15 K). | Celkem ≈ 105 kW (projektově). Při spádu 85/60 by stejný průtok znamenal 110 kW jen pro halu. Žádné z čísel není tepelná ztráta. |
| R3 | Odběr tepla přes **existující výměník** | HV VS 200 kW (ESL) je voda–voda, primár 95 °C / 0,5 MPa. Typ, plocha a teploty výměníku **[CHYBÍ]**. | Zapojení TČ na primár výměníku stojí ≈ 3–5 K [O]. Ze 70 °C z TČ by pak k saharám šlo ≈ 65–67 °C. rev0 navrhovala připojení **za výměník** (na sekundár). |
| R4 | Jen sahary | Na stejném rozdělovači RS Kombi 100 je i větev **administrativy** (radiátory, ESBE, DAB VA 35/130) [P] | Administrativu je potřeba zahrnout do bilance i do hydrauliky, jinak zůstane bez tepla. |
| R5 | TUV není součástí | Klient výslovně požaduje „ohřev vody (12 zaměstnanců × 3 směny)“. ACV 320 l se dnes ohřívá z výměníkové stanice [P]. | Po odpojení teplovodu přestane TUV fungovat. Je potřeba rozhodnout, kdo a čím ji ohřeje. |
| R6 | AKU 2 × 1 000 l ve „stávající prostorné kotelně“ | Výkres VS ukazuje místnost ≈ 4,8 m dlouhou s HV VS, rozdělovačem, ACV 320, expanzí a úpravou vody [P]. Šířka **[CHYBÍ]**. | 2 × AKU (Ø ≈ 1,0 m s izolací, v ≈ 2,0–2,1 m, klopná výška ≈ 2,3 m) + 3 elektrokotle + čerpadla se pravděpodobně nevejdou. Nutná obhlídka a zaměření. |
| R7 | Dvě RH X50 ≈ 33,6 kW | Návod RH X50: **max. 20 kW / 32 A na jednotku, jistič 40 A** [D] → 2 × = **40 kW / 64 A**. Výkonová mapa: max. ≈ 17,5 kW na jednotku [D]. | Hodnota 33,6 kW v dokumentaci není. Pro jištění a souběh platí 64 A. |
| R8 | Stávající koncepce = mobilní kontejner s glykolovým primárem a výměníkem (studie, rev0) | Nové zadání kontejner nezmiňuje | Pokud zůstane glykol + deskový výměník, ztráta ≈ 2–3 K ještě víc ztíží dosažení 70 °C. Bez glykolu hrozí zamrznutí venkovních jednotek (návod pod 0 °C nemrznoucí směs **požaduje** [D]). |
| R9 | rev0 / e‑mail: 2 × X50 bez bivalence, TUV v ACV | Nové zadání přidává elektrokotle a ruší TUV | E‑mail p. Dorňákovi je nutné před odesláním přepracovat. |

## 2. RH X50 při 70 °C (výkonová mapa výrobce [D], max. otáčky, 1 jednotka)

| Bod | Topný výkon | COP | Příkon (výpočet) | Zdroj |
|---|---|---|---|---|
| A7/W70 | 32,3 kW | 2,00 | 16,2 kW | [D] mapa |
| A2/W70 | 29,9 kW | 1,80 | 16,6 kW | [D] mapa |
| A−7/W70 | 24,2 kW | 1,40 | 17,3 kW | [D] mapa |
| A−10/W70 | 21,9 kW | 1,25 | 17,5 kW | [D] mapa |
| A−12/W70 | **bez dat** | — | — | mapa W70 končí u −10 °C |
| A−15/W70 | **bez dat** | — | — | dtto |

- Certifikovaná data **[C]** (KEYMARK) existují jen pro W35/W55. Pro W70 nic certifikovaného není.
- Návod uvádí výstup „20–78 °C“ a v textu „při −25 °C výstup až 65 °C“ [D]. Výkonová mapa ale má W65 až od −12 °C a W70 až od −10 °C. **Rozpor je nutné vyjasnit s výrobcem.** Dokud nebude vyjasněn, 70 °C pod −10 °C nenabízet.
- Pod −10 °C mapa dává: W65 při −12 °C 23,4 kW, W60 při −12 °C 25,4 kW a při −15 °C 22,2 kW.
- Kaskáda 2 × X50: 70 °C → 43,8 kW (−10 °C); 60 °C → 50,8 kW (−12 °C).
- **Max. přípustná vstupní (vratná) teplota do X50 [CHYBÍ]**, návod ji neuvádí. Mapa W70 pracuje s ΔT ≈ 5 K, tedy se vstupem ≈ 65 °C [O]. Pro návrh je to rozhodující údaj, vyžádat od výrobce.
- Regulátor X50 má vlastní výstup „pomocný zdroj tepla“ (parametry 22–26, čidlo celkové výstupní teploty) [D]. Lze ho použít jako záložní signál, nadřazené řízení ale zůstane na PLC.

## 3. Teplovzdušné jednotky SAHARA a výměník

- **SAHARA W3634, 5 ks:** výrobce, výkon, průtok vzduchu, výkonová tabulka **[CHYBÍ]**. Projekt uvádí jen typ a nastavení šroubení Hertz Stromax (Š25/3,5–5,2) [P].
  - Pravděpodobně jde o starší řadu GEA Sahara, to je potřeba ověřit [O].
  - Zdroj údajů: štítky na jednotkách (foto), případně výrobce GEA / Kampmann a technický list.
- **Hrubý odhad do doby získání dat** [O]. Výkon ≈ úměrný rozdílu střední teploty vody a vzduchu, hala 17 °C, při stejném průtoku vzduchu i vody:

| Režim | vůči 80/60 °C (hala 20 °C) | vůči 85/60 °C |
|---|---|---|
| 70/60 °C | ≈ 96 % | ≈ 91 % |
| 70/55 °C | ≈ 91 % | ≈ 87 % |
| 65/55 °C | ≈ 86 % | ≈ 82 % |

  - **Varování:** spád 70/60 °C (ΔT 10 K) potřebuje pro stejný výkon **2× průtok** proti 80/60 °C.
  - Čerpadlo haly DAB A 50/180 XM (3,8 m³/h) ho nedá. Při stávajícím průtoku se zpátečka ochladí víc a výkon klesne pod hodnoty v tabulce.
  - Přesný přepočet vyžaduje tabulku výrobce (výkon při různých teplotách vody a stupních ventilátoru).
- **HV VS 200 kW (ESL):** typ výměníku, plocha a projektové teploty sekundáru **[CHYBÍ]**. Zdroj: štítek výměníku nebo dokumentace ESL.

## 4. Elektrický příkon (přívod 3 × 160 A)

| Spotřebič | Max. proud / fáze |
|---|---|
| 2 × RH X50 (max. dle návodu) | 64 A [D] |
| 3 × elektrokotel 24 kW (400 V, cos φ ≈ 1) | 104 A [O] |
| Čerpadla, PLC, regulace, ostatní | ≈ 5 A [O] |
| **Součet** | **≈ 173 A > 160 A** |

- Plný souběh všech zdrojů **není možný**.
- Při trvalém využití hlavního jističe max. 85 % (≈ 136 A) zbývá pro elektrokotle při plném chodu obou X50 jen ≈ 67 A, tedy **≈ 46 kW**. Při skutečném odběru X50 v bodě −10/W70 (≈ 27 A na jednotku) je to ≈ 54 kW.
- Plných 72 kW elektrokotlů je k dispozici jen při vypnutých TČ (nouzový režim): ≈ 109 A.
- Dynamické omezování podle měření fázových proudů je proto **nutné**, ne volitelné.

## 5. Výkonová bilance (orientačně, při −12 °C)

- TČ: W65 46,8 kW, W60 50,8 kW, W70 pod −10 °C bez dat.
- Elektrokotle elektricky omezené na ≈ 46–54 kW.
- **Celkem ≈ 93–105 kW.** Na projektových 88 kW (hala) stačí, na hala + administrativa ≈ 105 kW těsně.
- **Nouzový režim jen elektrokotle: 72 kW < 88 kW.**
  - Při projektové zátěži haly (88 kW při −12 °C) by samotné elektrokotle udržely 17 °C jen do ≈ −7 °C.
  - S administrativou do ≈ −3 °C [O].

## 6. Elektrokotle – kandidát Protherm RAY 24 KE

Zjištěno:
- nástěnný kotel s plynulou modulací (prospekt výrobce),
- min. jistič 40 A, kaskáda 24 a 28 kW.

**[CHYBÍ]:**
- externí řízení jednotlivých stupňů (12 × 6 kW),
- max. teplota a tlak,
- vestavěné čerpadlo a expanze (malá, pro domácí soustavy),
- komunikační rozhraní,
- aktuální cena.

Kotel s vlastní modulací a vlastním čerpadlem **nelze bez dalšího řídit po 6 kW z PLC**. Pro 12 stupňů po 6 kW je vhodnější alternativa:
- průmyslový elektrokotel, nebo
- elektrické topné příruby se stykači řízenými přímo z PLC,
- obojí s nezávislým havarijním termostatem (STB).

Výběr a ceny budou v rozpočtu označeny jako ověřené, předpokládané nebo odhad.

## 7. Hydraulika – zásadní připomínka k paralelnímu zapojení

- **Paralelní napojení elektrokotlů do AKU** ohřívá celou akumulaci, tedy i vodu, která se vrací do TČ. Při cílové teplotě 70 °C stoupne vstup do X50 nad ≈ 65 °C. Jednotka pak vypadne na vysoký tlak nebo nedá výkon, a elektřina vytlačí TČ z provozu (opak požadované priority).
- **Doporučuji sériový dohřev za akumulací** (přívod do soustavy):
  - TČ nahřívají AKU do teploty, kterou zvládnou (≈ 55–65 °C),
  - elektrický stupeň dohřívá jen přívod k saharám na 70 °C, a to jen když je třeba,
  - zpátečka do TČ zůstává studená.
- Dohřev musí mít **vlastní okruh s obtokem**: při poruše TČ pracuje sám. Varianta s vestavěnými čerpadly malých kotlů (≈ 1 m³/h) v hlavní větvi (≈ 7–8 m³/h) nefunguje.
- Paralelní zapojení AKU 2 × 1 000 l: v pořádku, s rozdělovacím vedením podle Tichelmanna. Alternativou je sériové řazení AKU (lepší stratifikace).
- Definitivně podle hydraulického výpočtu ve výstupech.

## 8. Navrhované změny proti rev0

1. Zdroje: 2 × X50 + elektrická bivalence (3 × 24 kW, řízení po 6 kW, je-li výrobek vhodný).
2. Umístění: AKU a technologie ve stávající kotelně místo kontejneru. **Ověřit prostor (R6)** a rozhodnout o glykolu (R8).
3. Připojení: **za výměníkem HV VS** (doporučeno) místo přes výměník. Musí rozhodnout klient / zadavatel (R3).
4. Teplota: max. 70 °C, ekvitermní řízení. 70 °C z TČ jen do −10 °C, pod tím dohřev elektřinou.
5. TUV mimo projekt – **vyžaduje potvrzení** (R5).
6. Elektro: přívod 3 × 160 A, dynamické omezení elektrokotlů, prioritní odpojování stupňů, rezerva 15 %.
7. Rev0 zůstává archivně beze změn, změny jen v `rev1/`. E‑mail se přepracuje až po rozhodnutí.

## 9. Otázky, bez kterých výstupy nedokončím správně

1. Odkud je spád 85/60 °C a hodnota 88 kW? Počítat halu + administrativu?
2. Připojení za výměník (doporučeno), nebo přes výměník HV VS?
3. Kontejner zůstává (glykol + výměník), nebo X50 přímo na vodu do stávající kotelny?
4. Opravdu bez TUV? Klient ji v poptávce uvádí.
5. Rozměry kotelny (půdorys, výška, dveře) – vejdou se 2 × AKU 1 000 l?
6. Štítky / typové listy: SAHARA W3634, výměník HV VS, čerpadla.
7. Od výrobce X50: max. vstupní teplota vody, potvrzení provozní obálky W65–W78 pod −10 °C.

Zdroje:
- Návod RH X50 – `REO/RH X50 komerční/RH X50 - REO HEATING/RH-X50-navod-k-pouziti.pdf`, str. 7–8 a 33–34.
- Výkonová mapa X50 – `univerzalni/src/vykony.json` (z DATA.json výrobce).
- Podklady klienta – `../podklady/`.
- Protherm RAY – https://www.protherm.cz/files/downloads/prospekty/prospekt-ray-v-02022024-2855726.pdf a https://www.arecenze.cz/?p=152519.

## Doplněk 19. 10. 2026 (po auditu)
- R2 vyřešen novým podkladem: statistika dodávky tepla MM Holz 2006–2026 → skutečná potřeba 62 kW při −12 °C / 69 kW při −15 °C (viz `02-vykonova-bilance.md`). Číslo 88 kW se pro návrh nepoužívá.
- Zadavatel rozhodl: připojení za výměník, sériový elektrický dohřev, bilance hala + administrativa, chybějící údaje označit.
