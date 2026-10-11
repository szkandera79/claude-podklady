<?php
/* Odeslání poptávky z kontaktního formuláře ThermaVera Energy
   Posílá e-mail na adresu níže. Funguje na PHP hostingu web4u (funkce mail()). */

$PRIJEMCE = 'info@thermavera.cz';     // hlavní příjemce poptávek
$KOPIE = 'szkandera@rivatrade.cz';    // kopie (Cc) – nech prázdné '' pro vypnutí
$ODESILATEL = 'info@thermavera.cz';   // From – musí být na doméně webu

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
  'Jméno a příjmení'   => $jmeno,
  'Firma / obec / SVJ' => clean($_POST['firma'] ?? ''),
  'E-mail'             => $email,
  'Telefon'            => clean($_POST['tel'] ?? ''),
  'Typ objektu'        => clean($_POST['typ'] ?? ''),
  'Současný zdroj tepla' => clean($_POST['zdroj'] ?? ''),
  'Roční spotřeba / náklady' => clean($_POST['spotreba'] ?? ''),
  'Místo realizace'    => clean($_POST['misto'] ?? ''),
  'Zájem o model'      => clean($_POST['model'] ?? ''),
];

$telo  = "Nová poptávka z webu thermavera.cz\n";
$telo .= str_repeat('-', 40) . "\n\n";
foreach ($pole as $label => $val) {
  $telo .= $label . ": " . ($val !== '' ? $val : '—') . "\n";
}
$pozn = trim((string)($_POST['pozn'] ?? ''));
$telo .= "\nPoznámka:\n" . ($pozn !== '' ? $pozn : '—') . "\n";

$predmet = '=?UTF-8?B?' . base64_encode('Nová poptávka z webu – ' . $jmeno) . '?=';

$hlavicky  = 'From: ThermaVera web <' . $ODESILATEL . ">\r\n";
$hlavicky .= 'Reply-To: ' . $jmeno . ' <' . $email . ">\r\n";
if ($KOPIE !== '') { $hlavicky .= 'Cc: ' . $KOPIE . "\r\n"; }
$hlavicky .= "MIME-Version: 1.0\r\n";
$hlavicky .= "Content-Type: text/plain; charset=UTF-8\r\n";
$hlavicky .= "Content-Transfer-Encoding: 8bit\r\n";

$odeslano = @mail($PRIJEMCE, $predmet, $telo, $hlavicky, '-f' . $ODESILATEL);

/* Automatický potvrzovací e-mail tazateli (v jeho jazyce) */
if ($odeslano) {
  $lang = in_array(($_POST['lang'] ?? 'cs'), ['cs','en','de','pl'], true) ? $_POST['lang'] : 'cs';
  $ar = [
    'cs' => ['Děkujeme za vaši poptávku – ThermaVera Energy',
             "Dobrý den,\n\nděkujeme za vaši poptávku. Obdrželi jsme ji a co nejdříve se vám ozveme.\n\nS pozdravem\nThermaVera Energy\ninfo@thermavera.cz | +420 774 872 467"],
    'en' => ['Thank you for your enquiry – ThermaVera Energy',
             "Hello,\n\nthank you for your enquiry. We have received it and will get back to you as soon as possible.\n\nKind regards,\nThermaVera Energy\ninfo@thermavera.cz | +420 774 872 467"],
    'de' => ['Danke für Ihre Anfrage – ThermaVera Energy',
             "Guten Tag,\n\nvielen Dank für Ihre Anfrage. Wir haben sie erhalten und melden uns so bald wie möglich bei Ihnen.\n\nMit freundlichen Grüßen\nThermaVera Energy\ninfo@thermavera.cz | +420 774 872 467"],
    'pl' => ['Dziękujemy za zapytanie – ThermaVera Energy',
             "Dzień dobry,\n\ndziękujemy za zapytanie. Otrzymaliśmy je i odezwiemy się najszybciej, jak to możliwe.\n\nZ poważaniem\nThermaVera Energy\ninfo@thermavera.cz | +420 774 872 467"],
  ];
  $arPredmet = '=?UTF-8?B?' . base64_encode($ar[$lang][0]) . '?=';
  $arHlavicky  = 'From: ThermaVera Energy <' . $ODESILATEL . ">\r\n";
  $arHlavicky .= 'Reply-To: ' . $ODESILATEL . "\r\n";
  $arHlavicky .= "MIME-Version: 1.0\r\n";
  $arHlavicky .= "Content-Type: text/plain; charset=UTF-8\r\n";
  $arHlavicky .= "Content-Transfer-Encoding: 8bit\r\n";
  @mail($email, $arPredmet, $ar[$lang][1], $arHlavicky, '-f' . $ODESILATEL);

  echo json_encode(['ok' => true]);
} else {
  fail('E-mail se nepodařilo odeslat.');
}
