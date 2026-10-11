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
    const off: any = buildParams(makeEnv(), [{ role: "user", content: "Ahoj" }]);
    expect(off.tools).toBeUndefined();
    const on: any = buildParams(makeEnv({ GITHUB_TOKEN: "gh", GITHUB_REPO: "szkandera79/Projekty" }), [
      { role: "user", content: "Ahoj" },
    ]);
    expect(on.tools.map((t: any) => t.name)).toEqual(["seznam_projektu", "obsah_slozky", "precti_soubor", "hledej"]);
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
