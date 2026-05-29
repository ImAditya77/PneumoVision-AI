const state = {
  history: [],
  stats: { total: 0, normal: 0, pneumonia: 0, averageConfidence: 0 },
};

const form = document.querySelector("#prediction-form");
const formMessage = document.querySelector("#form-message");
const resultPanel = document.querySelector("#result-panel");
const fileInput = document.querySelector("#image-input");
const fileLabel = document.querySelector("#file-label");

document.querySelectorAll(".nav-button").forEach((button) => {
  button.addEventListener("click", () => showView(button.dataset.view));
});

fileInput.addEventListener("change", () => {
  fileLabel.textContent = fileInput.files[0]?.name || "Choose or drop a JPG/PNG chest X-ray";
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = new FormData(form);
  setMessage("Analyzing image...");
  form.querySelector("button").disabled = true;

  try {
    const response = await fetch("/api/predict", { method: "POST", body: data });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "Prediction failed.");
    renderResult(payload.result);
    await loadHistory();
    setMessage("Prediction complete.");
  } catch (error) {
    setMessage(error.message, true);
  } finally {
    form.querySelector("button").disabled = false;
  }
});

async function loadHistory() {
  const response = await fetch("/api/history");
  const payload = await response.json();
  state.history = payload.records;
  state.stats = payload.stats;
  renderStats();
  renderHistory();
}

function renderResult(record) {
  const tone = record.prediction === "Pneumonia" ? "danger" : "success";
  resultPanel.innerHTML = `
    <div class="result-summary ${tone}">
      <div>
        <p class="eyebrow">Prediction</p>
        <h2>${record.prediction}</h2>
      </div>
      <strong>${record.confidence}%</strong>
    </div>
    <div class="image-compare">
      <figure>
        <img src="${record.image_path}" alt="Uploaded chest X-ray" />
        <figcaption>Original X-ray</figcaption>
      </figure>
      <figure>
        <img src="${record.gradcam_path}" alt="Grad-CAM heatmap overlay" />
        <figcaption>Grad-CAM overlay</figcaption>
      </figure>
    </div>
    <div class="result-actions">
      <a class="secondary-button" href="/api/report/${record.id}">Download Report</a>
    </div>
  `;
}

function renderStats() {
  document.querySelector("#stat-total").textContent = state.stats.total;
  document.querySelector("#stat-normal").textContent = state.stats.normal;
  document.querySelector("#stat-pneumonia").textContent = state.stats.pneumonia;
  document.querySelector("#stat-confidence").textContent = `${state.stats.averageConfidence}%`;

  const total = Math.max(state.stats.total, 1);
  document.querySelector("#normal-bar").style.width = `${(state.stats.normal / total) * 100}%`;
  document.querySelector("#pneumonia-bar").style.width = `${(state.stats.pneumonia / total) * 100}%`;
}

function renderHistory() {
  const list = document.querySelector("#history-list");
  if (!state.history.length) {
    list.innerHTML = `<p class="muted">No predictions saved yet.</p>`;
    return;
  }
  list.innerHTML = state.history
    .map(
      (record) => `
      <article class="history-item">
        <img src="${record.gradcam_path}" alt="Prediction heatmap for ${record.name}" />
        <div>
          <h3>${record.name}</h3>
          <p>${record.prediction} · ${record.confidence}% · ${record.created_at}</p>
        </div>
        <a class="icon-button" href="/api/report/${record.id}" title="Download report">PDF</a>
        <button class="icon-button danger-text" onclick="deleteRecord(${record.id})" title="Delete record">Delete</button>
      </article>`
    )
    .join("");
}

async function deleteRecord(id) {
  await fetch(`/api/history/${id}`, { method: "DELETE" });
  await loadHistory();
}

function showView(viewId) {
  document.querySelectorAll(".view").forEach((view) => view.classList.toggle("active", view.id === viewId));
  document.querySelectorAll(".nav-button").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === viewId);
  });
  if (viewId !== "predict") loadHistory();
}

function setMessage(text, isError = false) {
  formMessage.textContent = text;
  formMessage.classList.toggle("error", isError);
}

loadHistory();

