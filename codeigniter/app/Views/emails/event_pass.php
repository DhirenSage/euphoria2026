<div style="font-family:Arial,sans-serif;color:#111">
  <div style="background:#111;padding:16px">
    <img src="https://customer-assets-gfyr7b9c.emergentagent.net/job_sage-mega-fest/artifacts/0yfnekpb_logotechweek.png" alt="SAGE University Indore" width="160" style="vertical-align:middle">
    <img src="https://customer-assets-gfyr7b9c.emergentagent.net/job_sage-mega-fest/artifacts/vevgaaxu_euphorialogo.png" alt="EUPHORIA" width="140" style="vertical-align:middle;margin-left:24px">
  </div>
  <p>Hello <?= esc($registration['participant_name']) ?>,</p>
  <p>Your registration for <strong><?= esc($registration['event_name']) ?></strong> is confirmed.</p>
  <p>Registration ID: <strong><?= esc($registration['registration_id']) ?></strong><br>Venue: <?= esc($registration['venue'] ?: 'SAGE University Indore') ?></p>
  <p>Your digital pass is attached. Please keep its QR code ready at the entry gate.</p>
  <p><a href="<?= esc($passUrl) ?>" style="display:inline-block;background:#eab308;color:#111;padding:12px 18px;text-decoration:none;font-weight:bold">View secure digital pass</a></p>
  <p>SAGE University Indore</p>
</div>