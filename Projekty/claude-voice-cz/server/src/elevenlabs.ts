// Přirozený hlas (text → řeč) a přesné rozpoznávání řeči (řeč → text) přes ElevenLabs.
// Klíč je jen na serveru; aplikace volá /v1/tts a /v1/stt se svým tokenem.

export interface VoiceEnv {
  ELEVENLABS_API_KEY?: string;
  ELEVENLABS_VOICE?: string; // ID hlasu
  ELEVENLABS_TTS_MODEL?: string; // výchozí eleven_flash_v2_5 (nízká prodleva, umí česky)
  ELEVENLABS_STT_MODEL?: string; // výchozí scribe_v1
  TTS_MONTHLY_CHARS?: string; // měsíční strop znaků (bezplatný tarif 10 000)
  STT_MONTHLY_SECONDS?: string; // měsíční strop sekund přepisu
  USAGE: KVNamespace;
}

export const TTS_MAX_TEXT = 1200;
export const STT_MAX_BYTES = 4_000_000; // ~2 min WAV 16 kHz mono

function monthKey(kind: string): string {
  return `${kind}:${new Date().toISOString().slice(0, 7)}`;
}

async function used(env: VoiceEnv, kind: string): Promise<number> {
  return Number((await env.USAGE.get(monthKey(kind))) ?? "0");
}

async function add(env: VoiceEnv, kind: string, amount: number): Promise<void> {
  const key = monthKey(kind);
  const current = Number((await env.USAGE.get(key)) ?? "0");
  await env.USAGE.put(key, String(current + amount), { expirationTtl: 60 * 60 * 24 * 70 });
}

export async function voiceUsage(env: VoiceEnv) {
  return {
    tts_chars: await used(env, "tts"),
    tts_limit: Number(env.TTS_MONTHLY_CHARS ?? "0"),
    stt_seconds: await used(env, "stt"),
    stt_limit: Number(env.STT_MONTHLY_SECONDS ?? "0"),
  };
}

function jsonError(status: number, error: string): Response {
  return new Response(JSON.stringify({ error }), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" },
  });
}

/** Text → řeč: vrací surové PCM 16 bit, 24 kHz, mono (přehrává se rovnou v aplikaci). */
export async function handleTTS(request: Request, env: VoiceEnv, fetcher: typeof fetch = (i, o) => fetch(i, o)): Promise<Response> {
  if (!env.ELEVENLABS_API_KEY) return jsonError(503, "Přirozený hlas není na serveru nastavený.");
  let body: any;
  try {
    body = await request.json();
  } catch {
    return jsonError(400, "Neplatný JSON");
  }
  const text = typeof body?.text === "string" ? body.text.trim() : "";
  if (!text) return jsonError(400, "Chybí text.");
  if (text.length > TTS_MAX_TEXT) return jsonError(400, "Text je příliš dlouhý.");
  const limit = Number(env.TTS_MONTHLY_CHARS ?? "0");
  if (limit > 0 && (await used(env, "tts")) + text.length > limit) {
    return jsonError(429, "Měsíční limit přirozeného hlasu je vyčerpán.");
  }
  const voice = /^[A-Za-z0-9]{10,40}$/.test(body?.voice ?? "") ? body.voice : env.ELEVENLABS_VOICE;
  if (!voice) return jsonError(503, "Není nastavený hlas.");
  const res = await fetcher(
    `https://api.elevenlabs.io/v1/text-to-speech/${voice}/stream?output_format=pcm_24000`,
    {
      method: "POST",
      headers: { "xi-api-key": env.ELEVENLABS_API_KEY, "content-type": "application/json", accept: "audio/pcm" },
      body: JSON.stringify({
        text,
        model_id: env.ELEVENLABS_TTS_MODEL || "eleven_flash_v2_5",
        language_code: "cs",
        voice_settings: { stability: 0.5, similarity_boost: 0.75, speed: 1.05 },
      }),
    },
  );
  if (!res.ok || !res.body) {
    const detail = (await res.text()).slice(0, 300);
    console.error("tts error", res.status, detail);
    const status = res.status === 401 || res.status === 402 || res.status === 429 ? 429 : 502;
    return jsonError(status, status === 429 ? "Kredit nebo limit ElevenLabs je vyčerpán." : "Chyba hlasové služby.");
  }
  await add(env, "tts", text.length);
  return new Response(res.body, { headers: { "content-type": "audio/pcm", "x-sample-rate": "24000" } });
}

/** Řeč → text: tělo požadavku je WAV (16 kHz mono); vrací {text}. */
export async function handleSTT(request: Request, env: VoiceEnv, fetcher: typeof fetch = (i, o) => fetch(i, o)): Promise<Response> {
  if (!env.ELEVENLABS_API_KEY) return jsonError(503, "Přesné rozpoznávání není na serveru nastavené.");
  const audio = await request.arrayBuffer();
  if (audio.byteLength < 1000) return jsonError(400, "Nahrávka je prázdná.");
  if (audio.byteLength > STT_MAX_BYTES) return jsonError(400, "Nahrávka je příliš dlouhá.");
  const seconds = Math.ceil(audio.byteLength / 32_000); // 16 kHz × 2 B
  const limit = Number(env.STT_MONTHLY_SECONDS ?? "0");
  if (limit > 0 && (await used(env, "stt")) + seconds > limit) {
    return jsonError(429, "Měsíční limit přesného rozpoznávání je vyčerpán.");
  }
  const form = new FormData();
  form.append("model_id", env.ELEVENLABS_STT_MODEL || "scribe_v1");
  form.append("language_code", "cs");
  form.append("tag_audio_events", "false");
  form.append("file", new Blob([audio], { type: "audio/wav" }), "promluva.wav");
  const res = await fetcher("https://api.elevenlabs.io/v1/speech-to-text", {
    method: "POST",
    headers: { "xi-api-key": env.ELEVENLABS_API_KEY },
    body: form,
  });
  if (!res.ok) {
    const detail = (await res.text()).slice(0, 300);
    console.error("stt error", res.status, detail);
    const status = res.status === 401 || res.status === 402 || res.status === 429 ? 429 : 502;
    return jsonError(status, status === 429 ? "Kredit nebo limit ElevenLabs je vyčerpán." : "Chyba rozpoznávání řeči.");
  }
  const data: any = await res.json();
  await add(env, "stt", seconds);
  return new Response(JSON.stringify({ text: String(data?.text ?? "").trim() }), {
    headers: { "content-type": "application/json; charset=utf-8" },
  });
}

/** Seznam hlasů: vlastní (v účtu) a sdílené české z knihovny ElevenLabs. */
export async function handleVoices(url: URL, env: VoiceEnv, fetcher: typeof fetch = (i, o) => fetch(i, o)): Promise<Response> {
  if (!env.ELEVENLABS_API_KEY) return jsonError(503, "Hlas není nastavený.");
  const headers = { "xi-api-key": env.ELEVENLABS_API_KEY };
  const [own, shared] = await Promise.all([
    fetcher("https://api.elevenlabs.io/v2/voices?page_size=100", { headers }).then((r) => (r.ok ? r.json() : { voices: [] })),
    fetcher(
      `https://api.elevenlabs.io/v1/shared-voices?language=cs&page_size=${Math.min(Number(url.searchParams.get("n")) || 30, 100)}&sort=usage_character_count_1y`,
      { headers },
    ).then((r) => (r.ok ? r.json() : { voices: [] })),
  ]);
  const pick = (v: any) => ({
    voice_id: v.voice_id,
    name: v.name,
    gender: v.gender ?? v.labels?.gender ?? null,
    age: v.age ?? v.labels?.age ?? null,
    accent: v.accent ?? v.labels?.accent ?? null,
    category: v.category ?? null,
    description: (v.description ?? "").slice(0, 160),
    preview_url: v.preview_url ?? null,
    public_owner_id: v.public_owner_id ?? null,
    usage_1y: v.usage_character_count_1y ?? null,
  });
  return new Response(
    JSON.stringify({ current: env.ELEVENLABS_VOICE ?? null, own: (own as any).voices?.map(pick) ?? [], czech: (shared as any).voices?.map(pick) ?? [] }),
    { headers: { "content-type": "application/json; charset=utf-8" } },
  );
}

/** Přidá sdílený hlas z knihovny do účtu (nutné před použitím přes API). */
export async function handleAddVoice(request: Request, env: VoiceEnv, fetcher: typeof fetch = (i, o) => fetch(i, o)): Promise<Response> {
  if (!env.ELEVENLABS_API_KEY) return jsonError(503, "Hlas není nastavený.");
  const body: any = await request.json().catch(() => ({}));
  const ok = (s: unknown) => typeof s === "string" && /^[A-Za-z0-9]{6,64}$/.test(s);
  if (!ok(body.public_owner_id) || !ok(body.voice_id)) return jsonError(400, "Neplatný hlas.");
  const res = await fetcher(`https://api.elevenlabs.io/v1/voices/add/${body.public_owner_id}/${body.voice_id}`, {
    method: "POST",
    headers: { "xi-api-key": env.ELEVENLABS_API_KEY, "content-type": "application/json" },
    body: JSON.stringify({ new_name: String(body.name ?? "Český hlas").slice(0, 60) }),
  });
  const text = await res.text();
  return new Response(text, { status: res.status, headers: { "content-type": "application/json; charset=utf-8" } });
}
