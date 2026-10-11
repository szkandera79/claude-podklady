// Nástroje pro čtení repozitáře projektů na GitHubu (jen čtení, jeden repozitář).

export interface GitHubEnv {
  GITHUB_TOKEN?: string;
  GITHUB_REPO?: string; // "vlastnik/nazev"
}

export const MAX_RESULT_CHARS = 30_000;

export const GITHUB_TOOLS = [
  {
    name: "seznam_projektu",
    description:
      "Vrátí přehled projektů uživatele: složky v kořeni repozitáře a obsah kořenového CLAUDE.md (rozcestník s popisem projektů). Použij jako první krok, když se uživatel ptá na své projekty.",
    input_schema: { type: "object", properties: {}, required: [] },
  },
  {
    name: "obsah_slozky",
    description: "Vypíše soubory a podsložky v dané složce repozitáře (cesta relativní ke kořeni, např. „bd-michal“ nebo „thermavera-web/assets“).",
    input_schema: {
      type: "object",
      properties: { cesta: { type: "string", description: "Cesta ke složce; prázdný řetězec = kořen." } },
      required: ["cesta"],
    },
  },
  {
    name: "precti_soubor",
    description:
      "Přečte textový soubor z repozitáře (README, .md, .py, .json, .html — u HTML vrátí jen čitelný text bez značek a skriptů). Dlouhé soubory jsou zkrácené.",
    input_schema: {
      type: "object",
      properties: { cesta: { type: "string", description: "Cesta k souboru, např. „bd-michal/README.md“." } },
      required: ["cesta"],
    },
  },
  {
    name: "hledej",
    description:
      "Hledá v repozitáři: soubory, jejichž cesta obsahuje hledaný výraz, a (pokud to GitHub umožní) soubory obsahující výraz v textu. Použij, když nevíš, kde co leží.",
    input_schema: {
      type: "object",
      properties: { vyraz: { type: "string", description: "Hledané slovo nebo část názvu." } },
      required: ["vyraz"],
    },
  },
].map((t) => ({ ...t, eager_input_streaming: true }));

export function githubEnabled(env: GitHubEnv): boolean {
  return Boolean(env.GITHUB_TOKEN && env.GITHUB_REPO && /^[\w.-]+\/[\w.-]+$/.test(env.GITHUB_REPO));
}

/** Bezpečná cesta uvnitř repozitáře (žádné „..“, žádné absolutní cesty). */
export function sanitizePath(input: unknown): string | null {
  if (typeof input !== "string") return null;
  const parts = input.trim().replace(/\\/g, "/").split("/").filter((p) => p && p !== ".");
  if (parts.some((p) => p === "..")) return null;
  return parts.join("/");
}

function stripAccents(s: string): string {
  return s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
}

export function htmlToText(html: string): string {
  return html
    .replace(/<(script|style|svg|noscript)[\s\S]*?<\/\1>/gi, " ")
    .replace(/<br\s*\/?>|<\/(p|div|li|h[1-6]|tr|section|table)>/gi, "\n")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/[ \t]+/g, " ")
    .replace(/\n\s*\n+/g, "\n")
    .trim();
}

function truncate(s: string, max = MAX_RESULT_CHARS): string {
  return s.length > max ? s.slice(0, max) + `\n…[zkráceno, soubor má ${s.length} znaků]` : s;
}

const BINARY = /\.(png|jpe?g|gif|webp|pdf|zip|docx?|xlsx?|pptx?|heic|mov|mp4|woff2?|ttf|ico)$/i;

type Fetcher = typeof fetch;

export class GitHubReader {
  private treeCache: string[] | null = null;
  // Pozor: v Cloudflare Workers se `fetch` nesmí volat jako metoda objektu (Illegal invocation) → obalit.
  constructor(private env: GitHubEnv, private fetcher: Fetcher = (input, init) => fetch(input, init)) {}

  private async api(path: string): Promise<any> {
    const res = await this.fetcher(`https://api.github.com/repos/${this.env.GITHUB_REPO}${path}`, {
      headers: {
        Authorization: `Bearer ${this.env.GITHUB_TOKEN}`,
        Accept: "application/vnd.github+json",
        "User-Agent": "claude-voice-cz",
        "X-GitHub-Api-Version": "2022-11-28",
      },
    });
    if (res.status === 404) throw new Error("Nenalezeno.");
    if (res.status === 401 || res.status === 403) throw new Error(`GitHub odmítl přístup (${res.status}).`);
    if (!res.ok) throw new Error(`Chyba GitHubu (${res.status}).`);
    return res.json();
  }

  private encode(path: string): string {
    return path.split("/").map(encodeURIComponent).join("/");
  }

  async listDir(path: string): Promise<string> {
    const items = await this.api(`/contents/${this.encode(path)}`);
    if (!Array.isArray(items)) return `„${path}“ je soubor, ne složka.`;
    const lines = items
      .filter((i: any) => !i.name.startsWith("."))
      .map((i: any) => (i.type === "dir" ? `📁 ${i.name}/` : `${i.name} (${Math.round((i.size ?? 0) / 1024)} kB)`));
    return lines.length ? lines.join("\n") : "Složka je prázdná.";
  }

  async readFile(path: string): Promise<string> {
    if (!path) return "Chybí cesta k souboru.";
    if (BINARY.test(path)) return "Tento soubor není textový (obrázek, PDF, Office…) a nelze ho přečíst.";
    const file = await this.api(`/contents/${this.encode(path)}`);
    if (Array.isArray(file)) return `„${path}“ je složka. Obsah:\n` + (await this.listDir(path));
    if (file.encoding !== "base64" || typeof file.content !== "string") {
      return "Soubor je příliš velký nebo ho nelze načíst přes API.";
    }
    const bytes = Uint8Array.from(atob(file.content.replace(/\n/g, "")), (c) => c.charCodeAt(0));
    let text = new TextDecoder("utf-8").decode(bytes);
    if (/\.html?$/i.test(path)) text = htmlToText(text);
    return truncate(text);
  }

  async listProjects(): Promise<string> {
    const root = await this.listDir("");
    let guide = "";
    try {
      guide = await this.readFile("CLAUDE.md");
    } catch {
      /* rozcestník nemusí existovat */
    }
    return truncate(`Složky v kořeni repozitáře:\n${root}\n\n--- CLAUDE.md (rozcestník) ---\n${guide}`);
  }

  private async tree(): Promise<string[]> {
    if (!this.treeCache) {
      const repo = await this.api("");
      const t = await this.api(`/git/trees/${encodeURIComponent(repo.default_branch)}?recursive=1`);
      this.treeCache = (t.tree ?? []).filter((e: any) => e.type === "blob").map((e: any) => e.path as string);
    }
    return this.treeCache ?? [];
  }

  async search(query: string): Promise<string> {
    const q = query.trim();
    if (q.length < 2) return "Zadej alespoň dva znaky.";
    const needle = stripAccents(q);
    const byPath = (await this.tree()).filter((p) => stripAccents(p).includes(needle)).slice(0, 30);
    let byContent: string[] = [];
    try {
      const res = await this.fetcher(
        `https://api.github.com/search/code?per_page=15&q=${encodeURIComponent(`${q} repo:${this.env.GITHUB_REPO}`)}`,
        {
          headers: {
            Authorization: `Bearer ${this.env.GITHUB_TOKEN}`,
            Accept: "application/vnd.github+json",
            "User-Agent": "claude-voice-cz",
          },
        },
      );
      if (res.ok) byContent = (((await res.json()) as any).items ?? []).map((i: any) => i.path as string);
    } catch {
      /* fulltext je jen doplněk */
    }
    const parts: string[] = [];
    if (byPath.length) parts.push("Soubory podle názvu:\n" + byPath.join("\n"));
    if (byContent.length) parts.push("Soubory obsahující výraz:\n" + byContent.join("\n"));
    return parts.length ? parts.join("\n\n") : `Pro „${q}“ jsem nic nenašel.`;
  }

  /** Spustí nástroj podle jména; chyby vrací jako text (is_error). */
  async run(name: string, input: any): Promise<{ content: string; isError: boolean }> {
    try {
      switch (name) {
        case "seznam_projektu":
          return { content: await this.listProjects(), isError: false };
        case "obsah_slozky": {
          const p = sanitizePath(input?.cesta ?? "");
          if (p === null) return { content: "Neplatná cesta.", isError: true };
          return { content: await this.listDir(p), isError: false };
        }
        case "precti_soubor": {
          const p = sanitizePath(input?.cesta);
          if (!p) return { content: "Neplatná nebo chybějící cesta.", isError: true };
          return { content: await this.readFile(p), isError: false };
        }
        case "hledej": {
          if (typeof input?.vyraz !== "string") return { content: "Chybí hledaný výraz.", isError: true };
          return { content: await this.search(input.vyraz), isError: false };
        }
        default:
          return { content: `Neznámý nástroj ${name}.`, isError: true };
      }
    } catch (err: any) {
      console.error("github tool error", name, err?.message);
      return { content: err?.message ?? "Chyba při čtení repozitáře.", isError: true };
    }
  }
}
