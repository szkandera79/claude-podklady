"""Vygeneruje referenční výsledky Python jádra pro křížovou kontrolu TypeScript přepisu (frontend/src/core/golden.json).
Spuštění: python tests/make_golden.py"""
import json
import sys
from dataclasses import replace
from pathlib import Path

sys.path[:0] = [str(Path(__file__).parent), str(Path(__file__).parents[1])]
from conftest import make_route, station  # noqa: E402
from vrp.models import Mode, PlanParams, RoadClass, Surface, Tariff, Vehicle  # noqa: E402
from vrp.optimizer import plan_route  # noqa: E402

V = Vehicle()
TAR = {"PRE": Tariff("PRE", 12.1, preferred=True, member=True, priority=1),
       "Lidl": Tariff("Lidl", 10.0, preferred=True, priority=2)}
ROUTES = {
    "mix": [(120, RoadClass.MOTORWAY, 130, 5, 300), (40, RoadClass.PRIMARY, 90, 3, -100, Surface.WET),
            (10, RoadClass.CITY, 50, 2), (300, RoadClass.MOTORWAY, 130, -2, 0, Surface.SNOW, 15)],
    "leto": [(600, RoadClass.MOTORWAY, 130, 22)],
}
STATIONS = [station("A", 90, kw=150, operator="PRE", points=2), station("B", 150, kw=50, operator="Lidl"),
            station("C", 230, kw=300, detour_km=2, detour_min=3), station("D", 330, kw=120, operator="PRE"),
            station("E", 420, kw=75, points=1), station("F", 520, kw=200)]
out = []
for rname, secs in ROUTES.items():
    for mode in Mode:
        for soc in (90, 55):
            for cons in (False, True):
                p = PlanParams(soc, mode=mode, conservative=cons)
                r = make_route(secs)
                pl = plan_route(r, STATIONS, V, p, tariffs=TAR)
                out.append({"route": rname, "mode": mode.value, "soc": soc, "conservative": cons,
                            "feasible": pl.feasible, "total_min": round(pl.total_min, 6),
                            "cost": round(pl.cost_czk, 6), "arrival_soc": pl.arrival_soc,
                            "stops": [[s.station.id, s.arrive_soc, s.depart_soc] for s in pl.stops],
                            "energy": round(pl.trip_energy_kwh, 6)})
target = Path(__file__).parents[2] / "frontend" / "src" / "core" / "golden.json"
target.write_text(json.dumps({"cases": out}, ensure_ascii=False, indent=1))
print(len(out), "případů →", target)
