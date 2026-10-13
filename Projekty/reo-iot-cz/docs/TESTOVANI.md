# Plán testování — Reo Heating IOT CZ

Testujeme ve třech vrstvách: **automaticky** (bez IOT, na anonymizovaných vzorcích),
**bezpečnostně** (statická kontrola kódu) a **ručně v IOT** (uživatel podle checklistu).

## 1. Automatické testy (Claude Code spouští při každé změně)
| Oblast | Co se ověřuje |
|---|---|
| Data | `data-src/` projde validací: povinná pole, štítek V/O/H/R, u štítku V odkaz dokument+strana, žádné duplicity v slovníku, číselné limity jen se štítkem V |
| Překlad | na uložených HTML vzorcích: přeloží se očekávané texty; čísla, jednotky a kódy zůstanou; originál dostupný v `title`; vypnutí vrátí stránku do původního stavu (porovnání DOM) |
| Formuláře | po překladu jsou `value`, `name`, `selected` a odesílaná data všech formulářů **identická** s originálem (`FormData` před/po) |
| Dynamický obsah | vložení nového prvku do stránky → přeloží se; žádná nekonečná smyčka observeru |
| Chyby | vyhledání podle kódu vrací správnou řídicí jednotku; stejný kód u dvou jednotek → dva oddělené výsledky |
| Diagnostika | sada ručně připravených anonymizovaných případů → očekávané doporučené kontroly; bez dat model/režim asistent upozorní na chybějící údaje |
| Výkon | překlad stránky do ~100 ms, žádné znatelné zpomalení |

Nástroj: Node + jsdom (nebo Playwright s lokálním HTML) — upřesní se v etapě 1.

## 2. Bezpečnostní kontrola (automaticky, blokuje vydání)
- `manifest.json` neobsahuje jiná oprávnění než povolená (`BEZPECNOST.md` §2).
- Grep kódu na `fetch(`, `XMLHttpRequest`, `WebSocket`, `sendBeacon`, `eval(`, `.value =`,
  `.submit(`, `.click(` → musí být prázdný (výjimky jen se zdůvodněním).
- `git ls-files` neobsahuje PDF, snímky mimo `tests/vzorky/`, `.env`, index dokumentace.
- Vzorky v `tests/vzorky/` neobsahují vzory typu e‑mail, telefon, Virtual ID (regex + ruční kontrola).

## 3. Ruční test v IOT (uživatel, checklist ke každé verzi)
1. Rozšíření vypnuto → otevřít zařízení, projít obrazovky → vše funguje (výchozí stav).
2. Rozšíření zapnuto → stejné obrazovky: texty česky, hodnoty a jednotky beze změny.
3. Najetí myší na přeložený parametr → zobrazí se anglický originál.
4. Přepnout CS ↔ EN a vypnout překlad → okamžitě se vrátí originál.
5. Otevřít servisní nastavení **bez ukládání** → hodnoty polí shodné s anglickou verzí.
6. Konzole Chrome (Zobrazit → Vývojář → Konzole): žádné chyby rozšíření.
7. Karta Síť (Network): rozšíření nevytváří žádné vlastní požadavky.
8. Zaznamenat chybějící / nepřesné překlady → doplnit do `slovnik.csv`.

> Servisní nastavení během testu **neukládat**. Test probíhá na vlastním zařízení
> Reo Heating, nikdy na zařízení jiného distributora.

## 4. Odborná kontrola obsahu
Každá nová dávka parametrů/chyb/pravidel projde odbornou revizí uživatele
(terminologie, správnost postupů). Stav revize se zapisuje do položky (`revize: datum, kdo`).
