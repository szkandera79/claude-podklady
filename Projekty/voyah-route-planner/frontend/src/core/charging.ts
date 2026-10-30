/**
 * Doba a cena nabíjení (přepis backend/vrp/charging.py).
 * P = min( křivka_vozu(SoC) × k_teplota_baterie , výkon_stanice × k_sdílení ); křivka je na straně stojanu
 * (záznam PRE 22. 1. 2026: 89,95 kW, ≈1,01 kWh ze stojanu na 1 %), čas = energie ze stojanu / P.
 */
import type { Station, Tariff, Vehicle } from "./models";

export const SHARED_POWER_FACTOR = 0.5;

/** Předpoklad ke kalibraci: 0,6 při −10 °C → 1,0 při +15 °C. */
export function batteryTempFactor(t: number | null): number {
  if (t === null || t >= 15) return 1;
  return Math.max(0.6, 0.6 + (0.4 * (t + 10)) / 25);
}

export function effectivePower(v: Vehicle, stationKw: number, soc: number, shared = false,
                               battTemp: number | null = null): number {
  const car = v.curve.powerAt(soc) * batteryTempFactor(battTemp);
  const stall = stationKw * (shared ? SHARED_POWER_FACTOR : 1);
  return Math.max(0.1, Math.min(car, stall));
}

/** Kumulativní minuty a kWh ze stojanu od 0 % po každé celé %; dotaz a→b je O(1). */
export class ChargeTable {
  constructor(public minutes: number[], public gridKwh: number[]) {}
  time(a: number, b: number) { return this.minutes[b] - this.minutes[a]; }
  energy(a: number, b: number) { return this.gridKwh[b] - this.gridKwh[a]; }
}

export function buildChargeTable(v: Vehicle, stationKw: number, shared = false,
                                 battTemp: number | null = null): ChargeTable {
  const step = v.usableKwh / 100 / v.chargeEfficiency;
  const minutes = [0];
  const grid = [0];
  for (let s = 0; s < 100; s++) {
    const p = effectivePower(v, stationKw, s + 0.5, shared, battTemp);
    minutes.push(minutes[s] + (step / p) * 60);
    grid.push(grid[s] + step);
  }
  return new ChargeTable(minutes, grid);
}

export function chargeCost(t: Tariff | undefined, kwh: number, minutes: number, defaultPrice: number): number {
  if (!t) return kwh * defaultPrice;
  let c = kwh * t.priceKwh + minutes * t.priceMin + t.sessionFee;
  if (minutes > t.blockingAfterMin) c += (minutes - t.blockingAfterMin) * t.blockingFeeMin;
  return c;
}

export const stationChargeTable = (v: Vehicle, s: Station, battTemp: number | null = null) =>
  buildChargeTable(v, s.maxKw, s.sharedPower, battTemp);

/** Využitelná kapacita z nabíjení: energie do baterie / ΔSoC. */
export const estimateUsableKwh = (gridKwh: number, from: number, to: number, eff = 0.95) =>
  (gridKwh * eff) / ((to - from) / 100);
