# Evidence nabídek (ThermaVera · REO HEATING)

Přehled všech obchodních nabídek, studií a smluv na jednom místě. Vzniklo 2. 11. 2026.

- **Artefakt:** https://claude.ai/artifact/WxyCpZ8Vr113qLqytUFg7U (soukromý, `capabilities {"db": {}}`)
- **Zdroj stránky:** `index.html` — po úpravě publikovat na stejnou URL (bez parametru `capabilities` se zachová `db`).
- **Data žijí v databázi artefaktu**, kolekce `nabidky` (ne v gitu — jsou tam jména soukromých osob).
  Claude je čte a zapisuje nástrojem `ArtifactData` (`list` / `set` / `update` s `if_version`).

## Záznam (dokument v `nabidky/<id>`)
`klient, misto, segment, znacka (ThermaVera | REO HEATING), typ, cislo, datum (YYYY-MM-DD nebo YYYY-MM),
reseni, cena (číslo, Kč bez DPH, hlavní varianta), cenaText, navratnost, stav, dalsiKrok, termin, kontakt,
odkaz (URL artefaktu), slozka (cesta v Projektech), poznamka, upraveno (ISO)`

Stavy: `rozpracovano · k-odeslani · odeslano · jednani · vyhrano · prohrano · nahrazeno · doplnit · vzor`.
„Otevřené“ v souhrnu = rozpracováno + k odeslání + odesláno + jednání. `vzor` se ukazuje zvlášť jako šablony.

## Pravidlo
**Každá nová nebo revidovaná nabídka → nový / upravený záznam v evidenci** (id = slug složky, např. `bd-jandova-rev1`).
Starou verzi přepnout na `nahrazeno`.

## Výchozí naplnění (2. 11. 2026)
12 nabídek/studií/smluv + 5 vzorů ze složek Projektů a `ThermaVera nabídky/`. Stav u starších je
`doplnit` — skutečný stav zná jen uživatel. Vynecháno: RD Vendryně 738 (vlastní realizace), leady z `reo-crm`.
