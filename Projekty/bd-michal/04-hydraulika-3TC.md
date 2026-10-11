# Zdroj tepla 3× TČ — hydraulika a režimy TČ2 / TČ3 (TV-BDM-04, TV-BDM-05)

**Stupeň:** předběžný návrh · **Rev.:** 1 · **Datum:** 09/2026

**Rev. 1:** TČ1 pouze vytápění, TČ2 vytápění + TUV, TČ3 záloha připojovaná k ÚT nebo k TUV jen při poruše nebo nedostatku výkonu.

> **Předběžný návrh, ne prováděcí dokumentace.** Dimenze DN jsou orientační, stanovené jen
> z průtoku při ΔT 5 K a doporučené rychlosti. Před objednáním je nutný výpočet tlakových
> ztrát celé trasy, návrh čerpadel, expanzních nádob a pojistných ventilů. Zpracuje
> autorizovaný projektant TZB.

## Soubory

| Soubor | Obsah |
|---|---|
| `04-hydraulika-3TC.svg` | celkové hydraulické schéma: tři paralelní větve TČ, sběrač/rozdělovač, akumulace 2× 1 000 l, okruh vytápění, nabíjení TUV 3× 1 000 l, tabulka průtoků a DN |
| `05-rezimy-TC2-TC3.svg` | čtyři provozní režimy (A vytápění, B TČ2 nabíjí TUV, C TČ3 záloha ÚT, D TČ3 záloha TUV), poloha ventilů, matice režimů, logika řízení |
| `src/gen_3tc.py` | generátor obou výkresů — úpravy dělat zde a znovu spustit `python3 src/gen_3tc.py` |

## Zadání (09/2026, rev. 1)

- TČ1 50 kW — MASTER, **pouze vytápění**.
- TČ2 50 kW — SLAVE, **vytápění i příprava TUV**.
- TČ3 50 kW — **záloha**, připojí se k vytápění nebo k TUV jen při poruše nebo nedostatku výkonu.
- Topná akumulace 2× 1 000 l, TUV 3× 1 000 l, monobloky vzduch/voda, Modbus.
- Tepelná ztráta objektu 53 kW při −15 °C (PENB).

## Koncepce zapojení — čtyři oddělené okruhy

1. **Primár TČ.** Tři paralelní větve DN50. Každá větev má antivibrační hadice, uzávěry na obou
   stranách, vlastní čerpadlo P1–P3, filtr s magnetickým odkalovačem, zpětnou klapku ZK,
   průtokoměr, čidlo teploty a pojistný ventil před uzávěrem. Zpětná klapka brání zpětnému
   průtoku přes stojící jednotku.    TČ1 je napojeno přímo do sběrače/rozdělovače DN150. TČ2 a TČ3 mají každé dvojici 3cestných
   ventilů (V2.1/V2.2, V3.1/V3.2): port B vede do sběrače ÚT, port A do společného potrubí DN80
   k výměníku VT. Klidová poloha ventilů je B.
2. **Topná akumulace.** AKU1 a AKU2 po 1 000 l, propojené horem i spodem DN100. Primár je
   napojen na AKU1, vytápění na AKU2, nádoby tak tvoří hydraulické oddělení primáru od vytápění.
   Hrdla vyžadují rozrážeče proudu, jinak proud 26 m³/h rozmíchá stratifikaci.
3. **Okruh vytápění.** DN65, směšovací ventil V1 omezuje přívod do podlahového topení na 35 °C,
   zdvojené čerpadlo P4, kalorimetr M3, vlastní EN2 a PV2.
4. **Nabíjení TUV.** TČ2, případně TČ3, ohřívá deskový výměník VT dimenzovaný na ~100 kW (okruh k VT s vlastní EN3 a PV3). Na straně
   pitné vody nabíjecí čerpadlo P5 odebírá vodu ze spodu TUV1 a vrací ohřátou do horní části TUV3.
   Zásobníky jsou v sérii: studená voda → TUV1 → TUV2 → TUV3 → termostatický směšovací ventil → byty.
   Topné patrony E3–E5 v každém zásobníku slouží pro legionellu a zálohu.

## Průtoky a předběžné DN

Výpočet: `Q [m³/h] = P [kW] / (1,152 · ΔT [K])`, voda ~40 °C, ΔT = 5 K, ocelové trubky.
Rychlost a měrná tlaková ztráta R jsou orientační (drsnost 0,045 mm).

| Úsek | Výkon | Průtok | DN | v [m/s] | R [Pa/m] |
|---|---|---|---|---|---|
| Větev TČ1 / TČ2 / TČ3 | 50 kW | 8,7 m³/h (2,4 l/s) | DN50 | 1,03 | ≈215 |
| Přívod do AKU — TČ1+TČ2 | 100 kW | 17,4 m³/h (4,8 l/s) | DN80 | 0,90 | ≈100 |
| Přívod do AKU — i s TČ3 | 150 kW | 26,0 m³/h (7,2 l/s) | **DN100** | 0,80 | ≈60 |
| Sběrač / rozdělovač | 150 kW | 26,0 m³/h | DN150 | 0,36 | — |
| Propojení AKU1–AKU2 | ≤150 kW | ≤26,0 m³/h | DN100 | ≤0,80 | — |
| Okruh vytápění | 53 kW | 9,2 m³/h | DN65 | 0,66 | ≈65 |
| Potrubí k VT: TČ2 + TČ3 | 100 kW | 17,4 m³/h | DN80 | 0,90 | ≈100 |

- Přívod do akumulace navrhnout na 150 kW, protože v režimu C topí všechna tři TČ.
- Výměník VT a potrubí k němu navrhnout na 100 kW, protože v režimu D mohou TUV nabíjet TČ2 i TČ3.
- Při delší vnější trase k monoblokům zvážit větve DN65 (R klesne na ≈60 Pa/m).
- S 30 % propylenglykolem vzroste průtok o ~6 % a tlaková ztráta o 35–40 %. V praxi to znamená o jednu DN výš.

## Provozní režimy

| Režim | TČ1 | TČ2 (V2) | TČ3 (V3) | Spouštěč |
|---|---|---|---|---|
| A — vytápění | ÚT | ÚT, port B | stojí, klid B | výchozí stav, TUV nabitá |
| B — TČ2 nabíjí TUV | ÚT | TUV, port A | stojí, klid B | TS7 < 45 °C; konec TS8 ≥ 52 °C nebo 60 min |
| C — záloha ÚT | ÚT | ÚT nebo TUV | ÚT, port B | deficit ÚT, porucha TČ1, porucha TČ2 v době topení |
| D — záloha TUV | ÚT | TUV nebo porucha | TUV, port A | porucha TČ2, nabíjení > 60 min a TS7 < 42 °C |

## Logika řízení (stručně)

- **Priorita požadavků:** bezpečnost a protizámraz, TUV pod 40 °C, vytápění, komfort TUV, patrony.
- **TČ2 přepíná do TUV samo** (režim B). Po dobu nabíjení topí TČ1 samo.
- **Deficit ÚT** je potvrzený, když dostupná TČ běží na ≥ 95 % po 15 minut a akumulace je pod žádanou o více než 3 K. Typicky nastane během nabíjení TUV v zimě, pak se připojí TČ3 (režim C).
- **TČ3 vždy jen k jednomu okruhu.** Při současném požadavku má přednost TUV pod 40 °C, jinak vytápění. Zbytek kryjí patrony podle TV-BDM-03.
- **Návrat TČ3 do zálohy:** požadavek zanikl na 20 minut nebo porucha odstraněna. Minimální doba v režimu 30 minut.
- **Sekvence přepnutí** (TČ2 i TČ3): stop kompresoru a doběh čerpadla 2 minuty, přestavení obou ventilů páru současně, kontrola koncových spínačů, změna režimu a žádané teploty přes Modbus, start po minimální době klidu. TČ2 a TČ3 se nepřepínají současně. Nesoulad spínačů znamená alarm a blokaci jednotky.
- **Provozuschopnost zálohy:** TČ3 jednou týdně zkušební běh 30 minut, střídavě do ÚT a do TUV.

## Upozornění k zadání a doporučené úpravy

### 1. Výkon „50 kW" — při jakých podmínkách?
Ztráta objektu je 53 kW při −15 °C. Pokud je 50 kW jmenovitý výkon při A7/W35, dá jednotka
při −15 °C a výstupu 45 °C obvykle jen 60–70 %, tedy 30–35 kW. TČ1+TČ2 pak pokryjí ztrátu těsně
a TČ3 jako třetí stupeň má smysl. Pokud je 50 kW výkon už při −15 °C, je instalace 150 kW
zhruba trojnásobkem ztráty a vychází zbytečně drahá (investice, rezervovaný příkon, taktování
při malém odběru). **Doporučení:** vyžádat výkonové křivky a ztrátu ověřit výpočtem podle ČSN EN 12831.

### 2. Nová logika řeší zálohu TUV i vytápění
Protože je přepínatelné TČ2 i TČ3, má TUV zálohu tepelným čerpadlem a vytápění také. To odstraňuje
hlavní slabinu první verze.

### 3. Odvrácená strana pevných rolí
- **TČ2 nese nejvíc práce.** Topí i nabíjí TUV, takže naběhá nejvíc motohodin a nejvíc startů.
  TČ3 jako čistá záloha stojí většinu roku. Doporučuji zvážit střídání rolí TČ2 a TČ3 jednou za měsíc
  nebo po 500 h. Hydraulika to umožňuje beze změn, jde jen o parametr v řízení.
- **Během nabíjení TUV topí v zimě jen TČ1.** Při −15 °C dá asi 30–35 kW proti ztrátě 53 kW, takže
  téměř každé zimní nabíjení TUV spustí režim C a TČ3 poběží pravidelně. Pak je lepší brát ho jako
  plánovaný třetí stupeň, ne výjimečnou zálohu. Alternativa je nabíjet TUV mimo ranní špičku a
  v nejteplejší části dne.

### 4. Akumulace — volit 2× 1 000 l, ne 1 000 l
Jedna jednotka při minimální modulaci (~15 kW) nabije 1 000 l o 5 K za 23 minut, 2 000 l za 46 minut.
Při 150 kW zdroje je 1 000 l příliš malá rezerva pro taktování, odmrazování a přepínání TČ3.
**Doporučení:** 2× 1 000 l jako minimum, lépe 2× 1 500 l, pokud to prostor dovolí.

### 5. Náplň primáru: voda, nebo glykol
Monobloky stojí venku a při výpadku proudu hrozí zamrznutí.
- **Voda** (zakresleno): protizámrazové ventily u jednotek, záložní napájení čerpadel P1–P3,
  ochranný ohřev vnější trasy. Vyšší COP, nižší ztráty.
- **Glykol:** celý primár včetně sběrače a okruhu TČ3–VT s glykolem a výměník ~150 kW mezi
  sběračem a akumulací. Nutná vyšší DN, výměník ubere 2–3 K a jednotky procent COP.
  VT na pitnou vodu pak s dvojitou stěnou.

Rozhodnutí je potřeba před dalším stupněm, mění sestavu kotelny.

### 6. TUV přes deskový výměník místo spirál
Zakreslen externí deskový výměník. Spirály ve standardních zásobnících 1 000 l nepřenesou 50 kW
při malém teplotním rozdílu na konci nabíjení. Na TČ by bylo potřeba asi 0,25 m²/kW, tedy ~12 m²
na tři zásobníky. Výměník navíc umožní sériové zapojení zásobníků se stratifikací.
Riziko je zanášení vodním kamenem: výstup VT omezit na 55 °C, legionellu řešit patronami přímo
v zásobnících a ověřit tvrdost vody. Pokud výrobce dodá zásobníky se spirálami ≥ 4 m², jde o
jednodušší alternativu bez čerpadla P5.

### 7. Legionella
Běžné monobloky dosáhnou výstupu 55–60 °C. Dezinfekce 60–65 °C proto vyžaduje patrony E3–E5,
případně TČ3 s chladivem R290 a vyšší výstupní teplotou.

### 9. Monobloky s vestavěným čerpadlem
Pokud mají jednotky vlastní oběhové čerpadlo, vnější P1–P3 odpadají nebo je nutná hydraulická
koordinace, aby nevznikl konflikt dvou čerpadel v sérii. Zpětná klapka ve větvi zůstává.

### 10. Rezervovaný příkon
Při −15 °C mají tři jednotky elektrický příkon řádově 50–60 kW, k tomu patrony. Ověřit hlavní
jistič a zapojit omezovač příkonu (TV-BDM-03, kap. 9).

## Co ověřit před dalším stupněm
1. Výkonové křivky TČ (A−15 až A+7, W35–W55), minimální průtok, vestavěné čerpadlo, max. výstupní teplota.
2. Tepelná ztráta výpočtem ČSN EN 12831 a odběrový diagram TUV.
3. Náplň primáru (voda × glykol) a délka vnější trasy k monoblokům.
4. Rozměry kotelny pro 2 AKU + 3 TUV + VT, přístup pro servis.
5. Rezervovaný příkon a sazba (blokování HDO).
6. Rozhodnutí o střídání rolí TČ2 a TČ3.

## Návaznost na starší podklady
- `01-hydraulicke-schema.svg` a `02-schema-regulace.svg` vycházejí ze 2× TČ a jedné akumulace.
  Pro zdroj platí nově TV-BDM-04.
- `03-rizeni-bivalence.md` a `03-stavovy-automat.svg` počítají se 2 jednotkami. Principy deficitu
  zůstávají, doplnit je třeba role TČ1–TČ3, režimy A–D, přepínání V2/V3 a Modbus registry TČ3.
