<?php
$catalogueEventIds = array_map('intval', array_column($events, 'id'));
$routeEventId = $event && in_array((int)$event['id'], $catalogueEventIds, true) ? (int)$event['id'] : null;
$preselectedEventId = (int)(old('event_id') ?: ($routeEventId ?? 0));
$preselectedCategoryId = (int)(old('category_id') ?: ($routeEventId ? $event['category_id'] : 0));
$selectedEvent = null;
foreach ($events as $candidate) if ((int)$candidate['id'] === $preselectedEventId) $selectedEvent = $candidate;
$fieldsByEvent = [];
foreach ($customFields as $field) $fieldsByEvent[(int)$field['event_id']][] = $field;
?>
<main class="page-shell registration-page">
  <section class="registration-compact-hero" data-testid="registration-page-header">
    <div>
      <?= view('partials/official_logos', ['variant'=>'registration']) ?>
      <span class="eyebrow accent">EUPHORIA 2K26 / REGISTRATION</span>
      <h1>Register for<br><em>your event.</em></h1>
    </div>
    <div class="registration-hero-copy">
      <span class="registration-step-pill">01 · Details</span>
      <span class="registration-step-pill">02 · Event</span>
      <span class="registration-step-pill">03 · Payment</span>
      <p data-testid="registration-selected-summary"><?= $selectedEvent ? esc($selectedEvent['name']) : 'Choose from 32 cultural, literary, science and sports events.' ?></p>
    </div>
  </section>

  <form method="post" enctype="multipart/form-data" action="<?= base_url('registration') ?>" class="registration-form registration-form-layout" data-testid="registration-form">
    <input type="hidden" name="<?= csrf_token() ?>" value="<?= csrf_hash() ?>">

    <div class="registration-form-card">
      <div class="registration-card-heading">
        <span class="eyebrow">PARTICIPANT INFORMATION</span>
        <h2>Tell us about yourself</h2>
        <p>Fields marked with an asterisk are required.</p>
      </div>

      <div class="form-section registration-details-section">
        <span class="form-section-number">01</span>
        <div class="form-grid">
          <label>Your name <b>*</b>
            <input name="name" value="<?= esc(old('name')) ?>" placeholder="Your full name" required data-testid="registration-name-input">
          </label>
          <label>Father's name <span class="label-muted">Optional</span>
            <input name="fathername" value="<?= esc(old('fathername')) ?>" placeholder="Father's name" data-testid="registration-father-name-input">
          </label>
          <label>Email address <b>*</b>
            <input type="email" name="mail" value="<?= esc(old('mail')) ?>" placeholder="name@example.com" required data-testid="registration-email-input">
          </label>
          <label>Mobile number <b>*</b>
            <input type="tel" name="mobile_no" value="<?= esc(old('mobile_no')) ?>" placeholder="10-digit mobile number" pattern="[6-9][0-9]{9}" required data-testid="registration-mobile-input">
          </label>
          <label>Your age <span class="label-muted">Optional</span>
            <input type="number" name="age" value="<?= esc(old('age')) ?>" min="10" max="100" placeholder="Age" data-testid="registration-age-input">
          </label>
          <label>School / college name <b>*</b>
            <input name="school_clg_name" value="<?= esc(old('school_clg_name')) ?>" placeholder="Institution name" required data-testid="registration-college-input">
          </label>
          <label>City <span class="label-muted">Optional</span>
            <input name="city" value="<?= esc(old('city')) ?>" placeholder="Your city" data-testid="registration-city-input">
          </label>
          <label>Participant type <b>*</b>
            <select name="participant_affiliation" required data-testid="registration-affiliation-select">
              <option value="">Select affiliation</option>
              <option value="sageian" <?= old('participant_affiliation') === 'sageian' ? 'selected' : '' ?>>SAGEian</option>
              <option value="non_sageian" <?= old('participant_affiliation') === 'non_sageian' ? 'selected' : '' ?>>Non-SAGEian</option>
            </select>
          </label>
        </div>
      </div>

      <div class="form-section registration-choice-section">
        <span class="form-section-number">02</span>
        <div class="registration-section-heading">
          <span class="eyebrow">EVENT SELECTION</span>
          <h3>Choose where you want to compete</h3>
        </div>
        <div class="form-grid registration-event-grid">
          <label>Event category <b>*</b>
            <select id="registration-category" name="category_id" required data-testid="registration-category-select">
              <option value="">Select Event Category</option>
              <?php foreach ($categories as $category): ?>
                <option value="<?= esc($category['id']) ?>" <?= (int)$category['id'] === $preselectedCategoryId ? 'selected' : '' ?>><?= esc($category['name']) ?></option>
              <?php endforeach ?>
            </select>
          </label>
          <div id="registration-event-panel" class="registration-event-panel <?= $preselectedCategoryId ? 'is-visible' : '' ?>">
            <label>Event <b>*</b>
              <select id="registration-event" name="event_id" required data-selected-event="<?= esc($preselectedEventId) ?>" data-testid="registration-event-select">
                <option value="">Choose an event</option>
              </select>
            </label>
          </div>
        </div>

        <div id="registration-event-details" class="event-selection-summary <?= $selectedEvent ? 'is-visible' : '' ?>" data-testid="registration-event-details">
          <div><span class="eyebrow">SELECTED EVENT</span><strong id="registration-event-name"><?= esc($selectedEvent['name'] ?? '—') ?></strong></div>
          <div><span class="eyebrow">FEE</span><strong id="registration-event-fee"><?= $selectedEvent ? esc(money($selectedEvent['fee'])) : '₹—' ?></strong></div>
          <div><span class="eyebrow">ENTRY</span><strong id="registration-event-type"><?= $selectedEvent ? esc(strtoupper($selectedEvent['registration_type'])) : '—' ?></strong></div>
        </div>

        <div id="registration-team-panel" class="registration-team-panel <?= ($selectedEvent['registration_type'] ?? '') === 'team' ? 'is-visible' : '' ?>">
          <div class="registration-section-heading">
            <span class="eyebrow">TEAM DETAILS</span>
            <h3>Register your team captain now</h3>
          </div>
          <div class="form-grid">
            <label>Team name <b>*</b>
              <input id="registration-team-name" name="team_name" value="<?= esc(old('team_name')) ?>" placeholder="Your team name" data-testid="registration-team-input">
            </label>
            <label>Team member names <span class="label-muted">One per line</span>
              <textarea name="team_member_names" placeholder="One member per line" data-testid="registration-team-members-input"><?= esc(old('team_member_names')) ?></textarea>
            </label>
          </div>
          <p id="registration-team-size" class="team-size-note mono"></p>
        </div>
        <div id="registration-custom-fields" class="registration-custom-fields" data-testid="registration-custom-fields"></div>
      </div>
    </div>

    <aside class="registration-sticky-summary" data-testid="registration-fee-display">
      <div class="registration-summary-top">
        <span class="eyebrow">REGISTRATION SUMMARY</span>
        <span class="registration-live-dot">LIVE</span>
      </div>
      <div class="registration-summary-price">
        <span>Entry fee</span>
        <strong id="registration-fee-value"><?= $selectedEvent ? esc(money($selectedEvent['fee'])) : '₹—' ?></strong>
        <small>Final amount is verified from the event database.</small>
      </div>
      <div class="registration-summary-points">
        <span><b>✓</b> Secure server-side pricing</span>
        <span><b>✓</b> Unique registration ID</span>
        <span><b>✓</b> QR pass after confirmation</span>
      </div>
      <label class="checkbox-label registration-consent"><input type="checkbox" name="terms" value="1" required data-testid="registration-terms-checkbox"> <span>I agree to the event rules, privacy policy and refund terms.</span></label>
      <button class="button button-yellow full-width" type="submit" data-testid="registration-submit-button">Continue to payment <span>↗</span></button>
      <p class="registration-support mono">NEED HELP? CONTACT THE EUPHORIA DESK</p>
    </aside>
  </form>
</main>
<script id="registration-events-data" type="application/json"><?= json_encode($events, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT) ?></script>
<script id="registration-fields-data" type="application/json"><?= json_encode($fieldsByEvent, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT) ?></script>