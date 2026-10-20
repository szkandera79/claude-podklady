# CLAUDE.md – reo-crm

- Data CRM jsou osobní údaje (GDPR): nikdy je necommituj, nevkládej do `src/`, README ani do odpovědí víc, než je potřeba.
  `data/` a `dist/` jsou v `.gitignore` – nesahej na to.
- Artefakt se ukládá sám. Před každou publikací stáhni živou verzi a spusť `build.py --extract`; publikace ze starých dat
  by přepsala práci uživatele. `force` jen s výslovným souhlasem.
- Kód je jeden soubor `src/index.html`; funkce `buildDoc` skládá uloženou stránku (title, styl, stav, SHELL, skript) –
  při změně struktury stránky ji uprav taky, jinak se po prvním uložení změna ztratí.
- Texty česky, tón B2B (viz kořenový CLAUDE.md).
