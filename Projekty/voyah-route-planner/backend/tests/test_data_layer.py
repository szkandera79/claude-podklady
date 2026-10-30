"""Datová vrstva bez sítě: parsování OSM / OCM / ORS / OSRM, slučování, koridor, počasí, geometrie.
Vstupy jsou ručně sestavené podle struktury skutečných odpovědí (ověřeno 30. 10. 2026)."""
from vrp.models import RoadClass, Surface
from vrp_data.chargers import merge, to_stations
from vrp_data.geo import Polyline, encode_polyline, haversine_km
from vrp_data.ocm import parse_poi
from vrp_data.operators import normalize_operator
from vrp_data.osm import parse_element, parse_kw
from vrp_data.routing import parse_ors, parse_osrm
from vrp_data.weather import headwind_kmh, surface_from


def test_polyline_encoding_matches_google_example():
    pts = [(38.5, -120.2), (40.7, -120.95), (43.252, -126.453)]
    assert encode_polyline(pts) == "_p~iF~ps|U_ulLnnqC_mqNvxq`@"


def test_haversine_ostrava_praha():
    assert 275 < haversine_km((49.8209, 18.2625), (50.0755, 14.4378)) < 280


def test_projection_on_route():
    line = Polyline.from_points([(50.0, 14.0), (50.0, 15.0)])          # ~71,5 km na východ
    km, off = line.project((50.02, 14.5))
    assert abs(km - line.length_km / 2) < 0.5
    assert 2.0 < off < 2.5


def test_parse_kw_variants():
    assert parse_kw("150 kW") == 150
    assert parse_kw("50 kW;150 kW") == 150
    assert parse_kw("22000 W") == 22
    assert parse_kw(None) is None


def test_operator_normalization():
    assert normalize_operator("Pražská energetika") == "PRE"
    assert normalize_operator("PRE (cz)") == "PRE"
    assert normalize_operator("E.ON Energie") == "E.ON"
    assert normalize_operator("ČEZ") == "ČEZ"
    assert normalize_operator("Tesla (including non-tesla)") == "Tesla"
    assert normalize_operator("Prefa") == "Prefa"


def _osm(id_, lat, lon, **tags):
    t = {"amenity": "charging_station", "socket:type2_combo": "2"}
    t.update(tags)
    return {"type": "node", "id": id_, "lat": lat, "lon": lon, "tags": t}


def test_osm_parse_power_access_and_notes():
    r = parse_element(_osm(1, 50.0, 14.5, operator="Pražská energetika", **{"socket:type2_combo:output": "150 kW"}))
    assert r.operator == "PRE" and r.max_kw == 150 and r.power_known and r.points == 2
    lidl = parse_element(_osm(2, 50.0, 14.6, operator="Lidl", access="customers", opening_hours="Mo-Sa 07:00-21:00"))
    assert lidl.max_kw == 50 and not lidl.power_known
    assert any("výkon v datech chybí" in n for n in lidl.notes)
    assert any("otevírací dobu" in n for n in lidl.notes)
    tesla = parse_element(_osm(3, 50.0, 14.7, operator="Tesla"))
    assert any("Tesla" in n for n in tesla.notes)
    assert parse_element({"type": "node", "id": 4, "lat": 50, "lon": 14,
                          "tags": {"amenity": "charging_station", "socket:type2": "2"}}) is None


def _ocm(id_, lat, lon, kw=None, operational=True, open_data=True, usage=1, operator="PRE (cz)"):
    return {
        "ID": id_, "UsageTypeID": usage, "StatusType": {"IsOperational": operational},
        "OperatorInfo": {"Title": operator}, "DateLastVerified": "2025-10-07T10:00:00Z",
        "DataProvider": {"IsOpenDataLicensed": open_data},
        "AddressInfo": {"Title": f"OCM {id_}", "Latitude": lat, "Longitude": lon, "Town": "Praha"},
        "Connections": [{"ConnectionTypeID": 33, "PowerKW": kw, "Quantity": 2},
                        {"ConnectionTypeID": 25, "PowerKW": 22}],
    }


def test_ocm_parse_and_license_filter():
    r = parse_poi(_ocm(10, 50.0, 14.5, kw=100))
    assert r.operator == "PRE" and r.max_kw == 100 and r.points == 2 and r.updated == "2025-10-07"
    assert parse_poi(_ocm(11, 50.0, 14.5, kw=100, open_data=False)) is None
    assert parse_poi(_ocm(12, 50.0, 14.5, kw=100, usage=6)).access == "customers"


def test_merge_fills_power_and_status_from_ocm():
    osm = [parse_element(_osm(1, 50.0, 14.5, operator="Pražská energetika"))]
    ocm_recs = [parse_poi(_ocm(10, 50.0005, 14.5005, kw=100, operational=False)),   # ~65 m → sloučit
                parse_poi(_ocm(11, 50.1, 14.5, kw=150))]                            # jinde → přidat
    merged = merge(osm, ocm_recs)
    assert len(merged) == 2
    m = merged[0]
    assert m.source == "OSM+OCM" and m.max_kw == 100 and m.power_known and m.operational is False
    assert not any("výkon v datech chybí" in n for n in m.notes)


def test_corridor_projection_and_exclusions():
    line = Polyline.from_points([(50.0, 14.0), (50.0, 15.0)])
    recs = [parse_element(_osm(1, 50.0, 14.5, **{"socket:type2_combo:output": "150 kW"})),
            parse_element(_osm(2, 50.03, 14.5, **{"socket:type2_combo:output": "150 kW"})),     # ~3,3 km
            parse_element(_osm(3, 50.2, 14.5)),                                                # ~22 km
            parse_element(_osm(4, 50.0, 14.6, access="private"))]
    st = to_stations(recs, line, corridor_km=5)
    assert [s.id for s in st] == ["OSM:node/1", "OSM:node/2"]
    assert st[0].detour_km == 0 and st[1].detour_km > 4
    assert abs(st[0].route_km - line.length_km / 2) < 0.5
    assert st[0].lat == 50.0


def test_parse_ors_classes_and_elevation():
    coords = [[14.0 + k * 0.01, 50.0, 200 + k] for k in range(301)]   # ~215 km, stoupání 300 m
    data = {"features": [{"geometry": {"coordinates": coords}, "properties": {
        "summary": {"distance": 215000, "duration": 8000},
        "segments": [{"steps": [{"way_points": [0, 20], "distance": 14000, "duration": 1500},
                                {"way_points": [20, 300], "distance": 200000, "duration": 6500}]}],
        "extras": {"waycategory": {"values": [[0, 20, 0], [20, 300, 1]]},
                   "waytype": {"values": [[0, 10, 3], [10, 20, 2], [20, 300, 1]]}}}}]}
    rr = parse_ors(data)
    by = {}
    for s in rr.route.segments:
        by[s.road_class] = by.get(s.road_class, 0) + s.length_km
    assert by[RoadClass.MOTORWAY] > 190 and RoadClass.CITY in by and RoadClass.DISTRICT in by
    assert abs(sum(s.elevation_delta_m for s in rr.route.segments) - 300) < 1
    assert all(s.length_km <= 1.8 for s in rr.route.segments)
    mw = [s for s in rr.route.segments if s.road_class == RoadClass.MOTORWAY]
    assert all(s.speed_limit == 130 for s in mw)


def test_parse_osrm_detects_motorway_by_ref():
    step_mw = {"distance": 100000, "duration": 3500, "ref": "D1", "intersections": [{}],
               "geometry": {"coordinates": [[14.0 + k * 0.1, 50.0] for k in range(15)]}}
    step_city = {"distance": 3000, "duration": 400, "ref": "", "intersections": [{}],
                 "geometry": {"coordinates": [[15.4, 50.0], [15.42, 50.0]]}}
    res, pts = parse_osrm({"routes": [{"duration": 3900, "legs": [{"steps": [step_mw, step_city]}]}]})
    assert pts[0].cls == RoadClass.MOTORWAY and pts[-1].cls == RoadClass.CITY


def test_weather_helpers():
    assert abs(headwind_kmh(20, 90, 90) - 12) < 1e-9       # vítr od východu, jedu na východ → proti
    assert abs(headwind_kmh(20, 270, 90) + 12) < 1e-9      # do zad
    assert surface_from(0, 0.5) == Surface.SNOW
    assert surface_from(1.0, 0) == Surface.WET
    assert surface_from(0.0, 0) == Surface.DRY
