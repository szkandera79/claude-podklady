"""Datový model plánovače — čisté datové třídy bez I/O.

Jednotky: vzdálenost km, rychlost km/h, energie kWh, výkon kW, čas minuty, cena Kč s DPH.
SoC (stav baterie) v procentech 0–100.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class RoadClass(str, Enum):
    CITY = "mesto"
    DISTRICT = "okresni"
    PRIMARY = "prvni_trida"
    EXPRESSWAY = "rychlostni"
    MOTORWAY = "dalnice"


class DriveProfile(str, Enum):
    ECO = "eko"
    STANDARD = "standard"
    FAST = "rychly"


class Mode(str, Enum):
    FASTEST = "nejrychlejsi"
    CHEAPEST = "nejlevnejsi"
    BALANCED = "vyvazeny"


class Surface(str, Enum):
    DRY = "sucho"
    WET = "mokro"
    SNOW = "snih"


# ---------------------------------------------------------------- vozidlo

@dataclass
class ChargingCurve:
    """Body (SoC %, max. výkon kW) měřené na straně stojanu; mezi body lineární interpolace."""

    points: List[Tuple[float, float]]

    def power_at(self, soc: float) -> float:
        pts = self.points
        if soc <= pts[0][0]:
            return pts[0][1]
        for (s0, p0), (s1, p1) in zip(pts, pts[1:]):
            if soc <= s1:
                return p0 + (p1 - p0) * (soc - s0) / (s1 - s0)
        return pts[-1][1]


@dataclass
class Vehicle:
    name: str = "Voyah Free 2023"
    usable_kwh: float = 100.0
    nominal_kwh: float = 106.0
    connector: str = "CCS2"
    mass_kg: float = 2400.0          # vůz + běžná posádka
    extra_load_kg: float = 0.0
    charge_efficiency: float = 0.95  # energie do baterie / energie ze stojanu
    curve: ChargingCurve = field(default_factory=lambda: ChargingCurve([
        # uživatel 30. 10. 2026: 10–80 % 89 kW, 80–90 % 40 kW, nad 90 % zhruba polovina (~20 kW)
        (0, 60), (10, 89), (80, 89), (81, 40), (90, 40), (91, 20), (100, 20),
    ]))

    @property
    def total_mass(self) -> float:
        return self.mass_kg + self.extra_load_kg


# ---------------------------------------------------------------- trasa

@dataclass
class Segment:
    """Úsek trasy (typicky 0,5–2 km) s atributy pro energetický model."""

    length_km: float
    road_class: RoadClass
    speed_limit: float                # km/h (z routeru nebo odhad dle třídy)
    elevation_delta_m: float = 0.0
    temp_c: float = 20.0
    headwind_kmh: float = 0.0         # průmět větru proti směru jízdy (záporný = do zad)
    surface: Surface = Surface.DRY


@dataclass
class Route:
    segments: List[Segment]
    name: str = ""

    @property
    def length_km(self) -> float:
        return sum(s.length_km for s in self.segments)


# ---------------------------------------------------------------- nabíječky a tarify

@dataclass
class Station:
    id: str
    name: str
    operator: str
    route_km: float                   # poloha průmětu na trasu (km od startu)
    max_kw: float
    detour_km: float = 0.0            # jedním směrem z trasy ke stanici
    detour_min: float = 0.0           # jedním směrem
    points: int = 1
    connectors: Tuple[str, ...] = ("CCS2",)
    access_ok: bool = True            # veřejná / přístupná vozu (Tesla jen otevřené)
    shared_power: bool = False        # výkon se dělí mezi body
    data_source: str = ""
    data_updated: Optional[str] = None
    is_live_status: bool = False      # dostupnost z živého zdroje (jinak „neověřeno")
    available: Optional[bool] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    address: str = ""
    notes: Tuple[str, ...] = ()       # upozornění pro uživatele (neznámý výkon, otevírací doba, Tesla…)


@dataclass
class Tariff:
    operator: str
    price_kwh: float                  # Kč/kWh S DPH (vstup bez DPH převádí `with_vat`)
    price_min: float = 0.0            # Kč/min
    session_fee: float = 0.0          # Kč za nabíjení
    blocking_fee_min: float = 0.0     # Kč/min po uplynutí `blocking_after_min`
    blocking_after_min: float = 9999.0
    preferred: bool = False
    member: bool = False
    priority: int = 99                # 1 = nejvyšší

    @staticmethod
    def with_vat(price: float, includes_vat: bool, vat: float = 0.21) -> float:
        return price if includes_vat else round(price * (1 + vat), 2)


# ---------------------------------------------------------------- parametry plánování

@dataclass
class EnergyParams:
    """Koeficienty energetického modelu. Výchozí hodnoty jsou předpoklady ke kalibraci (ANALYZA.md kap. 5)."""

    # c(v) = a + b·v_vzduch² [kWh/100 km] — fit: 17,5 @ 90 km/h, 25 @ 125 km/h (léto, ≥ 15 °C)
    a: float = 9.43
    b: float = 0.000997
    city_extra: float = 1.5           # kWh/100 km navíc za rozjezdy ve městě
    drive_efficiency: float = 0.90    # stoupání: m·g·Δh / η
    regen_efficiency: float = 0.60    # klesání: vrátí se m·g·Δh · η
    heat_start_c: float = 15.0        # pod touto teplotou se počítá topení navíc
    heat_kw_per_c: float = 0.12       # kW na °C pod heat_start
    heat_base_kw: float = 0.3         # skoková složka při zapnutí topení
    cool_start_c: float = 25.0
    cool_kw: float = 0.5
    batt_temp_coef: float = 0.006     # +0,6 % spotřeby na °C pod 15 °C
    surface_factor: Dict[str, float] = field(default_factory=lambda: {
        Surface.DRY.value: 1.0, Surface.WET.value: 1.05, Surface.SNOW.value: 1.15,
    })
    uncertainty: float = 0.08         # pásmo nejistoty (konzervativní režim)


@dataclass
class PlanParams:
    start_soc: float
    reserve_station: float = 10.0
    reserve_destination: float = 15.0
    profile: DriveProfile = DriveProfile.STANDARD
    mode: Mode = Mode.FASTEST
    conservative: bool = False
    stop_overhead_min: float = 4.0
    value_of_time_czk_h: float = 300.0   # pro vyvážený režim
    preferred_bonus_min: float = 5.0     # „sleva" v minutách pro prioritu 1 (klesá s prioritou)
    only_preferred: bool = False
    min_station_kw: float = 0.0          # 0 = bez preference
    default_price_kwh: float = 19.0      # síť bez zadaného tarifu
    battery_temp_c: Optional[float] = None  # teplota baterie při nabíjení (None = zahřátá)
    energy_factor: float = 1.0           # korekce z aktuální jízdy (k_trip)
