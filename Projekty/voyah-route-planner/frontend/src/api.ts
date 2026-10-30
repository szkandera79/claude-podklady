/** Rozhraní pro obrazovky. Vše se počítá v telefonu (local/service.ts) — žádný vlastní server. */
import { ApiError, service } from "./local/service";

export { ApiError };
export const api = service;

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
