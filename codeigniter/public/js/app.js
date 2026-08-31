document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('form').forEach(function(form){ form.addEventListener('submit',function(){ var button=form.querySelector('button[type="submit"]'); if(button){button.disabled=true;button.dataset.originalText=button.textContent;button.textContent='Working…';}}); });
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