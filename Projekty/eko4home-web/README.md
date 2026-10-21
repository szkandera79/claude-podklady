# eko4home-web — návrh redesignu eko4home.cz

Jednostránkový návrh (statické HTML) nového webu eko4home.cz (Riva Trade s.r.o., sídlo Třinec; působí po celé ČR a na Slovensku).

- **Design** podle https://klimatizacekasparek.vercel.app — zelená `#1f6d3f` / tmavá `#123821` / světlá `#e8f3ec`,
  akcent `#fcbb00`, písmo Inter + ručně psaný Kalam. Ilustrační fotky `assets/img/k-*.webp` jsou odtud.
- **Produkty** (ceny bez DPH, za zařízení bez montáže):
  - REO R290 RH030–RH060 — ceny 95/105/125/169 tis. Kč bez DPH (zadal uživatel 20. 10. 2026), COP a fotky z https://reoheating.cz/eshop/
  - REO R290 Smart RH06–RH16 (129/139/149/159/169/189 tis. Kč bez DPH, zadal uživatel 20. 10. 2026) a RHX20 Pro / RHX30 Pro (300/350 tis.) a RH X50 (430 tis., prodejní cena z nástroje kaskád 27. 9. 2026) — záložka „Bytové domy a firmy“
  - Nádrže AKU 100/500, TUV 200/300, Watertank 210/70 a 330/120 — z e-shopu REO
- Úvod přes celou šířku: schéma F s RH060 (`hero-schema.webp`; varianta s RHX30 Pro `hero-x30.webp`) vpravo dole, vlevo rozmazané pozadí (`hero-blur.webp`) + tmavý přechod, bílý text; varianty pozadí v `navrhy-hero/`; pod úvodem pruh „Topí přímo ze sluníčka“ (Smart RH14). Sekce „Pro koho“: rodinné domy · bytové domy a SVJ · komerční objekty
  (BD a firmy = RHX30 Pro + RH X50). Působnost: celá ČR a Slovensko, sídlo Třinec.
- Texty (Proč my, recenze, kontakt) převzaty ze současného eko4home.cz.

## Otevřené body
- Ceny, které chybí / ověřit: montáž, RH X50 — 430 000 Kč převzato z navrh_kaskady.py, ověřit.
- Fotky z referenčního webu: hero (značka AUX) a CTA (Samsung) záměrně vynechány — cizí značky TČ.
  Ostatní k-* fotky jsou AI ilustrace cizího webu → před ostrým nasazením ověřit souhlas / nahradit vlastními.
- Realizace: chybí sekce — vlastní fotky Eko4home (ne Kašpar ani partnerské bez souhlasu).
- Watertank 330/120: e-shop uvádí průměr jednou 70 cm, jednou 56 cm — ověřit.
- Hlučnost RH řady uvádět jako L_WA z protokolů TÜV SÜD, ne „≤47 dB“ z e-shopu.
- Formulář je jen maketa (bez odesílání).

## Náhled
Otevřít `eko4home-web/index.html` v prohlížeči, nebo konfigurace „projekty“ → http://localhost:8000/eko4home-web/

## Obrázky s venkovními jednotkami
Ilustrace z referenčního webu měly cizí bílé jednotky → nahrazeny vložením jednotky REO R290 (`rh-male.png`, logo REO HEATING)
přes Pillow; originály v `assets/src-orig/`. Obrázek „Jak funguje“ = schéma jednotka + Watertank (`src-orig/schema-reo-watertank.webp`) vložené do původní scény, potrubí dokreslené (`tools/schema_*.py`, cesty v nich ukazují do scratchpadu). `k-jak-vybrat.webp` = nově sestavená řada Smart / RH060 / RH030–RH050.

## Parametry na kartách (20. 10. 2026)
- Smart / RHX Pro: max. výkon A7/W35 + modulace z `REO/PW Helios/REO R290 Smart/data/vykonove-mapy.json` (RH14 jen z 1F mapy — 3F chybí).
- Hluk: na webu jen akustický tlak ve 3 m = L_WA − 20·log 3 − 8 (stejně jako `REO/R290-datove-listy/src/compare.js`).
- Topná voda: Smart, RHX Pro, RH X50 až 75 °C; RH030–RH060 až 70 °C (e-shop).
- Sekce „Jak funguje“: scéna G v2 (`tools/scene_g_compose.py`) – jednotka −15 %, černé izolované potrubí, okruh topení do podlahy + popisky TUV / topení; v1 v `src-orig/`.
