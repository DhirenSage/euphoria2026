<?php

/*
 * TEMPORARY cPanel preflight checker.
 * 1. Replace CPANEL_USER.
 * 2. Upload temporarily to public_html/euphoria/preflight.php.
 * 3. Open https://sageuniversity.in/euphoria/preflight.php.
 * 4. DELETE IT IMMEDIATELY after checking.
 *
 * It deliberately does not print phpinfo(), secrets, or environment values.
 */

$privateRoot = '/home/CPANEL_USER/euphoria_app';
$requiredExtensions = ['curl', 'dom', 'fileinfo', 'gd', 'intl', 'mbstring', 'mysqli', 'openssl', 'zip'];
$checks = [
    'PHP 8.2 or newer' => version_compare(PHP_VERSION, '8.2.0', '>='),
    'Private app directory exists' => is_dir($privateRoot . '/app'),
    'Composer vendor exists' => is_file($privateRoot . '/vendor/autoload.php'),
    'CodeIgniter Paths exists' => is_file($privateRoot . '/app/Config/Paths.php'),
    'Production .env exists' => is_file($privateRoot . '/.env'),
    'Writable directory is writable' => is_writable($privateRoot . '/writable'),
];

foreach ($requiredExtensions as $extension) {
    $checks['PHP extension: ' . $extension] = extension_loaded($extension);
}

$allPassed = ! in_array(false, $checks, true);
header('Content-Type: text/html; charset=UTF-8');
header('X-Robots-Tag: noindex, nofollow');
?>
<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>EUPHORIA cPanel Preflight</title></head>
<body style="margin:0;background:#0f172a;color:#e2e8f0;font-family:system-ui;padding:30px">
<main style="max-width:760px;margin:auto"><h1>EUPHORIA cPanel Preflight</h1><p>PHP <?= htmlspecialchars(PHP_VERSION, ENT_QUOTES, 'UTF-8') ?></p>
<table style="width:100%;border-collapse:collapse;background:#111827"><?php foreach ($checks as $label => $passed): ?><tr><td style="padding:12px;border-bottom:1px solid #334155"><?= htmlspecialchars($label, ENT_QUOTES, 'UTF-8') ?></td><td style="padding:12px;border-bottom:1px solid #334155;color:<?= $passed ? '#86efac' : '#fca5a5' ?>;font-weight:bold"><?= $passed ? 'PASS' : 'FAIL' ?></td></tr><?php endforeach ?></table>
<p style="padding:14px;background:<?= $allPassed ? '#14532d' : '#7f1d1d' ?>;font-weight:bold"><?= $allPassed ? 'Server is ready for application testing.' : 'Resolve every FAIL before going live.' ?></p>
<p style="color:#fbbf24"><strong>Delete this file from public_html immediately after checking.</strong></p></main></body></html>