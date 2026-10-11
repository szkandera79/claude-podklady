# reoheating-web

Redesign webu **reoheating.cz** — jednostránkový web (landing page) značky **REO HEATING**
(český výrobce tepelných čerpadel vzduch–voda; provozovatel Riva Trade s.r.o., Třinec).

Design je postaven podle vzoru <https://klimatizacekasparek.vercel.app> — bílo-zelený,
vzdušný, se stejným pořadím a typy sekcí. Obsah, produkty i fotografie jsou REO HEATING.

## Struktura
- `index.html` — celý web (interní CSS + vanilla JS, bez frameworků)
- `odeslat.php` — odeslání poptávky na info@reoheating.cz (PHP `mail()`, honeypot)
- `ochrana-udaju.html` — GDPR
- `favicon.svg`, `robots.txt`, `sitemap.xml`
- `assets/images/` — `hero.jpg` + `realizace/` (fotky z katalogu realizací REO HEATING)

## Náhled
```
python3 -m http.server 8123      # → http://localhost:8123
```

## Build pro hosting (plochý `dist/`)
Web4u / net2ftp zplošťuje strukturu složek při rozbalení ZIPu, proto se nahrává `dist/`:
```
rm -rf dist && mkdir dist
sed -e 's#assets/images/realizace/##g' -e 's#assets/images/##g' index.html > dist/index.html
cp odeslat.php favicon.svg ochrana-udaju.html robots.txt sitemap.xml dist/
cp assets/images/*.jpg assets/images/*.png dist/
cp assets/images/realizace/*.jpg dist/
```

## Zdroje obsahu
- Texty a parametry produktů: reoheating.cz (domácí / průmyslová čerpadla, mobilní kotelna, dotace)
- Realizace a fotografie: `~/Claude/REO-katalog-instalaci` (Katalog realizací REO HEATING)
- Logo: `~/Claude/REO-katalog-instalaci/logo-reo*.png`
