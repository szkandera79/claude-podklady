# Banner Generátor

AI nástroj pro tvorbu reklamních bannerů (PNG + MP4) pro Meta Ads pomocí Gemini API.

> **Nový tady?** Začni souborem `INSTALL.md` — Claude Code tě tím provede.

## Jak to funguje

1. **Produktová složka** — každý klient/značka má svou složku (např. `banners-vzor/`) s `PROJECT.md` (popis značky, produkty, cílová skupina, legislativa) a produktovými fotkami.
2. **PNG bannery** — generují se přes Gemini API (`gemini-3.1-flash-image-preview`) ve 3 formátech: feed 1080×1080, stories 1080×1920, portrait 1080×1350. Formát landscape 1200×628 se NEPOUŽÍVÁ.
3. **MP4 animace** — z hotového PNG se vytvoří HTML wrapper s CSS efekty (fade-in, shimmer, glow) a převede na MP4 přes puppeteer + ffmpeg.

## Rychlý start

```bash
npm install                    # Nainstaluje puppeteer + tsx
cp .env.example .env.local     # Zkopíruj a vyplň GEMINI_API_KEY
```

Detaily v `INSTALL.md`.

## Workflow pro nový produkt

Přečti si `BANNER-INSTRUCTIONS.md` — tam je kompletní postup (Fáze 0–4).

Zkráceně:
1. **Fáze 0:** Najdi/vytvoř `PROJECT.md` ve složce klienta (brand, produkty, cílovka, legislativa). Vzor je v `banners-vzor/PROJECT.md`.
2. **Fáze 1:** Analýza produktu → navrhni 6 konceptů → nech schválit.
3. **Fáze 2:** Generuj 18 PNG přes Gemini API (6 konceptů × 3 formáty).
4. **Fáze 3:** Ukaž výsledky, vyber nejlepší.
5. **Fáze 4:** Volitelně rozhýbej vybrané bannery na MP4.

## Struktura složek

```
banner-generator/
├── CLAUDE.md                  # Tento soubor (kontext pro AI)
├── INSTALL.md                 # Návod pro první spuštění
├── BANNER-INSTRUCTIONS.md     # Hlavní instrukce pro tvorbu bannerů
├── generate-banners.ts        # Batch generátor PNG přes Gemini API
├── banner-to-mp4.ts           # Skript pro konverzi HTML animace → MP4
├── package.json               # Dependencies (puppeteer, tsx)
├── .env.local                 # GEMINI_API_KEY (gitignored, vytvoříš sám)
├── .env.example               # Šablona pro .env.local
├── render-sablony.ts          # Render HTML šablon → PNG (puppeteer)
├── sablony/                   # HTML šablony bannerů (engine + značky + assets/)
├── configs/
│   └── vzor.ts                # Šablona configu pro generate-banners.ts
└── banners-vzor/              # Šablona klientské složky
    └── PROJECT.md             # Šablona popisu značky
```

## Příkazy

```bash
# Batch generování 18 PNG (6 konceptů × 3 formáty) podle configu
npx tsx generate-banners.ts vzor

# Jen vybrané koncepty
npx tsx generate-banners.ts vzor --only=K1,K3

# Jen jeden formát
npx tsx generate-banners.ts vzor --format=1080x1080

# MP4 z animovaného HTML banneru
npx tsx banner-to-mp4.ts banners-vzor/koncept_4_animated_1080x1920.html --duration=6 --fps=30
```

## HTML šablony (pixel-přesné bannery se skutečným logem a fotkami)

Druhá cesta vedle Gemini: bannery jako HTML/CSS se skutečnými assety, renderované puppeteerem do PNG.
Použij ji, když má banner přesně držet existující design, logo a reálný produkt (AI by je vymyslelo).

```bash
npx tsx render-sablony.ts reo-tc                 # REO HEATING – tepelná čerpadla (R1–R5)
npx tsx render-sablony.ts thermavera-kotelny     # ThermaVera – kotelny pro bytové domy (T1–T5)
npx tsx render-sablony.ts reo-tc --only=R1,R3    # jen vybrané
open sablony/reo-tc.html                         # náhled všech bannerů v prohlížeči (galerie)
```

- `sablony/engine.css` + `engine.js` = sdílený layout. Designový jazyk převzatý z REO AI bannerů
  (`Projekty/marketing/Design`): logo vlevo nahoře, headline se zvýrazněným slovem, fotka vpravo
  s přechodem do bílé, produkt přes fotku, kulatý odznak, zelený pruh, tmavý pruh se žlutým CTA, lišta ikon.
- `sablony/<šablona>.html` = značka (`BRAND`: logo, barvy) + pole `BANNERS` s texty. Značení v textech:
  `[[zelená]]`, `{{žlutá}}`, `**tučně**`, `|` = nový řádek. Jemné doladění pozic přes `vars` (např. `h1`,
  `prod-w`, `badge-x`) nebo `css` (`&` = selektor banneru).
- Výstup: `bannery-<šablona>/<ID>_1080x1080.png` + `prehled.jpg` (přehled skript nevytváří — mřížka 2 sloupce 540 px, skládá se ručně přes Pillow).
- Assety v `sablony/assets/`:
  - REO logo = **jen nové závazné logo** z `~/Claude/REO/logo/` (od 22. 10. 2026): `reo-logo.svg`,
    na tmavém banneru (`dark: true`) automaticky `reo-logo-white.svg` (`BRAND.logoDark`). Staré AI logo
    „REOHEATING“ (`reo-logo-ai.png`) ani modré „RH“ už nepoužívat.
  - Jednotky: velké (`reo-skupina*.png`, `reo-unit-1.png`) nesou na panelu původní AI logo svisle (fotky jednotek se nemění);
    řada **Smart** (`reo-smart-jednotka.png`) má jen nápis „REO HEATING“ (na celé logo není místo).
    Bannery o pilířích REO R290 Smart ukazují jen Smart jednotku.
  - Nepoužívej reálné fotky instalací, kde je na jednotce vidět jiné logo (`reo-foto-zahrada.jpg`).
  - ThermaVera: logo „7“ + nápis jako na webu, fotky `tv-*.jpg` z webu thermavera.cz.
- Texty REO: 3 pilíře R290 Smart (topí přímo ze slunce „od jara do podzimu“ / účinnost „víc než většina
  značkových“ + poznámka o SCOP při 35 °C / „kompresor Mitsubishi Electric“). Texty ThermaVera:
  návratnost jen „u vhodných projektů obvykle do 7 let“, ETS2 jen „může“, žádné fiktivní reference.

## Přidání nového klienta

1. Vytvoř novou složku: `banners-mojeznacka/`
2. Zkopíruj a uprav `banners-vzor/PROJECT.md` → `banners-mojeznacka/PROJECT.md`
3. Přidej produktové fotky (PNG / JPG / WEBP)
4. Vytvoř config v `configs/mojeznacka.ts` (vzor je v `configs/vzor.ts`)
5. Postupuj dle `BANNER-INSTRUCTIONS.md`

## Gemini API

- **Model:** `gemini-3.1-flash-image-preview` (vždy ověř dostupnost nejnovějšího)
- **Endpoint:** `https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent`
- **API klíč:** z `.env.local` → `GEMINI_API_KEY`
- **Získání klíče:** https://aistudio.google.com/apikey (zdarma)

## Pravidla

1. Komunikuj česky.
2. **Bannery jsou problem-first, ne feature-first** — headline rezonuje s bolestí/situací/potřebou cílovky, ne s tím co produkt obsahuje. Maximálně 1 ze 6 konceptů smí být čistě feature/price-driven, zbytek řeší konkrétní problém. Detaily v `BANNER-INSTRUCTIONS.md` (Zlaté pravidlo + Fáze 1 bod 6).
3. **Doménová jasnost (1-second test)** — banner musí v 1 sekundě sdělit i TÉMA produktu (řeč, spánek, hořčík, pleť…). Když to není v headlinu, MUSÍ být v eyebrow nebo sub-line. Detaily v `BANNER-INSTRUCTIONS.md` (Druhé zlaté pravidlo).
4. **Vyvážení médií** — sada 6 konceptů MUSÍ obsahovat min 2× lifestyle fotku + 2× ilustraci + 1× UGC + 1× typografii. Pouze-ilustrace nebo pouze-typografie sady = chyba. Detaily v `BANNER-INSTRUCTIONS.md` (Třetí zlaté pravidlo).
5. **Cold-audience test (1.5s scroll)** — banner musí v 1.5 sekundě říct cold audience: 1) je to produkt, 2) pro koho, 3) co řeší, 4) co dělat. Zákaz assumed-context headlinů („Nevíte co koupit?", „Konečně nic nehledám"). Vizuál musí poznatelně reprezentovat produkt — žádné abstraktní ikony bez produktu, žádné rozpadlé thumbnaily v UGC. Detaily v `BANNER-INSTRUCTIONS.md` (Čtvrté zlaté pravidlo).
6. Vždy odstraň bílé pozadí produktové fotky v banneru.
7. Stories safe zone: obsah jen mezi y=320 a y=1570 (Instagram UI překrývá zbytek).
8. Legislativa EU: žádné léčebné claims, jen životní situace a schválená EU tvrzení.
9. MP4 animace: NIKDY zoom/scale na Stories, pouze fade-in/shimmer/glow/sparkles.
10. **Žádné srovnávání s konkurencí** (zdravotní profesionály — logopeda, lékaře, ordinaci) v banneru — riziko negativní reakce + medical claim. „Doma to ale začít můžete" ✓ / „Za logopedem 40 min, doma za 10" ❌
11. **Frázování bezpečných sloves: kategorie > aktivní claim.** I bezpečná slovesa („rozvíjí", „procvičuje") mohou být riskantní podle formy. Preferuj „**PRODUKT pro X**" (kategorie/účel — „kartičky pro rozvoj řeči") místo „**AKTIVITA, která X**" (slib výsledku — „hraní, které rozvíjí řeč"). Detaily v `BANNER-INSTRUCTIONS.md` (Frázování bezpečných sloves).

## Požadavky na systém

- **Node.js** 20+ (pro puppeteer a tsx) — https://nodejs.org/ nebo `brew install node` (Mac) / `winget install OpenJS.NodeJS.LTS` (Windows)
- **ffmpeg** — potřeba pro konverzi na MP4
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`
  - Windows: `winget install Gyan.FFmpeg` (v PowerShellu jako admin)
- **Cursor** nebo **Claude Code** — AI IDE pro generování bannerů
- **Gemini API klíč** — zdarma na https://aistudio.google.com/apikey
