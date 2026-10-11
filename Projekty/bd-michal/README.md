# Kotelna BD Michal — koncepční schémata

Podklady k projednání pro zdroj tepla bytového domu **Michal**. Nejde o web ThermaVery —
jsou to samostatné projektové podklady mimo `index.html`.

## Soubory
- **`01-hydraulicke-schema.svg`** — hydraulické schéma zdroje tepla
  (2× TČ REO X50 → společný primární okruh se sběračem → akumulace → zásobník TUV;
  elektrokotel jako záloha, distribuce do topných okruhů).
- **`02-schema-regulace.svg`** — funkční schéma regulace (MaR): PLC jako nadřazený
  regulátor, sběrnice Modbus TCP, hardwarová I/O, sekvence spínání zdrojů, priorita TUV,
  odmrazování, ochrany, alarmy, vzdálený dohled, energetický manažer.
- **`03-rizeni-bivalence.md`** — funkční specifikace nadřazeného řízení bivalence pro
  programátora MaR: výpočet výkonového deficitu místo pevné bivalentní teploty, měření
  tepelného výkonu z průtoku a ΔT, kaskádování a rotace, bivalence ÚT i TUV, legionella,
  samostatný algoritmus přebytku FVE, poruchové režimy, omezovač příkonu, stavový automat,
  matice priorit, seznam čidel a I/O, mapa Modbus registrů, tabulka parametrů, alarmy.
- **`03-stavovy-automat.svg`** — výkres stavového automatu a matice priorit (grafická
  podoba kapitol 10 a 11 specifikace).
- **`04-hydraulika-3TC.svg`** — **aktuální zdroj (09/2026): 3× TČ vzduch/voda 50 kW.**
  TČ1 jen ÚT, TČ2 ÚT + TUV, TČ3 záloha (rev. 1). Tři paralelní větve se zpětnými klapkami a uzávěry, sběrač/rozdělovač DN150, akumulace
  2× 1 000 l, okruh vytápění, nabíjení TUV 3× 1 000 l přes deskový výměník, tabulka průtoků
  pro 50/100/150 kW při ΔT 5 K a předběžné DN.
- **`05-rezimy-TC2-TC3.svg`** — čtyři režimy: A vytápění, B TČ2 nabíjí TUV, C TČ3 záloha ÚT,
  D TČ3 záloha TUV; poloha ventilů V2/V3, matice režimů, logika řízení.
- **`04-hydraulika-3TC.md`** — popis, průtoky, logika řízení a **upozornění k zadání
  s doporučenými úpravami** (výkon při −15 °C, záloha TUV, glykol, akumulace).
- **`smlouva/`** — návrh smlouvy o dílo (zhotovitel Riva Trade, s.r.o.) v2.0 po zátěžovém testu z pozice objednatele: text smlouvy, přílohy, riziková analýza, modelové situace. `.docx` se generuje z `.md` přes `python3 smlouva/src/md2docx.py`.
- **`src/gen_3tc.py`** — generátor výkresů 04 a 05 (`python3 src/gen_3tc.py`).

> Výkresy 01–03 vycházejí ze 2× TČ. Pro zdroj tepla platí TV-BDM-04; specifikaci řízení 03
> je potřeba doplnit o role TČ1–TČ3 a režimy A–D.

Oba soubory jsou vektorové (SVG) — otevřou se v prohlížeči i v editoru (Inkscape/Illustrator),
lze je tisknout a exportovat do PDF (v prohlížeči: Tisk → Uložit jako PDF, formát A3 na šířku).

## ⚠️ Charakter podkladu
**Koncepční schémata — orientační podklad k projednání, ne razítkovaná dokumentace.**
Dimenze potrubí, počty a typy armatur, výkony a rozsah I/O musí ověřit autorizovaný
projektant TZB / MaR podle skutečných tepelných ztrát objektu a měřených dat.

## Předpoklady (k potvrzení)
| Položka | Předpoklad ve schématu | Ověřit |
|---|---|---|
| TČ REO X50 | 2× 50 kW (celkem ~100 kW) | skutečný jmenovitý výkon při návrhové −15 °C |
| Elektrokotel | ~45 kW, záloha/špička | dle bilance a rezervovaného příkonu |
| Akumulace | 1× buffer (stratifikace) | objem dle taktování a výkonu |
| TUV | zásobník s nabíjením z akumulace | objem dle odběrového diagramu domu |
| Regulace | PLC + Modbus TCP master | konkrétní typ (Siemens/Beckhoff/…), rozsah I/O |

Upřesnění osazení pro dokument 03 (dle zadání 09/2026): akumulace ÚT **1 000 l**,
zásobník TUV **3 000 l**, elektrické topné patrony v obou nádržích, FVE 46 kWp
s baterií 40,8 kWh, tepelná ztráta objektu 53 kW při −15 °C (PENB č. 530077.2).

## Návrhové varianty — porovnání a doporučení
Kde existuje více technicky správných řešení, uvádím varianty s doporučením:

1. **Ohřev TUV: topný had v zásobníku × externí deskový výměník + nabíjecí čerpadlo**
   - *Had:* jednodušší, méně armatur, nižší cena; pomalejší dohřev, nižší výkonová špička.
   - *Deskový výměník:* rychlé nabití, hygieničtější (menší objem stojaté vody), vyšší výkon;
     složitější, dražší, nutné čerpadlo a regulace.
   - **Doporučení:** pro bytový dům s koncentrovanými odběry TUV **externí výměník + nabíjecí
     čerpadlo** (varianta ve schématu) — lépe pokryje ranní/večerní špičky.

2. **Elektrokotel: v sérii na přívodu × jako ohřev akumulace**
   - *V sérii:* rychlá reakce na okamžitý deficit, dohřeje přesně přívod do ÚT.
   - *Do akumulace:* jednodušší hydraulika, ale pomalejší a méně adresné.
   - **Doporučení:** **v sérii za akumulací** (varianta ve schématu) — elektrokotel je záloha/špička,
     má se přidávat jen chybějící výkon a se zpožděním.

3. **Primár: prostý rozdělovač/sběrač × hydraulický vyrovnávač (anuloid/HVDT)**
   - *Rozdělovač/sběrač:* přehledné, když akumulace plní funkci hydraulického oddělení.
   - *HVDT:* jistota oddělení průtoků primár/sekundár u rozdílných čerpadel.
   - **Doporučení:** s dostatečně dimenzovanou **akumulací jako hydraulickým oddělením** obvykle
     stačí rozdělovač/sběrač; HVDT zvážit dle skutečných průtoků TČ.

4. **Primární čerpadla: 1 společné × 2 (na každé TČ)**
   - **Doporučení:** **2 čerpadla** (po jednom na TČ, ve schématu) — nezávislý provoz a defrost
     jednotlivých TČ, redundance při poruše.

## Sekvence řízení (shrnutí)
`TČ1 → TČ2 → (trvající deficit) → elektrokotel se zpožděním`, priorita levných zdrojů,
střídání TČ dle motohodin, priorita TUV, koordinace defrostů, ochrany a alarmy, měření
a report do cloudu přes energetický manažer.


## Otevřené body k doplnění (blokují detailní návrh MaR)
1. Rezervovaný příkon / hlavní jistič a sazba včetně časů blokování HDO.
2. Výkonové křivky dodaných TČ (−15 až +15 °C, výstup 30–50 °C).
3. Modbus dokumentace jednotek — mapa registrů a význam bitů stavového slova.
4. Skladba topných patron (počty, výkony, stupně vs. modulace SSR).
5. Potvrzení objemů nádrží proti taktování a odběrovému diagramu TUV.
6. Typ PLC a HMI, rozsah I/O karet.

Podrobně viz kapitola 16 v `03-rizeni-bivalence.md`.

## Zdrojové podklady
Projektová dokumentace, PENB a koncepce vytápění (porovnání centrální × decentrální
varianty) jsou mimo repozitář ve složce `~/Claude/BD Michal Claude`.
