"""Testovací fixtury. Stanice zde jsou SYNTETICKÉ — slouží jen k ověření algoritmu, nikdy ne v produkci."""
from __future__ import annotations

from typing import Iterable, Tuple

import pytest

from vrp.models import RoadClass, Route, Segment, Station, Surface, Tariff, Vehicle


def make_route(sections: Iterable[Tuple], name: str = "test") -> Route:
    """sections: (km, třída, limit[, teplota °C[, převýšení m celkem[, povrch[, protivítr km/h]]]]) → úseky po 1 km."""
    segs = []
    for sec in sections:
        km, rc, limit = sec[:3]
        temp = sec[3] if len(sec) > 3 else 20.0
        dz = sec[4] if len(sec) > 4 else 0.0
        surface = sec[5] if len(sec) > 5 else Surface.DRY
        wind = sec[6] if len(sec) > 6 else 0.0
        n = int(round(km))
        for _ in range(n):
            segs.append(Segment(km / n, rc, limit, dz / n, temp, wind, surface))
    return Route(segs, name)


def motorway(km: float, temp: float = 20.0) -> Route:
    return make_route([(km, RoadClass.MOTORWAY, 130, temp)])


def station(sid: str, km: float, kw: float = 150, operator: str = "Jiný", **kw_args) -> Station:
    return Station(id=sid, name=f"Test {sid}", operator=operator, route_km=km, max_kw=kw,
                   points=kw_args.pop("points", 4), data_source="fixture", **kw_args)


@pytest.fixture
def vehicle() -> Vehicle:
    return Vehicle()


@pytest.fixture
def tariffs():
    return {
        "PRE": Tariff("PRE", Tariff.with_vat(10, False), preferred=True, member=True, priority=1),
        "Lidl": Tariff("Lidl", Tariff.with_vat(10, True), preferred=True, priority=2),
        "Tesla": Tariff("Tesla", Tariff.with_vat(12, False), preferred=True, priority=3),
        "E.ON": Tariff("E.ON", Tariff.with_vat(14, False), preferred=True, priority=4),
    }
