// Dlouhodobá paměť o uživateli (uložená v KV, společná pro všechny rozhovory).

export interface MemoryItem {
  id: string;
  text: string;
  date: string; // YYYY-MM-DD
}

const KEY = "memory:v1";
export const MAX_ITEMS = 80;
export const MAX_TEXT = 400;

export const MEMORY_TOOLS = [
  {
    name: "zapamatuj_si",
    description:
      "Uloží trvalou informaci o uživateli do dlouhodobé paměti (platí pro všechny budoucí rozhovory): fakta o něm, jeho firmách a projektech, preference (např. tykání), důležitá rozhodnutí. Použij, když o to uživatel požádá, nebo když sdělí zjevně trvalou a užitečnou informaci. Neukládej hesla, čísla karet ani jiné citlivé údaje.",
    input_schema: {
      type: "object",
      properties: { text: { type: "string", description: "Jedna stručná věta ve třetí osobě, např. „Uživatel chce, aby mu asistent tykal.“" } },
      required: ["text"],
    },
  },
  {
    name: "zapomen",
    description: "Smaže položku z dlouhodobé paměti podle jejího čísla (viz seznam v systémovém promptu), když uživatel požádá o zapomenutí nebo je informace zastaralá.",
    input_schema: {
      type: "object",
      properties: { cislo: { type: "string", description: "Číslo položky, např. „m3“." } },
      required: ["cislo"],
    },
  },
].map((t) => ({ ...t, eager_input_streaming: true }));

export async function loadMemory(kv: KVNamespace): Promise<MemoryItem[]> {
  try {
    const raw = await kv.get(KEY);
    const items = raw ? (JSON.parse(raw) as MemoryItem[]) : [];
    return Array.isArray(items) ? items : [];
  } catch {
    return [];
  }
}

async function save(kv: KVNamespace, items: MemoryItem[]): Promise<void> {
  await kv.put(KEY, JSON.stringify(items));
}

/** Blok do systémového promptu. Prázdná paměť = prázdný řetězec. */
export function memoryPrompt(items: MemoryItem[]): string {
  if (!items.length) return "";
  return (
    "Co víš o uživateli z dřívějších rozhovorů (dlouhodobá paměť; řiď se tím, ale nevyjmenovávej to bez důvodu):\n" +
    items.map((m) => `- [${m.id}] ${m.text}`).join("\n")
  );
}

export async function runMemoryTool(
  kv: KVNamespace,
  name: string,
  input: any,
): Promise<{ content: string; isError: boolean }> {
  const items = await loadMemory(kv);
  if (name === "zapamatuj_si") {
    const text = typeof input?.text === "string" ? input.text.trim().slice(0, MAX_TEXT) : "";
    if (!text) return { content: "Chybí text k zapamatování.", isError: true };
    if (items.some((m) => m.text.toLowerCase() === text.toLowerCase())) {
      return { content: "Tohle už v paměti je.", isError: false };
    }
    const next = Math.max(0, ...items.map((m) => Number(m.id.slice(1)) || 0)) + 1;
    items.push({ id: `m${next}`, text, date: new Date().toISOString().slice(0, 10) });
    while (items.length > MAX_ITEMS) items.shift();
    await save(kv, items);
    return { content: `Uloženo jako m${next}.`, isError: false };
  }
  if (name === "zapomen") {
    const id = String(input?.cislo ?? "").trim().toLowerCase();
    const before = items.length;
    const rest = items.filter((m) => m.id !== id);
    if (rest.length === before) return { content: `Položka ${id} v paměti není.`, isError: true };
    await save(kv, rest);
    return { content: `Položka ${id} smazána.`, isError: false };
  }
  return { content: `Neznámý nástroj ${name}.`, isError: true };
}

export const MEMORY_TOOL_NAMES = new Set(MEMORY_TOOLS.map((t) => t.name));
