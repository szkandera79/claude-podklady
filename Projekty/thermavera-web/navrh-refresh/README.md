# Návrh refreshe thermavera.cz podle FB kreativ (11. 11. 2026)

Světlý styl podle bannerů REO HEATING (bílý podklad, jasně zelená, žlutá CTA, antracitový text, zelené a žluté oblouky).
**Jen návrh:** `refresh.css` přepisuje interní styly `index.html`, ostrý web ani `dist/` se nemění.
Texty se nemění, takže není potřeba nic překládat.

## Náhled
Kopie `dist/` ve scratchpadu + `<link rel="stylesheet" href="refresh.css">` za interní `<style>`;
konfigurace `thermavera-refresh` v `.claude/launch.json` (port 8010). Současný stav pro srovnání: `thermavera-integrace` (port 8009).

## Co se mění
| Prvek | Teď | Návrh |
|---|---|---|
| Paleta | tmavě zelená #2E6B33, text #16201C | jasně zelená #5AA23C, žlutá #F2C230, antracit #1F2421, světlé pozadí |
| Hero | tmavý přechod přes fotku, bílé písmo | světlý panel vlevo, fotka vpravo, tmavé písmo, zelené zvýraznění, oblouky dole |
| Ikony | kolečko se světle zeleným podkladem | bílé kolečko s tenkým zeleným obrysem |
| Zvýrazněné bloky (model, CTA pruh, kontaktní karta) | tmavě zelené | jasně zelené |
| Patička | tmavá | světlá se zeleným pruhem nahoře |
| Menu | položky se lámaly na dva řádky | jeden řádek, e‑mail v hlavičce schovaný pod 1 500 px |

## Zapracování (po schválení)
Přenést pravidla z `refresh.css` do `:root` a příslušných pravidel v `<style>` v `index.html`
(nebo `refresh.css` přidat do `dist/` a načíst ho odkazem), přegenerovat `dist/`, nahrát `index.html`.
Podstránky `mobilni-kotelny/` a `kalkulacka.html` mají vlastní styly — sjednotit zvlášť.
Aktualizovat paletu v `thermavera-web/CLAUDE.md`.
