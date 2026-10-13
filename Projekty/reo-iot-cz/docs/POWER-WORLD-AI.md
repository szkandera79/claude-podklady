# Prověření AI diagnostiky Power World (zadání bod 8)

Stav k 2026-10-13: **existence AI diagnostiky NEPOTVRZENA.**

## Co veřejné zdroje potvrzují
- Power World provozuje **IoT cloudovou platformu** (Wi‑Fi / DTU), která zaznamenává provozní
  parametry jednotek; při poruše jde hlášení servisnímu partnerovi nebo do back-endu Power World.
  IoT je standardem u řad R32 a R290. ([powerworldhp.com](https://www.powerworldhp.com/heat-pump-series),
  [ISH 2025 – profil vystavovatele](https://ish.messefrankfurt.com/frankfurt/en/exhibitor-search.detail.html/power-world-machinery-equipment-co-ltd/mf_1_0052505337_4349217_10000006202501.html))
- Nizozemský distributor popisuje, že se servisní technici přihlásí k TČ na dálku a z dat
  **sami** udělají prvotní analýzu příčiny — jde o ruční diagnostiku, ne AI.
  ([powerworld-e.nl – IoT increases service](https://powerworld-e.nl/en/news/iot-increases-service))
- Existuje video návod k „IoT Management Platform“ ([YouTube](https://www.youtube.com/watch?v=ePF3p7GiuSI)).

## Co se nenašlo
- Žádná zmínka o AI / strojovém učení pro diagnostiku u Power World.
- Žádná veřejná dokumentace API, SDK ani vývojářský portál.
- Žádné podmínky pro integraci třetích stran.

## Závěr a další krok
- Pro projekt **navrhujeme vlastní nezávislé řešení** (pravidla + dokumentace, viz `ARCHITEKTURA.md` §7).
- Doporučený dotaz na Power World (e‑mail z obchodního kontaktu / after-sales):
  1. Má IOT platforma AI nebo automatickou diagnostiku? Je pro distributory dostupná?
  2. Existuje API nebo export dat pro distributora, omezený na vlastní zařízení?
  3. Souhlasí s použitím rozšíření prohlížeče (read-only, překlad) nad platformou?
  4. Je k dispozici kompletní seznam parametrů a chybových kódů pro jednotlivé řídicí jednotky?
- Odpověď zapsat sem s datem.
