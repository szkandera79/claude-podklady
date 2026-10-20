# eko4home-web — návrh redesignu eko4home.cz

Jednostránkový návrh (statické HTML) nového webu eko4home.cz (Riva Trade s.r.o., sídlo Třinec; působí po celé ČR a na Slovensku).

- **Design** podle https://klimatizacekasparek.vercel.app — zelená `#1f6d3f` / tmavá `#123821` / světlá `#e8f3ec`,
  akcent `#fcbb00`, písmo Inter + ručně psaný Kalam. Ilustrační fotky `assets/img/k-*.webp` jsou odtud.
- **Produkty** (ceny bez DPH, za zařízení bez montáže):
  - REO R290 RH030–RH060 — ceny, COP a fotky z https://reoheating.cz/eshop/ (129/139/159/189 tis.)
  - REO R290 Smart RH06–RH16 (99–149 tis.) a RHX20 Pro / RHX30 Pro (300/350 tis.) a RH X50 (430 tis., prodejní cena z nástroje kaskád 27. 9. 2026) — záložka „Bytové domy a firmy“
  - Nádrže AKU 100/500, TUV 200/300, Watertank 210/70 a 330/120 — z e-shopu REO
- Úvod: jednotka RH060 s logem REO HEATING (`rh-velke.png` z e-shopu). Sekce „Pro koho“: rodinné domy · bytové domy a SVJ · komerční objekty
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
