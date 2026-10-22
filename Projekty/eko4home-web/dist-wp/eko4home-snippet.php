<?php
/**
 * Eko4Home – nová úvodní stránka (statické HTML místo šablony Divi) + odeslání formuláře.
 * Code Snippets → Přidat nový → PHP → vložit celý tento soubor → „Spustit všude“ → Uložit a aktivovat.
 * Vypnutí = deaktivovat snippet (vrátí původní WordPress úvod).
 */
add_action('template_redirect', function () {
    if (is_admin() || !is_front_page()) return;

    // Složka, kam se v Médiích nahrály obrázky (rok/měsíc nahrání). Při jiném měsíci upravit.
    $img = '/wp-content/uploads/2026/10/';

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
<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Eko4Home – tepelná čerpadla a fotovoltaika | Třinec</title>
<meta name="description" content="Tepelná čerpadla REO HEATING R290, akumulační nádrže a fotovoltaika na klíč pro rodinné domy, bytové domy i komerční objekty. Sídlo v Třinci, realizace po celé České republice a na Slovensku.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Kalam:wght@400;700&display=swap" rel="stylesheet">
<style>
:root{
  --brand:#34a263; --brand-dark:#1f4d33; --brand-light:#e9f6ee; --brand-mid:#2b8a52; --yellow:#f5b800;
  --amber:#f5b800; --ink:#2d2f2e; --muted:#5f6662; --line:#dfe8e2; --bg:#ffffff; --bg-soft:#f6f9f7;
  --radius:20px; --shadow:0 10px 30px rgba(18,56,33,.08);
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:Inter,system-ui,sans-serif;color:var(--ink);background:var(--bg);line-height:1.6;-webkit-font-smoothing:antialiased}
img{max-width:100%;display:block}
a{color:inherit;text-decoration:none}
.wrap{max-width:1200px;margin:0 auto;padding:0 24px}
.hand{font-family:Kalam,cursive;color:var(--brand);font-weight:700}
.eyebrow{display:inline-block;font-size:.8rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--brand);background:var(--brand-light);padding:6px 14px;border-radius:999px;margin-bottom:16px}
h1,h2,h3{line-height:1.15;letter-spacing:-.02em}
h2{font-size:clamp(1.9rem,3.6vw,2.8rem);font-weight:800;margin-bottom:14px}
.lead{color:var(--muted);font-size:1.08rem;max-width:640px}
section{padding:96px 0}
.center{text-align:center}.center .lead{margin:0 auto}
.btn{display:inline-flex;align-items:center;gap:8px;font-weight:600;padding:14px 26px;border-radius:999px;transition:.2s;border:2px solid transparent;cursor:pointer;font-size:1rem;white-space:nowrap}
.btn-primary{background:var(--brand);color:#fff}.btn-primary:hover{background:var(--brand-mid)}
.btn-ghost{border-color:var(--brand);color:var(--brand)}.btn-ghost:hover{background:var(--brand-light)}
.btn-amber{background:var(--amber);color:var(--brand-dark)}.btn-amber:hover{filter:brightness(.95)}

/* header */
header{position:sticky;top:0;z-index:50;background:rgba(255,255,255,.92);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.nav{display:flex;align-items:center;justify-content:space-between;height:76px;gap:20px}
.logo{display:inline-flex;flex-direction:column;align-items:center;line-height:1;gap:2px}
.logo{flex:0 0 auto}
.logo img,.logo-svg{height:63px;width:auto;max-width:none}
.logo span{font-weight:800;font-size:1.5rem;letter-spacing:-.03em;color:#232323}
.logo-light span{color:#fff}
.menu{display:flex;gap:20px;font-weight:500;font-size:.95rem;white-space:nowrap}
.menu a:hover{color:var(--brand)}
.nav-right{display:flex;align-items:center;gap:18px}
.phone{font-weight:700;color:var(--brand-dark);white-space:nowrap}
.burger{display:none;background:none;border:0;font-size:1.6rem;cursor:pointer;color:var(--brand-dark)}

/* hero */
.hero{position:relative;overflow:hidden;color:#fff;min-height:min(80vh,720px);display:flex;align-items:center;padding:72px 0;background:#1d2a22 url(%%IMG%%hero-blur.webp) left center/cover}
.hero::before{content:"";position:absolute;right:0;bottom:0;width:min(62%,980px);aspect-ratio:1186/838;background:url(%%IMG%%hero-schema.webp) center/cover no-repeat;-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 16%),linear-gradient(180deg,transparent 0,#000 14%);-webkit-mask-composite:source-in;mask-image:linear-gradient(90deg,transparent 0,#000 16%),linear-gradient(180deg,transparent 0,#000 14%);mask-composite:intersect}
.hero::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(14,36,24,.92) 0%,rgba(14,36,24,.78) 32%,rgba(14,36,24,.2) 46%,rgba(14,36,24,0) 55%)}
.hero .wrap{position:relative;z-index:2;max-width:1400px;width:100%}
.hero-grid{display:block}
.hero-grid > div{max-width:560px}
.hero h1{color:#fff;text-shadow:0 2px 18px rgba(0,0,0,.35)}
.hero h1 .hand{color:#8fd9a8}
.hero .hero-grid p{color:#e3ece6}
.hero .eyebrow{background:rgba(255,255,255,.14);color:#fff;backdrop-filter:blur(4px)}
.hero .btn-ghost{border-color:#fff;color:#fff}.hero .btn-ghost:hover{background:rgba(255,255,255,.12)}
.hero .stat strong{color:#fff}.hero .stat span{color:#c9d8ce}
.hero h1{font-size:clamp(2.3rem,4.2vw,3.6rem);font-weight:800;margin-bottom:20px}
.hero h1 .yellow{color:var(--yellow)}
.hero h1::after{content:"";display:block;width:72px;height:4px;border-radius:2px;background:var(--yellow);margin-top:22px}
.hero h1 .hand{font-size:1.1em;display:inline-block;transform:rotate(-2deg)}
.hero p{color:var(--muted);font-size:1.12rem;margin-bottom:30px;max-width:540px}
.hero-cta{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:40px}
.stats{display:flex;gap:26px;flex-wrap:wrap}
.stat strong{display:block;font-size:1.6rem;font-weight:800;color:var(--brand-dark)}
.stat span{color:var(--muted);font-size:.9rem}
.hero-img{position:relative}
.hero-unit{border-radius:28px;box-shadow:var(--shadow);width:100%;background:radial-gradient(circle at 50% 40%,#fff 0,var(--brand-light) 50%,#cfe6d7 100%);display:grid;grid-template-columns:1.25fr 1fr;gap:12px;align-items:end;padding:56px 22px 22px}
.hu{display:flex;flex-direction:column;align-items:center;gap:14px}
.hu img{height:300px;width:auto;max-width:100%;object-fit:contain;filter:drop-shadow(0 18px 18px rgba(18,56,33,.22))}
.hu-smart img{height:200px}
.hu-pair{display:flex;align-items:flex-end;justify-content:center}
.hu-pair img{height:290px}
.hu-pair .hu-small{height:175px;margin-left:-34px;position:relative}
.hu figcaption{background:#fff;border-radius:16px;padding:12px 12px;width:100%;display:flex;flex-wrap:wrap;gap:6px 8px;justify-content:center;box-shadow:0 4px 14px rgba(18,56,33,.08)}
.hu figcaption b{width:100%;text-align:center;color:var(--brand-dark);font-size:.92rem}
.hu figcaption .scop-h{color:var(--muted);font-weight:700;letter-spacing:.02em;margin-top:-2px}
.hu figcaption small{width:100%;text-align:center;color:var(--brand);font-weight:600;font-size:.76rem}
.scop{background:var(--brand-light);border-radius:10px;padding:5px 9px;font-weight:800;color:var(--brand-dark);font-size:1.02rem;line-height:1.15;display:inline-flex;align-items:center;gap:7px;text-align:left}
.scop svg{width:24px;height:24px;flex:0 0 24px}
.scop-35 svg{color:#e0662b}.scop-55 svg{color:#c24b2a}
.scop i{display:block;font-style:normal;font-weight:600;font-size:.64rem;color:var(--muted);letter-spacing:.02em}
.mscop{display:flex;flex-direction:column;gap:6px;margin-top:8px}
.mscop::before{content:"SCOP · průměrný roční topný faktor";font-size:.68rem;font-weight:700;color:var(--muted);letter-spacing:.06em}
.mscop .scop{font-size:.95rem;padding:5px 7px;gap:6px}.mscop .scop svg{width:20px;height:20px;flex-basis:20px}
.scop-legend{display:flex;flex-wrap:wrap;gap:8px 18px;background:var(--bg-soft);border-left:4px solid var(--yellow);border-radius:10px;padding:12px 14px;font-size:.85rem;color:var(--muted);margin:4px 0 16px}
.scop-legend b{color:var(--ink)}
.scop-legend span{display:inline-flex;align-items:center;gap:6px}
.scop-legend svg{width:20px;height:20px}
.badge{position:absolute;z-index:2;background:#fff;border-radius:16px;padding:14px 18px;box-shadow:var(--shadow);display:flex;gap:12px;align-items:center;font-size:.9rem}
.badge .ic{width:42px;height:42px;border-radius:12px;background:var(--brand-light);display:grid;place-items:center;font-size:1.3rem}
.badge b{display:block;color:var(--brand-dark)}
.badge.b2{right:-14px;top:-18px}

/* sun band */
.sunband{background:linear-gradient(135deg,#fffaf0,#fff 55%,var(--brand-light));padding:80px 0}
.sun-grid{display:grid;grid-template-columns:1fr 1.2fr;gap:56px;align-items:center}
.sun-img{position:relative;display:grid;place-items:center}
.sun-img img{max-height:560px;width:100%;object-fit:contain;filter:drop-shadow(0 20px 22px rgba(18,56,33,.2))}
.sun-img .sun{position:absolute;top:-40px;right:-10px;font-size:4.2rem;filter:drop-shadow(0 0 22px rgba(252,187,0,.7))}
.sun-list{list-style:none;display:grid;gap:12px;margin:22px 0 28px}
.sun-list li{padding-left:30px;position:relative;color:var(--muted)}
.sun-list li::before{content:"✓";position:absolute;left:0;top:0;width:22px;height:22px;border-radius:50%;background:var(--brand);color:#fff;font-size:.75rem;display:grid;place-items:center;font-weight:800}
.sun-list b{color:var(--ink)}
.hl-box{display:block;margin-top:8px;background:var(--yellow);color:var(--ink);font-weight:700;padding:10px 14px;border-radius:12px;box-shadow:0 6px 16px rgba(245,184,0,.35);font-size:1rem}
.hl-box strong{font-weight:800}
mark.hl{background:linear-gradient(transparent 45%,rgba(245,184,0,.55) 45%);color:var(--ink);font-weight:700;padding:0 2px}
.hero-photo{position:relative;border-radius:28px;overflow:hidden;box-shadow:var(--shadow)}
.hero-photo img{width:100%;aspect-ratio:1186/838;object-fit:cover;display:block}
.hero-cap{position:absolute;left:16px;top:16px;background:rgba(255,255,255,.94);backdrop-filter:blur(6px);border-radius:16px;padding:12px 14px;display:flex;flex-direction:column;gap:6px;box-shadow:0 6px 18px rgba(0,0,0,.15)}
.hero-cap b{color:var(--brand-dark);font-size:.92rem}
.hero-cap .scop-h{font-size:.72rem;color:var(--muted);font-weight:700}
.hero-cap-row{display:flex;gap:8px}
.sun-cap{margin-top:14px;background:#fff;border-radius:999px;padding:6px 14px;font-size:.85rem;font-weight:700;color:var(--brand-dark);box-shadow:0 4px 14px rgba(18,56,33,.1)}
.new-tag{display:inline-block;background:var(--yellow);color:var(--ink);font-weight:800;font-size:.72em;letter-spacing:.06em;text-transform:uppercase;border-radius:999px;padding:2px 9px;margin-right:8px;vertical-align:1px}
.nerez{position:absolute;left:12px;top:12px;background:var(--brand);color:#fff;font-weight:800;font-size:.8rem;letter-spacing:.03em;padding:5px 11px;border-radius:999px;box-shadow:0 4px 12px rgba(52,162,99,.35)}
.nerez-band{display:flex;gap:14px;align-items:center;background:#fff;border:2px solid var(--brand);border-radius:20px;padding:16px 20px;margin-bottom:22px;box-shadow:var(--shadow)}
.nerez-band b{display:block;font-size:1.1rem;color:var(--brand-dark)}
.nerez-band span{color:var(--muted);font-size:.93rem}
.nerez-ic{flex:0 0 44px;height:44px;border-radius:50%;background:var(--brand);color:#fff;display:grid;place-items:center;font-weight:800;font-size:1.3rem}
/* why */
.why-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:22px;margin-top:48px}
.card{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:28px;transition:.2s}
.card:hover{box-shadow:var(--shadow);transform:translateY(-3px)}
.card .ic{width:52px;height:52px;border-radius:14px;background:var(--brand-light);display:grid;place-items:center;font-size:1.5rem;margin-bottom:18px}
.card h3{font-size:1.15rem;margin-bottom:8px}
.card p{color:var(--muted);font-size:.95rem}

/* segments */
.segs{display:grid;grid-template-columns:repeat(3,1fr);gap:22px;margin-top:44px}
.seg{background:#fff;border:1px solid var(--line);border-radius:24px;padding:30px;display:flex;flex-direction:column}
.seg.featured{background:var(--brand);color:#fff;border-color:var(--brand)}
.seg .ic{width:56px;height:56px;border-radius:16px;background:var(--brand-light);display:grid;place-items:center;font-size:1.6rem;margin-bottom:18px}
.seg.featured .ic{background:rgba(255,255,255,.15)}
.seg h3{font-size:1.3rem;margin-bottom:8px}
.seg p{color:var(--muted);font-size:.95rem;flex:1;margin-bottom:16px}
.seg.featured p{color:#d6eadc}
.seg .fit{font-size:.82rem;font-weight:600;color:var(--brand);background:var(--brand-light);padding:6px 12px;border-radius:999px;align-self:flex-start;margin-bottom:16px}
.seg.featured .fit{background:rgba(255,255,255,.15);color:#fff}
.seg a{font-weight:700;color:var(--brand)}
.seg.featured a{color:var(--amber)}
/* products */
#produkty{background:var(--bg-soft)}
.tabs{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin:40px 0 36px}
.tab{background:#fff;border:1px solid var(--line);padding:12px 22px;border-radius:999px;font-weight:600;cursor:pointer;font-size:.95rem;color:var(--ink);font-family:inherit}
.tab.active{background:var(--brand);color:#fff;border-color:var(--brand)}
.panel{display:none}.panel.active{display:block}
.series{display:grid;grid-template-columns:380px 1fr;gap:40px;background:#fff;border-radius:28px;padding:36px;box-shadow:var(--shadow);align-items:start}
.series-img{background:radial-gradient(circle at 50% 60%,var(--brand-light),#fff 70%);border-radius:22px;padding:28px;display:grid;place-items:center;min-height:300px}
.series-img img{max-height:300px;object-fit:contain}
.series-img.stack{display:flex;flex-direction:column;justify-content:space-around;gap:28px;align-self:stretch}
.series-img.stack figure{display:flex;flex-direction:column;align-items:center;gap:10px}
.series-img.stack figure:first-child img{max-height:330px}
.series-img.stack figure:last-child img{max-height:260px}
.series-img.smart-stack figure:first-child img{max-height:230px}
.series-img.smart-stack figure:last-child{width:100%;flex:1;justify-content:center}
.series-img.smart-stack figure:last-child img{width:100%;height:auto;max-height:none;max-width:none}
.series-img.smart-stack{padding:20px 8px}
.series-img.fill{padding:20px 8px;align-self:stretch}
.series-img.fill img{width:100%;height:auto;max-height:520px;object-fit:contain}
.series-img.stack figcaption{font-size:.85rem;font-weight:700;color:var(--brand-dark);background:#fff;border-radius:999px;padding:4px 12px;box-shadow:0 3px 10px rgba(18,56,33,.08)}
.series h3{font-size:1.7rem;margin-bottom:6px}
.series .tag{color:var(--brand);font-weight:600;margin-bottom:14px}
.series > div > p{color:var(--muted);margin-bottom:18px}
.pills{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:22px}
.pill{background:var(--brand-light);color:var(--brand-dark);font-size:.85rem;font-weight:600;padding:6px 12px;border-radius:999px}
.models{display:grid;grid-template-columns:repeat(auto-fill,minmax(165px,1fr));gap:12px}
.model{border:1px solid var(--line);border-radius:16px;padding:16px;display:flex;flex-direction:column;gap:2px}
.model .name{font-weight:800;color:var(--brand-dark)}
.model .spec{font-size:.85rem;color:var(--muted)}
.model .pw{font-size:.88rem;color:var(--ink)}
.model .pw{font-size:.78rem;color:var(--muted)}
.model .noise{display:flex;align-items:center;gap:6px;font-size:.8rem;color:var(--muted);margin-top:8px}
.model .noise b{color:var(--ink)}
.spk{width:18px;height:18px;flex:0 0 18px;color:var(--brand)}
.model .pw b{display:block;font-size:1.15rem;color:var(--brand-dark);line-height:1.2}
.model .ph{font-size:.72rem;font-weight:700;color:var(--muted);background:var(--bg-soft);border-radius:6px;padding:1px 6px;vertical-align:2px}
.model .price{margin-top:8px;font-weight:800;font-size:1.15rem}
.model .price small{display:block;font-weight:500;color:var(--muted);font-size:.75rem}
.model .price.tbd{color:#b45309;font-size:.95rem}
.note{font-size:.8rem;color:var(--muted);margin-top:16px}
.pillars{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:22px}
.pillar{background:var(--bg-soft);border-radius:14px;padding:14px}
.pillar b{display:block;color:var(--brand-dark);font-size:.95rem}
.pillar span strong{color:var(--brand-dark)}
.pillar span{font-size:.82rem;color:var(--muted)}
.tanks{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:20px}
.tank{background:#fff;border-radius:22px;overflow:hidden;box-shadow:var(--shadow);display:flex;flex-direction:column}
.tank .ti{position:relative;background:radial-gradient(circle at 50% 60%,var(--brand-light),#fff 75%);height:230px;display:grid;place-items:center;padding:18px}
.tank .ti img{max-height:200px;object-fit:contain}
.tank .tb{padding:20px 22px 24px;display:flex;flex-direction:column;flex:1}
.tank h4{font-size:1.08rem;margin-bottom:6px}
.tank p{color:var(--muted);font-size:.88rem;margin-bottom:12px;flex:1}
.tank .price{font-weight:800;font-size:1.2rem}
.tank .price small{font-weight:500;color:var(--muted);font-size:.75rem}
.tank .combo{font-size:.85rem;color:var(--brand);font-weight:600}

/* how */
.how{display:grid;grid-template-columns:1fr 1fr;gap:56px;align-items:center}
.how img{border-radius:28px;box-shadow:var(--shadow)}
.steps{display:grid;gap:18px;margin-top:28px}
.step{display:flex;gap:16px}
.step .n{flex:0 0 44px;height:44px;border-radius:50%;background:var(--brand);color:#fff;font-weight:800;display:grid;place-items:center}
.step h4{margin-bottom:2px}
.step p{color:var(--muted);font-size:.95rem}

/* process */
#postup{background:var(--brand-dark);color:#fff}
#postup .eyebrow{background:rgba(255,255,255,.1);color:#9fd8b3}
#postup .lead{color:#b9cfc1}
.process{display:grid;grid-template-columns:repeat(4,1fr);gap:22px;margin-top:48px;counter-reset:p}
.pstep{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);border-radius:var(--radius);padding:26px}
.pstep .n{font-family:Kalam,cursive;font-size:2.4rem;color:var(--amber);line-height:1}
.pstep h3{margin:10px 0 6px;font-size:1.15rem}
.pstep p{color:#b9cfc1;font-size:.93rem}

/* services */
.services{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin-top:44px}
.svc{border-radius:var(--radius);overflow:hidden;background:#fff;border:1px solid var(--line)}
.svc img{aspect-ratio:4/3;object-fit:cover;width:100%}
.svc div{padding:20px}
.svc h3{font-size:1.08rem;margin-bottom:6px}
.svc p{color:var(--muted);font-size:.9rem}

/* cta band */
.band{position:relative;border-radius:32px;overflow:hidden;color:#fff;padding:64px;display:grid;grid-template-columns:1.3fr 1fr;gap:30px;align-items:center;background:var(--brand)}
.band::before{content:"";position:absolute;inset:0;background:url(%%IMG%%k-topeni.webp) right center/cover;opacity:.18}
.band > *{position:relative}
.band h2{color:#fff}
.band p{color:#d6eadc;font-size:1.08rem}
.band .hand{color:var(--amber)}

/* reviews */
.reviews{display:grid;grid-template-columns:repeat(2,1fr);gap:22px;margin-top:44px}
.review{background:var(--bg-soft);border-radius:var(--radius);padding:30px}
.review .stars{color:var(--amber);letter-spacing:2px;margin-bottom:10px}
.review p{font-size:1.02rem;margin-bottom:16px}
.review b{display:block}
.review span{color:var(--muted);font-size:.9rem}

/* blog */
.posts{display:grid;grid-template-columns:repeat(3,1fr);gap:22px;margin-top:44px}
.post{border-radius:var(--radius);overflow:hidden;border:1px solid var(--line);background:#fff}
.post img{aspect-ratio:4/3;object-fit:cover;width:100%}
.post div{padding:22px}
.post h3{font-size:1.1rem;margin-bottom:6px}
.post p{color:var(--muted);font-size:.92rem;margin-bottom:12px}
.post a{color:var(--brand);font-weight:600}

/* contact */
#kontakt{background:var(--bg-soft)}
.contact{display:grid;grid-template-columns:1fr 1.2fr;gap:40px;margin-top:40px}
.cinfo{display:grid;gap:14px;align-content:start}
.ci{background:#fff;border-radius:16px;padding:20px;display:flex;gap:14px;align-items:center;border:1px solid var(--line)}
.ci .ic{width:46px;height:46px;border-radius:12px;background:var(--brand-light);display:grid;place-items:center;font-size:1.2rem;flex:0 0 46px}
.ci small{color:var(--muted);display:block}
.ci b{color:var(--brand-dark)}
form{background:#fff;border-radius:24px;padding:32px;box-shadow:var(--shadow);display:grid;gap:14px;grid-template-columns:1fr 1fr}
form .full{grid-column:1/-1}
label{font-size:.85rem;font-weight:600;display:grid;gap:6px}
input,select,textarea{font:inherit;padding:12px 14px;border:1px solid var(--line);border-radius:12px;background:var(--bg-soft);width:100%}
input:focus,select:focus,textarea:focus{outline:2px solid var(--brand);border-color:transparent}
form small{color:var(--muted)}

footer{background:var(--brand-dark);color:#b9cfc1;padding:56px 0 28px;font-size:.92rem}
.fgrid{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:30px;margin-bottom:36px}
footer h4{color:#fff;margin-bottom:12px}
footer a:hover{color:#fff}
footer .logo{margin-bottom:14px}
footer .logo img,footer .logo-svg{height:63px}
.fbottom{border-top:1px solid rgba(255,255,255,.12);padding-top:20px;font-size:.82rem;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}

@media (max-width:980px){
  .hero{min-height:0;align-items:flex-start;padding:40px 0 calc(70.7vw + 10px);background-position:center top}
  .hero::before{width:100%;-webkit-mask-image:linear-gradient(180deg,transparent 0,#000 18%);mask-image:linear-gradient(180deg,transparent 0,#000 18%)}
  .hero::after{background:linear-gradient(180deg,rgba(14,36,24,.95) 0%,rgba(14,36,24,.88) 55%,rgba(14,36,24,.2) 78%,rgba(14,36,24,0) 90%)}
}
@media (max-width:1320px){.phone{display:none}}
@media (max-width:1180px){
  .menu{display:none}.burger{display:block}
  .menu.open{display:flex;flex-direction:column;position:absolute;top:76px;left:0;right:0;background:#fff;padding:20px 24px;border-bottom:1px solid var(--line)}
  .hero-grid,.how,.contact,.band,.sun-grid{grid-template-columns:1fr}
  .series{grid-template-columns:1fr;padding:24px}
  .why-grid,.services,.posts,.process{grid-template-columns:repeat(2,1fr)}
  .segs{grid-template-columns:1fr}
  .badge.b1{left:12px}.badge.b2{right:12px}
  .fgrid{grid-template-columns:1fr 1fr}
}
@media (max-width:620px){
  .wrap{padding:0 16px}
  section{padding:64px 0}
  .why-grid,.services,.posts,.process,.reviews,.pillars{grid-template-columns:1fr}
  .phone,.nav-right .btn,.badge{display:none}
  .sun-img img{max-height:340px}.series-img.stack figure:first-child img{max-height:240px}.series-img.stack figure:last-child img{max-height:190px}.series-img.smart-stack figure:last-child img{width:100%;max-width:300px;height:auto;max-height:none}.series-img.fill img{max-width:300px;max-height:380px}.sun-img .sun{font-size:3rem;top:-40px}
  .logo img,.logo .logo-svg{height:52px}
  .hero-photo{margin:0 -16px;border-radius:0;box-shadow:none}.hero-cap{position:static;border-radius:0;box-shadow:none;background:var(--bg-soft)}.hero-unit{padding:24px 12px 14px;gap:8px}.hu img{height:190px}.hu-smart img{height:120px}.hu-pair img{height:170px}.hu-pair .hu-small{height:100px;margin-left:-20px}.scop{font-size:.9rem;padding:3px 7px}
  form{grid-template-columns:1fr;padding:22px}
  .band{padding:36px 24px}
  .fgrid{grid-template-columns:1fr}
  .stats{gap:22px}
}
</style>
</head>
<body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <symbol id="i-floor" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3c-1 1.3 1 2.4 0 3.7M12 3c-1 1.3 1 2.4 0 3.7M18 3c-1 1.3 1 2.4 0 3.7"/><path d="M2 10h20"/><path d="M3 14h16a2 2 0 0 1 0 4H5a2 2 0 0 0 0 4h16"/></symbol>
  <symbol id="i-rad" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 2c-.8 1 .8 2 0 3M15 2c-.8 1 .8 2 0 3"/><rect x="3" y="7" width="4" height="13" rx="2"/><rect x="10" y="7" width="4" height="13" rx="2"/><rect x="17" y="7" width="4" height="13" rx="2"/><path d="M5 22v-2M19 22v-2"/></symbol>
</svg>

<header>
  <div class="wrap nav">
    <a href="#" class="logo"><svg xmlns="http://www.w3.org/2000/svg" class="logo-svg" role="img" aria-label="REO HEATING" viewBox="24 22 264 101">
  <path d="M76.07 79.02 L112.09 42.35 L126.02 55.61 L130.98 50.39 L111.91 32.25 L70.93 73.98 Z" fill="#838383"/>
  <path d="M119.98 76.11 L160.96 37.21 L202.47 78.07 L207.53 72.93 L161.04 27.19 L115.02 70.89 Z" fill="#50854D"/>
  <rect x="86" y="44.5" width="6" height="14" fill="#838383"/>
  <rect x="181" y="39.5" width="6.2" height="14" fill="#50854D"/>
  <g fill="#F0C246"><rect x="152.00" y="54.00" width="8.00" height="7.50"/><rect x="152.00" y="63.10" width="8.00" height="7.50"/><rect x="161.60" y="54.00" width="8.00" height="7.50"/><rect x="161.60" y="63.10" width="8.00" height="7.50"/><circle cx="213" cy="44.5" r="8.9"/><path d="M210.09 34.00 L213.00 27.10 L215.91 34.00 Z"/><path d="M215.73 33.95 L221.70 29.43 L220.77 36.86 Z"/><path d="M220.64 36.73 L228.07 35.80 L223.55 41.77 Z"/><path d="M223.50 41.59 L230.40 44.50 L223.50 47.41 Z"/><path d="M223.55 47.23 L228.07 53.20 L220.64 52.27 Z"/><path d="M220.77 52.14 L221.70 59.57 L215.73 55.05 Z"/><path d="M215.91 55.00 L213.00 61.90 L210.09 55.00 Z"/><path d="M210.27 55.05 L204.30 59.57 L205.23 52.14 Z"/><path d="M205.36 52.27 L197.93 53.20 L202.45 47.23 Z"/><path d="M202.50 47.41 L195.60 44.50 L202.50 41.59 Z"/><path d="M202.45 41.77 L197.93 35.80 L205.36 36.73 Z"/><path d="M205.23 36.86 L204.30 29.43 L210.27 33.95 Z"/></g>
  <path d="M34.95720338983051 116.3H31.0V88.0H40.07358757062147Q42.11214689265537 88.0 43.95084745762712 88.41970338983052Q45.789548022598865 88.83940677966102 47.168573446327684 89.75875706214688Q48.5475988700565 90.67810734463276 49.347033898305085 92.17704802259887Q50.14646892655367 93.67598870056497 50.14646892655367 95.83446327683616Q50.14646892655367 98.95225988700565 48.22782485875706 100.87090395480226Q46.309180790960454 102.78954802259886 43.27132768361582 103.30918079096045L51.18573446327683 116.3H46.389124293785315L39.19420903954802 103.70889830508474H34.95720338983051ZM34.95720338983051 100.39124293785311H39.51398305084746Q40.91299435028249 100.39124293785311 42.11214689265537 100.15141242937852Q43.311299435028246 99.91158192090396 44.21066384180791 99.37196327683615Q45.11002824858757 98.83234463276835 45.62966101694915 97.97295197740112Q46.14929378531073 97.1135593220339 46.14929378531073 95.83446327683616Q46.14929378531073 94.55536723163841 45.62966101694915 93.69597457627118Q45.11002824858757 92.83658192090395 44.25063559322034 92.31694915254238Q43.39124293785311 91.79731638418079 42.23206214689266 91.57747175141243Q41.0728813559322 91.35762711864407 39.793785310734464 91.35762711864407H34.95720338983051ZM57.93266949152542 112.78248587570621H72.72221751412428V116.3H53.97546610169491V88.0H72.12264124293785V91.47754237288136H57.93266949152542V99.95155367231638H71.28323446327683V103.34915254237288H57.93266949152542ZM104.97112994350283 102.11002824858757Q104.97112994350283 105.38771186440678 103.8319350282486 108.1257768361582Q102.69274011299436 110.86384180790961 100.69415254237289 112.84244350282486Q98.69556497175142 114.8210451977401 95.93751412429378 115.92026836158192Q93.17946327683616 117.01949152542373 89.94175141242938 117.01949152542373Q86.7040395480226 117.01949152542373 83.9659745762712 115.92026836158192Q81.22790960451978 114.8210451977401 79.22932203389831 112.84244350282486Q77.23073446327685 110.86384180790961 76.11152542372882 108.1257768361582Q74.9923163841808 105.38771186440678 74.9923163841808 102.11002824858757Q74.9923163841808 98.79237288135593 76.11152542372882 96.05430790960452Q77.23073446327685 93.3162429378531 79.22932203389831 91.37761299435027Q81.22790960451978 89.43898305084745 83.9659745762712 88.35974576271187Q86.7040395480226 87.28050847457627 89.94175141242938 87.28050847457627Q93.17946327683616 87.28050847457627 95.93751412429378 88.35974576271187Q98.69556497175142 89.43898305084745 100.69415254237289 91.37761299435027Q102.69274011299436 93.3162429378531 103.8319350282486 96.05430790960452Q104.97112994350283 98.79237288135593 104.97112994350283 102.11002824858757ZM100.69415254237289 102.11002824858757Q100.69415254237289 99.79166666666666 99.93468926553673 97.73312146892656Q99.17522598870057 95.67457627118644 97.77621468926554 94.11567796610169Q96.37720338983051 92.55677966101695 94.39860169491526 91.65741525423729Q92.42 90.75805084745762 89.94175141242938 90.75805084745762Q87.50347457627119 90.75805084745762 85.52487288135595 91.65741525423729Q83.54627118644069 92.55677966101695 82.16724576271187 94.11567796610169Q80.78822033898305 95.67457627118644 80.0287570621469 97.73312146892656Q79.26929378531074 99.79166666666666 79.26929378531074 102.11002824858757Q79.26929378531074 104.4683615819209 80.0287570621469 106.54689265536723Q80.78822033898305 108.62542372881356 82.18723163841808 110.16433615819209Q83.58624293785311 111.70324858757061 85.54485875706214 112.58262711864407Q87.50347457627119 113.46200564971751 89.94175141242938 113.46200564971751Q92.38002824858758 113.46200564971751 94.37861581920905 112.58262711864407Q96.37720338983051 111.70324858757061 97.77621468926554 110.16433615819209Q99.17522598870057 108.62542372881356 99.93468926553673 106.54689265536723Q100.69415254237289 104.4683615819209 100.69415254237289 102.11002824858757ZM117.22587570621468 88.0H121.18307909604519V99.8316384180791H135.49296610169492V88.0H139.49014124293785V116.3H135.49296610169492V103.34915254237288H121.18307909604519V116.3H117.22587570621468ZM148.7552966101695 112.78248587570621H163.54484463276836V116.3H144.79809322033898V88.0H162.94526836158192V91.47754237288136H148.7552966101695V99.95155367231638H162.10586158192092V103.34915254237288H148.7552966101695ZM168.41310734463278 116.3H164.01621468926555L176.28754237288138 88.0H179.88500000000002L192.03641242937854 116.3H187.55957627118647L184.68161016949153 109.34491525423729H171.25110169491526ZM172.6501129943503 105.86737288135593H183.2426271186441L177.9663559322034 92.59675141242937ZM204.0196468926554 116.3H200.0624435028249V91.47754237288136H190.98885593220342V88.0H213.09323446327687V91.47754237288136H204.0196468926554ZM219.240593220339 116.3H215.2833898305085V88.0H219.240593220339ZM244.49444915254242 110.62401129943503H244.5743926553673V88.0H248.5315960451978V116.3H243.53512711864414L228.58569209039553 93.19632768361582H228.50574858757068V116.3H224.54854519774017V88.0H229.70490112994355ZM275.1844632768362 93.8358757062147Q273.9053672316385 92.43686440677966 271.9267655367232 91.59745762711864Q269.94816384180797 90.75805084745762 267.5098870056498 90.75805084745762Q265.0316384180792 90.75805084745762 263.03305084745773 91.65741525423729Q261.0344632768362 92.55677966101695 259.6354519774012 94.11567796610169Q258.2364406779662 95.67457627118644 257.47697740113006 97.73312146892656Q256.71751412429387 99.79166666666666 256.71751412429387 102.11002824858757Q256.71751412429387 104.4683615819209 257.47697740113006 106.54689265536723Q258.2364406779662 108.62542372881356 259.6354519774012 110.16433615819209Q261.0344632768362 111.70324858757061 263.0730225988701 112.58262711864407Q265.11158192090403 113.46200564971751 267.6298022598871 113.46200564971751Q269.6283898305085 113.46200564971751 271.30720338983053 113.10225988700564Q272.9860169491526 112.74251412429378 274.2251412429379 112.06299435028248V104.1885593220339H267.9495762711865V100.83093220338984H278.142372881356V114.5412429378531Q275.90395480225993 115.74039548022598 273.2658192090396 116.37994350282486Q270.62768361581925 117.01949152542373 267.5098870056498 117.01949152542373Q264.19223163841815 117.01949152542373 261.4141949152543 115.92026836158192Q258.6361581920905 114.8210451977401 256.63757062146897 112.84244350282486Q254.63898305084751 110.86384180790961 253.5197740112995 108.1257768361582Q252.4005649717515 105.38771186440678 252.4005649717515 102.11002824858757Q252.4005649717515 98.79237288135593 253.53975988700574 96.05430790960452Q254.67895480225997 93.3162429378531 256.6975282485877 91.37761299435027Q258.7161016949153 89.43898305084745 261.47415254237296 88.35974576271187Q264.2322033898306 87.28050847457627 267.4699152542374 87.28050847457627Q270.86751412429385 87.28050847457627 273.5256355932204 88.279802259887Q276.183757062147 89.27909604519775 277.94251412429384 90.95790960451977Z" fill="#363533"/>
</svg>
</a>
    <nav class="menu" id="menu">
      <a href="#produkty">Tepelná čerpadla</a>
      <a href="#pro-koho">Bytové domy a firmy</a>
      <a href="#nadrze" data-tab="nadrze">Nádrže</a>
      <a href="#fotovoltaika">Fotovoltaika</a>
      <a href="#postup">Jak to probíhá</a>
      <a href="#kontakt">Kontakt</a>
    </nav>
    <div class="nav-right">
      <a class="phone" href="tel:+420774872467">+420 774 872 467</a>
      <a class="btn btn-primary" href="#kontakt">Nezávazná poptávka</a>
      <button class="burger" aria-label="Menu" onclick="document.getElementById('menu').classList.toggle('open')">☰</button>
    </div>
  </div>
</header>

<section class="hero" aria-label="Úvod">
  <div class="wrap hero-grid">
    <div>
      <span class="eyebrow">Česká republika · Slovensko</span>
      <h1><span class="yellow">Teplo</span>, které <span class="hand">šetří</span> čas i peníze</h1>
      <p>Tepelná čerpadla REO HEATING s ekologickým chladivem R290, akumulační nádrže a fotovoltaika. Pro rodinné domy, bytové domy i komerční objekty – navrhneme, dodáme, namontujeme vlastními lidmi a vyřídíme dotaci.</p>
      <div class="hero-cta">
        <a class="btn btn-primary" href="#produkty">Vybrat tepelné čerpadlo →</a>
        <a class="btn btn-ghost" href="#kontakt">Zdarma posoudíme váš dům</a>
      </div>
      <div class="stats">
        <div class="stat"><strong>6–50 kW</strong><span>na jednotku, více v kaskádě</span></div>
        <div class="stat"><strong>R290</strong><span>přírodní chladivo</span></div>
        <div class="stat"><strong>A–Z</strong><span>vlastní montáž i elektro</span></div>
      </div>
    </div>
  </div>
</section>

<section class="sunband">
  <div class="wrap sun-grid">
    <div class="sun-img"><img src="%%IMG%%rhx-pro-alpha.png" alt="REO R290 Smart RHX30 Pro"><span class="sun">☀️</span></div>
    <div>
      <span class="eyebrow"><span class="new-tag">Novinka</span>REO R290 Smart</span>
      <h2>Topí přímo <span class="hand">ze sluníčka</span></h2>
      <p class="lead">Fotovoltaické panely připojíte přímo k jednotce – bez střídače, baterie a další elektroniky. Jednotka pak topí levně a úsporně ze sluníčka, a co sluníčko nepokryje, automaticky odebere ze sítě.</p>
      <ul class="sun-list">
        <li><b>Nemusíte pořizovat velkou a drahou domácí fotovoltaiku</b> – stačí několik panelů zapojených rovnou do čerpadla.</li>
        <li><b>Kompresor Mitsubishi Electric</b> – spolehlivé srdce celé jednotky.</li>
        <li><b>Tichý chod</b> – pětistupňové odhlučnění, akustický tlak ve 3 m už od 32 dB(A).</li>
        <li><b>Topná voda až 75 °C</b> – zvládne i radiátory ve starších domech a ohřev teplé vody.</li>
        <li><b>SCOP až 5,29 s podlahovým topením a 3,91 s radiátory</b> (RH14)<span class="hl-box">průměrný roční topný faktor – <strong>víc než většina značkových R290 monobloků</strong></span></li>
      </ul>
      <a class="btn btn-primary" href="#produkty" data-go="smart">Chci topit ze sluníčka →</a>
    </div>
  </div>
</section>

<section id="proc">
  <div class="wrap center">
    <span class="eyebrow">Proč eko4home</span>
    <h2>Služby <span class="hand">do posledního wattu</span></h2>
    <p class="lead">Jsme nadšenci do udržitelné energie. Necílíme na kvantitu – proto stihneme rychlou realizaci i pružný servis.</p>
    <div class="why-grid" style="text-align:left">
      <div class="card"><div class="ic">📍</div><h3>Celá ČR a Slovensko</h3><p>Sídlíme v Třinci, ale realizujeme po celé České republice i na Slovensku.</p></div>
      <div class="card"><div class="ic">🔗</div><h3>Jeden výrobce, jeden kontakt</h3><p>Montujeme vyladěné systémy REO HEATING. Při servisu řešíte vše s jedním partnerem.</p></div>
      <div class="card"><div class="ic">🚐</div><h3>Dojedeme k vám</h3><p>Situaci posoudíme přímo u vás, vše spočítáme a vybrané řešení zrealizujeme.</p></div>
      <div class="card"><div class="ic">🛠️</div><h3>Montáž od A do Z</h3><p>Vlastní montážníci i elektrikáři, plné sklady. Další firmu nepotřebujete.</p></div>
      <div class="card"><div class="ic">💳</div><h3>Financování a dotace</h3><p>Pomůžeme s financováním a dotaci vyřídíme za vás na základě plné moci.</p></div>
      <div class="card"><div class="ic">⚖️</div><h3>Poměr cena / kvalita</h3><p>Vždy řešíme účinnost a provozní náklady, aby systém dával smysl dlouhodobě.</p></div>
    </div>
  </div>
</section>

<section id="pro-koho" style="padding-top:0">
  <div class="wrap center">
    <span class="eyebrow">Pro koho</span>
    <h2>Rodinné domy, bytové domy <span class="hand">i firmy</span></h2>
    <p class="lead">Od jednoho čerpadla pro novostavbu po kaskádovou kotelnu pro bytový dům nebo komerční objekt.</p>
    <div class="segs" style="text-align:left">
      <div class="seg"><div class="ic">🏡</div><h3>Rodinné domy</h3><p>Novostavby i rekonstrukce. Jedno čerpadlo 6–22 kW, bojler nebo kombinovaný Watertank, volitelně fotovoltaika.</p><span class="fit">RH030–RH060 · Smart RH06–RH16</span><a href="#produkty" data-go="smart">Vybrat čerpadlo →</a></div>
      <div class="seg featured"><div class="ic">🏢</div><h3>Bytové domy a SVJ</h3><p>Náhrada plynové kotelny nebo CZT. Kaskáda tepelných čerpadel s akumulací a ohřevem TUV, návrh pro výbor SVJ a pomoc s dotací.</p><span class="fit">RHX30 Pro · RH X50 · kaskády</span><a href="#produkty" data-go="pro">Zobrazit jednotky →</a></div>
      <div class="seg"><div class="ic">🏭</div><h3>Komerční objekty</h3><p>Haly, kanceláře, provozovny, ubytování. Výkonné jednotky a kaskády na míru, kombinace s fotovoltaikou na střeše.</p><span class="fit">RHX30 Pro · RH X50 · kaskády</span><a href="#kontakt" data-pick="Komerční objekt">Poptat řešení →</a></div>
    </div>
  </div>
</section>

<section id="produkty">
  <div class="wrap">
    <div class="center">
      <span class="eyebrow">Produkty</span>
      <h2>Řešení pro <span class="hand">každý dům</span></h2>
      <p class="lead">Tepelná čerpadla REO HEATING vzduch–voda s chladivem R290 a nerezové nádrže. Ceny jsou bez DPH, za zařízení bez montáže.</p>
    </div>
    <div class="tabs" role="tablist">
      <button class="tab active" data-tab="rh">REO R290 · RH030–RH060</button>
      <button class="tab" data-tab="smart">REO R290 Smart · RH06–RH16</button>
      <button class="tab" data-tab="pro">Bytové domy a firmy · RHX30 Pro / RH X50</button>
      <button class="tab" data-tab="nadrze" id="nadrze">Nerezové nádrže a TUV</button>
    </div>

    <p class="note center" style="margin:-18px 0 22px">Akustický tlak ve 3 m je dopočten z akustického výkonu L<sub>WA</sub> dle podkladů výrobce pro volné pole; u řady Smart a Pro uvádíme nejnižší hodnotu (provoz A7/W35) (L<sub>p</sub> = L<sub>WA</sub> − 20·log r − 8). Skutečnost ovlivní odrazy od zdí a umístění jednotky.</p>

    <div class="panel active" data-panel="rh">
      <div class="series">
        <div class="series-img stack"><figure><img src="%%IMG%%rh-rada-predni.png" alt="Tepelná čerpadla REO R290 RH060 a RH030–RH050 zepředu"><figcaption>RH060 · RH030–RH050</figcaption></figure><figure><img src="%%IMG%%rh-rada-zadni.png" alt="Tepelná čerpadla REO R290 zezadu s přípojkami"><figcaption>pohled zezadu – přípojky</figcaption></figure></div>
        <div>
          <h3>REO R290 · RH030–RH060</h3>
          <div class="tag">Osvědčená řada pro rodinné domy, 8–22 kW</div>
          <p>Monoblok vzduch–voda pro vytápění, chlazení i ohřev teplé vody s výstupní teplotou až 70 °C. Inverterový kompresor Highly, energetická třída A+++. RH060 zvládne i větší domy a v kaskádě bytové domy.</p>
          <div class="pills"><span class="pill">R290</span><span class="pill">A+++</span><span class="pill">topná voda až 70 °C</span><span class="pill">topení · chlazení · TUV</span><span class="pill">SCOP 4,8</span></div>
          <div class="scop-legend"><b>SCOP = průměrný roční topný faktor</b> – kolik kWh tepla vyrobí čerpadlo z 1 kWh elektřiny v průměru za celou topnou sezónu.<span><svg style="color:#e0662b"><use href="#i-floor"/></svg>35 °C – podlahové topení</span><span><svg style="color:#c24b2a"><use href="#i-rad"/></svg>55 °C – radiátory</span><span><svg class="spk" style="width:18px;height:18px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9v6h4l5 4V5L8 9z"/><path d="M16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/></svg>akustický tlak ve vzdálenosti 3 m od jednotky</span></div>
          <div class="models">
            <div class="model"><span class="name">RH030</span><span class="spec">8,9 kW · COP 5,17</span><span class="spec">novostavby, menší domy</span><span class="noise"><svg class="spk" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9v6h4l5 4V5L8 9z"/><path d="M16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/></svg><span>akustický tlak ve 3&nbsp;m: <b>40</b>&nbsp;dB(A)</span></span><span class="price">95 000 Kč <small>bez DPH</small></span></div>
            <div class="model"><span class="name">RH040</span><span class="spec">11,4 kW · COP 5,29</span><span class="spec">středně velké domy</span><span class="noise"><svg class="spk" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9v6h4l5 4V5L8 9z"/><path d="M16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/></svg><span>akustický tlak ve 3&nbsp;m: <b>43</b>&nbsp;dB(A)</span></span><span class="price">105 000 Kč <small>bez DPH</small></span></div>
            <div class="model"><span class="name">RH050</span><span class="spec">14,8 kW · COP 5,22</span><span class="spec">větší zateplené domy</span><span class="noise"><svg class="spk" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9v6h4l5 4V5L8 9z"/><path d="M16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/></svg><span>akustický tlak ve 3&nbsp;m: <b>41</b>&nbsp;dB(A)</span></span><span class="price">125 000 Kč <small>bez DPH</small></span></div>
            <div class="model"><span class="name">RH060</span><span class="spec">22,0 kW · COP 5,22</span><span class="mscop"><span class="scop scop-35"><svg><use href="#i-floor"/></svg><span><i>podlaha 35 °C</i>4,80</span></span><span class="scop scop-55"><svg><use href="#i-rad"/></svg><span><i>radiátory 55 °C</i>3,89</span></span></span><span class="spec">velké domy, BD v kaskádě</span><span class="noise"><svg class="spk" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9v6h4l5 4V5L8 9z"/><path d="M16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/></svg><span>akustický tlak ve 3&nbsp;m: od&nbsp;<b>34</b>&nbsp;dB(A)</span></span><span class="price">169 000 Kč <small>bez DPH</small></span></div>
          </div>
          <p class="note">Topný výkon max. při A7/W35. Akustický výkon L<sub>WA</sub> 58–62 dB(A) dle protokolů TÜV SÜD (EN 12102-1). SCOP RH060 dle KEYMARK (EN 14825, průměrné klima).</p>
        </div>
      </div>
    </div>

    <div class="panel" data-panel="smart">
      <div class="series">
        <div class="series-img stack smart-stack"><figure><img src="%%IMG%%smart.png" alt="Tepelné čerpadlo REO R290 Smart RH06–RH16"><figcaption>RH06 – RH16</figcaption></figure><figure><img src="%%IMG%%rhx-pro-alpha.png" alt="Tepelné čerpadlo REO R290 Smart RHX30 Pro"><figcaption>RHX30 Pro</figcaption></figure></div>
        <div>
          <h3>REO R290 Smart · RH06–RH16</h3>
          <div class="tag">Topí přímo ze sluníčka</div>
          <div class="pillars">
            <div class="pillar"><b>☀️ Topí ze sluníčka</b><span>Panely připojíte přímo k jednotce – bez střídače, baterie a další elektroniky. Co chybí, odebere ze sítě. Nepotřebujete velkou a drahou domácí FV.</span></div>
            <div class="pillar"><b>📈 Vysoká účinnost</b><span>SCOP až <strong>5,29</strong> s podlahovým topením (35 °C) a až <strong>3,94</strong> s radiátory (55 °C) – <mark class="hl">víc než většina značkových R290 monobloků</mark>.</span></div>
            <div class="pillar"><b>⚙️ Mitsubishi Electric</b><span>Kompresor Mitsubishi Electric – osvědčená spolehlivost.</span></div>
          </div>
          <div class="pills"><span class="pill">🌡️ topná voda až 75 °C</span><span class="pill">🔇 tichý chod – od 32 dB(A) ve 3 m</span><span class="pill">R290</span><span class="pill">kompresor Mitsubishi Electric</span><span class="pill">integrovaný dohřev 3 kW</span></div>
          <p class="note" style="margin:0 0 8px"><b>Číslo v názvu modelu</b> (RH06 … RH16) odpovídá orientačně tepelné ztrátě domu v kW, pro který se jednotka hodí. Skutečný maximální topný výkon je vyšší – uvádíme ho při venkovní teplotě 7 °C a topné vodě 35 °C (A7/W35).</p>
          <p class="note" style="margin:0 0 14px">SCOP (průměrný roční topný faktor) dle EN 14825, průměrné klima, podklady výrobce.</p>
          <p>Jednotka má integrovaný elektrický dohřev 3 kW, oběhové čerpadlo i expanzní nádobu. Přímé napájení z fotovoltaiky využijete hlavně od jara do podzimu.</p>
          <div class="scop-legend"><b>SCOP = průměrný roční topný faktor</b> – kolik kWh tepla vyrobí čerpadlo z 1 kWh elektřiny v průměru za celou topnou sezónu.<span><svg style="color:#e0662b"><use href="#i-floor"/></svg>35 °C – podlahové topení</span><span><svg style="color:#c24b2a"><use href="#i-rad"/></svg>55 °C – radiátory</span><span><svg class="spk" style="width:18px;height:18px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9v6h4l5 4V5L8 9z"/><path d="M16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/></svg>akustický tlak ve vzdálenosti 3 m od jednotky</span></div>
          <div class="models">
            <div class="model"><span class="name">RH06 <small class="ph">1F</small></span><span class="pw"><b>8,5&nbsp;kW</b>max. výkon při A7/W35</span><span class="spec">modulace 3,4–8,5&nbsp;kW</span><span class="mscop"><span class="scop scop-35"><svg><use href="#i-floor"/></svg><span><i>podlaha 35 °C</i>5,00</span></span><span class="scop scop-55"><svg><use href="#i-rad"/></svg><span><i>radiátory 55 °C</i>3,84</span></span></span><span class="noise"><svg class="spk" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9v6h4l5 4V5L8 9z"/><path d="M16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/></svg><span>akustický tlak ve 3&nbsp;m: <b>35</b>&nbsp;dB(A)</span></span><span class="price">129 000 Kč <small>bez DPH</small></span></div>
            <div class="model"><span class="name">RH08 <small class="ph">3F</small></span><span class="pw"><b>11,0&nbsp;kW</b>max. výkon při A7/W35</span><span class="spec">modulace 4,1–11,0&nbsp;kW</span><span class="mscop"><span class="scop scop-35"><svg><use href="#i-floor"/></svg><span><i>podlaha 35 °C</i>5,15</span></span><span class="scop scop-55"><svg><use href="#i-rad"/></svg><span><i>radiátory 55 °C</i>3,90</span></span></span><span class="noise"><svg class="spk" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9v6h4l5 4V5L8 9z"/><path d="M16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/></svg><span>akustický tlak ve 3&nbsp;m: od&nbsp;<b>32</b>&nbsp;dB(A)</span></span><span class="price">139 000 Kč <small>bez DPH</small></span></div>
            <div class="model"><span class="name">RH10 <small class="ph">3F</small></span><span class="pw"><b>12,9&nbsp;kW</b>max. výkon při A7/W35</span><span class="spec">modulace 4,2–12,9&nbsp;kW</span><span class="mscop"><span class="scop scop-35"><svg><use href="#i-floor"/></svg><span><i>podlaha 35 °C</i>5,20</span></span><span class="scop scop-55"><svg><use href="#i-rad"/></svg><span><i>radiátory 55 °C</i>3,90</span></span></span><span class="noise"><svg class="spk" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9v6h4l5 4V5L8 9z"/><path d="M16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/></svg><span>akustický tlak ve 3&nbsp;m: od&nbsp;<b>36</b>&nbsp;dB(A)</span></span><span class="price">149 000 Kč <small>bez DPH</small></span></div>
            <div class="model"><span class="name">RH12 <small class="ph">3F</small></span><span class="pw"><b>17,0&nbsp;kW</b>max. výkon při A7/W35</span><span class="spec">modulace 6,3–17,0&nbsp;kW</span><span class="mscop"><span class="scop scop-35"><svg><use href="#i-floor"/></svg><span><i>podlaha 35 °C</i>5,11</span></span><span class="scop scop-55"><svg><use href="#i-rad"/></svg><span><i>radiátory 55 °C</i>3,94</span></span></span><span class="noise"><svg class="spk" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9v6h4l5 4V5L8 9z"/><path d="M16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/></svg><span>akustický tlak ve 3&nbsp;m: od&nbsp;<b>37</b>&nbsp;dB(A)</span></span><span class="price">159 000 Kč <small>bez DPH</small></span></div>
            <div class="model"><span class="name">RH14 <small class="ph">3F</small></span><span class="pw"><b>19,3&nbsp;kW</b>max. výkon při A7/W35</span><span class="spec">modulace 6,6–19,3&nbsp;kW</span><span class="mscop"><span class="scop scop-35"><svg><use href="#i-floor"/></svg><span><i>podlaha 35 °C</i>5,29</span></span><span class="scop scop-55"><svg><use href="#i-rad"/></svg><span><i>radiátory 55 °C</i>3,91</span></span></span><span class="noise"><svg class="spk" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9v6h4l5 4V5L8 9z"/><path d="M16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/></svg><span>akustický tlak ve 3&nbsp;m: od&nbsp;<b>38</b>&nbsp;dB(A)</span></span><span class="price">169 000 Kč <small>bez DPH</small></span></div>
            <div class="model"><span class="name">RH16 <small class="ph">3F</small></span><span class="pw"><b>22,0&nbsp;kW</b>max. výkon při A7/W35</span><span class="spec">modulace 7,8–22,0&nbsp;kW</span><span class="mscop"><span class="scop scop-35"><svg><use href="#i-floor"/></svg><span><i>podlaha 35 °C</i>5,09</span></span><span class="scop scop-55"><svg><use href="#i-rad"/></svg><span><i>radiátory 55 °C</i>3,88</span></span></span><span class="noise"><svg class="spk" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9v6h4l5 4V5L8 9z"/><path d="M16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/></svg><span>akustický tlak ve 3&nbsp;m: od&nbsp;<b>37</b>&nbsp;dB(A)</span></span><span class="price">189 000 Kč <small>bez DPH</small></span></div>
          </div>
        </div>
      </div>
    </div>

    <div class="panel" data-panel="pro">
      <div class="series">
        <div class="series-img fill"><img src="%%IMG%%rhx-pro-alpha.png" alt="Tepelné čerpadlo REO RHX20 Pro / RHX30 Pro"></div>
        <div>
          <h3>REO R290 Smart · RHX20 Pro / RHX30 Pro</h3>
          <div class="tag">Výkonné jednotky pro bytové domy, firmy a kaskády</div>
          <p>Větší jednotky řady Smart pro objekty s vyšší potřebou tepla. Kompresor Mitsubishi Electric, možnost přímého připojení fotovoltaiky, řazení do kaskády. Elektrický dohřev a expanzi řešíme v rámci kotelny.</p>
          <div class="pills"><span class="pill">🌡️ topná voda až 75 °C</span><span class="pill">🔇 tichý chod – od 32 dB(A) ve 3 m</span><span class="pill">R290</span><span class="pill">kaskády</span><span class="pill">kompresor Mitsubishi Electric</span><span class="pill">bytové domy · firmy</span></div>
          <div class="models">
            <div class="model"><span class="name">RHX20 Pro</span><span class="pw"><b>28,0&nbsp;kW</b>max. výkon při A7/W35</span><span class="spec">modulace 10,2–28,0&nbsp;kW</span><span class="noise"><svg class="spk" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9v6h4l5 4V5L8 9z"/><path d="M16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/></svg><span>akustický tlak ve 3&nbsp;m: od&nbsp;<b>32</b>&nbsp;dB(A)</span></span><span class="price">300 000 Kč <small>bez DPH</small></span></div>
            <div class="model"><span class="name">RHX30 Pro</span><span class="pw"><b>40,0&nbsp;kW</b>max. výkon při A7/W35</span><span class="spec">modulace 12,7–40,0&nbsp;kW</span><span class="noise"><svg class="spk" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9v6h4l5 4V5L8 9z"/><path d="M16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/></svg><span>akustický tlak ve 3&nbsp;m: od&nbsp;<b>37</b>&nbsp;dB(A)</span></span><span class="price">350 000 Kč <small>bez DPH</small></span></div>
          </div>
        </div>
      </div>
      <div class="series" style="margin-top:24px">
        <div class="series-img fill"><img src="%%IMG%%rh-x50.png" alt="Komerční tepelné čerpadlo REO RH X50"></div>
        <div>
          <h3>REO RH X50</h3>
          <div class="tag">Komerční tepelné čerpadlo pro bytové domy a velké objekty</div>
          <p>Výkonná jednotka R290 pro náhradu plynových kotelen a CZT. Topná voda až 75 °C – vhodné i pro starší radiátorové soustavy a ohřev TUV. Ve kaskádě pokryje potřebu celého bytového domu.</p>
          <div class="pills"><span class="pill">R290</span><span class="pill">🌡️ topná voda až 75 °C</span><span class="pill">A+++ (35 °C)</span><span class="pill">kaskády</span></div>
          <div class="models">
            <div class="model"><span class="name">RH X50</span><span class="spec">49,3 kW · COP 3,80 při A7/W35</span><span class="spec">24,8 kW při −15 °C / W55</span><span class="noise"><svg class="spk" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9v6h4l5 4V5L8 9z"/><path d="M16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/></svg><span>akustický tlak ve 3&nbsp;m: <b>48</b>&nbsp;dB(A)</span></span><span class="price">430 000 Kč <small>bez DPH</small></span></div>
          </div>
          <p class="note">Pro bytové domy a firmy připravíme návrh kotelny na míru – počet jednotek, akumulace, ohřev TUV, záloha.</p>
        </div>
      </div>
    </div>

    <div class="panel" data-panel="nadrze">
      <div class="nerez-band"><span class="nerez-ic">✓</span><div><b>Všechny naše nádrže jsou z nerezové oceli 304</b><span>Nerez nekoroduje a je hygienická – voda zůstává čistá a bez rzi, nádrž si drží vzhled i funkci dlouhá léta.</span></div></div>
      <div class="tanks">
        <div class="tank"><div class="ti"><span class="nerez">✓ Nerez 304</span><img src="%%IMG%%aku-100.png" alt="Akumulační nádrž AKU 100 l"></div><div class="tb"><h4>Nerezová AKU nádrž 100 l + 3 kW</h4><p>Akumulační a vyrovnávací zásobník z nerezové oceli 304, izolace 50 mm, ⌀ 470 × 1 045 mm.</p><span class="price">15 000 Kč <small>bez DPH</small></span></div></div>
        <div class="tank"><div class="ti"><span class="nerez">✓ Nerez 304</span><img src="%%IMG%%aku-500.jpg" alt="Akumulační nádrž AKU 500 l"></div><div class="tb"><h4>Nerezová AKU nádrž 500 l</h4><p>Velký akumulační zásobník bez výměníku z nerezové oceli 304, PUR 50 mm, 70 × 70 × 179 cm. Připojí i krb nebo kotel; lze doplnit spirálu 9 kW.</p><span class="price">35 000 Kč <small>bez DPH</small></span></div></div>
        <div class="tank"><div class="ti"><span class="nerez">✓ Nerez 304</span><img src="%%IMG%%tuv.png" alt="Zásobník TUV 200 l"></div><div class="tb"><h4>Nerezový bojler TUV 200 l</h4><p>Nádrž i výměník z nerezové oceli 304, výměník ⌀ 25 mm × 20 m (2,7 m²), izolace 50 mm, ⌀ 520 × 1 560 mm.</p><span class="price">25 000 Kč <small>bez DPH</small></span></div></div>
        <div class="tank"><div class="ti"><span class="nerez">✓ Nerez 304</span><img src="%%IMG%%tuv.png" alt="Zásobník TUV 300 l"></div><div class="tb"><h4>Nerezový bojler TUV 300 l</h4><p>Nádrž i výměník z nerezové oceli 304, výměník ⌀ 25 mm × 30 m (4,3 m²), izolace 50 mm, ⌀ 560 × 1 860 mm.</p><span class="price">30 000 Kč <small>bez DPH</small></span></div></div>
        <div class="tank"><div class="ti"><span class="nerez">✓ Nerez 304</span><img src="%%IMG%%watertank.png" alt="Kombinovaný zásobník Watertank 210/70"></div><div class="tb"><h4>Nerezový Watertank 210/70 l</h4><p>Kombinovaný nerezový zásobník (ocel 304) TUV + topné vody v jednom „slim“ tanku (⌀ 56 cm, výška 190 cm), výměník 3,5 m², v každé nádrži spirála 3 kW.</p><span class="price">39 000 Kč <small>bez DPH</small></span><span class="combo">s naším TČ jen 25 000 Kč</span></div></div>
        <div class="tank"><div class="ti"><span class="nerez">✓ Nerez 304</span><img src="%%IMG%%watertank.png" alt="Kombinovaný zásobník Watertank 330/120"></div><div class="tb"><h4>Nerezový Watertank 330/120 l</h4><p>Větší kombinovaný nerezový zásobník (ocel 304) (⌀ 70 cm, výška 190 cm), výměník 3,5 m², spirály 3 kW, připojení dvou zdrojů tepla.</p><span class="price">45 000 Kč <small>bez DPH</small></span><span class="combo">s naším TČ jen 31 000 Kč</span></div></div>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap how">
    <img src="%%IMG%%k-ohrev-vody.webp" alt="Princip tepelného čerpadla a ohřevu vody">
    <div>
      <span class="eyebrow">Princip</span>
      <h2>Jak tepelné čerpadlo <span class="hand">funguje</span></h2>
      <div class="steps">
        <div class="step"><span class="n">1</span><div><h4>Odebírá teplo ze vzduchu</h4><p>Chladivo R290 se ve výparníku odpaří i při mrazu a pohltí energii z venkovního vzduchu.</p></div></div>
        <div class="step"><span class="n">2</span><div><h4>Zvýší jeho teplotu</h4><p>Kompresor chladivo stlačí – tím vzroste tlak i teplota na úroveň pro vytápění.</p></div></div>
        <div class="step"><span class="n">3</span><div><h4>Předá teplo do domu</h4><p>V kondenzátoru se teplo předá do topné vody pro radiátory, podlahovku i bojler.</p></div></div>
        <div class="step"><span class="n">4</span><div><h4>Většinu energie má zdarma</h4><p>Z jedné kWh elektřiny vyrobí orientačně 3–5 kWh tepla podle teploty venku a topné vody.</p></div></div>
      </div>
    </div>
  </div>
</section>

<section id="postup">
  <div class="wrap">
    <span class="eyebrow">Jak to probíhá</span>
    <h2>Jednoduchá cesta k levnějšímu vytápění</h2>
    <p class="lead">Od první schůzky po dlouhodobý servis – vše s jedním partnerem.</p>
    <div class="process">
      <div class="pstep"><span class="n">01</span><h3>Schůzka u vás</h3><p>Zdarma posoudíme dům, otopnou soustavu a vaše požadavky.</p></div>
      <div class="pstep"><span class="n">02</span><h3>Návrh a nabídka</h3><p>Navrhneme výkon čerpadla, akumulaci a ohřev vody. Cenu dostanete předem.</p></div>
      <div class="pstep"><span class="n">03</span><h3>Montáž a dotace</h3><p>Vlastní montážníci a elektrikáři. Papírování k dotaci vyřídíme za vás.</p></div>
      <div class="pstep"><span class="n">04</span><h3>Servis</h3><p>Pravidelná údržba a rychlá pomoc po celé ČR i na Slovensku.</p></div>
    </div>
  </div>
</section>

<section id="fotovoltaika">
  <div class="wrap">
    <div class="center">
      <span class="eyebrow">Doplňkové služby</span>
      <h2>Fotovoltaika, topení <span class="hand">a víc</span></h2>
      <p class="lead">Tepelné čerpadlo, fotovoltaika, nebo jejich mix – doporučíme to, co dává smysl pro váš dům.</p>
    </div>
    <div class="services">
      <div class="svc"><img src="%%IMG%%k-elektroinstalace.webp" alt="Fotovoltaika a elektroinstalace"><div><h3>Fotovoltaika</h3><p>Elektrárny pro domy i firmy. S řadou Smart může FV topit přímo do tepelného čerpadla.</p></div></div>
      <div class="svc"><img src="%%IMG%%k-topeni.webp" alt="Otopná soustava"><div><h3>Topení</h3><p>Návrh a úprava otopné soustavy pro nízkoteplotní provoz s tepelným čerpadlem.</p></div></div>
      <div class="svc"><img src="%%IMG%%k-zatepleni.webp" alt="Zateplení domu"><div><h3>Zateplení</h3><p>Doporučíme opatření, která sníží tepelnou ztrátu a potřebný výkon čerpadla.</p></div></div>
      <div class="svc"><img src="%%IMG%%k-dotace-zelena-usporam.webp" alt="Dotace Nová zelená úsporám"><div><h3>Dotace a financování</h3><p>Vyřídíme dotaci a poradíme s financováním, když nechcete platit vše najednou.</p></div></div>
    </div>
  </div>
</section>

<section style="padding-top:0">
  <div class="wrap">
    <div class="band">
      <div>
        <h2>Zjistěte, <span class="hand">kolik ušetříte</span></h2>
        <p>Nezávazně spočítáme orientační provozní náklady pro váš dům a doporučíme vhodné řešení.</p>
      </div>
      <div style="display:flex;gap:12px;flex-wrap:wrap;justify-content:flex-end">
        <a class="btn btn-amber" href="#kontakt">Nezávazně poptat</a>
        <a class="btn" style="border-color:#fff;color:#fff" href="tel:+420774872467">Zavolat</a>
      </div>
    </div>
  </div>
</section>

<section style="padding-top:0">
  <div class="wrap center">
    <span class="eyebrow">Reference</span>
    <h2>Co říkají <span class="hand">naši zákazníci</span></h2>
    <div class="reviews" style="text-align:left">
      <div class="review"><div class="stars">★★★★★</div><p>„S elektrárnou jsme opravdu spokojení. Máme první letní sezonu za sebou a úspora je opravdu znatelná! Rozhodně doporučuji.“</p><b>Vojta Czieslar</b><span>Návsí</span></div>
      <div class="review"><div class="stars">★★★★★</div><p>„Vše proběhlo dle domluvy na začátku. Chlapi jsou opravdu na svém místě a ví, co dělají. Díky za spolupráci.“</p><b>Marek Studníček</b><span>Třinec – Oldřichovice</span></div>
    </div>
  </div>
</section>

<section style="padding-top:0">
  <div class="wrap center">
    <span class="eyebrow">Poradna</span>
    <h2>Užitečné články</h2>
    <div class="posts" style="text-align:left">
      <div class="post"><img src="%%IMG%%k-jak-vybrat.webp" alt=""><div><h3>Jak vybrat tepelné čerpadlo</h3><p>RH řada, Smart, nebo Pro? Podle čeho zvolit výkon a typ.</p><a href="#">Číst článek →</a></div></div>
      <div class="post"><img src="%%IMG%%k-naklady-na-provoz.webp" alt=""><div><h3>Kolik stojí provoz</h3><p>Co ovlivňuje spotřebu a jak pomůže fotovoltaika.</p><a href="#">Číst článek →</a></div></div>
      <div class="post"><img src="%%IMG%%k-naklady-na-provoz.webp" alt="" style="object-position:left"><div><h3>Proč akumulační nádrž</h3><p>Delší běh kompresoru, odmrazování a připojení dalšího zdroje tepla.</p><a href="#">Číst článek →</a></div></div>
    </div>
  </div>
</section>

<section id="kontakt">
  <div class="wrap">
    <div class="center">
      <span class="eyebrow">Kontakt</span>
      <h2>Domluvíme si <span class="hand">schůzku u vás</span></h2>
      <p class="lead">Zavolejte nebo napište. Zdarma zhodnotíme situaci a doporučíme nejvhodnější řešení.</p>
    </div>
    <div class="contact">
      <div class="cinfo">
        <a class="ci" href="tel:+420774872467"><span class="ic">📞</span><div><small>Zavolejte nám</small><b>+420 774 872 467</b></div></a>
        <a class="ci" href="mailto:info@reoheating.cz"><span class="ic">✉️</span><div><small>Napište e-mail</small><b>info@reoheating.cz</b></div></a>
        <div class="ci"><span class="ic">📍</span><div><small>Sídlíme v Třinci</small><b>Schůzku si domluvte předem</b><br><small>Jsme často v terénu, ať s vámi počítáme.</small></div></div>
      </div>
      <form method="post" action="/#kontakt"><input type="hidden" name="e4h_form" value="1"><input type="text" name="web" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true">
        <label>Jméno a příjmení<input name="jmeno" required></label>
        <label>Telefon<input type="tel" name="telefon" required></label>
        <label class="full">E-mail<input type="email" name="email"></label>
        <label class="full">Adresa realizace<input name="adresa"></label>
        <label class="full">Mám zájem o
          <select name="zajem"><option>Tepelné čerpadlo RH030–RH060</option><option>REO R290 Smart (topí ze sluníčka)</option><option>Bytový dům / SVJ</option><option>Komerční objekt</option><option>RHX30 Pro / RH X50</option><option>Nerezová nádrž / bojler TUV</option><option>Fotovoltaika</option><option>Fotovoltaika + tepelné čerpadlo</option></select>
        </label>
        <label class="full">Zpráva<textarea name="zprava" rows="4"></textarea></label>
        <div class="full"><button class="btn btn-primary" type="submit">Odeslat poptávku</button></div>
        <small class="full">Osobní údaje použijeme jen pro vyřízení poptávky.</small>
      </form>
    </div>
  </div>
</section>

<footer>
  <div class="wrap">
    <div class="fgrid">
      <div><div class="logo"><svg xmlns="http://www.w3.org/2000/svg" class="logo-svg" role="img" aria-label="REO HEATING" viewBox="24 22 264 101">
  <path d="M76.07 79.02 L112.09 42.35 L126.02 55.61 L130.98 50.39 L111.91 32.25 L70.93 73.98 Z" fill="#C9C9C9"/>
  <path d="M119.98 76.11 L160.96 37.21 L202.47 78.07 L207.53 72.93 L161.04 27.19 L115.02 70.89 Z" fill="#50854D"/>
  <rect x="86" y="44.5" width="6" height="14" fill="#C9C9C9"/>
  <rect x="181" y="39.5" width="6.2" height="14" fill="#50854D"/>
  <g fill="#F0C246"><rect x="152.00" y="54.00" width="8.00" height="7.50"/><rect x="152.00" y="63.10" width="8.00" height="7.50"/><rect x="161.60" y="54.00" width="8.00" height="7.50"/><rect x="161.60" y="63.10" width="8.00" height="7.50"/><circle cx="213" cy="44.5" r="8.9"/><path d="M210.09 34.00 L213.00 27.10 L215.91 34.00 Z"/><path d="M215.73 33.95 L221.70 29.43 L220.77 36.86 Z"/><path d="M220.64 36.73 L228.07 35.80 L223.55 41.77 Z"/><path d="M223.50 41.59 L230.40 44.50 L223.50 47.41 Z"/><path d="M223.55 47.23 L228.07 53.20 L220.64 52.27 Z"/><path d="M220.77 52.14 L221.70 59.57 L215.73 55.05 Z"/><path d="M215.91 55.00 L213.00 61.90 L210.09 55.00 Z"/><path d="M210.27 55.05 L204.30 59.57 L205.23 52.14 Z"/><path d="M205.36 52.27 L197.93 53.20 L202.45 47.23 Z"/><path d="M202.50 47.41 L195.60 44.50 L202.50 41.59 Z"/><path d="M202.45 41.77 L197.93 35.80 L205.36 36.73 Z"/><path d="M205.23 36.86 L204.30 29.43 L210.27 33.95 Z"/></g>
  <path d="M34.95720338983051 116.3H31.0V88.0H40.07358757062147Q42.11214689265537 88.0 43.95084745762712 88.41970338983052Q45.789548022598865 88.83940677966102 47.168573446327684 89.75875706214688Q48.5475988700565 90.67810734463276 49.347033898305085 92.17704802259887Q50.14646892655367 93.67598870056497 50.14646892655367 95.83446327683616Q50.14646892655367 98.95225988700565 48.22782485875706 100.87090395480226Q46.309180790960454 102.78954802259886 43.27132768361582 103.30918079096045L51.18573446327683 116.3H46.389124293785315L39.19420903954802 103.70889830508474H34.95720338983051ZM34.95720338983051 100.39124293785311H39.51398305084746Q40.91299435028249 100.39124293785311 42.11214689265537 100.15141242937852Q43.311299435028246 99.91158192090396 44.21066384180791 99.37196327683615Q45.11002824858757 98.83234463276835 45.62966101694915 97.97295197740112Q46.14929378531073 97.1135593220339 46.14929378531073 95.83446327683616Q46.14929378531073 94.55536723163841 45.62966101694915 93.69597457627118Q45.11002824858757 92.83658192090395 44.25063559322034 92.31694915254238Q43.39124293785311 91.79731638418079 42.23206214689266 91.57747175141243Q41.0728813559322 91.35762711864407 39.793785310734464 91.35762711864407H34.95720338983051ZM57.93266949152542 112.78248587570621H72.72221751412428V116.3H53.97546610169491V88.0H72.12264124293785V91.47754237288136H57.93266949152542V99.95155367231638H71.28323446327683V103.34915254237288H57.93266949152542ZM104.97112994350283 102.11002824858757Q104.97112994350283 105.38771186440678 103.8319350282486 108.1257768361582Q102.69274011299436 110.86384180790961 100.69415254237289 112.84244350282486Q98.69556497175142 114.8210451977401 95.93751412429378 115.92026836158192Q93.17946327683616 117.01949152542373 89.94175141242938 117.01949152542373Q86.7040395480226 117.01949152542373 83.9659745762712 115.92026836158192Q81.22790960451978 114.8210451977401 79.22932203389831 112.84244350282486Q77.23073446327685 110.86384180790961 76.11152542372882 108.1257768361582Q74.9923163841808 105.38771186440678 74.9923163841808 102.11002824858757Q74.9923163841808 98.79237288135593 76.11152542372882 96.05430790960452Q77.23073446327685 93.3162429378531 79.22932203389831 91.37761299435027Q81.22790960451978 89.43898305084745 83.9659745762712 88.35974576271187Q86.7040395480226 87.28050847457627 89.94175141242938 87.28050847457627Q93.17946327683616 87.28050847457627 95.93751412429378 88.35974576271187Q98.69556497175142 89.43898305084745 100.69415254237289 91.37761299435027Q102.69274011299436 93.3162429378531 103.8319350282486 96.05430790960452Q104.97112994350283 98.79237288135593 104.97112994350283 102.11002824858757ZM100.69415254237289 102.11002824858757Q100.69415254237289 99.79166666666666 99.93468926553673 97.73312146892656Q99.17522598870057 95.67457627118644 97.77621468926554 94.11567796610169Q96.37720338983051 92.55677966101695 94.39860169491526 91.65741525423729Q92.42 90.75805084745762 89.94175141242938 90.75805084745762Q87.50347457627119 90.75805084745762 85.52487288135595 91.65741525423729Q83.54627118644069 92.55677966101695 82.16724576271187 94.11567796610169Q80.78822033898305 95.67457627118644 80.0287570621469 97.73312146892656Q79.26929378531074 99.79166666666666 79.26929378531074 102.11002824858757Q79.26929378531074 104.4683615819209 80.0287570621469 106.54689265536723Q80.78822033898305 108.62542372881356 82.18723163841808 110.16433615819209Q83.58624293785311 111.70324858757061 85.54485875706214 112.58262711864407Q87.50347457627119 113.46200564971751 89.94175141242938 113.46200564971751Q92.38002824858758 113.46200564971751 94.37861581920905 112.58262711864407Q96.37720338983051 111.70324858757061 97.77621468926554 110.16433615819209Q99.17522598870057 108.62542372881356 99.93468926553673 106.54689265536723Q100.69415254237289 104.4683615819209 100.69415254237289 102.11002824858757ZM117.22587570621468 88.0H121.18307909604519V99.8316384180791H135.49296610169492V88.0H139.49014124293785V116.3H135.49296610169492V103.34915254237288H121.18307909604519V116.3H117.22587570621468ZM148.7552966101695 112.78248587570621H163.54484463276836V116.3H144.79809322033898V88.0H162.94526836158192V91.47754237288136H148.7552966101695V99.95155367231638H162.10586158192092V103.34915254237288H148.7552966101695ZM168.41310734463278 116.3H164.01621468926555L176.28754237288138 88.0H179.88500000000002L192.03641242937854 116.3H187.55957627118647L184.68161016949153 109.34491525423729H171.25110169491526ZM172.6501129943503 105.86737288135593H183.2426271186441L177.9663559322034 92.59675141242937ZM204.0196468926554 116.3H200.0624435028249V91.47754237288136H190.98885593220342V88.0H213.09323446327687V91.47754237288136H204.0196468926554ZM219.240593220339 116.3H215.2833898305085V88.0H219.240593220339ZM244.49444915254242 110.62401129943503H244.5743926553673V88.0H248.5315960451978V116.3H243.53512711864414L228.58569209039553 93.19632768361582H228.50574858757068V116.3H224.54854519774017V88.0H229.70490112994355ZM275.1844632768362 93.8358757062147Q273.9053672316385 92.43686440677966 271.9267655367232 91.59745762711864Q269.94816384180797 90.75805084745762 267.5098870056498 90.75805084745762Q265.0316384180792 90.75805084745762 263.03305084745773 91.65741525423729Q261.0344632768362 92.55677966101695 259.6354519774012 94.11567796610169Q258.2364406779662 95.67457627118644 257.47697740113006 97.73312146892656Q256.71751412429387 99.79166666666666 256.71751412429387 102.11002824858757Q256.71751412429387 104.4683615819209 257.47697740113006 106.54689265536723Q258.2364406779662 108.62542372881356 259.6354519774012 110.16433615819209Q261.0344632768362 111.70324858757061 263.0730225988701 112.58262711864407Q265.11158192090403 113.46200564971751 267.6298022598871 113.46200564971751Q269.6283898305085 113.46200564971751 271.30720338983053 113.10225988700564Q272.9860169491526 112.74251412429378 274.2251412429379 112.06299435028248V104.1885593220339H267.9495762711865V100.83093220338984H278.142372881356V114.5412429378531Q275.90395480225993 115.74039548022598 273.2658192090396 116.37994350282486Q270.62768361581925 117.01949152542373 267.5098870056498 117.01949152542373Q264.19223163841815 117.01949152542373 261.4141949152543 115.92026836158192Q258.6361581920905 114.8210451977401 256.63757062146897 112.84244350282486Q254.63898305084751 110.86384180790961 253.5197740112995 108.1257768361582Q252.4005649717515 105.38771186440678 252.4005649717515 102.11002824858757Q252.4005649717515 98.79237288135593 253.53975988700574 96.05430790960452Q254.67895480225997 93.3162429378531 256.6975282485877 91.37761299435027Q258.7161016949153 89.43898305084745 261.47415254237296 88.35974576271187Q264.2322033898306 87.28050847457627 267.4699152542374 87.28050847457627Q270.86751412429385 87.28050847457627 273.5256355932204 88.279802259887Q276.183757062147 89.27909604519775 277.94251412429384 90.95790960451977Z" fill="#FFFFFF"/>
</svg>
</div><p>Úsporná řešení na míru pro Váš dům přímo od výrobce.</p></div>
      <div><h4>Produkty</h4><a href="#produkty">REO R290 RH030–RH060</a><br><a href="#produkty">REO R290 Smart</a><br><a href="#produkty">RHX30 Pro / RH X50</a><br><a href="#produkty">Nádrže</a></div>
      <div><h4>Kontakt</h4><a href="tel:+420774872467">+420 774 872 467</a><br><a href="mailto:info@reoheating.cz">info@reoheating.cz</a><br>Třinec</div>
      <div><h4>Působíme</h4>Celá Česká republika<br>a Slovensko</div>
    </div>
    <div class="fbottom"><span>© 2026 Riva Trade s.r.o. · IČ 08864811 · DIČ CZ08864811</span><a href="#">Podmínky ochrany osobních údajů</a></div>
  </div>
</footer>

<script>
function showTab(id){
  document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('active',t.dataset.tab===id));
  document.querySelectorAll('.panel').forEach(p=>p.classList.toggle('active',p.dataset.panel===id));
}
document.querySelectorAll('.tab').forEach(t=>t.addEventListener('click',()=>showTab(t.dataset.tab)));
document.querySelectorAll('.menu a[data-tab]').forEach(a=>a.addEventListener('click',()=>showTab(a.dataset.tab)));
document.querySelectorAll('[data-go]').forEach(a=>a.addEventListener('click',()=>showTab(a.dataset.go)));
document.querySelectorAll('[data-pick]').forEach(a=>a.addEventListener('click',()=>{const s=document.querySelector('form select');s.value=a.dataset.pick;}));
document.querySelectorAll('.menu a').forEach(a=>a.addEventListener('click',()=>document.getElementById('menu').classList.remove('open')));
</script>
<script>if(location.search.indexOf("odeslano=1")>-1){var b=document.querySelector("form button");if(b){b.textContent="Děkujeme, ozveme se ✓";b.disabled=true;}}</script>
</body>
</html>

E4H;
    echo str_replace('%%IMG%%', $img, $html);
    exit;
});
