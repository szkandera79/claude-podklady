# Vzorová nabídka — zelená kotelna pro bytové domy, verze RHX30 Pro (25–100 kW)

Druhé provedení velké zelené kotelny: stejná struktura, grafika i předpoklady jako
`vzor-bytove-domy/` (jednotky RH X50), ale postavené na **RHX30 Pro** (REO R290 Smart, Pro řada).
Vzniklo 20. 10. 2026.

| | `vzor-bytove-domy/` (X50) | **tato verze (RHX30 Pro)** |
|---|---|---|
| Výkon jednotky při −15 °C / 50 °C | 25 kW | **20 kW** (19,0 W55 / 20,8 W45 / 22,4 W35) |
| Kaskáda | 1–4 jednotky (25–100 kW) | **1–5 jednotek** (25–100 kW) |
| Akustický výkon (W55) | 65 dB(A) | **59 dB(A)**, L_p 39–42 dB(A) v 1 m, noční režim 2 stupně |
| SCOP (EN 14825) | 4,57 / 3,21 (W35/W55) | **5,25 / 3,90** |
| SCOP_CZ model (W55) | 3,12 | **3,51** (v nabídce konzervativně 3,4) |
| FV přímo do jednotky | ne | **ano** (volitelná deska MPPT, bez střídače a baterie) |
| Cena sestavy | 1 350 / 1 600 / 1 990 / 2 380 tis. | **1 070 / 1 400 / 1 730 / 2 060 / 2 390 tis.** |

Zdroj dat: výkonová mapa výrobce a KEYMARK (`porovnani-x50-rh060/src/results2.json`),
akustika a FV z podkladů REO R290 Smart (`REO/PW Helios/REO R290 Smart/`).

## Dimenzování
Deficit do ~10 kW kryjí elektrické patrony v akumulaci; **nad 50 kW ztráty se deficit řeší další
jednotkou**. 25–30 kW → 1× (nebo 2× se zálohou), 30–50 → 2×, 50–70 → 3×, 70–90 → 4×, 90–100 → 5×.
Domy nad 100 kW se spíš hodí pro verzi s X50.

## Ceny (bez DPH) — odvozené, k potvrzení
Vnitřní část kotelny **740 000 Kč** (z nabídky s X50: 1 600 000 − 2 × 430 000) + **330 000 Kč**
za jednotku RHX30 Pro (ceník 2026, `porovnani-x50-rh060/src/navrh_kaskady.py`).
Splátky 8 400 / 6 800 Kč za jednotku = přepočet z BD Jandova poměrem 330/430 tis.

## Soubory
- `nabidka.html` — nabídka (tisk / PDF z prohlížeče, 10 stran A4); interní blok se netiskne.
- `schema-kaskada.svg` ← `src/gen_schema.py` (5 jednotek, TČ 3–5 přerušovaně);
  vložení do nabídky `src/build_nabidka.py`:
  `python3 vzor-bytove-domy-rhx30/src/gen_schema.py && python3 vzor-bytove-domy-rhx30/src/build_nabidka.py`
- `src/model.py` — propočet modelových domů A–D (30/50/70/90 kW); čísla v nabídce (sekce 6
  a shrnutí) jsou přepsaná ručně. Návratnost 2,3–3,5 roku při 1 209 Kč/GJ (Ostrava),
  3,2–4,9 roku při průměru ČR 967 Kč/GJ.
- `src/build_artefakt.py` — stránka artefaktu s tlačítkem na stažení PDF.

## Artefakt
https://claude.ai/artifact/2Q1NABF2A6MQ3H8VeK3t4t (soukromý, sdílí se přes Share).
Po změně nabídky: vytisknout PDF → `python3 vzor-bytove-domy-rhx30/src/build_artefakt.py <pdf> <výstup.html>`
→ publikovat na stejnou URL s `capabilities {"downloads": true}`.
Verze s X50: https://claude.ai/artifact/949jZkx8hZfEJrY5wXsMLx

## Tisk do PDF
```
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --no-pdf-header-footer \
  --print-to-pdf="$HOME/Downloads/ThermaVera-zelena-kotelna-RHX30-Pro.pdf" \
  "file://$PWD/vzor-bytove-domy-rhx30/nabidka.html"
```

## Otevřené body
1. **FV u Pro řady**: výrobce uvádí limity jen pro RH06–RH16 (250–600 V DC, 13 A, do 5,5 kWp).
   Pro RHX20/RHX30 Pro je v tabulkách nemá — potvrdit, než se budou slibovat počty panelů.
2. **Ceny sestav a splátky** jsou odvozené (viz výše), ne ceníkové.
3. **Výkon**: mapa výrobce vs. KEYMARK se u −10 °C liší (21,8 vs. 26,8 kW) — viz
   `porovnani-x50-rh060/README.md`.
4. **Akustika**: netvrdit „nejtišší na trhu“ (proti značkové konkurenci R290 to neplatí),
   srovnáváme jen s X50. Hygienické limity (NV 272/2011 Sb.) řeší akustická studie v projektu.
