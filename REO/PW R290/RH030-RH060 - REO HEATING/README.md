# RH030 – RH060 — návod k instalaci a obsluze (starší ovladač), REO HEATING

Česká verze originálního návodu výrobce `../Power World R290 Heat Pump User Manual.pdf` (11/2022, 50 stran),
v designu manuálu X30/Helios: originální layout, český text vysázený na místo anglického, logo REO HEATING na titulce.
Platí pro jednotky se **starším ovladačem**; pro novější panel vznikne samostatný návod z verze výrobce 2024
(`../../R290 new models/Power World New Version Software R290 Heat Pump.pdf`).

| Originál | REO HEATING |
|---|---|
| PW030-DKZLRS-E/S | RH030 (1fázové) |
| PW040-DKZLRS-E/S | RH040 (1fázové) |
| PW050-DKZLRS-E/S / -E | RH050 (1fázové / 3fázové) |
| PW060-DKZLRS-E | RH060 (3fázové) |
| BOM CP-RW… | RH-RW… |

Výstup: `RH030-RH060-navod-CZ_REO-HEATING.pdf` — je i v artefaktu „REO R290“ (https://claude.ai/artifact/EfdLeGPzZkM3H3RM4ZFTWR).

## Postup (složka `cz/`)
1. `extract.py` → `segments.json`, `chunks/` (odstavce a buňky k překladu)
2. překlad `cs/chunk_*.json` podle `PREKLAD-ZADANI.md` (terminologie, přeznačení modelů, věcné opravy originálu)
3. `icons_extract.py` → `icons.json`; značky ikon v textu jsou ručně v `cs_icons.json`
4. `build.py` → PDF. Ruční úpravy sazby v `OVERRIDE`, popisky v `CAPTIONS`, svislé popisky obr. 2 ve `FIG2`,
   rozpad dílů v `nahradni-dily.json`, úpravy obrázků v `IMG_EDITS` (graf ekvitermní křivky česky,
   snímek aplikace: název Wi‑Fi „pwjsb“ výrobce → „MojeWiFi“). Na konci build ověří, že v textu, metadatech
   ani surových datech PDF nezůstal odkaz na výrobce.

## Věcné opravy originálu
NEC/CEC → ČSN / EN; vlastnost „žádné riziko výbuchu/požáru“ přepsána (R290 je hořlavé); kód Er 20 „1–348“ → 1–384;
„high/low voltage switch“ = vysokotlaký/nízkotlaký spínač; přečíslování v kap. Údržba; „výrobce“ → „dodavatel“.

## K ověření (rozpory v originálu, přeloženo věrně)
- Sterilizace: kap. ovladače uvádí > 65 / ≤ 60 °C, kap. aplikace > 60 / ≤ 55 °C a konec „≥ 70 °C a 30 min ≥ 65 °C“.
- Topná vložka TBH, podmínka vypnutí „režim chlazení / TUV“ odporuje podmínce zapnutí (režim TUV).
- Rozsah automatické korekce teploty: 20–60 °C (ovladač) vs. 20–70 °C (aplikace).
- „Není nutná doplňková elektrická topná vložka“ (Hlavní vlastnosti) vs. kapitoly o přídavném ohřevu.
- Rozpad dílů RH050/RH060 pol. 9 a 20 „dlimp“ → přeloženo jako „Příchytka“.
