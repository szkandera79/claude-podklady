# AI Marketing Manager – audit a návrh (fáze 1 + 2)

Datum: 31. 10. 2026 · Stav: **návrh ke schválení, nic se neprogramuje**

Značení: **[OVĚŘENO]** = zjištěno v souborech / dokumentaci · **[PŘEDPOKLAD]** = odhad, potvrdit ·
**[CHYBÍ PŘÍSTUP]** = vyžaduje tvou akci nebo schválení třetí strany (Meta, Google).

---

## 1. Co už máme hotové (audit)

Prošel jsem repozitář Projekty, `~/Claude`, `~/Developer`, historii sezení v Claude Code a seznam artefaktů.

| Co | Kde | Využitelnost pro novou aplikaci |
|---|---|---|
| **Generátor bannerů** – Gemini API (`gemini-3.1-flash-image-preview`), 3 formáty Meta (1080×1080, 1080×1920, 1080×1350), HTML šablony s reálným logem a fotkami (puppeteer → PNG), PNG → MP4 | `banner-generator/` [OVĚŘENO] | **Vysoká.** Přenese se jako modul „Kreativy“: prompty konceptů, šablony `sablony/*.html` (REO R1–R5, ThermaVera T1–T5), `PROJECT.md` jako vzor profilu značky. Gemini billing je aktivní. |
| **Pravidla a znalosti značky REO HEATING** – logo, barvy (#34A263), zákaz zmínek výrobce (Power World / Helios), ověřené parametry (SCOP 55 °C = 3,97; LWA z TÜV SÜD; 3 prodejní pilíře Smart), ceníky | paměť Claude + `REO/`, `konkurence-tc-smart/`, `audit-akustika-…`, `reo-nahradni-dily/` [OVĚŘENO] | **Vysoká.** Základ „AI znalostní databáze“ značky – každý údaj se zdrojem. Přesně to splní požadavek „AI nesmí měnit technické parametry“. |
| **Tiskové materiály** – letáky, katalogy Smart, RH X50/X100 (CZ/EN) | artefakt „Marketing REO HEATING“ 8zGFmzL6…, `REO/` [OVĚŘENO] | Střední – obsah do knihovny médií a zdroj textů. |
| **REO CRM** – leady z formulářů FB/IG (přes Google Drive tabulky), fáze obchodu, schůzky, faktury | `reo-crm/`, artefakt LnRFiysRw114a2LJbqid6P [OVĚŘENO] | **Vysoká pro měření.** Aplikace zná cenu za *poptávku*; CRM zná, zda z ní byl *zákazník*. Propojením získáme cenu za zakázku. Data CRM jsou osobní údaje – zůstávají mimo git. |
| **Google Ads + Sklik pro ThermaVeru** – živé kampaně, GA4, importované konverze (`generate_lead`, `phone_click`…) | `marketing/google-ads-kampan.md`, `ppc-podklady.md`, paměť [OVĚŘENO] | Střední – podklady pro budoucí modul Google Ads; měření konverzí na webu je vzor i pro REO. |
| **Leady SVJ s drahým CZT** + právní pravidla oslovování (§ 7 zák. 480/2004 Sb.) | `marketing/svj-leady-czt/` [OVĚŘENO] | Nízká přímo; pravidla se převezmou do mantinelů AI (žádné nevyžádané e-maily). |
| **Claude Voice CZ** – serverový prostředník (Cloudflare Worker) drží API klíč a denní limity, česká řeč | `~/Developer/ClaudeVoiceCZ` [OVĚŘENO] | Střední – vzor bezpečného držení klíčů a limitů útraty AI; hlasové ovládání v pozdější iOS verzi. |
| **Fotky realizací** | `Reference zelena kotelna/`, „REO Realizace “ | Pozor: **čeká se na souhlas partnera** s použitím fotek (paměť). Do reklam až po souhlasu. |

### Co jsem NENAŠEL
- **Systém pro navrhování marketingových témat a kampaní**, o kterém píšeš. V lokálních projektech ani
  v historii Claude Code není – nejspíš vznikl v **běžném chatu na claude.ai** (tam nevidím) nebo jinde.
  → **Potřebuji od tebe odkaz/umístění** (projekt na claude.ai, Google Drive, export). Prompty a postupy
  z něj převezmu do AI vrstvy, ať nic neduplikujeme.
- **Žádná integrace s Meta API** – neexistuje Meta App, tokeny ani kód. [OVĚŘENO]
- **Super Heating CZ** – kromě zmínky v generátoru bannerů nemám žádné podklady (web, logo, stránky FB/IG,
  sortiment, vztah k e-shopu eko4home / Riva Trade). [CHYBÍ PŘÍSTUP]

---

## 2. Co můžeme využít (integrace bez duplicit)

1. **Kreativy:** logika `generate-banners.ts` + `render-sablony.ts` se přesune do serverové služby
   „creative“ (stejné prompty, šablony, assety). Původní nástroj zůstává, nemaže se.
2. **Profil značky:** `banners-*/PROJECT.md` + paměťová pravidla → strukturovaný profil značky v databázi
   (tón, zakázaná slova, povinné formulace typu „orientačně“, logo, barvy).
3. **Znalostní databáze:** ověřené technické údaje (datové listy R290, akustika, ceníky) se naimportují
   jako „fakta se zdrojem“. AI smí v textech použít jen tato fakta; vše ostatní označí k ověření.
4. **CRM:** v 1. verzi jen čtení (párování leadů z Meta formulářů s fází v CRM). Plná migrace CRM do
   aplikace je možná později – ne teď.
5. **Měření:** GA4 + konverzní události z thermavera.cz jako vzor pro REO web a e-shop Super Heating.

---

## 3. Co je potřeba doprogramovat

Prakticky celou aplikaci: přihlášení, správu značek, napojení Meta (synchronizace, zápisy se schvalováním),
dashboard, AI asistenta s nástroji, kalendář a plánovač publikování, reporty, pravidla a limity,
auditní log, PWA. Z existujícího kódu se přebírá hlavně generování kreativ a obsah znalostní databáze.

---

## 4. Technická architektura (doporučení)

### Stack
| Vrstva | Volba | Proč |
|---|---|---|
| Aplikace | **Next.js (App Router) + TypeScript + React**, jeden repozitář | Jeden kód pro UI i serverové API; tvoje preference; snadné PWA. |
| UI | Tailwind + shadcn/ui, grafy Recharts | Rychlé, přehledné, dotykové ovládání. |
| Databáze | **PostgreSQL** + Drizzle ORM | Relační data (značky, kampaně, metriky po dnech), migrace v gitu. |
| Úlohy na pozadí | **pg-boss** (fronta v Postgresu) – samostatný worker proces | Synchronizace statistik, publikování v naplánovaný čas, reporty, upozornění. Bez Redisu = levnější provoz. |
| Soubory | Cloudflare R2 (S3 kompatibilní) | Knihovna obrázků a videí; levné úložiště bez poplatků za stahování. |
| Přihlášení | Better Auth: heslo + **povinné 2FA (TOTP)**, volitelně passkey | Bezpečné, bez externí placené služby. |
| AI | **Anthropic API** přes vlastní modul `ai/` (vyměnitelný poskytovatel) | Asistent s nástroji (tool use); Gemini zůstává pro obrázky. |
| Hosting | 1 malý server (VPS, např. Hetzner) s Dockerem: app + worker + Postgres + denní šifrované zálohy mimo server | Nejnižší náklady, vše na jednom místě. Alternativa bez správy serveru: Railway / Render (dražší, ale jednodušší). |

### Moduly (každý samostatný, rozšiřitelný)
```
core/          značky, uživatelé, role, auditní log, šifrování tajných údajů
connectors/
  meta/        Marketing API + Graph API (kampaně, sestavy, reklamy, kreativy, statistiky, příspěvky, leady)
  google-ads/  stejné rozhraní – v 1. verzi jen připravené
ai/            asistent, nástroje, prompty, profil + znalosti značky, kontrola faktů
creative/      Gemini obrázky, HTML šablony, video (později)
content/       příspěvky, kalendář, schvalování, plánovač
analytics/     denní metriky, výpočty CPL/CTR/CPC/CPM/ROAS, reporty
automation/    pravidla, limity, upozornění, návrhy změn
```
Platformy (Meta, Google) se připojují přes společné rozhraní `AdPlatform` (načti kampaně, načti metriky,
vytvoř návrh, proveď schválenou změnu). Google Ads se pak přidá bez zásahu do zbytku.

### Datový model (hlavní tabulky)
- `brands` – značka, profil (tón, zakázané formulace, barvy, logo), limity útraty
- `users`, `brand_members` (role: vlastník / editor / jen čtení) – oddělení značek na úrovni dotazů
- `platform_connections` – připojení Meta/Google, **šifrovaný token** (AES-256-GCM, klíč mimo databázi)
- `ad_accounts`, `pages`, `ig_accounts` – přiřazení aktiv ke značce
- `campaigns`, `ad_sets`, `ads`, `creatives` – zrcadlo stavu z Mety (synchronizace)
- `insights_daily` – metriky po dnech na úrovni reklamy (zdroj pravdy pro všechny výpočty)
- `leads` – leady z formulářů Meta (osobní údaje, přístup jen vlastník; vazba na CRM)
- `media_assets` – knihovna (vlastní fotky, AI obrázky – vždy označené)
- `knowledge_facts` – ověřené údaje se zdrojem a platností
- `content_items` – příspěvky / reklamní texty / články, stav (návrh → ke schválení → schváleno → publikováno)
- `calendar_events` – plán příspěvků a kampaní
- `change_requests` – **každý zápis do Mety** (typ, data, dopad na útratu, kdo schválil, výsledek)
- `automation_rules` – pravidla a limity (zpočátku vše vypnuté)
- `audit_log` – nezměnitelná historie všech akcí (kdo, co, kdy, odkud)
- `ai_messages` – historie asistenta vč. použitých dat

### Ochrana před nechtěným utrácením (jádro návrhu)
1. AI **nikdy nevolá zápisové API přímo.** Umí jen číst data a vytvářet *návrhy* (`change_requests`).
2. Provedení návrhu = tlačítko „Schválit“ ve rozhraní + **opětovné potvrzení 2FA** u všeho, co zvyšuje útratu
   (spuštění kampaně, zvýšení rozpočtu, nová reklama).
3. Nové kampaně se v Metě zakládají ve stavu **PAUSED**; aktivace je samostatný schvalovaný krok.
4. **Pevné limity na značku** (max. denní rozpočet kampaně, max. měsíční útrata) – server odmítne i schválenou
   změnu nad limit. Jako druhá pojistka limit útraty účtu přímo v Metě (`spend_cap`).
5. Pozastavení (snižuje útratu) jde jedním klikem; v nouzi „Zastavit vše“ pro značku.
6. Automatické úpravy (fáze 5) jen v mezích pravidel, která jsi schválil, a vždy se záznamem v auditu.

### AI asistent – jak zabráníme vymýšlení čísel
- Asistent odpovídá nad **nástroji** (`nacti_metriky`, `seznam_kampani`, `porovnej_reklamy`, `navrhni_kampan`…),
  ne z hlavy. Čísla v odpovědi pocházejí jen z výsledků nástrojů; server je zobrazuje s datem stažení.
- Každý údaj má štítek: **Skutečná data Meta** · **Odhad Mety** (např. odhadovaný dosah) · **Doporučení AI**.
- Konverze/poptávky = jen to, co Meta vrací jako výsledky (leady z formulářů, pixel/CAPI události).
  Když data chybí, asistent řekne „nemám data“, nedopočítá je.
- Texty reklam se kontrolují proti znalostní databázi: technický údaj bez zdroje = varování před schválením.
- Model: Claude Opus 5.5 pro asistenta a návrhy kampaní; levnější Claude Haiku 5.5 pro rutinu
  (třídění, krátké souhrny). Hlas: ve webu Web Speech API (kde prohlížeč podporuje češtinu), v iOS aplikaci
  rozpoznávání Apple (vzor ClaudeVoiceCZ).

### Uživatelské rozhraní
Horní lišta: **přepínač značky** (REO Heating / Super Heating CZ). Menu (na mobilu spodní lišta):
**Přehled · Asistent · Kampaně · Obsah a kalendář · Knihovna · Reporty · Nastavení.**
- *Přehled:* útrata dnes / tento měsíc (vs. limit), poptávky, cena za poptávku, graf 30 dní, aktivní kampaně,
  naplánované příspěvky, upozornění (zamítnutá reklama, problém s platbou, kampaň bez výsledků), doporučení AI.
- *Kampaně:* tabulka s jednoduchými názvy sloupců, detail kampaně, tlačítko Pozastavit, „Navrhnout změnu“.
- *Schvalování:* jedna fronta „Čeká na tvé schválení“ – návrhy kampaní, změny rozpočtů, příspěvky.

### Mobil
1. Responzivní web + **PWA** (instalace na plochu iPhonu i Androidu, upozornění push – na iPhonu od iOS 16.4
   jen u nainstalované PWA).
2. Později **Capacitor** obal stejného kódu → aplikace pro iOS/Android (nativní hlas, spolehlivější notifikace).

---

## 5. Provozní náklady (měsíčně, orientačně)

| Položka | Odhad | Pozn. |
|---|---|---|
| Server (VPS) vč. databáze | ~150–400 Kč | [PŘEDPOKLAD] podle velikosti; alternativa Railway/Render ~500–1 000 Kč |
| Úložiště médií (R2) | 0–50 Kč | do 10 GB zdarma [PŘEDPOKLAD – ověřit aktuální ceník] |
| Zálohy mimo server | ~50 Kč | |
| Doména / subdoména | 0 Kč | např. `marketing.reoheating.cz` |
| Anthropic API (asistent, návrhy, reporty) | ~500–1 500 Kč | Ceník [OVĚŘENO 10/2026]: Opus 5.5 $4/$20, Sonnet 5.5 $2/$10, Haiku 5.5 $0,10/$0,50 za 1 M tokenů vstup/výstup. Odhad pro ~500 dotazů asistenta + týdenní reporty s cachováním; s Sonnet 5.5 zhruba poloviční. Nastavíme měsíční limit v Anthropic Console. |
| Gemini (obrázky) | ~100–500 Kč | podle počtu generovaných obrázků; billing již aktivní |
| Meta Marketing / Graph API | 0 Kč | |
| Google Ads API | 0 Kč | |
| **Celkem bez reklamního rozpočtu** | **≈ 1 000–2 500 Kč** | reklamní rozpočet se platí Metě zvlášť jako dosud |

Vývoj dělám já v Claude Code – žádné externí licence ani předplatné nejsou nutné.

---

## 6. Co potřebujeme od Mety

### Stav pravidel [OVĚŘENO z dokumentace a changelogu Meta, 10/2026 – při zakládání zkontrolovat v App Dashboardu]
- Meta v květnu 2026 přejmenovala úrovně přístupu: dřívější „Standard Access“ je nyní **Limited Access**,
  „Advanced Access“ je **Full Access**; funkce „Ads Management Standard Access“ se jmenuje **Marketing API Access Tier**.
- **Limited Access (výchozí) stačí pro správu vlastních reklamních účtů a aktiv** (jsi admin). Full Access
  (App Review) je potřeba pro správu cizích účtů – to nepotřebujeme. Limited má nižší limity volání; pro 2 značky
  to podle mě stačí [PŘEDPOKLAD]. Automatický postup na vyšší tier po 500 voláních za 15 dní.
- Aktuální verze API: v25 (2/2026), v26 ohlášená na letošek. Od v25 už nelze přes API zakládat staré
  „Advantage+ shopping/app“ kampaně – používá se nová jednotná struktura kampaní. Ve v26 se ruší některé metriky
  dosahu stránek a příspěvků (page reach, story impressions) – v dashboardu je nebudeme stavět.
- Instagram: publikování přes Content Publishing API (dvoukrokově: kontejner → publikace), denní limit příspěvků
  na účet (dotazuje se přes `content_publishing_limit`). **Instagram nemá nativní plánování** – naplánované
  příspěvky publikuje náš plánovač. Facebook stránka plánování podporuje nativně (`scheduled_publish_time`).

### Postup propojení (bezpečný, bez přihlašování hesly v aplikaci)
1. Ověřit, že **reklamní účty, stránky, IG, pixel/dataset a leadové formuláře vlastní tvoje Business portfolio,
   ne agentura** (agentura má mít jen partnerský přístup). Toto je klíčové pro odchod od agentury. [CHYBÍ PŘÍSTUP]
2. Dvoufázové ověření pro všechny adminy Business portfolia.
3. Vytvořit **Meta App typu Business** ve tvém portfoliu (developers.facebook.com).
4. Vytvořit **systémového uživatele** (admin) v Business Settings, přiřadit mu reklamní účty, stránky a IG obou značek,
   vygenerovat token s potřebnými oprávněními. Token zadáš jednou do aplikace (server ho zašifruje, prohlížeč ho
   nikdy neuvidí).
5. **Business Verification** (ověření firmy dokladem) – u vlastních aktiv nemusí být hned nutná, ale některá
   oprávnění / vyšší limity ji vyžadují; doporučuji ji spustit hned, trvá dny. [CHYBÍ PŘÍSTUP]

### Oprávnění (scopes)
| Oprávnění | K čemu | Fáze |
|---|---|---|
| `ads_read` | čtení kampaní a statistik | 3 |
| `ads_management` | zakládání/úpravy/pozastavení kampaní, sestav, reklam, nahrání kreativ | 3 (pauza) / 4 |
| `business_management` | čtení aktiv portfolia, přiřazení | 3 |
| `pages_show_list`, `pages_read_engagement` | seznam stránek, příspěvky, reakce | 3 |
| `read_insights` | statistiky stránek | 3 |
| `leads_retrieval` + `pages_manage_metadata` | stažení leadů z formulářů, webhook nových leadů | 3–4 |
| `pages_manage_posts` | publikování a plánování příspěvků na FB | 4 |
| `pages_manage_ads` | reklamy z příspěvků stránky, leadové formuláře | 4 |
| `instagram_basic`, `instagram_content_publish`, `instagram_manage_insights` | IG účet, publikace, statistiky | 4 |
| `instagram_manage_comments`, `pages_manage_engagement` | moderování komentářů | později (volitelně) |

### Co API **neumí** nebo kde jsou limity (neslibuji)
- Některé novinky Ads Manageru přicházejí do API se zpožděním nebo vůbec; některé typy kampaní nelze přes API zakládat.
- Schvalování reklam provádí Meta – reklama může být zamítnuta i po našem schválení.
- Statistiky mají zpoždění (hodiny), atribuční okna dle nastavení Mety; historie insights je omezená
  (cca 37 měsíců) [PŘEDPOKLAD – ověřit].
- Meta Business Suite „Inbox“ (zprávy) – jiná oprávnění, mimo rozsah.
- Placení faktur a změny platební metody – jen v Metě, ne přes API.

---

## 7. První funkční verze (fáze 3) – návrh rozsahu

**Cíl:** každý den otevřeš aplikaci místo Ads Manageru a vidíš skutečná čísla obou značek; asistent je umí vysvětlit.

1. Přihlášení (heslo + 2FA), role vlastník.
2. Správa značek: REO Heating, Super Heating CZ (profil, barvy, logo, limity, přiřazení FB/IG/účtů).
3. Propojení Meta (token systémového uživatele, šifrovaně), test připojení.
4. Synchronizace: všechny kampaně/sestavy/reklamy + denní metriky zpětně (např. 24 měsíců), pak každou hodinu.
5. Dashboard: útrata dnes/měsíc, poptávky, cena za poptávku, CTR, CPC, CPM, trend 30 dní, aktivní kampaně, upozornění.
6. Přehled kampaní s detailem a srovnáním období.
7. AI asistent (text, čeština; hlas kde prohlížeč umí): otázky nad daty, srovnání reklam, **návrh** kampaně (bez publikace).
8. Jediná zápisová akce: **Pozastavit kampaň** (snižuje útratu) – s potvrzením a záznamem v auditu.
9. Auditní log, denní zálohy, PWA instalace.

**Mimo 1. verzi:** zakládání kampaní v Metě, publikování příspěvků, kalendář, generování grafiky v aplikaci,
automatizace, Google Ads, nativní iOS.

---

## 8. Harmonogram (orientační)

| Fáze | Obsah | Délka | Závislost |
|---|---|---|---|
| 0 – Přípravy (ty) | vlastnictví aktiv, 2FA, Meta App, systémový uživatel, Business Verification, API klíč Anthropic, server | 1–2 týdny (souběžně) | **blokuje napojení na Metu** |
| 2 – Schválení | odsouhlasení tohoto návrhu | – | tvé rozhodnutí |
| 3 – První verze | viz bod 7 | 2–3 týdny | fáze 0 |
| 4 – Tvorba a publikování | AI návrhy kampaní → schválení → založení v Metě (PAUSED) → aktivace; reklamní texty, A/B varianty, kreativy (Gemini + šablony), knihovna médií, kalendář, publikace FB/IG | 3–4 týdny | |
| 5 – Automatizace | týdenní/měsíční reporty, upozornění, doporučení rozpočtů, pravidla s limity (vypnutá do schválení) | 2 týdny | ≥ 4 týdny dat |
| 6 – Rozšíření | Capacitor iOS/Android, Google Ads (developer token požádat včas – schvaluje Google), video | 3–6 týdnů | |

Celkem cca **2,5–3,5 měsíce** do stavu, kdy zvládneš běžnou správu bez agentury.
Doporučuji **1–2 měsíce souběhu s agenturou** (aplikace čte a porovnává, agentura ještě spravuje) a teprve
potom převzít kampaně.

**Google Ads:** v 1. verzi jen připravené rozhraní. Žádost o developer token Google Ads API ale podat hned
(nic to nezdrží a schválení trvá). Účet Riva Trade s živou kampaní ThermaVera už existuje.

---

## 9. Rozhodnutí uživatele (31. 10. 2026) – návrh SCHVÁLEN („začni“)
- **Značky:** REO Heating, Super Heating CZ, ThermaVera, Eko4home. Vlastník všech: **Riva Trade, s.r.o.**;
  Meta/Google účty pod soukromým účtem jindrich.szkandera@gmail.com.
- Cíl: nahradit agenturu, kampaně spravovat sám přes aplikaci. Později možná další uživatelé → role připravit.
- **Rozpočet na reklamu: 20 000 Kč/měsíc pro ThermaVeru a REO Heating dohromady, zatím na zkoušku**
  → v aplikaci společný měsíční limit pro tyto dvě značky.
- **Hosting:** levný vlastní server.
- Původní „systém na marketingová témata“ se lokálně nenašel (Dokumenty, Stahování, Projekty, historie Claude Code).
  Ve Stahování je jen agenturní „Obsahová strategie – Eko4Home.pdf“ (2023). Pokud se najde v chatu na claude.ai,
  převezmeme prompty do AI vrstvy.

## 10. Původní otevřené otázky
1. Kde je uložený původní systém na marketingová témata a kampaně (claude.ai projekt / Drive / jinde)?
2. Super Heating CZ: web/e-shop, logo, FB stránka a IG účet, je to stejná firma (Riva Trade) a stejné Business portfolio jako REO?
3. Kdo vlastní reklamní účty – ty, nebo agentura? Kolik reklamních účtů je (jeden společný / každá značka svůj)?
4. Měsíční rozpočty na reklamu obou značek (kvůli limitům v aplikaci).
5. Bude aplikaci používat ještě někdo další (kolega, agentura jen pro čtení)?
6. Hosting: levný vlastní server (správu obstarám já), nebo dražší spravovaná služba?
7. ThermaVera – patří do aplikace také jako třetí značka?
