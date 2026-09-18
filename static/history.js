async function loadStats() {
  const res = await fetch("/api/stats");
  const stats = await res.json();
  document.getElementById("stat-total").textContent = stats.total_reports;
  document.getElementById("stat-duration").textContent = stats.avg_duration_seconds
    ? `${stats.avg_duration_seconds}s`
    : "–";
}

async function loadHistory() {
  const list = document.getElementById("history-list");
  const res = await fetch("/api/history");
  const reports = await res.json();

  if (reports.length === 0) {
    list.innerHTML = `
      <div class="empty-state">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none"><path d="M12 8v4l2.5 2.5M21 12a9 9 0 1 1-3-6.7" stroke="currentColor" stroke-width="1.5"/></svg>
        <div>No reports yet — run your first research query.</div>
      </div>`;
    document.getElementById("stat-latest").textContent = "–";
    return;
  }

  document.getElementById("stat-latest").textContent = new Date(
    reports[0].created_at
  ).toLocaleDateString(undefined, { month: "short", day: "numeric" });

  list.innerHTML = reports
    .map(
      (r) => `
      <li>
        <a class="history-item" href="/report/${r.id}">
          <div class="h-question">${escapeHtml(r.question)}</div>
          <div class="h-meta">
            <span>${new Date(r.created_at).toLocaleString()}</span>
            <span>⏱ ${r.duration_seconds}s</span>
          </div>
        </a>
      </li>`
    )
    .join("");
}

function escapeHtml(s) {
  const div = document.createElement("div");
  div.textContent = s;
  return div.innerHTML;
}

loadStats();
loadHistory();
