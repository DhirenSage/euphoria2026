document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('form').forEach(function(form){ form.addEventListener('submit',function(){ var button=form.querySelector('button[type="submit"]'); if(button){button.disabled=true;button.dataset.originalText=button.textContent;button.textContent='Working…';}}); });
  var registrationCategory = document.getElementById('registration-category');
  var registrationEvent = document.getElementById('registration-event');
  var registrationData = document.getElementById('registration-events-data');
  if (registrationCategory && registrationEvent && registrationData) {
    var registrationEvents = JSON.parse(registrationData.textContent || '[]');
    var eventPanel = document.getElementById('registration-event-panel');
    var eventDetails = document.getElementById('registration-event-details');
    var teamPanel = document.getElementById('registration-team-panel');
    var teamName = document.getElementById('registration-team-name');
    var preselectedEvent = registrationEvent.dataset.selectedEvent || '';

    function money(amount) { return '₹' + Number(amount).toLocaleString('en-IN', { maximumFractionDigits: 0 }); }
    function clearEvent() {
      registrationEvent.innerHTML = '<option value="">Choose an event</option>';
      eventDetails.classList.remove('is-visible');
      teamPanel.classList.remove('is-visible');
      teamName.required = false;
      document.getElementById('registration-fee-value').textContent = '₹—';
      document.getElementById('registration-event-name').textContent = '—';
      document.getElementById('registration-event-fee').textContent = '₹—';
      document.getElementById('registration-event-type').textContent = '—';
    }
    function loadEvents(keepSelection) {
      clearEvent();
      var categoryId = registrationCategory.value;
      if (!categoryId) { eventPanel.classList.remove('is-visible'); return; }
      registrationEvents.filter(function(event){ return String(event.category_id) === categoryId; }).forEach(function(event){
        var option = document.createElement('option'); option.value = event.id; option.textContent = event.name + ' – ' + money(event.fee); registrationEvent.appendChild(option);
      });
      eventPanel.classList.add('is-visible');
      if (keepSelection && preselectedEvent && registrationEvent.querySelector('option[value="' + preselectedEvent + '"]')) { registrationEvent.value = preselectedEvent; registrationEvent.dispatchEvent(new Event('change')); }
    }
    registrationCategory.addEventListener('change', function(){ preselectedEvent = ''; loadEvents(false); });
    registrationEvent.addEventListener('change', function(){
      var selected = registrationEvents.find(function(event){ return String(event.id) === registrationEvent.value; });
      if (!selected) { eventDetails.classList.remove('is-visible'); teamPanel.classList.remove('is-visible'); teamName.required = false; document.getElementById('registration-fee-value').textContent = '₹—'; return; }
      var fee = money(selected.fee);
      document.getElementById('registration-fee-value').textContent = fee;
      document.getElementById('registration-event-name').textContent = selected.name;
      document.getElementById('registration-event-fee').textContent = fee;
      document.getElementById('registration-event-type').textContent = String(selected.registration_type).toUpperCase();
      eventDetails.classList.add('is-visible');
      var isTeam = selected.registration_type === 'team'; teamPanel.classList.toggle('is-visible', isTeam); teamName.required = isTeam;
      document.getElementById('registration-team-size').textContent = isTeam && selected.min_team_size ? 'TEAM SIZE / ' + selected.min_team_size + '–' + selected.max_team_size + ' MEMBERS' : '';
    });
    loadEvents(true);
  }
  var day = document.getElementById('scan-day');
  var eventSelect = document.getElementById('scan-event');
  if (eventSelect && day) {
    eventSelect.addEventListener('change', function () {
      Array.from(day.options).forEach(function (option) { option.hidden = option.value !== '' && option.dataset.event !== eventSelect.value; });
      day.value = '';
    });
  }
  var scanButton = document.getElementById('scan-submit');
  if (scanButton) {
    scanButton.addEventListener('click', async function () {
      var result = document.getElementById('scan-result');
      var token = document.getElementById('scan-token').value;
      var eventId = eventSelect.value;
      var dayId = day.value;
      var gateId = document.getElementById('scan-gate').value;
      if (!token || !eventId || !dayId) { result.className = 'scan-result result-denied'; result.innerHTML = '<span class="scan-icon">!</span><strong>Assignment required</strong><span>Select event, day and gate before scanning.</span>'; return; }
      scanButton.disabled = true; scanButton.textContent = 'Validating...';
      try {
        var csrf=document.querySelector('meta[name="csrf-token"]');
        var response = await fetch('/scanner/scan', { method:'POST', headers:{'Content-Type':'application/json','X-Requested-With':'XMLHttpRequest','X-CSRF-TOKEN':csrf?csrf.content:''}, body:JSON.stringify({token:token,event_id:eventId,day_id:dayId,gate_id:gateId}) });
        var data = await response.json();
        if(data.csrf&&csrf)csrf.content=data.csrf;
        result.className = 'scan-result ' + (data.ok ? 'result-allowed' : 'result-denied');
        result.innerHTML = '<span class="scan-icon">' + (data.ok ? '✓' : '!') + '</span><strong>' + (data.ok ? 'Entry allowed' : (data.status === 'duplicate' ? 'Already recorded' : 'Entry denied')) + '</strong><span>' + data.message + (data.registration ? ' · ' + data.registration.participant_name + ' · ' + data.registration.registration_id : '') + '</span>';
        document.getElementById('scan-token').value = '';
      } catch (error) { result.className = 'scan-result result-denied'; result.innerHTML = '<span class="scan-icon">!</span><strong>Scanner unavailable</strong><span>Check the connection and try again.</span>'; }
      scanButton.disabled = false; scanButton.innerHTML = 'Validate entry <span>↗</span>';
    });
  }
});