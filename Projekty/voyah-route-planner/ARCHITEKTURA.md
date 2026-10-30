# Architektura (etapa 2) — Voyah Smart Route Planner

Navazuje na [ANALYZA.md](ANALYZA.md). Stav 30. 10. 2026: **hotové výpočetní jádro (`backend/vrp`) a datová vrstva
(`backend/vrp_data`), 46 testů, plánování z příkazové řádky funguje na skutečných datech.** Zbývá API a PWA.

## Moduly

```
backend/
  vrp/                    výpočetní jádro — čistý Python, žádné I/O, deterministické
    models.py             datový model (Vehicle, ChargingCurve, Segment, Route, Station, Tariff, EnergyParams, PlanParams)
    charging.py           doba a cena nabíjení: min(křivka vozu × teplota baterie, výkon stanice)
    energy.py             energetický model úseků, jízdní profily, kumulativní profil trasy
    optimizer.py          DP nad (uzel, SoC %), režimy nejrychlejší / nejlevnější / vyvážený, varianty
    trip.py               aktivní cesta: ruční SoC → k_trip → přepočet + varování
    calibration.py        dlouhodobá kalibrace k(skupina silnic, teplotní pásmo), odhad kapacity
  tests/                  scénáře s SYNTETICKÝMI stanicemi (jen testy)
  vrp_data/               datová vrstva (jen standardní knihovna Pythonu, disková cache ~/.cache/voyah-route-planner)
    config.py             klíče z ~/.config/voyah-route-planner/.env (mimo iCloud a git)
    http.py               HTTP + cache; záloha přes curl kvůli starému TLS v systémovém Pythonu macOS
    geocode.py            adresa → souřadnice (Photon / OSM, bez klíče)
    routing.py            openrouteservice → Route; při výpadku OSRM + převýšení z Open-Meteo Elevation
    osm.py                nabíječky CCS2 z OpenStreetMap (Overpass, dlaždice 1°, zrcadla, cache 7 dní) — HLAVNÍ ZDROJ
    ocm.py                Open Charge Map podél trasy — doplněk (stav, datum ověření, cena), kontrola licence poskytovatele
    chargers.py           sloučení OSM+OCM (do 150 m), koridor 5 km, odhad zajížďky
    operators.py          sjednocení názvů provozovatelů (Pražská energetika → PRE …)
    weather.py            Open-Meteo: teplota, protivítr, povrch v hodině průjezdu
    planner.py            adresa → trasa → počasí → nabíječky → plány ve 3 režimech
    cli.py                python -m vrp_data.cli "Ostrava" "Praha" --soc 60
  — další krok —
  api/                    FastAPI: /plan, /trip/{id}/soc, /settings, /history; SQLite
frontend/                 React + TypeScript + Vite PWA, MapLibre + OpenFreeMap
```

Jádro nezná zdroj dat: router, databáze nabíječek i počasí se mapují na `Route` / `Station`. Výměna ORS → Valhalla
nebo přidání NAP (AFIR) proto nezasáhne optimalizátor ani testy.

## Datový model (hlavní entity)

| Entita | Klíčová pole |
|---|---|
| `Vehicle` | využitelná kapacita (100 kWh), účinnost nabíjení (0,95), hmotnost, konektor CCS2, `ChargingCurve` |
| `ChargingCurve` | body (SoC %, kW na straně stojanu): 0→60❓, 10→89, 80→89, 81→40, 90→40, 91→20, 100→20 (nad 80 % dle uživatele 30. 10.) |
| `Segment` | délka, třída silnice, rychlostní limit, převýšení, teplota, protivítr, povrch |
| `Station` | operátor, poloha na trase (km), max. kW, zajížďka km/min, počet bodů, konektory, přístupnost, zdroj a stáří dat, živý stav |
| `Tariff` | Kč/kWh s DPH, Kč/min, poplatek za relaci, blokovací poplatek, preferovaná, členství, priorita |
| `PlanParams` | start SoC, rezervy (10 / 15 %), profil jízdy, režim, konzervativní režim, hodnota času, jen preferované, min. výkon stanice |
| `Plan` | zastávky (příjezd → odjezd %, minuty, kWh, Kč, další úsek), jízda / nabíjení / celkem, SoC v cíli, cena, varování |

Databáze (SQLite přes SQLAlchemy, etapa 3c): `settings` (JSON vozidla, tarifů, parametrů), `stations_cache`
(OCM, s datem importu a licencí poskytovatele), `trips`, `soc_readings`, `calibration_cells`, `observations`.

## API (návrh kontraktu)

| Metoda | Účel |
|---|---|
| `POST /api/plan` | {start, cíl, průjezdní body, SoC, rezerva, profil, režim} → varianty A/B/C s plány |
| `POST /api/trips` | uloží zvolený plán jako aktivní cestu |
| `POST /api/trips/{id}/soc` | {SoC, GPS} → promítnutí na trasu, `soc_update`, nový plán + varování |
| `POST /api/trips/{id}/finish` | konec cesty → kalibrační pozorování |
| `GET/PUT /api/settings` | vozidlo, křivka, tarify, rezervy, profily |
| `GET /api/stations?bbox=` | nabíječky pro mapu (s atribucí zdroje) |

API klíče (ORS, OCM) jen v `.env` na serveru; frontend volá výhradně vlastní backend.

## Ověřené vlastnosti jádra (testy)

| # | Scénář | Test |
|---|---|---|
| 1 | bez nabíjení | `test_reachable_without_charging` |
| 2 | jedna zastávka | `test_one_stop` |
| 3 | více zastávek | `test_multiple_stops` |
| 4 | dálnice léto (25 kWh @ 125 km/h) | `test_summer_motorway_matches_user_value` |
| 5 | dálnice zima (složené koeficienty) | `test_winter_motorway_composed_of_factors` |
| 6 | okresní silnice (17,5 @ 90) | `test_district_road_90` |
| 7 | výpadek stanice | `test_station_outage_replans` |
| 8 | ruční SoC během cesty | `test_soc_update_on_prediction` |
| 9 | výrazně vyšší spotřeba | `test_much_higher_consumption_warns_and_replans` |
| 10 | do 80 % vs. nad 80 % | `test_charging_above_80_when_it_saves_a_costly_stop`, `test_two_short_stops_beat_…` |
| 11 | 100 vs. 250 kW | `test_station_power_above_car_limit_gives_no_gain` |
| 12 | preferovaný operátor | `test_preferred_operator_in_balanced_mode`, `test_preference_is_not_absolute_…` |
| 13 | chybí data o nabíječkách | `test_no_charger_data` |
| 14 | žádná dosažitelná nabíječka | `test_gap_without_reachable_charger` |
| + | záznam PRE 22. 1. 2026 | `test_reproduces_pre_record` (model 24,8 min / 36,8 kWh vs. skutečnost 23,6 min / 35,4 kWh) |
| + | režim nejlevnější, konzervativní režim, zajížďky, varianty profilů, kalibrace, odlehlé hodnoty | ostatní testy |

Výkon: trasa 1 500 km se 60 kandidátními stanicemi ≈ 0,1 s.

## Pokrytí nabíječek (ověřeno 30. 10. 2026, ČR, CCS2)

| Zdroj | Stanic | Poznámka |
|---|---|---|
| OpenStreetMap | 901 | ČEZ 367, E.ON 169, PRE 153, Lidl 49, Tesla 12; výkon uveden u 56 % |
| Open Charge Map | 232 | jen Tesla 3, Lidl 7; část záznamů ověřena naposledy 2016–2021 |

Proto je hlavním zdrojem OSM, OCM doplňuje. Chybějící výkon se počítá konzervativně 50 kW (s upozorněním).

## Příklad (skutečná data, 30. 10. 2026 večer, OSRM záloha)

`Ostrava → Praha, start 60 %`: 376 km, 196 nabíječek v koridoru. Nejrychlejší: 4 h 18 min (jízda 3 h 25 min,
nabíjení 45 min), ČEZ futurego km 130 (25→49 %) + IONITY km 254 (10→50 %), v cíli 15 %, ~1 280 Kč.
Nejlevnější: Lidl, 4 h 53 min, ~663 Kč. Vyvážený: 2× PRE, 4 h 26 min, ~800 Kč.

## Plánování z příkazové řádky

```bash
cd voyah-route-planner/backend && ~/.venvs/voyah-route-planner/bin/python -m vrp_data.cli "Ostrava" "Praha" --soc 60
```

## Spuštění testů

```bash
python3 -m venv ~/.venvs/voyah-route-planner && ~/.venvs/voyah-route-planner/bin/pip install pytest
```

```bash
cd voyah-route-planner/backend && ~/.venvs/voyah-route-planner/bin/python -m pytest -q
```

Virtuální prostředí je mimo iCloud (`~/.venvs/`), aby se nesynchronizovaly tisíce souborů.

## Známá omezení jádra

- SoC se mezi uzly zaokrouhluje dolů (konzervativně, ≤ 1 % na úsek).
- Model nabíjení je o ~5 % pomalejší než záznam PRE → využitelná kapacita je možná blíž 96 kWh; zpřesní kalibrace z dalších nabíjení.
- Křivka pod 10 % je předpoklad (❓); nad 80 % dle zkušenosti uživatele (40 kW do 90 %, pak ~20 kW), ne z měřeného záznamu.
- Důsledek křivky: 10→80 % ≈ 50 min, 80→90 % ≈ 15 min, 90→100 % ≈ 31 min → nad 90 % se vyplatí jen výjimečně.
- Čekání na obsazenou stanici zatím jen jako penalizace stanic s jedním bodem; živá data až s NAP / etapa 5.
- Zajížďka k nabíječce je odhad z vzdušné vzdálenosti (1,4×); upřesnění maticí routeru je plánované.
- openrouteservice měl 30. 10. výpadek (HTTP 502 / bez odpovědi) — jeho napojení je otestované jen na vzorových
  datech; po obnovení ověřit skutečnou odpověď (hlavně kódy zemí v `countryinfo`). Do té doby jede záloha OSRM.
- OSRM demo server je jen pro vývoj (podmínky užití); na VPS poběží vlastní Valhalla nebo ORS.
