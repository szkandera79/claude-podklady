# Claude Voice CZ — Fáze 1: technické ověření

Stav k 11. 10. 2026. Body označené **[OVĚŘIT NA ZAŘÍZENÍ]** jsou zatím jen
teoretický předpoklad. Za ověřené je budeme považovat až po testu na vašem iPhonu.

## 1. Vývojové prostředí (zjištěno na Macu)

| Položka | Stav |
|---|---|
| macOS 26.6.2, Apple Silicon (arm64) | ✅ v pořádku |
| Volné místo 99 GB | ✅ stačí (Xcode + iOS platforma ≈ 25–35 GB) |
| Swift 6.3.2, git, Node 24 | ✅ k dispozici |
| **Xcode** | ❌ **chybí** — nutné nainstalovat z App Storu |
| iOS SDK / simulátor / `devicectl` | ❌ chybí (přijdou s Xcode) |
| Homebrew, GitHub CLI | není (zatím nepotřebujeme) |

## 2. Architektura

```
iPhone (SwiftUI)                         Server (prostředník)              Anthropic
┌──────────────────────────┐   HTTPS    ┌────────────────────────┐ HTTPS ┌──────────┐
│ Mikrofon → rozpoznání řeči│──text────▶│ ověří token zařízení    │──────▶│ Claude   │
│ detekce konce promluvy    │           │ hlídá denní limit       │       │ API      │
│ přerušení (barge-in)      │◀─stream───│ drží API klíč (secret)  │◀──────│ (stream) │
│ syntéza řeči po větách    │  (SSE)    │ (později: TTS, GitHub)  │       └──────────┘
│ přepis konverzace         │           └────────────────────────┘
└──────────────────────────┘
```

- **Aplikace** nikdy nedrží API klíč Anthropicu. Má jen vlastní přístupový token
  uložený v iOS Klíčence (Keychain).
- **Server** = Cloudflare Worker (bezplatný tarif stačí, umí streamování, klíč je
  uložen jako šifrovaný „secret"). Alternativa: Vercel. Hosting web4u (PHP)
  nedoporučuji, protože streamování přes PHP je tam nespolehlivé.
- **Streamování:** Claude posílá odpověď po kouscích. Aplikace začne mluvit hned
  po první dokončené větě, takže nečeká na celou odpověď. To je hlavní nástroj
  pro nízkou latenci.
- **Rozšiřitelnost (GitHub):** server bude mít „nástroje" (tool use), kam později
  přidáme čtení repozitářů a dokumentace. Aplikace se kvůli tomu měnit nemusí.

## 3. Výběr modelu Claude

| Model | Cena vstup/výstup za 1 M tokenů | Vlastnosti |
|---|---|---|
| **Claude Opus 5.5** (`claude-opus-5-5`) | $4 / $20 | nejlepší kvalita, výchozí volba |
| Claude Sonnet 5.5 (`claude-sonnet-5-5`) | $2 / $10 | rychlejší, poloviční cena |
| Claude Haiku 5.5 (`claude-haiku-5-5`) | $0,10 / $0,50 | nejrychlejší a nejlevnější |

**Doporučení:** začít s Opus 5.5 na nízké úrovni „přemýšlení" (`effort: low`),
což je rozumné pro konverzaci. Model půjde přepnout jedním nastavením na serveru,
bez nové instalace aplikace. Ve fázi 6 změříme reálnou prodlevu. Pokud bude Opus
pro hlas pomalý, rozhodnete, zda přejít na Sonnet nebo Haiku.

**Odhad nákladů (Opus 5.5):** jedna výměna ≈ 3 000 tokenů vstupu (kontext roste)
a 200 tokenů výstupu ≈ **0,3–0,4 Kč**. Díky ukládání kontextu do mezipaměti
(prompt caching) bude cena nižší. 100 výměn denně ≈ 30–40 Kč. Haiku by vyšel
zhruba 40× levněji.

## 4. Rozpoznávání české řeči (STT)

| Varianta | Výhody | Nevýhody | Cena |
|---|---|---|---|
| **Apple `SFSpeechRecognizer` (cs-CZ)** | zdarma, vestavěné, nativní, funguje se zamčenou obrazovkou při aktivní audio relaci | horší přesnost u odborných termínů; rozpoznávání na serverech Applu má limit délky úlohy (~1 min), takže je nutné průběžné restartování | 0 Kč |
| Apple `SpeechTranscriber` (iOS 26) | moderní, plně v zařízení | **podpora češtiny nepotvrzena** — ověříme za běhu přes `supportedLocales` | 0 Kč |
| Cloud: Soniox / ElevenLabs Scribe / OpenAI transcribe | výrazně vyšší přesnost, lepší interpunkce | další účet a klíč (přes server), streamování přes WebSocket, vyšší složitost | řádově 3–10 Kč/hod. řeči |

**Postup:** prototyp postavíme na Apple (zdarma, bez dalších účtů). Kód bude mít
rozhraní, které umožní později vyměnit poskytovatele za cloudového, pokud kvalita
nebude stačit.

## 5. Česká hlasová syntéza (TTS)

| Varianta | Výhody | Nevýhody | Cena |
|---|---|---|---|
| **Apple `AVSpeechSynthesizer`, hlas Zuzana (Vylepšená)** | zdarma, okamžitá odezva, offline, funguje na pozadí | znatelně „robotický" projev | 0 Kč |
| ElevenLabs (Flash / Multilingual) | velmi přirozená čeština, streamování | nejdražší; nutný účet | ~$50–100 / 1 M znaků (≈ 4–8 Kč / 10 min řeči) |
| OpenAI TTS / Azure Neural | dobrá kvalita, levnější | přirozenost češtiny je nutné posoudit poslechem | ~$15–22 / 1 M znaků |

**Postup:** prototyp s Apple hlasem. Ve fázi 6 přidáme volitelný cloudový hlas
přes server a porovnáte je poslechem. Kvalita hlasu je subjektivní a rozhodnutí
bude na vás.

## 6. Kritický požadavek: zamčená obrazovka a provoz na pozadí

Oficiální mechanismus iOS: **Background Mode „Audio"** + `AVAudioSession`
v kategorii `.playAndRecord`. Je to legální a schválený postup, který používají
hlasové a VoIP aplikace (ChatGPT, WhatsApp apod.). Žádné obcházení systému.

| Požadavek | Proveditelnost | Poznámka |
|---|---|---|
| Pokračování rozhovoru při zamčení | ✅ podporováno | relace se musí **spustit v popředí**. Dokud běží audio, iOS aplikaci nechá. Na pozadí ukazuje oranžovou tečku mikrofonu. **[OVĚŘIT NA ZAŘÍZENÍ]** |
| Spuštění nové relace ze zamčeného telefonu | ⚠️ omezeně | aplikace nemůže sama začít nahrávat na pozadí. Alternativa: zkratka Siri / tlačítko Akce („Hej Siri, Claude") přes App Intents. **[OVĚŘIT]** |
| Rozpoznávání řeči Applem na pozadí | ⚠️ pravděpodobně ano | dlouhé relace vyžadují restart rozpoznávací úlohy. **Hlavní technické riziko.** |
| Bluetooth sluchátka | ✅ | `.allowBluetooth` (HFP). Pozor: při použití mikrofonu sluchátek přejde zvuk do „telefonní" kvality |
| Audiosystém auta | ✅ přes Bluetooth (jako hovor) | **CarPlay aplikace není možná** — Apple povoluje kategorii hlasových asistentů jen vybraným vývojářům se zvláštním oprávněním. Bluetooth v autě ale bude fungovat. |
| Přerušení telefonním hovorem | ✅ | `AVAudioSession.interruptionNotification`; po skončení hovoru relaci obnovíme. Kontext konverzace zůstane. **[OVĚŘIT]** |
| Přerušení Clauda vlastní řečí (barge-in) | ✅ s výhradou | potlačení ozvěny (`voiceProcessing` v AVAudioEngine) zabrání tomu, aby si aplikace „slyšela" vlastní hlas. Na reproduktoru telefonu bude spolehlivost nižší než ve sluchátkách. |

## 7. Instalace s bezplatným Apple účtem

- ✅ Lze nainstalovat přímo z Macu přes kabel nebo Wi-Fi (Personal Team).
- ⚠️ **Podpis vyprší po 7 dnech.** Pak je nutné aplikaci znovu nainstalovat
  z Macu (1 kliknutí v Xcode). Data uvnitř aplikace zůstanou.
- ✅ Background Mode „Audio" s bezplatným účtem funguje.
- Placený Apple Developer Program (99 USD/rok) by odstranil 7denní limit a umožnil
  TestFlight. **Zatím ho nepotřebujeme.** Navrhnu ho až v případě, že vás bude
  týdenní přeinstalace obtěžovat.
- Na iPhonu bude nutné zapnout **Režim vývojáře** (Nastavení → Soukromí
  a zabezpečení). Provedu vás tím.

## 8. Bezpečnost a limity nákladů

1. API klíč Anthropicu existuje **jen** jako secret na serveru. Nikdy v aplikaci,
   v kódu, v gitu ani v této konverzaci. Na server ho zadáte sami příkazem,
   který vám připravím.
2. Aplikace se k serveru prokazuje tokenem uloženým v Klíčence iPhonu.
3. Veškerá komunikace probíhá přes HTTPS (TLS).
4. Ochrana proti nákladům, ve třech vrstvách:
   - **měsíční limit útraty přímo v Anthropic Console** (tvrdá pojistka, nastavíte sami),
   - **denní limit tokenů na serveru** (např. 2 M tokenů/den ≈ 250 Kč u Opusu),
   - limit délky odpovědi (`max_tokens`) a délky relace a automatické ukončení
     relace po delším tichu.

## 9. Hlavní rizika

1. **Rozpoznávání češtiny Applem** — přesnost a chování na pozadí. Zmírnění:
   vyměnitelný poskytovatel STT.
2. **Prodleva Opus 5.5** — přemýšlení nelze u tohoto modelu vypnout, jen snížit.
   Zmírnění: měření a případné přepnutí modelu na serveru.
3. **Ozvěna a falešné přerušení** při použití reproduktoru telefonu.
4. **7denní platnost** instalace s bezplatným účtem.
5. **iOS může v budoucnu změnit pravidla** pro audio na pozadí (nízké riziko).

## 10. Implementační postup

| Fáze | Obsah | Potřebuji od vás |
|---|---|---|
| 1 ✅ | tento dokument | — |
| 1b | instalace Xcode, prázdná aplikace na iPhonu (test podpisu a Režimu vývojáře) | instalace Xcode, kabel, Apple ID v Xcode |
| 2 | server (Cloudflare Worker) + aplikace: tlačítko → česká otázka → hlasová odpověď | účet Cloudflare, vložení API klíče do serveru |
| 2b | **test zamčené obrazovky** hned na prototypu (nejrizikovější část ověříme co nejdřív) | 10 minut testování |
| 3 | automatická detekce řeči, střídání mluvčích, přerušování | testování |
| 4 | Bluetooth, auto, telefonní hovor | test v autě |
| 5 | finální instalace + návod | — |
| 6 | latence, hlas, baterie, náklady | rozhodnutí o modelu a hlasu |
