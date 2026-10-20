# REO HEATING CRM

Vlastní CRM pro REO HEATING / Ria Trade: leady z formulářů Facebook/Instagram (Google Drive tabulky
„List 2“ = zákazníci, „partneřipoptávky“ = partneři), nástěnka fází (nový → kontakt → schůzka → nabídka →
vyhráno / ztraceno), tabulka, agenda a kalendář schůzek, karta leadu s komentáři, kontakty, poznámky,
soubory z Drivu, e-mail s nabídkou, ceník a faktury / zálohové faktury s QR platbou.

**Artefakt:** https://claude.ai/artifact/LnRFiysRw114a2LJbqid6P („Reo Heating CRM“, soukromý)
— capabilities: `artifact` (stránka si ukládá data sama), `downloads`, MCP Google Drive (čtení tabulek a souborů).

## Struktura
| Cesta | Obsah | Git |
|---|---|---|
| `src/index.html` | celá aplikace (HTML + CSS + JS) s prázdným stavem `{}` | ano |
| `data/state.json` | data CRM: leady, poznámky, kontakty, faktury, nastavení firmy, ceník | **ne** (osobní údaje) |
| `data/artefakt-*.html` | stažené zálohy živé stránky | **ne** |
| `dist/index.html` | sestavená stránka k publikaci (kód + data) | **ne** |
| `build.py` | sestavení / rozdělení | ano |

## Postup úprav (Claude)
1. **Stáhnout živou verzi** artefaktu (Artifact `read` s `path: index.html`, `out_dir: reo-crm/data`) –
   CRM si data ukládá samo, lokální kopie může být starší.
2. `python3 reo-crm/build.py --extract reo-crm/data/index.html` → aktuální data do `data/state.json`, kód do `src/`.
3. Upravit `src/index.html`.
4. `python3 reo-crm/build.py` → `dist/index.html` → publikovat na URL artefaktu výše.

Stav dat při založení projektu: rev 16 z 7. 9. 2026 (463 leadů ve snímku tabulek, 80 faktur, 13 kontaktů).
