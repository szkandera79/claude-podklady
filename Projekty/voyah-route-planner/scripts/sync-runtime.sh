#!/bin/sh
# Zkopíruje backend + sestavený frontend mimo iCloud (náhledový server nemá do iCloud Drive přístup).
set -e
SRC="$(cd "$(dirname "$0")/.." && pwd)"
DST="$HOME/.local/share/voyah-route-planner/runtime"
mkdir -p "$DST/backend" "$DST/frontend"
rsync -a --delete --exclude '__pycache__' --exclude '.pytest_cache' "$SRC/backend/" "$DST/backend/"
rsync -a --delete "$SRC/frontend/dist/" "$DST/frontend/dist/"
echo "runtime: $DST"
