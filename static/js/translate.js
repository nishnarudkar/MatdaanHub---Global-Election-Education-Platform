"use strict";

function toggleLangPicker() {
  const picker = document.getElementById("langPicker");
  if (picker) picker.classList.toggle("hidden");
}

async function selectLanguage(lang) {
  const picker = document.getElementById("langPicker");
  if (picker) picker.classList.add("hidden");

  if (lang === "en") {
    window.showToast("Language reset to English.");
    window.matdaanState.translateLang = null;
    return;
  }

  window.showToast(`Translating to ${lang}...`);
  window.matdaanState.translateLang = lang;

  const textNodes = [];
  const elements = document.querySelectorAll(
    ".section-header p, .section-header h2, .detail-desc, .hero-sub, .hero-badge"
  );

  for (const el of elements) {
    const original = el.getAttribute("data-original") || el.textContent.trim();
    if (!el.getAttribute("data-original")) el.setAttribute("data-original", original);
    textNodes.push({ el, text: original });
  }

  for (const { el, text } of textNodes) {
    try {
      const res = await fetch("/api/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, target_language: lang })
      });
      const data = await res.json();

      if (data.translated_text) {
        el.textContent = data.translated_text;
      }
    } catch (e) {
      // Ignore individual translation failures and continue.
    }
  }

  window.showToast("Page translated.");
}

window.toggleLangPicker = toggleLangPicker;
window.selectLanguage = selectLanguage;
