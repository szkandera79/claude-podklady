#!/bin/sh
# Build PDF letáku z letak.html (spouštět ze složky letáku)
cd "$(dirname "$0")"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$PWD/REO_HEATING_Letak_RH030-RH060.pdf" --virtual-time-budget=8000 "file://$PWD/letak.html" 2>/dev/null
