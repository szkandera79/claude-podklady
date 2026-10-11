#!/bin/bash
# Uloží na server token GitHubu (jen pro čtení repozitáře projektů) a ověří přístup.
# Spuštění:  ~/Developer/ClaudeVoiceCZ/scripts/set-github-token.sh  — otevře okno pro vložení tokenu.
set -uo pipefail
cd "$(dirname "$0")/../server"
REPO="$(sed -n 's/^GITHUB_REPO = "\([^"]*\)".*/\1/p' wrangler.toml)"

INPUT="$(osascript <<'OSA' 2>/dev/null
set dlg to display dialog "Vložte token GitHubu (⌘V) a klikněte na Uložit.

Token se uloží jen na váš server a slouží pouze ke čtení repozitáře projektů." default answer "" with hidden answer with title "Claude Voice CZ – GitHub" buttons {"Zrušit", "Uložit"} default button "Uložit" cancel button "Zrušit" with icon note
return text returned of dlg
OSA
)"
TOKEN="$(printf "%s" "$INPUT" | LC_ALL=C grep -Eo '(github_pat_|ghp_)[A-Za-z0-9_]{20,}' | head -1)"
unset INPUT
if [ -z "$TOKEN" ]; then
  echo "❌ V okně nebyl token GitHubu (začíná „github_pat_“). Spusťte skript znovu."; exit 1
fi
echo "✓ Token přijat (${TOKEN:0:11}…, ${#TOKEN} znaků). Ověřuji přístup k ${REPO}…"
CODE="$(curl -s -o /dev/null -w "%{http_code}" -L -H "Authorization: Bearer $TOKEN" -H "User-Agent: claude-voice-cz" "https://api.github.com/repos/$REPO/contents/")"
if [ "$CODE" != "200" ]; then
  unset TOKEN
  echo "❌ GitHub odmítl přístup k ${REPO} (HTTP $CODE). Zkontrolujte, že token má přístup k tomuto repozitáři a oprávnění Contents: Read-only."
  exit 1
fi
echo "✓ Token vidí repozitář ${REPO}."
printf "%s" "$TOKEN" | npx wrangler secret put GITHUB_TOKEN >/dev/null 2>&1 || { unset TOKEN; echo "❌ Uložení na server selhalo."; exit 1; }
unset TOKEN
printf "" | pbcopy
echo "✓ Token uložen jako šifrovaný secret na serveru. Schránka vymazána."
echo "Hotovo — napište to Claudovi v Claude Code, vyzkouší to."
