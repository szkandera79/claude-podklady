#!/bin/bash
# Spouští synchronizaci zrcadla claude-podklady po dokončení práce v Claude Code
# (Stop hook v ~/.claude/settings.json). Nejvýš jednou za 10 minut, nikdy souběžně.
# Běží uvnitř aplikace Claude, která má přístup k iCloud Drive (úloha na pozadí ho nemá).
STAMP="$HOME/Developer/claude-podklady/.last-sync"
LOCK="$HOME/Developer/claude-podklady/.sync.lock"
LOG="$HOME/Library/Logs/claude-podklady-sync.log"
INTERVAL=600

now=$(date +%s)
last=$(cat "$STAMP" 2>/dev/null || echo 0)
[ $((now - last)) -lt $INTERVAL ] && exit 0
mkdir "$LOCK" 2>/dev/null || exit 0          # už běží jiná synchronizace
echo "$now" > "$STAMP"
(
  trap 'rmdir "$LOCK" 2>/dev/null' EXIT
  echo "=== $(date '+%Y-%m-%d %H:%M:%S')"
  GIT_SSH_COMMAND="ssh -o ConnectTimeout=20 -o BatchMode=yes" \
    /usr/bin/python3 -I "$HOME/Developer/ClaudeVoiceCZ/scripts/sync_podklady.py"
) >> "$LOG" 2>&1 &
exit 0
