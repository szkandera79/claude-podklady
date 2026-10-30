# Nasazení a spuštění

Od 30. 10. 2026 je hlavní varianta **aplikace bez serveru (varianta 3)**: vše se počítá přímo v telefonu
(`frontend/src/core` = přepis Python jádra, `frontend/src/data` = trasy, nabíječky, počasí; data v IndexedDB telefonu).
Stačí ji nahrát jako statický web s HTTPS. Python backend (`backend/`) zůstává jako referenční implementace,
nástroj pro balík nabíječek a příkazová řádka; serverová varianta (FastAPI + Docker) je popsaná níže pro případ potřeby.

## 1. Sestavení (na Macu)

```bash
cd voyah-route-planner/frontend && npm install && ./link-node-modules.sh
```

```bash
cd voyah-route-planner/backend && ~/.venvs/voyah-route-planner/bin/python tools/build_charger_tiles.py
```

```bash
cd voyah-route-planner/frontend && npx vitest run && npm run build
```

Výsledek je složka `frontend/dist` (≈ aplikace + balík nabíječek CCS2 z OSM pro CZ, SK, AT, PL, HU, SI, HR, DE).
Balík obnovovat cca 1× měsíčně (skript výše) a znovu nahrát.

## 2. Hosting zdarma (statický web s HTTPS)

| Služba | Postup | Poznámka |
|---|---|---|
| **Cloudflare Pages** (doporučeno) | účet zdarma → Workers & Pages → Create → Pages → *Upload assets* → přetáhnout obsah `dist` | adresa `*.pages.dev`; volitelně Cloudflare Access (zdarma) = přístup jen pro váš e-mail |
| Netlify Drop | app.netlify.com/drop → přetáhnout složku `dist` | nejrychlejší; bez účtu odkaz po čase vyprší |
| GitHub Pages | samostatné **veřejné** repo jen se sestavenou aplikací | soukromé repo vyžaduje placený GitHub |

V sestavené aplikaci **nejsou žádné klíče** — publikovat ji je bezpečné.

## 3. Klíče do telefonu (jednou)

```bash
node voyah-route-planner/scripts/setup-link.mjs https://<adresa-aplikace>/
```

Otevře se QR kód s nastavovacím odkazem (klíče jsou za `#`, prohlížeč je nikdy neposílá na server; aplikace je
uloží do telefonu a z adresy smaže). Naskenujte ho fotoaparátem iPhonu → otevře se aplikace → **Sdílet → Přidat
na plochu**. Soubor s QR (`~/.local/share/voyah-route-planner/nastaveni-qr.png`) pak smažte.

Bez klíčů aplikace funguje také: trasy přes záložní OSRM (demo server, jen pro nekomerční užití) a nabíječky
jen z OpenStreetMap.

## 4. Data v telefonu

Nastavení, cesty a kalibrace jsou jen v telefonu (IndexedDB). **Nastavení → Záloha dat → Stáhnout zálohu**
(uložit do Souborů / iCloudu); obnova tamtéž. Smazání dat Safari = ztráta kalibrace, proto zálohovat.

## Klíče na dalších zařízeních

Každá kopie aplikace má vlastní úložiště (Safari ≠ aplikace na ploše iPhonu ≠ aplikace v Docku Macu). Klíče se do ní dostanou:
- **iPhone (aplikace na ploše):** Nastavení → 📷 Naskenovat QR kód s klíči (QR: `node scripts/setup-link.mjs <URL>`).
- **Mac (prohlížeč / Dock):** `node scripts/setup-link.mjs <URL> --schranka` → v aplikaci Nastavení → vložit nastavovací odkaz → Uložit; nebo `--otevrit` (otevře odkaz ve výchozím prohlížeči).
- **Lokální náhled (localhost):** automaticky — `sync-runtime.sh` zapíše `local-keys.json` jen do kopie mimo iCloud
  (práva 600), aplikace ho čte jen na localhost; server poslouchá jen na 127.0.0.1 (z Wi-Fi nedostupný).
  Ve `frontend/dist` ani ve složce pro Netlify soubor nikdy není.

## Lokální náhled (vývoj)

```bash
voyah-route-planner/scripts/sync-runtime.sh
```

Pak v Claude Code náhled „voyah“ (`.claude/launch.json`, port 8010, statický server z kopie mimo iCloud —
náhledový proces nemá přístup do iCloud Drive). `node_modules` leží v `frontend/node_modules.nosync`
(iCloud ji nesynchronizuje); po `npm install` spustit `./link-node-modules.sh`.

## Serverová varianta (rezerva)

FastAPI (`backend/vrp_api`) + Docker + Caddy (`deploy/`) — pro případ, že by výpočty měly běžet na serveru
(sdílená kalibrace více zařízení, skryté klíče). Docker obraz zatím nebyl sestaven ani vyzkoušen.

```bash
cp deploy/.env.example deploy/.env && docker compose -f deploy/docker-compose.yml up -d --build
```
