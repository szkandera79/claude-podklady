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
    s = re.sub(r'\swidth="[^"]*"\s+height="[^"]*"', f' class="{cls}" role="img" aria-label="REO HEATING"', s, count=1)
    return s
html = html.replace('<img src="assets/img/logo-reoheating.svg" alt="REO HEATING">', svg('logo-reoheating.svg', 'logo-svg'))
html = html.replace('<img src="assets/img/logo-reoheating-light.svg" alt="REO HEATING">', svg('logo-reoheating-light.svg', 'logo-svg'))
html = html.replace('.logo img{height:63px;width:auto;max-width:none}', '.logo img,.logo-svg{height:63px;width:auto;max-width:none}')
html = html.replace('footer .logo img{height:63px}', 'footer .logo img,footer .logo-svg{height:63px}')
html = html.replace('  .logo img{height:52px}', '  .logo img,.logo .logo-svg{height:52px}')
assert 'logo-reoheating' not in html, 'logo nenahrazeno'

# 2) formulář → POST na úvodní stránku (zpracuje snippet přes wp_mail)
form_old = re.search(r'<form onsubmit="[^"]*">', html).group(0)
html = html.replace(form_old, '<form method="post" action="/#kontakt"><input type="hidden" name="e4h_form" value="1"><input type="text" name="web" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true">')
for old, new in [('<label>Jméno a příjmení<input required>', '<label>Jméno a příjmení<input name="jmeno" required>'),
                 ('<label>Telefon<input type="tel" required>', '<label>Telefon<input type="tel" name="telefon" required>'),
                 ('<label class="full">E-mail<input type="email">', '<label class="full">E-mail<input type="email" name="email">'),
                 ('<label class="full">Adresa realizace<input>', '<label class="full">Adresa realizace<input name="adresa">'),
                 ('<select>', '<select name="zajem">'),
                 ('<textarea rows="4">', '<textarea name="zprava" rows="4">')]:
    assert old in html, old; html = html.replace(old, new, 1)
html = html.replace('</body>', '<script>if(location.search.indexOf("odeslano=1")>-1){var b=document.querySelector("form button");if(b){b.textContent="Děkujeme, ozveme se ✓";b.disabled=true;}}</script>\n</body>')

# 3) obrázky → složka pro nahrání do Médií
OUT.mkdir(exist_ok=True)
img_dir = OUT / 'obrazky'; shutil.rmtree(img_dir, ignore_errors=True); img_dir.mkdir()
used = sorted(set(re.findall(r'assets/img/([A-Za-z0-9._-]+)', html)))
for f in used: shutil.copy(ROOT / 'assets/img' / f, img_dir / f)
html = html.replace('assets/img/', '%%IMG%%')
assert "\nE4H" not in html

php = r"""<?php
/**
 * Eko4Home – nová úvodní stránka (statické HTML místo šablony Divi) + odeslání formuláře.
 * Code Snippets → Přidat nový → PHP → vložit celý tento soubor → „Spustit všude“ → Uložit a aktivovat.
 * Vypnutí = deaktivovat snippet (vrátí původní WordPress úvod).
 */
add_action('template_redirect', function () {
    if (is_admin() || !is_front_page()) return;

    // Složka, kam se v Médiích nahrály obrázky (rok/měsíc nahrání). Při jiném měsíci upravit.
    $img = '/wp-content/uploads/__ROK__/__MESIC__/';

    if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['e4h_form'])) {
        if (empty($_POST['web'])) {                        // honeypot proti spamu
            $t = function ($k) { return sanitize_text_field(wp_unslash($_POST[$k] ?? '')); };
            $email = sanitize_email(wp_unslash($_POST['email'] ?? ''));
            $body  = "Jméno: " . $t('jmeno') . "\nTelefon: " . $t('telefon') . "\nE-mail: " . $email
                   . "\nAdresa realizace: " . $t('adresa') . "\nZájem: " . $t('zajem')
                   . "\n\nZpráva:\n" . sanitize_textarea_field(wp_unslash($_POST['zprava'] ?? ''));
            $headers = $email ? ['Reply-To: ' . $email] : [];
            wp_mail('info@reoheating.cz', 'Poptávka z webu eko4home.cz – ' . $t('jmeno'), $body, $headers);
        }
        wp_safe_redirect(home_url('/?odeslano=1#kontakt'));
        exit;
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
php = php.replace('__ROK__', f'{d.year}').replace('__MESIC__', f'{d.month:02d}').replace('__HTML__', html)
(OUT / 'eko4home-snippet.php').write_text(php, encoding='utf-8')
print('obrázků:', len(used), '| snippet:', round(len(php.encode())/1024), 'kB |', OUT)
