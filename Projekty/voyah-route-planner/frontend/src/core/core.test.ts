/** Testy jádra — převedené scénáře z backend/tests + křížová kontrola s Python implementací (golden.json).
 *  Stanice jsou SYNTETICKÉ, jen pro ověření algoritmu. */
import { describe, expect, it } from "vitest";
import golden from "./golden.json";
import { addObservation, calibrationFn, emptyCalibration, factor, uncertainty } from "./calibration";
import { buildChargeTable, estimateUsableKwh } from "./charging";
import { batteryFactor, hvacKw, routeProfile } from "./energy";
import type { DriveProfile, RoadClass, Route, Station, Surface } from "./models";
import { defaultEnergy, defaultVehicle, planParams, segment, station, tariff, withVat } from "./models";
import { planRoute } from "./optimizer";
import { socUpdate } from "./trip";

type Sec = [number, RoadClass, number, number?, number?, Surface?, number?];
function makeRoute(secs: Sec[]): Route {
  const segs = [];
  for (const [km, rc, lim, temp = 20, dz = 0, surface = "sucho", wind = 0] of secs) {
    const n = Math.round(km);
    for (let i = 0; i < n; i++) segs.push(segment(km / n, rc, lim, { tempC: temp, elevationDeltaM: dz / n, surface, headwindKmh: wind }));
  }
  return { segments: segs };
}
const motorway = (km: number, temp = 20) => makeRoute([[km, "dalnice", 130, temp]]);
const st = (id: string, km: number, kw = 150, extra: Partial<Station> = {}) =>
  station(id, km, kw, { name: `Test ${id}`, points: 4, dataSource: "fixture", ...extra });
const V = defaultVehicle();
const per100 = (r: Route, profile: DriveProfile = "rychly") => {
  const p = routeProfile(r, V, defaultEnergy(), profile);
  return (p.kwh[p.kwh.length - 1] / p.totalKm) * 100;
};
const TARIFFS = {
  PRE: tariff("PRE", withVat(10, false), { preferred: true, member: true, priority: 1 }),
  Lidl: tariff("Lidl", withVat(10, true), { preferred: true, priority: 2 }),
  Tesla: tariff("Tesla", withVat(12, false), { preferred: true, priority: 3 }),
  "E.ON": tariff("E.ON", withVat(14, false), { preferred: true, priority: 4 }),
};

describe("energetický model a nabíjení", () => {
  it("léto dálnice 25 kWh @ 125 km/h", () => expect(per100(makeRoute([[100, "dalnice", 125, 20]]))).toBeCloseTo(25, 0));
  it("okresní silnice 17,5 @ 90", () => expect(Math.abs(per100(makeRoute([[100, "okresni", 90, 20]])) - 17.5)).toBeLessThan(0.1));
  it("zima = složené koeficienty", () => {
    const p = defaultEnergy();
    const w = per100(makeRoute([[100, "dalnice", 125, -5]]));
    expect(Math.abs(w - (25.01 + (hvacKw(-5, p) / 125) * 100) * batteryFactor(-5, p))).toBeLessThan(0.1);
  });
  it("stoupání, sníh, protivítr", () => {
    const base = per100(makeRoute([[100, "dalnice", 125, 20]]));
    expect(per100(makeRoute([[100, "dalnice", 125, 20, 0, "snih"]]))).toBeGreaterThan(base * 1.1);
    expect(per100(makeRoute([[100, "dalnice", 125, 20, 0, "sucho", 20]]))).toBeGreaterThan(base);
    const up = per100(makeRoute([[100, "dalnice", 125, 20, 500]]));
    const down = per100(makeRoute([[100, "dalnice", 125, 20, -500]]));
    expect(up - base).toBeGreaterThan(base - down);
  });
  it("100 vs 250 kW stejný čas, 50 kW pomalejší", () => {
    expect(buildChargeTable(V, 100).time(10, 80)).toBeCloseTo(buildChargeTable(V, 250).time(10, 80), 9);
    expect(buildChargeTable(V, 50).time(10, 80)).toBeGreaterThan(buildChargeTable(V, 100).time(10, 80) * 1.5);
  });
  it("záznam PRE 22. 1. 2026 (28→63 % za 23:33, 35,4 kWh)", () => {
    const t = buildChargeTable(V, 200);
    expect(Math.abs(t.time(28, 63) - 23.55) / 23.55).toBeLessThan(0.07);
    expect(Math.abs(t.energy(28, 63) - 35.4) / 35.4).toBeLessThan(0.07);
    expect(estimateUsableKwh(35.4, 28, 63)).toBeGreaterThan(92);
  });
});

describe("optimalizace zastávek", () => {
  it("bez nabíjení", () => {
    const p = planRoute(motorway(200), [st("A", 100)], V, planParams(80));
    expect(p.feasible && p.stops.length === 0 && p.arrivalSoc >= 15).toBe(true);
  });
  it("jedna zastávka", () => {
    const p = planRoute(motorway(450), [st("A", 150), st("B", 250), st("C", 350)], V, planParams(90));
    expect(p.stops.length).toBe(1);
    expect(p.totalMin).toBeCloseTo(p.driveMin + p.chargeMin + p.stopOverheadMin, 6);
  });
  it("více zastávek", () => {
    const sts = Array.from({ length: 8 }, (_, k) => st(String(k), 100 + 100 * k));
    const p = planRoute(motorway(900), sts, V, planParams(90));
    expect(p.stops.length).toBeGreaterThanOrEqual(2);
    expect(p.stops.every((s) => s.arriveSoc >= 10)).toBe(true);
  });
  it("nad 80 %, když ušetří drahou zastávku", () => {
    const p = planRoute(motorway(560), [st("A", 250), st("B", 450, 150, { detourKm: 8, detourMin: 10 })], V, planParams(90));
    expect(p.stops.length).toBe(1);
    expect(p.stops[0].departSoc).toBeGreaterThan(80);
  });
  it("výpadek stanice → jiná", () => {
    const sts = [st("A", 200), st("B", 260), st("C", 320)];
    const first = planRoute(motorway(500), sts, V, planParams(90)).stops[0].station.id;
    const p = planRoute(motorway(500), sts.map((s) => (s.id === first ? { ...s, available: false } : s)), V, planParams(90));
    expect(p.feasible && !p.stops.some((s) => s.station.id === first)).toBe(true);
  });
  it("preferovaný operátor / ne absolutně / nejlevnější", () => {
    const a = planRoute(motorway(450), [st("x", 200, 150, { operator: "Jiný" }), st("pre", 205, 150, { operator: "PRE" })],
                        V, planParams(90, { mode: "vyvazeny" }), { tariffs: TARIFFS });
    expect(a.stops.map((s) => s.station.operator)).toEqual(["PRE"]);
    const b = planRoute(motorway(450), [st("x", 200, 150), st("pre", 205, 50, { operator: "PRE" })], V, planParams(90), { tariffs: TARIFFS });
    expect(b.stops.map((s) => s.station.operator)).toEqual(["Jiný"]);
    const c = planRoute(motorway(450), [st("e", 200, 150, { operator: "E.ON" }), st("l", 210, 150, { operator: "Lidl" }),
                                       st("p", 220, 150, { operator: "PRE" })], V, planParams(90, { mode: "nejlevnejsi" }), { tariffs: TARIFFS });
    expect(c.stops.map((s) => s.station.operator)).toEqual(["Lidl"]);
  });
  it("bez dat o nabíječkách / nedosažitelná mezera", () => {
    expect(planRoute(motorway(500), [], V, planParams(90)).reason).toContain("žádná použitelná nabíječka");
    expect(planRoute(motorway(520), [st("A", 50), st("B", 470)], V, planParams(80)).reason).toContain("km 470");
  });
});

describe("cesta a kalibrace", () => {
  const sts = Array.from({ length: 10 }, (_, k) => st(String(k), 100 + 50 * k));
  it("vyšší spotřeba → varování a přepočet", () => {
    const r = motorway(600);
    const prof = routeProfile(r, V, defaultEnergy(), "standard");
    const soc = 90 - (prof.energyBetween(0, 150) / V.usableKwh) * 100 - 12;
    const u = socUpdate(r, sts, V, planParams(90), { routeKm: 0, soc: 90 }, { routeKm: 150, soc });
    expect(u.kTrip).toBeGreaterThan(1.2);
    expect(u.warnings.some((w) => w.includes("níž"))).toBe(true);
    expect(u.plan.feasible).toBe(true);
  });
  it("kalibrace se smrštěním a odmítnutím odlehlých hodnot", () => {
    const cal = emptyCalibration();
    for (let i = 0; i < 5; i++) addObservation(cal, { kmByClass: { dalnice: 200 }, tempC: 0, predictedKwh: 50, socStart: 90, socEnd: 35 }, 100);
    const k = factor(cal, "dalnice", 0);
    expect(k).toBeGreaterThan(1.05);
    expect(k).toBeLessThanOrEqual(1.1);
    expect(factor(cal, "dalnice", 20)).toBe(1);
    expect(uncertainty(cal)).toBeLessThan(0.08);
    expect(addObservation(cal, { kmByClass: { dalnice: 100 }, tempC: 20, predictedKwh: 25, socStart: 90, socEnd: 50 }, 100)).toBe(false);
    expect(calibrationFn(cal)).toBeDefined();
  });
});

describe("křížová kontrola s Python jádrem", () => {
  const S = [st("A", 90, 150, { operator: "PRE", points: 2 }), st("B", 150, 50, { operator: "Lidl" }),
             st("C", 230, 300, { detourKm: 2, detourMin: 3 }), st("D", 330, 120, { operator: "PRE" }),
             st("E", 420, 75, { points: 1 }), st("F", 520, 200)];
  const routes: Record<string, Sec[]> = {
    mix: [[120, "dalnice", 130, 5, 300], [40, "prvni_trida", 90, 3, -100, "mokro"], [10, "mesto", 50, 2],
          [300, "dalnice", 130, -2, 0, "snih", 15]],
    leto: [[600, "dalnice", 130, 22]],
  };
  const tar = { PRE: tariff("PRE", 12.1, { preferred: true, member: true, priority: 1 }),
                Lidl: tariff("Lidl", 10, { preferred: true, priority: 2 }) };
  for (const c of golden.cases) {
    it(`${c.route} ${c.mode} SoC ${c.soc}${c.conservative ? " konzervativně" : ""}`, () => {
      const p = planRoute(makeRoute(routes[c.route]), S, V,
                          planParams(c.soc, { mode: c.mode as never, conservative: c.conservative }), { tariffs: tar });
      expect(p.feasible).toBe(c.feasible);
      expect(p.stops.map((s) => [s.station.id, s.arriveSoc, s.departSoc])).toEqual(c.stops);
      expect(p.totalMin).toBeCloseTo(c.total_min, 3);
      expect(p.costCzk).toBeCloseTo(c.cost, 2);
      expect(p.tripEnergyKwh).toBeCloseTo(c.energy, 3);
      expect(p.arrivalSoc).toBe(c.arrival_soc);
    });
  }
});

describe("přívěs", () => {
  it("+10 kWh/100 km na dálnici, +5 na okresní silnici", () => {
    const e = { ...defaultEnergy(), trailerMotorway: 10, trailerOther: 5 };
    const kwh = (r: Route, en = defaultEnergy()) => { const p = routeProfile(r, V, en, "rychly"); return p.kwh[p.kwh.length - 1]; };
    const dal = makeRoute([[100, "dalnice", 125, 20]]);
    const okr = makeRoute([[100, "okresni", 90, 20]]);
    expect(kwh(dal, e) - kwh(dal)).toBeCloseTo(10, 1);
    expect(kwh(okr, e) - kwh(okr)).toBeCloseTo(5, 1);
  });
  it("rychlost s přívěsem omezena (115 km/h): delší čas, okresky beze změny", () => {
    const e = { ...defaultEnergy(), maxSpeed: 115 };
    const min = (r: Route, en = defaultEnergy()) => { const p = routeProfile(r, V, en, "rychly"); return p.minutesBetween(0, p.totalKm); };
    expect(min(makeRoute([[115, "dalnice", 130, 20]]), e)).toBeCloseTo(60, 1);
    expect(min(makeRoute([[90, "okresni", 90, 20]]), e)).toBeCloseTo(60, 1);
  });
});
