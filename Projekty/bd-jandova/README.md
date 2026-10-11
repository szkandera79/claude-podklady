# Kotelna BD Jandova 7, Ostrava-Zábřeh — nabídka

Podklady k nabídce pro bytový dům **Jandova 7, Ostrava-Zábřeh** (17 b.j.), náhrada dodávky
tepla z CZT (Veolia) tepelnými čerpadly vzduch/voda REO X50. Nejde o web ThermaVery —
samostatné projektové podklady mimo `index.html`.

## Soubory
- **`nabidka.html`** — cenová nabídka ve dvou variantách (tisk / uložení do PDF z prohlížeče).
  Obsahuje interní blok „před odesláním ověřit", který se **netiskne** a jde skrýt tlačítkem.
- **`schema-kotelny.svg`** — přehledový výkres obou variant na jednom listu (A3 na šířku),
  příloha nabídky.
- **`schema-varianta-1.svg`**, **`schema-varianta-2.svg`** — jednotlivé varianty, formát na výšku.
  Tyto jsou vložené v nabídce — na šířku A4 zůstává popis čitelný, což celý A3 list nesplňuje.
- **`src/gen_schema.py`** — generátor všech tří výkresů (`python3 src/gen_schema.py` z kořene repa).
- **`src/build_nabidka.py`** — vloží obě schémata variant přímo do `nabidka.html` jako inline SVG.
  **Spouštět po každé změně schémat**, jinak zůstane v nabídce stará kresba:
  `python3 bd-jandova/src/gen_schema.py && python3 bd-jandova/src/build_nabidka.py`
  Skript je idempotentní — obsah mezi značkami `<!--SCHEMA:1-->` … `<!--/SCHEMA:1-->` přepíše.
  Díky tomu je `nabidka.html` **soběstačný jediný soubor** bez externích odkazů.

## Tisk do PDF
Z běžícího náhledu (`python3 -m http.server 8000` z kořene repa) přes headless Chrome:

```
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CHROME" --headless=new --no-pdf-header-footer --virtual-time-budget=12000 \
  --print-to-pdf="$HOME/Downloads/BD-Jandova-cenova-nabidka.pdf" \
  "http://localhost:8000/bd-jandova/nabidka.html"
```

Přílohu A3 se schématem obou variant se tiskne přes dočasnou obálku s `@page{size:A3 landscape}`.
Interní blok se do PDF nedostane — skrývá ho tisková CSS (`.no-print`).

> **Dvě pasti, na které se přišlo při tisku:**
>
> 1. **Schéma přes `<img src="*.svg">` Safari při tisku nevykreslí** — v PDF zůstane
>    prázdné místo, i když na obrazovce je vidět. Proto jsou schémata v nabídce vložená
>    jako **inline `<svg>`** (viz `build_nabidka.py`). Nevracet zpět na `<img>`.
> 2. **SVG musí mít na kořeni `width`/`height`, ne jen `viewBox`** — bez nich některé
>    prohlížeče při tisku zkolabují výšku na nulu. Generátor je doplňuje.
>
> Tisková CSS drží **stejnou šířku sazby jako náhled** (796 px) a poměrově ji zmenší
> na tiskovou šířku A4 přes `zoom`. Mobilní breakpoint je proto omezený na
> `@media screen` — jinak by se na A4 (pod 760 px) sesypaly sloupce pod sebe.

## Zadání od klienta (vyúčtování Veolia)
Cena tepla **1 354 Kč/GJ s DPH** → **1 209 Kč/GJ bez DPH** (dodávka tepla, sazba 12 %).
Nabídka je celá vedená bez DPH.

| Položka | Spotřeba | Náklad bez DPH |
|---|---|---|
| Vytápění | 210 GJ · 58,3 MWh | 253 875 Kč |
| Ohřev TV | 231 GJ · 64,2 MWh | 279 263 Kč |
| **Celkem** | **441 GJ · 122,5 MWh** | **533 138 Kč** (597 114 Kč s DPH) |

> Pozn.: první verze nabídky počítala s 1 325 Kč/GJ jako cenou bez DPH (celkem 584 325 Kč).
> Klient 21. 9. 2026 upřesnil, že správná cena je 1 354 Kč/GJ **včetně** DPH.

Odběr TV 701 m³/rok · 17 bytových jednotek ·
tepelná ztráta **30 kW při −15 °C** (odhad ze spotřeby, k ověření výpočtem).

## Varianty
| | Varianta 1 | Varianta 2 (doporučena) |
|---|---|---|
| Zdroj | 1× REO X50 + el. bivalence | 2× REO X50 v kaskádě |
| Výkon při −15 °C | 25 kW | 50 kW |
| Cena bez DPH | 1 350 000 Kč | 1 600 000 Kč |
| Provozní náklady / rok | 174 600 Kč | 176 200 Kč |
| Roční úspora | 358 500 Kč | 356 900 Kč |
| Prostá návratnost | 3,8 roku | 4,5 roku |

Společné pro obě varianty: akumulace 2× 1 000 l, zásobníky TUV 3× 1 000 l,
ohřev TUV topnými hady přímo v zásobnících, kompletní strojovna, regulace a vzdálený dohled.

## Předpoklady propočtu
- SCOP **3,0** pro vytápění a **2,7** pro ohřev TV při teplotě otopné vody 55 °C.
  (Vstupní studie počítala u TV s 3,50 — pro nabídku sníženo, příprava TV běží na vyšší teploty.)
- Cena elektřiny 3 500 Kč/MWh, servis 15 000 Kč (V1) / 25 000 Kč (V2) ročně.
- U varianty 1 uvažováno **3 % roční potřeby tepla** dokrytých elektrickými patronami
  (odhad z průběhu venkovních teplot; 1 jednotka 25 kW proti souběhu ÚT 30 kW + TV ~7 kW).
- Bez inflace, bez dotace, bez nákladů na financování.

## Financování (pronájem TČ, servis v ceně splátky)
| | V1 / 60 měs | V1 / 120 měs | V2 / 60 měs | V2 / 120 měs |
|---|---|---|---|---|
| Vstupní investice | 950 000 Kč | 950 000 Kč | 800 000 Kč | 800 000 Kč |
| Měsíční splátka | 10 900 Kč | 8 900 Kč | 21 800 Kč | 17 800 Kč |
| Roční úspora | 242 700 Kč | 266 700 Kč | 120 300 Kč | 168 300 Kč |
| Odkup po skončení | 15 % | 1 Kč | 15 % | 1 Kč |

## ⚠️ Otevřené body (blokují finální nabídku)
1. **Splátkové podmínky a odkupní cena** — potvrdit s financující stranou (v nabídce orientačně).
2. **Rozpad ceny** na stavební část kotelny × tepelná čerpadla (950 000 / 800 000 Kč) je odhad.
3. **Sazba DPH** u bytového domu — potvrdit dle charakteru díla. SVJ obvykle není plátce DPH,
   takže reálně platí ceny s DPH. Ve srovnání s DPH (teplo i investice 12 %, elektřina
   a servis 21 %) vychází návratnost **3,9 roku (V1) / 4,7 roku (V2)**; při investici
   s 21 % DPH 4,2 / 5,0 roku.
4. **Rezervovaný příkon / hlavní jistič** — neověřeno, může být nutné posílení (není v ceně).
5. **Teplotní spád otopné soustavy** — ověřit, zda soustava zvládne 55 °C; jinak klesne SCOP.
6. **Podmínky ukončení odběru od Veolie** — výpovědní lhůta a poplatky za odpojení.
7. **Tepelná ztráta 30 kW** — potvrdit výpočtem, zatím odhad ze spotřeby.

## Zjištění k dalšímu prodeji
Na ohřev TV jde **231 GJ na 701 m³**, tj. ~91 kWh/m³ proti teoretickým ~52 kWh/m³ na ohřev
z 10 na 55 °C. Rozdíl **90–100 GJ ročně** (dnes ~120 000 Kč bez DPH) odchází ve ztrátách rozvodů
a cirkulace TV. Samostatná příležitost: izolace stoupaček + regulace cirkulace — řešitelné
nezávisle na výměně zdroje.

## Charakter podkladu
**Cenová nabídka a koncepční schéma — orientační podklad, nenahrazuje projektovou dokumentaci.**
Dimenze potrubí, armatury, výkony a rozsah MaR ověří autorizovaný projektant TZB podle
skutečné tepelné ztráty a měřených dat.
