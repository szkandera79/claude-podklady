# Architektura — Reo Heating IOT CZ

Stav: **návrh** (2026-10-13). IOT: `http://162.62.225.58/` (přihlášení `/#/login`;
směrování přes `#/` naznačuje jednostránkovou aplikaci — ověří se podle snímků). Konkrétní napojení na stránky IOT se doplní až podle
anonymizovaných snímků obrazovky — strukturu IOT ani jeho API nevymýšlíme.

## 1. Základní princip
Rozšíření Chrome (Manifest V3) je **vrstva nad stránkou**: čte jen to, co je na
obrazovce, přidává překlad a informační prvky, ale nic neodesílá a nic nemění v datech
ani formulářích IOT. Veškerá odborná data jsou **uvnitř rozšíření** (offline JSON),
žádné volání externích služeb ve verzích 1–4.

```
 ┌──────────────── stránka IOT (Chrome) ────────────────┐
 │  původní rozhraní (EN)                               │
 │   + content script: překlad textů, ikony ⓘ, tooltipy │──┐ zprávy (chrome.runtime)
 └──────────────────────────────────────────────────────┘  │
 ┌──────── postranní panel (side panel) ────────┐          │
 │ Encyklopedie · Chyby · Diagnostika · Zdroje  │◄─────────┘
 └──────────────────────────────────────────────┘
        ▲ čte jen lokální data rozšíření
 ┌──────┴───────────── data/ (JSON, generované) ────────┐
 │ slovnik · parametry · chyby · index dokumentace     │
 └──────────────────────────────────────────────────────┘
        ▲ build skript (Python) na Macu
 ┌──────┴───────────── zdroje ──────────────────────────┐
 │ data-src/ (CSV/YAML, v gitu)  podklady/ (PDF, mimo git)│
 └──────────────────────────────────────────────────────┘
```

## 2. Moduly
| Modul | Složka | Úkol | Etapa |
|---|---|---|---|
| Lokalizace | `extension/src/i18n/` | překlad textových uzlů stránky podle slovníku, originál v `title`, přepínač CS/EN, MutationObserver pro dynamický obsah | 1 |
| Odborný slovník | `data-src/slovnik.csv` → `data/slovnik.json` | terminologie EN→CS (editovatelná tabulka) | 1 |
| Encyklopedie parametrů | `extension/src/encyklopedie/`, `data-src/parametry/*.yaml` | ikona ⓘ u parametru, karta s vysvětlením | 2 |
| Databáze chyb | `extension/src/chyby/`, `data-src/chyby/*.yaml` | vyhledání podle kódu i příznaku, rozlišení podle řídicí jednotky | 3 |
| Zpracování dokumentace | `tools/` (Python), výstup `data/dokumentace-index.json` | text z PDF po stránkách → vyhledávací index s odkazem dokument+strana | 3 |
| Diagnostický asistent | `extension/src/diagnostika/`, `data-src/pravidla/*.yaml` | ručně zadané hodnoty → pravidla souvislostí → možné příčiny + postup ověření + zdroje | 4 |
| Uživatelské rozhraní | `extension/src/ui/`, `extension/sidepanel/` | panel, přepínače, design Reo Heating | 1–4 |
| (budoucí) AI vrstva | `extension/src/ai/` — **zatím neexistuje** | volitelná, oddělená od statické databáze; jen výslovně odeslaná anonymizovaná data | po etapě 4 |

Moduly spolu komunikují jen přes jasná rozhraní (např. `slovnik.prelozit(text)`,
`chyby.hledat(dotaz, ridiciJednotka)`), takže lze každý rozvíjet zvlášť.

## 3. Struktura složek (cílová)
```
reo-iot-cz/
├── PROJECT_BRIEF.md        úplné zadání
├── README.md               stav, plán, otevřené body, jak pokračovat
├── CLAUDE.md               pravidla pro Claude Code v tomto projektu
├── docs/                   ARCHITEKTURA, BEZPECNOST, TESTOVANI, POWER-WORLD-AI
├── data-src/               ZDROJ odborných dat — upravuje člověk
│   ├── slovnik.csv         EN;CS;kategorie;poznámka (lze otevřít v Numbers/Excelu)
│   ├── parametry/*.yaml    1 soubor = 1 parametr
│   ├── chyby/*.yaml        1 soubor = 1 řídicí jednotka / model
│   └── pravidla/*.yaml     diagnostické souvislosti
├── tools/                  build skripty (validace dat, PDF → index, sestavení data/)
├── extension/              samotné rozšíření (načítá se do Chromu)
│   ├── manifest.json
│   ├── src/…               moduly viz tabulka
│   ├── sidepanel/          HTML/CSS/JS postranního panelu
│   └── data/               GENEROVANÉ JSON (z data-src + index dokumentace)
├── tests/                  automatické testy + anonymizované HTML vzorky stránek
└── podklady/               MIMO GIT: PDF manuály, surové snímky obrazovky
```

## 4. Úrovně důvěryhodnosti informací
Každá odborná položka (parametr, chyba, pravidlo, odpověď asistenta) nese štítek:

| Štítek | Význam | Požadavek |
|---|---|---|
| **V – výrobce** | potvrzeno dokumentací Power World | povinný odkaz: dokument + strana |
| **O – obecná znalost** | obecná technika TČ / chladicích okruhů | bez konkrétních limitů pro model |
| **H – hypotéza** | úvaha asistenta / zatím neověřeno | jasně označit, nikdy jako fakt |
| **R – praxe Reo Heating** | vlastní servisní poznatek | autor + datum |

Číselné limity se do databáze zapisují **jen se štítkem V** a s vazbou na model,
chladivo a režim. Jinak systém vypíše „Dokumentace hodnotu nepotvrzuje.“

## 5. Lokalizace — technické zásady
- Překládají se **pouze textové uzly** (a atributy `placeholder`, `title`, `aria-label`).
- **Nikdy** se nemění `value` u `input/select/textarea/button`, atributy `name`, `id`,
  `href`, `action`, ani `<option>` bez explicitního atributu `value` (jeho text by se odeslal).
- Čísla, jednotky, kódy (např. `E05`, `°C`, `Hz`, Virtual ID) zůstávají beze změny.
- Originál se uchová (`data-reo-orig` + `title`), překlad lze kdykoli vrátit 1 kliknutím.
- Neznámé texty se zaznamenají **jen lokálně** (seznam „chybí překlad“, bez hodnot a jmen),
  aby šlo slovník doplňovat.
- Pokud IOT používá framework, který překreslování textů nesnese, použije se
  „overlay“ režim (překlad v bublině, DOM beze změny). Rozhodne se podle analýzy v etapě 1.

## 6. Dokumentace (etapa 3)
1. PDF se uloží do `podklady/dokumentace/<model>/` (mimo git) a zapíše do `podklady/katalog.yaml`
   (název, model, řídicí jednotka, verze, jazyk, typ, oprávnění k užití).
2. `tools/` extrahuje text po stránkách (PyMuPDF; u skenů OCR), rozdělí na úseky
   a vytvoří lokální fulltextový index (`extension/data/dokumentace-index.json`).
3. Index obsahuje text neveřejných manuálů → **není v gitu**, generuje se lokálně.
4. Vyhledávání běží v rozšíření offline (MiniSearch nebo vlastní jednoduchý index).
5. Odkaz „dokument X, str. N“ otevře PDF přímo na stránce (`file.pdf#page=N`).

## 7. Diagnostický asistent (etapa 4)
- Vstup: ručně vyplněný formulář v panelu (model, chladivo, režim, venkovní teplota,
  požadovaná teplota vody, frekvence kompresoru, další hodnoty) nebo uživatelem
  **výslovně** označené hodnoty ze stránky (bez jména zákazníka a Virtual ID).
- Jádro: **pravidla souvislostí** (YAML), např. „vysoká výtlačná teplota → zkontroluj
  přehřátí sání, tlaky, EEV, průtok vody, ΔT, množství chladiva…“ — vše se štítky V/O/H.
- Výstup: seznam možných příčin (pravděpodobnost jen tam, kde je podložená), postup
  ověřování, odkazy do dokumentace, upozornění na chybějící údaje.
- Bez externí AI. Případná AI vrstva později jen jako samostatný modul s výslovným
  potvrzením odeslání a náhledem toho, co odchází.

## 8. Aktualizace bez přeprogramování
Odborná data žijí v `data-src/` (CSV/YAML). Postup: upravit tabulku → spustit
`python3 reo-iot-cz/tools/build.py` (validace + JSON) → v Chromu „Obnovit“ rozšíření.
Vzdálené stahování aktualizací (by vyžadovalo další síťová oprávnění) zatím nezavádíme.

## 9. Verzování
- Projekt je složka v repozitáři `szkandera79/Projekty` (soukromý, automatická synchronizace).
- Až bude rozšíření stabilní, lze ho vyčlenit do samostatného repozitáře (vlastní verze, release ZIP).
- Verze rozšíření v `manifest.json` (SemVer), změny v `CHANGELOG.md`.
