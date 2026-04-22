"use strict";

window.matdaanState = {
  currentView: "explore",
  currentCountry: null,
  chatHistory: [],
  quizState: { country: null, questions: [], current: 0, score: 0, answered: false },
  translateLang: null,
  allCountries: {}
};

document.addEventListener("DOMContentLoaded", () => {
  initNav();
  initCountryCards();
  if (window.initChatInput) window.initChatInput();
  bindQuizCountryButtons();
  loadAllCountries();
  setView("explore");
});

function initNav() {
  document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.addEventListener("click", () => setView(btn.dataset.view));
  });

  const translateToggle = document.getElementById("translateToggle");
  if (translateToggle) {
    translateToggle.addEventListener("click", () => {
      if (window.toggleLangPicker) window.toggleLangPicker();
    });
  }

  document.querySelectorAll(".lang-picker button").forEach(btn => {
    btn.addEventListener("click", () => {
      if (window.selectLanguage) window.selectLanguage(btn.dataset.lang);
    });
  });

  document.addEventListener("click", e => {
    if (!e.target.closest(".header-actions")) {
      document.getElementById("langPicker")?.classList.add("hidden");
    }
  });
}

function setView(view) {
  window.matdaanState.currentView = view;

  document.querySelectorAll(".view").forEach(v => {
    v.classList.toggle("active", v.id === `view-${view}`);
    v.classList.toggle("hidden", v.id !== `view-${view}`);
  });

  document.querySelectorAll(".nav-btn").forEach(btn => {
    const isActive = btn.dataset.view === view;
    btn.classList.toggle("active", isActive);
    btn.setAttribute("aria-current", isActive ? "page" : "false");
  });

  if (view === "compare") renderCompare();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function initCountryCards() {
  document.querySelectorAll(".country-card").forEach(card => {
    card.addEventListener("click", () => openCountry(card.dataset.country));
    card.addEventListener("keydown", e => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        openCountry(card.dataset.country);
      }
    });
  });
}

async function openCountry(countryId) {
  try {
    const res = await fetch(`/api/elections/${countryId}`);
    if (!res.ok) throw new Error("Country not found");

    const data = await res.json();
    window.matdaanState.currentCountry = countryId;
    renderCountryDetail(data);

    document.querySelector(".country-grid")?.classList.add("hidden");
    document.getElementById("countryDetail")?.classList.remove("hidden");
    document.getElementById("countryDetail")?.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) {
    showToast("Could not load country data.");
  }
}

function renderCountryDetail(data) {
  document.getElementById("detailFlag").textContent = data.flag;
  document.getElementById("detailName").textContent = data.name;
  document.getElementById("detailSystem").textContent = data.system;
  document.getElementById("detailBody").textContent = data.body;
  document.getElementById("detailFreq").textContent = data.frequency;
  document.getElementById("detailDesc").textContent = data.description;

  const factsEl = document.getElementById("detailFacts");
  factsEl.innerHTML = (data.facts || []).map(f =>
    `<span class="fact-chip" role="listitem">💡 ${escapeHtml(f)}</span>`
  ).join("");

  if (window.renderTimeline) window.renderTimeline(data.timeline || []);
  if (window.renderVotingSteps) window.renderVotingSteps(data.steps || []);
  if (window.initDetailTabs) window.initDetailTabs();
}

function closeCountry() {
  window.matdaanState.currentCountry = null;
  document.getElementById("countryDetail")?.classList.add("hidden");
  document.querySelector(".country-grid")?.classList.remove("hidden");
}

async function loadAllCountries() {
  try {
    const res = await fetch("/api/elections");
    window.matdaanState.allCountries = await res.json();
  } catch (e) {
    window.matdaanState.allCountries = {};
  }
}

// Compulsory voting and cycle metadata — kept separate since it's not in the API response
const COMPARE_META = {
  india:        { compulsory: false, cycle: 5 },
  usa:          { compulsory: false, cycle: 4 },
  uk:           { compulsory: false, cycle: 5 },
  eu:           { compulsory: false, cycle: 5 },
  brazil:       { compulsory: true,  cycle: 4 },
  south_africa: { compulsory: false, cycle: 5 },
  australia:    { compulsory: true,  cycle: 3 },
  japan:        { compulsory: false, cycle: 4 },
  mexico:       { compulsory: false, cycle: 6 },
  canada:       { compulsory: false, cycle: 4 },
};

function renderCompare() {
  const tbody = document.getElementById("compareBody");
  if (!tbody) return;

  // Use live data from allCountries; fall back to empty if not yet loaded
  const countries = window.matdaanState.allCountries;
  const ids = Object.keys(countries);

  if (ids.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center">Loading…</td></tr>`;
    // Retry once data arrives
    setTimeout(renderCompare, 500);
    return;
  }

  tbody.innerHTML = ids.map(id => {
    const c = countries[id];
    const meta = COMPARE_META[id] || { compulsory: false, cycle: "?" };
    const voters = c.voters || "—";
    return `<tr>
      <td><span class="flag-cell" aria-hidden="true">${c.flag}</span> ${escapeHtml(c.name)}</td>
      <td>${escapeHtml(c.system)}</td>
      <td>${escapeHtml(c.frequency || "—")}</td>
      <td>${escapeHtml(voters)}</td>
      <td style="font-size:0.82rem">${escapeHtml(c.body || "—")}</td>
      <td><span class="badge ${meta.compulsory ? "badge-yes" : "badge-no"}">${meta.compulsory ? "Yes" : "No"}</span></td>
    </tr>`;
  }).join("");

  // Bar charts — voters
  const voterNums = ids.map(id => {
    const raw = (countries[id].voters || "0").replace(/[^0-9.]/g, "");
    return parseFloat(raw) || 0;
  });
  const maxV = Math.max(...voterNums, 1);
  document.getElementById("voterChart").innerHTML = ids.map((id, i) => {
    const c = countries[id];
    const pct = Math.round((voterNums[i] / maxV) * 100);
    return `<div class="bar-row">
      <span class="bar-label" aria-hidden="true">${c.flag}</span>
      <div class="bar-track"><div class="bar-fill" style="width:0%" data-width="${pct}%" role="img" aria-label="${escapeHtml(c.name)}: ${escapeHtml(c.voters || '—')}"></div></div>
      <span class="bar-val">${escapeHtml(c.voters || '—')}</span>
    </div>`;
  }).join("");

  // Bar charts — cycle
  const cycles = ids.map(id => (COMPARE_META[id] || {}).cycle || 0);
  const maxC = Math.max(...cycles, 1);
  document.getElementById("cycleChart").innerHTML = ids.map((id, i) => {
    const c = countries[id];
    const pct = Math.round((cycles[i] / maxC) * 100);
    return `<div class="bar-row">
      <span class="bar-label" aria-hidden="true">${c.flag}</span>
      <div class="bar-track"><div class="bar-fill" style="width:0%" data-width="${pct}%" role="img" aria-label="${escapeHtml(c.name)}: every ${cycles[i]} years"></div></div>
      <span class="bar-val">${cycles[i]} yrs</span>
    </div>`;
  }).join("");

  requestAnimationFrame(() => {
    setTimeout(() => {
      document.querySelectorAll(".bar-fill").forEach(bar => {
        bar.style.width = bar.dataset.width;
      });
    }, 100);
  });
}

function bindQuizCountryButtons() {
  document.querySelectorAll(".quiz-country-btn").forEach(btn => {
    btn.addEventListener("click", () => startQuiz(btn.dataset.country));
  });
}

async function startQuiz(countryId) {
  document.querySelectorAll(".quiz-country-btn").forEach(b => {
    b.classList.toggle("active", b.dataset.country === countryId);
  });

  try {
    const res = await fetch(`/api/elections/${countryId}`);
    if (!res.ok) throw new Error("Quiz source data unavailable");

    const country = await res.json();
    const questions = buildQuizQuestions(country);

    window.matdaanState.quizState = {
      country: countryId,
      questions,
      current: 0,
      score: 0,
      answered: false
    };

    document.getElementById("quizContainer")?.classList.remove("hidden");
    renderQuizQuestion();
  } catch (e) {
    showToast("Could not load quiz.");
  }
}

function buildQuizQuestions(countryData) {
  const defaults = [
    {
      q: `How often are national elections held in ${countryData.name}?`,
      options: ["Every year", countryData.frequency, "Every 10 years", "No fixed schedule"],
      answer: 1
    },
    {
      q: `Which body primarily manages elections in ${countryData.name}?`,
      options: [countryData.body, "United Nations", "World Bank", "Local courts only"],
      answer: 0
    },
    {
      q: `Which electoral system is used in ${countryData.name}?`,
      options: [countryData.system, "Sortition", "Direct digital voting only", "Military appointment"],
      answer: 0
    },
    {
      q: `Approximately how many voters are represented in ${countryData.name}?`,
      options: [countryData.voters, "Under 1 million", "Under 10 million", "No voter registry"],
      answer: 0
    }
  ];

  return defaults;
}

function renderQuizQuestion() {
  const { questions, current, score } = window.matdaanState.quizState;
  const qc = document.getElementById("quizContainer");
  if (!qc) return;

  if (current >= questions.length) {
    const pct = Math.round((score / questions.length) * 100);
    const msg = pct >= 75 ? "Great work! You're election-ready!" : pct >= 50 ? "Good effort! Keep learning." : "Keep learning — democracy needs you!";
    qc.innerHTML = `
      <div class="quiz-score" role="region" aria-label="Quiz results">
        <div class="inked-finger-wrap" aria-hidden="true">
          <svg class="inked-finger-svg" viewBox="0 0 80 110" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Inked finger celebrating vote">
            <g class="finger-body">
              <rect x="28" y="30" width="24" height="55" rx="12" fill="#6366f1"/>
              <rect x="28" y="30" width="24" height="20" rx="10" fill="#8b5cf6"/>
              <rect x="30" y="78" width="20" height="12" rx="6" fill="#4f46e5"/>
            </g>
            <g class="ink-dot">
              <circle cx="40" cy="90" r="7" fill="#1a1d2e"/>
              <circle cx="40" cy="90" r="4" fill="#0d1117" opacity="0.8"/>
            </g>
            <g class="sparkles">
              <circle class="sp sp1" cx="18" cy="22" r="3" fill="#6366f1"/>
              <circle class="sp sp2" cx="62" cy="18" r="2.5" fill="#8b5cf6"/>
              <circle class="sp sp3" cx="12" cy="50" r="2" fill="#6366f1"/>
              <circle class="sp sp4" cx="68" cy="48" r="2.5" fill="#8b5cf6"/>
              <circle class="sp sp5" cx="40" cy="8" r="3" fill="#6366f1"/>
            </g>
          </svg>
        </div>
        <span class="quiz-score-num" aria-label="Score ${score} out of ${questions.length}">${score}/${questions.length}</span>
        <div class="quiz-score-label">${msg} You scored ${pct}%.</div>
        <button class="quiz-restart-btn" onclick="startQuiz('${window.matdaanState.quizState.country}')" aria-label="Try again">Try Again</button>
      </div>`;
    return;
  }

  const q = questions[current];
  window.matdaanState.quizState.answered = false;

  qc.innerHTML = `
    <div class="quiz-progress" aria-label="Question ${current + 1} of ${questions.length}">Question ${current + 1} of ${questions.length} · Score: ${score}</div>
    <div class="quiz-progress-bar" role="progressbar" aria-valuenow="${current}" aria-valuemin="0" aria-valuemax="${questions.length}">
      <div class="quiz-progress-fill" style="width:${(current / questions.length) * 100}%"></div>
    </div>
    <div class="quiz-q" id="quizQuestion">${escapeHtml(q.q)}</div>
    <div class="quiz-options" role="list" aria-labelledby="quizQuestion">
      ${q.options.map((opt, i) =>
        `<button class="quiz-option" role="listitem" data-index="${i}" onclick="answerQuiz(${i})" aria-label="Option ${i + 1}: ${escapeHtml(opt)}">${escapeHtml(opt)}</button>`
      ).join("")}
    </div>
    <div id="quizFeedback" aria-live="polite"></div>`;
}

function answerQuiz(selectedIndex) {
  if (window.matdaanState.quizState.answered) return;
  window.matdaanState.quizState.answered = true;

  const { questions, current } = window.matdaanState.quizState;
  const correct = questions[current].answer;
  const isCorrect = selectedIndex === correct;

  if (isCorrect) window.matdaanState.quizState.score += 1;

  document.querySelectorAll(".quiz-option").forEach((btn, i) => {
    btn.disabled = true;
    if (i === correct) btn.classList.add("correct");
    else if (i === selectedIndex && !isCorrect) btn.classList.add("wrong");
  });

  const fb = document.getElementById("quizFeedback");
  if (!fb) return;

  fb.innerHTML = `<div class="quiz-feedback ${isCorrect ? "correct" : "wrong"}" role="alert">
    ${isCorrect ? "Correct." : `The correct answer is: <strong>${escapeHtml(questions[current].options[correct])}</strong>`}
  </div>
  <button class="quiz-next-btn" onclick="nextQuizQuestion()" aria-label="${current + 1 < questions.length ? "Next question" : "See results"}">
    ${current + 1 < questions.length ? "Next Question" : "See Results"}
  </button>`;
}

function nextQuizQuestion() {
  window.matdaanState.quizState.current += 1;
  renderQuizQuestion();
}

function openQuizForCurrent() {
  if (window.matdaanState.currentCountry) {
    setView("quiz");
    startQuiz(window.matdaanState.currentCountry);
  }
}

function showToast(msg, duration = 3500) {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = "toast";
  toast.textContent = msg;
  toast.setAttribute("role", "status");
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = "slide-in 0.3s ease reverse both";
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#x27;");
}

window.showToast = showToast;
window.escapeHtml = escapeHtml;
window.setView = setView;
window.closeCountry = closeCountry;
window.openQuizForCurrent = openQuizForCurrent;
window.answerQuiz = answerQuiz;
window.nextQuizQuestion = nextQuizQuestion;
window.startQuiz = startQuiz;
