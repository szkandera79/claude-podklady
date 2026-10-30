import type { Calibration, PlanRequest, PlanResult, Settings, SocUpdate, Trip } from "./types";

const TOKEN_KEY = "vrp_token";

function token(): string | null {
  try { return localStorage.getItem(TOKEN_KEY); } catch { return null; }
}
export function setToken(t: string): void {
  try { localStorage.setItem(TOKEN_KEY, t); } catch { /* soukromý režim */ }
}

export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

async function call<T>(method: string, path: string, body?: unknown): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const t = token();
  if (t) headers.Authorization = `Bearer ${t}`;
  let r: Response;
  try {
    r = await fetch(path, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
  } catch {
    throw new ApiError(0, "Server je nedostupný — zkontrolujte připojení k internetu.");
  }
  if (!r.ok) {
    let msg = `Chyba ${r.status}`;
    try { const j = await r.json(); msg = typeof j.detail === "string" ? j.detail : msg; } catch { /* */ }
    throw new ApiError(r.status, msg);
  }
  return r.json() as Promise<T>;
}

export const api = {
  plan: (req: PlanRequest) => call<PlanResult>("POST", "/api/plan", req),
  getPlan: (id: string) => call<PlanResult>("GET", `/api/plan/${id}`),
  startTrip: (plan_id: string, variant: string) =>
    call<{ trip_id: string }>("POST", "/api/trips", { plan_id, variant }),
  trip: (id: string) => call<Trip>("GET", `/api/trips/${id}`),
  soc: (id: string, soc: number, lat?: number, lon?: number, route_km?: number) =>
    call<SocUpdate>("POST", `/api/trips/${id}/soc`, { soc, lat, lon, route_km }),
  finish: (id: string, soc: number, lat?: number, lon?: number) =>
    call<{ ok: boolean; calibration: string }>("POST", `/api/trips/${id}/finish`, { soc, lat, lon }),
  settings: () => call<Settings>("GET", "/api/settings"),
  saveSettings: (s: Settings) => call<Settings>("PUT", "/api/settings", s),
  resetSettings: () => call<Settings>("POST", "/api/settings/reset"),
  calibration: () => call<Calibration>("GET", "/api/calibration"),
  resetCalibration: () => call<{ ok: boolean }>("POST", "/api/calibration/reset"),
};

export function currentPosition(): Promise<{ lat: number; lon: number }> {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) return reject(new Error("Zařízení neposkytuje polohu."));
    navigator.geolocation.getCurrentPosition(
      (p) => resolve({ lat: p.coords.latitude, lon: p.coords.longitude }),
      (e) => reject(new Error(e.code === 1 ? "Přístup k poloze byl zamítnut (Nastavení → Soukromí → Polohové služby)."
        : "Polohu se nepodařilo zjistit.")),
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 30000 });
  });
}
