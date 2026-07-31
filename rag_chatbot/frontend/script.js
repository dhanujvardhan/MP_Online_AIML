// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------
const API_BASE = "http://localhost:8000";

// ---------------------------------------------------------------------------
// Elements
// ---------------------------------------------------------------------------
const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const browseBtn = document.getElementById("browseBtn");
const uploadStatus = document.getElementById("uploadStatus");
const kbInfo = document.getElementById("kbInfo");
const resetBtn = document.getElementById("resetBtn");

const chatWindow = document.getElementById("chatWindow");
const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function addMessage(text, sender = "bot", sources = []) {
  const div = document.createElement("div");
  div.className = `message ${sender}`;
  div.textContent = text;

  if (sources.length > 0) {
    const src = document.createElement("span");
    src.className = "sources";
    src.textContent = "Sources: " + sources.join(", ");
    div.appendChild(src);
  }

  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return div;
}

function addTypingIndicator() {
  const div = document.createElement("div");
  div.className = "typing";
  div.id = "typingIndicator";
  div.textContent = "Bot is thinking...";
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function removeTypingIndicator() {
  const el = document.getElementById("typingIndicator");
  if (el) el.remove();
}

async function refreshStatus() {
  try {
    const res = await fetch(`${API_BASE}/status`);
    const data = await res.json();
    if (data.total_chunks === 0) {
      kbInfo.textContent = "No documents loaded yet.";
    } else {
      kbInfo.textContent = `${data.documents.length} document(s), ${data.total_chunks} chunks loaded.`;
    }
  } catch (err) {
    kbInfo.textContent = "⚠️ Backend not reachable. Is it running?";
  }
}

// ---------------------------------------------------------------------------
// Upload handling
// ---------------------------------------------------------------------------
browseBtn.addEventListener("click", () => fileInput.click());
dropZone.addEventListener("click", () => fileInput.click());

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.style.borderColor = "#7c82ff";
});
dropZone.addEventListener("dragleave", () => {
  dropZone.style.borderColor = "#4b4f80";
});
dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.style.borderColor = "#4b4f80";
  if (e.dataTransfer.files.length > 0) {
    uploadFile(e.dataTransfer.files[0]);
  }
});

fileInput.addEventListener("change", () => {
  if (fileInput.files.length > 0) {
    uploadFile(fileInput.files[0]);
  }
});

async function uploadFile(file) {
  const validExt = [".pdf", ".txt"].some((ext) => file.name.toLowerCase().endsWith(ext));
  if (!validExt) {
    uploadStatus.textContent = "❌ Only .pdf or .txt files are supported.";
    uploadStatus.style.color = "#ff8080";
    return;
  }

  uploadStatus.textContent = `⏳ Processing "${file.name}"...`;
  uploadStatus.style.color = "#f0c674";

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch(`${API_BASE}/upload`, {
      method: "POST",
      body: formData,
    });
    const data = await res.json();

    if (!res.ok) throw new Error(data.detail || "Upload failed");

    uploadStatus.textContent = `✅ ${data.message}`;
    uploadStatus.style.color = "#9de3a0";
    addMessage(`📄 Document "${file.name}" added to the knowledge base (${data.chunks_added} chunks).`, "bot");
    refreshStatus();
  } catch (err) {
    uploadStatus.textContent = `❌ ${err.message}`;
    uploadStatus.style.color = "#ff8080";
  }
}

// ---------------------------------------------------------------------------
// Reset knowledge base
// ---------------------------------------------------------------------------
resetBtn.addEventListener("click", async () => {
  if (!confirm("Clear the entire knowledge base?")) return;
  try {
    await fetch(`${API_BASE}/reset`, { method: "POST" });
    addMessage("🗑 Knowledge base cleared.", "bot");
    refreshStatus();
  } catch (err) {
    addMessage("⚠️ Could not reset knowledge base. Is the backend running?", "bot");
  }
});

// ---------------------------------------------------------------------------
// Chat handling
// ---------------------------------------------------------------------------
chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const query = userInput.value.trim();
  if (!query) return;

  addMessage(query, "user");
  userInput.value = "";
  sendBtn.disabled = true;
  addTypingIndicator();

  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, top_k: 3 }),
    });
    const data = await res.json();
    removeTypingIndicator();

    if (!res.ok) throw new Error(data.detail || "Something went wrong");

    addMessage(data.answer, "bot", data.sources || []);
  } catch (err) {
    removeTypingIndicator();
    addMessage(`⚠️ Error: ${err.message}. Is the backend running on ${API_BASE}?`, "bot");
  } finally {
    sendBtn.disabled = false;
  }
});

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------
refreshStatus();
