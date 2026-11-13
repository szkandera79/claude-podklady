<?php
/* Antispam a kontrola poptávky z webu eko4home.cz – sdílí statická verze (odeslat.php)
   i verze pro WordPress (snippet). Vrací ['ok'=>bool, 'error'=>string, 'spam'=>bool, 'pole'=>[...] ]. */

// Cloudflare Turnstile – tajný klíč (prázdný = ověření vypnuto). Veřejný klíč patří do E4H_TS v index.html.
if (!defined('E4H_TURNSTILE_SECRET')) define('E4H_TURNSTILE_SECRET', '');
if (!defined('E4H_RATE_LIMIT'))       define('E4H_RATE_LIMIT', 3);      // max. poptávek z jedné IP za hodinu
if (!defined('E4H_MIN_SECONDS'))      define('E4H_MIN_SECONDS', 4);     // formulář vyplněný rychleji = robot

function e4h_clean($v) { return trim(str_replace(["\r", "\n", "%0a", "%0d"], ' ', (string)$v)); }

function e4h_check(array $p, string $ip): array {
  $bad = function ($m) { return ['ok' => false, 'error' => $m, 'spam' => false, 'pole' => []]; };
  $spam = ['ok' => true, 'error' => '', 'spam' => true, 'pole' => []];   // tváříme se OK, nic neposíláme

  // 1) honeypot + časová past
  if (!empty($p['web'])) return $spam;
  $t = (int)($p['t'] ?? 0);
  if ($t <= 0 || time() - $t < E4H_MIN_SECONDS || time() - $t > 86400) return $spam;

  // 2) omezení počtu odeslání z jedné IP
  $rl = sys_get_temp_dir() . '/e4h_rl_' . sha1($ip);
  $hist = array_filter(json_decode(@file_get_contents($rl) ?: '[]', true) ?: [], function ($x) { return $x > time() - 3600; });
  if (count($hist) >= E4H_RATE_LIMIT) return $bad('Z tohoto připojení už přišlo několik poptávek. Zkuste to prosím později nebo nám zavolejte.');

  // 3) Cloudflare Turnstile
  if (E4H_TURNSTILE_SECRET !== '') {
    $resp = (string)($p['cf-turnstile-response'] ?? '');
    if ($resp === '') return $bad('Potvrďte prosím ověření, že nejste robot.');
    $ctx = stream_context_create(['http' => ['method' => 'POST', 'timeout' => 8,
      'header' => "Content-Type: application/x-www-form-urlencoded\r\n",
      'content' => http_build_query(['secret' => E4H_TURNSTILE_SECRET, 'response' => $resp, 'remoteip' => $ip])]]);
    $r = json_decode(@file_get_contents('https://challenges.cloudflare.com/turnstile/v0/siteverify', false, $ctx) ?: '{}', true);
    if (empty($r['success'])) return $bad('Ověření se nezdařilo, obnovte prosím stránku a zkuste to znovu.');
  }

  // 4) povinná pole a jejich formát
  $jmeno = e4h_clean($p['jmeno'] ?? '');
  $tel   = preg_replace('/[\s().\/-]/', '', (string)($p['telefon'] ?? ''));
  $email = e4h_clean($p['email'] ?? '');
  $psc   = preg_replace('/\s/', '', (string)($p['psc'] ?? ''));
  $objekt = e4h_clean($p['objekt'] ?? ''); $vyt = e4h_clean($p['vytapeni'] ?? '');
  $plocha = preg_replace('/\D/', '', (string)($p['plocha'] ?? ''));
  $zprava = trim((string)($p['zprava'] ?? '')); $adresa = e4h_clean($p['adresa'] ?? '');

  if (mb_strlen($jmeno) < 2 || mb_strlen($jmeno) > 80) return $bad('Vyplňte prosím jméno a příjmení.');
  // ČR/SK: +420/+421/00420/00421, nebo 9 číslic (ČR), nebo 0 + 9 číslic (SK zápis 0905 …)
  if (preg_match('/^(?:(?:00|\+)?(420|421))?(0?)([1-9]\d{8})$/', $tel, $m) !== 1) return $bad('Zadejte prosím platné telefonní číslo (ČR nebo SK).');
  $pred = $m[1] !== '' ? $m[1] : ($m[2] === '0' ? '421' : '420');
  $tel = '+' . $pred . ' ' . implode(' ', str_split($m[3], 3));
  if ($email !== '' && !filter_var($email, FILTER_VALIDATE_EMAIL)) return $bad('Zadejte prosím platný e-mail, nebo pole nechte prázdné.');
  if (preg_match('/^\d{5}$/', $psc) !== 1) return $bad('Zadejte prosím PSČ místa realizace (5 číslic).');
  if ($objekt === '') return $bad('Vyberte prosím typ objektu.');
  if ($vyt === '') return $bad('Vyberte prosím současné vytápění.');
  if (empty($p['souhlas'])) return $bad('Je potřeba souhlas se zpracováním osobních údajů.');
  if (mb_strlen($zprava) > 2000) return $bad('Zpráva je příliš dlouhá.');

  // 5) typické znaky spamu – odkazy, azbuka, jednorázové e-maily
  $vse = $jmeno . ' ' . $zprava . ' ' . $adresa;
  if (preg_match('~(https?://|www\.|\[url|<a\s|\.(ru|xyz|top|click|info)\b)~i', $vse)) return $spam;
  if (preg_match('/\p{Cyrillic}/u', $vse)) return $spam;
  $jednoraz = ['mailinator.com','guerrillamail.com','10minutemail.com','temp-mail.org','yopmail.com','trashmail.com','sharklasers.com','getnada.com','dispostable.com','maildrop.cc'];
  if ($email !== '' && in_array(strtolower(substr(strrchr($email, '@'), 1)), $jednoraz, true)) return $bad('Použijte prosím běžnou e-mailovou adresu.');

  $hist[] = time(); @file_put_contents($rl, json_encode(array_values($hist)));

  // PSČ: ČR 1xxxx–7xxxx, SK 0xxxx / 8xxxx / 9xxxx
  $zeme = in_array($psc[0], ['0', '8', '9'], true) ? 'SK' : 'CZ';
  return ['ok' => true, 'error' => '', 'spam' => false, 'pole' => [
    'Jméno a příjmení' => $jmeno, 'Telefon' => $tel, 'E-mail' => $email,
    'PSČ' => substr($psc, 0, 3) . ' ' . substr($psc, 3) . " ($zeme)", 'Adresa realizace' => $adresa,
    'Typ objektu' => $objekt, 'Současné vytápění' => $vyt, 'Vytápěná plocha' => $plocha !== '' ? "$plocha m²" : '',
    'Zájem' => e4h_clean($p['zajem'] ?? ''), 'Zpráva' => $zprava,
  ]];
}

function e4h_predmet(array $pole): string {
  return 'Poptávka eko4home.cz – ' . $pole['Typ objektu'] . ', PSČ ' . $pole['PSČ'] . ' – ' . $pole['Jméno a příjmení'];
}

function e4h_telo(array $pole): string {
  $t = "Nová poptávka z webu eko4home.cz\n" . str_repeat('-', 40) . "\n\n";
  foreach ($pole as $k => $v) { if ($k !== 'Zpráva') $t .= $k . ': ' . ($v !== '' ? $v : '—') . "\n"; }
  return $t . "\nZpráva:\n" . ($pole['Zpráva'] !== '' ? $pole['Zpráva'] : '—') . "\n";
}
