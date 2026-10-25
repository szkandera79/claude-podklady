# Schémata zapojení TČ — REO HEATING (pro kutily)

Jednoduchá, přehledná schémata zapojení tepelného čerpadla s číslovanými popisky,
seznamem součástí a krátkým „jak to funguje“. Značka REO HEATING (logo z `~/Claude/REO/logo`).

| Soubor | Obsah |
|---|---|
| `schema-varianta-1.svg` / `.png` | **Varianta 1** — pouze vytápění s akumulační nádrží; sekundární čerpadlo za AKU spíná bezdrátový termostat |

Varianta 1 obsahuje: uzavírací ventily u venkovní jednotky (výstup i vratka), protizámrazový ventil na vratce,
separátor vzduchu a nečistot s odvzdušňovacím a pojistným ventilem na výstupu, AKU, expanzní nádobu,
sekundární čerpadlo s uzávěry, přijímač (relé) + bezdrátový termostat, čidlo AKU → řízení TČ.

## Build
```
python3 reo-schemata-zapojeni/src/gen_schema.py
```
PNG (2800 px) přes Chrome headless — příkaz viz historie / `REO/logo/build.sh` (stejný postup).

## Otevřené
- Další varianty (TUV, bivalence, FV) — doplnit jako `schema-varianta-N`.
