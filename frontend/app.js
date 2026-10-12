/* No framework or third-party assets: the screen should be the short part. */
'use strict';
const $ = id => document.getElementById(id);
const cacheKey = 'hfh-v1';
let state;
try { state = JSON.parse(localStorage.getItem(cacheKey) || '{}'); } catch { state = {}; }
let config = {}, recorder, stream, recordTimeout, phase = 'home';
function save() { localStorage.setItem(cacheKey, JSON.stringify(state)); }
function message(text = '') { $('status').textContent = text; }
function show(name) {
  phase = name;
  for (const id of ['home','offer','zen','reflection','result']) $(id).hidden = id !== name;
  document.body.classList.toggle('zen', name === 'zen');
  message();
  if (name === 'reflection') { $('note').value = state.note || ''; $('note').focus(); }
  if (name === 'zen') tick();
}
async function api(path, options = {}) {
  const headers = { ...(state.token ? {Authorization: `Bearer ${state.token}`} : {}), ...options.headers };
  if (options.body && !(options.body instanceof FormData)) headers['Content-Type'] = 'application/json';
  let response;
  try { response = await fetch(path, {...options, headers}); }
  catch { throw new Error('Connection unavailable. Your quest and field note remain in this browser. Reconnect and retry.'); }
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    const detail = typeof error.detail === 'string' ? error.detail : `Request failed (${response.status}). Check your input and retry.`;
    throw new Error(detail);
  }
  return response.status === 204 ? null : response.json();
}
async function busy(button, work) {
  const original = button.textContent;
  button.disabled = true; button.textContent = 'A moment…';
  try { await work(); } catch (error) { message(error.message); }
  finally { button.disabled = false; button.textContent = original; }
}
function offer(quest) {
  state.quest = quest; save();
  $('questTitle').textContent = quest.title; $('questTask').textContent = quest.task;
  $('questDuration').textContent = `${quest.minutes} minutes · ${quest.mobility === 'seated' ? 'seated observation' : 'your own pace'}`;
  show(quest.started_at ? 'zen' : 'offer');
}
function tick() {
  if (phase !== 'zen' || !state.quest?.started_at) return;
  const left = Math.max(0, Math.ceil(state.quest.started_at + state.quest.minutes * 60 - Date.now()/1000));
  $('timer').textContent = `${String(Math.floor(left/60)).padStart(2,'0')}:${String(left%60).padStart(2,'0')}`;
  // Never assume setInterval ran while the phone was locked: use the saved timestamp.
}
setInterval(tick, 1000);
document.addEventListener('visibilitychange', tick);
$('questForm').addEventListener('submit', event => {
  event.preventDefault();
  busy($('generate'), async () => {
    if (!state.token) { state.token = (await api('/api/session', {method:'POST'})).token; save(); }
    const quest = await api('/api/quests', {method:'POST', body:JSON.stringify({mood:$('mood').value, minutes:Number($('minutes').value), mobility:$('mobility').value})});
    state.note = ''; state.phase = 'offer'; offer(quest);
  });
});
$('accept').onclick = () => busy($('accept'), async () => {
  state.quest = await api(`/api/quests/${state.quest.id}/accept`, {method:'POST'});
  state.phase = 'zen'; save(); show('zen');
});
$('return').onclick = () => { state.phase = 'reflection'; save(); show('reflection'); };
$('note').oninput = () => { state.note = $('note').value; save(); };
function renderResult(receipt) {
  state.receipt = receipt; delete state.quest; delete state.note; state.phase = 'result'; save();
  show('result'); $('award').textContent = `+${receipt.xp_awarded} XP for being present.`;
  $('feedback').textContent = receipt.feedback; $('level').textContent = `Level ${receipt.level} · ${receipt.total_xp} XP`;
  $('progress').textContent = `Level ${receipt.level} · ${receipt.total_xp} XP`;
}
$('reflectionForm').addEventListener('submit', event => {
  event.preventDefault();
  busy($('submit'), async () => {
    state.note = $('note').value; save();
    const receipt = await api(`/api/quests/${state.quest.id}/reflection`, {method:'POST', body:JSON.stringify({reflection:state.note})});
    if (receipt.retry) { message(receipt.feedback + ' You can revise your note or end without XP.'); return; }
    renderResult(receipt);
  });
});
async function abandon(button) {
  await busy(button, async () => {
    await api(`/api/quests/${state.quest.id}`, {method:'DELETE'});
    delete state.quest; delete state.note; state.phase = 'home'; save(); show('home');
  });
}
$('discard').onclick = () => abandon($('discard'));
$('abandon').onclick = () => abandon($('abandon'));
$('done').onclick = () => { state.phase = 'home'; save(); show('home'); message('Your field note is complete. You can close this tab now.'); };
$('export').onclick = () => busy($('export'), async () => {
  const data = state.token ? await api('/api/me') : {xp:0, level:1, completed:[]};
  const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], {type:'application/json'}));
  const a = document.createElement('a'); a.href = url; a.download = 'happiness-field-notes.json'; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
});
$('erase').onclick = () => {
  if (!confirm('Delete your server profile, progress, session, and browser drafts? This cannot be undone.')) return;
  busy($('erase'), async () => {
    if (state.token) await api('/api/me', {method:'DELETE'});
    state = {}; localStorage.removeItem(cacheKey); $('progress').textContent = 'Level 1 · 0 XP'; show('home');
  });
};
function stopRecording() {
  clearTimeout(recordTimeout);
  if (recorder?.state === 'recording') recorder.stop();
  if (stream) stream.getTracks().forEach(track => track.stop());
  $('record').textContent = 'Record voice note';
}
$('record').onclick = async () => {
  if (recorder?.state === 'recording') { stopRecording(); return; }
  try {
    if (!navigator.mediaDevices || !window.MediaRecorder) throw new Error('Recording needs HTTPS (or localhost) and a supported browser. Use text instead.');
    stream = await navigator.mediaDevices.getUserMedia({audio:true});
    const chunks = []; recorder = new MediaRecorder(stream);
    recorder.ondataavailable = event => { if (event.data.size) chunks.push(event.data); };
    recorder.onstop = () => busy($('record'), async () => {
      const form = new FormData(); form.append('audio', new Blob(chunks, {type:recorder.mimeType}), 'note.audio');
      const transcript = await api('/api/transcribe', {method:'POST', body:form});
      state.note = [state.note || '', transcript.text].filter(Boolean).join(' ').slice(0,2000); save(); $('note').value = state.note;
      message('Transcript ready. Review it before completing your quest.');
    });
    recorder.start(); $('record').textContent = 'Stop recording'; recordTimeout = setTimeout(stopRecording, 60000);
  } catch (error) { stopRecording(); message(error.message); }
};
async function boot() {
  if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(() => {});
  // Restore usable offline state first, then reconcile with the authoritative server.
  if (state.quest) {
    offer(state.quest);
    if (state.phase === 'reflection') show('reflection');
  } else if (state.receipt && state.phase === 'result') renderResult(state.receipt);
  try {
    config = await api('/api/config');
    $('privacy').textContent = config.storage === 'sqlite' ? 'Local profile: Gemma and your progress run on this backend computer. Internet is not required after installation and model downloads.' : 'Hosted/Atlas profile: requests reach the app backend; MongoDB Atlas stores XP, levels, completed quests, and AI feedback. Raw reflections are not stored by default. Gemma runs wherever the backend operator configures it.';
    $('voiceTools').hidden = !config.voice;
    if (state.token) {
      const data = await api('/api/me');
      $('progress').textContent = `Level ${data.level} · ${data.xp} XP`;
      if (state.quest && data.completed.some(item => item.quest_id === state.quest.id)) {
        renderResult(data.completed.find(item => item.quest_id === state.quest.id));
      } else if (data.active) {
        if (state.quest && state.quest.id !== data.active.id) { delete state.note; state.phase = 'offer'; }
        const oldPhase = state.phase; offer(data.active);
        if (oldPhase === 'reflection' && data.active.started_at) show('reflection');
      } else if (state.quest) {
        delete state.quest; delete state.note; state.phase = 'home'; save(); show('home');
      }
    }
  } catch (error) { message(error.message); }
}
boot();
