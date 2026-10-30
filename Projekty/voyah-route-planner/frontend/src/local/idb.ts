/** Minimální IndexedDB úložiště v telefonu: "kv" (nastavení, plány, cesty, kalibrace) a "cache" (odpovědi služeb). */
const DB = "voyah-planner";
const STORES = ["kv", "cache"] as const;
type StoreName = (typeof STORES)[number];

let dbp: Promise<IDBDatabase> | null = null;
const mem: Record<StoreName, Map<string, unknown>> = { kv: new Map(), cache: new Map() };   // záloha bez IndexedDB

function db(): Promise<IDBDatabase> {
  if (!dbp) {
    dbp = new Promise((resolve, reject) => {
      if (typeof indexedDB === "undefined") return reject(new Error("bez IndexedDB"));
      const r = indexedDB.open(DB, 1);
      r.onupgradeneeded = () => STORES.forEach((s) => r.result.objectStoreNames.contains(s) || r.result.createObjectStore(s));
      r.onsuccess = () => resolve(r.result);
      r.onerror = () => reject(r.error);
    });
  }
  return dbp;
}

function tx<T>(store: StoreName, mode: IDBTransactionMode, fn: (s: IDBObjectStore) => IDBRequest): Promise<T> {
  return db().then((d) => new Promise<T>((resolve, reject) => {
    const req = fn(d.transaction(store, mode).objectStore(store));
    req.onsuccess = () => resolve(req.result as T);
    req.onerror = () => reject(req.error);
  }));
}

export async function idbGet<T>(store: StoreName, key: string): Promise<T | undefined> {
  try { return await tx<T | undefined>(store, "readonly", (s) => s.get(key)); }
  catch { return mem[store].get(key) as T | undefined; }
}
export async function idbPut(store: StoreName, key: string, value: unknown): Promise<void> {
  try { await tx(store, "readwrite", (s) => s.put(value, key)); }
  catch { mem[store].set(key, value); }
}
export async function idbDel(store: StoreName, key: string): Promise<void> {
  try { await tx(store, "readwrite", (s) => s.delete(key)); }
  catch { mem[store].delete(key); }
}
export async function idbKeys(store: StoreName): Promise<string[]> {
  try { return (await tx<IDBValidKey[]>(store, "readonly", (s) => s.getAllKeys())).map(String); }
  catch { return [...mem[store].keys()]; }
}
