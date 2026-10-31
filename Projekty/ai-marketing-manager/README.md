# AI Marketing Manager

Vlastní aplikace pro správu marketingu značek **REO Heating, ThermaVera, Super Heating CZ a Eko4home** (Riva Trade, s.r.o.):
dashboard, AI asistent v češtině, správa kampaní Meta (Facebook + Instagram) přes oficiální API, generátor bannerů,
schvalování změn, reporty. Cíl: nahradit reklamní agenturu.

**Kód:** `~/Developer/ai-marketing-manager` (vlastní git, mimo iCloud) – podrobnosti v jeho `README.md` a `CLAUDE.md`.
**Návrh a audit:** [`navrh-faze-1-2.md`](navrh-faze-1-2.md) (schváleno 31. 10. 2026).

## Stav
- 31. 10. 2026: hotová **první verze (fáze 3)** + integrovaný generátor bannerů (modul Kreativy). Běží lokálně
  (konfigurace „ai-marketing“ v `.claude/launch.json`, port 3100).
- Chybí k ostrému provozu: **token systémového uživatele Meta** (návod v aplikaci → Nastavení), **ANTHROPIC_API_KEY**
  pro asistenta, server (VPS) + doména.
- Další fáze: publikování kampaní, kalendář a příspěvky, leady + CRM, reporty a automatizace, Google Ads, iOS.
