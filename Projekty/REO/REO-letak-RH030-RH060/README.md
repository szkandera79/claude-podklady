# REO HEATING — nabídkový leták RH030–RH060 (výprodej skladu)

Dvoustránkový leták A4 pro koncové zákazníky, značka **REO HEATING**, zelená #34A263.
Obsah vychází z mejlové nabídky „totální výprodej skladu“ (10/2026) a z letáku REO R290
(`~/Downloads/Letak-REO-R290 (kopie).pdf`). Přehled „Cena tepla 2026“ záměrně **není** součástí.

- Strana 1: produkt, cena RH040 104 900 Kč bez DPH, 8 parametrů, modelová řada, 4 realizace.
- Strana 2: sestava A (pouze ÚT, 121 400 Kč) a B (ÚT + TUV, 146 400 Kč) + orientační instalace,
  servis PREMIUM, co poslat pro nabídku, QR, cena pro montážní partnery 74 990 Kč.

## Soubory
- `letak.tpl.html` — šablona (interní CSS, bez JS), `gen.py` doplní model → `letak-RH030…RH060.html`
  a `REO_HEATING_Letak_RH0x0.pdf`; spouští `build.sh`. Ceny a texty modelů jsou v `MODELS` v `gen.py`.
- `artefakt/` — stránka s přepínačem modelů (náhled stran jako JPG + PDF),
  artefakt https://claude.ai/artifact/Rq3a8QCf1TP4dbpAeP5Ft5 (po změně: znovu vyrenderovat `artefakt/img` a publikovat).
- `foto/` — fotky realizací (`../REO-katalog-instalaci/fotky` + dodané), `hero-scena.jpg` = výřez z obálky letáku REO R290
- `logo-reo-heating.svg` — závazné logo z `../logo/` (od 22. 10. 2026 jediné povolené), `qr-reoheating.svg`

## Ceny modelů (bez DPH)
RH030 94 900 · RH040 104 900 (mejl) · RH050 124 900 · RH060 168 900 Kč (e-shop 20. 10. 2026, zaokrouhleno na …900).
Příslušenství a orientační instalace u všech modelů podle mejlu pro RH040 — u RH050/RH060 ověřit (větší AKU, instalace).
Cena pro montážní partnery známa jen u RH040 (74 990 Kč), ostatní „na dotaz“.

## Odchylky od mejlu (záměrně)
- Hlučnost: místo „47 dB z 1 m, cca 35 dB ze 3 m“ uvedeno měřené LpA 43–47 dB(A) v 1 m (TÜV SÜD);
  35 dB ve 3 m neodpovídá LWA 57–62 dB(A).
- SCOP „až 4,71“ vypuštěn — v letáku R290 je 4,71 COP při ohřevu TUV, ne SCOP.
- „Průměrná úspora 60–80 000 Kč“ (při výprodejových cenách) a „záruka až 10 let“ doplněny na pokyn uživatele 22. 10. 2026.
- Cena RH040 sjednocena na 104 900 Kč (mejl uvádí jednou 104 990 Kč, součty počítají se 104 900).
- Tepelná ztráta pro RH040 „7–10 kW“ (mejl uvádí jednou 6–9 kW).

## Fotky realizací (22. 10. 2026)
- Strana 1: Dolní Morava, Dolní Benešov, Kunčice (venkovní jednotky) + `novy-venek.jpg`; strana 2: kotelny (`novy-kotelna.jpg`, Benešov, Odry = `odry-watertank.jpg` s nádrží WATERTANK).
- `novy-venek.jpg` a `novy-kotelna.jpg`: dodané uživatelem, nápis cizí značky na jednotce a hydroboxu přepsán na „REO HEATING“
  (retuš v PIL — vyplnění plochy přechodem a nový nápis Avenir Next). Lokalita: Baška u Frýdku-Místku.
