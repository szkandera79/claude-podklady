#!/bin/bash
# Automatická obnova instalace Claude Voice (bezplatný Apple účet = 7 dní).
# Spouští ji macOS každých 15 minut (LaunchAgent cz.claudevoice.auto-reinstall).
# Když do vypršení zbývá < 36 h: upozorní na Macu a jakmile je iPhone připojený a odemčený,
# vynutí nový podepisovací profil a aplikaci přeinstaluje.
set -uo pipefail
ROOT="$HOME/Developer/ClaudeVoiceCZ"
STATE="$ROOT/.installed-expiry"
LOCK="$ROOT/.auto-reinstall.lock"
NOTIFIED="$ROOT/.auto-reinstall.notified"
PROFILES="$HOME/Library/Developer/Xcode/UserData/Provisioning Profiles"
BACKUP="$ROOT/.profile-backup"
BUNDLE="cz.claudevoice.jindrichszkandera"
THRESHOLD_HOURS="${THRESHOLD_HOURS:-36}"
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer

notify() { osascript -e "display notification \"$2\" with title \"$1\" sound name \"Glass\"" >/dev/null 2>&1; }
log() { echo "$(date '+%Y-%m-%d %H:%M') $*"; }

# Platnost nainstalované verze (z posledního úspěšného install-iphone.sh, jinak z posledního sestavení)
EXP="$(cat "$STATE" 2>/dev/null)"
if [ -z "$EXP" ]; then
  EXP="$(security cms -D -i "$ROOT/ios/build/Build/Products/Debug-iphoneos/ClaudeVoiceCZ.app/embedded.mobileprovision" 2>/dev/null | plutil -extract ExpirationDate raw -o - - 2>/dev/null)"
fi
[ -n "$EXP" ] || { log "Neznám platnost instalace."; exit 0; }
EXP_TS="$(date -j -u -f "%Y-%m-%dT%H:%M:%SZ" "$EXP" +%s 2>/dev/null)" || exit 0
LEFT_H=$(( (EXP_TS - $(date +%s)) / 3600 ))
[ "$LEFT_H" -ge "$THRESHOLD_HOURS" ] && exit 0

mkdir "$LOCK" 2>/dev/null || exit 0
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

# Je iPhone k dispozici?
DEVICE="$(xcrun devicectl list devices 2>/dev/null | awk '/iPhone/ && /physical/ && !/unavailable/ && (/connected/ || /available/) {for(i=1;i<=NF;i++) if ($i ~ /^[0-9A-F]{8}-[0-9A-F]{16}$/) {print $i; exit}}')"
if [ -z "$DEVICE" ]; then
  # Upozornění na Macu nejvýš jednou za 6 hodin
  if [ ! -f "$NOTIFIED" ] || [ $(( $(date +%s) - $(stat -f %m "$NOTIFIED") )) -gt 21600 ]; then
    notify "Claude Voice: obnova instalace" "Zbývá ${LEFT_H} h. Připojte iPhone kabelem k Macu a odemkněte ho."
    touch "$NOTIFIED"
  fi
  log "Zbývá ${LEFT_H} h, iPhone není připojený."
  exit 0
fi

log "Zbývá ${LEFT_H} h — obnovuji instalaci."
# Vynutit nový profil (jinak by Xcode použil starý se stejnou platností): profily této aplikace do zálohy.
mkdir -p "$BACKUP"
for f in "$PROFILES"/*.mobileprovision; do
  [ -f "$f" ] || continue
  if security cms -D -i "$f" 2>/dev/null | grep -q "$BUNDLE"; then mv "$f" "$BACKUP/"; fi
done
if "$ROOT/scripts/install-iphone.sh"; then
  NEW="$(cat "$STATE" 2>/dev/null)"
  notify "Claude Voice obnoven" "Instalace platí do ${NEW:-dalších 7 dní}. iPhone můžete odpojit."
  rm -f "$NOTIFIED"
  log "Obnoveno do $NEW."
else
  log "Instalace se nepovedla (iPhone zamčený?) — zkusím za 15 minut."
fi
