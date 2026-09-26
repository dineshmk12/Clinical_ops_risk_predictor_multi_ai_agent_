const STATUS_CLASS = { Healthy: "good", "At Risk": "warning", Critical: "critical", Completed: "good" };
const STATUS_COLOR = { Healthy: "#0ca30c", "At Risk": "#fab219", Critical: "#d03b3b", Completed: "#0ca30c" };

const el = (id) => document.getElementById(id);
const sessionId = "dashboard-" + Math.random().toString(36).slice(2, 8);

async function api(path, opts) {
  const res = await fetch(path, opts);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}

function badge(tier) {
  const cls = STATUS_CLASS[tier] || "good";
  return `<span class="badge ${cls}">${tier}</span>`;
}

function barRow(name, score, tier) {
  const pct = Math.round((score ?? 0) * 100);
  const color = STATUS_COLOR[tier] || "#0ca30c";
  return `<div class="risk-row">
      <span class="name">${name}</span>
      <span class="bar-track"><span class="bar-fill" style="width:${pct}%;background:${color}"></span></span>
      ${badge(tier)}
    </div>`;
}

async function loadStudies() {
  const studies = await api("/studies");
  const select = el("study-select");
  select.innerHTML = studies.map((s) => `<option value="${s.study_id}">${s.study_id} — ${s.name}</option>`).join("");
  return studies;
}

function drawSparkline(canvas, series) {
  const ctx = canvas.getContext("2d");
  const w = canvas.width, h = canvas.height;
  ctx.clearRect(0, 0, w, h);
  if (!series.length) {
    ctx.fillStyle = "#898781";
    ctx.font = "13px system-ui";
    ctx.fillText("No enrollment data", 12, h / 2);
    return;
  }
  const max = Math.max(...series, 1);
  const min = Math.min(...series, 0);
  const pad = 12;
  const stepX = (w - pad * 2) / Math.max(series.length - 1, 1);
  const scaleY = (h - pad * 2) / Math.max(max - min, 1);

  ctx.strokeStyle = "#e1e0d9";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(pad, h - pad);
  ctx.lineTo(w - pad, h - pad);
  ctx.stroke();

  ctx.strokeStyle = "#2a78d6";
  ctx.lineWidth = 2;
  ctx.beginPath();
  series.forEach((v, i) => {
    const x = pad + i * stepX;
    const y = h - pad - (v - min) * scaleY;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  const lastX = pad + (series.length - 1) * stepX;
  const lastY = h - pad - (series[series.length - 1] - min) * scaleY;
  ctx.fillStyle = "#2a78d6";
  ctx.beginPath();
  ctx.arc(lastX, lastY, 4, 0, Math.PI * 2);
  ctx.fill();
}

async function loadDashboard(studyId) {
  el("health-value").textContent = "…";

  const safe = (promise, fallback) => promise.catch((err) => { console.error(err); return fallback; });

  const [health, forecast, compliance, sites, milestones, history, approvals] = await Promise.all([
    safe(api(`/studies/${studyId}/health`), null),
    safe(api(`/studies/${studyId}/enrollment/forecast`), null),
    safe(api(`/studies/${studyId}/compliance`), null),
    safe(api(`/studies/${studyId}/sites/risk`), { sites: [] }),
    safe(api(`/studies/${studyId}/milestones/predict`), { milestones: [] }),
    safe(api(`/studies/${studyId}/enrollment/history?weeks=26`), []),
    safe(api(`/approvals?status=pending`), []),
  ]);

  if (!health || !forecast || !compliance) return;

  el("health-value").textContent = `${health.health_score}`;
  el("health-value").style.color = health.health_score >= 75 ? "#0ca30c" : health.health_score >= 50 ? "#fab219" : "#d03b3b";
  el("health-trend").textContent = `${health.health_trend} — ${health.health_summary}`;

  el("enrollment-value").textContent = `${Math.round(forecast.delay_probability * 100)}%`;
  el("enrollment-sub").textContent = `Forecasted enrollment: ${forecast.forecasted_enrollment} (confidence ${Math.round(forecast.confidence * 100)}%)`;

  el("compliance-value").textContent = `${compliance.compliance_score}`;
  el("compliance-sub").textContent = compliance.findings[0] || "No findings";

  const siteList = el("site-list");
  siteList.innerHTML = sites.sites.length
    ? sites.sites.map((s) => barRow(s.site_id, s.risk_score, s.risk_tier)).join("")
    : `<div class="empty-state">No sites found</div>`;

  const milestoneList = el("milestone-list");
  milestoneList.innerHTML = milestones.milestones.length
    ? milestones.milestones
        .map((m) => barRow(`${m.milestone_type} (${m.predicted_date || "TBD"})`, m.delay_probability, m.risk_category))
        .join("")
    : `<div class="empty-state">No milestones found</div>`;

  const approvalList = el("approval-list");
  const studyApprovals = (approvals || []).filter((a) => a.study_id === studyId);
  approvalList.innerHTML = studyApprovals.length
    ? studyApprovals.map((a) => `<div class="risk-row"><span class="name">${a.approval_type}</span>${badge("At Risk")}</div>`).join("")
    : `<div class="empty-state">No pending approvals for this study</div>`;

  const weekly = {};
  history.forEach((r) => { weekly[r.date] = (weekly[r.date] || 0) + r.subjects_enrolled; });
  const series = Object.keys(weekly).sort().map((d) => weekly[d]);
  drawSparkline(el("enrollment-chart"), series);
}

function appendChat(role, html) {
  const log = el("chat-log");
  const div = document.createElement("div");
  div.className = `chat-msg ${role}`;
  div.innerHTML = html;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}

async function init() {
  await loadStudies();
  const select = el("study-select");
  const refresh = () => loadDashboard(select.value);
  select.addEventListener("change", refresh);
  await refresh();

  el("chat-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const input = el("chat-input");
    const question = input.value.trim();
    if (!question) return;
    appendChat("user", question);
    input.value = "";
    try {
      const res = await api("/copilot/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, study_id: select.value, question }),
      });
      const evidenceHtml = res.evidence && res.evidence.length
        ? `<div class="evidence">Evidence: ${res.evidence.map((e) => e.doc_id).join(", ")}</div>`
        : "";
      appendChat("assistant", `${res.answer.replace(/\n/g, "<br/>")}${evidenceHtml}`);
    } catch (err) {
      appendChat("assistant", `Request blocked: ${err.message}`);
    }
  });
}

init();
