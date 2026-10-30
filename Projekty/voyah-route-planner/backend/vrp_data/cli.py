"""Plánování z příkazové řádky (do doby, než bude PWA).

    python -m vrp_data.cli "Ostrava" "Praha" --soc 80
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta

from vrp.models import DriveProfile, Mode, PlanParams, Tariff

from .http import SourceError
from .planner import ATTRIBUTION, plan_trip

# výchozí tarify uživatele (30. 10. 2026)
DEFAULT_TARIFFS = {
    "PRE": Tariff("PRE", Tariff.with_vat(10, False), preferred=True, member=True, priority=1),
    "Lidl": Tariff("Lidl", Tariff.with_vat(10, True), preferred=True, priority=2),
    "Tesla": Tariff("Tesla", Tariff.with_vat(12, False), preferred=True, priority=3),
    "E.ON": Tariff("E.ON", Tariff.with_vat(14, False), preferred=True, priority=4),
}


def _hm(minutes: float) -> str:
    return f"{int(minutes // 60)} h {int(round(minutes % 60)):02d} min"


def main() -> None:
    ap = argparse.ArgumentParser(description="Voyah Smart Route Planner — plán cesty")
    ap.add_argument("odkud")
    ap.add_argument("kam")
    ap.add_argument("--pres", action="append", default=[], help="průjezdní bod (lze opakovat)")
    ap.add_argument("--soc", type=float, required=True, help="stav baterie při odjezdu v %%")
    ap.add_argument("--rezerva-cil", type=float, default=15)
    ap.add_argument("--rezerva-nabijecka", type=float, default=10)
    ap.add_argument("--profil", choices=[p.value for p in DriveProfile], default="standard")
    ap.add_argument("--konzervativni", action="store_true")
    a = ap.parse_args()

    params = PlanParams(start_soc=a.soc, reserve_destination=a.rezerva_cil, reserve_station=a.rezerva_nabijecka,
                        profile=DriveProfile(a.profil), conservative=a.konzervativni)
    now = datetime.now()
    try:
        res = plan_trip(a.odkud, a.kam, params, via=a.pres, tariffs=DEFAULT_TARIFFS,
                        variants=["nejrychlejsi", "vyvazeny", "nejlevnejsi"])
    except SourceError as e:
        print(f"Plán nelze spočítat: {e}")
        raise SystemExit(1)

    print(f"\n{res.origin} → {res.destination}  ({res.route.route.length_km:.0f} km, trasa: {res.route.source}, "
          f"nabíječek v koridoru: {res.station_count})")
    for n in res.notes:
        print(f"  ! {n}")
    for mode, plan in res.plans.items():
        print(f"\n== Režim: {mode} ==")
        if not plan.feasible:
            print(f"  {plan.reason}")
            continue
        print(f"  Celkem {_hm(plan.total_min)} (jízda {_hm(plan.drive_min)}, nabíjení {_hm(plan.charge_min)}), "
              f"příjezd ~{(now + timedelta(minutes=plan.total_min)):%H:%M}, v cíli {plan.arrival_soc} %, "
              f"cena nabíjení ~{plan.cost_czk:.0f} Kč")
        for s in plan.stops:
            st = s.station
            print(f"  • km {s.arrive_km:.0f}: {st.name} ({st.operator}, {st.max_kw:.0f} kW) — "
                  f"{s.arrive_soc} % → {s.depart_soc} %, {s.charge_min:.0f} min, ~{s.cost_czk:.0f} Kč; "
                  f"další úsek {s.next_leg_km:.0f} km")
        for w in plan.warnings:
            print(f"    - {w}")
    print(f"\nOdhad, ne měření. {ATTRIBUTION}")


if __name__ == "__main__":
    main()
