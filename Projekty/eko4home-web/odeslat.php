<?php
/* Odeslání poptávky z formuláře na eko4home.cz (statická verze webu). Funkce mail() na hostingu. */
$PRIJEMCE   = 'info@reoheating.cz';   // kam chodí poptávky
$ODESILATEL = 'info@eko4home.cz';     // From – musí být na doméně webu (eko4home.cz)
$TELEFON    = '+420 774 872 467';

header('Content-Type: application/json; charset=utf-8');
function fail($m){ http_response_code(400); echo json_encode(['ok'=>false,'error'=>$m]); exit; }
function clean($v){ return trim(str_replace(["\r","\n","%0a","%0d"],' ',(string)$v)); }

if ($_SERVER['REQUEST_METHOD'] !== 'POST') fail('Neplatný požadavek.');
if (!empty($_POST['web'])) { echo json_encode(['ok'=>true]); exit; }   // honeypot

$jmeno = clean($_POST['jmeno'] ?? ''); $tel = clean($_POST['telefon'] ?? ''); $email = clean($_POST['email'] ?? '');
if ($jmeno === '') fail('Vyplňte prosím jméno.');
if ($tel === '') fail('Vyplňte prosím telefon.');
if ($email !== '' && !filter_var($email, FILTER_VALIDATE_EMAIL)) fail('Zadejte prosím platný e-mail.');

$telo  = "Nová poptávka z webu eko4home.cz\n" . str_repeat('-', 40) . "\n\n";
foreach (['Jméno a příjmení'=>$jmeno,'Telefon'=>$tel,'E-mail'=>$email,
          'Adresa realizace'=>clean($_POST['adresa'] ?? ''),'Zájem'=>clean($_POST['zajem'] ?? '')] as $k=>$v)
  $telo .= $k . ': ' . ($v !== '' ? $v : '—') . "\n";
$z = trim((string)($_POST['zprava'] ?? '')); $telo .= "\nZpráva:\n" . ($z !== '' ? $z : '—') . "\n";

$predmet = '=?UTF-8?B?' . base64_encode('Poptávka z webu eko4home.cz – ' . $jmeno) . '?=';
$h  = 'From: Web eko4home.cz <' . $ODESILATEL . ">\r\n";
if ($email !== '') $h .= 'Reply-To: ' . $jmeno . ' <' . $email . ">\r\n";
$h .= "MIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: 8bit\r\n";

if (@mail($PRIJEMCE, $predmet, $telo, $h, '-f' . $ODESILATEL)) {
  if ($email !== '') {
    $ap = '=?UTF-8?B?' . base64_encode('Děkujeme za poptávku – REO HEATING') . '?=';
    $at = "Dobrý den,\n\nděkujeme za vaši poptávku, co nejdříve se vám ozveme.\n\nS pozdravem\nREO HEATING\ninfo@reoheating.cz | $TELEFON\n";
    @mail($email, $ap, $at, 'From: REO HEATING <' . $ODESILATEL . ">\r\nReply-To: info@reoheating.cz\r\nMIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: 8bit\r\n", '-f' . $ODESILATEL);
  }
  echo json_encode(['ok'=>true]);
} else fail('E-mail se nepodařilo odeslat.');
