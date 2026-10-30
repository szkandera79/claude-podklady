"""FastAPI aplikace. Spuštění: uvicorn vrp_api.app:app --port 8010 (z adresáře backend).

Přístup: pokud je v ~/.config/voyah-route-planner/.env nastaveno VRP_APP_TOKEN, vyžaduje se hlavička
`Authorization: Bearer <token>` (aplikace se na token zeptá jednou a uloží si ho v telefonu).
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from vrp.calibration import GROUP, Observation
from vrp.energy import route_profile
from vrp.models import DriveProfile, Mode, PlanParams
from vrp.optimizer import plan_route
from vrp.trip import SocReading, soc_update

from vrp_data.config import secret
from vrp_data.geo import Polyline
from vrp_data.http import SourceError
from vrp_data.planner import ATTRIBUTION, VARIANTS, plan_trip

from . import settings as S
from .serialize import plan_to_dict, route_from_dict, route_to_dict, station_brief, station_from_dict, station_to_dict
from .store import Store

FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
OFFROUTE_WARN_KM = 3.0
CHARGE_DETECT_PCT = 2.0
MIN_OBS_KM = 20.0

app = FastAPI(title="Voyah Smart Route Planner", docs_url="/api/docs", openapi_url="/api/openapi.json")
store = Store()


def auth(authorization: Optional[str] = Header(None)) -> None:
    token = secret("VRP_APP_TOKEN")
    if token and authorization != f"Bearer {token}":
        raise HTTPException(401, "Neplatný nebo chybějící přístupový token")


def current_settings() -> Dict[str, Any]:
    return S.merged(store.get("settings", {}))


def model_objects(s: Dict[str, Any]):
    vehicle = S.vehicle_from(s)
    cal = S.calibration_from(store.get("calibration", {}), vehicle.usable_kwh)
    energy = S.energy_from(s)
    if cal.cells:
        energy.uncertainty = min(energy.uncertainty, cal.uncertainty(energy.uncertainty))
    return vehicle, energy, S.tariffs_from(s), cal


def params_from(s: Dict[str, Any], soc: float, **over) -> PlanParams:
    p = s["planning"]
    params = PlanParams(
        start_soc=soc, reserve_station=float(p["reserve_station"]), reserve_destination=float(p["reserve_destination"]),
        profile=DriveProfile(p["profile"]), conservative=bool(p["conservative"]),
        stop_overhead_min=float(p["stop_overhead_min"]), value_of_time_czk_h=float(p["value_of_time_czk_h"]),
        min_station_kw=float(p["min_station_kw"]), only_preferred=bool(p["only_preferred"]),
        default_price_kwh=float(p["default_price_kwh"]))
    return replace(params, **{k: v for k, v in over.items() if v is not None})


# ------------------------------------------------------------------ modely požadavků

class PlanRequest(BaseModel):
    origin: str
    destination: str
    via: List[str] = []
    soc: float = Field(..., ge=1, le=100)
    reserve_destination: Optional[float] = Field(None, ge=0, le=60)
    reserve_station: Optional[float] = Field(None, ge=0, le=60)
    profile: Optional[str] = None
    conservative: Optional[bool] = None


class TripRequest(BaseModel):
    plan_id: str
    variant: str = "nejrychlejsi"


class SocRequest(BaseModel):
    soc: float = Field(..., ge=0, le=100)
    lat: Optional[float] = None
    lon: Optional[float] = None
    route_km: Optional[float] = None


# ------------------------------------------------------------------ endpointy

@app.get("/api/health")
def health() -> Dict[str, Any]:
    return {"ok": True, "auth": bool(secret("VRP_APP_TOKEN")), "attribution": ATTRIBUTION}


@app.post("/api/plan", dependencies=[Depends(auth)])
def api_plan(req: PlanRequest) -> Dict[str, Any]:
    s = current_settings()
    vehicle, energy, tariffs, cal = model_objects(s)
    params = params_from(s, req.soc, reserve_destination=req.reserve_destination,
                         reserve_station=req.reserve_station,
                         profile=DriveProfile(req.profile) if req.profile else None, conservative=req.conservative)
    try:
        res = plan_trip(req.origin, req.destination, params, via=req.via, vehicle=vehicle, energy=energy,
                        tariffs=tariffs, corridor_km=float(s["planning"]["corridor_km"]),
                        calibration=cal.as_fn() if cal.cells else None)
    except SourceError as e:
        raise HTTPException(502, f"Plán nelze spočítat: {e}")
    route = route_to_dict(res.route.route, res.route.points, res.route.source)
    result = {
        "origin": res.origin, "destination": res.destination, "route_source": res.route.source,
        "distance_km": round(res.route.route.length_km, 1), "geometry": route["points"],
        "notes": res.notes, "calibrated": bool(cal.cells), "attribution": ATTRIBUTION,
        "plans": {k: plan_to_dict(p) for k, p in res.plans.items()},
        "stations": [station_brief(st) for st in res.stations],
        "request": req.model_dump(),
    }
    result["plan_id"] = store.save_plan(req.model_dump(), route, [station_to_dict(st) for st in res.stations], result)
    return result


@app.get("/api/plan/{plan_id}", dependencies=[Depends(auth)])
def api_plan_get(plan_id: str) -> Dict[str, Any]:
    p = store.load_plan(plan_id)
    if not p:
        raise HTTPException(404, "Plán nenalezen")
    return {**p["result"], "plan_id": plan_id}


@app.post("/api/trips", dependencies=[Depends(auth)])
def api_trip_create(req: TripRequest) -> Dict[str, Any]:
    p = store.load_plan(req.plan_id)
    if not p:
        raise HTTPException(404, "Plán nenalezen")
    if req.variant not in VARIANTS:
        raise HTTPException(400, "Neznámá varianta")
    soc = float(p["request"]["soc"])
    state = {"reference": {"km": 0.0, "soc": soc}, "last": None, "k_trip": 1.0,
             "plan": p["result"]["plans"][req.variant]}
    tid = store.create_trip(req.plan_id, req.variant, state)
    store.add_reading(tid, 0.0, soc, None, None, "start")
    return {"trip_id": tid, **state}


def _trip_context(tid: str):
    trip = store.load_trip(tid)
    if not trip:
        raise HTTPException(404, "Cesta nenalezena")
    plan = store.load_plan(trip["plan_id"])
    route, points = route_from_dict(plan["route"])
    stations = [station_from_dict(d) for d in plan["stations"]]
    return trip, plan, route, points, stations


@app.get("/api/trips/{tid}", dependencies=[Depends(auth)])
def api_trip_get(tid: str) -> Dict[str, Any]:
    trip, plan, *_ = _trip_context(tid)
    return {**trip, "readings": store.readings(tid), "plan_result": plan["result"]}


def _observation(route, ref: Dict, end: Dict, settings: Dict) -> Optional[Observation]:
    """Kalibrační pozorování z úseku mezi dvěma známými SoC (bez nabíjení mezi nimi)."""
    if end["km"] - ref["km"] < MIN_OBS_KM or end["soc"] >= ref["soc"]:
        return None
    vehicle = S.vehicle_from(settings)
    prof = route_profile(route, vehicle, S.energy_from(settings), DriveProfile(settings["planning"]["profile"]))
    km_by, temps, pos = {}, [], 0.0
    for seg in route.segments:
        mid = pos + seg.length_km / 2
        if ref["km"] <= mid <= end["km"]:
            km_by[seg.road_class] = km_by.get(seg.road_class, 0.0) + seg.length_km
            temps.append(seg.temp_c)
        pos += seg.length_km
    if not km_by:
        return None
    return Observation(km_by, sum(temps) / len(temps), prof.energy_between(ref["km"], end["km"]),
                       ref["soc"], end["soc"])


def _add_observation(obs: Optional[Observation], settings: Dict) -> Optional[bool]:
    if obs is None:
        return None
    cal = S.calibration_from(store.get("calibration", {}), float(settings["vehicle"]["usable_kwh"]))
    applied = cal.add(obs)
    store.put("calibration", S.calibration_to(cal))
    log = store.get("observations", [])
    log.append({"km": {k.value: round(v, 1) for k, v in obs.km_by_class.items()}, "temp_c": round(obs.temp_c, 1),
                "predicted_kwh": round(obs.predicted_kwh, 1), "soc_start": obs.soc_start, "soc_end": obs.soc_end,
                "applied": applied})
    store.put("observations", log[-500:])
    return applied


@app.post("/api/trips/{tid}/soc", dependencies=[Depends(auth)])
def api_trip_soc(tid: str, req: SocRequest) -> Dict[str, Any]:
    trip, plan, route, points, stations = _trip_context(tid)
    if trip["finished"]:
        raise HTTPException(400, "Cesta je ukončená")
    s = current_settings()
    vehicle, energy, tariffs, cal = model_objects(s)
    warnings: List[str] = []
    offroute = 0.0
    if req.lat is not None and req.lon is not None:
        km, offroute = Polyline.from_points(points).project((req.lat, req.lon))
        if offroute > OFFROUTE_WARN_KM:
            warnings.append(f"Jste {offroute:.0f} km mimo plánovanou trasu — pro přesný výsledek naplánujte "
                            "trasu znovu z aktuální polohy.")
    elif req.route_km is not None:
        km = req.route_km
    else:
        raise HTTPException(400, "Chybí poloha (GPS) nebo km trasy")

    st = trip["state"]
    ref = st["reference"]
    params = params_from(s, req.soc, **{k: v for k, v in {
        "reserve_destination": plan["request"].get("reserve_destination"),
        "reserve_station": plan["request"].get("reserve_station"),
        "profile": DriveProfile(plan["request"]["profile"]) if plan["request"].get("profile") else None,
        "conservative": plan["request"].get("conservative")}.items() if v is not None})
    params = replace(params, **VARIANTS[trip["variant"]])
    calib = cal.as_fn() if cal.cells else None
    old_ids = [x["station"]["id"] for x in st["plan"]["stops"] if x["arrive_km"] > km]

    prev = st.get("last") or ref
    if req.soc > prev["soc"] + CHARGE_DETECT_PCT or km < ref["km"]:
        # nabíjelo se (nebo nový začátek) → nový referenční bod; odchylka spotřeby se přenáší
        if st.get("last"):
            _add_observation(_observation(route, ref, st["last"], s), s)
        new_plan = plan_route(route, stations, vehicle, replace(params, energy_factor=st["k_trip"]), energy,
                              tariffs, calib, start_km=km)
        result = {"predicted_soc": None, "measured_ratio": None, "k_trip": st["k_trip"]}
        st["reference"] = {"km": km, "soc": req.soc}
        st["last"] = None
        kind = "po_nabiti"
    else:
        upd = soc_update(route, stations, vehicle, params, SocReading(ref["km"], ref["soc"]),
                         SocReading(km, req.soc), energy, tariffs, calib)
        new_plan = upd.plan
        warnings += upd.warnings
        st["k_trip"] = upd.k_trip
        st["last"] = {"km": km, "soc": req.soc}
        result = {"predicted_soc": round(upd.predicted_soc, 1), "measured_ratio": round(upd.measured_ratio, 3),
                  "k_trip": round(upd.k_trip, 3)}
        kind = "jizda"
    new_ids = [x.station.id for x in new_plan.stops]
    if new_plan.feasible and old_ids != new_ids:
        warnings.append("Plán zastávek se změnil." if new_ids else "Další nabíjení už není potřeba.")
    st["plan"] = plan_to_dict(new_plan)
    store.update_trip(tid, st)
    store.add_reading(tid, km, req.soc, req.lat, req.lon, kind)
    return {"route_km": round(km, 1), "offroute_km": round(offroute, 1), "remaining_km":
            round(route.length_km - km, 1), "actual_soc": req.soc, **result, "warnings": warnings,
            "plan": st["plan"]}


@app.post("/api/trips/{tid}/finish", dependencies=[Depends(auth)])
def api_trip_finish(tid: str, req: SocRequest) -> Dict[str, Any]:
    trip, plan, route, points, _ = _trip_context(tid)
    s = current_settings()
    if req.lat is not None and req.lon is not None:
        km, _ = Polyline.from_points(points).project((req.lat, req.lon))
    else:
        km = req.route_km if req.route_km is not None else route.length_km
    st = trip["state"]
    applied = _add_observation(_observation(route, st["reference"], {"km": km, "soc": req.soc}, s), s)
    store.add_reading(tid, km, req.soc, req.lat, req.lon, "cil")
    store.update_trip(tid, st, finished=True)
    msg = {None: "Úsek byl na kalibraci příliš krátký nebo se během něj nabíjelo.",
           True: "Jízda byla započtena do kalibrace spotřeby.",
           False: "Odchylka byla příliš velká (> 40 %) — jízda uložena, ale do modelu nezapočtena."}[applied]
    return {"ok": True, "calibration": msg}


@app.get("/api/trips", dependencies=[Depends(auth)])
def api_trips() -> List[Dict[str, Any]]:
    return store.trips()


@app.get("/api/settings", dependencies=[Depends(auth)])
def api_settings_get() -> Dict[str, Any]:
    return current_settings()


@app.put("/api/settings", dependencies=[Depends(auth)])
def api_settings_put(body: Dict[str, Any]) -> Dict[str, Any]:
    s = S.merged(body)
    try:
        S.vehicle_from(s), S.energy_from(s), S.tariffs_from(s)
        DriveProfile(s["planning"]["profile"])
    except (KeyError, TypeError, ValueError) as e:
        raise HTTPException(400, f"Neplatné nastavení: {e}")
    store.put("settings", s)
    return s


@app.post("/api/settings/reset", dependencies=[Depends(auth)])
def api_settings_reset() -> Dict[str, Any]:
    store.put("settings", {})
    return current_settings()


@app.get("/api/calibration", dependencies=[Depends(auth)])
def api_calibration() -> Dict[str, Any]:
    s = current_settings()
    cal = S.calibration_from(store.get("calibration", {}), float(s["vehicle"]["usable_kwh"]))
    return {"cells": [{"group": g, "band": b, "factor": round(k, 3), "weight": round(n, 2)}
                      for (g, b), (k, n) in sorted(cal.cells.items())],
            "uncertainty": round(cal.uncertainty(float(s["energy"]["uncertainty"])), 3),
            "observations": store.get("observations", [])[-50:]}


@app.post("/api/calibration/reset", dependencies=[Depends(auth)])
def api_calibration_reset() -> Dict[str, Any]:
    store.put("calibration", {})
    return {"ok": True}


# ------------------------------------------------------------------ frontend (PWA)

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        f = (FRONTEND_DIST / path).resolve()
        if path and f.is_file() and FRONTEND_DIST in f.parents:
            return FileResponse(f)
        return FileResponse(FRONTEND_DIST / "index.html")
