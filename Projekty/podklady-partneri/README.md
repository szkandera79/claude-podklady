# Podklady REO HEATING pro projektanty a partnery

Stránka ke stažení všech prodejních a technických podkladů k REO R290 Smart a RHX Pro.
Artefakt **„Podklady REO HEATING“**: https://claude.ai/artifact/DdPrC4GgfPpeQUaSN36QUA (od 11. 11. 2026).
Stejnou sadu (+ e-mail projektantovi) obsahuje složka `~/Downloads/Projektant`.

## Obsah
- Ceník (`REO/PW Helios/REO R290 Smart/cenik/cenik.pdf`, ceny z eko4home.cz)
- Katalog Smart, technický list pro partnery, technická prezentace Smart + RHX Pro, instalační návod CZ
- Datové listy a energetické štítky ErP 8 nabízených modelů (RH06 1F, RH08–RH16 3F, RHX20/30 Pro)
- Katalog nerezových nádrží
- Pokyny k instalaci V2 (AKU + TUV) a H2 (hydrobox + AKU + TUV) — pozor, vznikly pro RH030–RH060

Zdroje jsou v projektech v `REO/` a `reo-schemata-zapojeni/`; PDF se sem nekopírují (velikost repa).

## Aktualizace
    python3 podklady-partneri/build.py <scratchpad>/podklady

Skript zkopíruje PDF do `soubory/`, ověří, že v žádném není odkaz na výrobce (Power World, Helios, typové kódy,
WK*), a vygeneruje `index.html`. Pak publikovat `index.html` + všechny `soubory/**` na stejnou URL artefaktu
(root = výstupní složka, capabilities `downloads`). Celkem ~52 MB, limit jednoho publish je 64 MB.

## Technické poznámky
- Rám artefaktu neumožňuje stahování odkazem → tlačítka používají schopnost `downloads` (fetch souboru + `save`).
  Kde není k dispozici (např. nepřihlášený prohlížeč), stránka zobrazí výzvu napsat na info@reoheating.cz.
- Artefakt neservíruje `.zip` → ZIP datových listů / štítků skládá prohlížeč (JSZip 3.10.1 z cdnjs).
- Artefakt je soukromý; pro partnery ho sdílet přes Share (odkaz). Ceník obsahuje koncové ceny — partnerské podmínky jen na vyžádání.
