// Nástroje, které provádí telefon (kalendář, připomínky). Server je jen nabídne Claudovi;
// když je Claude zavolá, server pošle požadavek aplikaci a ta pošle výsledky v navazujícím požadavku.

export const DEVICE_TOOLS = [
  {
    name: "kalendar_udalosti",
    description: "Vrátí události z kalendáře uživatele v daném období (např. „co mám ve čtvrtek“, „jaký mám týden“).",
    input_schema: {
      type: "object",
      properties: {
        od: { type: "string", description: "Začátek období, ISO 8601 s časovým posunem, např. 2026-10-15T00:00:00+02:00" },
        do: { type: "string", description: "Konec období, ISO 8601 s časovým posunem" },
      },
      required: ["od", "do"],
    },
  },
  {
    name: "kalendar_vytvor",
    description:
      "Vytvoří událost v kalendáři uživatele. Před vytvořením zopakuj název, den a čas a nech si to potvrdit, pokud to uživatel výslovně neschválil.",
    input_schema: {
      type: "object",
      properties: {
        nazev: { type: "string" },
        zacatek: { type: "string", description: "ISO 8601 s časovým posunem" },
        konec: { type: "string", description: "ISO 8601 s časovým posunem; když chybí, trvá hodinu" },
        celodenni: { type: "boolean" },
        misto: { type: "string" },
        poznamka: { type: "string" },
      },
      required: ["nazev", "zacatek"],
    },
  },
  {
    name: "pripominky",
    description: "Vrátí seznam nesplněných připomínek uživatele (aplikace Připomínky).",
    input_schema: { type: "object", properties: {}, required: [] },
  },
  {
    name: "pripominka_vytvor",
    description: "Vytvoří připomínku (aplikace Připomínky), volitelně s termínem upozornění („připomeň mi zítra v 9…“).",
    input_schema: {
      type: "object",
      properties: {
        nazev: { type: "string" },
        termin: { type: "string", description: "ISO 8601 s časovým posunem; vynech, když bez termínu" },
        poznamka: { type: "string" },
      },
      required: ["nazev"],
    },
  },
].map((t) => ({ ...t, eager_input_streaming: true }));

export const DEVICE_TOOL_NAMES = new Set(DEVICE_TOOLS.map((t) => t.name));

export const DEVICE_SYSTEM_PROMPT = `Máš přístup ke kalendáři a připomínkám v uživatelově iPhonu (nástroje kalendar_udalosti, kalendar_vytvor, pripominky, pripominka_vytvor).
- Časy zadávej ve formátu ISO 8601 s posunem pro Europe/Prague. Aktuální datum a čas najdeš v hranatých závorkách v poslední zprávě uživatele.
- Než něco vytvoříš, stručně zopakuj, co a kdy vytvoříš, a nech si to potvrdit — pokud uživatel nedal jasný pokyn se všemi údaji.
- Termíny říkej přirozeně („ve čtvrtek v devět“), ne ve formátu data.`;

/** Poznámka s aktuálním časem do poslední zprávy uživatele (klient ji posílá stejnou i v navazujícím požadavku). */
export function timeNote(iso?: string): string {
  const d = iso && !Number.isNaN(Date.parse(iso)) ? new Date(iso) : new Date();
  const s = new Intl.DateTimeFormat("cs-CZ", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "Europe/Prague",
  }).format(d);
  return `[Aktuální datum a čas: ${s}, časové pásmo Europe/Prague]`;
}
