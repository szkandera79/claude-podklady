<?php
/* Odeslání poptávky z formuláře na eko4home.cz (statická verze webu). Kontroly a antispam v antispam-lib.php. */
require __DIR__ . '/antispam-lib.php';

$PRIJEMCE   = 'info@reoheating.cz';   // kam chodí poptávky
$ODESILATEL = 'info@eko4home.cz';     // From – musí být na doméně webu (eko4home.cz)
$TELEFON    = '+420 774 872 467';

header('Content-Type: application/json; charset=utf-8');
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo json_encode(['ok' => false, 'error' => 'Neplatný požadavek.']); exit; }

$r = e4h_check($_POST, $_SERVER['REMOTE_ADDR'] ?? '');
if (!$r['ok']) { http_response_code(400); echo json_encode(['ok' => false, 'error' => $r['error']]); exit; }
if ($r['spam']) { echo json_encode(['ok' => true]); exit; }   // robotovi neprozradíme, že byl odhalen

$pole = $r['pole'];
$h  = 'From: Web eko4home.cz <' . $ODESILATEL . ">\r\n";
if ($pole['E-mail'] !== '') $h .= 'Reply-To: ' . $pole['Jméno a příjmení'] . ' <' . $pole['E-mail'] . ">\r\n";
$h .= "MIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: 8bit\r\n";
$predmet = '=?UTF-8?B?' . base64_encode(e4h_predmet($pole)) . '?=';

if (@mail($PRIJEMCE, $predmet, e4h_telo($pole), $h, '-f' . $ODESILATEL)) {
  if ($pole['E-mail'] !== '') {
    $ap = '=?UTF-8?B?' . base64_encode('Děkujeme za poptávku – REO HEATING') . '?=';
    $at = "Dobrý den,\n\nděkujeme za vaši poptávku, co nejdříve se vám ozveme.\n\nS pozdravem\nREO HEATING\ninfo@reoheating.cz | $TELEFON\n";
    @mail($pole['E-mail'], $ap, $at, 'From: REO HEATING <' . $ODESILATEL . ">\r\nReply-To: info@reoheating.cz\r\nMIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: 8bit\r\n", '-f' . $ODESILATEL);
  }
  echo json_encode(['ok' => true]);
} else {
  http_response_code(500); echo json_encode(['ok' => false, 'error' => 'E-mail se nepodařilo odeslat, zavolejte nám prosím ' . $TELEFON . '.']);
}
