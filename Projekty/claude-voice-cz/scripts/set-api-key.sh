#!/bin/bash
# Uloží API klíč Anthropicu na server (Cloudflare secret) a ověří, že Claude odpovídá.
# Spusťte  ~/Developer/ClaudeVoiceCZ/scripts/set-api-key.sh  — otevře se okno macOS
# se skrytým políčkem, do kterého klíč vložíte. V Terminálu se klíč nikde neobjeví.
set -uo pipefail
cd "$(dirname "$0")/../server"
URL="https://claude-voice-cz.jindrich-szkandera.workers.dev"
APP_TOKEN="$(cat .app-token)"

echo "Otevírám okno pro zadání klíče…"
INPUT="$(osascript <<'OSA' 2>/dev/null
set dlg to display dialog "Vložte API klíč Anthropicu (⌘V) a klikněte na Uložit.

Klíč se uloží jen na váš server, nikde se nezobrazí." default answer "" with hidden answer with title "Claude Voice CZ" buttons {"Zrušit", "Uložit"} default button "Uložit" cancel button "Zrušit" with icon note
return text returned of dlg
OSA
)"
# Najdeme klíč kdekoli v zadaném textu (ignoruje mezery, neviditelné znaky, okolní text).
ANTHROPIC_KEY="$(printf "%s" "$INPUT" | LC_ALL=C grep -Eo 'sk-ant-[A-Za-z0-9_-]{30,}' | head -1)"
INPUT_LEN=${#INPUT}
unset INPUT
if [ -z "$ANTHROPIC_KEY" ]; then
  echo "❌ V okně nebyl zadán klíč Anthropicu (zadáno $INPUT_LEN znaků)."
  echo "   Zkopírujte klíč v console.anthropic.com (Copy), spusťte skript znovu a vložte ho do okna."
  exit 1
fi
echo "✓ Klíč přijat (${ANTHROPIC_KEY:0:11}…, ${#ANTHROPIC_KEY} znaků)."

echo "Ukládám klíč na server…"
if ! printf "%s" "$ANTHROPIC_KEY" | npx wrangler secret put ANTHROPIC_API_KEY >/dev/null 2>/tmp/cvcz-secret-err; then
  unset ANTHROPIC_KEY
  echo "❌ Uložení selhalo:"; tail -5 /tmp/cvcz-secret-err; rm -f /tmp/cvcz-secret-err
  exit 1
fi
unset ANTHROPIC_KEY
rm -f /tmp/cvcz-secret-err
# Vyčistit schránku, ať klíč nezůstane k omylu vložitelný jinam.
printf "" | pbcopy
echo "✓ Klíč uložen jako šifrovaný secret na serveru. Schránka vymazána."

echo "Ověřuji spojení s Claudem (může trvat pár sekund)…"
# Cloudflare rozšíří nový secret během několika sekund — test až 4× zopakujeme.
for attempt in 1 2 3 4; do
  sleep 5
  RESP="$(curl -sS -N --max-time 90 -X POST "$URL/v1/chat" \
    -H "Authorization: Bearer $APP_TOKEN" -H "Content-Type: application/json" \
    -d '{"messages":[{"role":"user","content":"Odpověz jen jednou krátkou větou: funguje to?"}]}')"
  TEXT="$(echo "$RESP" | sed -n 's/^data: //p' | python3 -c 'import sys,json; ev=[json.loads(l) for l in sys.stdin if l.strip()]; print("".join(e.get("text","") if e.get("type")=="text" else ("[CHYBA] "+e.get("message","") if e.get("type")=="error" else "") for e in ev))')"
  [ -n "$TEXT" ] && [[ "$TEXT" != *"[CHYBA]"* ]] && break
done
if [ -n "$TEXT" ] && [[ "$TEXT" != *"[CHYBA]"* ]]; then
  echo "✓ Claude odpověděl: $TEXT"
else
  echo "⚠️  Test se nezdařil: ${TEXT:-$RESP}"
  echo "   Pokud Anthropic klíč odmítl, nejde o API klíč pro Claude API."
  echo "   Napište to Claudovi v Claude Code — podívá se do logu serveru."
fi
