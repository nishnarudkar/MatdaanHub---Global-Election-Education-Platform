"use strict";

function renderTimeline(timeline) {
  const tlEl = document.getElementById("timelineContainer");
  if (!tlEl) return;

  tlEl.innerHTML = (timeline || []).map((t, i) =>
    `<div class="tl-item" role="listitem" style="animation-delay:${i * 0.06}s">
      <div class="tl-day" aria-label="Day ${t.days}">Day ${t.days}</div>
      <div class="tl-dot" aria-hidden="true"></div>
      <div class="tl-content">
        <div class="tl-phase">${window.escapeHtml(t.phase)}</div>
        <div class="tl-desc">${window.escapeHtml(t.description)}</div>
      </div>
    </div>`
  ).join("");
}

function renderVotingSteps(steps) {
  const stepsEl = document.getElementById("stepsContainer");
  if (!stepsEl) return;

  stepsEl.innerHTML = (steps || []).map((s, i) =>
    `<div class="step-card" style="animation-delay:${i * 0.07}s">
      <div class="step-icon" aria-hidden="true">${s.icon}</div>
      <div>
        <div class="step-title">${i + 1}. ${window.escapeHtml(s.title)}</div>
        <div class="step-detail">${window.escapeHtml(s.detail)}</div>
      </div>
    </div>`
  ).join("");
}

function initDetailTabs() {
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const tab = btn.dataset.tab;
      document.querySelectorAll(".tab-btn").forEach(b => {
        b.classList.toggle("active", b.dataset.tab === tab);
        b.setAttribute("aria-selected", b.dataset.tab === tab ? "true" : "false");
      });
      document.querySelectorAll(".tab-content").forEach(tc => {
        const isActive = tc.id === `tab-${tab}`;
        tc.classList.toggle("active", isActive);
        if (isActive) tc.removeAttribute("hidden");
        else tc.setAttribute("hidden", "");
      });
    });
  });
}

window.renderTimeline = renderTimeline;
window.renderVotingSteps = renderVotingSteps;
window.initDetailTabs = initDetailTabs;
