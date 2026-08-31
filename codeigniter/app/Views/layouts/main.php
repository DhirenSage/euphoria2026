<!doctype html>
<html lang="en" class="dark">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title><?= esc($title ?? 'EUPHORIA 2026') ?></title>
    <meta name="description" content="EUPHORIA 2026 — SAGE University Indore's mega student festival.">
    <meta name="csrf-token" content="<?= csrf_hash() ?>">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="<?= base_url('css/app.css') ?>">
</head>
<body>
<header class="site-header" data-testid="site-header">
    <a class="brand" href="<?= base_url('/') ?>" data-testid="brand-home-link"><span class="brand-mark">S</span><span>SAGE / <strong>EUPHORIA</strong></span></a>
    <nav class="main-nav" data-testid="main-navigation">
        <a href="<?= base_url('events') ?>" data-testid="nav-events-link">Events</a><a href="<?= base_url('gallery') ?>" data-testid="nav-gallery-link">Gallery</a><a href="<?= base_url('about-euphoria') ?>" data-testid="nav-about-link">About</a>
    </nav>
    <div class="header-actions"><a class="text-link" href="<?= base_url('login') ?>" data-testid="nav-login-link">Admin <span>↗</span></a><a class="button button-yellow button-small" href="<?= base_url('events') ?>" data-testid="nav-register-link">Register <span>↗</span></a></div>
</header>
<?php if ($message = session('message')): ?><div class="flash flash-success" data-testid="flash-success"><?= esc($message) ?></div><?php endif ?>
<?php if ($error = session('error')): ?><div class="flash flash-error" data-testid="flash-error"><?= esc($error) ?></div><?php endif ?>
<?= $content ?>
<footer class="site-footer"><div><span class="eyebrow">SAGE UNIVERSITY INDORE</span><h2>Make your<br><em>moment.</em></h2></div><div class="footer-meta"><span class="mono">EUPHORIA / 2026</span><span>Culture · Sport · Code · Create</span><span>© SAGE University Indore</span></div></footer>
<script src="<?= base_url('js/app.js') ?>"></script>
</body>
</html>