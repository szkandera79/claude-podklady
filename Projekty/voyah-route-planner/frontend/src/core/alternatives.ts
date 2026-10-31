/**
 * Záložní nabíječky ke každé zastávce plánu a levnější alternativy.
 * Pro každou zastávku: kandidáti do ±windowKm po trase (původní stanice vyřazena, jako by byla nefunkční) →
 * plán s povinnou zastávkou u kandidáta → rozdíl celkového času a ceny proti původnímu plánu.
 * Počítá se mimo hlavní výpočet (Web Worker), hlavní plánování nezdržuje.
 */
import { routeProfile } from "./energy";
import type { PlanParams, Route, Station, Vehicle } from "./models";
import { tariffForStation } from "./models";
import { costWeight, planRoute, usableStations, type Plan, type PlanOptions } from "./optimizer";

export interface Alternative {
  station: Station;
  plan: Plan;
  deltaMin: number;          // + = cesta delší
  deltaCzk: number;          // − = levnější
  score: number;             // menší = lepší (minuty + váha ceny dle režimu)
}

export interface StopAlternatives {
  stationId: string;
  backups: Alternative[];
  cheaper: Alternative | null;   // nejlevnější alternativa s úsporou ≥ savingCzk
}

export interface AlternativeOpts { perStop?: number; windowKm?: number; maxCandidates?: number; savingCzk?: number; }

export function stopAlternatives(route: Route, stations: Station[], v: Vehicle, p: PlanParams, o: PlanOptions,
                                 base: Plan, a: AlternativeOpts = {}): StopAlternatives[] {
  const perStop = a.perStop ?? 2;
  const windowKm = a.windowKm ?? 40;
  const maxCands = a.maxCandidates ?? 6;
  const tariffs = o.tariffs ?? {};
  const prof = o.profileCache ?? routeProfile(route, v, o.energy!, p.profile, o.calibration);
  const opts: PlanOptions = { ...o, profileCache: prof };
  const w = costWeight(p);
  const used = new Set(base.stops.map((s) => s.station.id));
  const all = usableStations(stations, v, p, tariffs, o.startKm ?? 0, prof.totalKm);

  return base.stops.map((stop) => {
    const without = stations.map((s) => (s.id === stop.station.id ? { ...s, available: false } : s));
    const rank = (s: Station) => {
      const t = tariffForStation(tariffs[s.operator], s.maxKw);
      return Math.abs(s.routeKm - stop.arriveKm) / 10 + s.detourKm
        - (t?.preferred ? 3 : 0) - (s.maxKw >= p.idealKwMin && s.maxKw <= p.idealKwMax ? 1 : 0) + (s.maxKw < 50 ? 4 : 0);
    };
    const cands = all.filter((s) => !used.has(s.id) && Math.abs(s.routeKm - stop.arriveKm) <= windowKm)
      .sort((x, y) => rank(x) - rank(y)).slice(0, maxCands);
    const alts: Alternative[] = [];
    for (const c of cands) {
      const plan = planRoute(route, without, v, p, { ...opts, requiredStationId: c.id });
      if (!plan.feasible) continue;
      const deltaMin = plan.totalMin - base.totalMin;
      const deltaCzk = plan.costCzk - base.costCzk;
      alts.push({ station: c, plan, deltaMin, deltaCzk, score: deltaMin + w * deltaCzk });
    }
    alts.sort((x, y) => x.score - y.score);
    const saving = a.savingCzk ?? Infinity;
    const cheaper = alts.filter((x) => -x.deltaCzk >= saving).sort((x, y) => x.deltaCzk - y.deltaCzk)[0] ?? null;
    return { stationId: stop.station.id, backups: alts.slice(0, perStop), cheaper };
  });
}
