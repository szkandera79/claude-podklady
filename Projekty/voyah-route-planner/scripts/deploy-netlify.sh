#!/bin/sh
# Sestaví aplikaci a připraví složku ~/voyah-netlify (+ zip). Je-li v ~/.config/voyah-route-planner/.env
# NETLIFY_AUTH_TOKEN a NETLIFY_SITE_ID, rovnou ji nasadí na Netlify (jinak zip nahrát ručně přes app.netlify.com).
# Klíče API se do sestavení nikdy nedostanou (kontrola níže).
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$HOME/voyah-netlify"
cd "$ROOT/frontend"
[ -L node_modules ] || ./link-node-modules.sh
npm run build >/dev/null
rm -rf "$OUT" && cp -R dist "$OUT"
# novější datum ověření z denní kontroly (stejná verze dat) převzít
LATEST="$HOME/.local/share/voyah-route-planner/ceniky-latest.json"
[ -f "$LATEST" ] && python3 - "$LATEST" "$OUT/data/ceniky.json" <<'PY'
import json, sys
a, b = (json.load(open(x)) for x in sys.argv[1:3])
if a.get("generated") == b.get("generated"):
    open(sys.argv[2], "w").write(json.dumps(a, ensure_ascii=False, indent=1))
PY
cat > "$OUT/_headers" <<'H'
/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: no-referrer
/sw.js
  Cache-Control: no-cache
/index.html
  Cache-Control: no-cache
/data/ceniky.json
  Cache-Control: no-cache
/data/osm/*
  Cache-Control: public, max-age=86400
H
ENV="$HOME/.config/voyah-route-planner/.env"
LEAK=$(find "$OUT" -name 'local-keys*')
for K in ORS_API_KEY OCM_API_KEY; do
  V=$(grep -s "^$K=" "$ENV" | cut -d= -f2-)
  [ -n "$V" ] && grep -rqsF "$V" "$OUT" && LEAK="$LEAK $K"
done
if [ -n "$LEAK" ]; then echo "CHYBA: sestavení obsahuje klíče — nenasazuji" >&2; rm -rf "$OUT"; exit 1; fi
rm -f "$HOME/voyah-netlify.zip" && (cd "$OUT" && zip -qr "$HOME/voyah-netlify.zip" .)
TOKEN=$(grep -s '^NETLIFY_AUTH_TOKEN=' "$ENV" | cut -d= -f2-)
SITE=$(grep -s '^NETLIFY_SITE_ID=' "$ENV" | cut -d= -f2-)
if [ -n "$TOKEN" ] && [ -n "$SITE" ]; then
  NETLIFY_AUTH_TOKEN="$TOKEN" npx -y netlify-cli@17.38.1 deploy --prod --dir "$OUT" --site "$SITE" --message "ceníky $(date +%F)" \
    | grep -E "Website URL|Deploy is live|Error" || true
else
  echo "Netlify token není nastaven — nahrajte ručně: $HOME/voyah-netlify.zip"
fi
