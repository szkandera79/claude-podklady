# RH030 – RH060 — návod k instalaci a obsluze (novější ovladač), REO HEATING

Česká verze originálu výrobce `../Power World New Version Software R290 Heat Pump.pdf` (verze 1.0, 28. 5. 2024, 62 stran)
pro jednotky s **novějším dotykovým ovladačem**. Stejný postup a design jako u návodu pro starší ovladač
(`../../PW R290/RH030-RH060 - REO HEATING/`): originální layout, český text vysázený na místo anglického,
logo REO HEATING na titulce.

Výstup: `RH030-RH060-novy-ovladac-navod-CZ_REO-HEATING.pdf` (62 stran, 10,8 MB). Publikováno v artefaktu
„Manuály REO HEATING“ (https://claude.ai/artifact/2DUqsPohBnVWECCKqTdYYu, `r290-novy/`) a připraveno v
`../../R290-datove-listy/` pro artefakt „REO R290“ (EfdLeGPzZkM3H3RM4ZFTWR).

| Originál | REO HEATING |
|---|---|
| PWxxx-DKZLRS-E/S (i „-ES“) | RHxxx (1fázové) |
| PWxxx-DKZLRS-E | RHxxx (3fázové) |

Originál pokrývá i **RH040 3F, RH055 a RH070** (1F/3F) — v návodu ponecháno věrně (rebrand ≠ redesign).

## Postup (složka `cz/`)
1. `extract.py` → `segments.json`, `chunks/`; `icons_extract.py` → `icons.json`
2. překlad: 398 segmentů převzato ze staršího návodu (shodný anglický text, `tm_hits.json`), zbytek přeložen
   podle `PREKLAD-ZADANI.md` (`todo/` → `cs_todo/`); vše sloučeno do `cs/chunk_00.json`; ikony v textu `cs_icons.json`
3. `build.py` → PDF. Ruční úpravy v `OVERRIDE` (titulka, rámeček NEBEZPEČÍ, nadpisy s modely), svislé popisky
   obr. 2 a 3 (`FIG2`, `FIG_PAGES`), tabulky náhradních dílů `nahradni-dily.json` (str. 11–13, shodné se starým návodem),
   úpravy obrázků `IMG_EDITS`: schéma kaskády (kód ovladače výrobce „PW58330“ → „Kabelový ovladač“, popisky česky),
   snímky telefonu s Wi‑Fi výrobce „pwjsb“/„PWAB“ → neutrální názvy. Odstraněn zvýrazňovač originálu (anotace + žluté
   podbarvení). Build na konci kontroluje odkazy na výrobce v textu i metadatech; rastry ověřeny OCR (macOS Vision).

## Narovnáno v překladu
NEC/CEC → ČSN/EN; R290 je hořlavé; Er 20 „1–348“ → 384; P23/P24 (sklon vs. posun křivky) podle vzorce;
podmínka vypnutí TBH „chlazení/TUV“ → „chlazení/vytápění“; 61_4 ikona při párování „bliká“ (orig. „does not flash“).

## K ověření (rozpory v originálu, přeloženo věrně)
- Číslování kapitol: „4.3“ je dvakrát (topná vložka TUV a záložní ohřev vytápění).
- H02: tabulka 0 = nízkouhlíkový / 1 = ekonomický hybridní, text uvádí H02=1 / H02=2.
- Ceny H07–H09 v RMB; buňky S3/S4 tabulky parametrů jsou v originále useknuté.
- Schéma kaskádové instalace (str. 16) a schémata zapojení (str. 21–22) zůstávají anglicky (rastrové obrázky).
