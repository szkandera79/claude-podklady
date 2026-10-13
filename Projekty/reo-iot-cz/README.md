# Reo Heating – IOT CZ

Servisní a diagnostická nadstavba (rozšíření Google Chrome) nad platformou **IOT Power World**
(`http://162.62.225.58/`): český překlad, encyklopedie parametrů, databáze chyb a diagnostický
asistent. Interní nástroj servisu Reo Heating. Úplné zadání: [PROJECT_BRIEF.md](PROJECT_BRIEF.md).

Navázání v nové relaci: **„Pokračujeme v projektu IOT CZ.“**

## Dokumenty
| Soubor | Obsah |
|---|---|
| [PROJECT_BRIEF.md](PROJECT_BRIEF.md) | úplné zadání (závazné) |
| [docs/ARCHITEKTURA.md](docs/ARCHITEKTURA.md) | moduly, struktura složek, úrovně důvěryhodnosti V/O/H/R, tok dat |
| [docs/BEZPECNOST.md](docs/BEZPECNOST.md) | read-only pravidla, oprávnění, co nesmí do gitu, anonymizace snímků |
| [docs/TESTOVANI.md](docs/TESTOVANI.md) | automatické, bezpečnostní a ruční testy |
| [docs/POWER-WORLD-AI.md](docs/POWER-WORLD-AI.md) | prověření AI diagnostiky Power World (zatím nepotvrzena) |
| [podklady/](podklady/README.md) | **mimo git** — manuály PDF, surové snímky obrazovky |

## Stav etap
| Etapa | Obsah | Stav |
|---|---|---|
| 0 | Architektura, bezpečnost, testy, rešerše AI Power World | ✅ hotovo 2026-10-13 |
| 1 | Analýza IOT + česká lokalizace | ⏳ čeká na snímky obrazovky |
| 2 | Encyklopedie parametrů | — |
| 3 | Import manuálů + databáze chyb | — |
| 4 | Diagnostický asistent (ruční data, bez externí AI) | — |
| 5 | Posouzení autorizovaného napojení na IOT | — (jen se souhlasem Power World) |

## Co je potřeba od uživatele (etapa 1)
1. **Anonymizované snímky obrazovky IOT** (postup v [BEZPECNOST.md §5](docs/BEZPECNOST.md)) → `podklady/snimky/`:
   přihlášení, seznam/vyhledání zařízení, detail zařízení online, všechny záložky s parametry,
   servisní nastavení (jen zobrazit, neukládat), stránka s chybou/alarmem, případně historie/grafy.
2. Ke každému snímku: o jaký model / řídicí jednotku jde (RH030–RH060 starší panel, nový panel,
   R290 Smart, RH X50…).
3. Případně uložená stránka (Chrome → Soubor → Uložit stránku jako… „Pouze HTML“) jedné obrazovky
   s parametry — pomůže přesně zjistit strukturu; před předáním anonymizovat.

## Dokumentace Power World — co už máme (v `../REO/`)
- `PW R290/Power World R290 Heat Pump User Manual.pdf` (RH030–RH060, starší řídicí jednotka)
- `R290 new models/Power World New Version Software R290 Heat Pump.pdf` (nový panel)
- `PW Helios/aTechnical Manual Helios Residential and Commercial.pdf` (REO R290 Smart)
- `RH X50 komerční/PW_R290_Commercial_Heat_Pump_Technical_Manual_20250520 cs.pdf`, `R32 Easylife Plus-TECHNICAL MANUAL…`

Chybí zejména: **servisní manuály, kompletní seznamy chybových kódů po řídicích jednotkách,
elektrická schémata, dokumentace k IOT platformě**.

## Rozhodnutí
- 2026-10-13: projekt je složka v `Projekty` (auto-sync na GitHub); neveřejné materiály v `podklady/` mimo git.
- 2026-10-13: verze 1–4 bez jakékoli síťové komunikace; diagnostika = pravidla + dokumentace.
- Rozšíření je interní nástroj — Power World se v něm zmiňovat smí. Kdyby se cokoli z něj
  použilo pro zákazníky, platí pravidlo značky REO HEATING (žádné odkazy na výrobce).

## Otevřené body
- Název firmy v UI: „Real Heating“ vs. „Reo Heating“ (v zadání obojí) — upřesnit.
- IOT běží na holé IP přes **nešifrované HTTP** → heslo jde sítí nechráněné; doporučit dotaz na Power World, zda existuje HTTPS adresa.
- Dotaz na Power World (AI, API, souhlas s rozšířením) — text v [POWER-WORLD-AI.md](docs/POWER-WORLD-AI.md).
