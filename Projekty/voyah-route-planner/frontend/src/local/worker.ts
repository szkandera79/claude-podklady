/** Web Worker pro výpočty na pozadí (záložní nabíječky, levnější alternativy) — hlavní plánování nečeká. */
import { computeBackups } from "./service";

self.onmessage = (e: MessageEvent) => {
  const { id, input } = e.data;
  try { (self as unknown as Worker).postMessage({ id, result: computeBackups(input) }); }
  catch (err) { (self as unknown as Worker).postMessage({ id, error: (err as Error).message }); }
};
