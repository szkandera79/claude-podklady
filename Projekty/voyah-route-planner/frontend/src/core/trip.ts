/**
 * Aktivní cesta: ruční SoC → porovnání s predikcí → přepočet (přepis backend/vrp/trip.py).
 * Krátkodobá odchylka k_trip platí jen pro zbytek cesty; dlouhodobý profil mění až kalibrace po cestě.
 */
import type { CalibrationFn } from "./energy";
import { routeProfile } from "./energy";
import type { EnergyParams, PlanParams, Route, Station, Tariff, Vehicle } from "./models";
import { defaultEnergy } from "./models";
import { Plan, planRoute } from "./optimizer";

export const K_TRIP_MIN = 0.7;
export const K_TRIP_MAX = 1.6;
export const FULL_WEIGHT_KWH = 20;
export const WARN_DEVIATION_PCT = 5;

export interface SocReading { routeKm: number; soc: number; }

export interface TripUpdate {
  predictedSoc: number;
  actualSoc: number;
  measuredRatio: number;
  kTrip: number;
  plan: Plan;
  warnings: string[];
}

export function socUpdate(route: Route, stations: Station[], v: Vehicle, p: PlanParams, ref: SocReading,
                          cur: SocReading, energy: EnergyParams = defaultEnergy(),
                          tariffs: Record<string, Tariff> = {}, calibration?: CalibrationFn,
                          previous?: Plan): TripUpdate {
  const prof = routeProfile(route, v, energy, p.profile, calibration);
  const predictedKwh = prof.energyBetween(ref.routeKm, cur.routeKm);
  const predictedPct = (predictedKwh / v.usableKwh) * 100;
  const usedKwh = ((ref.soc - cur.soc) / 100) * v.usableKwh;
  const ratio = predictedKwh > 0.5 ? usedKwh / predictedKwh : 1;
  const w = Math.min(1, Math.max(usedKwh, 0) / FULL_WEIGHT_KWH);
  const kTrip = Math.min(K_TRIP_MAX, Math.max(K_TRIP_MIN, 1 + (ratio - 1) * w));

  const plan = planRoute(route, stations, v, { ...p, startSoc: cur.soc, energyFactor: kTrip },
                         { energy, tariffs, calibration, startKm: cur.routeKm, profileCache: prof });
  const warnings: string[] = [];
  const predictedSoc = ref.soc - predictedPct;
  const dev = cur.soc - predictedSoc;
  if (dev <= -WARN_DEVIATION_PCT) {
    const pct = Math.round(ratio * 100 - 100);
    warnings.push(`Baterie je o ${Math.round(-dev)} % níž, než předpokládal plán (spotřeba ≈ ${pct >= 0 ? "+" : ""}${pct} % proti modelu). Zbytek cesty počítán se zvýšenou spotřebou.`);
  }
  if (!plan.feasible) warnings.push("POZOR: se současnou spotřebou nelze bezpečně dojet. " + plan.reason);
  else if (plan.stops.length && plan.stops[0].arriveSoc < p.reserveStation + 3)
    warnings.push(`Příjezd k další nabíječce jen s ${plan.stops[0].arriveSoc} % — zvažte nižší rychlost.`);
  if (previous && plan.feasible) {
    const old = previous.stops.filter((s) => s.arriveKm > cur.routeKm).map((s) => s.station.id).join("|");
    const now = plan.stops.map((s) => s.station.id).join("|");
    if (old !== now) warnings.push(now ? "Plán zastávek se změnil: " + plan.stops.map((s) => s.station.name).join(" → ")
                                       : "Plán zastávek se změnil: další nabíjení už není potřeba.");
  }
  return { predictedSoc, actualSoc: cur.soc, measuredRatio: ratio, kTrip, plan, warnings };
}
