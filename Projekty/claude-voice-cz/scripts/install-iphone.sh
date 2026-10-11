#!/bin/bash
# Claude Voice CZ — (pře)instalace aplikace do iPhonu jedním příkazem.
# Použití: připojte iPhone kabelem (nebo ve stejné Wi-Fi), odemkněte ho a spusťte:
#   ~/Developer/ClaudeVoiceCZ/scripts/install-iphone.sh
# S bezplatným Apple účtem platí instalace 7 dní — pak stačí spustit tento příkaz znovu.
set -uo pipefail
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
cd "$(dirname "$0")/../ios"

say() { printf "\n\033[1;34m▶ %s\033[0m\n" "$*"; }
ok() { printf "\033[1;32m✓ %s\033[0m\n" "$*"; }
fail() { printf "\033[1;31m✗ %s\033[0m\n" "$*"; exit 1; }

say "1/3 Hledám iPhone"
DEVICE="$(xcrun devicectl list devices 2>/dev/null | awk '/iPhone/ && /physical/ && !/unavailable/ && (/connected/ || /available/) {for(i=1;i<=NF;i++) if ($i ~ /^[0-9A-F]{8}-[0-9A-F]{16}$/) {print $i; exit}}')"
[ -n "$DEVICE" ] || fail "iPhone nenalezen. Připojte ho kabelem, odemkněte a případně potvrďte „Důvěřovat tomuto počítači“."
ok "iPhone nalezen ($DEVICE)"

say "2/3 Sestavuji aplikaci (může trvat 1–2 minuty)"
LOG="$(mktemp)"
if ! xcodebuild -project ClaudeVoiceCZ.xcodeproj -scheme ClaudeVoiceCZ -destination 'generic/platform=iOS' \
     -derivedDataPath build -allowProvisioningUpdates build >"$LOG" 2>&1; then
  grep -E "error:" "$LOG" | head -5
  fail "Sestavení selhalo. Pošlete Claudovi výpis výše."
fi
EXP="$(security cms -D -i build/Build/Products/Debug-iphoneos/ClaudeVoiceCZ.app/embedded.mobileprovision 2>/dev/null | plutil -extract ExpirationDate raw -o - - 2>/dev/null)"
ok "Sestaveno. Nová instalace platí do: ${EXP:-neznámo}"

say "3/3 Instaluji do iPhonu (iPhone musí být odemčený)"
if xcrun devicectl device install app --device "$DEVICE" build/Build/Products/Debug-iphoneos/ClaudeVoiceCZ.app >"$LOG" 2>&1; then
  [ -n "$EXP" ] && printf "%s" "$EXP" > "$(dirname "$0")/../.installed-expiry"
  ok "Hotovo — aplikace Claude Voice je v iPhonu. Konverzace i nastavení zůstaly zachované."
else
  grep -iE "error|unlock|locked" "$LOG" | head -3
  fail "Instalace selhala — nejčastěji je iPhone zamčený. Odemkněte ho a spusťte příkaz znovu."
fi
