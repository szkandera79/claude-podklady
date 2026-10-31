/** Záložní stanice, povinná stanice, max. zajížďka, ideální výkon — SYNTETICKÉ stanice. */
import { describe, expect, it } from "vitest";
import { stopAlternatives } from "./alternatives";
import { defaultEnergy, defaultVehicle, planParams, segment, station, tariff } from "./models";
import { planRoute } from "./optimizer";

const V = defaultVehicle();
const road = (km: number) => ({ segments: Array.from({ length: km }, () => segment(1, "dalnice", 130)) });
const R = road(500);
const ST = [
  station("a", 180, 150, { operator: "PRE", points: 4 }), station("b", 200, 89, { operator: "Lidl", points: 4 }),
  station("c", 215, 75, { operator: "ČEZ", points: 4 }), station("d", 260, 50, { operator: "Jiný", points: 4 }),
  station("e", 160, 100, { operator: "E.ON", points: 4 }), station("f", 235, 75, { operator: "Jiný", points: 2 }),
  station("far", 205, 150, { operator: "PRE", points: 4, detourKm: 15, detourMin: 20 }),
];
const TAR = { PRE: tariff("PRE", 10, { preferred: true, priority: 1 }), Lidl: tariff("Lidl", 11, { preferred: true, priority: 2 }),
              "ČEZ": tariff("ČEZ", 16) };
const P = planParams(80, { mode: "vyvazeny", maxDetourKm: 8, idealBonusMin: 2 });
const O = { energy: defaultEnergy(), tariffs: TAR };

describe("výběr a záložní stanice", () => {
  it("bonus preferované sítě nepřidá zastávku navíc", () => {
    const plain = planRoute(R, ST, V, { ...P, idealBonusMin: 0, preferredBonusMin: 0 }, O);
    expect(planRoute(R, ST, V, P, O).stops.length).toBe(plain.stops.length);
  });
  it("zajížďka nad limit se nepoužije", () => {
    const p = planRoute(R, ST, V, P, O);
    expect(p.feasible).toBe(true);
    expect(p.stops.map((s) => s.station.id)).not.toContain("far");
  });
  it("povinná stanice je v plánu, nedosažitelná vrátí důvod", () => {
    const p = planRoute(R, ST, V, P, { ...O, requiredStationId: "c" });
    expect(p.stops.map((s) => s.station.id)).toContain("c");
    const bad = planRoute(road(600), [station("z", 590, 150, { points: 4 })], V, planParams(80), { ...O, requiredStationId: "z" });
    expect(bad.feasible).toBe(false);
    expect(bad.reason).toMatch(/nelze bezpečně dojet/);
  });
  it("ke každé zastávce 2 dosažitelné zálohy bez původní stanice", () => {
    const base = planRoute(R, ST, V, P, O);
    const alts = stopAlternatives(R, ST, V, P, O, base, { savingCzk: 50 });
    expect(alts).toHaveLength(base.stops.length);
    for (const [k, a] of alts.entries()) {
      expect(a.backups.length).toBe(2);
      for (const b of a.backups) {
        expect(b.plan.feasible).toBe(true);
        expect(b.station.id).not.toBe(base.stops[k].station.id);
        expect(b.plan.stops.map((s) => s.station.id)).not.toContain(base.stops[k].station.id);
        expect(b.plan.stops.every((s) => s.arriveSoc >= P.reserveStation)).toBe(true);
      }
    }
  });
  it("výpočet záloh je rychlý (< 300 ms)", () => {
    const many = Array.from({ length: 150 }, (_, i) => station(`s${i}`, 5 + i * 3.3, [50, 75, 150][i % 3], { points: 4 }));
    const r = road(500);
    const base = planRoute(r, many, V, P, O);
    const t0 = performance.now();
    stopAlternatives(r, many, V, P, O, base);
    expect(performance.now() - t0).toBeLessThan(300);
  });
});
