<div style="font-family:sans-serif;color:#111;padding:32px">
  <div style="background:#111;padding:18px">
    <img src="https://customer-assets-gfyr7b9c.emergentagent.net/job_sage-mega-fest/artifacts/0yfnekpb_logotechweek.png" alt="SAGE University Indore" style="width:160px;height:auto;vertical-align:middle">
    <img src="https://customer-assets-gfyr7b9c.emergentagent.net/job_sage-mega-fest/artifacts/vevgaaxu_euphorialogo.png" alt="EUPHORIA" style="width:150px;height:auto;vertical-align:middle;margin-left:28px">
  </div>
  <hr><h2><?= esc($registration['event_name']) ?></h2>
  <p><strong>Pass holder:</strong> <?= esc($registration['participant_name']) ?></p>
  <p><strong>Registration:</strong> <?= esc($registration['registration_id']) ?></p>
  <p><strong>Venue:</strong> <?= esc($registration['venue'] ?? 'SAGE University Indore') ?></p>
  <img src="<?= esc($qr) ?>" width="220"><p>Keep this QR ready at the entry gate.</p>
</div>