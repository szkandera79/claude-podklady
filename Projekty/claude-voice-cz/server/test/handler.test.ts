import { describe, expect, it } from "vitest";
import { buildParams, handleRequest, safeEqual, validateMessages, type Env, type StreamFactory } from "../src/handler";

class MemoryKV {
  store = new Map<string, string>();
  async get(k: string) {
    return this.store.get(k) ?? null;
  }
  async put(k: string, v: string) {
    this.store.set(k, v);
  }
}

function makeEnv(overrides: Partial<Env> = {}): Env & { USAGE: MemoryKV } {
  return {
    ANTHROPIC_API_KEY: "test-key",
    APP_TOKEN: "secret-token",
    MODEL: "claude-opus-5-5",
    EFFORT: "low",
    MAX_TOKENS: "1500",
    DAILY_TOKEN_LIMIT: "1000",
    USAGE: new MemoryKV(),
    ...overrides,
  } as any;
}

function makeCtx() {
  const pending: Promise<unknown>[] = [];
  return {
    ctx: { waitUntil: (p: Promise<unknown>) => pending.push(p), passThroughOnException() {} } as any,
    flush: () => Promise.all(pending),
  };
}

function fakeStream(events: any[], captured: { params?: any; aborted?: boolean } = {}): StreamFactory {
  return (_env, params) => {
    captured.params = params;
    return {
      events: (async function* () {
        for (const e of events) yield e;
      })(),
      final: async () => ({ content: [] }),
      abort: () => {
        captured.aborted = true;
      },
    };
  };
}

const okEvents = [
  { type: "message_start", message: { usage: { input_tokens: 100, cache_read_input_tokens: 20 } } },
  { type: "content_block_start", content_block: { type: "thinking" } },
  { type: "content_block_delta", delta: { type: "thinking_delta", thinking: "" } },
  { type: "content_block_delta", delta: { type: "text_delta", text: "Dobrý den. " } },
  { type: "content_block_delta", delta: { type: "text_delta", text: "Jak vám mohu pomoci?" } },
  { type: "message_delta", delta: { stop_reason: "end_turn" }, usage: { output_tokens: 30 } },
  { type: "message_stop" },
];

function chatRequest(body: unknown, token = "secret-token") {
  return new Request("https://x/v1/chat", {
    method: "POST",
    headers: { authorization: `Bearer ${token}`, "content-type": "application/json" },
    body: JSON.stringify(body),
  });
}

function parseSSE(text: string) {
  return text
    .split("\n\n")
    .filter((l) => l.startsWith("data: "))
    .map((l) => JSON.parse(l.slice(6)));
}

describe("validateMessages", () => {
  it("přijme správnou konverzaci", () => {
    const r = validateMessages([
      { role: "user", content: "Ahoj" },
      { role: "assistant", content: "Dobrý den" },
      { role: "user", content: "Jak se máš?" },
    ]);
    expect(Array.isArray(r)).toBe(true);
  });
  it("odmítne špatné střídání a konec asistentem", () => {
    expect(typeof validateMessages([{ role: "assistant", content: "x" }])).toBe("string");
    expect(typeof validateMessages([{ role: "user", content: "a" }, { role: "assistant", content: "b" }])).toBe("string");
    expect(typeof validateMessages([{ role: "user", content: "a" }, { role: "user", content: "b" }])).toBe("string");
  });
  it("odmítne prázdné a příliš dlouhé zprávy", () => {
    expect(typeof validateMessages([])).toBe("string");
    expect(typeof validateMessages([{ role: "user", content: "   " }])).toBe("string");
    expect(typeof validateMessages([{ role: "user", content: "x".repeat(9000) }])).toBe("string");
  });
});

describe("safeEqual", () => {
  it("porovnává správně", () => {
    expect(safeEqual("abc", "abc")).toBe(true);
    expect(safeEqual("abc", "abd")).toBe(false);
    expect(safeEqual("abc", "abcd")).toBe(false);
  });
});

describe("buildParams", () => {
  it("posílá model, effort, cache a fallback; nikdy nepošle API klíč", () => {
    const p: any = buildParams(makeEnv(), [{ role: "user", content: "Ahoj" }]);
    expect(p.model).toBe("claude-opus-5-5");
    expect(p.output_config).toEqual({ effort: "low" });
    expect(p.cache_control).toEqual({ type: "ephemeral" });
    expect(p.fallbacks).toBe("default");
    expect(p.thinking).toBeUndefined(); // u Opus 5.5 nelze vypnout; necháváme výchozí adaptivní
    expect(JSON.stringify(p)).not.toContain("test-key");
  });
});

describe("handleRequest", () => {
  it("health nepotřebuje token", async () => {
    const { ctx } = makeCtx();
    const r = await handleRequest(new Request("https://x/health"), makeEnv(), ctx, fakeStream([]));
    expect(r.status).toBe(200);
  });

  it("bez tokenu / se špatným tokenem vrací 401", async () => {
    const { ctx } = makeCtx();
    const body = { messages: [{ role: "user", content: "Ahoj" }] };
    expect((await handleRequest(chatRequest(body, ""), makeEnv(), ctx, fakeStream(okEvents))).status).toBe(401);
    expect((await handleRequest(chatRequest(body, "spatny"), makeEnv(), ctx, fakeStream(okEvents))).status).toBe(401);
  });

  it("streamuje text, počítá spotřebu a ignoruje bloky přemýšlení", async () => {
    const env = makeEnv();
    const { ctx, flush } = makeCtx();
    const captured: any = {};
    const r = await handleRequest(
      chatRequest({ messages: [{ role: "user", content: "Ahoj" }] }),
      env,
      ctx,
      fakeStream(okEvents, captured),
    );
    expect(r.status).toBe(200);
    expect(r.headers.get("content-type")).toContain("text/event-stream");
    const events = parseSSE(await r.text());
    const text = events.filter((e) => e.type === "text").map((e) => e.text).join("");
    expect(text).toBe("Dobrý den. Jak vám mohu pomoci?");
    expect(events.at(-1)).toMatchObject({ type: "done", stop_reason: "end_turn", usage: { total: 150 } });
    await flush();
    expect([...env.USAGE.store.values()]).toEqual(["150"]);
    expect(captured.params.messages).toEqual([{ role: "user", content: "Ahoj" }]);
  });

  it("po vyčerpání denního limitu vrací 429 a Clauda nevolá", async () => {
    const env = makeEnv({ DAILY_TOKEN_LIMIT: "100" });
    env.USAGE.store.set(`usage:${new Date().toISOString().slice(0, 10)}`, "100");
    const { ctx } = makeCtx();
    const captured: any = {};
    const r = await handleRequest(
      chatRequest({ messages: [{ role: "user", content: "Ahoj" }] }),
      env,
      ctx,
      fakeStream(okEvents, captured),
    );
    expect(r.status).toBe(429);
    expect(captured.params).toBeUndefined();
  });

  it("odpojení klienta (přerušení) zastaví generování", async () => {
    const env = makeEnv();
    const { ctx } = makeCtx();
    const captured: any = {};
    const slow: StreamFactory = (_e, params) => {
      captured.params = params;
      return {
        events: (async function* () {
          yield okEvents[0];
          yield okEvents[3];
          await new Promise((res) => setTimeout(res, 50));
          yield okEvents[4];
        })(),
        final: async () => ({ content: [] }),
        abort: () => (captured.aborted = true),
      };
    };
    const r = await handleRequest(chatRequest({ messages: [{ role: "user", content: "Ahoj" }] }), env, ctx, slow);
    const reader = r.body!.getReader();
    await reader.read();
    await reader.cancel();
    expect(captured.aborted).toBe(true);
  });

  it("chyba API se pošle klientovi jako srozumitelná hláška", async () => {
    const { ctx } = makeCtx();
    const failing: StreamFactory = () => ({
      events: (async function* () {
        throw Object.assign(new Error("overloaded"), { status: 529 });
      })(),
      final: async () => ({ content: [] }),
      abort() {},
    });
    const r = await handleRequest(chatRequest({ messages: [{ role: "user", content: "Ahoj" }] }), makeEnv(), ctx, failing);
    const events = parseSSE(await r.text());
    expect(events[0].type).toBe("error");
    expect(events[0].message).toContain("přetížený");
  });
});

describe("GitHub nástroje", () => {
  it("bez tokenu se nástroje neposílají, s tokenem ano", () => {
    const off: any = buildParams(makeEnv({ WEB_TOOLS: "off" }), [{ role: "user", content: "Ahoj" }]);
    expect(off.tools.map((t: any) => t.name)).toEqual(["zapamatuj_si", "zapomen"]);
    const on: any = buildParams(makeEnv({ GITHUB_TOKEN: "gh", GITHUB_REPO: "szkandera79/Projekty", WEB_TOOLS: "off" }), [
      { role: "user", content: "Ahoj" },
    ]);
    expect(on.tools.map((t: any) => t.name)).toEqual(["zapamatuj_si", "zapomen", "seznam_projektu", "obsah_slozky", "precti_soubor", "hledej"]);
    expect(on.system).toContain("repozitáři");
    expect(JSON.stringify(on)).not.toContain('"gh"');
  });

  it("kolo s nástrojem: spustí nástroj, vrátí celý obsah asistenta a pokračuje", async () => {
    const env = makeEnv({ GITHUB_TOKEN: "gh", GITHUB_REPO: "szkandera79/Projekty" });
    const { ctx, flush } = makeCtx();
    const calls: any[] = [];
    const assistantContent = [
      { type: "thinking", thinking: "", signature: "sig" },
      { type: "text", text: "Moment, podívám se." },
      { type: "tool_use", id: "tu1", name: "obsah_slozky", input: { cesta: "../tajne" } },
    ];
    const factory: StreamFactory = (_e, params) => {
      calls.push(structuredClone(params));
      const round = calls.length;
      const events =
        round === 1
          ? [
              { type: "message_start", message: { usage: { input_tokens: 50 } } },
              { type: "content_block_delta", delta: { type: "text_delta", text: "Moment, podívám se." } },
              { type: "message_delta", delta: { stop_reason: "tool_use" }, usage: { output_tokens: 10 } },
            ]
          : [
              { type: "message_start", message: { usage: { input_tokens: 80 } } },
              { type: "content_block_start", content_block: { type: "text" } },
              { type: "content_block_delta", delta: { type: "text_delta", text: "Taková složka není." } },
              { type: "message_delta", delta: { stop_reason: "end_turn" }, usage: { output_tokens: 5 } },
            ];
      return {
        events: (async function* () {
          for (const e of events) yield e;
        })(),
        final: async () => ({ content: round === 1 ? assistantContent : [] }),
        abort() {},
      };
    };
    const r = await handleRequest(chatRequest({ messages: [{ role: "user", content: "Co je ve složce?" }] }), env, ctx, factory);
    const events = parseSSE(await r.text());
    expect(events.filter((e) => e.type === "text").map((e) => e.text).join("")).toBe("Moment, podívám se. Taková složka není.");
    expect(calls.length).toBe(2);
    const second = calls[1].messages;
    expect(second[1]).toEqual({ role: "assistant", content: assistantContent }); // beze změny vč. thinking
    expect(second[2].content[0]).toMatchObject({ type: "tool_result", tool_use_id: "tu1", is_error: true }); // „..“ odmítnuto
    await flush();
    expect([...env.USAGE.store.values()]).toEqual(["145"]);
  });
});

import { GitHubReader, htmlToText, sanitizePath } from "../src/github";

describe("GitHubReader", () => {
  it("sanitizePath odmítne únik z repozitáře", () => {
    expect(sanitizePath("bd-michal/README.md")).toBe("bd-michal/README.md");
    expect(sanitizePath("/bd-michal//./README.md")).toBe("bd-michal/README.md");
    expect(sanitizePath("../etc/passwd")).toBeNull();
    expect(sanitizePath("a/../../b")).toBeNull();
    expect(sanitizePath(42)).toBeNull();
  });

  it("htmlToText odstraní skripty, styly a značky", () => {
    const t = htmlToText("<style>x{}</style><h1>Nabídka</h1><script>alert(1)</script><p>Cena&nbsp;1 600 000 Kč</p>");
    expect(t).toContain("Nabídka");
    expect(t).toContain("Cena 1 600 000 Kč");
    expect(t).not.toContain("alert");
  });

  it("čte soubor přes GitHub API (base64, UTF-8) a posílá token jen GitHubu", async () => {
    const seen: string[] = [];
    const fakeFetch = (async (url: string, init: any) => {
      seen.push(url);
      expect(init.headers.Authorization).toBe("Bearer gh");
      const b64 = btoa(String.fromCharCode(...new TextEncoder().encode("# Kotelna BD Michal\nTČ 3× 50 kW")));
      return new Response(JSON.stringify({ encoding: "base64", content: b64 }), { status: 200 });
    }) as any;
    const gh = new GitHubReader({ GITHUB_TOKEN: "gh", GITHUB_REPO: "szkandera79/Projekty" }, fakeFetch);
    const r = await gh.run("precti_soubor", { cesta: "bd-michal/README.md" });
    expect(r.isError).toBe(false);
    expect(r.content).toContain("Kotelna BD Michal");
    expect(r.content).toContain("TČ 3× 50 kW");
    expect(seen[0]).toBe("https://api.github.com/repos/szkandera79/Projekty/contents/bd-michal/README.md");
  });

  it("binární soubory a chyby přístupu vrací srozumitelně", async () => {
    const deny = (async () => new Response("{}", { status: 401 })) as any;
    const gh = new GitHubReader({ GITHUB_TOKEN: "gh", GITHUB_REPO: "a/b" }, deny);
    expect((await gh.run("precti_soubor", { cesta: "foto.jpg" })).content).toContain("není textový");
    const r = await gh.run("obsah_slozky", { cesta: "" });
    expect(r.isError).toBe(true);
    expect(r.content).toContain("odmítl přístup");
  });
});

describe("GitHubReader – výchozí fetch", () => {
  it("volá globální fetch bez vazby na objekt (Workers: Illegal invocation)", async () => {
    const orig = globalThis.fetch;
    let thisArg: unknown = "unset";
    (globalThis as any).fetch = function (this: unknown) {
      thisArg = this;
      return Promise.resolve(new Response(JSON.stringify([]), { status: 200 }));
    };
    try {
      const gh = new GitHubReader({ GITHUB_TOKEN: "gh", GITHUB_REPO: "a/b" });
      await gh.run("obsah_slozky", { cesta: "" });
      expect(thisArg).not.toBeInstanceOf(GitHubReader);
    } finally {
      globalThis.fetch = orig;
    }
  });
});

describe("Web (hledání a čtení stránek)", () => {
  it("ve výchozím stavu posílá web_search a web_fetch s lokalizací na ČR a datum", () => {
    const p: any = buildParams(makeEnv(), [{ role: "user", content: "Jaké je počasí?" }]);
    expect(p.tools.slice(0, 2).map((t: any) => t.type)).toEqual(["web_search_20260209", "web_fetch_20260209"]);
    expect(p.tools[0].user_location).toEqual({ type: "approximate", timezone: "Europe/Prague" });
    expect(p.system).toContain("internetu");
    expect(p.system).toMatch(/Dnes je .*20\d\d/);
  });

  it("pause_turn: vrátí obsah asistenta a pokračuje bez nové zprávy uživatele", async () => {
    const env = makeEnv();
    const { ctx } = makeCtx();
    const calls: any[] = [];
    const paused = [{ type: "server_tool_use", id: "s1", name: "web_search", input: { query: "počasí Ostrava" } }];
    const factory: StreamFactory = (_e, params) => {
      calls.push(structuredClone(params));
      const first = calls.length === 1;
      const events = first
        ? [{ type: "message_delta", delta: { stop_reason: "pause_turn" }, usage: { output_tokens: 3 } }]
        : [
            { type: "content_block_delta", delta: { type: "text_delta", text: "Zítra bude polojasno." } },
            { type: "message_delta", delta: { stop_reason: "end_turn" }, usage: { output_tokens: 6 } },
          ];
      return {
        events: (async function* () {
          for (const e of events) yield e;
        })(),
        final: async () => ({ content: first ? paused : [] }),
        abort() {},
      };
    };
    const r = await handleRequest(chatRequest({ messages: [{ role: "user", content: "Počasí?" }] }), env, ctx, factory);
    const events = parseSSE(await r.text());
    expect(events.filter((e) => e.type === "text").map((e) => e.text).join("")).toBe("Zítra bude polojasno.");
    expect(calls.length).toBe(2);
    expect(calls[1].messages.at(-1)).toEqual({ role: "assistant", content: paused });
  });
});

import { loadMemory, memoryPrompt, runMemoryTool } from "../src/memory";

describe("Dlouhodobá paměť", () => {
  it("uloží, nezdvojí, smaže a vypíše do promptu", async () => {
    const kv: any = new MemoryKV();
    expect(memoryPrompt(await loadMemory(kv))).toBe("");
    expect((await runMemoryTool(kv, "zapamatuj_si", { text: "Uživatel chce tykání." })).content).toContain("m1");
    expect((await runMemoryTool(kv, "zapamatuj_si", { text: "uživatel chce tykání." })).content).toContain("už v paměti");
    await runMemoryTool(kv, "zapamatuj_si", { text: "Firma ThermaVera Energy." });
    const p = memoryPrompt(await loadMemory(kv));
    expect(p).toContain("[m1] Uživatel chce tykání.");
    expect(p).toContain("[m2] Firma ThermaVera Energy.");
    expect((await runMemoryTool(kv, "zapomen", { cislo: "M1" })).isError).toBe(false);
    expect((await loadMemory(kv)).map((m) => m.id)).toEqual(["m2"]);
    expect((await runMemoryTool(kv, "zapomen", { cislo: "m9" })).isError).toBe(true);
    expect((await runMemoryTool(kv, "zapamatuj_si", { text: "  " })).isError).toBe(true);
  });

  it("paměť je v systémovém promptu a během odpovědi se nemění (i po zapamatuj_si)", async () => {
    const env = makeEnv({ WEB_TOOLS: "off" });
    await runMemoryTool(env.USAGE as any, "zapamatuj_si", { text: "Uživatel se jmenuje Jindřich." });
    const { ctx } = makeCtx();
    const calls: any[] = [];
    const factory: StreamFactory = (_e, params) => {
      calls.push(structuredClone(params));
      const first = calls.length === 1;
      const events = first
        ? [{ type: "message_delta", delta: { stop_reason: "tool_use" }, usage: { output_tokens: 3 } }]
        : [
            { type: "content_block_delta", delta: { type: "text_delta", text: "Zapamatuji si to." } },
            { type: "message_delta", delta: { stop_reason: "end_turn" }, usage: { output_tokens: 4 } },
          ];
      return {
        events: (async function* () {
          for (const e of events) yield e;
        })(),
        final: async () => ({
          content: first ? [{ type: "tool_use", id: "t1", name: "zapamatuj_si", input: { text: "Má rád stručnost." } }] : [],
        }),
        abort() {},
      };
    };
    const r = await handleRequest(chatRequest({ messages: [{ role: "user", content: "Zapamatuj si, že mám rád stručnost." }] }), env, ctx, factory);
    await r.text();
    expect(calls[0].system).toContain("Uživatel se jmenuje Jindřich.");
    expect(calls[1].system).toBe(calls[0].system); // stejný prefix v rámci odpovědi
    expect(calls[1].messages.at(-1).content[0]).toMatchObject({ type: "tool_result", tool_use_id: "t1" });
    expect((await loadMemory(env.USAGE as any)).map((m) => m.text)).toContain("Má rád stručnost.");
  });
});

import { validateContinuation, withTimeNote } from "../src/handler";
import { timeNote } from "../src/device";

describe("Fotky ve zprávách", () => {
  it("převede obrázek do formátu API a odmítne nepovolené typy a velikosti", () => {
    const ok: any = validateMessages([
      { role: "user", content: [{ type: "text", text: "Co je na fotce?" }, { type: "image", media_type: "image/jpeg", data: "QUJD" }] },
    ]);
    expect(ok[0].content[1]).toEqual({ type: "image", source: { type: "base64", media_type: "image/jpeg", data: "QUJD" } });
    expect(typeof validateMessages([{ role: "user", content: [{ type: "image", media_type: "image/heic", data: "x" }] }])).toBe("string");
    expect(typeof validateMessages([{ role: "user", content: [{ type: "image", media_type: "image/png", data: "x".repeat(5_000_001) }] }])).toBe("string");
    const five = Array.from({ length: 5 }, () => ({ type: "image", media_type: "image/png", data: "QQ==" }));
    expect(typeof validateMessages([{ role: "user", content: five }])).toBe("string");
    expect(typeof validateMessages([{ role: "assistant", content: [{ type: "text", text: "x" }] }])).toBe("string");
  });
});

describe("Kalendář v telefonu (client tools)", () => {
  it("timeNote je pro stejný čas stejná a withTimeNote ji připojí k poslední zprávě", () => {
    const iso = "2026-10-15T07:30:00Z";
    expect(timeNote(iso)).toBe(timeNote(iso));
    expect(timeNote(iso)).toContain("9:30");
    const m: any = withTimeNote([{ role: "user", content: "Co mám ve čtvrtek?" }], timeNote(iso));
    expect(m[0].content.at(-1).text).toContain("Aktuální datum a čas");
  });

  it("validateContinuation vyžaduje výsledky ke všem voláním", () => {
    const assistant = [{ type: "tool_use", id: "a", name: "pripominky", input: {} }];
    expect(validateContinuation(undefined)).toBeNull();
    expect(typeof validateContinuation({ assistant, tool_results: [{ tool_use_id: "x", content: "?" }] })).toBe("string");
    const ok: any = validateContinuation({ assistant, tool_results: [{ tool_use_id: "a", content: "Nic" }] });
    expect(ok[1].content[0]).toEqual({ type: "tool_result", tool_use_id: "a", content: "Nic" });
  });

  it("volání kalendáře se předá aplikaci a navazující požadavek pokračuje beze změny prefixu", async () => {
    const env = makeEnv({ WEB_TOOLS: "off" });
    const { ctx } = makeCtx();
    const assistant = [
      { type: "thinking", thinking: "", signature: "sig" },
      { type: "tool_use", id: "k1", name: "kalendar_udalosti", input: { od: "2026-10-15T00:00:00+02:00", do: "2026-10-16T00:00:00+02:00" } },
    ];
    const calls: any[] = [];
    const factory: StreamFactory = (_e, params) => {
      calls.push(structuredClone(params));
      const n = calls.length;
      const events =
        n === 1
          ? [{ type: "message_delta", delta: { stop_reason: "tool_use" }, usage: { output_tokens: 5 } }]
          : [
              { type: "content_block_delta", delta: { type: "text_delta", text: "Ve čtvrtek máte jednu schůzku." } },
              { type: "message_delta", delta: { stop_reason: "end_turn" }, usage: { output_tokens: 5 } },
            ];
      return {
        events: (async function* () {
          for (const e of events) yield e;
        })(),
        final: async () => ({ content: n === 1 ? assistant : [] }),
        abort() {},
      };
    };
    const base = { messages: [{ role: "user", content: "Co mám ve čtvrtek?" }], client_tools: ["kalendar"], now: "2026-10-14T08:00:00Z" };
    const r1 = parseSSE(await (await handleRequest(chatRequest(base), env, ctx, factory)).text());
    const ct = r1.find((e) => e.type === "client_tools");
    expect(ct.calls).toEqual([{ id: "k1", name: "kalendar_udalosti", input: assistant[1].input }]);
    expect(r1.at(-1)).toMatchObject({ type: "done", stop_reason: "client_tools" });
    expect(calls[0].tools.map((t: any) => t.name)).toContain("kalendar_vytvor");

    const r2 = parseSSE(
      await (
        await handleRequest(
          chatRequest({ ...base, continuation: { assistant: ct.pending.assistant, tool_results: [{ tool_use_id: "k1", content: "10:00 Schůzka SVJ" }] } }),
          env,
          ctx,
          factory,
        )
      ).text(),
    );
    expect(r2.filter((e) => e.type === "text").map((e) => e.text).join("")).toBe("Ve čtvrtek máte jednu schůzku.");
    const second = calls[1];
    expect(second.messages[0]).toEqual(calls[0].messages[0]); // stejná zpráva vč. poznámky s časem
    expect(second.messages[1]).toEqual({ role: "assistant", content: assistant });
    expect(second.messages[2].content[0]).toMatchObject({ tool_use_id: "k1", content: "10:00 Schůzka SVJ" });
  });

  it("bez client_tools se kalendář nenabízí", () => {
    const p: any = buildParams(makeEnv({ WEB_TOOLS: "off" }), [{ role: "user", content: "x" }]);
    expect(p.tools.map((t: any) => t.name)).not.toContain("kalendar_udalosti");
  });
});

import { handleSTT, handleTTS } from "../src/elevenlabs";

describe("ElevenLabs (hlas a rozpoznávání)", () => {
  const venv = (o: any = {}) => ({ ELEVENLABS_API_KEY: "el", ELEVENLABS_VOICE: "voice1234567", TTS_MONTHLY_CHARS: "20", STT_MONTHLY_SECONDS: "10", USAGE: new MemoryKV(), ...o }) as any;
  const req = (body: any) => new Request("https://x/v1/tts", { method: "POST", body: JSON.stringify(body) });

  it("TTS: pošle text s klíčem jen ElevenLabs, vrátí PCM a počítá znaky; po limitu 429", async () => {
    const env = venv();
    const seen: any[] = [];
    const fake = (async (url: string, init: any) => {
      seen.push({ url, init });
      return new Response(new Uint8Array([1, 2, 3, 4]), { status: 200 });
    }) as any;
    const r = await handleTTS(req({ text: "Dobrý den." }), env, fake);
    expect(r.status).toBe(200);
    expect(r.headers.get("content-type")).toBe("audio/pcm");
    expect(new Uint8Array(await r.arrayBuffer())).toEqual(new Uint8Array([1, 2, 3, 4]));
    expect(seen[0].url).toContain("/text-to-speech/voice1234567/stream?output_format=pcm_24000");
    expect(seen[0].init.headers["xi-api-key"]).toBe("el");
    expect(JSON.parse(seen[0].init.body).language_code).toBe("cs");
    expect((await handleTTS(req({ text: "Tohle je delší text nad limit." }), env, fake)).status).toBe(429);
  });

  it("TTS: vyčerpaný kredit ElevenLabs → 429 (aplikace přejde na hlas Apple)", async () => {
    const fake = (async () => new Response('{"detail":"quota"}', { status: 401 })) as any;
    expect((await handleTTS(req({ text: "Ahoj" }), venv({ TTS_MONTHLY_CHARS: "0" }), fake)).status).toBe(429);
    expect((await handleTTS(req({ text: "Ahoj" }), venv({ ELEVENLABS_API_KEY: undefined }), fake)).status).toBe(503);
  });

  it("STT: pošle WAV jako formulář s češtinou a vrátí text", async () => {
    let form: FormData | undefined;
    const fake = (async (_u: string, init: any) => {
      form = init.body;
      return new Response(JSON.stringify({ text: " Kolik stojí tepelné čerpadlo? " }), { status: 200 });
    }) as any;
    const wav = new Uint8Array(32_000);
    const r = await handleSTT(new Request("https://x/v1/stt", { method: "POST", body: wav }), venv(), fake);
    expect(await r.json()).toEqual({ text: "Kolik stojí tepelné čerpadlo?" });
    expect(form?.get("language_code")).toBe("cs");
    expect(form?.get("model_id")).toBe("scribe_v1");
    const tiny = await handleSTT(new Request("https://x/v1/stt", { method: "POST", body: new Uint8Array(10) }), venv(), fake);
    expect(tiny.status).toBe(400);
  });
});
