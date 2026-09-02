document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('form').forEach(function(form){ form.addEventListener('submit',function(){ var button=form.querySelector('button[type="submit"]'); if(button){button.disabled=true;button.dataset.originalText=button.textContent;button.textContent='Working…';}}); });
  var registrationCategory = document.getElementById('registration-category');
  var registrationEvent = document.getElementById('registration-event');
  var registrationData = document.getElementById('registration-events-data');
  if (registrationCategory && registrationEvent && registrationData) {
    var registrationEvents = JSON.parse(registrationData.textContent || '[]');
    var eventPanel = document.getElementById('registration-event-panel');
    var eventDetails = document.getElementById('registration-event-details');
    var fieldsData = document.getElementById('registration-fields-data');
    var fieldsPanel = document.getElementById('registration-custom-fields');
    var fieldsByEvent = fieldsData ? JSON.parse(fieldsData.textContent || '{}') : {};
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
      if (fieldsPanel) fieldsPanel.innerHTML = '';
    }
    function renderCustomFields(eventId) {
      if (!fieldsPanel) return;
      fieldsPanel.innerHTML = '';
      var fields = fieldsByEvent[String(eventId)] || [];
      if (!fields.length) return;
      var heading = document.createElement('div'); heading.className = 'registration-section-heading'; heading.innerHTML = '<span class="eyebrow">EVENT QUESTIONS</span><h3>Complete the event-specific details</h3>'; fieldsPanel.appendChild(heading);
      var grid = document.createElement('div'); grid.className = 'form-grid';
      fields.forEach(function(field){
        var label=document.createElement('label'); label.textContent=field.label+(Number(field.is_required)?' *':'');
        var control;
        var options=[]; try{ options=field.options_json?JSON.parse(field.options_json):[]; }catch(error){ options=[]; }
        if(field.field_type==='textarea'){control=document.createElement('textarea');}
        else if(['select','radio'].includes(field.field_type)){control=document.createElement('select');var blank=document.createElement('option');blank.value='';blank.textContent='Select an option';control.appendChild(blank);options.forEach(function(value){var option=document.createElement('option');option.value=value;option.textContent=value;control.appendChild(option);});}
        else{control=document.createElement('input');control.type=field.field_type==='phone'?'tel':field.field_type;}
        control.name=field.field_name;control.required=Boolean(Number(field.is_required));control.dataset.testid='registration-field-'+field.field_name;label.appendChild(control);grid.appendChild(label);
      }); fieldsPanel.appendChild(grid);
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
      renderCustomFields(selected.id);
      var isTeam = selected.registration_type === 'team'; teamPanel.classList.toggle('is-visible', isTeam); teamName.required = isTeam;
      document.getElementById('registration-team-size').textContent = isTeam && selected.min_team_size ? 'TEAM SIZE / ' + selected.min_team_size + '–' + selected.max_team_size + ' MEMBERS' : '';
    });
    loadEvents(true);
  }
  document.querySelectorAll('[data-confirm]').forEach(function(element){ element.addEventListener('click',function(event){ if(!window.confirm(element.dataset.confirm||'Continue?'))event.preventDefault(); }); });
  document.querySelectorAll('.print-pass-trigger').forEach(function(button){button.addEventListener('click',function(){window.print();});});
  function addRepeaterRow(containerId, html){var container=document.getElementById(containerId);if(!container)return;var wrapper=document.createElement('div');wrapper.innerHTML=html;var row=wrapper.firstElementChild;container.appendChild(row);}
  var addDay=document.getElementById('add-event-day');if(addDay)addDay.addEventListener('click',function(){var index=document.querySelectorAll('#event-days-list .repeater-row').length+1;addRepeaterRow('event-days-list','<div class="repeater-row"><label>Label<input name="day_label[]" value="Day '+index+'"></label><label>Date<input type="date" name="day_date[]"></label><button type="button" class="table-action danger-action remove-row">Remove</button></div>');});
  var addField=document.getElementById('add-registration-field');if(addField)addField.addEventListener('click',function(){var index=document.querySelectorAll('#registration-fields-list .field-builder-row').length;addRepeaterRow('registration-fields-list','<div class="field-builder-row"><label>Label<input name="field_label[]"></label><label>Field name<input name="field_name[]"></label><label>Type<select name="field_type[]"><option value="text">Text</option><option value="number">Number</option><option value="email">Email</option><option value="phone">Phone</option><option value="date">Date</option><option value="select">Select</option><option value="radio">Radio</option><option value="checkbox">Checkbox</option><option value="textarea">Textarea</option><option value="file">File</option></select></label><label>Options<input name="field_options[]"></label><label class="checkbox-label"><input type="checkbox" name="field_required[]" value="'+index+'"> Required</label><button type="button" class="table-action danger-action remove-row">Remove</button></div>');});
  document.addEventListener('click',function(event){var button=event.target.closest('.remove-row');if(button)button.closest('.repeater-row,.field-builder-row').remove();});
  var day = document.getElementById('scan-day');
  var eventSelect = document.getElementById('scan-event');
  if (eventSelect && day) {
    eventSelect.addEventListener('change', function () {
      Array.from(day.options).forEach(function (option) { option.hidden = option.value !== '' && option.dataset.event !== eventSelect.value; });
      day.value = '';
    });
  }
  var assignmentEvent=document.getElementById('assignment-event');var assignmentDay=document.getElementById('assignment-day');if(assignmentEvent&&assignmentDay){assignmentEvent.addEventListener('change',function(){Array.from(assignmentDay.options).forEach(function(option){option.hidden=option.value!==''&&option.dataset.event!==assignmentEvent.value;});assignmentDay.value='';});}
  var scanButton = document.getElementById('scan-submit');
  function escapeHtml(value){var div=document.createElement('div');div.textContent=String(value==null?'':value);return div.innerHTML;}
  if (scanButton) {
    scanButton.addEventListener('click', async function () {
      var result = document.getElementById('scan-result');
      var token = document.getElementById('scan-token').value;
      var eventId = eventSelect.value;
      var dayId = day.value;
      var gateId = document.getElementById('scan-gate').value;
      if (!token || !eventId || !dayId || !gateId) { result.className = 'scan-result result-denied'; result.innerHTML = '<span class="scan-icon">!</span><strong>Assignment required</strong><span>Select event, day and gate before scanning.</span>'; return; }
      scanButton.disabled = true; scanButton.textContent = 'Validating...';
      try {
        var csrf=document.querySelector('meta[name="csrf-token"]');
        var response = await fetch('/scanner/scan', { method:'POST', headers:{'Content-Type':'application/json','X-Requested-With':'XMLHttpRequest','X-CSRF-TOKEN':csrf?csrf.content:''}, body:JSON.stringify({token:token,event_id:eventId,day_id:dayId,gate_id:gateId}) });
        var data = await response.json();
        if(data.csrf&&csrf)csrf.content=data.csrf;
        result.className = 'scan-result ' + (data.ok ? 'result-allowed' : 'result-denied');
        var detail=data.registration?'<div class="scan-registration"><b>'+escapeHtml(data.registration.participant_name)+'</b><span>'+escapeHtml(data.registration.registration_id)+'</span><span>'+escapeHtml(data.registration.event_name)+' · PAYMENT '+escapeHtml(String(data.registration.payment_status).toUpperCase())+' · PASS '+escapeHtml(String(data.registration.qr_status).toUpperCase())+'</span></div>':'';
        var firstEntry=data.status==='duplicate'&&data.entry&&data.entry.entry_time?'<span>First entry: '+escapeHtml(data.entry.entry_time)+'</span>':'';
        result.innerHTML = '<span class="scan-icon">' + (data.ok ? '✓' : '!') + '</span><strong>' + (data.ok ? 'Entry allowed' : (data.status === 'duplicate' ? 'Entry already recorded' : 'Entry denied')) + '</strong><span>' + escapeHtml(data.message) + '</span>'+detail+firstEntry;
        if(data.ok&&navigator.vibrate)navigator.vibrate(120);
        document.getElementById('scan-token').value = '';
      } catch (error) { result.className = 'scan-result result-denied'; result.innerHTML = '<span class="scan-icon">!</span><strong>Scanner unavailable</strong><span>Check the connection and try again.</span>'; }
      scanButton.disabled = false; scanButton.innerHTML = 'Validate entry <span>↗</span>';
    });
  }
  var cameraButton=document.getElementById('camera-start');
  if(cameraButton){cameraButton.addEventListener('click',async function(){var status=document.getElementById('camera-status');var video=document.getElementById('scanner-video');if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){status.textContent='Camera access is unavailable. Use the secure token fallback.';return;}try{var stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:'environment'},audio:false});video.srcObject=stream;await video.play();status.textContent=('BarcodeDetector' in window)?'Camera ready. Point it at the QR code.':'Camera ready, but this browser cannot decode QR codes. Use the secure token fallback.';cameraButton.textContent='Camera active';cameraButton.disabled=true;if('BarcodeDetector' in window){var detector=new BarcodeDetector({formats:['qr_code']});var timer=setInterval(async function(){if(!video.srcObject){clearInterval(timer);return;}try{var codes=await detector.detect(video);if(codes.length){document.getElementById('scan-token').value=codes[0].rawValue;scanButton.click();stream.getTracks().forEach(function(track){track.stop();});video.srcObject=null;cameraButton.disabled=false;cameraButton.textContent='Open camera';status.textContent='QR captured. Camera stopped.';clearInterval(timer);}}catch(error){}},450);}}catch(error){status.textContent='Camera permission was denied. Use the secure token fallback.';}});}
});