/** Datová vrstva bez sítě (převedeno z backend/tests/test_data_layer.py) + přenos klíčů nastavovacím odkazem. */
import { describe, expect, it } from "vitest";
import { decodeSetup, encodeSetup } from "../local/keys";
import { merge, toStations } from "./chargers";
import { Polyline, encodePolyline, haversineKm } from "./geo";
import { parsePoi } from "./ocm";
import { normalizeOperator } from "./operators";
import { parseElement, parseKw } from "./osm";
import { parseOrs, parseOsrm } from "./routing";
import { headwindKmh, surfaceFrom } from "./weather";

const osm = (id: number, lat: number, lon: number, tags: Record<string, string> = {}) =>
  ({ type: "node", id, lat, lon, tags: { amenity: "charging_station", "socket:type2_combo": "2", ...tags } });
const ocm = (id: number, lat: number, lon: number, kw: number | null, extra: Record<string, unknown> = {}) => ({
  ID: id, UsageTypeID: 1, StatusType: { IsOperational: true }, OperatorInfo: { Title: "PRE (cz)" },
  DateLastVerified: "2025-10-07T10:00:00Z", DataProvider: { IsOpenDataLicensed: true },
  AddressInfo: { Title: `OCM ${id}`, Latitude: lat, Longitude: lon, Town: "Praha" },
  Connections: [{ ConnectionTypeID: 33, PowerKW: kw, Quantity: 2 }, { ConnectionTypeID: 25, PowerKW: 22 }], ...extra });

describe("geometrie a provozovatelé", () => {
  it("polyline podle příkladu Google", () =>
    expect(encodePolyline([[38.5, -120.2], [40.7, -120.95], [43.252, -126.453]])).toBe("_p~iF~ps|U_ulLnnqC_mqNvxq`@"));
  it("Ostrava–Praha vzdušnou čarou", () => {
    const d = haversineKm([49.8209, 18.2625], [50.0755, 14.4378]);
    expect(d).toBeGreaterThan(275);
    expect(d).toBeLessThan(280);
  });
  it("průmět na trasu", () => {
    const line = Polyline.from([[50, 14], [50, 15]]);
    const [km, off] = line.project([50.02, 14.5]);
    expect(Math.abs(km - line.lengthKm / 2)).toBeLessThan(0.5);
    expect(off).toBeGreaterThan(2);
    expect(off).toBeLessThan(2.5);
  });
  it("názvy provozovatelů", () => {
    expect(normalizeOperator("Pražská energetika")).toBe("PRE");
    expect(normalizeOperator("PRE (cz)")).toBe("PRE");
    expect(normalizeOperator("E.ON Energie")).toBe("E.ON");
    expect(normalizeOperator("Tesla (including non-tesla)")).toBe("Tesla");
    expect(normalizeOperator("Prefa")).toBe("Prefa");
  });
});

describe("nabíječky", () => {
  it("výkon a OSM", () => {
    expect(parseKw("50 kW;150 kW")).toBe(150);
    expect(parseKw("22000 W")).toBe(22);
    const r = parseElement(osm(1, 50, 14.5, { operator: "Pražská energetika", "socket:type2_combo:output": "150 kW" }))!;
    expect([r.operator, r.maxKw, r.powerKnown, r.points]).toEqual(["PRE", 150, true, 2]);
    const l = parseElement(osm(2, 50, 14.6, { operator: "Lidl", access: "customers" }))!;
    expect(l.maxKw).toBe(50);
    expect(l.notes.join()).toContain("otevírací dobu");
    expect(parseElement({ type: "node", id: 3, lat: 50, lon: 14, tags: { "socket:type2": "2" } })).toBeNull();
  });
  it("OCM a licence poskytovatele", () => {
    expect(parsePoi(ocm(10, 50, 14.5, 100))!.updated).toBe("2025-10-07");
    expect(parsePoi(ocm(11, 50, 14.5, 100, { DataProvider: { IsOpenDataLicensed: false } }))).toBeNull();
  });
  it("sloučení OSM + OCM a koridor", () => {
    const m = merge([parseElement(osm(1, 50, 14.5, { operator: "Pražská energetika" }))!],
                    [parsePoi(ocm(10, 50.0005, 14.5005, 100, { StatusType: { IsOperational: false } }))!,
                     parsePoi(ocm(11, 50.1, 14.5, 150))!]);
    expect(m.length).toBe(2);
    expect([m[0].source, m[0].maxKw, m[0].operational]).toEqual(["OSM+OCM", 100, false]);
    const line = Polyline.from([[50, 14], [50, 15]]);
    const st = toStations([parseElement(osm(1, 50, 14.5))!, parseElement(osm(2, 50.03, 14.5))!,
                           parseElement(osm(3, 50.2, 14.5))!, parseElement(osm(4, 50, 14.6, { access: "private" }))!], line, 5);
    expect(st.map((s) => s.id)).toEqual(["OSM:node/1", "OSM:node/2"]);
    expect(st[1].detourKm).toBeGreaterThan(4);
  });
});

describe("trasy a počasí", () => {
  it("ORS: třídy a převýšení", () => {
    const coords = Array.from({ length: 301 }, (_, k) => [14 + k * 0.01, 50, 200 + k]);
    const rr = parseOrs({ features: [{ geometry: { coordinates: coords }, properties: {
      summary: { duration: 8000 },
      segments: [{ steps: [{ way_points: [0, 20], distance: 14000, duration: 1500 }, { way_points: [20, 300], distance: 200000, duration: 6500 }] }],
      extras: { waycategory: { values: [[0, 20, 0], [20, 300, 1]] }, waytype: { values: [[0, 10, 3], [10, 20, 2], [20, 300, 1]] } } } }] });
    const by: Record<string, number> = {};
    for (const s of rr.route.segments) by[s.roadClass] = (by[s.roadClass] || 0) + s.lengthKm;
    expect(by.dalnice).toBeGreaterThan(190);
    expect(by.mesto && by.okresni).toBeTruthy();
    expect(rr.route.segments.reduce((a, s) => a + s.elevationDeltaM, 0)).toBeCloseTo(300, 0);
  });
  it("OSRM: dálnice podle označení", () => {
    const pts = parseOsrm({ routes: [{ legs: [{ steps: [
      { distance: 100000, duration: 3500, ref: "D1", intersections: [{}], geometry: { coordinates: Array.from({ length: 15 }, (_, k) => [14 + k * 0.1, 50]) } },
      { distance: 3000, duration: 400, ref: "", intersections: [{}], geometry: { coordinates: [[15.4, 50], [15.42, 50]] } }] }] }] });
    expect(pts[0].cls).toBe("dalnice");
    expect(pts[pts.length - 1].cls).toBe("mesto");
  });
  it("vítr a povrch", () => {
    expect(headwindKmh(20, 90, 90)).toBeCloseTo(12, 9);
    expect(headwindKmh(20, 270, 90)).toBeCloseTo(-12, 9);
    expect([surfaceFrom(0, 0.5), surfaceFrom(1, 0), surfaceFrom(0, 0)]).toEqual(["snih", "mokro", "sucho"]);
  });
});

describe("nastavovací odkaz", () => {
  it("klíče tam a zpět, bez znaků mimo URL", () => {
    const k = { ors: "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6Ij+/=", ocm: "1234abcd-0000-1111-2222-333344445555" };
    const enc = encodeSetup(k);
    expect(enc).toMatch(/^[A-Za-z0-9_-]+$/);
    expect(decodeSetup(enc)).toEqual(k);
    expect(decodeSetup("nesmysl!!")).toBeNull();
  });
});
