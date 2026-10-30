"""Transparentní kalibrace spotřeby z ujetých úseků (ANALYZA.md kap. 8).

Faktor k(skupina silnic, teplotní pásmo) — vážený průměr se „smrštěním" k 1,0:
    k_nový = (n·k_starý + w·k_změřený) / (n + w),   w = spotřebovaná energie / 10 kWh
Měřená energie = ΔSoC × využitelná kapacita (nejistota ±1 % SoC ≈ ±1 kWh → krátké úseky mají malou váhu).
Odlehlé hodnoty (|k − 1| > 0,4) se uloží, ale do modelu nevstoupí bez potvrzení.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .models import RoadClass

TEMP_BANDS = [(-99.0, -5.0), (-5.0, 5.0), (5.0, 15.0), (15.0, 25.0), (25.0, 99.0)]
GROUP = {
    RoadClass.MOTORWAY: "dalnice", RoadClass.EXPRESSWAY: "dalnice",
    RoadClass.PRIMARY: "silnice", RoadClass.DISTRICT: "silnice", RoadClass.CITY: "mesto",
}
PRIOR_WEIGHT = 2.0
OUTLIER = 0.4
WEIGHT_KWH = 10.0


def temp_band(temp_c: float) -> int:
    for i, (lo, hi) in enumerate(TEMP_BANDS):
        if lo <= temp_c < hi:
            return i
    return len(TEMP_BANDS) - 1


@dataclass
class Observation:
    km_by_class: Dict[RoadClass, float]
    temp_c: float
    predicted_kwh: float
    soc_start: float
    soc_end: float
    applied: bool = False


@dataclass
class CalibrationTable:
    usable_kwh: float = 100.0
    cells: Dict[Tuple[str, int], Tuple[float, float]] = field(default_factory=dict)  # (k, váha)
    observations: List[Observation] = field(default_factory=list)

    def factor(self, road_class: RoadClass, temp_c: float) -> float:
        return self.cells.get((GROUP[road_class], temp_band(temp_c)), (1.0, 0.0))[0]

    def as_fn(self):
        return self.factor

    def add(self, obs: Observation) -> bool:
        """Vrátí True, pokud pozorování vstoupilo do modelu."""
        self.observations.append(obs)
        measured = (obs.soc_start - obs.soc_end) / 100.0 * self.usable_kwh
        if obs.predicted_kwh <= 0 or measured <= 0:
            return False
        ratio = measured / obs.predicted_kwh
        if abs(ratio - 1.0) > OUTLIER:
            return False
        total_km = sum(obs.km_by_class.values()) or 1.0
        band = temp_band(obs.temp_c)
        for rc, km in obs.km_by_class.items():
            key = (GROUP[rc], band)
            k_old, n = self.cells.get(key, (1.0, PRIOR_WEIGHT))
            w = measured / WEIGHT_KWH * km / total_km
            self.cells[key] = ((n * k_old + w * ratio) / (n + w), n + w)
        obs.applied = True
        return True

    def uncertainty(self, base: float = 0.08) -> float:
        """Pásmo nejistoty klesá s množstvím kalibračních dat (min. 3 %)."""
        extra = sum(max(n - PRIOR_WEIGHT, 0.0) for _, n in self.cells.values())
        return max(0.03, base / math.sqrt(1.0 + extra / 5.0))


def estimate_usable_kwh(grid_kwh: float, soc_from: float, soc_to: float, charge_efficiency: float = 0.95) -> float:
    """Využitelná kapacita z nabíjení: energie do baterie / ΔSoC."""
    return grid_kwh * charge_efficiency / ((soc_to - soc_from) / 100.0)
