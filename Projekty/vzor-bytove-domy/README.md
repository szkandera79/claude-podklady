# Vzorová nabídka — zelená kotelna pro bytové domy (25–100 kW)

Obecná nabídka k rozesílání SVJ / bytovým družstvům, vzniklá zobecněním nabídky
**BD Jandova 7** (`bd-jandova/`). Bez jména klienta a bez adresy.

## Princip dimenzování
- Modul = **REO X50: 25 kW při −15 °C a výstupu 50 °C**. Výkon se skládá kaskádou 1–4 jednotek.
- Deficit do ~10 kW kryjí elektrické patrony v akumulaci (≈ 3 % roční potřeby tepla).
- **Tepelná ztráta nad 60 kW → deficit řešíme další jednotkou**, ne elektřinou.

| Tepelná ztráta | Jednotky | Výkon −15 °C | Cena od (bez DPH) |
|---|---|---|---|
| 25–35 kW | 1 (nebo 2 se zálohou) | 25 / 50 kW | 1 350 000 / 1 600 000 Kč |
| 35–60 kW | 2 | 50 kW | 1 600 000 Kč |
| 60–85 kW | 3 | 75 kW | 1 990 000 Kč |
| 85–100 kW | 4 | 100 kW | 2 380 000 Kč |

Každá třetí a další jednotka = **+390 000 Kč** (platí i pro dodatečné rozšíření).

## Soubory
- **`nabidka.html`** — vzorová nabídka (tisk / PDF z prohlížeče), soběstačný jeden soubor.
  Interní blok „před prvním rozesláním ověřit" se netiskne.
- **`schema-kaskada.svg`** — koncepční schéma modulární kaskády (TČ 3 a 4 přerušovaně).
- **`src/gen_schema.py`** → generuje schéma; **`src/build_nabidka.py`** → vloží ho inline do nabídky:
  `python3 vzor-bytove-domy/src/gen_schema.py && python3 vzor-bytove-domy/src/build_nabidka.py`
- **`src/model.py`** — propočet modelových scénářů (domy A–D: 30/55/75/95 kW). Čísla jsou v nabídce
  přepsaná ručně (sekce 4 a 5) — po změně předpokladů srovnat.

## Předpoklady modelových scénářů
Vytápění = ztráta × 2 000 h, TUV = 70 % vytápění, CZT 1 209 Kč/GJ bez DPH (Ostrava, ERÚ 2026 = 1 354 s DPH), SCOP 3,0 (ÚT) / 2,7 (TUV),
elektřina 3 500 Kč/MWh, servis 15 000 Kč + 10 000 Kč za každou další jednotku. Vychází 2,5–4,5 roku
návratnosti **proti CZT** — u domů s vlastní plynovou kotelnou je úspora výrazně nižší
(v nabídce ošetřeno boxem „Kdy vyjde úspora nižší").

## Ceny tepla CZT (sekce 5)
Průměry ČR podle úrovně dodávky z předběžného ceníku ERÚ k 1. 1. 2026 (vážené množstvím, přepočteno na bez DPH ÷ 1,12):
domovní předávací stanice 967, sekundární rozvod 944, bloková kotelna 910, domovní kotelna 828 Kč/GJ.
Modelové domy A–D mají návratnost uvedenou pro Ostravu 1 209 Kč/GJ (4,5 / 2,9 / 2,6 / 2,5 roku) i pro průměr ČR 967 Kč/GJ (6,5 / 4,2 / 3,7 / 3,5 roku).
Při novém ceníku ERÚ (vychází k 1. 1.) čísla aktualizovat.

## Artefakt „Zelená kotelna – vzor"
Webová verze nabídky: https://claude.ai/artifact/949jZkx8hZfEJrY5wXsMLx (soukromá, sdílí se přes Share).
Je to `nabidka.html` bez interní poznámky (jen `<title>`, `<style>` a obsah `<body>`). Po změně nabídky
artefakt znovu publikovat na stejnou URL. Artefakt **nemá tlačítko tisku** — sandboxovaný iframe blokuje `window.print()` i otevření
přiloženého PDF v nové záložce (ověřeno 9/2026). Místo toho má **tlačítko „Stáhnout nabídku v PDF"**:
publikuje se s `capabilities: {"downloads": true}` a PDF je v stránce vložené jako base64 konstanta
`PDF_B64`, kterou tlačítko předá `claude.use('downloads').save(...)`. Při každé změně nabídky je proto
nutné **nejdřív vygenerovat nové PDF** a teprve pak publikovat artefakt:
`python3 vzor-bytove-domy/src/build_artefakt.py <pdf> <výstup.html>` → publikovat na stejnou URL s `capabilities {"downloads": true}`. Přehled cen tepla CZT 2026: https://claude.ai/artifact/56cq7XoAz7XYuJKZjdPnVr

## Tisk do PDF
Stejně jako u BD Jandova (viz `bd-jandova/README.md`, včetně dvou pastí se SVG):
```
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --no-pdf-header-footer \
  --print-to-pdf="$HOME/Downloads/ThermaVera-vzorova-nabidka-bytove-domy.pdf" \
  "file://$PWD/vzor-bytove-domy/nabidka.html"
```
Aktuální rozvržení = 9 stran A4, struktura jako BD Jandova: karty sestav (sekce 4), ceny tepla ERÚ + modelové domy (sekce 5), biomasa a teplo jako služba (sekce 7), schéma (sekce 8), shrnutí + podpis na poslední straně.

## Biomasa a teplo jako služba (sekce 7)
Na přání doplníme nebo nahradíme TČ kotlem na biomasu s vlastním zásobníkem paliva; palivo klientům
dodáváme a o provoz se staráme. Alternativně „teplo jako služba": kotelnu postavíme, vlastníme a provozujeme,
SVJ platí za GJ podle smlouvy. V nabídce zatím **bez cen**.

## Otevřené body
1. Ověřit, zda příplatek 390 000 Kč za 3. a další jednotku pokrývá i větší AKU/TUV z ceníku.
2. Splátky 10 900 / 8 900 Kč za jednotku (převzato z BD Jandova) — potvrdit s financující stranou.
3. Výkon REO X50 25 kW při −15 °C / 50 °C ověřit proti výkonovému listu.
4. Ceník biomasy (kotle, zásobníky paliva, cena paliva) a podmínky tepla jako služby; ověřit potřebu licence ERÚ při prodeji tepla.
