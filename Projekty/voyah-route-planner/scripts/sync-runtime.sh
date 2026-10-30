#!/bin/sh
# Zkopíruje backend + sestavený frontend mimo iCloud (náhledový server nemá do iCloud Drive přístup).
set -e
SRC="$(cd "$(dirname "$0")/.." && pwd)"
DST="$HOME/.local/share/voyah-route-planner/runtime"
mkdir -p "$DST/backend" "$DST/frontend"
rsync -a --delete --exclude '__pycache__' --exclude '.pytest_cache' "$SRC/backend/" "$DST/backend/"
rsync -a --delete "$SRC/frontend/dist/" "$DST/frontend/dist/"
# klíče jen pro lokální náhled (localhost) — soubor vzniká pouze v kopii mimo iCloud, nikdy ve frontend/dist
ENVF="$HOME/.config/voyah-route-planner/.env"
if [ -f "$ENVF" ]; then
  ( umask 077; python3 - "$ENVF" "$DST/frontend/dist/local-keys.json" <<'PY'
import json, sys
env = dict(l.split("=", 1) for l in open(sys.argv[1]).read().splitlines() if "=" in l and not l.lstrip().startswith("#"))
k = {"ors": env.get("ORS_API_KEY", "").strip(), "ocm": env.get("OCM_API_KEY", "").strip()}
json.dump({a: b for a, b in k.items() if b and b != "sem-vlozte-klic"}, open(sys.argv[2], "w"))
PY
  )
fi
echo "runtime: $DST"
