// Minimal markdown-to-HTML renderer (headings, bold, italics, links, lists).
// Kept dependency-free on purpose.
function renderMarkdown(text) {
  const escape = (s) =>
    s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  const lines = escape(text).split("\n");
  let html = "";
  let inList = false;

  const inline = (s) =>
    s
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.+?)\*/g, "<em>$1</em>")
      .replace(/\[(\d+)\]/g, '<sup>[$1]</sup>')
      .replace(/(https?:\/\/[^\s)]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');

  for (const raw of lines) {
    const line = raw.trim();
    const heading = line.match(/^(#{1,6})\s+(.*)/);
    const listItem = line.match(/^[-*]\s+(.*)/);

    if (heading) {
      if (inList) { html += "</ul>"; inList = false; }
      const level = heading[1].length;
      html += `<h${level}>${inline(heading[2])}</h${level}>`;
    } else if (listItem) {
      if (!inList) { html += "<ul>"; inList = true; }
      html += `<li>${inline(listItem[1])}</li>`;
    } else if (line === "") {
      if (inList) { html += "</ul>"; inList = false; }
    } else {
      if (inList) { html += "</ul>"; inList = false; }
      html += `<p>${inline(line)}</p>`;
    }
  }
  if (inList) html += "</ul>";
  return html;
}

function renderSources(sources) {
  if (!sources || sources.length === 0) return "";
  const escape = (s) => {
    const div = document.createElement("div");
    div.textContent = s;
    return div.innerHTML;
  };
  const cards = sources
    .map(
      (s, i) => `
      <a class="source-card" href="${escape(s.url)}" target="_blank" rel="noopener">
        <span class="source-index">${i + 1}</span>
        <span class="source-text">
          <div class="source-title">${escape(s.title || s.url)}</div>
          <div class="source-url">${escape(s.url)}</div>
        </span>
      </a>`
    )
    .join("");
  return `<div class="section-title">Sources</div>${cards}`;
}
