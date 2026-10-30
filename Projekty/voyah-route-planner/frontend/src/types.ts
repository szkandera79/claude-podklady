export interface StationBrief {
  id: string; name: string; operator: string; lat: number | null; lon: number | null; max_kw: number;
  points: number; address: string; route_km: number; detour_km: number; source: string;
  updated: string | null; notes: string[];
}
export interface Stop {
  station: StationBrief; arrive_km: number; arrive_soc: number; depart_soc: number; charge_min: number;
  grid_kwh: number; cost_czk: number; avg_kw: number; next_leg_km: number; arrive_min: number; depart_min: number;
}
export interface Plan {
  feasible: boolean; reason: string; mode: string; profile: string; distance_km: number; drive_min: number;
  charge_min: number; stop_overhead_min: number; total_min: number; cost_czk: number; arrival_soc: number;
  trip_energy_kwh: number; warnings: string[]; stops: Stop[];
}
export interface PlanRequest {
  origin: string; destination: string; via: string[]; soc: number;
  reserve_destination?: number; reserve_station?: number; profile?: string; conservative?: boolean;
}
export interface PlanResult {
  plan_id: string; origin: string; destination: string; route_source: string; distance_km: number;
  geometry: [number, number][]; notes: string[]; calibrated: boolean; attribution: string;
  plans: Record<string, Plan>; stations: StationBrief[]; request: PlanRequest;
}
export interface SocUpdate {
  route_km: number; offroute_km: number; remaining_km: number; actual_soc: number;
  predicted_soc: number | null; measured_ratio: number | null; k_trip: number; warnings: string[]; plan: Plan;
}
export interface Reading { route_km: number; soc: number; ts: number; kind: string; }
export interface Trip {
  id: string; plan_id: string; variant: string; created: number; finished: number | null;
  state: { reference: { km: number; soc: number }; k_trip: number; plan: Plan };
  readings: Reading[]; plan_result: PlanResult;
}
export interface TariffTierSetting { from_kw: number; price: number; price_min?: number; after_min?: number; }
export interface Tariff {
  operator: string; price: number; includes_vat: boolean; price_min?: number; session_fee?: number;
  blocking_fee_min?: number; blocking_after_min?: number; preferred: boolean; member: boolean; priority: number;
  payment?: string; note?: string; tiers?: TariffTierSetting[];
}
export interface Settings {
  vehicle: { name: string; usable_kwh: number; charge_efficiency: number; mass_kg: number; extra_load_kg: number;
             curve: [number, number][] };
  energy: Record<string, number>;
  planning: { reserve_station: number; reserve_destination: number; profile: string; conservative: boolean;
              stop_overhead_min: number; value_of_time_czk_h: number; min_station_kw: number;
              only_preferred: boolean; corridor_km: number; default_price_kwh: number; prices_without_vat?: boolean; tesla_ok?: boolean };
  tariffs: Tariff[];
  tariffs_version?: number;
}
export interface Calibration {
  cells: { group: string; band: number; factor: number; weight: number }[];
  uncertainty: number;
  observations: { km: Record<string, number>; temp_c: number; predicted_kwh: number; soc_start: number;
                  soc_end: number; applied: boolean }[];
}
