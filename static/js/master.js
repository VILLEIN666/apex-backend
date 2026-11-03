// APEX SOVEREIGN V7 — Master Control (Full)
const API_BASE = window.location.origin;
const MASTER_EMAIL = "mrvillein66@gmail.com";
const MASTER_PASS = "Villein66";
let TOKEN = "", DEVICES = [], WS = null;
const $ = id => document.getElementById(id);

const icons = {
  lock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>',
  ring: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>',
  loc: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>',
  view: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>',
  log: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>',
  wipe: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>',
  battery: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;display:inline"><rect x="1" y="6" width="18" height="12" rx="2" ry="2"></rect><line x1="23" y1="13" x2="23" y2="11"></line></svg>',
  storage: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;display:inline"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>',
  screen: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;display:inline"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>',
  pin: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;display:inline"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>'
};

async function autoLogin() {
  try {
    const res = await fetch(`${API_BASE}/api/auth/login`, { method: "POST", body: new URLSearchParams({ username: MASTER_EMAIL, password: MASTER_PASS }) });
    if (res.ok) { TOKEN = (await res.json()).access_token; startDashboard(); return; }
    const reg = await fetch(`${API_BASE}/api/auth/register`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email: MASTER_EMAIL, name: "Villein", password: MASTER_PASS, consent_accepted: true }) });
    if (reg.ok) { TOKEN = (await reg.json()).access_token; startDashboard(); return; }
    toast("Auth failed", "error");
  } catch (e) { toast("Connection error: " + e.message, "error"); }
}

function startDashboard() { loadDevices(); connectWS(); }

async function api(path, opts = {}) {
  opts.headers = { ...(opts.headers || {}), "Authorization": "Bearer " + TOKEN };
  const res = await fetch(API_BASE + path, opts);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function showTab(name) {
  document.querySelectorAll(".nav-tab").forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
  const idx = name === "devices" ? 1 : name === "add" ? 2 : 3;
  document.querySelector(`.nav-tab:nth-child(${idx})`).classList.add("active");
  $(`tab-${name}`).classList.add("active");
  if (name === "audit") updateAuditDeviceList();
}

async function loadDevices() {
  try {
    DEVICES = await api("/api/devices");
    renderDevices();
    updateAuditDeviceList();
    $("deviceCount").textContent = `${DEVICES.filter(d => d.is_paired).length} Devices`;
  } catch (e) { $("devicesGrid").innerHTML = `<div class="empty" style="color:#ef4444">Load failed: ${e.message}</div>`; }
}

function refreshDevices() { toast("Refreshing...", "success"); loadDevices(); }

function renderDevices() {
  const grid = $("devicesGrid");
  const paired = DEVICES.filter(d => d.is_paired);
  if (paired.length === 0) {
    grid.innerHTML = `<div class="empty" style="grid-column:1/-1;text-align:center;padding:80px 20px;color:#64748b">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width:80px;height:80px;opacity:0.3;margin:auto;display:block;margin-bottom:20px">
        <rect x="4" y="2" width="16" height="20" rx="2"/><line x1="12" y1="18" x2="12" y2="18"/>
      </svg>
      <p style="font-size:18px;font-weight:600;margin-bottom:8px">No Devices Connected</p>
      <p style="font-size:13px">Go to "Add Device" tab to pair a child device</p>
    </div>`;
    return;
  }
  grid.innerHTML = paired.map(d => renderDeviceCard(d)).join("");
}

function renderDeviceCard(d) {
  const batteryColor = d.battery_level < 20 ? "#ef4444" : d.battery_level < 50 ? "#f59e0b" : "#10b981";
  const storagePct = d.storage_total_mb ? Math.min(100, (d.storage_free_mb / d.storage_total_mb) * 100) : 0;
  const screenPct = d.daily_limit_minutes ? Math.min(100, (d.screen_time_minutes / d.daily_limit_minutes) * 100) : 0;
  return `
  <div class="device-card ${d.is_online ? 'online' : 'offline'}">
    <div class="device-header">
      <div><div class="device-name"><span class="status-dot ${d.is_online ? 'online' : 'offline'}"></span>${escape(d.child_name || "Unknown")}</div>
        <div class="device-model">${escape(d.device_model || "Android")}</div></div>
      <div style="font-size:11px;color:#64748b;text-align:right">${d.is_online ? '<span style="color:#10b981">● ONLINE</span>' : '<span style="color:#ef4444">● OFFLINE</span>'}</div>
    </div>
    <div class="device-stats">
      <div class="stat"><div class="stat-label">${icons.battery} BATTERY</div><div class="stat-value">${d.battery_level || 0}%</div><div class="progress-bar"><div class="progress-fill" style="width:${d.battery_level || 0}%;background:${batteryColor}"></div></div></div>
      <div class="stat"><div class="stat-label">${icons.storage} STORAGE</div><div class="stat-value">${d.storage_free_mb || 0} MB</div><div class="progress-bar"><div class="progress-fill" style="width:${storagePct}%;background:#3b82f6"></div></div></div>
      <div class="stat"><div class="stat-label">${icons.screen} SCREEN</div><div class="stat-value">${d.screen_time_minutes || 0} min</div><div class="progress-bar"><div class="progress-fill" style="width:${screenPct}%;background:#8b5cf6"></div></div></div>
      <div class="stat"><div class="stat-label">${icons.pin} LOCATION</div><div class="stat-value" style="font-size:12px">${d.last_lat ? d.last_lat.toFixed(3) + ', ' + d.last_lon.toFixed(3) : "—"}</div></div>
    </div>
    <div class="device-actions">
      <button onclick="event.stopPropagation(); sendCommand(${d.id},'LOCK')">${icons.lock}<span>Lock</span></button>
      <button onclick="event.stopPropagation(); sendCommand(${d.id},'RING')">${icons.ring}<span>Ring</span></button>
      <button onclick="event.stopPropagation(); sendCommand(${d.id},'LOCATE')">${icons.loc}<span>Locate</span></button>
      <button class="stream" onclick="event.stopPropagation(); openScreenStream(${d.id})">${icons.view}<span>View</span></button>
      <button onclick="event.stopPropagation(); openAuditFor(${d.id})">${icons.log}<span>Log</span></button>
      <button class="danger" onclick="event.stopPropagation(); sendCommand(${d.id},'WIPE')">${icons.wipe}<span>Wipe</span></button>
    </div>
  </div>`;
}

function escape(s) { return String(s || "").replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }

async function sendCommand(id, cmd) {
  const labels = { LOCK: "Lock this device?", RING: "Ring this device?", LOCATE: "Locate this device?", WIPE: "⚠️ WIPE ALL DATA? Cannot undo!" };
  if (!confirm(labels[cmd] || `Send ${cmd}?`)) return;
  try { await api(`/api/commands/${id}/${cmd}`, { method: "POST" }); toast(`✅ ${cmd} sent`, "success"); }
  catch (e) { toast("❌ " + e.message, "error"); }
}

async function createPairing() {
  const name = $("newChildName").value.trim() || "New Child";
  $("qrContainer").innerHTML = '<p style="color:#94a3b8;text-align:center">Generating QR...</p>';
  try {
    const data = await api(`/api/devices/create-pairing?child_name=${encodeURIComponent(name)}`, { method: "POST" });
    $("qrContainer").innerHTML = `<img src="${data.qr_url}" alt="QR" style="max-width:250px;background:#fff;padding:16px;border-radius:16px;margin-top:20px">
      <div class="enroll-url">${data.enroll_url}</div>
      <p style="color:#94a3b8;font-size:12px;margin-top:12px">📱 Scan with child's phone</p>
      <a href="${data.enroll_url}" target="_blank" class="btn btn-primary" style="margin-top:16px;display:inline-flex">Open Enroll Page</a>`;
    $("newChildName").value = ""; loadDevices();
  } catch (e) { $("qrContainer").innerHTML = `<p style="color:#ef4444">${e.message}</p>`; }
}

function openScreenStream(id) {
  const d = DEVICES.find(x => x.id === id);
  if (!d) return;
  $("modalTitle").textContent = `📺 ${d.child_name} — Live Screen`;
  $("modalBody").innerHTML = `<p style="color:#94a3b8;font-size:13px;margin-bottom:16px">Child must press "Start Screen Streaming" first.</p>
    <div class="screen-view" id="screenView">
      <img id="screenImg" src="/api/devices/${id}/frame?t=${Date.now()}"
           onerror="document.getElementById('screenView').innerHTML='<div style=padding:60px;text-align:center;color:#64748b>No frame yet<br><span style=font-size:12px>Waiting for child...</span></div>'"
           onload="this.style.display='block'" style="display:none;width:100%">
    </div>
    <button class="btn btn-primary" onclick="refreshScreenFrame(${id})" style="margin-top:16px;width:100%">🔄 Refresh Frame</button>`;
  $("deviceModal").classList.add("active");
  if (window._screenTimer) clearInterval(window._screenTimer);
  window._screenTimer = setInterval(() => refreshScreenFrame(id), 3000);
}

function refreshScreenFrame(id) {
  const img = $("screenImg");
  if (img) { img.src = `/api/devices/${id}/frame?t=${Date.now()}`; img.style.display = "block"; }
}

function closeModal() { $("deviceModal").classList.remove("active"); if (window._screenTimer) clearInterval(window._screenTimer); }

function updateAuditDeviceList() {
  const sel = $("auditDevice"); if (!sel) return;
  const cur = sel.value;
  sel.innerHTML = '<option value="">Select a device...</option>' + DEVICES.filter(d => d.is_paired).map(d => `<option value="${d.device_uid}">${escape(d.child_name)}</option>`).join("");
  if (cur) sel.value = cur;
}

function openAuditFor(id) {
  const d = DEVICES.find(x => x.id === id); if (!d) return;
  showTab("audit");
  setTimeout(() => { $("auditDevice").value = d.device_uid; loadAudit(); }, 100);
}

async function loadAudit() {
  const uid = $("auditDevice").value;
  if (!uid) { toast("Select a device first", "error"); return; }
  $("auditLog").innerHTML = '<p style="color:#94a3b8;text-align:center;padding:40px">Loading logs...</p>';
  try {
    const log = await api(`/api/audit/${encodeURIComponent(uid)}`);
    if (!log || log.length === 0) { $("auditLog").innerHTML = '<p style="color:#64748b;text-align:center;padding:40px">No logs found</p>'; return; }
    $("auditLog").innerHTML = log.map(e => `<div class="audit-item"><div class="audit-time">${e.server_ts ? new Date(e.server_ts).toLocaleString() : "—"}</div><div class="audit-event">${escape(e.event || "")}</div>${e.detail ? `<div class="audit-detail">${escape(e.detail)}</div>` : ""}</div>`).join("");
  } catch (e) { $("auditLog").innerHTML = `<p style="color:#ef4444">${e.message}</p>`; }
}

function connectWS() {
  if (WS) WS.close();
  const proto = location.protocol === "https:" ? "wss:" : "ws:";
  WS = new WebSocket(`${proto}//${location.host}/ws/devices`);
  WS.onopen = () => { const s = $("connectionStatus"); if (s) { s.className = "status-badge live"; s.innerHTML = '<span class="dot"></span> LIVE'; } };
  WS.onclose = () => { const s = $("connectionStatus"); if (s) { s.className = "status-badge offline"; s.innerHTML = '<span class="dot"></span> OFFLINE'; } setTimeout(connectWS, 3000); };
  WS.onmessage = (e) => { try { DEVICES = JSON.parse(e.data); renderDevices(); updateAuditDeviceList(); $("deviceCount").textContent = `${DEVICES.filter(d => d.is_paired).length} Devices`; } catch (_) {} };
}

function toast(msg, type = "") {
  const el = $("toast"); const m = $("toastMessage");
  if (m) m.textContent = msg; else el.textContent = msg;
  el.className = "toast show " + type;
  clearTimeout(window._toastTimer);
  window._toastTimer = setTimeout(() => { el.classList.remove("show"); }, 3500);
}

autoLogin();
