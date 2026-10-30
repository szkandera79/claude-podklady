# Nasazení a spuštění

## Lokálně na Macu (vývoj)

```bash
cd voyah-route-planner/frontend && npm install && ./link-node-modules.sh && npm run build
```

```bash
voyah-route-planner/scripts/sync-runtime.sh
```

Pak v Claude Code náhled „voyah“ (`.claude/launch.json`, port 8010) — server běží z kopie mimo iCloud
(`~/.local/share/voyah-route-planner/runtime`), protože náhledový proces nemá přístup do iCloud Drive.
Klíče: `~/.config/voyah-route-planner/.env`. Data (nastavení, cesty, kalibrace): `~/.local/share/voyah-route-planner/app.sqlite`.

Z iPhonu ve stejné Wi-Fi lze otevřít `http://<IP Macu>:8010`, ale **bez GPS** (Safari dává polohu jen přes HTTPS) —
místo polohy lze do „Odkud“ psát adresu.

`node_modules` leží v `frontend/node_modules.nosync` (iCloud ji nesynchronizuje); po každém `npm install` spustit
`./link-node-modules.sh`.

## Server (VPS) — doporučeno

1. VPS s Dockerem, např. Hetzner CX22 (2 vCPU, 4 GB RAM, ~4–5 €/měs.), Ubuntu 24.04.
2. Doména (nebo subdoména) s A záznamem na IP serveru.
3. Na server zkopírovat složku `voyah-route-planner` (bez `node_modules*`, `dist`).
4. `cp deploy/.env.example deploy/.env` a doplnit DOMAIN, ORS_API_KEY, OCM_API_KEY, VRP_APP_TOKEN.
5. `docker compose -f deploy/docker-compose.yml up -d --build`
6. V Safari na iPhonu otevřít `https://<doména>`, zadat token, **Sdílet → Přidat na plochu**.

⚠️ Docker obraz zatím nebyl sestaven ani vyzkoušen (lokálně není Docker). Ověřit při prvním nasazení.

⚠️ Záložní router OSRM používá veřejný demo server, který není určen pro provoz. Na VPS má být hlavním routerem
openrouteservice (klíč), případně vlastní Valhalla/OSRM (CZ+okolí ≈ 4–8 GB RAM).
