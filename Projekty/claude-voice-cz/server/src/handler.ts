import { GITHUB_SYSTEM_PROMPT, SYSTEM_PROMPT, WEB_SYSTEM_PROMPT } from "./systemPrompt";
import { GITHUB_TOOLS, GitHubReader, githubEnabled } from "./github";
import { handleAddVoice, handleSTT, handleTTS, handleVoices, voiceUsage } from "./elevenlabs";
import { DEVICE_SYSTEM_PROMPT, DEVICE_TOOLS, DEVICE_TOOL_NAMES, timeNote } from "./device";
import { MEMORY_TOOLS, MEMORY_TOOL_NAMES, loadMemory, memoryPrompt, runMemoryTool } from "./memory";

export interface Env {
  ANTHROPIC_API_KEY: string;
  APP_TOKEN: string;
  MODEL: string;
  EFFORT: string;
  MAX_TOKENS: string;
  DAILY_TOKEN_LIMIT: string;
  USAGE: KVNamespace;
  GITHUB_TOKEN?: string;
  GITHUB_REPO?: string;
  /** "off" vypne hledání a čtení webu. */
  WEB_TOOLS?: string;
  ELEVENLABS_API_KEY?: string;
  ELEVENLABS_VOICE?: string;
  ELEVENLABS_TTS_MODEL?: string;
  ELEVENLABS_STT_MODEL?: string;
  TTS_MONTHLY_CHARS?: string;
  STT_MONTHLY_SECONDS?: string;
}

/** Nástroje Anthropicu běžící na jejich serverech (hledání a čtení webu). */
export const WEB_TOOLS = [
  {
    type: "web_search_20260209",
    name: "web_search",
    max_uses: 5,
    // Pozn.: country „CZ“ vyhledávač nepodporuje (400) — stačí časové pásmo.
    user_location: { type: "approximate", timezone: "Europe/Prague" },
  },
  { type: "web_fetch_20260209", name: "web_fetch", max_uses: 3, max_content_tokens: 20000 },
];

export function webEnabled(env: Env): boolean {
  return (env.WEB_TOOLS ?? "on") !== "off";
}

/** Dnešní datum česky (Europe/Prague) — mění se jednou denně, mezipaměť to nenaruší. */
export function todayCs(now = new Date()): string {
  return new Intl.DateTimeFormat("cs-CZ", { weekday: "long", day: "numeric", month: "long", year: "numeric", timeZone: "Europe/Prague" }).format(now);
}

export interface ChatMessage {
  role: "user" | "assistant";
  /** Text, nebo (u uživatele) bloky text + obrázky ve formátu Claude API. */
  content: string | any[];
}

/** Abstrakce nad streamem Claude API — umožňuje testy bez skutečného volání. */
export interface ModelStream {
  events: AsyncIterable<any>;
  /** Kompletní zpráva po doběhnutí streamu (obsah vč. bloků tool_use a thinking). */
  final(): Promise<any>;
  abort(): void;
}

/** Max. počet kol s nástroji v jedné odpovědi (pojistka proti zacyklení a nákladům). */
export const MAX_TOOL_ROUNDS = 6;
export type StreamFactory = (env: Env, params: Record<string, unknown>) => ModelStream;

// Limity vstupu — chrání před omylem i zneužitím tokenu.
export const LIMITS = {
  maxMessages: 200,
  maxMessageChars: 8_000,
  maxTotalChars: 200_000,
  maxImagesPerMessage: 4,
  maxImagesTotal: 8,
  maxImageBase64: 5_000_000, // ~3,7 MB obrázku (limit API je 5 MB)
  maxContinuationBytes: 400_000,
};

const IMAGE_TYPES = new Set(["image/jpeg", "image/png", "image/webp", "image/gif"]);

const encoder = new TextEncoder();

function json(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" },
  });
}

/** Porovnání tokenů v konstantním čase (bez úniku informace přes časování). */
export function safeEqual(a: string, b: string): boolean {
  const ea = encoder.encode(a);
  const eb = encoder.encode(b);
  let diff = ea.length ^ eb.length;
  const n = Math.max(ea.length, eb.length);
  for (let i = 0; i < n; i++) diff |= (ea[i] ?? 0) ^ (eb[i] ?? 0);
  return diff === 0;
}

export function validateMessages(input: unknown): ChatMessage[] | string {
  if (!Array.isArray(input) || input.length === 0) return "messages musí být neprázdné pole";
  if (input.length > LIMITS.maxMessages) return "konverzace je příliš dlouhá";
  let total = 0;
  let images = 0;
  const out: ChatMessage[] = [];
  for (let i = 0; i < input.length; i++) {
    const m = input[i];
    if (!m || (m.role !== "user" && m.role !== "assistant")) return `neplatná zpráva na pozici ${i}`;
    const expected = i % 2 === 0 ? "user" : "assistant";
    if (m.role !== expected) return "zprávy se musí střídat user/assistant, začínat i končit user";
    if (typeof m.content === "string") {
      const content = m.content.trim();
      if (content.length === 0) return `prázdná zpráva na pozici ${i}`;
      if (content.length > LIMITS.maxMessageChars) return `zpráva na pozici ${i} je příliš dlouhá`;
      total += content.length;
      out.push({ role: m.role, content });
      continue;
    }
    // Zpráva s obrázky: [{type:"text", text}, {type:"image", media_type, data}]
    if (m.role !== "user" || !Array.isArray(m.content) || m.content.length === 0) return `neplatná zpráva na pozici ${i}`;
    const parts: any[] = [];
    let msgImages = 0;
    for (const part of m.content) {
      if (part?.type === "text" && typeof part.text === "string") {
        const t = part.text.trim();
        if (!t) continue;
        if (t.length > LIMITS.maxMessageChars) return `zpráva na pozici ${i} je příliš dlouhá`;
        total += t.length;
        parts.push({ type: "text", text: t });
      } else if (part?.type === "image" && typeof part.data === "string" && IMAGE_TYPES.has(part.media_type)) {
        if (part.data.length > LIMITS.maxImageBase64) return "obrázek je příliš velký";
        msgImages++;
        images++;
        parts.push({ type: "image", source: { type: "base64", media_type: part.media_type, data: part.data } });
      } else {
        return `neplatná část zprávy na pozici ${i}`;
      }
    }
    if (msgImages > LIMITS.maxImagesPerMessage || images > LIMITS.maxImagesTotal) return "příliš mnoho obrázků";
    if (parts.length === 0) return `prázdná zpráva na pozici ${i}`;
    out.push({ role: "user", content: parts });
  }
  if (out[out.length - 1].role !== "user") return "poslední zpráva musí být od uživatele";
  if (total > LIMITS.maxTotalChars) return "konverzace je příliš dlouhá";
  return out;
}

/** Přidá k poslední zprávě uživatele poznámku s aktuálním časem (pro kalendář). */
export function withTimeNote(messages: ChatMessage[], note: string): ChatMessage[] {
  const out = [...messages];
  const last = out[out.length - 1];
  const parts = typeof last.content === "string" ? [{ type: "text", text: last.content }] : [...last.content];
  out[out.length - 1] = { role: "user", content: [...parts, { type: "text", text: note }] };
  return out;
}

/** Navazující požadavek po nástrojích v telefonu: obsah asistenta (beze změny) + výsledky nástrojů. */
export function validateContinuation(c: any): any[] | string | null {
  if (c == null) return null;
  if (JSON.stringify(c).length > LIMITS.maxContinuationBytes) return "navazující data jsou příliš velká";
  if (!Array.isArray(c.assistant) || c.assistant.length === 0) return "neplatné navazující data (assistant)";
  if (!Array.isArray(c.tool_results) || c.tool_results.length === 0) return "neplatné navazující data (tool_results)";
  const toolUseIds = new Set(c.assistant.filter((b: any) => b?.type === "tool_use").map((b: any) => b.id));
  const results: any[] = [];
  for (const r of c.tool_results) {
    if (typeof r?.tool_use_id !== "string" || !toolUseIds.has(r.tool_use_id)) return "výsledek nástroje nepatří k žádnému volání";
    results.push({
      type: "tool_result",
      tool_use_id: r.tool_use_id,
      content: String(r.content ?? "").slice(0, 30_000),
      ...(r.is_error ? { is_error: true } : {}),
    });
  }
  if (results.length !== toolUseIds.size) return "chybí výsledky některých nástrojů";
  return [
    { role: "assistant", content: c.assistant },
    { role: "user", content: results },
  ];
}

function todayKey(): string {
  return `usage:${new Date().toISOString().slice(0, 10)}`;
}

async function getUsage(env: Env): Promise<number> {
  return Number((await env.USAGE.get(todayKey())) ?? "0");
}

async function addUsage(env: Env, tokens: number): Promise<void> {
  if (tokens <= 0) return;
  const key = todayKey();
  const current = Number((await env.USAGE.get(key)) ?? "0");
  await env.USAGE.put(key, String(current + tokens), { expirationTtl: 60 * 60 * 24 * 40 });
}

/** `memory` = text paměti načtený jednou na začátku odpovědi (během odpovědi se nemění). */
export function buildParams(env: Env, messages: unknown[], memory = "", device = false): Record<string, unknown> {
  const gh = githubEnabled(env);
  const web = webEnabled(env);
  const tools = [...(web ? WEB_TOOLS : []), ...MEMORY_TOOLS, ...(gh ? GITHUB_TOOLS : []), ...(device ? DEVICE_TOOLS : [])];
  const system = [
    SYSTEM_PROMPT,
    web ? WEB_SYSTEM_PROMPT : "",
    gh ? GITHUB_SYSTEM_PROMPT : "",
    device ? DEVICE_SYSTEM_PROMPT : "",
    memory,
    `Dnes je ${todayCs()}.`,
  ]
    .filter(Boolean)
    .join("\n\n");
  return {
    model: env.MODEL,
    max_tokens: Number(env.MAX_TOKENS) || 1500,
    output_config: { effort: env.EFFORT || "low" },
    // Automatické ukládání prefixu konverzace do mezipaměti (levnější a rychlejší další kolo).
    cache_control: { type: "ephemeral" },
    system,
    ...(tools.length ? { tools } : {}),
    // Historie mezi koly je jen text a pouze se přidává na konec (append-only);
    // v rámci jedné odpovědi se vrací kompletní obsah (vč. thinking a tool_use).
    messages,
    // Při odmítnutí bezpečnostním klasifikátorem zkusí API doporučený záložní model.
    betas: ["server-side-fallback-2026-07-01"],
    fallbacks: "default",
  };
}

export async function handleRequest(
  request: Request,
  env: Env,
  ctx: ExecutionContext,
  createStream: StreamFactory,
): Promise<Response> {
  const url = new URL(request.url);

  if (url.pathname === "/health") return json(200, { ok: true });

  const auth = request.headers.get("authorization") ?? "";
  const token = auth.startsWith("Bearer ") ? auth.slice(7) : "";
  if (!env.APP_TOKEN || !token || !safeEqual(token, env.APP_TOKEN)) {
    return json(401, { error: "Neautorizovaný přístup" });
  }

  if (url.pathname === "/v1/usage" && request.method === "GET") {
    return json(200, {
      today: await getUsage(env),
      limit: Number(env.DAILY_TOKEN_LIMIT),
      voice: { enabled: Boolean(env.ELEVENLABS_API_KEY), ...(await voiceUsage(env)) },
    });
  }

  if (url.pathname === "/v1/tts" && request.method === "POST") return handleTTS(request, env);
  if (url.pathname === "/v1/stt" && request.method === "POST") return handleSTT(request, env);
  if (url.pathname === "/v1/voices" && request.method === "GET") return handleVoices(url, env);
  if (url.pathname === "/v1/voices/add" && request.method === "POST") return handleAddVoice(request, env);

  if (url.pathname !== "/v1/chat" || request.method !== "POST") {
    return json(404, { error: "Nenalezeno" });
  }

  let body: any;
  try {
    body = await request.json();
  } catch {
    return json(400, { error: "Neplatný JSON" });
  }
  const validated = validateMessages(body?.messages);
  if (typeof validated === "string") return json(400, { error: validated });
  const device = Array.isArray(body?.client_tools) && body.client_tools.includes("kalendar");
  const messages = device ? withTimeNote(validated, timeNote(typeof body?.now === "string" ? body.now : undefined)) : validated;
  const continuation = validateContinuation(body?.continuation);
  if (typeof continuation === "string") return json(400, { error: continuation });

  const limit = Number(env.DAILY_TOKEN_LIMIT) || 0;
  if (limit > 0 && (await getUsage(env)) >= limit) {
    return json(429, { error: "Denní limit spotřeby byl vyčerpán. Limit se obnoví o půlnoci (UTC)." });
  }

  const github = githubEnabled(env) ? new GitHubReader(env) : null;
  const memory = memoryPrompt(await loadMemory(env.USAGE));
  const runTool = async (name: string, input: any) => {
    if (MEMORY_TOOL_NAMES.has(name)) return runMemoryTool(env.USAGE, name, input);
    if (github) return github.run(name, input);
    return { content: `Nástroj ${name} není k dispozici.`, isError: true };
  };
  let current: ModelStream | null = null;
  let cancelled = false;
  let usedTokens = 0;
  let accounted = false;
  const account = () => {
    if (accounted) return;
    accounted = true;
    ctx.waitUntil(addUsage(env, usedTokens));
  };

  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      const send = (obj: unknown) => controller.enqueue(encoder.encode(`data: ${JSON.stringify(obj)}\n\n`));
      const convo: any[] = [...messages, ...(continuation ?? [])];
      let stopReason: string | null = null;
      let sentText = false;
      try {
        for (let round = 0; round <= MAX_TOOL_ROUNDS && !cancelled; round++) {
          current = createStream(env, buildParams(env, convo, memory, device));
          let roundInput = 0;
          let roundOutput = 0;
          let newBlock = false;
          for await (const event of current.events) {
            switch (event.type) {
              case "message_start": {
                const u = event.message?.usage ?? {};
                roundInput =
                  (u.input_tokens ?? 0) + (u.cache_creation_input_tokens ?? 0) + (u.cache_read_input_tokens ?? 0);
                break;
              }
              case "content_block_start":
                // Nový textový blok (např. po hledání na webu) oddělíme mezerou, ať se věty neslepí.
                if (event.content_block?.type === "text") newBlock = true;
                break;
              case "content_block_delta":
                if (event.delta?.type === "text_delta" && event.delta.text) {
                  if (sentText && newBlock && !/^\s/.test(event.delta.text)) send({ type: "text", text: " " });
                  newBlock = false;
                  send({ type: "text", text: event.delta.text });
                  sentText = true;
                }
                break;
              case "message_delta":
                if (event.usage?.output_tokens != null) roundOutput = event.usage.output_tokens;
                if (event.delta?.stop_reason) stopReason = event.delta.stop_reason;
                break;
            }
          }
          usedTokens += roundInput + roundOutput;
          if (cancelled) break;
          // Dlouhé hledání na webu: API se pozastavilo — pošleme obsah zpět a ono samo pokračuje.
          if (stopReason === "pause_turn") {
            if (round === MAX_TOOL_ROUNDS) break;
            const paused = await current.final();
            convo.push({ role: "assistant", content: paused.content });
            continue;
          }
          if (stopReason !== "tool_use") break;
          if (round === MAX_TOOL_ROUNDS) {
            send({ type: "text", text: " Hledání se protáhlo, zkuste prosím otázku upřesnit." });
            break;
          }
          const message = await current.final();
          const toolUses = (message?.content ?? []).filter((b: any) => b.type === "tool_use");
          if (toolUses.length === 0) break;
          const serverUses = toolUses.filter((t: any) => !DEVICE_TOOL_NAMES.has(t.name));
          const deviceUses = toolUses.filter((t: any) => DEVICE_TOOL_NAMES.has(t.name));
          const serverResults = await Promise.all(
            serverUses.map(async (t: any) => {
              const r = await runTool(t.name, t.input);
              return { type: "tool_result", tool_use_id: t.id, content: r.content, ...(r.isError ? { is_error: true } : {}) };
            }),
          );
          if (deviceUses.length && device) {
            // Nástroje v telefonu: předáme je aplikaci; ta pošle výsledky v navazujícím požadavku.
            send({
              type: "client_tools",
              calls: deviceUses.map((t: any) => ({ id: t.id, name: t.name, input: t.input })),
              pending: { assistant: message.content, server_results: serverResults },
            });
            stopReason = "client_tools";
            break;
          }
          // Celý obsah asistenta (thinking, text, tool_use) vracíme beze změny.
          convo.push({ role: "assistant", content: message.content });
          const deviceUnavailable = deviceUses.map((t: any) => ({
            type: "tool_result",
            tool_use_id: t.id,
            content: "Tato verze aplikace kalendář nepodporuje.",
            is_error: true,
          }));
          convo.push({ role: "user", content: [...serverResults, ...deviceUnavailable] });
        }
        if (stopReason === "refusal") {
          send({ type: "error", message: "Na tento dotaz Claude odmítl odpovědět." });
        }
        send({ type: "done", stop_reason: stopReason, usage: { total: usedTokens } });
      } catch (err: any) {
        console.error("stream error", err?.status, err?.message);
        const status = err?.status;
        const message =
          status === 429 || status === 529
            ? "Claude je momentálně přetížený, zkuste to prosím znovu."
            : "Chyba při komunikaci s Claudem.";
        try {
          send({ type: "error", message, detail: String(err?.message ?? "").slice(0, 400) });
        } catch {
          /* klient už odpojen */
        }
      } finally {
        account();
        try {
          controller.close();
        } catch {
          /* už zavřeno */
        }
      }
    },
    cancel() {
      // Klient se odpojil (např. uživatel Clauda přerušil) — zastavíme generování, ať neplatíme navíc.
      cancelled = true;
      current?.abort();
      account();
    },
  });

  return new Response(stream, {
    headers: {
      "content-type": "text/event-stream; charset=utf-8",
      "cache-control": "no-cache",
    },
  });
}
