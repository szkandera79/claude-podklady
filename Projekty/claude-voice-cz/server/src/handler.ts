import { GITHUB_SYSTEM_PROMPT, SYSTEM_PROMPT } from "./systemPrompt";
import { GITHUB_TOOLS, GitHubReader, githubEnabled } from "./github";

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
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
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
};

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
  const out: ChatMessage[] = [];
  for (let i = 0; i < input.length; i++) {
    const m = input[i];
    if (!m || (m.role !== "user" && m.role !== "assistant") || typeof m.content !== "string") {
      return `neplatná zpráva na pozici ${i}`;
    }
    const content = m.content.trim();
    if (content.length === 0) return `prázdná zpráva na pozici ${i}`;
    if (content.length > LIMITS.maxMessageChars) return `zpráva na pozici ${i} je příliš dlouhá`;
    const expected = i % 2 === 0 ? "user" : "assistant";
    if (m.role !== expected) return "zprávy se musí střídat user/assistant, začínat i končit user";
    total += content.length;
    out.push({ role: m.role, content });
  }
  if (out[out.length - 1].role !== "user") return "poslední zpráva musí být od uživatele";
  if (total > LIMITS.maxTotalChars) return "konverzace je příliš dlouhá";
  return out;
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

export function buildParams(env: Env, messages: unknown[]): Record<string, unknown> {
  const tools = githubEnabled(env);
  return {
    model: env.MODEL,
    max_tokens: Number(env.MAX_TOKENS) || 1500,
    output_config: { effort: env.EFFORT || "low" },
    // Automatické ukládání prefixu konverzace do mezipaměti (levnější a rychlejší další kolo).
    cache_control: { type: "ephemeral" },
    system: tools ? SYSTEM_PROMPT + "\n\n" + GITHUB_SYSTEM_PROMPT : SYSTEM_PROMPT,
    ...(tools ? { tools: GITHUB_TOOLS } : {}),
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
    return json(200, { today: await getUsage(env), limit: Number(env.DAILY_TOKEN_LIMIT) });
  }

  if (url.pathname !== "/v1/chat" || request.method !== "POST") {
    return json(404, { error: "Nenalezeno" });
  }

  let body: any;
  try {
    body = await request.json();
  } catch {
    return json(400, { error: "Neplatný JSON" });
  }
  const messages = validateMessages(body?.messages);
  if (typeof messages === "string") return json(400, { error: messages });

  const limit = Number(env.DAILY_TOKEN_LIMIT) || 0;
  if (limit > 0 && (await getUsage(env)) >= limit) {
    return json(429, { error: "Denní limit spotřeby byl vyčerpán. Limit se obnoví o půlnoci (UTC)." });
  }

  const github = githubEnabled(env) ? new GitHubReader(env) : null;
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
      const convo: any[] = [...messages];
      let stopReason: string | null = null;
      let sentText = false;
      try {
        for (let round = 0; round <= MAX_TOOL_ROUNDS && !cancelled; round++) {
          current = createStream(env, buildParams(env, convo));
          let roundInput = 0;
          let roundOutput = 0;
          let separated = false;
          for await (const event of current.events) {
            switch (event.type) {
              case "message_start": {
                const u = event.message?.usage ?? {};
                roundInput =
                  (u.input_tokens ?? 0) + (u.cache_creation_input_tokens ?? 0) + (u.cache_read_input_tokens ?? 0);
                break;
              }
              case "content_block_delta":
                if (event.delta?.type === "text_delta" && event.delta.text) {
                  // Text z dalšího kola oddělíme mezerou, ať se věty neslepí.
                  if (sentText && !separated && round > 0) {
                    send({ type: "text", text: " " });
                    separated = true;
                  }
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
          if (stopReason !== "tool_use" || !github || cancelled) break;
          if (round === MAX_TOOL_ROUNDS) {
            send({ type: "text", text: " Hledání se protáhlo, zkuste prosím otázku upřesnit." });
            break;
          }
          const message = await current.final();
          const toolUses = (message?.content ?? []).filter((b: any) => b.type === "tool_use");
          if (toolUses.length === 0) break;
          // Celý obsah asistenta (thinking, text, tool_use) vracíme beze změny.
          convo.push({ role: "assistant", content: message.content });
          const results = await Promise.all(
            toolUses.map(async (t: any) => {
              const r = await github.run(t.name, t.input);
              return { type: "tool_result", tool_use_id: t.id, content: r.content, ...(r.isError ? { is_error: true } : {}) };
            }),
          );
          convo.push({ role: "user", content: results });
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
          send({ type: "error", message });
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
