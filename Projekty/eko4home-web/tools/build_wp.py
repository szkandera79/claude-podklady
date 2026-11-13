"""Sestaví balíček pro WordPress (plugin Code Snippets): dist-wp/obrazky + dist-wp/eko4home-snippet.php.
Spouštět z kořene repa:  python3 eko4home-web/tools/build_wp.py
"""
import re, shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'dist-wp'
html = (ROOT / 'index.html').read_text(encoding='utf-8')

# 1) loga jako inline SVG (WordPress neumí nahrát .svg do Médií)
def svg(name, cls):
    s = (ROOT / 'assets/img' / name).read_text(encoding='utf-8')
    s = re.sub(r'<\?xml[^>]*\?>\s*', '', s)
    s = re.sub(r'\s(id|data-name)="[^"]*"', '', s, count=2)
    s = re.sub(r'\swidth="[^"]*"\s+height="[^"]*"', '', s, count=1)
    s = s.replace('<svg ', f'<svg class="{cls}" ', 1)
    return s
html = html.replace('<img src="assets/img/logo-reoheating.svg" alt="REO HEATING">', svg('logo-reoheating.svg', 'logo-svg'))
html = html.replace('<img src="assets/img/logo-reoheating-light.svg" alt="REO HEATING">', svg('logo-reoheating-light.svg', 'logo-svg'))
html = html.replace('.logo img{height:63px;width:auto;max-width:none}', '.logo img,.logo-svg{height:63px;width:auto;max-width:none}')
html = html.replace('footer .logo img{height:63px}', 'footer .logo img,footer .logo-svg{height:63px}')
html = html.replace('  .logo img{height:52px}', '  .logo img,.logo .logo-svg{height:52px}')
assert 'logo-reoheating' not in html, 'logo nenahrazeno'

# 2) formulář → POST na úvodní stránku (zpracuje snippet přes wp_mail)
old_form = '<form id="poptavka" method="post" action="odeslat.php" novalidate>'
assert old_form in html, 'formulář nenalezen'
html = html.replace(old_form, '<form id="poptavka" method="post" action="/" novalidate><input type="hidden" name="e4h_form" value="1">')
for old, new in []:  # pole už mají name v index.html
    pass
for old, new in [('<label>Jméno a příjmení<input required>', '<label>Jméno a příjmení<input name="jmeno" required>'),
                 ('<label>Telefon<input type="tel" required>', '<label>Telefon<input type="tel" name="telefon" required>'),
                 ('<label class="full">E-mail<input type="email">', '<label class="full">E-mail<input type="email" name="email">'),
                 ('<label class="full">Adresa realizace<input>', '<label class="full">Adresa realizace<input name="adresa">'),
                 ('<select>', '<select name="zajem">'),
                 ('<textarea rows="4">', '<textarea name="zprava" rows="4">')]:
    pass

# 3) obrázky → složka pro nahrání do Médií
OUT.mkdir(exist_ok=True)
img_dir = OUT / 'obrazky'; shutil.rmtree(img_dir, ignore_errors=True); img_dir.mkdir()
used = sorted(set(re.findall(r'assets/img/([A-Za-z0-9._-]+)', html)))
for f in used: shutil.copy(ROOT / 'assets/img' / f, img_dir / f)
html = html.replace('assets/img/', '%%IMG%%')
assert "\nE4H" not in html

php = r"""<?php
/**
 * Eko4Home – nová úvodní stránka (statické HTML místo šablony Divi) + odeslání formuláře s antispamem.
 * Code Snippets → Přidat nový → PHP → vložit celý tento soubor → „Spustit všude“ → Uložit a aktivovat.
 * Vypnutí = deaktivovat snippet (vrátí původní WordPress úvod).
 */
__LIB__
add_action('template_redirect', function () {
    if (is_admin() || !is_front_page()) return;

    // Složka, kam se v Médiích nahrály obrázky (rok/měsíc nahrání). Při jiném měsíci upravit.
    $img = '/wp-content/uploads/__ROK__/__MESIC__/';

    if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['e4h_form'])) {
        nocache_headers();
        $r = e4h_check(wp_unslash($_POST), $_SERVER['REMOTE_ADDR'] ?? '');
        if (!$r['ok']) wp_send_json(['ok' => false, 'error' => $r['error']], 400);
        if (!$r['spam']) {
            $pole = $r['pole'];
            $headers = $pole['E-mail'] !== '' ? ['Reply-To: ' . $pole['Jméno a příjmení'] . ' <' . $pole['E-mail'] . '>'] : [];
            if (!wp_mail('info@reoheating.cz', e4h_predmet($pole), e4h_telo($pole), $headers))
                wp_send_json(['ok' => false, 'error' => 'E-mail se nepodařilo odeslat, zavolejte nám prosím +420 774 872 467.'], 500);
            if ($pole['E-mail'] !== '')
                wp_mail($pole['E-mail'], 'Děkujeme za poptávku – REO HEATING', "Dobrý den,\n\nděkujeme za vaši poptávku, co nejdříve se vám ozveme.\n\nS pozdravem\nREO HEATING\ninfo@reoheating.cz | +420 774 872 467\n", ['Reply-To: info@reoheating.cz']);
        }
        wp_send_json(['ok' => true]);
    }

    nocache_headers();
    header('Content-Type: text/html; charset=utf-8');
    $html = <<<'E4H'
__HTML__
E4H;
    echo str_replace('%%IMG%%', $img, $html);
    exit;
});
"""
from datetime import date
d = date.today()
lib = (ROOT / 'antispam-lib.php').read_text(encoding='utf-8').replace('<?php', '', 1).strip()
php = php.replace('__LIB__', lib).replace('__ROK__', f'{d.year}').replace('__MESIC__', f'{d.month:02d}').replace('__HTML__', html)
(OUT / 'eko4home-snippet.php').write_text(php, encoding='utf-8')
print('obrázků:', len(used), '| snippet:', round(len(php.encode())/1024), 'kB |', OUT)
