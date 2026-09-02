<main class="page-shell pass-page">
  <div class="pass-intro">
    <?= view('partials/official_logos', ['variant'=>'pass']) ?>
    <span class="eyebrow accent">DIGITAL EVENT PASS</span>
    <h1>Show up<br><em>bright.</em></h1>
    <div class="pass-actions"><button type="button" class="text-link print-pass-trigger" data-testid="print-pass-button">Print / save pass ↗</button><a href="<?= base_url('pass/'.$registration['registration_id'].'/download').($passAccess!==''?'?key='.rawurlencode($passAccess):'') ?>" class="text-link" data-testid="download-pass-button">Download PDF ↓</a></div>
  </div>
  <div class="pass-card" data-testid="digital-pass-card">
    <div class="pass-card-top"><div><?= view('partials/official_logos', ['variant'=>'pass-card']) ?></div><span class="pass-stamp" data-testid="pass-status">ACTIVE</span></div>
    <div class="pass-card-event"><span class="eyebrow">EVENT</span><strong><?= esc($registration['event_name']) ?></strong><span><?= esc($registration['category_name']) ?></span></div>
    <div class="pass-card-details">
      <div><span class="eyebrow">PASS HOLDER</span><strong><?= esc($registration['participant_name']) ?></strong></div>
      <div><span class="eyebrow">REGISTRATION ID</span><strong class="mono"><?= esc($registration['registration_id']) ?></strong></div>
      <div><span class="eyebrow">VENUE</span><strong><?= esc($registration['venue'] ?: 'SAGE University Indore') ?></strong></div>
      <div><span class="eyebrow">DATE</span><strong><?= $registration['event_start'] ? esc(date('d M Y', strtotime($registration['event_start']))) : 'TBA' ?></strong></div>
    </div>
    <div class="qr-wrap"><img src="<?= esc($qr) ?>" alt="Secure QR pass" data-testid="pass-qr-image"><span class="mono">SCAN AT ENTRY / KEEP THIS PASS READY</span><code class="sr-only" data-testid="pass-qr-token"><?= esc($token) ?></code></div>
  </div>
</main>