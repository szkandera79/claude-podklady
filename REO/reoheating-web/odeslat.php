<?php
/* Odeslání poptávky z kontaktního formuláře REO HEATING
   Posílá e-mail na adresu níže. Funguje na běžném PHP hostingu (funkce mail()). */

$PRIJEMCE   = 'info@reoheating.cz';   // hlavní příjemce poptávek
$KOPIE      = '';                     // kopie (Cc) – nech prázdné '' pro vypnutí
$ODESILATEL = 'info@reoheating.cz';   // From – musí být na doméně webu
$TELEFON    = '+420 774 872 467';

header('Content-Type: application/json; charset=utf-8');

function fail($msg) { http_response_code(400); echo json_encode(['ok' => false, 'error' => $msg]); exit; }
function clean($v) { return trim(str_replace(["\r", "\n", "%0a", "%0d"], ' ', (string)$v)); } // proti header injection

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { fail('Neplatný požadavek.'); }

/* Honeypot – když je vyplněný skrytý "website", je to bot → tváříme se OK, ale nic neposíláme */
if (!empty($_POST['website'])) { echo json_encode(['ok' => true]); exit; }

$jmeno = clean($_POST['jmeno'] ?? '');
$email = clean($_POST['email'] ?? '');

if ($jmeno === '') { fail('Vyplňte prosím jméno.'); }
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) { fail('Zadejte prosím platný e-mail.'); }
if (empty($_POST['souhlas'])) { fail('Je potřeba souhlas se zpracováním osobních údajů.'); }

$pole = [
  'Jméno a příjmení'         => $jmeno,
  'E-mail'                   => $email,
  'Telefon'                  => clean($_POST['tel'] ?? ''),
  'Typ objektu'              => clean($_POST['typ'] ?? ''),
  'Současný zdroj tepla'     => clean($_POST['zdroj'] ?? ''),
  'Místo realizace'          => clean($_POST['misto'] ?? ''),
  'Roční spotřeba / náklady' => clean($_POST['spotreba'] ?? ''),
];

$telo  = "Nová poptávka z webu reoheating.cz\n";
$telo .= str_repeat('-', 40) . "\n\n";
foreach ($pole as $label => $val) {
  $telo .= $label . ": " . ($val !== '' ? $val : '—') . "\n";
}
$pozn = trim((string)($_POST['pozn'] ?? ''));
$telo .= "\nZpráva:\n" . ($pozn !== '' ? $pozn : '—') . "\n";

$predmet = '=?UTF-8?B?' . base64_encode('Nová poptávka z webu – ' . $jmeno) . '?=';

$hlavicky  = 'From: REO HEATING web <' . $ODESILATEL . ">\r\n";
$hlavicky .= 'Reply-To: ' . $jmeno . ' <' . $email . ">\r\n";
if ($KOPIE !== '') { $hlavicky .= 'Cc: ' . $KOPIE . "\r\n"; }
$hlavicky .= "MIME-Version: 1.0\r\n";
$hlavicky .= "Content-Type: text/plain; charset=UTF-8\r\n";
$hlavicky .= "Content-Transfer-Encoding: 8bit\r\n";

$odeslano = @mail($PRIJEMCE, $predmet, $telo, $hlavicky, '-f' . $ODESILATEL);

/* Automatický potvrzovací e-mail tazateli */
if ($odeslano) {
  $arPredmet = '=?UTF-8?B?' . base64_encode('Děkujeme za vaši poptávku – REO HEATING') . '?=';
  $arTelo = "Dobrý den,\n\nděkujeme za vaši poptávku. Obdrželi jsme ji a co nejdříve se vám ozveme.\n\n"
          . "S pozdravem\nREO HEATING\ninfo@reoheating.cz | " . $TELEFON . "\n";
  $arHlavicky  = 'From: REO HEATING <' . $ODESILATEL . ">\r\n";
  $arHlavicky .= 'Reply-To: ' . $ODESILATEL . "\r\n";
  $arHlavicky .= "MIME-Version: 1.0\r\n";
  $arHlavicky .= "Content-Type: text/plain; charset=UTF-8\r\n";
  $arHlavicky .= "Content-Transfer-Encoding: 8bit\r\n";
  @mail($email, $arPredmet, $arTelo, $arHlavicky, '-f' . $ODESILATEL);

  echo json_encode(['ok' => true]);
} else {
  fail('E-mail se nepodařilo odeslat.');
}
