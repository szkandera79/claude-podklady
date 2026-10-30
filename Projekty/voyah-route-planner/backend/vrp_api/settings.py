"""Uživatelské nastavení (JSON v SQLite) → objekty jádra. Výchozí hodnoty = stav k 30. 10. 2026."""
from __future__ import annotations

import copy
from typing import Any, Dict

from vrp.calibration import CalibrationTable
from vrp.models import ChargingCurve, EnergyParams, Tariff, Vehicle

DEFAULT_SETTINGS: Dict[str, Any] = {
    "vehicle": {
        "name": "Voyah Free 2023", "usable_kwh": 100.0, "charge_efficiency": 0.95,
        "mass_kg": 2400.0, "extra_load_kg": 0.0,
        "curve": [[0, 60], [10, 89], [80, 89], [81, 40], [90, 40], [91, 20], [100, 20]],
    },
    "energy": {
        "a": 9.43, "b": 0.000997, "city_extra": 1.5, "heat_start_c": 15.0, "heat_kw_per_c": 0.12,
        "heat_base_kw": 0.3, "batt_temp_coef": 0.006, "regen_efficiency": 0.6, "uncertainty": 0.08,
    },
    "planning": {
        "reserve_station": 10.0, "reserve_destination": 15.0, "profile": "standard", "conservative": False,
        "stop_overhead_min": 4.0, "value_of_time_czk_h": 300.0, "min_station_kw": 0.0,
        "only_preferred": False, "corridor_km": 5.0, "default_price_kwh": 19.0,
    },
    "tariffs": [
        {"operator": "PRE", "price": 10.0, "includes_vat": False, "preferred": True, "member": True, "priority": 1},
        {"operator": "Lidl", "price": 10.0, "includes_vat": True, "preferred": True, "member": False, "priority": 2},
        {"operator": "Tesla", "price": 12.0, "includes_vat": False, "preferred": True, "member": False, "priority": 3},
        {"operator": "E.ON", "price": 14.0, "includes_vat": False, "preferred": True, "member": False, "priority": 4},
    ],
}


def merged(stored: Dict[str, Any]) -> Dict[str, Any]:
    """Doplní chybějící klíče výchozími hodnotami (po rozšíření nastavení se staré uložení nerozbije)."""
    out = copy.deepcopy(DEFAULT_SETTINGS)
    for k, v in (stored or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k].update(v)
        else:
            out[k] = v
    return out


def vehicle_from(s: Dict[str, Any]) -> Vehicle:
    v = s["vehicle"]
    return Vehicle(name=v["name"], usable_kwh=float(v["usable_kwh"]), charge_efficiency=float(v["charge_efficiency"]),
                   mass_kg=float(v["mass_kg"]), extra_load_kg=float(v["extra_load_kg"]),
                   curve=ChargingCurve(sorted((float(a), float(b)) for a, b in v["curve"])))


def energy_from(s: Dict[str, Any]) -> EnergyParams:
    e = EnergyParams()
    for k, val in s["energy"].items():
        if hasattr(e, k):
            setattr(e, k, float(val))
    return e


def tariffs_from(s: Dict[str, Any]) -> Dict[str, Tariff]:
    out = {}
    for t in s["tariffs"]:
        out[t["operator"]] = Tariff(
            t["operator"], Tariff.with_vat(float(t["price"]), bool(t.get("includes_vat"))),
            price_min=float(t.get("price_min", 0)), session_fee=float(t.get("session_fee", 0)),
            blocking_fee_min=float(t.get("blocking_fee_min", 0)),
            blocking_after_min=float(t.get("blocking_after_min", 9999)),
            preferred=bool(t.get("preferred")), member=bool(t.get("member")), priority=int(t.get("priority", 99)))
    return out


def calibration_from(data: Dict[str, Any], usable_kwh: float) -> CalibrationTable:
    cal = CalibrationTable(usable_kwh=usable_kwh)
    for key, (k, n) in (data or {}).get("cells", {}).items():
        group, band = key.split("|")
        cal.cells[(group, int(band))] = (float(k), float(n))
    return cal


def calibration_to(cal: CalibrationTable) -> Dict[str, Any]:
    return {"cells": {f"{g}|{b}": [k, n] for (g, b), (k, n) in cal.cells.items()}}
