<?php
/* Denní středový kurz CZK/EUR z ČNB pro energetickou kalkulačku.
   Vrací JSON {rate, date, source}. Cachuje, aby se ČNB nestahovala při každém načtení. */

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: max-age=3600');

$cacheFile = __DIR__ . '/kurz_cache.json';
$cacheTtl  = 6 * 3600;            // 6 hodin
$fallback  = 25.0;               // záložní kurz, kdyby ČNB i cache selhaly
$cnbUrl    = 'https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt';

/* 1) Platná cache → vrať rovnou */
if (is_readable($cacheFile) && (time() - filemtime($cacheFile) < $cacheTtl)) {
    echo file_get_contents($cacheFile);
    exit;
}

/* 2) Stáhni z ČNB (cURL, fallback file_get_contents) */
function stahni($url) {
    if (function_exists('curl_init')) {
        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT        => 6,
            CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_USERAGENT      => 'ThermaVera-kalkulacka/1.0',
        ]);
        $r = curl_exec($ch);
        curl_close($ch);
        if ($r !== false && $r !== '') return $r;
    }
    if (ini_get('allow_url_fopen')) {
        $ctx = stream_context_create(['http' => ['timeout' => 6]]);
        $r = @file_get_contents($url, false, $ctx);
        if ($r !== false) return $r;
    }
    return null;
}

$data = stahni($cnbUrl);
$rate = null; $date = null;

if ($data !== null) {
    $lines = preg_split('/\r?\n/', $data);
    if (!empty($lines[0])) {
        $date = trim(explode(' ', $lines[0])[0]); // např. 16.06.2026
    }
    foreach ($lines as $ln) {
        $p = explode('|', $ln);                    // země|měna|množství|kód|kurz
        if (count($p) === 5 && $p[3] === 'EUR') {
            $amount = (float) str_replace(',', '.', $p[2]);
            $kurz   = (float) str_replace(',', '.', $p[4]);
            if ($amount > 0) $rate = $kurz / $amount;
            break;
        }
    }
}

/* 3) Úspěch → ulož cache a vrať */
if ($rate !== null && $rate > 0) {
    $out = json_encode(['rate' => round($rate, 3), 'date' => $date, 'source' => 'ČNB']);
    @file_put_contents($cacheFile, $out);
    echo $out;
    exit;
}

/* 4) Selhání → poslední cache, jinak fallback */
if (is_readable($cacheFile)) {
    echo file_get_contents($cacheFile);
    exit;
}
echo json_encode(['rate' => $fallback, 'date' => null, 'source' => 'fallback']);
