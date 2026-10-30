export function hm(min: number): string {
  const m = Math.round(min);
  const h = Math.floor(m / 60);
  return h ? `${h} h ${String(m % 60).padStart(2, "0")} min` : `${m} min`;
}
export function clock(offsetMin: number, from: Date = new Date()): string {
  const d = new Date(from.getTime() + offsetMin * 60000);
  return d.toLocaleTimeString("cs-CZ", { hour: "2-digit", minute: "2-digit" });
}
let priceSuffix = "";
/** Nastaví popisek k cenám podle nastavení („bez DPH“ / „s DPH“). */
export function setPriceBasis(withoutVat: boolean) { priceSuffix = withoutVat ? " bez DPH" : ""; }
export const czk = (v: number) => `${Math.round(v).toLocaleString("cs-CZ")} Kč${priceSuffix}`;
export const km = (v: number) => `${Math.round(v).toLocaleString("cs-CZ")} km`;

export const VARIANT_LABEL: Record<string, string> = {
  nejrychlejsi: "Nejrychlejší", vyvazeny: "Vyvážená", nejlevnejsi: "Nejlevnější", eko: "Úsporná jízda",
};
export const VARIANT_HINT: Record<string, string> = {
  nejrychlejsi: "nejkratší celkový čas",
  vyvazeny: "čas + cena + preferované sítě",
  nejlevnejsi: "nejnižší cena nabíjení",
  eko: "nižší rychlost, méně nabíjení",
};
export const PROFILE_LABEL: Record<string, string> = { eko: "Ekonomická", standard: "Standardní", rychly: "Rychlá" };
