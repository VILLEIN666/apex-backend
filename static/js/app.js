let TOKEN = localStorage.getItem("apex_token") || "";
const $ = id => document.getElementById(id);

function showPanel() {
  $("auth").style.display = "none";
  $("panel").style.display = "block";
  refresh();
}

async function api(path, opts = {}) {
  opts.headers = {
    ...(opts.headers || {}),
    "Authorization": "Bearer " + TOKEN
  };
  const r = await fetch(path, opts);
  if (r.status === 401) { logout(); throw new Error("auth"); }
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

async function register() {
  const email = $("email").value.trim();
  const name = $("name").value.trim();
  const pass = $("pass").value;
  const consent = $("consent").checked;

  $("autherr").textContent = "";
  if (!email || !pass) return $("autherr").textContent = "Email ও password দিন";
  if (!consent) return $("autherr").textContent = "Consent checkbox লাগবে";

  try {
    const r = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email, name: name || email.split("@")[0],
        password: pass, consent_accepted: consent
      })
    });
    const j = await r.json();
    if (!r.ok) throw new Error(j.detail || "Register failed");
    TOKEN = j.access_token;
    localStorage.setItem("apex_token", TOKEN);
    showPanel();
  } catch (e) {
    $("autherr").textContent = e.message;
  }
}

async function login() {
  const email = $("email").value.trim();
  const pass = $("pass").value;
  $("autherr").textContent = "";
  if (!email || !pass) return $("autherr").textContent = "Email ও password দিন";

  try {
    const body = new URLSearchParams({ username: email, password: pass });
    const r = await fetch("/api/auth/login", { method: "POST", body });
    const j = await r.json();
    if (!r.ok) throw new Error(j.detail || "Login failed");
    TOKEN = j.access_token;
    localStorage.setItem("apex_token", TOKEN);
    showPanel();
  } catch (e) {
    $("autherr").textContent = e.message;
  }
}

function logout() {
  TOKEN = "";
  localStorage.removeItem("apex_token");
  $("auth").style.display = "block";
  $("panel").style.display = "none";
}

async function createPairing() {
  const cname = $("cname").value.trim() || "New Child";
  $("qrbox").innerHTML = '<p class="small">Generating QR…</p>';
  try {
    const j = await api(`/api/devices/create-pairing?child_name=${encodeURIComponent(cname)}`, { method: "POST" });
    $("qrbox").innerHTML = `
      <img src="${j.qr_url}" alt="QR">
      <p class="small">${j.enroll_url}</p>
      <p class="small">📱 Scan with child's phone camera</p>
    `;
    $("cname").value = "";
    refresh();
  } catch (e) {
    $("qrbox").innerHTML = `<p class="err">QR failed: ${e.message}</p>`;
  }
}

async function refresh() {
  try {
    const list = await api("/api/devices");
    $("childlist").innerHTML = list.length
      ? list.map(d => `
        <li>
          <div>
            <b>${escape(d.child_name)}</b><br>
            <span class="small">${escape(d.device_model)} • v${d.android_version || '?'}</span>
          </div>
          <span class="${d.is_online ? 'online' : 'offline'}">${d.is_online ? 'ONLINE' : 'OFFLINE'}</span>
        </li>`).join("")
      : '<p class="empty">No devices yet</p>';
  } catch (e) {
    console.error(e);
  }
}

function escape(s) {
  return String(s || '').replace(/[&<>"']/g, c =>
    ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

if (TOKEN) {
  showPanel();
  setInterval(refresh, 10000);
}
