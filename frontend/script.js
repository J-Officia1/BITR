const form = document.getElementById("analysisForm");
const sourceText = document.getElementById("sourceText");
const apiBaseUrl = document.getElementById("apiBaseUrl");
const analyzeButton = document.getElementById("analyzeButton");
const demoButton = document.getElementById("demoButton");
const resetButton = document.getElementById("resetButton");
const statusBanner = document.getElementById("statusBanner");
const inputPanel = document.getElementById("inputPanel");
const telemetryPanel = document.getElementById("telemetryPanel");
const chartWrap = document.getElementById("chartWrap");
const resultCards = document.querySelectorAll(".result-card");
const detailCards = document.querySelectorAll(".detail-card");

const manipulationScoreEl = document.getElementById("manipulationScore");
const authenticityScoreEl = document.getElementById("authenticityScore");
const riskLevelEl = document.getElementById("riskLevel");
const guidancePreviewEl = document.getElementById("guidancePreview");
const guidanceTextEl = document.getElementById("guidanceText");
const manipulationBar = document.getElementById("manipulationBar");
const authenticityBar = document.getElementById("authenticityBar");
const tacticsGrid = document.getElementById("tacticsGrid");

const demoSampleText = "URGENT: Your bank account will be blocked within 30 minutes unless you verify now. This notice comes from the RBI cyber cell. Thousands have already completed the process successfully. Click immediately to avoid legal action.";
const emptyGuidancePreview = "Actionable guidance appears here after analysis.";
const emptyGuidanceText = "Paste text and run an analysis to receive a credibility summary, category breakdown, and safety guidance.";

let categoryChart;
let panelResizeObserver;
let currentLoadingButtonLabel = null;

function getDefaultApiBaseUrl() {
  if (window.location.protocol === "http:" || window.location.protocol === "https:") {
    return window.location.origin;
  }

  return "http://127.0.0.1:5000";
}

apiBaseUrl.value = getDefaultApiBaseUrl();

function initializeChart() {
  const ctx = document.getElementById("categoryChart");

  categoryChart = new Chart(ctx, {
    type: "radar",
    data: {
      labels: ["Fear", "Authority", "Scarcity", "Social Proof", "Emotional Amp"],
      datasets: [
        {
          label: "Category Score",
          data: [0, 0, 0, 0, 0],
          fill: true,
          backgroundColor: "rgba(72, 217, 255, 0.18)",
          borderColor: "#48d9ff",
          pointBackgroundColor: "#5cf2b5",
          pointBorderColor: "#07111f",
          pointHoverBackgroundColor: "#ffffff",
          pointHoverBorderColor: "#48d9ff",
          borderWidth: 2
        }
      ]
    },
    options: {
      maintainAspectRatio: false,
      scales: {
        r: {
          min: 0,
          max: 100,
          ticks: {
            display: false
          },
          angleLines: {
            color: "rgba(255,255,255,0.1)"
          },
          grid: {
            color: "rgba(255,255,255,0.08)"
          },
          pointLabels: {
            color: "#dce8f2",
            font: {
              family: "Manrope",
              size: 13,
              weight: "600"
            }
          }
        }
      },
      plugins: {
        legend: {
          display: false
        }
      }
    }
  });
}

function setStatus(message, type) {
  statusBanner.textContent = message;
  statusBanner.className = `status-banner ${type}`;
  statusBanner.classList.remove("hidden");
}

function hideStatus() {
  statusBanner.textContent = "";
  statusBanner.className = "status-banner hidden";
}

function clampScore(value) {
  const numeric = Number(value);
  if (Number.isNaN(numeric)) return 0;
  return Math.max(0, Math.min(100, numeric));
}

function normalizeCategoryScore(value) {
  const numeric = Number(value);
  if (Number.isNaN(numeric)) return 0;

  return numeric <= 10 ? numeric * 10 : numeric;
}

function riskTone(riskLevel) {
  const risk = (riskLevel || "").toLowerCase();
  if (risk.includes("high")) return "text-coral";
  if (risk.includes("moderate")) return "text-amber";
  return "text-mint";
}

function updateScoreCard(element, barElement, rawValue, suffix = "%") {
  const score = clampScore(rawValue);
  element.textContent = `${Math.round(score)}${suffix}`;
  barElement.style.width = `${score}%`;
}

function buildTacticMarkup(detectedTactics) {
  const entries = Object.entries(detectedTactics || {}).filter(([, values]) => {
    if (Array.isArray(values)) return values.length > 0;
    if (typeof values === "string") return values.trim().length > 0;
    return Boolean(values);
  });

  if (!entries.length) {
    tacticsGrid.innerHTML = `
      <div class="empty-state">
        No explicit tactics were returned by the API. The backend can populate <code>detected_tactics</code> with matched keywords or tactic explanations.
      </div>
    `;
    return;
  }

  tacticsGrid.innerHTML = entries.map(([category, values]) => {
    const normalized = Array.isArray(values) ? values.join(", ") : String(values);
    const count = Array.isArray(values) ? values.length : 1;

    return `
      <article class="tactic-card">
        <h4>${category}</h4>
        <p>${normalized}</p>
        <span class="tactic-badge">${count} signal${count === 1 ? "" : "s"} detected</span>
      </article>
    `;
  }).join("");
}

function updateChart(categoryScores = {}) {
  const values = [
    clampScore(normalizeCategoryScore(categoryScores.Fear ?? categoryScores["Fear Triggers"])),
    clampScore(normalizeCategoryScore(categoryScores.Authority ?? categoryScores["Authority Impersonation"])),
    clampScore(normalizeCategoryScore(categoryScores.Scarcity ?? categoryScores["Scarcity / Urgency"])),
    clampScore(normalizeCategoryScore(categoryScores.SocialProof ?? categoryScores["Social Proof"] ?? categoryScores["Social Proof Manipulation"])),
    clampScore(normalizeCategoryScore(categoryScores.EmotionalAmplification ?? categoryScores["Emotional Amplification"]))
  ];

  categoryChart.data.datasets[0].data = values;
  categoryChart.update();
}

function resetResultView() {
  updateScoreCard(manipulationScoreEl, manipulationBar, 0);
  updateScoreCard(authenticityScoreEl, authenticityBar, 0);
  riskLevelEl.textContent = "Low";
  riskLevelEl.className = "metric-value text-amber";
  guidancePreviewEl.textContent = emptyGuidancePreview;
  guidanceTextEl.textContent = emptyGuidanceText;
  tacticsGrid.innerHTML = `
    <div class="empty-state">
      Run an analysis to see detected manipulation tactics and matched signals here.
    </div>
  `;
  updateChart({
    Fear: 0,
    Authority: 0,
    Scarcity: 0,
    SocialProof: 0,
    EmotionalAmplification: 0
  });
}

function applyAnalysisResult(payload) {
  updateScoreCard(manipulationScoreEl, manipulationBar, payload.manipulation_score);
  updateScoreCard(authenticityScoreEl, authenticityBar, payload.authenticity_score);

  const riskLevel = payload.risk_level || "Low";
  riskLevelEl.textContent = riskLevel;
  riskLevelEl.className = `metric-value ${riskTone(riskLevel)}`;

  const guidance = payload.guidance || "No guidance returned.";
  guidancePreviewEl.textContent = guidance;
  guidanceTextEl.textContent = guidance;

  buildTacticMarkup(payload.detected_tactics);
  updateChart(payload.category_scores);
}

function setLoadingState(isLoading, activeButtonLabel = null) {
  currentLoadingButtonLabel = activeButtonLabel;

  resultCards.forEach((card) => card.classList.toggle("is-loading", isLoading));
  detailCards.forEach((card) => card.classList.toggle("is-loading", isLoading));
  telemetryPanel.classList.toggle("is-loading", isLoading);

  if (isLoading) {
    tacticsGrid.classList.add("is-loading");
    guidanceTextEl.classList.add("is-loading");
    analyzeButton.textContent = activeButtonLabel === "analyze" ? "Analyzing..." : "Analyze Text";
    demoButton.textContent = activeButtonLabel === "demo" ? "Loading Demo..." : "Load Demo Result";
    resetButton.textContent = "Reset";
  } else {
    tacticsGrid.classList.remove("is-loading");
    guidanceTextEl.classList.remove("is-loading");
    analyzeButton.textContent = "Analyze Text";
    demoButton.textContent = "Load Demo Result";
    resetButton.textContent = "Reset";
  }
}

function autoResizeTextarea() {
  if (!sourceText) return;

  sourceText.style.height = "auto";
  sourceText.style.height = `${sourceText.scrollHeight}px`;
  syncTelemetryHeight();
}

function syncTelemetryHeight() {
  if (!inputPanel || !telemetryPanel || !chartWrap) return;

  if (window.innerWidth < 1024) {
    telemetryPanel.style.height = "";
    telemetryPanel.style.minHeight = "";
    chartWrap.style.height = "";
    if (categoryChart) categoryChart.resize();
    return;
  }

  // Keep the input panel natural-height; only the telemetry card should follow it.
  telemetryPanel.style.height = "auto";
  telemetryPanel.style.minHeight = "";
  chartWrap.style.height = "";

  const inputHeight = Math.ceil(inputPanel.getBoundingClientRect().height);
  const telemetryHeaderHeight = telemetryPanel.scrollHeight - chartWrap.scrollHeight;
  const nextChartHeight = Math.max(320, inputHeight - telemetryHeaderHeight);

  telemetryPanel.style.height = `${inputHeight}px`;
  telemetryPanel.style.minHeight = `${inputHeight}px`;
  chartWrap.style.height = `${nextChartHeight}px`;

  if (categoryChart) {
    categoryChart.resize();
  }
}

async function pingServer() {
  const baseUrl = apiBaseUrl.value.trim().replace(/\/$/, "");
  if (!baseUrl) return;

  try {
    await fetch(`${baseUrl}/ping`, {
      method: "GET",
      mode: "cors"
    });
  } catch (error) {
    console.debug("Ping failed or route unavailable:", error);
  }
}

async function analyzeText(event) {
  event.preventDefault();

  currentLoadingButtonLabel = "analyze";
  const text = sourceText.value.trim();
  await requestAnalysis(text, "Analyzing text through the Flask backend...", "Analysis completed successfully. Frontend values now reflect live API data.");
}

async function requestAnalysis(text, loadingMessage, successMessage) {
  const baseUrl = apiBaseUrl.value.trim().replace(/\/$/, "");

  if (!text) {
    setStatus("Paste text before starting analysis.", "error");
    return;
  }

  if (!baseUrl) {
    setStatus("Enter a Flask API base URL first.", "error");
    return;
  }

  analyzeButton.disabled = true;
  demoButton.disabled = true;
  resetButton.disabled = true;
  setLoadingState(true, currentLoadingButtonLabel);
  setStatus(loadingMessage, "loading");

  try {
    const response = await fetch(`${baseUrl}/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      mode: "cors",
      body: JSON.stringify({ text })
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const payload = await response.json();

    if (payload.error) {
      throw new Error(payload.error);
    }

    applyAnalysisResult(payload);
    setStatus(successMessage, "success");
  } catch (error) {
    console.error(error);
    setStatus(error.message || "Could not reach the backend. Check Flask, CORS, and whether `/analyze` is running on the selected base URL.", "error");
  } finally {
    setLoadingState(false);
    analyzeButton.disabled = false;
    demoButton.disabled = false;
    resetButton.disabled = false;
  }
}

async function loadDemo() {
  currentLoadingButtonLabel = "demo";
  sourceText.value = demoSampleText;
  autoResizeTextarea();
  await requestAnalysis(
    demoSampleText,
    "Loading the demo sample through the live backend...",
    "Loaded the demo sample using the live backend, so the results match real analysis."
  );
}

function resetAnalysis() {
  sourceText.value = "";
  autoResizeTextarea();
  hideStatus();
  resetResultView();
  currentLoadingButtonLabel = null;
}

form.addEventListener("submit", analyzeText);
demoButton.addEventListener("click", loadDemo);
resetButton.addEventListener("click", resetAnalysis);
sourceText.addEventListener("input", autoResizeTextarea);
window.addEventListener("load", pingServer);
window.addEventListener("load", syncTelemetryHeight);
window.addEventListener("load", autoResizeTextarea);
window.addEventListener("resize", syncTelemetryHeight);

initializeChart();
resetResultView();
panelResizeObserver = new ResizeObserver(syncTelemetryHeight);
panelResizeObserver.observe(inputPanel);
panelResizeObserver.observe(sourceText);
loadDemo();
