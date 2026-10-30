"""API bez sítě: plan_trip je nahrazen syntetickou trasou (stanice jen pro test)."""
import pytest
from fastapi.testclient import TestClient

import vrp_api.app as appmod
from vrp_api.store import Store
from vrp_data.geo import Polyline
from vrp_data.planner import TripResult, plan_variants_for
from vrp_data.routing import RouteResult

from conftest import motorway, station

# trasa 450 km na východ po rovnoběžce 50° (1° délky ≈ 71,7 km)
POINTS = [(50.0, 12.0 + k * 0.01) for k in range(629)]
LINE = Polyline.from_points(POINTS)


def fake_plan_trip(origin, destination, params, via=(), vehicle=None, energy=None, tariffs=None, depart=None,
                   corridor_km=5.0, calibration=None, variants=None):
    route = motorway(round(LINE.length_km))
    sts = []
    for k in (150, 250, 350):
        lat, lon = LINE.point_at(k)
        sts.append(station(f"S{k}", k, operator="PRE", lat=lat, lon=lon))
    rr = RouteResult(route, POINTS, "test", 0)
    plans = plan_variants_for(rr, sts, params, vehicle, energy, tariffs, calibration, variants)
    return TripResult(origin, destination, rr, plans, sts, [])


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(appmod, "store", Store(tmp_path / "t.sqlite"))
    monkeypatch.setattr(appmod, "plan_trip", fake_plan_trip)
    monkeypatch.setattr(appmod, "secret", lambda name: None)
    return TestClient(appmod.app)


def make_plan(client, soc=90):
    r = client.post("/api/plan", json={"origin": "A", "destination": "B", "soc": soc})
    assert r.status_code == 200, r.text
    return r.json()


def test_plan_returns_variants_and_geometry(client):
    d = make_plan(client)
    assert set(d["plans"]) == {"nejrychlejsi", "vyvazeny", "nejlevnejsi", "eko"}
    p = d["plans"]["nejrychlejsi"]
    assert p["feasible"] and len(p["stops"]) == 1
    s = p["stops"][0]
    assert s["station"]["lat"] and s["depart_min"] > s["arrive_min"] > 0
    assert len(d["geometry"]) > 100 and d["plan_id"]
    assert client.get(f"/api/plan/{d['plan_id']}").json()["plan_id"] == d["plan_id"]


def test_trip_soc_update_projection_and_charging(client):
    d = make_plan(client)
    t = client.post("/api/trips", json={"plan_id": d["plan_id"], "variant": "nejrychlejsi"}).json()
    lat, lon = LINE.point_at(100)
    r = client.post(f"/api/trips/{t['trip_id']}/soc", json={"soc": 50, "lat": lat + 0.01, "lon": lon}).json()
    assert abs(r["route_km"] - 100) < 1 and r["offroute_km"] < 2
    assert r["k_trip"] > 1.0                      # 40 % na 100 km = víc než model
    assert any("níž" in w for w in r["warnings"])
    assert r["plan"]["feasible"]
    lat, lon = LINE.point_at(160)
    r2 = client.post(f"/api/trips/{t['trip_id']}/soc", json={"soc": 80, "lat": lat, "lon": lon}).json()
    assert r2["predicted_soc"] is None             # rozpoznáno nabíjení
    trip = client.get(f"/api/trips/{t['trip_id']}").json()
    assert [x["kind"] for x in trip["readings"]] == ["start", "jizda", "po_nabiti"]
    cal = client.get("/api/calibration").json()
    assert len(cal["observations"]) == 1           # úsek start → km 100 vstoupil do kalibrace


def test_offroute_warning(client):
    d = make_plan(client)
    t = client.post("/api/trips", json={"plan_id": d["plan_id"]}).json()
    lat, lon = LINE.point_at(50)
    r = client.post(f"/api/trips/{t['trip_id']}/soc", json={"soc": 75, "lat": lat + 0.2, "lon": lon}).json()
    assert r["offroute_km"] > 20 and any("mimo plánovanou trasu" in w for w in r["warnings"])


def test_finish_adds_calibration(client):
    d = make_plan(client, soc=90)
    t = client.post("/api/trips", json={"plan_id": d["plan_id"]}).json()
    r = client.post(f"/api/trips/{t['trip_id']}/finish", json={"soc": 62, "route_km": 120}).json()
    assert "započtena" in r["calibration"]
    cal = client.get("/api/calibration").json()
    assert cal["cells"] and cal["cells"][0]["group"] == "dalnice"
    r = client.post(f"/api/trips/{t['trip_id']}/soc", json={"soc": 50, "route_km": 130})
    assert r.status_code == 400


def test_settings_roundtrip_and_validation(client):
    s = client.get("/api/settings").json()
    assert s["vehicle"]["usable_kwh"] == 100 and s["tariffs"][0]["operator"] == "PRE"
    s["planning"]["reserve_destination"] = 20
    assert client.put("/api/settings", json=s).json()["planning"]["reserve_destination"] == 20
    s["planning"]["profile"] = "letadlo"
    assert client.put("/api/settings", json=s).status_code == 400
    d = make_plan(client)
    assert d["plans"]["nejrychlejsi"]["arrival_soc"] >= 20


def test_auth_required_when_token_set(client, monkeypatch):
    monkeypatch.setattr(appmod, "secret", lambda name: "tajne" if name == "VRP_APP_TOKEN" else None)
    assert client.get("/api/settings").status_code == 401
    assert client.get("/api/settings", headers={"Authorization": "Bearer tajne"}).status_code == 200
    assert client.get("/api/health").status_code == 200
