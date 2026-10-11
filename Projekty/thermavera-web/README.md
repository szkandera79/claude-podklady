# ThermaVera Energy — web

Jednostránkový web pro službu „zelené kotelny na klíč". Statický, bez frameworků —
jeden soubor `index.html` s interním CSS a vanilla JS.

## Rychlý start
Otevři `index.html` v prohlížeči. Pro živý náhled spusť lokální server:

```bash
python3 -m http.server 8000
# pak otevři http://localhost:8000
```

## Práce s Claude Code
V této složce (nebo v kořeni `~/Claude/Projekty`) spusť `claude`. Kontext projektu (značka, paleta, tón, mantinely,
seznam placeholderů a TODO) je v **`CLAUDE.md`** — Claude Code ho automaticky načte.

Příklady zadání:
- „Změň akcentní barvu na firemní #xxxxxx."
- „Nahraď placeholder v hero fotkou assets/images/kotelna.jpg."
- „Přidej hero slider se dvěma slidy."
- „Napoj kontaktní formulář na odeslání e‑mailem."

## Struktura
```
Projekty/thermavera-web/
├─ index.html              # aktivní web (světlý design)
├─ CLAUDE.md               # kontext a pravidla pro Claude Code
├─ README.md
├─ assets/images/          # sem reálné fotografie
└─ reference/
   ├─ thermavera-dark.html # alternativa: tmavá technická varianta
   └─ vireo.html           # starší koncept značky VIREO
```

## Úprava barev
Vše běží přes CSS proměnné v `:root` v `index.html`. Firemní akcent =
`--green-bright` (a `--amber` pro CTA).

## Nasazení
Jakýkoli statický hosting (Netlify, Vercel, GitHub Pages, FTP na web). Nahraj obsah
složky; vstupní soubor je `index.html`.

## Synchronizace
Web je podprojekt repozitáře **Projekty** (`~/Claude/Projekty/thermavera-web`) — synchronizace
přes GitHub viz `../README.md`.

## Poznámka
Kontaktní údaje, IČO/DIČ a obrázky jsou placeholdery — před spuštěním doplň dle
skutečnosti. Výpočty návratnosti jsou orientační (viz právní poznámka v patičce webu).
