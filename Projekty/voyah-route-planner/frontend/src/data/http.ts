/** HTTP z prohlížeče s časovým limitem a cache v IndexedDB (klíče API se do klíče cache nezapočítávají). */
import { idbDel, idbGet, idbKeys, idbPut } from "../local/idb";

export class SourceError extends Error {}

interface Cached { ts: number; data: unknown; }

async function hash(s: string): Promise<string> {
  if (globalThis.crypto?.subtle) {
    const b = await crypto.subtle.digest("SHA-1", new TextEncoder().encode(s));
    return [...new Uint8Array(b)].map((x) => x.toString(16).padStart(2, "0")).join("");
  }
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (Math.imul(31, h) + s.charCodeAt(i)) | 0;
  return String(h);
}

export interface RequestOpts {
  params?: Record<string, string | number>;
  body?: unknown;
  form?: boolean;
  headers?: Record<string, string>;
  timeoutS?: number;
  cacheKind?: string;
  ttlS?: number;
  referrerPolicy?: ReferrerPolicy;     // Nominatim chce identifikaci aplikace (stačí origin)
}

export async function requestJson<T = any>(url: string, o: RequestOpts = {}): Promise<T> {
  const full = o.params ? `${url}?${new URLSearchParams(Object.entries(o.params).map(([k, v]) => [k, String(v)]))}` : url;
  const host = new URL(url).host;
  let key = "";
  if (o.cacheKind && o.ttlS) {
    key = `${o.cacheKind}:${await hash(full + "|" + (o.body === undefined ? "" : JSON.stringify(o.body)))}`;
    const c = await idbGet<Cached>("cache", key);
    if (c && Date.now() - c.ts < o.ttlS * 1000) return c.data as T;
  }
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), (o.timeoutS ?? 30) * 1000);
  const headers: Record<string, string> = { Accept: "application/json, */*", ...(o.headers || {}) };
  let body: BodyInit | undefined;
  if (o.body !== undefined) {
    if (o.form) {
      body = new URLSearchParams(o.body as Record<string, string>);
      headers["Content-Type"] = "application/x-www-form-urlencoded";
    } else {
      body = JSON.stringify(o.body);
      headers["Content-Type"] = "application/json";
    }
  }
  let data: T;
  try {
    const r = await fetch(full, { method: body ? "POST" : "GET", headers, body, signal: ctrl.signal, referrerPolicy: o.referrerPolicy });
    if (!r.ok) throw new SourceError(`${host}: HTTP ${r.status}`);
    data = (await r.json()) as T;
  } catch (e) {
    if (e instanceof SourceError) throw e;
    throw new SourceError(`${host}: ${(e as Error).name === "AbortError" ? "timeout" : "nedostupné"}`);
  } finally {
    clearTimeout(timer);
  }
  if (key) await idbPut("cache", key, { ts: Date.now(), data } satisfies Cached);
  return data;
}

/** Smaže z cache položky starší než 30 dní (volá se při startu). */
export async function pruneCache(maxAgeS = 30 * 86400): Promise<void> {
  for (const k of await idbKeys("cache")) {
    const c = await idbGet<Cached>("cache", k);
    if (!c || Date.now() - c.ts > maxAgeS * 1000) await idbDel("cache", k);
  }
}
