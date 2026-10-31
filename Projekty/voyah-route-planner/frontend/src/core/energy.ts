/**
 * Energetický model jízdy (přepis backend/vrp/energy.py, ANALYZA.md kap. 5).
 * E_úsek = [ c(v_vzduch)·d + E_převýšení + P_HVAC(T)·t ] × f_vozovka × f_baterie(T) × k_kalibrace
 */
import type { DriveProfile, EnergyParams, RoadClass, Route, Segment, Vehicle } from "./models";
import { segment } from "./models";

const G = 9.81;
const J_PER_KWH = 3.6e6;
export const ECO_CAP: Record<RoadClass, number> = { dalnice: 110, rychlostni: 100, prvni_trida: 80, okresni: 80, mesto: 50 };
export const CITY_TRAFFIC_FACTOR = 0.7;

export type CalibrationFn = (rc: RoadClass, tempC: number) => number;

export function plannedSpeed(seg: Segment, profile: DriveProfile): number {
  const lim = seg.speedLimit;
  if (seg.roadClass === "mesto") {
    const base = lim * CITY_TRAFFIC_FACTOR;
    return profile === "eko" ? Math.min(base, ECO_CAP.mesto * CITY_TRAFFIC_FACTOR) : base;
  }
  if (profile === "eko") return Math.min(lim, ECO_CAP[seg.roadClass]);
  if (profile === "standard") return lim * 0.95;
  return lim;
}

export function consumptionPer100(v: number, p: EnergyParams, rc: RoadClass = "dalnice", headwind = 0): number {
  const va = v + headwind;
  let c = p.a + p.b * va * Math.abs(va);
  if (rc === "mesto") c += p.cityExtra;
  return Math.max(c, 0);
}

export function hvacKw(t: number, p: EnergyParams): number {
  if (t < p.heatStartC) return p.heatBaseKw + p.heatKwPerC * (p.heatStartC - t);
  if (t > p.coolStartC) return p.coolKw;
  return 0;
}

export const batteryFactor = (t: number, p: EnergyParams) => 1 + p.battTempCoef * Math.max(0, 15 - t);

export interface SegmentResult { speed: number; minutes: number; kwh: number; }

export function segmentEnergy(seg: Segment, v: Vehicle, p: EnergyParams, profile: DriveProfile,
                              cal?: CalibrationFn): SegmentResult {
  const planned = plannedSpeed(seg, profile);
  const speed = p.maxSpeed > 0 ? Math.min(planned, p.maxSpeed) : planned;
  const hours = seg.lengthKm / speed;
  const trailer = seg.roadClass === "dalnice" || seg.roadClass === "rychlostni" ? p.trailerMotorway ?? 0 : p.trailerOther ?? 0;
  const drive = ((consumptionPer100(speed, p, seg.roadClass, seg.headwindKmh) + trailer) / 100) * seg.lengthKm;
  const m = v.massKg + v.extraLoadKg;
  const dz = seg.elevationDeltaM;
  const elev = dz >= 0 ? (m * G * dz) / p.driveEfficiency / J_PER_KWH : (m * G * dz * p.regenEfficiency) / J_PER_KWH;
  const hvac = hvacKw(seg.tempC, p) * hours;
  let kwh = (drive * p.surfaceFactor[seg.surface] + elev + hvac) * batteryFactor(seg.tempC, p);
  if (cal) kwh *= cal(seg.roadClass, seg.tempC);
  return { speed, minutes: hours * 60, kwh };
}

/** Kumulativní km, minuty a kWh podél trasy; dotaz na libovolnou polohu lineární interpolací. */
export class RouteProfile {
  constructor(public km: number[], public minutes: number[], public kwh: number[]) {}

  private interp(arr: number[], x: number): number {
    const km = this.km;
    if (x <= 0) return arr[0];
    if (x >= km[km.length - 1]) return arr[arr.length - 1];
    let lo = 0;
    let hi = km.length - 1;
    while (hi - lo > 1) {
      const mid = (lo + hi) >> 1;
      if (km[mid] <= x) lo = mid; else hi = mid;
    }
    const f = (x - km[lo]) / (km[lo + 1] - km[lo]);
    return arr[lo] + f * (arr[lo + 1] - arr[lo]);
  }

  energyBetween(a: number, b: number) { return this.interp(this.kwh, b) - this.interp(this.kwh, a); }
  minutesBetween(a: number, b: number) { return this.interp(this.minutes, b) - this.interp(this.minutes, a); }
  get totalKm() { return this.km[this.km.length - 1]; }
}

export function routeProfile(route: Route, v: Vehicle, p: EnergyParams, profile: DriveProfile,
                             cal?: CalibrationFn): RouteProfile {
  const km = [0];
  const mins = [0];
  const kwh = [0];
  for (const seg of route.segments) {
    const r = segmentEnergy(seg, v, p, profile, cal);
    km.push(km[km.length - 1] + seg.lengthKm);
    mins.push(mins[mins.length - 1] + r.minutes);
    kwh.push(kwh[kwh.length - 1] + r.kwh);
  }
  return new RouteProfile(km, mins, kwh);
}

/** Energie zajížďky jedním směrem — okresní silnice 50 km/h. */
export function detourEnergy(detourKm: number, v: Vehicle, p: EnergyParams, tempC = 20): number {
  if (detourKm <= 0) return 0;
  return segmentEnergy(segment(detourKm, "okresni", 50, { tempC }), v, p, "rychly").kwh;
}
