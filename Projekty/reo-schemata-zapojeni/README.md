# Schémata zapojení TČ — REO HEATING (pro kutily)

Jednoduchá, přehledná schémata zapojení tepelného čerpadla s číslovanými popisky,
seznamem součástí a krátkým „jak to funguje“. Značka REO HEATING (logo z `~/Claude/REO/logo`).

| Soubor | Obsah |
|---|---|
| `schema-kuncice-aku100.svg` / `.png` | **Kunčice p. O., schéma 1 „Schéma hydraulického zapojení“** (pouze vytápění) — AKU 100 l (topná voda) + venkovní jednotka; uzávěr před separátorem na výstupu, uzávěr + protizámrazový ventil na vratce; pojistná skupina (pojistný ventil + manometr) a expanzní nádoba na stoupačce výstupu do topení za čerpadlem; magnetický filtr na vratce do TČ v technické místnosti (= filtr na vstupu dle návodu); TČ řídí podle vestavěného čidla vratné vody (vstup pro čidlo AKU nemá); generátor `src/gen_schema_kuncice.py` |
| `schema-kuncice-elektro.svg` / `.png` | Kunčice — schéma elektrického zapojení (dle návodu RH030–RH060: napájení 1F/3F, svorkovnice 1–6, rozvaděč TČ, přijímač → čerpadlo); `src/gen_schema_kuncice_elektro.py` |
| `schema-kuncice-patka.svg` / `.png` | Kunčice — betonová patka venkovní jednotky (2 ramena ze ztraceného bednění 200 × 500+ mm, osově 700, od stěny min. 400, doporučeno 500, výška 300+); `src/gen_patka_kuncice.py` |
| `schema-kuncice-tuv.svg` / `.png` | Kunčice — schéma 2: vytápění s AKU + TUV (trojcestný ventil, zásobník se spirálou, čidlo T2, SV/TV s pojistným ventilem a exp. nádobou TUV); `src/gen_schema_kuncice_tuv.py` |
| `kuncice/soupis-komponent.csv` | soupis komponent pro schéma 1 (generuje `src/soupis_kuncice.py`, zároveň vloží tabulku do stránky) |
| `kuncice/index.html` | popis instalace (venku / uvnitř) s fotkami z realizace, artefakt S9apdYbzv8x7RiMdabc8xK |
| `pokyny/` | **Pokyny k instalaci (bez hydroboxu)** — V1 vytápění s AKU, V2 AKU + TUV; PDF `REO-pokyny-instalace-V1-AKU.pdf`, `…-V2-AKU-TUV.pdf`; artefakty B1kNm4rR3A56NZ8vBEAeGU (V1), DC42DpVfQhRrkwxdTvX1xN (V2); build `src/build_pokyny.py` (po vygenerování schémat a PNG) |
| `schema-kuncice-elektro-tuv.svg` / `.png` | elektrické schéma s TUV (`gen_schema_kuncice_elektro.py --tuv`) |
| `schema-varianta-1.svg` / `.png` | **Varianta 1** (REO RH030–RH060) — pouze vytápění s akumulační nádrží; sekundární čerpadlo za AKU spíná bezdrátový termostat |

Varianta 1 obsahuje: uzavírací ventily u venkovní jednotky (výstup i vratka), protizámrazový ventil Caleffi na vratce,
separátor s odvzdušňovacím a pojistným ventilem venku hned za jednotkou (bezpečný únik vzduchu i případně uniklého R290), AKU, expanzní nádobu,
sekundární čerpadlo s uzávěry, přijímač (relé) + bezdrátový termostat, čidlo AKU → řízení TČ.

## Build
```
python3 reo-schemata-zapojeni/src/gen_schema.py
```
PNG (2800 px) přes Chrome headless — příkaz viz historie / `REO/logo/build.sh` (stejný postup).

## Otevřené
- **Další fáze: verze s hydroboxem** (V1 jen topení s AKU, V2 s TUV) — podle návodu `~/Downloads/REO_HEATING__Hydro_Box_installation_manual_CZ.pdf` a fotky instalace (hydrobox na zdi, AKU, zásobník TUV, exp. nádoby).
- Kunčice: elektrické schéma pro TUV (svorka 3 trojcestný ventil, svorka 1 vložka, čidlo T2) — zatím jen v textu.
- Další varianty (TUV, bivalence, FV) — doplnit jako `schema-varianta-N`.
