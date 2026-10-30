/**
 * Klíče API (openrouteservice, Open Charge Map) — NEJSOU v kódu aplikace. Ukládají se jen v telefonu (localStorage)
 * a předávají se nastavovacím odkazem: https://…/#setup=<base64 JSON>. Část za „#“ prohlížeč nikdy neposílá na server;
 * aplikace ji po uložení z adresy smaže.
 */
export interface ApiKeys { ors?: string; ocm?: string; }
const KEY = "vrp_keys";

export function getKeys(): ApiKeys {
  try { return JSON.parse(localStorage.getItem(KEY) || "{}"); } catch { return {}; }
}

export function setKeys(k: ApiKeys): void {
  const clean: ApiKeys = {};
  if (k.ors?.trim()) clean.ors = k.ors.trim();
  if (k.ocm?.trim()) clean.ocm = k.ocm.trim();
  try { localStorage.setItem(KEY, JSON.stringify(clean)); } catch { /* soukromý režim */ }
}

export function encodeSetup(k: ApiKeys): string {
  return btoa(unescape(encodeURIComponent(JSON.stringify(k)))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

export function decodeSetup(s: string): ApiKeys | null {
  try {
    const b = s.replace(/-/g, "+").replace(/_/g, "/");
    const d = JSON.parse(decodeURIComponent(escape(atob(b + "===".slice((b.length + 3) % 4)))));
    return typeof d === "object" && d ? { ors: d.ors, ocm: d.ocm } : null;
  } catch { return null; }
}

/** Z naskenovaného textu (nastavovací odkaz) uloží klíče; vrací seznam uložených klíčů nebo null. */
export function applySetupText(text: string): string[] | null {
  const m = text.match(/setup=([A-Za-z0-9_-]+)/);
  const k = m ? decodeSetup(m[1]) : null;
  if (!k || (!k.ors && !k.ocm)) return null;
  setKeys({ ...getKeys(), ...k });
  return [k.ors ? "openrouteservice" : "", k.ocm ? "Open Charge Map" : ""].filter(Boolean);
}

/** Při startu: převezme klíče z #setup=… a adresu vyčistí. Vrací true, pokud se klíče uložily. */
export function consumeSetupLink(): boolean {
  const m = location.hash.match(/setup=([A-Za-z0-9_-]+)/);
  if (!m) return false;
  const k = decodeSetup(m[1]);
  history.replaceState(null, "", location.pathname + location.search);
  if (!k) return false;
  setKeys({ ...getKeys(), ...k });
  return true;
}
