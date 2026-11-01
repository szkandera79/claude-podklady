# Schémata zapojení TČ — REO HEATING (pro kutily)

Jednoduchá, přehledná schémata zapojení tepelného čerpadla s číslovanými popisky,
seznamem součástí a krátkým „jak to funguje“. Značka REO HEATING (logo z `~/Claude/REO/logo`).

| Soubor | Obsah |
|---|---|
| `schema-kuncice-aku100.svg` / `.png` | **Kunčice p. O., schéma 1 „Schéma hydraulického zapojení“** (pouze vytápění) — AKU 100 l (topná voda) + venkovní jednotka; uzávěr před separátorem na výstupu, uzávěr + protizámrazový ventil na vratce; pojistná skupina (pojistný ventil + manometr) a expanzní nádoba na stoupačce výstupu do topení za čerpadlem; generátor `src/gen_schema_kuncice.py` |
| `kuncice/index.html` | popis instalace (venku / uvnitř) s fotkami z realizace, artefakt S9apdYbzv8x7RiMdabc8xK |
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
- Kunčice: elektrická část schématu (napájení TČ z rozvaděče „R.AC TČ“, čerpadlo + přijímač, čidlo AKU, ovladač TČ).
- Kunčice schéma 2: přidat zásobník TUV (velký zásobník na fotkách) — až bude schéma 1 schválené.
- Další varianty (TUV, bivalence, FV) — doplnit jako `schema-varianta-N`.
