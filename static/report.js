async function loadReport() {
  const res = await fetch(`/api/report/${window.REPORT_ID}`);
  if (!res.ok) {
    document.getElementById("report-question").textContent = "Report not found";
    return;
  }
  const data = await res.json();

  document.getElementById("report-question").textContent = data.question;
  document.getElementById("report-meta").innerHTML = `
    <span>${new Date(data.created_at).toLocaleString()}</span>
    <span>⏱ ${data.duration_seconds}s</span>
    <span>📄 ${data.sources.length} sources</span>`;
  document.getElementById("report-output").innerHTML = renderMarkdown(data.report);
  document.getElementById("sources-panel").innerHTML = renderSources(data.sources);
}

document.getElementById("copy-btn")?.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(document.getElementById("report-output").innerText);
    showToast("Report copied to clipboard");
  } catch {
    showToast("Could not copy to clipboard");
  }
});

loadReport();
