"use strict";

function initChatInput() {
  const input = document.getElementById("chatInput");
  if (!input) return;

  input.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendChat();
    }
  });
}

async function sendChat() {
  const input = document.getElementById("chatInput");
  const msg = (input?.value || "").trim();
  if (!msg) return;

  input.value = "";
  appendChatMsg("user", msg);

  const suggestions = document.getElementById("chatSuggestions");
  if (suggestions) suggestions.style.display = "none";

  const typingEl = appendTyping();
  const sendBtn = document.getElementById("chatSend");
  if (sendBtn) sendBtn.disabled = true;

  window.matdaanState.chatHistory.push({ role: "user", content: msg });

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: msg,
        history: window.matdaanState.chatHistory.slice(-8)
      })
    });

    const data = await res.json();
    typingEl.remove();
    const reply = data.response || "I could not process that. Please try again.";
    window.matdaanState.chatHistory.push({ role: "assistant", content: reply });
    appendChatMsg("assistant", reply);
  } catch (e) {
    typingEl.remove();
    appendChatMsg("assistant", "Sorry, I could not connect. Please try again.");
  } finally {
    if (sendBtn) sendBtn.disabled = false;
    if (input) input.focus();
  }
}

function sendSuggestion(btn) {
  const input = document.getElementById("chatInput");
  if (!input) return;

  input.value = btn.textContent.trim().replace(/[🇮🇳🇺🇸🇬🇧🇪🇺🇧🇷]/gu, "").trim();
  sendChat();
}

function appendChatMsg(role, text) {
  const win = document.getElementById("chatWindow");
  if (!win) return null;

  const div = document.createElement("div");
  div.className = `chat-msg ${role}`;
  div.setAttribute("role", "article");
  div.setAttribute("aria-label", `${role === "user" ? "You" : "Assistant"}: ${text}`);

  const avatar = role === "user" ? "👤" : "🗳️";
  div.innerHTML = `
    <div class="msg-avatar" aria-hidden="true">${avatar}</div>
    <div class="msg-bubble">${formatChatText(text)}</div>`;

  win.appendChild(div);
  win.scrollTop = win.scrollHeight;
  return div;
}

function appendTyping() {
  const win = document.getElementById("chatWindow");
  const div = document.createElement("div");
  div.className = "chat-msg assistant";
  div.setAttribute("aria-label", "Assistant is typing");
  div.innerHTML = `
    <div class="msg-avatar" aria-hidden="true">🗳️</div>
    <div class="msg-bubble">
      <div class="typing-indicator" aria-hidden="true">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>`;

  win.appendChild(div);
  win.scrollTop = win.scrollHeight;
  return div;
}

function formatChatText(text) {
  return window.escapeHtml(text)
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/\n\n/g, "</p><p>")
    .replace(/\n/g, "<br>")
    .replace(/^/, "<p>").replace(/$/, "</p>");
}

window.initChatInput = initChatInput;
window.sendChat = sendChat;
window.sendSuggestion = sendSuggestion;
