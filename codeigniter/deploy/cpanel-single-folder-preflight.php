<?php

/*
 * TEMPORARY single-folder cPanel preflight checker.
 * Upload as /public_html/euphoria/preflight.php, open it once, then DELETE it.
 * It never displays phpinfo(), credentials, or environment values.
 */

$root = __DIR__;
$envText = is_file($root . '/.env') ? (string) file_get_contents($root . '/.env') : '';
$envValue = static function (string $key) use ($envText): string {
    if (! preg_match('/^\s*' . preg_quote($key, '/') . '\s*=\s*[\'\"]?([^\'\"\r\n]+)[\'\"]?\s*$/mi', $envText, $matches)) return '';
    return trim($matches[1]);
};
$configured = static function (string $key) use ($envValue): bool {
    $value = $envValue($key);
    return $value !== '' && ! str_contains(strtoupper($value), 'REPLACE_');
};
$requiredExtensions = ['curl', 'dom', 'fileinfo', 'gd', 'intl', 'mbstring', 'mysqli', 'openssl', 'simplexml', 'zip'];
$checks = [
    'PHP 8.2 or newer' => version_compare(PHP_VERSION, '8.2.0', '>='),
    'Application source exists' => is_file($root . '/app/Config/Paths.php'),
    'Composer dependencies exist' => is_file($root . '/vendor/autoload.php'),
    'Production .env exists' => is_file($root . '/.env'),
    'Writable directory exists' => is_dir($root . '/writable'),
    'Writable directory is writable' => is_writable($root . '/writable'),
    'Root front controller exists' => is_file($root . '/index.php'),
    'Root .htaccess exists' => is_file($root . '/.htaccess'),
    'Production mode enabled' => strtolower($envValue('CI_ENVIRONMENT')) === 'production',
    'Easebuzz live mode enabled' => strtolower($envValue('EASEBUZZ_ENV')) === 'prod' && strtolower($envValue('PAYMENT_MODE')) === 'gateway',
    'Easebuzz live key configured' => $configured('EASEBUZZ_KEY'),
    'Easebuzz live salt configured' => $configured('EASEBUZZ_SALT'),
    'SMTP account configured' => $configured('email.SMTPUser') && $configured('email.SMTPPass'),
];

foreach ($requiredExtensions as $extension) {
    $checks['PHP extension: ' . $extension] = extension_loaded($extension);
}

$allPassed = ! in_array(false, $checks, true);
header('Content-Type: text/html; charset=UTF-8');
header('X-Robots-Tag: noindex, nofollow');
header('Cache-Control: no-store');
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>EUPHORIA cPanel Preflight</title>
</head>
<body style="margin:0;background:#0f172a;color:#e2e8f0;font-family:system-ui;padding:30px">
<main style="max-width:760px;margin:auto">
    <h1>EUPHORIA single-folder preflight</h1>
    <p>PHP <?= htmlspecialchars(PHP_VERSION, ENT_QUOTES, 'UTF-8') ?></p>
    <table style="width:100%;border-collapse:collapse;background:#111827">
        <?php foreach ($checks as $label => $passed): ?>
            <tr>
                <td style="padding:12px;border-bottom:1px solid #334155"><?= htmlspecialchars($label, ENT_QUOTES, 'UTF-8') ?></td>
                <td style="padding:12px;border-bottom:1px solid #334155;color:<?= $passed ? '#86efac' : '#fca5a5' ?>;font-weight:bold"><?= $passed ? 'PASS' : 'FAIL' ?></td>
            </tr>
        <?php endforeach ?>
    </table>
    <p style="padding:14px;background:<?= $allPassed ? '#14532d' : '#7f1d1d' ?>;font-weight:bold"><?= $allPassed ? 'Server files and PHP modules are ready for application testing.' : 'Resolve every FAIL before going live.' ?></p>
    <p style="color:#fbbf24"><strong>Delete preflight.php immediately after checking.</strong></p>
</main>
</body>
</html>