<main class="auth-page">
  <div class="auth-panel">
    <?= view('partials/official_logos', ['variant'=>'auth']) ?>
    <span class="eyebrow accent">ADMINISTRATION / SECURE ACCESS</span>
    <h1>Command<br><em>access.</em></h1>
    <p>Sign in to manage events, registrations, payments and entry operations.</p>
    <form method="post" action="<?= base_url('login') ?>" data-testid="admin-login-form">
      <input type="hidden" name="<?= csrf_token() ?>" value="<?= csrf_hash() ?>">
      <label>Work email<input type="email" name="email" required data-testid="admin-email-input"></label>
      <label>Password<input type="password" name="password" required data-testid="admin-password-input"></label>
      <button class="button button-yellow full-width" type="submit" data-testid="admin-login-submit">Enter command centre <span>↗</span></button>
    </form>
    <a href="<?= base_url('/') ?>" class="text-link">← Return to public site</a>
  </div>
  <div class="auth-art"><div class="auth-art-copy"><span class="mono">OPS / 01</span><h2>Every moment<br>counts.</h2></div></div>
</main>