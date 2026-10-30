/**
 * Transparentní kalibrace spotřeby (přepis backend/vrp/calibration.py, ANALYZA.md kap. 8).
 * k_nový = (n·k_starý + w·k_změřený) / (n + w), w = spotřebovaná energie / 10 kWh; odlehlé (|k−1| > 0,4) se neaplikují.
 */
import type { RoadClass } from "./models";

export const TEMP_BANDS: [number, number][] = [[-99, -5], [-5, 5], [5, 15], [15, 25], [25, 99]];
export const GROUP: Record<RoadClass, string> = {
  dalnice: "dalnice", rychlostni: "dalnice", prvni_trida: "silnice", okresni: "silnice", mesto: "mesto",
};
const PRIOR_WEIGHT = 2;
const OUTLIER = 0.4;
const WEIGHT_KWH = 10;

export function tempBand(t: number): number {
  const i = TEMP_BANDS.findIndex(([lo, hi]) => lo <= t && t < hi);
  return i < 0 ? TEMP_BANDS.length - 1 : i;
}

export interface Observation {
  kmByClass: Partial<Record<RoadClass, number>>;
  tempC: number;
  predictedKwh: number;
  socStart: number;
  socEnd: number;
  applied?: boolean;
  ts?: number;
}

export interface CalibrationData {
  cells: Record<string, [number, number]>;     // "skupina|pásmo" → [k, váha]
  observations: Observation[];
}

export const emptyCalibration = (): CalibrationData => ({ cells: {}, observations: [] });

export function factor(cal: CalibrationData, rc: RoadClass, t: number): number {
  return cal.cells[`${GROUP[rc]}|${tempBand(t)}`]?.[0] ?? 1;
}

export function calibrationFn(cal: CalibrationData) {
  return Object.keys(cal.cells).length ? (rc: RoadClass, t: number) => factor(cal, rc, t) : undefined;
}

/** Přidá pozorování (mutuje `cal`); vrací true, pokud vstoupilo do modelu. */
export function addObservation(cal: CalibrationData, obs: Observation, usableKwh: number): boolean {
  cal.observations.push(obs);
  if (cal.observations.length > 500) cal.observations.splice(0, cal.observations.length - 500);
  const measured = ((obs.socStart - obs.socEnd) / 100) * usableKwh;
  obs.applied = false;
  if (obs.predictedKwh <= 0 || measured <= 0) return false;
  const ratio = measured / obs.predictedKwh;
  if (Math.abs(ratio - 1) > OUTLIER) return false;
  const total = Object.values(obs.kmByClass).reduce((a, b) => a + (b || 0), 0) || 1;
  const band = tempBand(obs.tempC);
  for (const [rc, km] of Object.entries(obs.kmByClass) as [RoadClass, number][]) {
    const key = `${GROUP[rc]}|${band}`;
    const [kOld, n] = cal.cells[key] ?? [1, PRIOR_WEIGHT];
    const w = (measured / WEIGHT_KWH) * (km / total);
    cal.cells[key] = [(n * kOld + w * ratio) / (n + w), n + w];
  }
  obs.applied = true;
  return true;
}

export function uncertainty(cal: CalibrationData, base = 0.08): number {
  const extra = Object.values(cal.cells).reduce((a, [, n]) => a + Math.max(n - PRIOR_WEIGHT, 0), 0);
  return Math.max(0.03, base / Math.sqrt(1 + extra / 5));
}
