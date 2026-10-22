# Logo REO HEATING — závazné pro všechny dokumenty

**Od 22. 10. 2026 se v dokumentech REO HEATING používá jen toto logo** (šedá + zelená střecha,
žluté okno a slunce, pod tím nápis „REO HEATING“). Žádné jiné varianty (modré „RH“, stříbrné
„REO HEATING“ s obloukem, kreslené „REO HEATING S.R.O.“, „REOHEATING“ z webu) už nenabízet.

| Soubor | Použití |
|---|---|
| `logo-reo-heating.svg` | HTML/PDF dokumenty (vektor, text převeden na křivky) |
| `logo-reo-heating.png` | 3000 px, průhledné pozadí — Word, PowerPoint, PyMuPDF rebrandy |
| `logo-reo-heating-white(.svg/.png)` | na tmavé/zelené podklady (bílý nápis, světle šedá střecha) |
| `predloha-logo-reo-heating.png` | předloha od uživatele (292×140 px) — jen reference |

Barvy: šedá `#838383`, zelená `#50854D`, žlutá `#F0C246`, písmo `#363533`.

Logo je **překreslené z rastrové předlohy** (`build_logo.py`); písmo nápisu je Avenir Next Medium
jako nejbližší dostupná náhrada. Až bude k dispozici originální vektor (AI/SVG/PDF), nahradit jím.

Build: `./build.sh` (SVG z `build_logo.py`, PNG přes Chrome headless).
