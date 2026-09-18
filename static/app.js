const form = document.getElementById("research-form");
const questionInput = document.getElementById("question");
const charCount = document.getElementById("char-count");
const submitBtn = document.getElementById("submit-btn");
const apiKeyInput = document.getElementById("api-key-input");
const apiKeyToggle = document.getElementById("api-key-toggle");
const progressSection = document.getElementById("progress-section");
const progressLog = document.getElementById("progress-log");
const resultSection = document.getElementById("result-section");
const reportOutput = document.getElementById("report-output");
const sourcesPanel = document.getElementById("sources-panel");
const copyBtn = document.getElementById("copy-btn");
const statsBadge = document.getElementById("stats-badge");

const STEP_ORDER = ["search", "read", "synthesize", "done"];
const API_KEY_STORAGE_KEY = "gemini_api_key";

try {
  const savedKey = localStorage.getItem(API_KEY_STORAGE_KEY);
  if (savedKey) apiKeyInput.value = savedKey;
} catch {
  // localStorage unavailable (private mode, etc.) — key just won't persist
}

apiKeyInput?.addEventListener("input", () => {
  try {
    localStorage.setItem(API_KEY_STORAGE_KEY, apiKeyInput.value.trim());
  } catch {
    // ignore — persistence is a convenience, not a requirement
  }
});

apiKeyToggle?.addEventListener("click", () => {
  const showing = apiKeyInput.type === "text";
  apiKeyInput.type = showing ? "password" : "text";
  apiKeyToggle.textContent = showing ? "Show" : "Hide";
});

document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    questionInput.value = chip.dataset.q;
    questionInput.dispatchEvent(new Event("input"));
    questionInput.focus();
  });
});

questionInput.addEventListener("input", () => {
  charCount.textContent = questionInput.value.length;
});

function setStep(name) {
  const idx = STEP_ORDER.indexOf(name);
  document.querySelectorAll(".pipeline-step").forEach((el) => {
    const elIdx = STEP_ORDER.indexOf(el.dataset.step);
    el.classList.toggle("active", elIdx === idx);
    el.classList.toggle("done", elIdx < idx);
  });
}

function stepForMessage(message) {
  if (message.startsWith("Searching")) return "search";
  if (message.startsWith("Found") || message.includes("Reading") || message.includes("Summarized") || message.includes("Failed to summarize")) return "read";
  if (message.startsWith("Synthesizing")) return "synthesize";
  if (message.startsWith("Done")) return "done";
  return null;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = questionInput.value.trim();
  const apiKey = apiKeyInput.value.trim();
  if (!question) return;
  if (!apiKey) {
    showToast("Add your Gemini API key above first.");
    apiKeyInput.focus();
    return;
  }

  submitBtn.disabled = true;
  submitBtn.classList.add("loading");
  progressSection.classList.remove("hidden");
  resultSection.classList.add("hidden");
  progressLog.innerHTML = "";
  reportOutput.innerHTML = "";
  sourcesPanel.innerHTML = "";
  setStep("search");

  try {
    const res = await fetch("/api/research", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, api_key: apiKey }),
    });
    const data = await res.json();
    if (data.error) throw new Error(data.error);

    listenToJob(data.job_id);
  } catch (err) {
    showToast(err.message);
    resetForm();
  }
});

function resetForm() {
  submitBtn.disabled = false;
  submitBtn.classList.remove("loading");
}

function logLine(text, isError) {
  const li = document.createElement("li");
  li.textContent = text;
  if (isError) li.classList.add("error-line");
  progressLog.appendChild(li);
  progressLog.scrollTop = progressLog.scrollHeight;
}

function listenToJob(jobId) {
  const source = new EventSource(`/api/research/${jobId}/stream`);

  source.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === "progress") {
      logLine(data.message);
      const step = stepForMessage(data.message);
      if (step) setStep(step);
    } else if (data.type === "result") {
      setStep("done");
      resultSection.classList.remove("hidden");
      reportOutput.innerHTML = renderMarkdown(data.report);
      sourcesPanel.innerHTML = renderSources(data.sources);
      document.getElementById("result-duration").textContent = `⏱ ${data.duration_seconds}s`;
      document.getElementById("result-source-count").textContent = `📄 ${data.sources.length} sources`;
      resetForm();
      refreshStats();
      resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
      source.close();
    } else if (data.type === "error") {
      logLine(data.message, true);
      showToast(data.message);
      resetForm();
      source.close();
    }
  };

  source.onerror = () => {
    resetForm();
    source.close();
  };
}

copyBtn?.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(reportOutput.innerText);
    showToast("Report copied to clipboard");
  } catch {
    showToast("Could not copy to clipboard");
  }
});

async function refreshStats() {
  try {
    const res = await fetch("/api/stats");
    const stats = await res.json();
    statsBadge.textContent = `${stats.total_reports} reports run`;
  } catch {
    // stats badge is cosmetic; ignore failures
  }
}

refreshStats();
