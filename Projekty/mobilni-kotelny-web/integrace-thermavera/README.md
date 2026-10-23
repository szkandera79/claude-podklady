# Varianta 2 — služba mobilních kotelen jako součást thermavera.cz (zvolená, 23. 10. 2026)

Integrace pronájmu mobilních kotelen do webu ThermaVera. Skript `build_integrace.py` zabalí stránky samostatného webu
(`mobilni-kotelny-web/`, varianta 1) do rámu ThermaVera. Obě varianty tak mají jeden zdroj textů, kalkulačky a obrázků.

```
python3 mobilni-kotelny-web/integrace-thermavera/build_integrace.py --apply      # zápis do thermavera-web/
python3 mobilni-kotelny-web/integrace-thermavera/build_integrace.py <složka>     # jen náhled
```
Zapsáno do `thermavera-web/` 23. 10. 2026 (index.html, sitemap.xml, podsložka mobilni-kotelny/), build `dist/` hotový.
Náhled: konfigurace `thermavera-integrace` v `.claude/launch.json` (port 8009, složka ve scratchpadu).

## Struktura URL
| Stránka | URL |
|---|---|
| Přehled služby | thermavera.cz/mobilni-kotelny/ |
| Kalkulačka ceny tepla | thermavera.cz/mobilni-kotelny/kalkulacka.html |
| Článek „Proč nerozhoduje jen nájem“ | thermavera.cz/mobilni-kotelny/cena-tepla.html |

Stávající `thermavera.cz/kalkulacka.html` (návratnost trvalé kotelny) zůstává beze změny, obě kalkulačky se nepletou.

## Změny na homepage ThermaVera
1. **Menu:** nová položka „Mobilní kotelny“ hned za „Řešení“.
2. **Hero:** třetí tlačítko „Pronájem mobilní kotelny“ vedle „Spočítat návratnost“ a „Prověřit řešení bez investice“.
   Oznamovací lištu nepřidávám, na webu už je lišta ETS2.
3. **Karta „Mobilní kotelna“** v sekci Naše řešení: nový bod „Pronájem i s tepelným čerpadlem“, odkaz
   „Pronájem mobilní kotelny“ místo „Více informací“ (vedl na kontakt).
4. **Patička:** odkaz „Pronájem mobilní kotelny“ ve sloupci Řešení.
5. **Překlady:** nové texty jsou ve slovníku `TR` pro EN/DE/PL (pravidlo `thermavera-web/CLAUDE.md`).
6. **Hero:** k 5 fotkám realizací přibylo 6 AI vizualizací mobilních kotelen se štítkem „Vizualizace“ (jen u nich).

## Podstránky služby
- Hlavička ThermaVera Energy (logo vede na homepage, menu na sekce homepage, „Mobilní kotelny“ aktivní)
  + **druhá lišta služby**: drobečková navigace, Přehled, Kalkulačka, Článek, Ceník a odkup, Časté dotazy.
- Obsah, kalkulačka, ceník a obrázky jsou stejné jako ve variantě 1.
- Patička ThermaVera s údaji Riva Trade, s.r.o. a odkazem na ochranu osobních údajů webu.
- Podstránky jsou jen česky (jako stávající `kalkulacka.html`). Překlad EN/DE/PL je samostatný úkol.

## Nasazení a zbývající body
- **Build `dist/` pro web4u:** kořen je plochý jako dřív, podsložka `dist/mobilni-kotelny/` se nahrává přes FTP
  jako celá složka se strukturou (ne ZIPem přes net2ftp, ten složky zplošťuje).
- **Formulář poptávky** je napojený na `../odeslat.php` (pole model = „Pronájem mobilní kotelny – Havárie/Plánovaná odstávka“).
- **sitemap.xml:** tři nové URL doplněny. **Google Ads:** nová sestava s cílovou stránkou /mobilni-kotelny/ (zbývá).
- **Doména teplonacas.cz** (pokud ji zaregistrujete) jen jako přesměrování 301 na thermavera.cz/mobilni-kotelny/.
- Ceník nájmů (49/79 tis. Kč/měs., doprava 30 tis., montáž 50 tis.) je po nahrání veřejný.

## Varianta 1 vs. 2
| | 1 — samostatný web (teplonacas.cz) | 2 — součást thermavera.cz |
|---|---|---|
| Vyhledávání | nová doména začíná od nuly | využije zaindexovanou doménu a Ads účet |
| Značka | samostatná služba, srozumitelná i bez ThermaVera | posiluje ThermaVera jako komplexního dodavatele |
| Cesta zákazníka | rovnou k pronájmu | z pronájmu snadno k trvalé kotelně (odkup, zápočet) |
| Údržba | dva weby, dva hostingy | jeden web, jeden build |
| Riziko | — | homepage ThermaVera je delší, menu má o položku víc |
