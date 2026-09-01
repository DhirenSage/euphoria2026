<main class="auth-page scanner-auth">
  <div class="auth-panel">
    <?= view('partials/official_logos', ['variant'=>'auth']) ?>
    <span class="eyebrow accent">ENTRY OPERATIONS / SCANNER</span>
    <h1>Open<br><em>the gate.</em></h1>
    <p>Authorized staff only. Your assignment controls the event, day and gate you can scan.</p>
    <form method="post" action="<?= base_url('scanner/login') ?>" data-testid="scanner-login-form">
      <input type="hidden" name="<?= csrf_token() ?>" value="<?= csrf_hash() ?>">
      <label>Staff email<input type="email" name="email" required data-testid="scanner-email-input"></label>
      <label>Password<input type="password" name="password" required data-testid="scanner-password-input"></label>
      <button class="button button-yellow full-width" type="submit" data-testid="scanner-login-submit">Start scanner <span>↗</span></button>
    </form>
    <a href="<?= base_url('/') ?>" class="text-link">← Public site</a>
  </div>
  <div class="auth-art scanner-art"><div class="auth-art-copy"><span class="mono">GATE / 01</span><h2>Fast.<br>Focused.<br>Fair.</h2></div></div>
</main>