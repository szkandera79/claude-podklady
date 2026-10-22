# CLAUDE.md — REO HEATING (web)

## O projektu
Jednostránkový web značky **REO HEATING** — český výrobce tepelných čerpadel vzduch–voda.
Provozovatel: Riva Trade s.r.o., IČ 08864811. Showroom Smetanova 555, 739 61 Třinec.
Kontakt: info@reoheating.cz, +420 774 872 467. Cíl webu: **nezávazné poptávky**.

Web vznikl jako **klon designu** <https://klimatizacekasparek.vercel.app> (bílo-zelený,
Inter + Kalam, sticky průsvitná hlavička, střídání bílá / světle zelený tint / tmavě zelené
pruhy, reveal-on-scroll). Obsah je REO HEATING.

## Tech
- **Jeden soubor `index.html`** — interní CSS (`<style>`) + vanilla JS. Žádné frameworky.
- Barvy přes CSS proměnné v `:root`. Změna akcentu = `--brand`.
- Fonty Google: **Inter** (vše) + **Kalam** (ručně psaný akcent v h1 a v tagline).
- Jazyk: **pouze čeština** (na rozdíl od thermavera-web zde není i18n).

## Paleta
    --brand:#26804B        /* akcent, tlačítka, ikony */
    --brand-600:#1E6A3D
    --brand-dark:#1A5433   /* nadpisy, tmavé sekce */
    --brand-darker:#123D25 /* footer */
    --brand-light:#E9F6EE  /* pozadí ikon, světlé sekce */
    --brand-tint:#F5FBF7   /* jemné pozadí sekcí */
    --fg:#16241C  --muted:#5C6B62  --line:#E4EBE6

## Pořadí sekcí (podle vzoru)
header → `#uvod` hero → `#jak` (tmavá, princip) → `#naklady` (porovnání) → proces →
`#cerpadla` (3 produkty) → `#specifikace` (záložky s tabulkami) → `#sluzby` →
tmavý CTA pruh → `#proc` (Proč si vybrat nás) → `#realizace` (galerie + lightbox) →
Kvalitní montáž (split + checklist) → `#dotace` (Užitečné informace + partneři) →
`#kontakt` → footer.

## Obsahové mantinely
- **Žádné fiktivní reference ani recenze.** Realizace jsou reálné (katalog REO HEATING);
  pokud přibudou, přidávej je do pole `PROJECTS` v JS (hero + detailní fotky s popiskem).
- Náklady v sekci `#naklady` jsou **modelový propočet** — vždy nechat poznámku s předpoklady.
  Negarantovat úspory ani návratnost.
- Technické parametry drž shodné s katalogem výrobce; u tabulek nechat poznámku o normovaných
  podmínkách měření.
- Formulace „do −15 °C bez elektrodohřevu, provoz do −25 °C" — neměnit na silnější tvrzení.

## Placeholdery / TODO
- Chybí produktové fotky samotných jednotek (v kartách produktů jsou zatím fotky z realizací).
- Formulář: `odeslat.php` běží až na PHP hostingu (lokálně vrací chybu — to je v pořádku).
- Zvážit převzetí kalkulačky z thermavera-web (`kalkulacka.html`) v REO brandingu.

## Logo
- Od 22. 10. 2026 jen nové logo z `~/Claude/REO/logo/` (šedá + zelená střecha, slunce, nápis
  „REO HEATING“). `assets/images/logo-reo.png` / `logo-reo-alpha.png` = barevné, `logo-reo-white.png`
  = bílý nápis do tmavého footeru (720 px, průhledné). `favicon.svg` = jen symbol domů + slunce.
- Staré modré „RH / REOHEATING“ logo už nepoužívat.

## Konvence
- Texty česky, tlačítka v sentence-case („Nezávazná poptávka", „Zjistit více").
- Po větší změně zkontroluj breakpointy 1024 / 680 px a přístupnost (alt, aria, kontrast).
