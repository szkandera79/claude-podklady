# Cenová nabídka — zelená kotelna BD u Dolu Michal, Ostrava-Michálkovice

Nabídka pro novostavbu bytového domu (24 b.j.) ve dvou výkonnostních variantách. Graficky
i strukturou vychází z `vzor-bytove-domy/` (zelená kotelna) a technicky z
`porovnani-x50-2-3/` (data RH X50) a `bd-michal/` (PENB, schémata kotelny).

## Varianty
| | Varianta A | Varianta B (doporučená) |
|---|---|---|
| Jednotky | 2× RH X50 | 3× RH X50 |
| Výkon při −15 °C / W35 | 61,8 kW | 92,7 kW |
| Souběh s ohřevem TUV | 30,9 kW → deficit 22,1 kW | 61,8 kW → bez deficitu |
| Výpadek jednotky | 30,9 kW (58 % ztráty) | 61,8 kW (117 % ztráty) |
| Bivalence | 2× 11 kW patrony + elektrokotel 30 kW | doplňková patrona 11 kW |
| Investice bez DPH | 1 790 000 Kč | 2 090 000 Kč |

Rozdíl 300 000 Kč = třetí jednotka (390 000 Kč) místo průtokového dohřevu a elektrokotle (90 000 Kč).
Topné spirály v nádržích (5 × 12 000 Kč) a podružný rozvaděč (40 000 Kč) jsou v obou variantách.

## Vstupy
- Tepelná ztráta 53 kW při −15 °C (investor uvádí 52 kW), vytápění 107,45 MWh/rok — PENB č. 530077.2
  (TRIPLAN, 12/2023), podklady v `~/Claude/BD Michal Claude/`.
- TUV 50,07 MWh/rok = PENB (56,33 MWh pro 27 b.j.) přepočtené na **24 b.j.** potvrzených investorem 23. 9. 2026.
- RH X50: A−15/W35 **30,9 kW, COP 2,10**; A−15/W55 24,8 kW, COP 1,50 (výkonový protokol
  kopie v `src/rh-x50-data.json`).
- Ceník sestav ze vzorové nabídky: 2 jednotky 1 600 000 Kč, každá další 390 000 Kč.
- Ceny bivalence z podkladu 23. 9. 2026 (bez DPH): elektrokotel 30 kW 50 000 Kč, průtokový dohřev
  11 kW 20 000 Kč/ks, topná spirála 9 kW s termostatem 12 000 Kč/nádrž (5 nádrží = 45 kW), podružný rozvaděč 40 000 Kč.

## Poptávka pro investora
`poptavka.html` je **poptávkový list, který rozesílá investor konkurenci** — záměrně bez značky
dodavatele, s modrým akcentem a s místy k doplnění (zadavatel, kontakt, termín). Poptává výkon kaskády,
ne konkrétní počet jednotek (orientačně 2 × 50 kW): při −15 °C/35 °C nejméně 60 kW, pro TUV
nejméně 24 kW při −15 °C/55 °C, nejnižší stupeň do 15 kW. Varianta B = táž kaskáda plus jedna
jednotka jako plnohodnotná záloha, oceněná i samostatně. **Elektrická bivalence se nespecifikuje** —
zadán je jen funkční požadavek (krytí deficitu při ohřevu TUV a provoz při poruše jednotky), návrh
je na uchazeči. Závazné: akumulace 2× 1 000 l, zásobníky TUV 3× 1 000 l, spirála s termostatem v každé nádrži (výkon
nepředepsán, musí stačit na dezinfekci 55→65 °C do 4 h a na ukládání přebytků FVE), nejvýše
5 nádrží celkem a průměr do 90 cm kvůli stometrovému prostupu do kotelny.
Obsahuje prázdné tabulky k vyplnění (výkony a COP, příkon a jistič, rozpad ceny).

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --no-pdf-header-footer \
  --print-to-pdf="$HOME/Downloads/BD-Michal-poptavka-zdroj-tepla.pdf" \
  "file://$PWD/bd-michal-nabidka/poptavka.html"
```

## Podklad pro společníky investora
`podklad-spolecnici.html` shrnuje nabídku pro jednání investora se společníky, kteří se v oboru
orientují: efektivita (1,11 Kč/kWh tepla proti 3,50 Kč u přímotopu, SCOP 3,15), cena na byt
a na kW, třetí jednotka jako plnohodnotná záloha za 390 000 Kč (16 250 Kč/byt) a tabulka
pro doplnění konkurenčních nabídek.

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --no-pdf-header-footer \
  --print-to-pdf="$HOME/Downloads/BD-Michal-podklad-pro-spolecniky.pdf" \
  "file://$PWD/bd-michal-nabidka/podklad-spolecnici.html"
```

## Soubory
- `nabidka.html` — dokument (tisk / PDF z prohlížeče), soběstačný, interní blok se netiskne.
- `graf-vykon.svg` — graf krytí výkonu; do nabídky se vkládá inline mezi `<!--GRAF-->`.
- `src/model.py` — propočet krytí, roční bilance (binová metoda), výpadku jednotky a rezervovaného příkonu.
- `src/gen_chart.py` — generuje graf a vloží ho do nabídky.

```bash
python3 bd-michal-nabidka/src/model.py       # čísla do sekcí 3–9
python3 bd-michal-nabidka/src/gen_chart.py   # graf + inline do nabidka.html
```

## Tisk do PDF
```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --no-pdf-header-footer \
  --print-to-pdf="$HOME/Downloads/ThermaVera-BD-Michal-cenova-nabidka.pdf" \
  "file://$PWD/bd-michal-nabidka/nabidka.html"
```

## Poznámka k modelu
Teplotní křivka trvání je kalibrovaná na potřebu tepla z PENB (107,45 MWh na vytápění).
Vychází z ní průměrná venkovní teplota 11,3 °C, tedy víc než skutečný ostravský průměr —
PENB je na optimistické straně a model ho následuje.

## Otevřené body
1. Spirály 9 kW jsou ve všech pěti nádržích (2 AKU + 3 TUV). Spirály v akumulaci dávají 18 kW, tedy skoro celý deficit 22,1 kW — ověřit, zda je průtokový dohřev 2 × 11 kW u varianty A ještě potřeba.
2. Zásobníky TUV: 3× 1 000 l = 125 l/byt při 24 b.j.; pravidlo 150–180 l/byt by znamenalo 3,6–4,3 m³.
3. Rezervovaný příkon a sazbu potvrdit s distributorem.
4. Cena elektřiny 3 500 Kč/MWh bez DPH převzata ze vzorové nabídky.
