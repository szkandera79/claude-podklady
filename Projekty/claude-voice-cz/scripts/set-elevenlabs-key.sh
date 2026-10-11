#!/bin/bash
# Uloží na server API klíč ElevenLabs (hlas + rozpoznávání řeči) a ověří ho.
# Spuštění:  ~/Developer/ClaudeVoiceCZ/scripts/set-elevenlabs-key.sh  — otevře okno pro vložení klíče.
set -uo pipefail
cd "$(dirname "$0")/../server"

INPUT="$(osascript <<'OSA' 2>/dev/null
set dlg to display dialog "Vložte API klíč ElevenLabs (⌘V) a klikněte na Uložit.

Klíč se uloží jen na váš server, nikde se nezobrazí." default answer "" with hidden answer with title "Claude Voice CZ – ElevenLabs" buttons {"Zrušit", "Uložit"} default button "Uložit" cancel button "Zrušit" with icon note
return text returned of dlg
OSA
)"
KEY="$(printf "%s" "$INPUT" | LC_ALL=C grep -Eo '(sk_)?[A-Za-z0-9]{32,}' | head -1)"
INPUT_LEN=${#INPUT}
unset INPUT
if [ -z "$KEY" ]; then
  echo "❌ V okně nebyl klíč ElevenLabs (zadáno $INPUT_LEN znaků). Spusťte skript znovu."; exit 1
fi
echo "✓ Klíč přijat (${KEY:0:5}…, ${#KEY} znaků). Ověřuji u ElevenLabs…"
# Tarif a kredit (pokud má klíč oprávnění user_read)
curl -s -H "xi-api-key: $KEY" https://api.elevenlabs.io/v1/user/subscription | python3 -c 'import sys,json
try:
    d=json.load(sys.stdin); print("ℹ️  Tarif:", d.get("tier"), "| využito znaků:", d.get("character_count"), "z", d.get("character_limit"))
except Exception: pass'
# Najdeme hlasy, které účet smí přes API použít: zkusíme předinstalované hlasy, dokud jeden neprojde.
VOICES="$(curl -s -H "xi-api-key: $KEY" "https://api.elevenlabs.io/v2/voices?page_size=100" | python3 -c 'import sys,json
try:
    d=json.load(sys.stdin)
    for v in d.get("voices",[]):
        print(v.get("voice_id"), v.get("category"), v.get("name"), sep="\t")
except Exception: pass')"
echo "ℹ️  Hlasů v účtu: $(printf "%s" "$VOICES" | grep -c . )"
OK_VOICE=""
while IFS=$'\t' read -r VID CAT NAME; do
  [ -z "$VID" ] && continue
  CODE="$(curl -s -o /tmp/cvcz-el.out -w "%{http_code}" -X POST -H "xi-api-key: $KEY" -H "Content-Type: application/json" \
    -d '{"text":"Dobrý den, tady Claude.","model_id":"eleven_flash_v2_5"}' \
    "https://api.elevenlabs.io/v1/text-to-speech/$VID?output_format=mp3_22050_32")"
  if [ "$CODE" = "200" ]; then OK_VOICE="$VID"; echo "✓ Hlas „$NAME“ ($CAT) funguje."; break; fi
  echo "   – „$NAME“ ($CAT): HTTP $CODE"
done <<< "$VOICES"
rm -f /tmp/cvcz-el.out
if [ -z "$OK_VOICE" ]; then
  unset KEY
  echo "❌ Žádný hlas není s tímto tarifem přes API dostupný (bezplatný tarif hlasy přes API neumožňuje)."
  echo "   Řešení: placený tarif ElevenLabs (Starter / Creator), pak spusťte skript znovu."
  exit 1
fi
printf "%s" "$KEY" | npx wrangler secret put ELEVENLABS_API_KEY >/dev/null 2>&1 || { unset KEY; echo "❌ Uložení na server selhalo."; exit 1; }
unset KEY
printf "" | pbcopy
echo "✓ Klíč uložen jako šifrovaný secret na serveru. Schránka vymazána."
echo "ELEVENLABS_VOICE_OK=$OK_VOICE"
