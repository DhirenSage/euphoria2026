<main class="scanner-shell" data-testid="scanner-console">
  <header class="scanner-header"><a class="brand" href="<?= base_url() ?>"><span class="brand-mark">S</span><span>EUPHORIA <strong>ENTRY</strong></span></a><form method="post" action="<?= base_url('scanner/logout') ?>"><input type="hidden" name="<?= csrf_token() ?>" value="<?= csrf_hash() ?>"><button class="text-link" type="submit" data-testid="scanner-logout-button">Sign out ↗</button></form></header>
  <section class="scanner-stage">
    <div class="scanner-heading"><div><span class="eyebrow accent" data-testid="scanner-mode">AUTO EVENT ENTRY / DATABASE LIVE</span><h1>SCAN.<br><em>THAT'S IT.</em></h1><p>Scan any EUPHORIA pass. Event and today's configured event day are detected automatically—no event, day or gate selection.</p></div><div class="scanner-tools"><button type="button" data-sound-toggle data-testid="scanner-sound-toggle">Sound on</button><button type="button" data-torch-toggle data-testid="scanner-torch-toggle">Torch</button><button type="button" data-fullscreen-toggle data-testid="scanner-fullscreen-toggle">Fullscreen</button></div></div>
    <div class="scanner-auto-date"><span>SERVER DATE</span><strong data-testid="scanner-server-date"><?= esc($serverDate) ?></strong><small>No gate selection required</small></div>
    <div class="scanner-workspace">
      <form class="scanner-card" data-scanner-form data-scan-url="<?= base_url('scanner/scan') ?>" data-csrf-name="<?= csrf_token() ?>" data-csrf-value="<?= csrf_hash() ?>" data-testid="scanner-form">
        <div class="scanner-camera"><div id="qr-reader" data-testid="scanner-camera"></div><p data-camera-message>Camera is off. Open it and point directly at any EUPHORIA QR.</p><div class="scanner-camera-actions"><button class="button button-yellow" type="button" data-camera-start data-testid="scanner-camera-start">Open camera & scan</button><label class="button button-ghost">Upload QR image<input type="file" accept="image/*" hidden data-image-input data-testid="scanner-image-input"></label></div></div>
        <label>Manual secure token<input name="token" placeholder="EUPHORIA-…" autocomplete="off" data-testid="scanner-token-input"></label>
        <button class="button button-yellow full" type="submit" data-testid="scanner-submit">Verify and record today's entry ↗</button>
      </form>
      <article class="scanner-result" data-scanner-result data-testid="scanner-result"><span class="scanner-result-icon">⌁</span><strong>WAITING FOR A PASS</strong><p>Event and eligible day routing happen automatically.</p></article>
    </div>
  </section>
</main>