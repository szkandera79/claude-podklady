# CLAUDE.md — Reo Heating IOT CZ

Před prací si přečti `README.md` (stav etap, otevřené body) a dodržuj `docs/BEZPECNOST.md`.

## Nepřekročitelná pravidla
- **Read-only.** Rozšíření nemění hodnoty formulářů, neposílá požadavky, neklikne za uživatele,
  neprochází seznam zařízení, nečte hesla ani cookies. Ve verzích 1–4 žádná síťová komunikace.
- Oprávnění jen `storage`, `sidePanel` a adresa IOT `http://162.62.225.58/*`.
- **Nevymýšlej strukturu IOT ani jeho API** — vycházej jen ze snímků/HTML vzorků od uživatele.
- **Nevymýšlej číselné limity.** Limit jen se štítkem V (výrobce) a odkazem dokument + strana;
  jinak „Dokumentace hodnotu nepotvrzuje.“ Štítky: V výrobce / O obecná znalost / H hypotéza / R praxe Reo Heating.
- Stejný chybový kód může znamenat u různých řídicích jednotek něco jiného — vždy evidovat jednotku.
- Do gitu nikdy: PDF manuály, index z nich, neanonymizované snímky, jména zákazníků, Virtual ID, hesla.
  Ukládej je rovnou do `podklady/` (je v `.gitignore`); repo se synchronizuje automaticky.
- Diagnostika: možné příčiny + postup ověření, ne definitivní diagnóza.

## Styl
- Česky, srozumitelně — uživatel není programátor; každý krok vysvětli a řekni, co má udělat on.
- Odborná data se upravují v `data-src/` (CSV/YAML), kód je čte přes build skript v `tools/`.
