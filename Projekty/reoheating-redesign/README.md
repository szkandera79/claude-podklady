# reoheating-redesign — návrh nového webu REO HEATING

Refresh webu reoheating.cz (13. 11. 2026). Jednostránkový návrh, statické HTML (`index.html`, interní CSS + vanilla JS).
Artefakt: https://claude.ai/artifact/PdPNnYNXA75YnWvP8Vox5T (soukromý; aktualizovat publikací stejného souboru, `files` = `assets/img/*`).

## Grafika
- Podle FB/IG bannerů ThermaVera (příloha zadání 13. 11.): světlý hero — text vlevo, fotka vpravo za zeleným obloukem
  se žlutou linkou, antracitový pruh s ikonami (Rodinné domy / Bytové domy a SVJ / Firmy a průmysl / Mobilní kotelny),
  žlutá CTA s tmavým textem, zelené zvýraznění slov v nadpisech, tmavá sekce jako banner „Máte bytový dům…“,
  zelený pruh „Kolik vás stojí staré topení?“ s formulářem.
- Barvy (`:root`): zelená `#3E9B3A` / `#2F7F2D` / tmavá `#1F5A23`, tint `#EEF6EC`, žlutá `#F2C230`, antracit `#24272A`.
  Ladí s logem (zelená `#50854D`, žlutá `#F0C246`, písmo `#363533`).
- Písmo Poppins (nadpisy) + Inter (text). Logo = závazné z `~/Claude/REO/logo/`.
- Jen světlý vzhled (záměrně bez tmavého režimu).

## Sekce
hero střídá 2 verze (13. 11. rev.): **domácí** (schéma RH060 + Watertank 210/70 = hero z eko4home.cz, `hero-dum.webp`) a **průmyslová** (zelená kontejnerová kotelna na biomasu z galerie thermavera.cz `reference/lodni-1.jpg` → `hero-biomasa.jpg`, štítek „Realizace partnera“); mění se i nadpis a popisek → `#reseni` 4 segmenty →
`#zelene-kotelny` (5 kroků) → `#produkty` záložky RH030–RH060 / Smart / RHX Pro / RH X50 → `#mobilni-kotelny` →
`#realizace` (filtr) → `#vypocet` formulář → `#proc` → patička.

## Fotky (`assets/img`, zmenšené kopie)
- `hero-prumysl/bd/mobilni` (už jen v sekcích), `mob-*` = **AI vizualizace** z `mobilni-kotelny-web/assets/img` → vždy štítek „Vizualizace“.
- `hero-rd`, `rd-*` = realizace REO HEATING (z `REO/reoheating-web/assets/images/realizace`).
- `ref-*` = `Reference zelena kotelna/` (Bytové jednotky mobilní vytápění, La Coruna) — **realizace partnera Smart Heating
  Technology**, kontejnerové kotelny (zdroj tepla na fotkách není TČ REO). Popisky „realizace partnera“.
- Produkty `p-*.webp` z `eko4home-web/assets/img`.

## Data
Parametry a ceny převzaty z `eko4home-web/index.html` (zadání 20. 10. 2026): RH řada 95–169k, Smart 129–189k,
RHX20/30 Pro 300/350k, RH X50 430k (ověřit), hluk = akustický tlak ve 3 m z L_WA (TÜV SÜD).

## Otevřené body
- Souhlas Smart Heating Technology s fotkami na webu REO (zatím jen ústní, pro ThermaVeru) + zda je ukazovat, když nejde o TČ.
- Chybí vlastní fotky komerčních / průmyslových realizací TČ REO a reálné mobilní kotelny → nahradit vizualizace.
- Mobilní kotelny: ceník (ThermaVera 49k/79k měs. + doprava 30k + montáž 50k) na webu REO zatím neuveden — rozhodnout.
- „Prodloužená záruka u vybraných řad“, „náhradní díly skladem“, „dálkový dohled“ — potvrdit formulace.
- Formulář je maketa (bez odesílání) — pro ostrý web převzít `odeslat.php` + `antispam-lib.php` z `eko4home-web/`.
- Vztah k `REO/reoheating-web/` (stávající návrh) a `eko4home-web/` — který web nahrazuje.

## Náhled
Konfigurace „reo-redesign“ v `.claude/launch.json` (port 8012) servíruje kopii ve scratchpadu; jinak publikovaný artefakt.
