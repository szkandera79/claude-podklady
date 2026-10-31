#!/bin/sh
# Denní kontrola ceníků v 6:30 (launchd, tento Mac). Odinstalace: launchctl bootout gui/$(id -u)/cz.voyah.ceniky
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PL="$HOME/Library/LaunchAgents/cz.voyah.ceniky.plist"
BIN="$HOME/.local/share/voyah-route-planner/bin"
mkdir -p "$BIN" && cp "$ROOT/backend/tools/update_prices.py" "$BIN/"      # launchd nesmí do iCloud Drive
[ -f "$HOME/voyah-netlify/data/ceniky.json" ] || "$ROOT/scripts/deploy-netlify.sh"
cat > "$PL" <<P
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>cz.voyah.ceniky</string>
  <key>ProgramArguments</key><array>
    <string>/usr/bin/python3</string><string>$BIN/update_prices.py</string>
    <string>--data</string><string>$HOME/voyah-netlify/data/ceniky.json</string>
    <string>--deploy-dir</string><string>$HOME/voyah-netlify</string></array>
  <key>StartCalendarInterval</key><dict><key>Hour</key><integer>6</integer><key>Minute</key><integer>30</integer></dict>
  <key>EnvironmentVariables</key><dict><key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string></dict>
  <key>StandardOutPath</key><string>$HOME/Library/Logs/voyah-ceniky.log</string>
  <key>StandardErrorPath</key><string>$HOME/Library/Logs/voyah-ceniky.log</string>
</dict></plist>
P
launchctl bootout "gui/$(id -u)/cz.voyah.ceniky" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PL"
echo "nainstalováno: $PL (denně 6:30, log ~/Library/Logs/voyah-ceniky.log)"
