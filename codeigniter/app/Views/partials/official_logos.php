<?php $variant = $variant ?? 'header'; ?>
<span class="official-logo-lockup official-logo-lockup--<?= esc($variant) ?>" data-testid="official-logo-lockup">
  <img class="official-sage-logo" src="https://customer-assets-gfyr7b9c.emergentagent.net/job_sage-mega-fest/artifacts/0yfnekpb_logotechweek.png" alt="SAGE University Indore" <?= $variant === 'email' ? '' : 'loading="eager"' ?>>
  <span class="official-logo-divider" aria-hidden="true"></span>
  <img class="official-euphoria-logo" src="https://customer-assets-gfyr7b9c.emergentagent.net/job_sage-mega-fest/artifacts/vevgaaxu_euphorialogo.png" alt="EUPHORIA — Joy of Colours" <?= $variant === 'email' ? '' : 'loading="eager"' ?>>
</span>