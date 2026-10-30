/**
 * Optimalizace nabíjecích zastávek — DP nad stavem (uzel, SoC po 1 %) (přepis backend/vrp/optimizer.py).
 * Uzly: start, kandidátní stanice podél trasy, cíl; graf je acyklický → DP je exaktní.
 * Na stanici lze odjet s libovolným SoC nad příjezdem → cílové % nabití je výsledkem optimalizace.
 * Cílová funkce (minuty): čas + w_cena·Kč + penalizace − bonus preferované sítě (jen vyvážený režim).
 * SoC se zaokrouhluje dolů (konzervativně), chyba ≤ 1 % na úsek.
 */
import { ChargeTable, chargeCost, stationChargeTable } from "./charging";
import { CalibrationFn, RouteProfile, detourEnergy, routeProfile } from "./energy";
import type { DriveProfile, EnergyParams, Mode, PlanParams, Route, Station, Tariff, Vehicle } from "./models";
import { defaultEnergy } from "./models";

export const SINGLE_POINT_PENALTY_MIN = 2;
export const LOW_POWER_PENALTY_MIN = 10;
export const CHEAPEST_VOT_CZK_H = 30;
export const TIEBREAK_PER_SOC = 1e-3;

export interface StopPlan {
  station: Station;
  arriveKm: number;
  arriveSoc: number;
  departSoc: number;
  chargeMin: number;
  gridKwh: number;
  costCzk: number;
  avgKw: number;
  nextLegKm: number;
  arriveMin: number;
  departMin: number;
}

export interface Plan {
  feasible: boolean;
  reason: string;
  stops: StopPlan[];
  distanceKm: number;
  driveMin: number;
  chargeMin: number;
  stopOverheadMin: number;
  totalMin: number;
  costCzk: number;
  arrivalSoc: number;
  tripEnergyKwh: number;
  warnings: string[];
  profile: DriveProfile;
  mode: Mode;
}

interface Node {
  km: number;
  station?: Station;
  detKwh: number;
  detMin: number;
  detKm: number;
  table?: ChargeTable;
  tariff?: Tariff;
  penaltyMin: number;
  bonusMin: number;
}

type Parent = ["arr" | "dep", number, number] | null;
type Label = { obj: number; time: number; cost: number; parent: Parent };

function costWeight(p: PlanParams): number {
  if (p.mode === "nejrychlejsi") return 1e-4;
  if (p.mode === "nejlevnejsi") return 60 / CHEAPEST_VOT_CZK_H;
  return 60 / Math.max(p.valueOfTimeCzkH, 1);
}

export function usableStations(stations: Station[], v: Vehicle, p: PlanParams, tariffs: Record<string, Tariff>,
                               fromKm: number, toKm: number): Station[] {
  return stations
    .filter((s) => s.accessOk && s.connectors.includes(v.connector) && s.available !== false
      && s.routeKm > fromKm && s.routeKm < toKm
      && (!p.onlyPreferred || tariffs[s.operator]?.preferred))
    .sort((a, b) => a.routeKm - b.routeKm || (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
}

export interface PlanOptions {
  energy?: EnergyParams;
  tariffs?: Record<string, Tariff>;
  calibration?: CalibrationFn;
  startKm?: number;
  profileCache?: RouteProfile;
}

export function planRoute(route: Route, stations: Station[], v: Vehicle, p: PlanParams, o: PlanOptions = {}): Plan {
  const energy = o.energy ?? defaultEnergy();
  const tariffs = o.tariffs ?? {};
  const startKm = o.startKm ?? 0;
  const prof = o.profileCache ?? routeProfile(route, v, energy, p.profile, o.calibration);
  const endKm = prof.totalKm;
  const mult = p.energyFactor * (p.conservative ? 1 + energy.uncertainty : 1);
  const cap = v.usableKwh;
  const wCost = costWeight(p);

  const cands = usableStations(stations, v, p, tariffs, startKm, endKm);
  const nodes: Node[] = [{ km: startKm, detKwh: 0, detMin: 0, detKm: 0, penaltyMin: 0, bonusMin: 0 }];
  for (const s of cands) {
    const t = tariffs[s.operator];
    let pen = 0;
    if (s.points <= 1 && !s.isLiveStatus) pen += SINGLE_POINT_PENALTY_MIN;
    if (p.minStationKw && s.maxKw < p.minStationKw) pen += LOW_POWER_PENALTY_MIN;
    const bonus = p.mode === "vyvazeny" && t?.preferred ? p.preferredBonusMin / Math.max(t.priority, 1) : 0;
    nodes.push({ km: s.routeKm, station: s, detKwh: detourEnergy(s.detourKm, v, energy) * mult, detMin: s.detourMin,
                 detKm: s.detourKm, table: stationChargeTable(v, s, p.batteryTempC), tariff: t, penaltyMin: pen,
                 bonusMin: bonus });
  }
  nodes.push({ km: endKm, detKwh: 0, detMin: 0, detKm: 0, penaltyMin: 0, bonusMin: 0 });
  const n = nodes.length;
  const dest = n - 1;

  const arr: (Label | null)[][] = Array.from({ length: n }, () => new Array(101).fill(null));
  const dep: (Label | null)[][] = Array.from({ length: n }, () => new Array(101).fill(null));
  const startSoc = Math.floor(Math.min(p.startSoc, 100) + 1e-9);
  dep[0][startSoc] = { obj: 0, time: 0, cost: 0, parent: null };

  for (let i = 0; i < n - 1; i++) {
    const ni = nodes[i];
    if (ni.station && ni.table) {
      for (let a = 0; a <= 100; a++) {
        const la = arr[i][a];
        if (!la) continue;
        for (let b = a + 1; b <= 100; b++) {
          const tCh = ni.table.time(a, b);
          const kwh = ni.table.energy(a, b);
          const c = chargeCost(ni.tariff, kwh, tCh, p.defaultPriceKwh);
          const tAdd = tCh + p.stopOverheadMin;
          const bonus = ni.bonusMin * Math.min(1, kwh / 20);
          const obj = la.obj + tAdd + wCost * c + ni.penaltyMin - bonus + TIEBREAK_PER_SOC * a;
          const cur = dep[i][b];
          if (!cur || obj < cur.obj - 1e-9) dep[i][b] = { obj, time: la.time + tAdd, cost: la.cost + c, parent: ["arr", i, a] };
        }
      }
    }
    const states: [number, Label][] = [];
    dep[i].forEach((l, d) => { if (l) states.push([d, l]); });
    if (!states.length) continue;
    for (let j = i + 1; j < n; j++) {
      const nj = nodes[j];
      const e = prof.energyBetween(ni.km, nj.km) * mult + ni.detKwh + nj.detKwh;
      const ePct = (e / cap) * 100;
      if (ePct > 130) break;
      const t = prof.minutesBetween(ni.km, nj.km) + ni.detMin + nj.detMin;
      const reserve = j === dest ? p.reserveDestination : p.reserveStation;
      for (const [d, lab] of states) {
        const af = d - ePct;
        if (af < reserve - 1e-9) continue;
        const a = Math.floor(Math.min(af, 100) + 1e-9);
        const obj = lab.obj + t;
        const cur = arr[j][a];
        if (!cur || obj < cur.obj - 1e-9) arr[j][a] = { obj, time: lab.time + t, cost: lab.cost, parent: ["dep", i, d] };
      }
    }
  }

  let bestSoc = -1;
  let best: Label | null = null;
  arr[dest].forEach((l, a) => { if (l && (!best || l.obj < best.obj - 1e-9)) { best = l; bestSoc = a; } });
  if (!best) return infeasible(nodes, dep, p, prof, cap, mult, cands.length);
  return reconstruct(nodes, arr, dep, dest, bestSoc, p, prof, mult);
}

function reconstruct(nodes: Node[], arr: (Label | null)[][], dep: (Label | null)[][], dest: number, soc: number,
                     p: PlanParams, prof: RouteProfile, mult: number): Plan {
  const chain: { kind: "arr" | "dep"; idx: number; s: number; lab: Label }[] = [];
  let kind: "arr" | "dep" = "arr";
  let idx = dest;
  let s = soc;
  for (;;) {
    const lab: Label = (kind === "arr" ? arr : dep)[idx][s]!;
    chain.push({ kind, idx, s, lab });
    if (!lab.parent) break;
    [kind, idx, s] = lab.parent;
  }
  chain.reverse();

  const stops: StopPlan[] = [];
  chain.forEach((c, k) => {
    const nd = nodes[c.idx];
    if (c.kind === "dep" && nd.station && nd.table) {
      const prev = chain[k - 1];
      const a = prev.s;
      const tCh = nd.table.time(a, c.s);
      const kwh = nd.table.energy(a, c.s);
      stops.push({ station: nd.station, arriveKm: nd.km, arriveSoc: a, departSoc: c.s, chargeMin: tCh, gridKwh: kwh,
                   costCzk: chargeCost(nd.tariff, kwh, tCh, p.defaultPriceKwh), avgKw: tCh > 0 ? kwh / (tCh / 60) : 0,
                   nextLegKm: 0, arriveMin: prev.lab.time, departMin: c.lab.time });
    }
  });
  stops.forEach((st, k) => {
    const nxt = k + 1 < stops.length ? stops[k + 1].arriveKm : prof.totalKm;
    st.nextLegKm = nxt - st.arriveKm;
  });
  const final = arr[dest][soc]!;
  const chargeMin = stops.reduce((a, x) => a + x.chargeMin, 0);
  const overhead = p.stopOverheadMin * stops.length;
  const startKm = nodes[0].km;
  const usedIds = new Set(stops.map((x) => x.station.id));
  const detKm = nodes.filter((nd) => nd.station && usedIds.has(nd.station.id)).reduce((a, nd) => a + 2 * nd.detKm, 0);
  const warnings: string[] = [];
  for (const st of stops) {
    const s = st.station;
    if (!s.isLiveStatus) warnings.push(`${s.name}: dostupnost neověřena (data ${s.dataSource || "bez zdroje"}${s.dataUpdated ? ", " + s.dataUpdated : ""}).`);
    for (const note of s.notes) warnings.push(`${s.name}: ${note}`);
  }
  return { feasible: true, reason: "", stops, distanceKm: prof.totalKm - startKm + detKm,
           driveMin: final.time - chargeMin - overhead, chargeMin, stopOverheadMin: overhead, totalMin: final.time,
           costCzk: final.cost, arrivalSoc: soc, tripEnergyKwh: prof.energyBetween(startKm, prof.totalKm) * mult,
           warnings, profile: p.profile, mode: p.mode };
}

function infeasible(nodes: Node[], dep: (Label | null)[][], p: PlanParams, prof: RouteProfile, cap: number,
                    mult: number, candCount: number): Plan {
  let far = 0;
  for (let i = 0; i < nodes.length - 1; i++) if (dep[i].some((x) => x) && nodes[i].km >= nodes[far].km) far = i;
  const nf = nodes[far];
  let bestD = 0;
  dep[far].forEach((x, d) => { if (x) bestD = d; });
  const where = nf.station ? nf.station.name : "start";
  let reason: string;
  if (!candCount) {
    reason = `V datech není žádná použitelná nabíječka (CCS2, přístupná) na trase a cíl není dosažitelný s rezervou ${p.reserveDestination.toFixed(0)} %. Zkontrolujte zdroj dat nabíječek.`;
  } else {
    const target = nodes[far + 1];
    const need = (prof.energyBetween(nf.km, target.km) * mult / cap) * 100;
    const name = target.station ? target.station.name : "cíl";
    const reserve = target.station ? p.reserveStation : p.reserveDestination;
    reason = `Bezpečný plán neexistuje: z místa „${where}“ (km ${nf.km.toFixed(0)}, max. ${bestD} %) na „${name}“ (km ${target.km.toFixed(0)}) je potřeba ~${need.toFixed(0)} % + rezerva ${reserve.toFixed(0)} %. Zvažte nižší rychlost, menší rezervu nebo delší zajížďku k nabíječce.`;
  }
  return { feasible: false, reason, stops: [], distanceKm: 0, driveMin: 0, chargeMin: 0, stopOverheadMin: 0, totalMin: 0,
           costCzk: 0, arrivalSoc: 0, tripEnergyKwh: 0, warnings: [], profile: p.profile, mode: p.mode };
}
