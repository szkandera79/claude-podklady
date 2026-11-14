# Instalační standard REO HEATING – REO R290 Smart

Metodika pro projektanty a montážní party: hydraulická zapojení, regulace komfortní teploty, elektrické
zapojení, parametry a uvedení do provozu pro TČ REO R290 Smart (RH06–RH16, RHX20 Pro, RHX30 Pro).

Artefakt: https://claude.ai/artifact/4Fbg3QirxjmtSv7dCop8oH (verze 3 = standard v1.0; verze 1–2 = návod rev. 0).
Soukromý – partnerům sdílet přes menu Share.

**Stav:** koncepce schválena uživatelem 14. 11. 2026, standard v1.0 vydán týž den.
Údaje jsou značeny V (výrobce), O (odborný závěr REO), ? (k ověření).

## Katalog zapojení
| Označení | Stav | Obsah |
|---|---|---|
| SM-P1 v1.0 | standard | podlaha + sériová AKU ve vratce, R-A (1ZONE.TA) / R-B termostat |
| SM-P2 v1.0 | standard | podlaha + paralelní AKU + P_O, termostat L1–C1 |
| SM-R1 v1.0 | standard | radiátory s TRV + paralelní AKU + P_O (ze S3 rev. 0) |
| SM-R2 v1.0 | alternativa | radiátory + sériová AKU (ze S2 rev. 0) |
| SM-K1 v1.0 | doplňková | radiátory + směšovaná podlaha, RT_CTRL = 2 ZONE.SWITCH (ze S4 rev. 0) |
| SM-X1 v0.9 | podmíněné | oddělení deskovým výměníkem (glykol primár) |
| SM-E1 v1.0 | – | elektrické zapojení svorek (z E1 rev. 0) |
| SM-P0 | nepřípustné | podlaha bez AKU = S1 rev. 0, jen reference (výrobce AKU požaduje) |

## Soubory
| Soubor | Obsah |
|---|---|
| `index.html` | standard v1.0 – sestaví `src/build_metodika.py` z `src/metodika.template.html` |
| `schema-SM-*.svg/.png` | schémata v1.0 – `src/gen_sm.py` |
| `schema-S1…S4, E1 .svg/.png` | **referenční rev. 0, neměnit** – `src/gen_schemata.py` |
| `navod-rev0.html` | návod rev. 0 (reference) – `src/build.py` z `src/navod.template.html` (CSS a skript sdílí i metodika) |
| `src/symboly.py` | knihovna symbolů (kopie z `reo-schemata-zapojeni`) |

## Build (z kořene repozitáře)
```
python3 reo-smart-regulace/src/gen_sm.py
zsh reo-smart-regulace/src/render.sh
python3 reo-smart-regulace/src/build_metodika.py
```
Publikace: Artifact `index.html` + `files` = všechna schema-*.svg (stejná URL).

## Změny v1.0 proti rev. 0
- Zpětný ventil na výstupu TČ (prvek 26) – návod 2.8.2 bod 6; v rev. 0 chyběl.
- Bez AKU nepřípustné (příručka 4.4 „must install a buffer“).
- SV1 při odmrazování přepíná na TUV (příručka 6.2.6) → opraveno zdůvodnění sériové AKU.
- PANEL_CTRL jen bez termostatu, RT_CTRL s termostatem (návod 4.2.5–4.2.6).
- Radiátory s TRV: standard paralelní AKU; podlaha: sériová AKU.
- Polarita SV1 se liší (návod TUV = VYP, příručka TUV = ON) → ověřit testem komponent.

## Ověřená fakta (výrobce)
PUMPo/P_O = externí čerpadlo zóny A (dodávka stavby), za paralelní AKU; termostat C1–L1 spíná systém i P_O;
při TUV P_O stojí; výstupy 230 V max. 0,2 A; čidla T9 AI6B, T8 AI3, T7 AI2, T10 AI6C, T5 AI0, T20 AI6A;
AKU 60–400 l; průtok 1,46–5,2 m³/h, ztráta 30–60 kPa, výtlak 9–15 m; křivka vypnutá a HEAT_TEMP_SET 45 °C z výroby.

## Otevřené (dotaz výrobci, kap. 15 standardu)
Bez AKU a min. objem; řízení a křivka vestavěného čerpadla; SV1 při odmrazování a polarita; teplota vody v 1ZONE.TA;
glykol (rozpor 4.1 × 4.10); min. průtok; kabel ovladače; napětí L1/L2, rozsah ROOM_TEMP_dT; signál TMV1, aktivace T8/T7;
AKU pro RHX, spirála RH16. Výsledky z uvedení do provozu (SV1 při ručním odmrazování, křivka v TA) zapisovat sem.
