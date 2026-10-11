# Instalace Banner Generátoru

Tento soubor je určený **pro AI asistenta** (Claude Code v terminálu nebo Cursor).
Když ti uživatel řekne **„nainstaluj banner generátor"**, **„rozjeď to"** nebo prostě otevře tento projekt poprvé, proveď tyto kroky **automaticky** a komunikuj česky.

> **Když jsi člověk a čteš tohle:** stačí v této složce spustit Claude Code (`claude` v terminálu) nebo Cursor a napsat **„nainstaluj to"**. AI tě tím provede.

---

## ⚠️ AI: nejdřív zjisti platformu

Spusť:

```bash
uname -s 2>/dev/null || echo "Windows"
```

- Výstup `Darwin` → **macOS** → použij `brew` / `cp` / `which` / Unix shell.
- Výstup `Linux` → **Linux** (případně WSL na Windows) → `apt`/`dnf` / Unix shell.
- Výstup `Windows` → **nativní Windows** → použij **PowerShell** ekvivalenty: `Copy-Item`, `Get-Content`, `Test-Path`, `where.exe`, `winget` (viz „Windows poznámky" v každém kroku).

V dalších krocích jsou příkazy pro **macOS / Linux** primární. Pro **Windows** je vždy alternativa pod nadpisem „💠 Windows".

---

## Co tahle aplikace dělá

AI nástroj, který z popisu značky a produktové fotky vygeneruje **18 reklamních bannerů** pro Meta Ads (Facebook + Instagram) — feed, stories i portrait — za pár minut. Funguje přes **Google Gemini API**.

Detaily v `CLAUDE.md` a `BANNER-INSTRUCTIONS.md`.

---

## Kroky instalace (pro AI asistenta)

### 1. Ověř Node.js

```bash
node -v
```

- Pokud je **Node 20 nebo vyšší** → OK, pokračuj.
- Pokud chybí nebo je nižší:

  **macOS / Linux:**
  > „Potřebuješ Node.js 20+. Nainstaluj LTS verzi z https://nodejs.org/ nebo přes Homebrew: `brew install node`. Až to budeš mít, řekni mi „pokračuj"."

  **💠 Windows:**
  > „Potřebuješ Node.js 20+. Nejjednodušší cesta: stáhni LTS installer z https://nodejs.org/ a klikni dvakrát. Alternativně v PowerShellu: `winget install OpenJS.NodeJS.LTS`. Po instalaci **zavři a znovu otevři PowerShell**, aby se načetla `PATH`. Pak řekni „pokračuj"."

### 2. Spusť `npm install`

```bash
npm install
```

Stáhne `puppeteer` (chromium pro screenshoty z HTML, ~170 MB) a `tsx` (TypeScript runner). Trvá ~1 minutu. Funguje stejně na všech platformách.

### 3. Zjisti, jestli existuje `.env.local`

**macOS / Linux:**
```bash
ls -la .env.local 2>/dev/null
```

**💠 Windows (PowerShell):**
```powershell
Test-Path .env.local
```

- **Pokud `.env.local` neexistuje:**
  1. Zkopíruj šablonu:
     - macOS / Linux: `cp .env.example .env.local`
     - 💠 Windows (PowerShell): `Copy-Item .env.example .env.local`
  2. Zeptej se uživatele česky:
     > „Potřebuju tvůj **Gemini API klíč**. Pokud ho ještě nemáš, vytvoř si ho zdarma na https://aistudio.google.com/apikey (přihlásíš se Google účtem → tlačítko „Create API key" → zkopíruješ klíč začínající `AIza…`). Vlož mi ho sem do chatu."
  3. Po obdržení klíče: nahraď `your-api-key-here` v `.env.local` skutečným klíčem. Klíč **nikdy nevypisuj zpátky uživateli** ani neukládej nikam jinam než do `.env.local`.

- **Pokud `.env.local` existuje:** zkontroluj, že `GEMINI_API_KEY` není prázdné nebo `your-api-key-here`. Pokud je, postupuj jako výše.

### 4. Ověř, že je nainstalovaný `ffmpeg`

**macOS / Linux:**
```bash
which ffmpeg
```

**💠 Windows (PowerShell):**
```powershell
where.exe ffmpeg
```

- Pokud výstup ukazuje cestu → OK.
- Pokud chybí:

  **macOS:**
  > „Pro převod animovaných bannerů na MP4 potřebuju `ffmpeg`. Nainstaluj ho přes Homebrew: `brew install ffmpeg`. PNG bannery fungují i bez něj — bez MP4 efektů ale animace nepojedou. Chceš ffmpeg nainstalovat teď, nebo to přeskočit?"

  **Linux (Ubuntu/Debian):**
  > „Pro MP4 animace potřebuju `ffmpeg`: `sudo apt install ffmpeg`. PNG bannery fungují i bez něj."

  **💠 Windows:**
  > „Pro MP4 animace potřebuju `ffmpeg`. Nejjednodušší instalace v PowerShellu jako admin: `winget install Gyan.FFmpeg`. **Po instalaci zavři a znovu otevři PowerShell**, aby se načetla `PATH`. PNG bannery fungují i bez něj — bez MP4 efektů ale animace nepojedou. Chceš ffmpeg nainstalovat teď, nebo to přeskočit?"

### 5. Ověř, že Gemini API funguje

Tento test funguje na všech platformách (curl je dnes součástí Windows 10+ i macOS i Linuxu):

**macOS / Linux:**
```bash
API_KEY=$(grep GEMINI_API_KEY .env.local | cut -d'"' -f2)
curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-image-preview?key=${API_KEY}"
```

**💠 Windows (PowerShell):**
```powershell
$API_KEY = (Get-Content .env.local | Select-String 'GEMINI_API_KEY').ToString().Split('"')[1]
curl.exe -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-image-preview?key=$API_KEY"
```

- Pokud výstup obsahuje `"displayName"` → API funguje, pokračuj.
- Pokud obsahuje `"error"` (např. `API_KEY_INVALID`) → klíč je špatně, vrať se na krok 3 a požádej o nový.

### 6. Hlášení uživateli

Vypiš česky:

```
✅ Instalace hotová!

Co umíš dál:
1. Otevři `CLAUDE.md` — přehled jak projekt funguje.
2. Otevři `BANNER-INSTRUCTIONS.md` — kompletní postup tvorby bannerů (Fáze 0–4).
3. Když budeš chtít začít s prvním produktem, řekni mi:
   „Vytvoř bannery pro [název produktu]"
   a přilož URL produktové stránky + produktovou fotku.

Šablonu klientské složky najdeš v `banners-vzor/PROJECT.md`.
Šablonu configu pro generátor v `configs/vzor.ts`.
```

---

## Časté problémy

**`npm install` spadne na puppeteer / Chromium:**
Puppeteer stahuje Chromium (~170 MB). Pokud spadne na firewallu/proxy, zkus znovu, nebo přeskoč download a používej systémový prohlížeč:
- macOS / Linux: `PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true npm install`
- 💠 Windows (PowerShell): `$env:PUPPETEER_SKIP_CHROMIUM_DOWNLOAD="true"; npm install`

**`GEMINI_API_KEY nenalezen v .env.local`:**
Klíč v `.env.local` musí být ve formátu `GEMINI_API_KEY="AIza..."` (s uvozovkami, bez mezer kolem `=`). Na Windows si dej pozor, ať `.env.local` není uložený jako `.env.local.txt` — Poznámkový blok to dělá; vypni v Průzkumníku „Skrýt přípony" a soubor přejmenuj.

**`node` nebo `npm` se nenajde po instalaci (Windows):**
Po instalaci Node.js **zavři a znovu otevři PowerShell**, aby se přepsala proměnná `PATH`. To samé platí po instalaci `ffmpeg` přes `winget`.

**Banner se vygeneruje, ale je v angličtině:**
Gemini občas ignoruje češtinu. V configu konceptu zdůrazni `Czech language, exact wording` a po vygenerování zkontroluj texty — případně regeneruj přes `--only=K3`.

**MP4 nejde vytvořit:**
Ověř, že `ffmpeg` je v `PATH` (`which ffmpeg` na Macu/Linuxu, `where.exe ffmpeg` na Windows). Pokud chybí, vrať se na krok 4.

**Spouštím to v Claude Code v WSL na Windows:**
WSL = Linux subsystém, takže používej **macOS / Linux** příkazy, ne PowerShell. `.env.local` ale musí ležet ve složce projektu uvnitř WSL filesystému, ne v `/mnt/c/...` přes Windows boundary.
