#!/bin/zsh
# SVG → PNG (2800 px) přes Chrome headless. Spuštění: zsh reo-smart-regulace/src/render.sh
cd "${0:A:h}/.."
for f in schema-*.svg; do
  h=$(grep -o 'viewBox="0 0 [0-9]* [0-9]*"' $f | head -1 | awk '{print $4}' | tr -d '"')
  tmp=$(mktemp -t svgwrap).html
  echo "<html><body style='margin:0'><img src='file://$PWD/$f' style='width:1400px;height:${h}px;display:block'></body></html>" > $tmp
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --hide-scrollbars \
    --force-device-scale-factor=2 --window-size=1400,$h --screenshot="$PWD/${f:r}.png" "file://$tmp" >/dev/null 2>&1
  rm -f $tmp
done
ls -la *.png
