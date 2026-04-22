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

  const elements = document.querySelectorAll(
    ".section-header p, .section-header h2, .detail-desc, .hero-sub, .hero-badge"
  );

  const textsToTranslate = [];
  const elList = [];

  for (const el of elements) {
    const original = el.getAttribute("data-original") || el.textContent.trim();
    if (!el.getAttribute("data-original")) el.setAttribute("data-original", original);
    elList.push(el);
    textsToTranslate.push(original);
  }

  if (textsToTranslate.length === 0) return;

  try {
    const res = await fetch("/api/translate/batch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texts: textsToTranslate, target_language: lang })
    });
    
    if (!res.ok) throw new Error("Translation request failed");
    
    const data = await res.json();

    if (data.translated_texts && data.translated_texts.length === elList.length) {
      for (let i = 0; i < elList.length; i++) {
        elList[i].textContent = data.translated_texts[i];
      }
      window.showToast("Page translated.");
    } else {
      window.showToast("Translation response mismatched.");
    }
  } catch (e) {
    console.error("Batch translation error:", e);
    window.showToast("Failed to translate page.");
  }
}

window.toggleLangPicker = toggleLangPicker;
window.selectLanguage = selectLanguage;
