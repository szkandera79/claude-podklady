> **Kopie projektu.** Hlavní vývojová verze (git, sestavování v Xcode) je v `~/Developer/ClaudeVoiceCZ` — iCloud Drive se pro Xcode nehodí. Tato složka slouží jako záloha v repozitáři Projekty; po změnách ji aktualizuje Claude.

# Claude Voice CZ

Nativní aplikace pro iPhone na hlasový rozhovor s Claudem v češtině.
Funguje i při zamčené obrazovce, s Bluetooth sluchátky a v autě.

## Struktura projektu

| Složka | Obsah |
|---|---|
| `ios/` | aplikace pro iPhone (Swift, SwiftUI) — otevřít `ios/ClaudeVoiceCZ.xcodeproj` v Xcode |
| `server/` | serverový prostředník na Cloudflare Workers (TypeScript); drží API klíč a hlídá limity |
| `scripts/` | instalační skripty |
| `docs/` | technické ověření, testovací protokol |

## Jak to funguje

1. Mikrofon → Apple rozpoznávání řeči (čeština, průběžně).
2. Po krátkém tichu (výchozí 1,2 s) aplikace považuje promluvu za dokončenou a pošle text na server.
3. Server ověří token aplikace a denní limit a přepošle konverzaci Claudovi (streamování).
4. Aplikace začne mluvit hned po první celé větě odpovědi (česká syntéza Apple).
5. Když promluvíte do Claudovy odpovědi, aplikace ho okamžitě utne a poslouchá vás.
6. Celý přepis se ukládá v telefonu; kontext konverzace přetrvá i po zavření aplikace.

## Instalace

### A. Server (jednou)
Předpoklady: účet Cloudflare (zdarma) a API klíč z console.anthropic.com.
```bash
~/Developer/ClaudeVoiceCZ/scripts/setup-server.sh
```
Skript vás provede vším. API klíč zadáváte jen do Terminálu, nikam jinam.

**Doporučená pojistka:** v Anthropic Console → Settings → Limits nastavte měsíční limit útraty.

### B. Aplikace na iPhone (bezplatný Apple účet)
1. Xcode → Settings → Accounts → přidat Apple ID.
2. Otevřít `ios/ClaudeVoiceCZ.xcodeproj`.
3. Připojit iPhone kabelem, na iPhonu potvrdit „Důvěřovat tomuto počítači".
4. Na iPhonu zapnout **Nastavení → Soukromí a zabezpečení → Režim vývojáře** (iPhone se restartuje).
5. V Xcode nahoře vybrat svůj iPhone a stisknout ▶ (Run).
6. Na iPhonu při prvním spuštění: **Nastavení → Obecné → Správa VPN a zařízení → Apple Development → Důvěřovat**.

⚠️ S bezplatným účtem vyprší instalace po **7 dnech** — pak stačí v Xcode znovu stisknout ▶.

### Lepší český hlas
Nastavení iPhonu → Zpřístupnění → Předčítání obsahu → Hlasy → Čeština → stáhnout
„Zuzana (vylepšený)". Aplikace automaticky použije nejkvalitnější stažený hlas.

## Nastavení serveru (bez přeinstalace aplikace)
V `server/wrangler.toml` lze změnit model (`MODEL`), úroveň přemýšlení (`EFFORT`),
max. délku odpovědi a denní limit tokenů. Poté v `server/`: `npm run deploy`.

## Testy
```bash
cd ~/Developer/ClaudeVoiceCZ/server && npm test
```
```bash
~/Developer/ClaudeVoiceCZ/ios/LogicTests/run.sh
```

## Bezpečnost
- API klíč Anthropicu je jen jako šifrovaný secret na Cloudflare.
- Aplikace má vlastní přístupový token (uložený v Klíčence iPhonu). Při úniku lze token
  vyměnit: smazat `server/.app-token` a spustit instalační skript znovu.
- Limity: denní limit tokenů na serveru, `max_tokens` na odpověď, limity délky konverzace,
  automatické ukončení relace po nečinnosti, měsíční limit v Anthropic Console.
