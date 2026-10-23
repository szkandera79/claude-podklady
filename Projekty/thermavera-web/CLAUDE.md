# CLAUDE.md — ThermaVera Energy (web)

> Tato složka je podprojekt repozitáře **Projekty** (`~/Claude/Projekty/thermavera-web`).
> Pravidla níže platí pro web thermavera.cz; přehled všech projektů je v `../CLAUDE.md`.

Tento soubor dává Claude Code kontext k projektu. Drž se ho při všech úpravách.

## O projektu
Jednostránkový marketingový web (landing page) pro firmu **ThermaVera Energy** —
„zelené kotelny na klíč". Cílem webu je generovat **poptávky na technicko‑ekonomické
posouzení** a výpočet návratnosti pro firmy, obce, bytové domy/SVJ, průmysl,
developery a komerční objekty.

- **Claim:** „Zelené kotelny na klíč, které dávají ekonomický smysl."
- **Doplňkový claim:** „Teplo levněji, čistěji a nezávisleji."
- **Doména (cílová):** thermavera.cz
- **Jazyk webu:** čeština (vše, včetně nových textů).

## Tech stack a konvence
- **Jeden soubor `index.html`** s interním CSS (`<style>`) a minimem vanilla JS.
  Žádný React, žádné externí frameworky. Pokud má uživatel zájem rozdělit CSS/JS
  do samostatných souborů, udělej to až na vyžádání.
- Styly přes **CSS proměnné** v `:root` (viz níže). Barvu/akcent se mění jednou proměnnou.
- Vanilla JS jen pro: mobilní menu, FAQ accordion, smooth scroll, reveal‑on‑scroll,
  demo odeslání formuláře, **přepínač jazyků (i18n)**. Nepřidávej knihovny bez domluvy.
- Fonty přes Google Fonts: **Poppins** (nadpisy) + **Inter** (text).
- Plně responzivní (mobil/tablet/desktop), sticky header, `prefers-reduced-motion`.
- **Nepoužívej fotky z fotobank ani cizí obrázky** (autorská práva). Na místa fotek
  jsou připravené placeholdery `.ph` s popiskem — viz „Placeholdery".

## Vícejazyčnost (i18n) — DŮLEŽITÉ, drž při všech úpravách textů
Web je čtyřjazyčný: **CS (výchozí) / EN / DE / PL**. Architektura = **jedna stránka
+ přepínač jazyků** (rozbalovací `#langsel` v hlavičce). Řešení je čistý vanilla JS
ve **druhém `<script>` bloku na konci `index.html`**:
- Čeština je „zdroj pravdy" — je napevno v HTML. Engine prochází textové uzly a překládá
  je podle **českého originálu** přes slovník `TR` (klíč = český text po `trim()`,
  hodnota = `[EN, DE, PL]`). Překládá i atributy `alt`, `placeholder`, `aria-label`
  a dále `<title>`, meta `description`, `og:title`, `og:description` (objekt `META`)
  a nastavuje `<html lang>`. Volba se ukládá do `localStorage` (`tv_lang`).

**PRAVIDLO (automaticky dodržuj): Když přidáš nebo změníš jakýkoli český text**
(nadpis, odstavec, položku, tlačítko, `alt`, `placeholder`, popisek v galerii, FAQ,
meta tag…), **vždy ve stejném kroku přidej/uprav i překlad** do `TR` (resp. `META`)
pro EN, DE a PL. Klíč musí přesně odpovídat českému originálu (včetně interpunkce,
typografických uvozovek „ ", pomlček – —, `e‑mail` s pevnou pomlčkou apod.).
Nepřeložený text zůstane česky (graceful fallback) — ber to jako chybu k doplnění.
- Texty s vnitřním HTML (`<span>`, `<strong>`) jsou rozdělené na více textových uzlů
  → překládej **každý fragment zvlášť** (vlastní klíč pro každou část).
- Po úpravě otestuj přepnutí EN/DE/PL v náhledu (texty, `alt`, meta, `<html lang>`).
- Tón a právní mantinely (viz níže) platí ve **všech jazycích** — žádné garance úspor.

## Aktuální design
Aktivní `index.html` je ve **světlém, vzdušném stylu** (inspirováno designovým
jazykem reoheating.cz): bílá základna, centrované sekce ve formátu „eyebrow + velký
titulek", feature karty s ikonou v kolečku, produktové karty s obrázkovým pruhem a
odkazem „Více informací →", měkké zaoblené stíny, tlačítka v sentence‑case.

Alternativní koncepty (needituj, dokud o to uživatel nepožádá) jsou v `reference/`:
- `reference/thermavera-dark.html` — tmavá technická varianta (deep green hero).
- `reference/vireo.html` — starší koncept značky VIREO.

## Barevná paleta (CSS proměnné v `:root`)
    --green:#0F3D2E         /* hluboká zelená, tmavé prvky, footer */
    --green-bright:#1E8F5B  /* akcent: eyebrow, ikony, odkazy */
    --green-tint:#E7F3EC    /* světlé pozadí ikon/odznaků */
    --amber:#F2A33A         /* CTA tlačítka */
    --amber-deep:#DA8718    /* CTA hover */
    --ink:#16201C           /* hlavní text */
    --muted:#5F6B64         /* tlumený text */
    --bg:#FFFFFF / --bg-alt:#F4F8F5 / --line:#E5ECE7
Změna firemního akcentu = úprava `--green-bright` (a případně `--amber`).

## Struktura sekcí (kotvy / id)
header → `#top` hero → `#proc` (Proč) → `#reseni` (Co dodáváme) → Naše řešení →
`#kombinace` (diagram zdrojů) → `#ekonomika` (filozofie + 7 let) → `#ets2` →
`#technologie` (Kompletní služby) → `#financovani` (Modely spolupráce) →
`#prokoho` → FAQ → CTA pruh → `#kontakt` (formulář + kontakt) → footer.

## Obsahové a právní mantinely (DŮLEŽITÉ — dodržuj při psaní textů)
- **Návratnost:** vždy formulovat „u vhodných projektů obvykle do 7 let".
  Nikdy negarantuj návratnost ani konkrétní % úspory.
- **ETS2:** používej opatrné formulace — „ETS2 *může* zvýšit náklady",
  „*podle aktuálně uváděných informací* spuštění od roku 2028 (původně uváděn 2027)",
  povolenky nakupují **dodavatelé paliv**, ne přímo domácnosti; náklady se *mohou*
  promítnout do cen. Nepoužívej „určitě dramaticky zdraží", „garantujeme ochranu",
  „domácnosti budou nakupovat povolenky".
- **Tón:** seriózní B2B energetik (ekonomika, stabilita, nezávislost), NE eko‑aktivismus
  ani kýč. Žádný motiv listů jako hlavní vizuál. Vyhýbej se prázdným superlativům
  („revoluční", „unikátní") bez podložení.
- **Žádné fiktivní reference.** Pokud bude sekce referencí, nazvi ji „Modelové scénáře"
  nebo ji vynech, dokud uživatel nedodá reálné údaje.

## Placeholdery k nahrazení reálnými údaji
- **Fotky:** bloky `<div class="ph">…</div>` (hero, „Co dodáváme", „Naše řešení",
  filozofie). Nahradit `<img src="assets/images/…" alt="…">`. Fotky ukládej do
  `assets/images/`.
- **Kontakt:** `info@thermavera.cz`, `+420 000 000 000`, sídlo/adresa — doplnit dle skutečnosti.
- **Formulář** je demo (`preventDefault` → děkovná hláška). Pro ostrý provoz napojit
  na e‑mail/CRM (backend, např. Formspree, vlastní endpoint, nebo serverless funkce).

## Jak si web prohlédnout (preview)
Stačí otevřít `index.html` v prohlížeči. Pro „živý" reload doporuč lokální server:
    python3 -m http.server 8000      # pak http://localhost:8000
nebo `npx serve`.

## SEO (zachovat)
Meta title: „Zelené kotelny na klíč | Chytrá a hospodárná energetika | ThermaVera Energy".
Meta description a klíčová slova jsou v `<head>` — při změnách textů je drž konzistentní.

## Nasazení (web4u, doména thermavera.cz/.com)
- Hosting: **web4u**, tarif Optimal, PHP 8.5. Web běží ve složce `/html`.
- **Nahrává se obsah složky `thermavera-web/dist/`, ne celá složka webu.** `dist/` je „plochý" build:
  `index.html` má cesty k obrázkům jen jako název souboru (bez `assets/images/`),
  všechny `.jpg` leží vedle `index.html` a je tam i `odeslat.php`. Důvod: webový
  klient net2ftp při rozbalení ZIPu zploští strukturu složek.
- Build dist (ze složky webu — `cd thermavera-web`):
    rm -rf dist && mkdir dist
    sed -e 's#assets/images/reference/##g' -e 's#assets/images/##g' index.html > dist/index.html
    cp odeslat.php favicon.svg ochrana-udaju.html robots.txt sitemap.xml kalkulacka.html kurz.php dist/
    cp google*.html dist/   # ověřovací soubor Google Search Console
    cp assets/images/*.jpg dist/ ; cp assets/images/reference/*.jpg dist/
    cp -R mobilni-kotelny dist/   # služba Mobilní kotelny — podsložka se strukturou, nahrát jako složku přes FTP
- Měna v kalkulačce: `kurz.php` (server-side stáhne denní střed ČNB CZK/EUR, cache 6 h, JSON).
  Kalkulačka má přepínač Kč/€ (`setCurrency`), autodetekce dle jazyka prohlížeče (cs/sk→Kč, jinak €).
  Výstupy jdou přes `fmtM()` (dělí `FX`) + symbol `SYM`; převedeny jsou render funkce (ř. ~1257–1526)
  i `getExportData()` (Excel/PDF respektují zvolenou měnu — v `getExportData` převádějí peněžní vstupy
  helpery `m0`/`m1`, popisky používají `${SYM}` v template literálech; pozor: NESMÍ být v ' ' uvozovkách,
  jinak se neinterpoluje). VSTUPY v UI zůstávají v Kč (badge ukazuje kurz); v exportu se přepočítají dle měny.
  PDF report je obraz renderovaného HTML (html2canvas) → měna se propíše automaticky.
- Soubory navíc v rootu (mimo index.html): `odeslat.php` (formulář), `favicon.svg`,
  `ochrana-udaju.html` (GDPR), `robots.txt`, `sitemap.xml`. Pozn.: `og:image` a
  structured data (JSON-LD) v `<head>` používají absolutní URL https://thermavera.cz/...
- Kalkulačka úspor (na homepage): teaser sekce `#kalkulacka`, JS počítá orientační rozpětí
  úspory z ročních nákladů (řádek `#calc-out` je z i18n překladu vyloučen). Její CTA i hlavní
  tlačítka „Spočítat návratnost" vedou na **`kalkulacka.html`**.
- `kalkulacka.html` = plná energetická kalkulačka (samostatná stránka, jen česky). Vznikla
  z `energeticka-kalkulacka-v22_11.html` (Downloads) přeznačením z REO HEATING → ThermaVera:
  text/odkazy (reoheating.cz→thermavera.cz), claim, barvy přes CSS proměnné na paletu ThermaVera,
  logo „7". Je soběstačná (base64 obrázky + CDN knihovny pro export PDF/Excel/Word) — při
  buildu se jen zkopíruje, neflattenuje. Zdroj v Downloads je REO HEATING; rebranding je v repu.
  - ETS2: přepínač `#ets2Row` / `#ets2Toggle` (od 2028) orientačně navýší cenu fosilních paliv
    v `currentCost` (plyn ×1,25, tuhá paliva ×1,35, CZT ×1,20). Původní absolutní EUA model
    (`#euaPrice`, emisní faktory) je vypnutý (default 0, UI skryté), aby se výpočet nezdvojoval.
  - Výchozí spotřeba 330 MWh; pole `#heatLoss` (tepelná ztráta, volitelné — jinak odhad ze
    spotřeby přes ~2100 h plného výkonu). Z tepelné ztráty se v calc() odhadne investice do TČ
    a auto-předvyplní do `#hpInvest`/`#bioInvest` (ruční zápis = `dataset.auto='0'` → odhad se
    pro to pole vypne; proto tato pole NEMAJÍ inline `oninput`, listener je na konci skriptu).
    TČ kalibrace dle SVJ Baranova: kotelna+akumulace fixně 1 650 000 Kč + jednotky
    (100 kW = 750 000 Kč / 60 kW při −15 °C; 50 kW = 410 000 Kč / 30 kW). Nominál TČ ≈ 2,14× ztráta
    (140 kW→3×100 = 3,9 mil.; 70 kW→1×100+1×50). Vše bez DPH. Biomasa zatím orientačně (1,8× × 10 000 Kč/kW).
  - **Rodinné domy:** když je stávající zdroj `electric` (elektrokotel) NEBO tepelná potřeba `heatNeedMWh ≤ 40`
    (≈ plyn do 40 MWh / ekvivalent), `hpInvestEst` se přepíše na **fixních 250 000 Kč** (malé TČ, realizace
    245–265 tis.). Tato cena je **finální vč. 12 % DPH** (rezidenční sazba) — viz `isResidential` v calc().
    Biomasa pro RD je zatím **0 Kč** na předvyplněném vstupu (`bioInvestEst = isResidential ? 0 : …`) —
    čeká na reálné ceny kotlů; B2B biomasa dál na vzorci.
  - **DPH v kalkulačce:** přepínač `setVat` (bez DPH výchozí / s DPH 21 %) přes `let VAT`. Dva formátovače:
    `fmtM` (= `kc*VAT/FX`) pro **provozní náklady/úspory/ceny energií** (přepínač je mění), a `fmtP` (= `kc/FX`,
    BEZ VAT) pro **investice/dotace** (finální ceny — přepínač je NEmění; tím sedí rezidenčních 250k vč. 12 %
    i B2B Baranova bez DPH). V `getExportData` proto `m0`=investice/dotace→`fmtP`, `m1`=ceny energií→`fmtM`.
    Návratnost se počítá z raw hodnot (přepínač ji nemění). Excel list „Info" uvádí měnu + režim DPH.
- Repozitář si drží hezkou strukturu `assets/images/` jako zdroj pravdy.

## Mobilní kotelny (`mobilni-kotelny/`, od 23. 10. 2026)
- Podsložka **se generuje**, ručně ji neupravuj: zdroj je `../mobilni-kotelny-web/` (texty, kalkulačka, obrázky),
  po změně spusť z kořene repa `python3 mobilni-kotelny-web/integrace-thermavera/build_integrace.py --apply`
  (podsložku přegeneruje; úpravy homepage a sitemap provede jen poprvé).
- Na homepage: položka menu „Mobilní kotelny“, tlačítko v hero, odkaz v kartě Mobilní kotelna a v patičce (vše s TR překlady),
  v hero 6 AI vizualizací (`data-viz`) se štítkem „Vizualizace“ — nejsou to realizace, štítek nesmí zmizet.
- Poptávka ze služby jde přes `odeslat.php` (pole `model` = „Pronájem mobilní kotelny – …“). Podstránky jen česky.

## Kontaktní formulář (ostrý)
- Formulář v `#kontakt` odesílá přes `fetch` POST na **`odeslat.php`** (PHP `mail()`),
  poptávky chodí na **info@thermavera.cz**. Honeypot pole `website` proti spamu.
- Úspěch → zobrazí `#okmsg` (poděkování), chyba → `#errmsg`. Oba texty jsou v i18n slovníku.

## Možné další kroky (TODO)
- (Volitelně) hero slider se dvěma slidy: tepelná čerpadla / mobilní kotelna.
- (Volitelně) interaktivní kalkulačka orientační návratnosti.
- HTTPS: aktivovat Let's Encrypt v klientské sekci web4u + zapnout přesměrování na HTTPS.

## Konvence pro práci
- Texty piš česky, tlačítka v sentence‑case („Spočítat návratnost", „Více informací").
- Sekce drž ve formátu eyebrow (`.eyebrow`) + `<h2>`.
- Po větší změně zkontroluj responzivitu (breakpointy 980 / 820 / 620 px) a accessibility
  (kontrast, alt texty, aria u interaktivních prvků).
