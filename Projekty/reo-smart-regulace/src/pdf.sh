#!/bin/zsh
# PDF standardu (A4) přes Chrome headless. Spuštění: zsh reo-smart-regulace/src/pdf.sh (po build_metodika.py)
cd "${0:A:h}/.."
OUT="REO-R290-Smart_instalacni-standard_v1.0.pdf"
TMP="$PWD/.print-tmp.html"
sed 's/<details>/<details open>/g' index.html > "$TMP"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --no-pdf-header-footer \
  --virtual-time-budget=8000 --run-all-compositor-stages-before-draw \
  --print-to-pdf="$PWD/$OUT" "file://$TMP" 2>/dev/null
rm -f "$TMP"
ls -la "$OUT"
