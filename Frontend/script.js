const API_ENDPOINT = "/ask";

const el = (id) => document.getElementById(id);

function setLoading(on) {
  const loading = el("loading");
  const btn = document.querySelector(".btn.primary");

  if (on) {
    loading.classList.remove("hidden");
    if (btn) btn.disabled = true;
  } else {
    loading.classList.add("hidden");
    if (btn) btn.disabled = false;
  }
}

function toneFromConfidence(conf) {
  if (conf >= 0.8) return "good";
  if (conf >= 0.55) return "mid";
  return "low";
}

function escapeHTML(str = "") {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function showBadges(found, confidence, topSim) {
  const badges = el("badges");
  const conf = Number(confidence || 0);
  const sim = Number(topSim || 0);

  badges.innerHTML = `
    <span class="badge ${found ? toneFromConfidence(conf) : "low"}">
      ${found ? "FOUND" : "LOW / NOT FOUND"}
    </span>
    <span class="badge ${toneFromConfidence(conf)}">
      Confidence: ${Math.round(conf * 100)}%
    </span>
    <span class="badge mid">
      Top Similarity: ${sim.toFixed(3)}
    </span>
  `;
}

function buildEvidenceTable(matches) {
  if (!Array.isArray(matches) || matches.length === 0) {
    return `
      <div class="tableTitle">Evidence</div>
      <div class="panelHint">No matches returned.</div>
    `;
  }

  const rows = matches.map((m) => `
    <tr>
      <td class="src">📄 ${escapeHTML(m.source || "Unknown")}</td>
      <td class="score">${Number(m.score || 0).toFixed(4)}</td>
      <td class="snip">${escapeHTML(m.snippet || "")}</td>
    </tr>
  `).join("");

  return `
    <div class="tableTitle">Evidence (Source + Similarity + Snippet)</div>
    <table class="eTable">
      <thead>
        <tr>
          <th>Source</th>
          <th>Similarity</th>
          <th>Snippet</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function splitLowMatch(answerText) {
  const prefix = "(Low match) Best related info found:";
  if (!answerText) {
    return { banner: "", clean: "" };
  }

  if (answerText.startsWith(prefix)) {
    const clean = answerText.replace(prefix, "").trim();
    return {
      banner: "⚠️ Low Match: This is the closest related content found (similarity is not very high).",
      clean
    };
  }

  return {
    banner: "",
    clean: answerText
  };
}

async function askQuestion() {
  const question = (el("question").value || "").trim();

  if (!question) {
    el("question").focus();
    return;
  }

  setLoading(true);

  el("result").innerHTML = `
    <div class="empty">
      <div class="emptyIcon">⏳</div>
      <div class="emptyTitle">Fetching answer</div>
      <div class="emptySub">Please wait while the system searches your documents.</div>
    </div>
  `;

  try {
    const res = await fetch(API_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status} - ${res.statusText}`);
    }

    const data = await res.json();

    const found = !!data.found;
    const confidence = Number(data.confidence || 0);
    const topSim = Number(data.top_similarity || 0);

    showBadges(found, confidence, topSim);

    const rawAnswer = data.answer || "Information not found.";
    const matches = data.matches || [];

    const split = splitLowMatch(rawAnswer);

    const metricsHTML = `
      <div class="metricsRow">
        <div class="metricCard">
          <div class="metricLabel">Confidence</div>
          <div class="metricValue">${confidence.toFixed(4)}</div>
        </div>
        <div class="metricCard">
          <div class="metricLabel">Top Similarity</div>
          <div class="metricValue">${topSim.toFixed(4)}</div>
        </div>
        <div class="metricCard">
          <div class="metricLabel">Status</div>
          <div class="metricValue">${found ? "FOUND" : "LOW MATCH"}</div>
        </div>
      </div>
    `;

    el("result").innerHTML = `
      ${split.banner ? `<div class="warnBanner">${escapeHTML(split.banner)}</div>` : ""}
      ${metricsHTML}

      <div class="answerCard">
        <div class="answerTitle">${found ? "✅ Answer" : "❌ Information not found / Low match"}</div>
        <div class="answerText">${escapeHTML(split.clean || rawAnswer)}</div>
      </div>

      ${buildEvidenceTable(matches)}
    `;
  } catch (e) {
    showBadges(false, 0, 0);
    el("result").innerHTML = `
      <div class="answerCard">
        <div class="answerTitle">⚠️ Error</div>
        <div class="answerText">
          Could not reach backend.<br><br>
          Details: ${escapeHTML(e.message)}
        </div>
      </div>
    `;
  } finally {
    setLoading(false);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  el("question").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      askQuestion();
    }
  });
});