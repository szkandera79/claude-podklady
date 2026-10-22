#!/bin/sh
# SVG → PNG (průhledné pozadí, 3000 px šířka) přes Chrome headless
cd "$(dirname "$0")"
python3 build_logo.py
for v in logo-reo-heating logo-reo-heating-white; do
  printf '<html><body style="margin:0;background:transparent"><img src="%s.svg" style="width:3000px;display:block"></body></html>' "$v" > _r.html
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --hide-scrollbars \
    --default-background-color=00000000 --window-size=3000,1148 --screenshot="$PWD/$v.png" "file://$PWD/_r.html" 2>/dev/null
done
rm -f _r.html
# oříznout na obsah s okrajem 40 px
python3 -c "
from PIL import Image
for f in ['logo-reo-heating.png','logo-reo-heating-white.png']:
    im=Image.open(f); x0,y0,x1,y1=im.getbbox(); im.crop((x0-40,y0-40,x1+40,y1+40)).save(f,optimize=True)"
