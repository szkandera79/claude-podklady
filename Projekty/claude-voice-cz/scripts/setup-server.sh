#!/bin/bash
# Claude Voice CZ — instalace serveru na Cloudflare Workers.
# Spusťte v Terminálu:  ~/Developer/ClaudeVoiceCZ/scripts/setup-server.sh
#
# Co skript udělá:
#  1. přihlásí vás k Cloudflare (otevře prohlížeč),
#  2. vytvoří úložiště pro počítání denní spotřeby,
#  3. nasadí server,
#  4. vygeneruje přístupový token aplikace a uloží ho na server,
#  5. požádá vás o API klíč Anthropicu — zadáváte ho JEN sem do Terminálu (skrytě)
#     — a ověří, že Claude odpovídá,
#  6. zapíše adresu serveru a token do konfigurace aplikace pro iPhone.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SERVER="$ROOT/server"
SECRETS="$ROOT/ios/Config/Secrets.xcconfig"
cd "$SERVER"

say() { printf "\n\033[1;34m▶ %s\033[0m\n" "$*"; }
ok() { printf "\033[1;32m✓ %s\033[0m\n" "$*"; }

say "1/6 Přihlášení k Cloudflare"
if npx wrangler whoami 2>/dev/null | grep -q "You are logged in"; then
  ok "Už jste přihlášen(a)."
else
  npx wrangler login
fi

say "2/6 Úložiště pro denní limit spotřeby"
if grep -q 'id = "DOPLNIT_PRI_INSTALACI"' wrangler.toml; then
  OUT="$(npx wrangler kv namespace create USAGE 2>&1)" || { echo "$OUT"; exit 1; }
  KV_ID="$(echo "$OUT" | grep -Eo '[0-9a-f]{32}' | head -1)"
  [ -n "$KV_ID" ] || { echo "$OUT"; echo "Nepodařilo se zjistit ID úložiště."; exit 1; }
  sed -i '' "s/id = \"DOPLNIT_PRI_INSTALACI\"/id = \"$KV_ID\"/" wrangler.toml
  ok "Úložiště vytvořeno ($KV_ID)."
else
  ok "Úložiště už existuje."
fi

say "3/6 Nasazení serveru"
DEPLOY_OUT="$(npx wrangler deploy 2>&1)" || {
  if echo "$DEPLOY_OUT" | grep -q "workers.dev subdomain"; then
    LINK="$(echo "$DEPLOY_OUT" | grep -Eo 'https://dash\.cloudflare\.com/[^ ]*onboarding' | head -1)"
    echo "⚠️  Účet Cloudflare ještě nemá zvolenou subdoménu workers.dev."
    echo "   Otevřete: ${LINK:-https://dash.cloudflare.com → Workers & Pages}"
    echo "   zvolte krátký název, potvrďte a spusťte tento skript znovu."
  else
    echo "$DEPLOY_OUT"
  fi
  exit 1
}
URL="$(echo "$DEPLOY_OUT" | grep -Eo 'https://[a-zA-Z0-9.-]+\.workers\.dev' | head -1)"
[ -n "$URL" ] || { echo "$DEPLOY_OUT"; echo "Nepodařilo se zjistit adresu serveru."; exit 1; }
ok "Server běží na $URL (bez tajných údajů zatím všechny požadavky odmítá)"

say "4/6 Přístupový token aplikace"
if [ ! -s .app-token ]; then
  openssl rand -base64 36 | tr -d '/+=\n' > .app-token
  chmod 600 .app-token
fi
APP_TOKEN="$(cat .app-token)"
printf "%s" "$APP_TOKEN" | npx wrangler secret put APP_TOKEN >/dev/null
ok "Token vygenerován a uložen na server."

say "5/6 API klíč Anthropicu"
echo "Klíč najdete na https://console.anthropic.com → API Keys."
echo "Vložte ho a stiskněte Enter (při psaní se nezobrazuje):"
read -r -s ANTHROPIC_KEY
echo
[ -n "$ANTHROPIC_KEY" ] || { echo "Klíč je prázdný, končím."; exit 1; }
printf "%s" "$ANTHROPIC_KEY" | npx wrangler secret put ANTHROPIC_API_KEY >/dev/null
unset ANTHROPIC_KEY
ok "Klíč uložen jako šifrovaný secret na serveru (v počítači ani v projektu nezůstal)."

echo "Ověřuji spojení s Claudem…"
sleep 3
RESP="$(curl -sS -N --max-time 60 -X POST "$URL/v1/chat" \
  -H "Authorization: Bearer $APP_TOKEN" -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Odpověz jen jednou krátkou větou: funguje to?"}]}' || true)"
TEXT="$(echo "$RESP" | sed -n 's/^data: //p' | python3 -c 'import sys,json
out=""
for l in sys.stdin:
    try: e=json.loads(l)
    except Exception: continue
    if e.get("type")=="text": out+=e["text"]
    if e.get("type")=="error": out+="[CHYBA] "+e.get("message","")
print(out)')"
if [ -n "$TEXT" ] && [[ "$TEXT" != *"[CHYBA]"* ]]; then
  ok "Claude odpověděl: $TEXT"
else
  echo "⚠️  Test se nezdařil. Odpověď serveru:"; echo "$RESP" | head -20
  echo "Zkontrolujte API klíč a kredit v Anthropic Console. Pro detail: cd server && npx wrangler tail"
fi

say "6/6 Konfigurace aplikace pro iPhone"
TEAM="$(defaults read com.apple.dt.Xcode IDEProvisioningTeams 2>/dev/null | grep -Eo 'teamID = [A-Z0-9]{10}' | head -1 | cut -d' ' -f3 || true)"
SUFFIX="$(id -un | tr -cd 'a-zA-Z0-9' | tr 'A-Z' 'a-z')"
{
  echo "// Vygenerováno skriptem setup-server.sh — NENÍ v gitu."
  echo "CV_SERVER_URL = ${URL/https:\/\//https:/\$()/}"
  echo "CV_APP_TOKEN = $APP_TOKEN"
  echo "CV_BUNDLE_SUFFIX = $SUFFIX"
  [ -n "$TEAM" ] && echo "DEVELOPMENT_TEAM = $TEAM"
} > "$SECRETS"
chmod 600 "$SECRETS"
ok "Zapsáno do ios/Config/Secrets.xcconfig${TEAM:+ (tým $TEAM)}"

printf "\n\033[1;32mHotovo.\033[0m Napište Claudovi do Claude Code, že instalace serveru proběhla.\n"
