# Regulace komfortní teploty – REO R290 Smart

Návod pro projektanty a montážní party: jak u TČ REO R290 Smart (RH06–RH16, RHX20 Pro, RHX30 Pro)
řídit vnitřní (komfortní) teplotu domu – ekvitermní křivka #9 + prostorová teplota z ovladače / pokojový
termostat / zóny. Schémata s AKU i bez AKU, elektrické zapojení svorek, montážní postup, parametry.

Artefakt: https://claude.ai/artifact/4Fbg3QirxjmtSv7dCop8oH (soukromý – sdílet přes menu Share)

Zdroj: `~/Claude/REO/PW Helios/REO R290 Smart/REO-R290-Smart_navod-CZ.pdf` (kap. 2.7 aplikace, 2.10 schéma
zapojení, 3.3 ovladač, 3.3.21–22 křivky, 4.2 pokročilé nastavení) + instalační příručka výrobce (kap. 4.3–4.4
čerpadlo, AKU 60–400 l). Názvy výrobce v podkladech nepoužívat.

| Soubor | Obsah |
|---|---|
| `index.html` | návod (artefakt), sestaví `src/build.py` z `src/navod.template.html` + logo |
| `schema-S1.svg/.png` | bez AKU – podlahové vytápění, `1ZONE.TA` |
| `schema-S2.svg/.png` | sériová AKU ve vratce – radiátory (doporučeno pro většinu RD) |
| `schema-S3.svg/.png` | paralelní AKU + sekundární čerpadlo P_O přes relé, termostat L1–C1 |
| `schema-S4.svg/.png` | 2 zóny: radiátory + podlaha přes směšovací ventil TMV1, P_M1, T10 |
| `schema-E1.svg/.png` | svorky řídicí desky: napájení, SG/EVU, ovladač, H1/L1/C1/L2/H2, výstupy, čidla, RS485 |
| `src/symboly.py` | knihovna symbolů (kopie z `reo-schemata-zapojeni`) |

## Build (z kořene repozitáře)
```
python3 reo-smart-regulace/src/gen_schemata.py
zsh reo-smart-regulace/src/render.sh        # PNG 2800 px přes Chrome headless
python3 reo-smart-regulace/src/build.py
```
Publikace: Artifact s `files` = schema-*.svg (stejná cesta index.html → stejná URL).

## Klíčová zjištění z návodu
- `PANEL_CTRL`: 1ZONE.TW (voda) / 1ZONE.TA (prostorová teplota z čidla v ovladači) / 2ZONE.TW / 2ZONE.TW&TA / 3ZONE.TW / 3ZONE.TW&TA.
- `RT_CTRL`: OFF / ZONE.A.MODE.SW (H1 topení, C1 chlazení) / ZONE.A.SWITCH (L1–C1) / 2 ZONE.SWITCH (+L1–H1) / 3 ZONE.SWITCH (+L2–H2).
- `ROOM_TEMP_dT`: start TS−TR ≥ dT, stop TR ≥ TS. Při termostatu TČ reguluje jen teplotu vody.
- Přednastavené křivky jsou ploché (1.L–8.L ≈ 24–38 °C, 1.H–8.H ≈ 36–56 °C) → používat křivku #9 (2 body).
- Čidla: T9 AI6B TUV (v dodávce, ~10 m), T8 AI3 AKU nahoře, T7 AI2 AKU dole, T10 AI6C podlaha B1, T5 AI0 podlaha B2, T20 AI6A TWout3.
- Výstupy 230 V max. 0,2 A → relé/stykač. SG konfig. 7: EVU=1 omezení, 0/0 normál, SG=1 přebytek (jen TUV + powerful).

## Otevřené (ověřit u výrobce)
Číslování parametrů křivek (20/21 vs 26/27), aktivace a funkce čidel AKU, křivka při 1ZONE.TA, napětí na L1/L2,
délka kabelu ovladače, signál TMV (AIV/AOV), rozsah ROOM_TEMP_dT, objem AKU pro RHX20/30 Pro.
