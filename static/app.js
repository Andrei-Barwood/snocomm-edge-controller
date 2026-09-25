let isPaused = false;
let importLock = false;
let ws;
let lastChartUpdate = performance.now();
const $ = (id) => document.getElementById(id);
const palette = { ink: "#303030", paper: "#D7E0EC", gold: "#E3CA75", indigo: "#5A64BF", indigoDeep: "#485199" };

document.querySelectorAll(".nav-item").forEach((button) =>
  button.addEventListener("click", () => {
    if (button.hidden) return;
    document.querySelectorAll(".nav-item").forEach((item) => {
      item.classList.remove("active");
      item.removeAttribute("aria-current");
    });
    button.classList.add("active");
    button.setAttribute("aria-current", "page");
    document.querySelectorAll(".view").forEach((view) => {
      const active = view.id === `${button.dataset.view}-view`;
      view.classList.toggle("active", active);
      view.hidden = !active;
    });
    document.querySelector(".primary-nav").classList.remove("open");
    $("mobile-menu").setAttribute("aria-expanded", "false");
  })
);
$("mobile-menu").addEventListener("click", (e) => {
  const nav = $("primary-nav");
  const open = nav.classList.toggle("open");
  e.currentTarget.setAttribute("aria-expanded", String(open));
});

Chart.defaults.color = "#4F4F4F";
Chart.defaults.font.family = "Inter, system-ui, sans-serif";
const gridColor = "rgba(79,79,79,.13)";
const waveformChart = new Chart($("waveformChart"), {
  type: "line",
  data: {
    labels: Array.from({ length: 128 }, (_, i) => (i / 12.8).toFixed(1)),
    datasets: [
      { label: "Ia (carga)", borderColor: palette.indigo, backgroundColor: "rgba(90,100,191,.08)", borderWidth: 2, pointRadius: 0, data: [] },
      { label: "Referencia Ia", borderColor: "#CCB244", backgroundColor: "rgba(204,178,68,.10)", borderWidth: 2, pointRadius: 0, data: [] },
      { label: "In (neutro)", borderColor: "#8f3232", borderWidth: 1.5, pointRadius: 0, borderDash: [4, 3], data: [] },
    ],
  },
  options: {
    responsive: true,
    animation: false,
    interaction: { intersect: false },
    scales: {
      x: { grid: { color: gridColor }, title: { display: true, text: "Tiempo (ms)" } },
      y: { grid: { color: gridColor }, title: { display: true, text: "Amplitud (A)" } },
    },
    plugins: { legend: { labels: { usePointStyle: true } } },
  },
});
const spectrumChart = new Chart($("spectrumChart"), {
  type: "bar",
  data: {
    labels: ["I1", "H3", "H5", "H7"],
    datasets: [{ label: "RMS (A)", backgroundColor: [palette.indigoDeep, palette.gold, palette.indigo, "#8f3232"], data: [] }],
  },
  options: {
    responsive: true,
    animation: false,
    scales: {
      x: { grid: { display: false } },
      y: { grid: { color: gridColor }, title: { display: true, text: "RMS (A)" } },
    },
    plugins: { legend: { display: false } },
  },
});

function addLog(message, type = "info") {
  const el = document.createElement("div");
  el.className = `log-entry log-${type}`;
  el.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
  $("logs-box").appendChild(el);
  while ($("logs-box").children.length > 50) $("logs-box").firstChild.remove();
  $("logs-box").scrollTop = $("logs-box").scrollHeight;
}
$("clear-logs").addEventListener("click", () => {
  $("logs-box").replaceChildren();
  addLog("Registro limpiado por el operador.", "warn");
});

function fmt(value, digits = 1, suffix = "") {
  if (value === undefined || value === null || Number.isNaN(Number(value))) return "—";
  return `${Number(value).toFixed(digits)}${suffix}`;
}

function applyTelemetry(data) {
  $("kpi-dsp").textContent = fmt(data.t_dsp_ms, 3, " ms");
  $("kpi-freq").textContent = fmt(data.freq_est, 2, " Hz");
  $("kpi-thdi").textContent = fmt(data.thdi, 1, " %");
  $("kpi-sat").textContent = data.is_saturated ? "SATURADA" : "DENTRO DE LÍMITE";
  $("sat-card").style.borderTopColor = data.is_saturated ? palette.gold : palette.indigo;
  $("kpi-i1").textContent = fmt(data.i1_rms, 1, " A");
  $("kpi-h3").textContent = `${fmt(data.h3_rms, 1)} / ${fmt(data.in_rms, 1)} A`;
  $("kpi-h5").textContent = fmt(data.h5_rms, 1, " A");
  $("kpi-h7").textContent = fmt(data.h7_rms, 1, " A");
  if (performance.now() - lastChartUpdate > 200) {
    lastChartUpdate = performance.now();
    waveformChart.data.datasets[0].data = data.raw_waveform || [];
    waveformChart.data.datasets[1].data = data.comp_waveform || [];
    waveformChart.data.datasets[2].data = data.raw_neutral || [];
    waveformChart.update();
    spectrumChart.data.datasets[0].data = [data.i1_rms || 0, data.h3_rms || 0, data.h5_rms || 0, data.h7_rms || 0];
    spectrumChart.update();
    addLog(
      `Trama ${data.frame_count} · ${fmt(data.freq_est, 2)} Hz · THDi ${fmt(data.thdi, 1)} % · In ${fmt(data.in_rms, 1)} A`
    );
  }
}

function connectWebSocket() {
  const protocol = location.protocol === "https:" ? "wss:" : "ws:";
  ws = new WebSocket(`${protocol}//${location.host}/ws`);
  ws.onopen = () => addLog("Canal de telemetría conectado.");
  ws.onmessage = (event) => {
    if (isPaused || importLock) return;
    applyTelemetry(JSON.parse(event.data));
  };
  ws.onclose = () => {
    addLog("Canal desconectado; reintentando…", "warn");
    setTimeout(connectWebSocket, 2000);
  };
  ws.onerror = () => addLog("No fue posible conectar con la telemetría.", "error");
}
$("toggle-pause").addEventListener("click", (e) => {
  isPaused = !isPaused;
  e.currentTarget.textContent = isPaused ? "Reanudar datos" : "Pausar datos";
  e.currentTarget.setAttribute("aria-pressed", String(isPaused));
  addLog(isPaused ? "Visualización pausada." : "Visualización reanudada.", "warn");
});

const escapeHtml = (value) =>
  String(value).replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[char]));

async function refreshRuntime() {
  try {
    const runtime = await (await fetch("/api/runtime")).json();
    $("chip-server-label").textContent = runtime.server === "running" ? "en ejecución" : runtime.server;
    $("chip-acq-label").textContent = runtime.acquisition_label || runtime.acquisition;
    $("chip-hw-label").textContent = runtime.hardware_label || runtime.hardware;
    $("chip-acq").classList.toggle("live", runtime.telemetry_live || runtime.acquisition === "imported");
    $("monitor-idle").hidden = runtime.acquisition !== "none" || importLock;
  } catch (_error) {
    $("chip-server-label").textContent = "sin API";
  }
}

async function refreshProject() {
  try {
    const project = await (await fetch("/api/project")).json();
    $("project-id").textContent = project.project_id;
    const thdi = project.links.observed_thdi;
    $("project-thdi").textContent = thdi == null ? "sin datos DSP" : `${Number(thdi).toFixed(1)} %`;
    const icomp = project.links.tan_compensation_current_a ?? project.links.observed_compensation_current_a;
    $("project-icomp").textContent = icomp == null ? "—" : `${Number(icomp).toFixed(1)} A`;
    const bank = project.power_stage;
    $("project-bank").textContent = bank ? `${bank.state}${bank.fault && bank.fault !== "NONE" ? " · " + bank.fault : ""}` : "—";
  } catch (_error) {
    $("project-id").textContent = "no disponible";
  }
}
$("reset-project").addEventListener("click", async () => {
  await fetch("/api/project/reset", { method: "POST" });
  await refreshProject();
  addLog("Proyecto común reiniciado.", "warn");
});

$("design-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const submit = event.currentTarget.querySelector("button[type=submit]");
  const payload = {
    potencia_kw: Number(form.get("potencia_kw")),
    num_racks: Number(form.get("num_racks")),
    redundancia: form.get("redundancia"),
    ip_minimo: Number(String(form.get("ip_minimo")).replace("IP", "")),
    carga_armonica: form.has("carga_armonica"),
    sismico: form.has("sismico"),
  };
  submit.disabled = true;
  submit.textContent = "Calculando…";
  $("form-message").textContent = "";
  try {
    const response = await fetch("/api/tan/design", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "No se pudo calcular el diseño.");
    renderDesign(data);
    await refreshProject();
  } catch (error) {
    $("form-message").textContent = error.message;
  } finally {
    submit.disabled = false;
    submit.textContent = "Calcular diseño";
  }
});

function reportButtons(reports) {
  const labels = { xlsx: "Excel", pdf: "PDF", json: "JSON", md: "Markdown", html: "HTML", csv: "CSV BOM" };
  const items = Object.entries(reports || {}).map(([fmt, meta]) => {
    const target = fmt === "html" ? " target=\"_blank\" rel=\"noopener\"" : " download";
    return `<a class="button secondary report-link" href="${escapeHtml(meta.url)}"${target}>${labels[fmt] || fmt}</a>`;
  });
  return `<div class="export-bar"><p class="eyebrow">INFORME EN VARIOS FORMATOS</p><div class="export-actions">${items.join("")}</div></div>`;
}

function renderTable(headers, rows) {
  const head = headers.map((h) => `<th>${escapeHtml(h)}</th>`).join("");
  const body = rows
    .map((row) => `<tr>${row.map((cell) => `<td>${escapeHtml(cell)}</td>`).join("")}</tr>`)
    .join("");
  return `<div class="table-wrap"><table class="data-table"><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
}

function renderDesign(data) {
  const e = data.electrical;
  const n = data.enclosure;
  const s = data.separation;
  const observed = data.observed_harmonics;
  const warnings = (data.warnings || []).map((w) => `<div class="warning">${escapeHtml(w)}</div>`).join("");
  const observedBlock = observed
    ? `<article class="panel"><p class="eyebrow">MONITOR → TAN</p><h2>THDi ${escapeHtml(String(Number(observed.thdi).toFixed(1)))} %</h2>
       <p>I compensación observada: <strong>${escapeHtml(String(data.compensation_current_a))} A</strong></p>
       <p>${escapeHtml(data.ahf_module_suggestion || "")}</p>
       <p class="muted">${escapeHtml(data.ric04_neutral_note || "")}</p></article>`
    : `<article class="panel"><p class="eyebrow">MONITOR → TAN</p><h2>Sin telemetría DSP</h2><p>El prediseño no recibió THDi. Arranque industrial o calcule sólo con el flag de carga armónica.</p></article>`;
  const verTable = renderTable(
    ["N°", "Característica", "Artículo", "Estado"],
    (data.verifications || []).map((item) => [item.numero, item.caracteristica, item.articulo, item.estado])
  );
  const bomTable = renderTable(
    ["Código", "Descripción", "Cant.", "Ud.", "Categoría"],
    (data.bom || []).map((item) => [item.codigo, item.descripcion, item.cantidad, item.unidad, item.categoria])
  );
  $("design-result").innerHTML = `<article class="panel result-hero"><p class="eyebrow">${escapeHtml(data.shared_project_id || data.project_id)}</p><h2>${escapeHtml(n.nombre)}</h2><p>Familia ${escapeHtml(s.familia_tan)} · Forma ${escapeHtml(s.forma)} · IP${escapeHtml(n.ip_seleccionado)}</p></article><div class="result-grid"><div class="result-metric"><span>Corriente base</span><strong>${e.in_base_a} A</strong></div><div class="result-metric"><span>Selección</span><strong>${e.in_seleccion_a} A</strong></div><div class="result-metric"><span>Icc estimada</span><strong>${e.icc_estimada_ka} kA</strong></div><div class="result-metric"><span>ΔT estimado</span><strong>${e.delta_t_estimado_c} °C</strong></div></div>${warnings}${observedBlock}${reportButtons(data.reports)}<div class="result-detail"><article class="panel"><p class="eyebrow">ENVOLVENTE</p><h2>${escapeHtml(n.codigo)}</h2><ul>${n.justificacion.slice(0, 3).map((x) => `<li>${escapeHtml(x)}</li>`).join("")}</ul></article><article class="panel"><p class="eyebrow">SEGREGACIÓN</p><h2>Forma ${escapeHtml(s.forma)}</h2><ul>${s.justificacion.slice(0, 3).map((x) => `<li>${escapeHtml(x)}</li>`).join("")}</ul></article></div><article class="panel"><p class="eyebrow">VERIFICACIONES IEC 61439</p><h2>Tabla de diseño</h2>${verTable}</article><article class="panel"><p class="eyebrow">LISTA DE MATERIALES</p><h2>BOM tipificada</h2>${bomTable}</article>`;
}

let powerStageStatus = null;
async function refreshPowerStage() {
  try {
    const response = await fetch("/api/power-stage/status");
    if (!response.ok) throw new Error("Estado HIL no disponible.");
    renderPowerStage(await response.json());
    await refreshProject();
  } catch (error) {
    $("ps-message").textContent = error.message;
  }
}
function renderPowerStage(data) {
  powerStageStatus = data;
  const m = data.measurements;
  const o = data.outputs;
  const i = data.interlocks;
  $("ps-state").textContent = data.state;
  $("ps-fault").textContent = data.fault === "NONE" ? "Sin fallas activas" : `${data.fault}: ${data.fault_message}`;
  $("ps-vdc").textContent = `${m.dc_bus_v.toFixed(1)} V`;
  $("ps-current").textContent = `${m.phase_current_a.toFixed(1)} A`;
  $("ps-temperature").textContent = `${m.temperature_c.toFixed(1)} °C`;
  $("ps-precharge-label").textContent = `${m.precharge_percent.toFixed(0)}%`;
  $("ps-precharge-bar").style.width = `${Math.min(100, m.precharge_percent)}%`;
  $("chain-source").classList.toggle("active", data.state !== "POWER_OFF");
  $("chain-precharge").classList.toggle("active", o.precharge_contactor);
  $("chain-main").classList.toggle("active", o.main_contactor);
  $("chain-gates").classList.toggle("active", o.gate_enable && o.pwm_enabled);
  $("interlock-estop").classList.toggle("interlock-ok", i.estop_ok);
  $("interlock-sensor").classList.toggle("interlock-ok", i.sensor_ok);
  $("interlock-driver").classList.toggle("interlock-ok", i.gate_driver_ready);
  $("ps-events").innerHTML = data.events
    .map(
      (event) =>
        `<div class="event-row"><time>${escapeHtml(new Date(event.timestamp).toLocaleString())}</time><strong>${escapeHtml(event.state)}</strong><span>${escapeHtml(event.message)}</span></div>`
    )
    .join("");
}
async function sendPowerStageCommand(command, fault = null) {
  $("ps-message").textContent = "";
  try {
    const response = await fetch("/api/power-stage/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command, fault }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Comando rechazado por los interlocks.");
    renderPowerStage(data);
    await refreshProject();
  } catch (error) {
    $("ps-message").textContent = error.message;
  }
}
document.querySelectorAll(".ps-command").forEach((button) =>
  button.addEventListener("click", () => sendPowerStageCommand(button.dataset.command))
);
$("inject-fault").addEventListener("click", () => sendPowerStageCommand("inject_fault", $("fault-select").value));

async function loadBenchPackage() {
  try {
    const pack = await (await fetch("/api/bench/package")).json();
    $("bench-unifilar").innerHTML = pack.unifilar.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
    $("bench-risks").innerHTML = pack.risks
      .map((item) => `<li><strong>${escapeHtml(item.id)}</strong> ${escapeHtml(item.hazard)}</li>`)
      .join("");
    $("bench-bom").innerHTML = pack.cft_bom
      .map((item) => `<li>${escapeHtml(item.item)} <span>${escapeHtml(item.source)}</span></li>`)
      .join("");
    $("bench-accept").innerHTML = pack.acceptance
      .map((item) => `<li><strong>${escapeHtml(item.id)}</strong> ${escapeHtml(item.criterion)}</li>`)
      .join("");
    if (pack.layers) {
      $("bench-layers").innerHTML = ["A", "B", "C"]
        .filter((key) => pack.layers[key])
        .map((key) => `<li><strong>Capa ${key}</strong> ${escapeHtml(pack.layers[key])}</li>`)
        .join("");
    }
    if (pack.forbidden) {
      $("bench-forbidden").textContent = `Prohibido en este TPA: ${pack.forbidden}`;
    }
  } catch (_error) {
    $("bench-unifilar").innerHTML = "<li>No se pudo cargar el paquete del banco.</li>";
  }
}

function showImportMeta(payload) {
  const meta = payload.meta || {};
  const warnings = payload.warnings || [];
  const bits = [
    meta.filename && `Archivo: ${meta.filename}`,
    meta.mode && `Modo: ${meta.mode}`,
    meta.samples && `${meta.samples} muestras`,
    meta.fs_inferred_hz && `fs ≈ ${Number(meta.fs_inferred_hz).toFixed(0)} Hz`,
    meta.used_channels && `Canales: ${(meta.used_channels || []).join(", ")}`,
  ].filter(Boolean);
  $("import-meta").hidden = false;
  $("import-meta").innerHTML = `<p>${bits.map(escapeHtml).join(" · ")}</p>${
    warnings.length ? `<ul>${warnings.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : ""
  }`;
}

$("import-apply").addEventListener("click", async () => {
  const file = $("import-file").files[0];
  $("import-message").textContent = "";
  if (!file) {
    $("import-message").textContent = "Elija un CSV o JSON exportado del osciloscopio o de la central.";
    return;
  }
  const body = new FormData();
  body.append("file", file);
  const fs = Number($("import-fs").value);
  if (fs > 1) body.append("fs", String(fs));
  body.append("current_scale", $("import-iscale").value || "1");
  body.append("voltage_scale", $("import-vscale").value || "1");
  $("import-apply").disabled = true;
  $("import-apply").textContent = "Procesando…";
  try {
    const response = await fetch("/api/acquisition/import", { method: "POST", body });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "No se pudo importar la campaña.");
    importLock = true;
    lastChartUpdate = 0;
    applyTelemetry(data.telemetry);
    showImportMeta(data);
    addLog(`Campaña importada: ${file.name}`, "warn");
    await refreshRuntime();
    await refreshProject();
  } catch (error) {
    $("import-message").textContent = error.message;
  } finally {
    $("import-apply").disabled = false;
    $("import-apply").textContent = "Procesar y usar en el Monitor";
  }
});

$("import-clear").addEventListener("click", async () => {
  await fetch("/api/acquisition/clear", { method: "POST" });
  importLock = false;
  $("import-meta").hidden = true;
  $("import-message").textContent = "";
  addLog("Campaña importada liberada.", "warn");
  await refreshRuntime();
});

setInterval(refreshPowerStage, 500);
refreshPowerStage();
refreshRuntime();
refreshProject();
loadBenchPackage();
setInterval(refreshRuntime, 4000);
connectWebSocket();

let calcTemplates = [];
let calcBarChart = null;
let calcWaveChart = null;

function showView(viewName) {
  const target = document.querySelector(`.nav-item[data-view="${viewName}"]`);
  if (target?.hidden) return;
  document.querySelectorAll(".nav-item").forEach((item) => {
    const active = item.dataset.view === viewName;
    item.classList.toggle("active", active);
    if (active) item.setAttribute("aria-current", "page");
    else item.removeAttribute("aria-current");
  });
  document.querySelectorAll(".view").forEach((view) => {
    const active = view.id === `${viewName}-view`;
    view.classList.toggle("active", active);
    view.hidden = !active;
  });
  document.querySelector(".primary-nav").classList.remove("open");
  $("mobile-menu").setAttribute("aria-expanded", "false");
}

document.querySelectorAll(".js-open-legal").forEach((button) =>
  button.addEventListener("click", () => showView("legal"))
);

function fieldControl(field) {
  if (field.type === "select") {
    const options = (field.options || [])
      .map((opt) => `<option${opt === field.default ? " selected" : ""}>${escapeHtml(opt)}</option>`)
      .join("");
    return `<select name="${escapeHtml(field.name)}">${options}</select>`;
  }
  if (field.type === "checkbox") {
    return `<span class="check"><input name="${escapeHtml(field.name)}" type="checkbox"${field.default ? " checked" : ""}><span></span></span>`;
  }
  if (field.type === "text") {
    return `<input name="${escapeHtml(field.name)}" type="text" value="${escapeHtml(field.default || "")}">`;
  }
  const step = field.step != null ? ` step="${escapeHtml(field.step)}"` : ' step="0.1"';
  const unit = field.unit ? ` <span>${escapeHtml(field.unit)}</span>` : "";
  return `${unit}<input name="${escapeHtml(field.name)}" type="number"${step} value="${escapeHtml(field.default ?? "")}">`;
}

function renderCalcFields(template) {
  $("calc-template-summary").textContent = template.summary || "";
  $("calc-template-iec").textContent = template.iec || "";
  $("calc-fields").innerHTML = (template.fields || [])
    .map((field) => `<label>${escapeHtml(field.label)}${fieldControl(field)}</label>`)
    .join("");
}

function collectCalcParams(form) {
  const params = {};
  const template = calcTemplates.find((item) => item.id === $("calc-template").value);
  (template?.fields || []).forEach((field) => {
    if (field.type === "checkbox") {
      const input = form.querySelector(`[name="${field.name}"]`);
      params[field.name] = Boolean(input?.checked);
    } else {
      params[field.name] = form[field.name]?.value;
    }
  });
  return params;
}

function ensureCalcCharts() {
  if (calcBarChart) return;
  calcBarChart = new Chart($("calcBarChart"), {
    type: "bar",
    data: { labels: [], datasets: [{ label: "Valor", backgroundColor: [palette.indigoDeep, palette.gold, palette.ink, "#8f3232"], data: [] }] },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: { y: { grid: { color: gridColor } }, x: { grid: { display: false } } },
    },
  });
  calcWaveChart = new Chart($("calcWaveChart"), {
    type: "line",
    data: {
      labels: [],
      datasets: [
        { label: "CSV anterior", borderColor: palette.indigo, borderWidth: 2, pointRadius: 0, data: [] },
        { label: "CSV nuevo", borderColor: "#CCB244", borderWidth: 2, pointRadius: 0, data: [] },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { usePointStyle: true } } },
      scales: { x: { display: false }, y: { grid: { color: gridColor } } },
    },
  });
}

function renderCalculator(data) {
  ensureCalcCharts();
  const charts = data.charts || {};
  calcBarChart.data.labels = charts.labels || [];
  calcBarChart.data.datasets[0].data = charts.values || [];
  calcBarChart.update();
  const before = charts.wave_before || [];
  const after = charts.wave_after || [];
  const n = Math.max(before.length, after.length, 1);
  calcWaveChart.data.labels = Array.from({ length: n }, (_, i) => i);
  calcWaveChart.data.datasets[0].data = before;
  calcWaveChart.data.datasets[1].data = after;
  calcWaveChart.update();
  const pill = (data.status || "").toLowerCase();
  const suggestions = (data.suggestions || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("");
  const pdf = data.pdf
    ? `<a class="button primary report-link" href="${escapeHtml(data.pdf.url)}" download>Descargar informe PDF</a>`
    : "";
  $("calculator-result").innerHTML = `
    <article class="panel result-hero">
      <p class="eyebrow">${escapeHtml(data.run_id || "")}</p>
      <h2>${escapeHtml(data.template.name)}</h2>
      <p><span class="status-pill ${escapeHtml(pill)}">${escapeHtml(data.status_label)}</span> · ${escapeHtml(data.template.iec)}</p>
    </article>
    <div class="result-grid">
      <div class="result-metric"><span>Medido</span><strong>${data.measured == null ? "—" : escapeHtml(String(data.measured))}</strong></div>
      <div class="result-metric"><span>Diseño</span><strong>${data.design == null ? "—" : escapeHtml(String(data.design))}</strong></div>
      <div class="result-metric"><span>Desvío</span><strong>${data.abs_delta == null ? "—" : escapeHtml(String(data.abs_delta))}</strong></div>
      <div class="result-metric"><span>Relativo</span><strong>${data.rel_delta_pct == null ? "—" : escapeHtml(String(data.rel_delta_pct)) + " %"}</strong></div>
    </div>
    <article class="panel"><p class="eyebrow">LECTURA</p><h2>${escapeHtml(data.metric_label)}</h2><p>${escapeHtml(data.narrative)}</p></article>
    <article class="panel"><p class="eyebrow">IEC 61439-1 &amp; -2</p><h2>Por qué conviene el conjunto</h2><p>${escapeHtml(data.iec_note)}</p></article>
    <article class="panel chart-wrapper" id="calc-bar-panel"><div class="panel-title"><div><p class="eyebrow">COMPARACIÓN</p><h2>Valores de campaña y diseño</h2></div></div></article>
    <article class="panel"><p class="eyebrow">SUGERENCIAS</p><h2>Decisiones informadas</h2><ul class="calc-suggestions">${suggestions}</ul><div class="export-actions" style="margin-top:14px">${pdf}</div></article>
  `;
  $("calc-bar-panel").appendChild(calcBarChart.canvas);
  calcBarChart.resize();
  if (before.length || after.length) {
    const wavePanel = document.createElement("article");
    wavePanel.className = "panel chart-wrapper";
    wavePanel.innerHTML = `<div class="panel-title"><div><p class="eyebrow">FORMA DE ONDA</p><h2>CSV anterior y nuevo</h2></div></div>`;
    wavePanel.appendChild(calcWaveChart.canvas);
    $("calculator-result").appendChild(wavePanel);
    calcWaveChart.resize();
  }
}

async function loadCalculator() {
  try {
    const data = await (await fetch("/api/calculator/templates")).json();
    calcTemplates = data.templates || [];
    $("calc-template").innerHTML = calcTemplates
      .map((item) => `<option value="${escapeHtml(item.id)}">${escapeHtml(item.id)} · ${escapeHtml(item.name)}</option>`)
      .join("");
    if (calcTemplates[0]) renderCalcFields(calcTemplates[0]);
  } catch (_error) {
    $("calc-message").textContent = "No se pudieron cargar las 24 plantillas.";
  }
  try {
    const pack = await (await fetch("/api/calculator/examples")).json();
    $("demo-example-list").innerHTML = (pack.examples || [])
      .map(
        (item) =>
          `<a class="demo-card" href="${escapeHtml(item.url)}" download>
            <small>${escapeHtml(item.template_id)} · ${escapeHtml(item.role)}</small>
            <strong>${escapeHtml(item.title)}</strong>
            <small>${escapeHtml(item.story)}</small>
          </a>`
      )
      .join("");
  } catch (_error) {
    $("demo-example-list").innerHTML = "<p class=\"muted\">No se pudieron listar los CSV de demo.</p>";
  }
}

$("calc-template").addEventListener("change", () => {
  const template = calcTemplates.find((item) => item.id === $("calc-template").value);
  if (template) renderCalcFields(template);
});

$("calculator-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  $("calc-message").textContent = "";
  const after = $("calc-csv-after").files[0];
  const before = $("calc-csv-before").files[0];
  if (!after && !before) {
    $("calc-message").textContent = "Adjunte al menos un CSV del osciloscopio.";
    return;
  }
  const body = new FormData();
  body.append("template_id", $("calc-template").value);
  body.append("params", JSON.stringify(collectCalcParams(event.currentTarget)));
  if (before) body.append("csv_before", before);
  if (after) body.append("csv_after", after);
  const submit = event.currentTarget.querySelector("button[type=submit]");
  submit.disabled = true;
  submit.textContent = "Comparando…";
  try {
    const response = await fetch("/api/calculator/analyze", { method: "POST", body });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "No se pudo comparar.");
    renderCalculator(data);
  } catch (error) {
    $("calc-message").textContent = error.message;
  } finally {
    submit.disabled = false;
    submit.textContent = "Comparar y sugerir";
  }
});

async function loadLegal() {
  try {
    const data = await (await fetch("/api/calculator/legal")).json();
    $("legal-eyebrow").textContent = data.eyebrow || "MARCO DE USO";
    $("legal-title").textContent = data.title;
    $("legal-lead").textContent = data.lead || "";
    $("legal-sections").innerHTML = (data.sections || [])
      .map(
        (section) =>
          `<article class="legal-article"><h2>${escapeHtml(section.heading)}</h2>${(section.body || [])
            .map((p) => `<p>${escapeHtml(p)}</p>`)
            .join("")}</article>`
      )
      .join("");
  } catch (_error) {
    $("legal-lead").textContent = "No se pudo cargar el marco legal.";
  }
}

loadCalculator();
loadLegal();
