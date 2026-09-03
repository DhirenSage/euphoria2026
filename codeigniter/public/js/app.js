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
  function escapeHtml(value){var div=document.createElement('div');div.textContent=String(value==null?'':value);return div.innerHTML;}
  var scannerForm=document.querySelector('[data-scanner-form]');
  if(scannerForm){
    var scanButton=scannerForm.querySelector('[data-testid="scanner-submit"]');var tokenInput=scannerForm.querySelector('[name="token"]');var result=document.querySelector('[data-scanner-result]');var cameraMessage=scannerForm.querySelector('[data-camera-message]');var cameraButton=scannerForm.querySelector('[data-camera-start]');var imageInput=scannerForm.querySelector('[data-image-input]');var sound=true;var stream=null;var cameraTrack=null;var detector=('BarcodeDetector' in window)?new BarcodeDetector({formats:['qr_code']}):null;
    function tone(ok){if(!sound)return;try{var audio=new AudioContext();var oscillator=audio.createOscillator();var gain=audio.createGain();oscillator.frequency.value=ok?880:220;gain.gain.value=.08;oscillator.connect(gain);gain.connect(audio.destination);oscillator.start();oscillator.stop(audio.currentTime+(ok?.16:.3));}catch(error){}}
    function stopCamera(){if(stream)stream.getTracks().forEach(function(track){track.stop();});stream=null;cameraTrack=null;cameraButton.disabled=false;cameraButton.textContent='Open camera & scan';}
    async function verify(token){if(!token.trim())return;scanButton.disabled=true;scanButton.textContent='Verifying…';
      try {
        var csrf=document.querySelector('meta[name="csrf-token"]');
        var response = await fetch(scannerForm.dataset.scanUrl, { method:'POST', headers:{'Content-Type':'application/json','X-Requested-With':'XMLHttpRequest','X-CSRF-TOKEN':csrf?csrf.content:''}, body:JSON.stringify({token:token}) });
        var data = await response.json();
        if(data.csrf&&csrf)csrf.content=data.csrf;
        result.className = 'scanner-result ' + (data.ok ? 'result-allowed' : (data.status==='duplicate'?'result-duplicate':'result-denied'));
        var detail=data.registration?'<dl class="scan-registration"><div><dt>Participant</dt><dd>'+escapeHtml(data.registration.participant_name)+'</dd></div><div><dt>Registration</dt><dd>'+escapeHtml(data.registration.registration_id)+'</dd></div><div><dt>Event</dt><dd>'+escapeHtml(data.registration.event_name)+'</dd></div><div><dt>Event day</dt><dd>'+escapeHtml(data.registration.event_day_label||'—')+' · '+escapeHtml(data.registration.event_day_date||'—')+'</dd></div><div><dt>Institute</dt><dd>'+escapeHtml(data.registration.college)+'</dd></div><div><dt>Mobile</dt><dd>'+escapeHtml(data.registration.mobile)+'</dd></div><div><dt>Email</dt><dd>'+escapeHtml(data.registration.email)+'</dd></div><div><dt>Payment / pass</dt><dd>'+escapeHtml(String(data.registration.payment_status).toUpperCase())+' / '+escapeHtml(String(data.registration.qr_status).toUpperCase())+'</dd></div></dl>':'';
        var firstEntry=data.status==='duplicate'&&data.entry&&data.entry.entry_time?'<span>First entry: '+escapeHtml(data.entry.entry_time)+'</span>':'';
        result.innerHTML = '<span class="scanner-result-icon">' + (data.ok ? '✓' : '!') + '</span><strong>' + (data.ok ? 'ENTRY ALLOWED' : (data.status === 'duplicate' ? 'ENTRY ALREADY RECORDED' : 'ENTRY DENIED')) + '</strong><p>' + escapeHtml(data.message) + '</p>'+detail+firstEntry;tone(data.ok);if(navigator.vibrate)navigator.vibrate(data.ok?[100]:[180,80,180]);tokenInput.value='';
      }catch(error){result.className='scanner-result result-denied';result.innerHTML='<span class="scanner-result-icon">!</span><strong>SCANNER UNAVAILABLE</strong><p>Check the connection and try again.</p>';}scanButton.disabled=false;scanButton.textContent="Verify and record today's entry ↗";
    }
    scannerForm.addEventListener('submit',function(event){event.preventDefault();verify(tokenInput.value);});
    cameraButton.addEventListener('click',async function(){if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia||!detector){cameraMessage.textContent='This browser cannot decode camera QR. Use image upload or the secure token.';return;}try{stopCamera();stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:'environment'},audio:false});cameraTrack=stream.getVideoTracks()[0];var video=document.createElement('video');video.playsInline=true;video.muted=true;video.srcObject=stream;document.getElementById('qr-reader').replaceChildren(video);await video.play();cameraButton.disabled=true;cameraButton.textContent='Camera live';cameraMessage.textContent='Hold any EUPHORIA QR inside the frame.';var timer=setInterval(async function(){if(!stream){clearInterval(timer);return;}try{var codes=await detector.detect(video);if(codes.length){tokenInput.value=codes[0].rawValue;stopCamera();cameraMessage.textContent="QR captured. Verifying today's entry…";clearInterval(timer);verify(tokenInput.value);}}catch(error){}},400);}catch(error){cameraMessage.textContent='Camera permission failed. Upload the QR image or paste the secure token.';stopCamera();}});
    imageInput.addEventListener('change',async function(){var file=imageInput.files&&imageInput.files[0];if(!file||!detector){cameraMessage.textContent='Image decoding is not available in this browser. Paste the secure token.';return;}try{var bitmap=await createImageBitmap(file);var codes=await detector.detect(bitmap);if(!codes.length)throw new Error('No QR');tokenInput.value=codes[0].rawValue;cameraMessage.textContent="QR image decoded. Verifying today's entry…";verify(tokenInput.value);}catch(error){cameraMessage.textContent='No readable QR was found in that image.';}});
    var soundToggle=document.querySelector('[data-sound-toggle]');if(soundToggle)soundToggle.addEventListener('click',function(){sound=!sound;soundToggle.textContent='Sound '+(sound?'on':'off');});
    var fullscreenToggle=document.querySelector('[data-fullscreen-toggle]');if(fullscreenToggle)fullscreenToggle.addEventListener('click',async function(){if(!document.fullscreenElement)await document.documentElement.requestFullscreen();else await document.exitFullscreen();});
    var torchToggle=document.querySelector('[data-torch-toggle]');if(torchToggle)torchToggle.addEventListener('click',async function(){if(!cameraTrack){cameraMessage.textContent='Open the camera before using the torch.';return;}var caps=cameraTrack.getCapabilities?cameraTrack.getCapabilities():{};if(!caps.torch){cameraMessage.textContent='This camera does not expose torch control.';return;}var enabled=torchToggle.dataset.on!=='true';await cameraTrack.applyConstraints({advanced:[{torch:enabled}]});torchToggle.dataset.on=String(enabled);torchToggle.textContent='Torch '+(enabled?'on':'off');});
  }
  var mediaModal=document.querySelector('[data-media-modal]');
  if(mediaModal){var player=mediaModal.querySelector('[data-media-player]');document.querySelectorAll('[data-media-open]').forEach(function(button){button.addEventListener('click',function(){try{var item=JSON.parse(button.dataset.media);var content='';if(item.media_type==='video'&&item.video_provider==='direct')content='<video controls autoplay src="'+escapeHtml(item.embed_url||item.source_url)+'"></video>';else if(item.media_type==='video'&&item.embed_url)content='<iframe src="'+escapeHtml(item.embed_url)+'?autoplay=1" title="'+escapeHtml(item.title)+'" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>';else content='<img src="'+escapeHtml(item.public_url||item.source_url)+'" alt="'+escapeHtml(item.caption||item.title)+'">';player.innerHTML=content;mediaModal.querySelector('[data-media-title]').textContent=item.title;mediaModal.querySelector('[data-media-caption]').textContent=item.caption||'';mediaModal.querySelector('[data-media-section]').textContent=item.section+(item.event_name?' · '+item.event_name:'');mediaModal.showModal();}catch(error){}});});mediaModal.querySelector('[data-media-close]').addEventListener('click',function(){mediaModal.close();player.innerHTML='';});mediaModal.addEventListener('click',function(event){if(event.target===mediaModal){mediaModal.close();player.innerHTML='';}});}
  document.querySelectorAll('[data-media-filter]').forEach(function(button){button.addEventListener('click',function(){document.querySelectorAll('[data-media-filter]').forEach(function(item){item.classList.remove('active');});button.classList.add('active');var filter=button.dataset.mediaFilter;document.querySelectorAll('[data-media-type]').forEach(function(item){item.hidden=filter!=='all'&&item.dataset.mediaType!==filter;});});});
});