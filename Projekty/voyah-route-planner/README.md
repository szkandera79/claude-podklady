# Voyah Smart Route Planner

Osobní plánovač tras a nabíjení pro Voyah Free BEV 2023 (PWA pro iPhone + backend FastAPI).
Cíl: minimální celkový čas cesty vč. nabíjení při bezpečné rezervě; kalibrace spotřeby z vlastních jízd.

## Stav
- **Etapa 1–2 (analýza, návrh):** [ANALYZA.md](ANALYZA.md) — čeká na schválení, zatím se neprogramuje.
- Otevřené dotazy na uživatele: ANALYZA.md, kap. 15.

## Zásady
- Parametry vozu jsou výchozí předpoklady, ne ověřená data (EU spec. 106 kWh, DC 100 kW dle databází je odhad; uživatel pozoruje ~90 kW).
- Fiktivní nabíječky jen v testovacích fixturách.
- Žádné neověřené zásahy do vozu; integrace s autem až etapa 5.
- Bezplatné služby (ORS, Open-Meteo) jsou jen pro nekomerční užití.
