"""Výpočet doby a ceny nabíjení z nabíjecí křivky vozu a výkonu stanice.

Výkon v každém 1% kroku SoC:
    P = min( křivka_vozu(SoC) × k_teplota_baterie , výkon_stanice × k_sdílení )
Křivka je měřená na straně stojanu (záznam PRE 22. 1. 2026: 89,95 kW, ≈1,01 kWh ze stojanu na 1 %),
proto čas = energie ze stojanu / P.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .models import Station, Tariff, Vehicle

SHARED_POWER_FACTOR = 0.5


def battery_temp_factor(battery_temp_c: Optional[float]) -> float:
    """Omezení výkonu studenou baterií — předpoklad ke kalibraci: 0,6 při −10 °C → 1,0 při +15 °C."""
    if battery_temp_c is None or battery_temp_c >= 15:
        return 1.0
    return max(0.6, 0.6 + 0.4 * (battery_temp_c + 10) / 25)


def effective_power(vehicle: Vehicle, station_kw: float, soc: float,
                    shared: bool = False, battery_temp_c: Optional[float] = None) -> float:
    car = vehicle.curve.power_at(soc) * battery_temp_factor(battery_temp_c)
    stall = station_kw * (SHARED_POWER_FACTOR if shared else 1.0)
    return max(0.1, min(car, stall))


@dataclass
class ChargeTable:
    """Kumulativní čas [min] a energie ze stojanu [kWh] od 0 % po každé celé %; dotaz a→b je O(1)."""

    minutes: List[float]
    grid_kwh: List[float]

    def time(self, soc_from: int, soc_to: int) -> float:
        return self.minutes[soc_to] - self.minutes[soc_from]

    def energy(self, soc_from: int, soc_to: int) -> float:
        return self.grid_kwh[soc_to] - self.grid_kwh[soc_from]


def build_charge_table(vehicle: Vehicle, station_kw: float, shared: bool = False,
                       battery_temp_c: Optional[float] = None) -> ChargeTable:
    step_grid = vehicle.usable_kwh / 100.0 / vehicle.charge_efficiency
    minutes, grid = [0.0], [0.0]
    for s in range(100):
        p = effective_power(vehicle, station_kw, s + 0.5, shared, battery_temp_c)
        minutes.append(minutes[-1] + step_grid / p * 60.0)
        grid.append(grid[-1] + step_grid)
    return ChargeTable(minutes, grid)


def charge_cost(tariff: Optional[Tariff], grid_kwh: float, minutes: float,
                default_price_kwh: float) -> float:
    if tariff is None:
        return grid_kwh * default_price_kwh
    cost = grid_kwh * tariff.price_kwh + minutes * tariff.price_min + tariff.session_fee
    if minutes > tariff.blocking_after_min:
        cost += (minutes - tariff.blocking_after_min) * tariff.blocking_fee_min
    return cost


def station_charge_table(vehicle: Vehicle, station: Station,
                         battery_temp_c: Optional[float] = None) -> ChargeTable:
    return build_charge_table(vehicle, station.max_kw, station.shared_power, battery_temp_c)
