# Projekty

Společný repozitář projektů — web ThermaVera, nabídky a technické podklady pro bytové domy,
marketing a nástroje. Přehled projektů a pravidla pro Claude Code jsou v **`CLAUDE.md`**.

## Struktura
```
Projekty/
├─ CLAUDE.md               # rozcestník + společná pravidla
├─ thermavera-web/         # web thermavera.cz (vlastní CLAUDE.md, README)
├─ vzor-bytove-domy/       # vzorová nabídka pro SVJ / BD
├─ bd-jandova/, bd-michal/, bd-michal-nabidka/
├─ porovnani-x50-2-3/, porovnani-x50-rh060/
├─ mobilni-kotelna-tc/
├─ marketing/
└─ claude-voice-cz/        # kopie (hlavní verze v ~/Developer/ClaudeVoiceCZ)
```

## Synchronizace (GitHub)
Repozitář je zrcadlený na GitHub (`szkandera79/Projekty`, soukromý) a sdílený mezi iMacem
a MacBookem. Pracuj v lokální složce `~/Claude/Projekty` (odkaz na iCloud Drive `Claude/Projekty`).

- **Před prací:** `git pull`
- **Po práci:** `git commit -m "popis" && git push`

Na novém Macu nastaví odkazy `~/Claude/<složka>` skript
`~/Library/Mobile Documents/com~apple~CloudDocs/Claude/_setup-macbook.sh`.
