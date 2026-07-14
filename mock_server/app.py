"""
Mock "WorkFlow Pro" server used to exercise the test suite locally.

Reproduces the exact behaviors the case study describes so the tests
aren't just theoretical:
  - dashboard / project-list data "hydrates" after a short async delay
  - company2 is deliberately slower than company1 (per-tenant load variance)
  - the company2 test account requires 2FA
  - REST endpoints enforce tenant isolation via Bearer token + X-Tenant-ID
"""
import time
import uuid
from itertools import count

from flask import Flask, jsonify, request, session

app = Flask(__name__)
app.secret_key = "local-test-only-not-a-real-secret"

USERS = {
    "admin@company1.com": {"password": "password123", "tenant": "company1", "otp_required": False},
    "user@company2.com": {"password": "password123", "tenant": "company2", "otp_required": True},
}
VALID_OTP = "123456"

# in-memory "DB" seeded with one project per tenant
_id_counter = count(1)
PROJECTS = {}
for tenant, name in [("company1", "Company1 Kickoff"), ("company2", "Company2 Rollout")]:
    pid = next(_id_counter)
    PROJECTS[pid] = {"id": pid, "name": name, "tenant": tenant, "status": "active"}

TOKENS = {}  # token -> tenant


# ---------- HTML (drives the Playwright UI tests) ----------

LOGIN_HTML = """<!doctype html><html><body>
<form id="login-form">
  <input id="email" name="email">
  <input id="password" name="password" type="password">
  {otp_field}
  <button id="login-btn" type="button" onclick="doLogin()">Log in</button>
</form>
<script>
async function doLogin() {{
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const r = await fetch('/api/v1/auth/session-login', {{
    method: 'POST', headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{email, password}})
  }});
  const data = await r.json();
  if (data.otp_required) {{
    document.getElementById('otp-wrap').style.display = 'block';
    return;
  }}
  if (data.ok) window.location.href = '/dashboard';
}}
async function verifyOtp() {{
  const otp = document.getElementById('otp-code').value;
  const r = await fetch('/api/v1/auth/verify-otp', {{
    method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{otp}})
  }});
  const data = await r.json();
  if (data.ok) window.location.href = '/dashboard';
}}
</script>
</body></html>"""

OTP_FIELD = """<div id="otp-wrap" style="display:none">
  <input id="otp-code"><button id="verify-otp-btn" type="button" onclick="verifyOtp()">Verify</button>
</div>"""

DASHBOARD_HTML = """<!doctype html><html><body>
<div id="content"></div>
<script>
setTimeout(() => {{
  document.getElementById('content').innerHTML =
    '<div class="welcome-message">Welcome back!</div>';
}}, {delay});
</script>
</body></html>"""

PROJECTS_HTML = """<!doctype html><html><body>
<div class="project-list" id="list"></div>
<script>
setTimeout(async () => {{
  const r = await fetch('/api/v1/projects', {{headers: {{'X-Session': 'true'}}}});
  const data = await r.json();
  const list = document.getElementById('list');
  data.projects.forEach(p => {{
    const d = document.createElement('div');
    d.className = 'project-card';
    d.textContent = p.name + ' (' + p.tenant + ')';
    list.appendChild(d);
  }});
}}, {delay});
</script>
</body></html>"""


@app.route("/login")
def login_page():
    return LOGIN_HTML.format(otp_field=OTP_FIELD)


@app.route("/api/v1/auth/session-login", methods=["POST"])
def session_login():
    body = request.get_json()
    user = USERS.get(body.get("email"))
    if not user or user["password"] != body.get("password"):
        return jsonify({"ok": False, "error": "invalid_credentials"}), 401
    if user["otp_required"] and not session.get(f"otp_ok_{body['email']}"):
        session["pending_email"] = body["email"]
        return jsonify({"ok": False, "otp_required": True})
    session["tenant"] = user["tenant"]
    return jsonify({"ok": True})


@app.route("/api/v1/auth/verify-otp", methods=["POST"])
def verify_otp():
    body = request.get_json()
    email = session.get("pending_email")
    if not email or body.get("otp") != VALID_OTP:
        return jsonify({"ok": False}), 401
    session[f"otp_ok_{email}"] = True
    session["tenant"] = USERS[email]["tenant"]
    return jsonify({"ok": True})


@app.route("/dashboard")
def dashboard():
    tenant = session.get("tenant", "company1")
    delay = 300 if tenant == "company1" else 900  # per-tenant load variance
    return DASHBOARD_HTML.format(delay=delay)


@app.route("/projects")
def projects_page():
    tenant = session.get("tenant", "company1")
    delay = 300 if tenant == "company1" else 900
    return PROJECTS_HTML.format(delay=delay)


@app.route("/api/v1/projects", methods=["GET"])
def list_projects_for_session():
    tenant = session.get("tenant", "company1")
    time.sleep(0.05)
    projects = [p for p in PROJECTS.values() if p["tenant"] == tenant]
    return jsonify({"projects": projects})


# ---------- REST API (drives the pytest API layer + integration tests) ----------

@app.route("/api/v1/auth/login", methods=["POST"])
def api_login():
    body = request.get_json()
    user = USERS.get(body.get("email"))
    if not user or user["password"] != body.get("password"):
        return jsonify({"error": "invalid_credentials"}), 401
    token = str(uuid.uuid4())
    TOKENS[token] = user["tenant"]
    return jsonify({"token": token, "tenant": user["tenant"]})


def _authed_tenant():
    auth = request.headers.get("Authorization", "")
    token = auth.replace("Bearer ", "")
    header_tenant = request.headers.get("X-Tenant-ID")
    token_tenant = TOKENS.get(token)
    return token_tenant, header_tenant


@app.route("/api/v1/projects", methods=["POST"])
def create_project():
    token_tenant, header_tenant = _authed_tenant()
    if not token_tenant:
        return jsonify({"error": "unauthorized"}), 401
    body = request.get_json()
    pid = next(_id_counter)
    project = {"id": pid, "name": body["name"], "tenant": header_tenant, "status": "active"}
    PROJECTS[pid] = project
    return jsonify(project), 201


@app.route("/api/v1/projects/<int:pid>", methods=["GET"])
def get_project(pid):
    token_tenant, header_tenant = _authed_tenant()
    if not token_tenant:
        return jsonify({"error": "unauthorized"}), 401
    project = PROJECTS.get(pid)
    if not project or project["tenant"] != header_tenant:
        # 404, not 403 -- don't leak existence of another tenant's resource
        return jsonify({"error": "not_found"}), 404
    return jsonify(project)


@app.route("/api/v1/projects/<int:pid>", methods=["DELETE"])
def delete_project(pid):
    token_tenant, header_tenant = _authed_tenant()
    project = PROJECTS.get(pid)
    if project and project["tenant"] == header_tenant:
        del PROJECTS[pid]
    return "", 204


if __name__ == "__main__":
    app.run(port=5055)
