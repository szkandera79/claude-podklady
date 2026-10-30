# Voyah Smart Route Planner

Osobní plánovač tras a nabíjení pro Voyah Free BEV 2023 (PWA pro iPhone + backend FastAPI).
Cíl: minimální celkový čas cesty vč. nabíjení při bezpečné rezervě; kalibrace spotřeby z vlastních jízd.

## Stav
- **Etapa 1 (analýza):** [ANALYZA.md](ANALYZA.md) — schváleno 30. 10. 2026.
- **Etapa 2 + 3a (architektura, výpočetní jádro):** [ARCHITEKTURA.md](ARCHITEKTURA.md), kód `backend/vrp`, 34 testů zelených.
- **Etapa 3b (data):** hotovo — OSM + Open Charge Map, trasy ORS/OSRM, počasí Open-Meteo; plán z příkazové řádky, 46 testů.
- **Další krok 3c:** FastAPI + PWA pro iPhone, pak nasazení na VPS.
- Zodpovězeno 30. 10.: spotřeba, nabíjecí křivka (záznam PRE 22. 1. 2026), tarify, VPS schválen. Zbývající dotazy: ANALYZA.md, kap. 15.

## Zásady
- Parametry vozu jsou výchozí předpoklady, ne ověřená data (EU spec. 106 kWh; DC 89 kW v pásmu 10–80 % ověřeno záznamem PRE).
- Fiktivní nabíječky jen v testovacích fixturách.
- Žádné neověřené zásahy do vozu; integrace s autem až etapa 5.
- Bezplatné služby (ORS, Open-Meteo) jsou jen pro nekomerční užití.

## Testy
```bash
cd voyah-route-planner/backend && ~/.venvs/voyah-route-planner/bin/python -m pytest -q
```

## Plán z příkazové řádky
```bash
cd voyah-route-planner/backend && ~/.venvs/voyah-route-planner/bin/python -m vrp_data.cli "Ostrava" "Praha" --soc 60
```
Klíče: `~/.config/voyah-route-planner/.env` (`ORS_API_KEY`, `OCM_API_KEY`) — mimo iCloud a git.
