// Global State
let currentUser = null;
let currentStats = null;
let currentChatId = null;
let currentChat = null;
let chatMessages = [];
let isSendingChat = false;

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// Helper for extracting chunk count across schema variations
function getDocChunkCount(doc) {
  if (!doc) return 0;
  if (typeof doc.chunk_count === "number") return doc.chunk_count;
  if (typeof doc.chunks_count === "number") return doc.chunks_count;
  if (Array.isArray(doc.chunks)) return doc.chunks.length;
  return 0;
}

// Lucide Icon Helper function (SVG renderer matching Tailwind sizes & colors)
function getIconSvg(name, extraClass = "") {
  const icons = {
    sparkles: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3z"/></svg>`,
    brain: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/><path d="M15 13a3 3 0 1 0-6 0"/><path d="M12 5v13"/></svg>`,
    messageSquare: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`,
    fileText: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg>`,
    bot: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="12" x="3" y="6" rx="2"/><path d="M9 11h.01"/><path d="M15 11h.01"/><path d="M12 2v4"/><path d="M12 18v4"/></svg>`,
    globe: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>`,
    code2: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m18 16 4-4-4-4"/><path d="m6 8-4 4 4 4"/><path d="m14.5 4-5 16"/></svg>`,
    search: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>`,
    barChart3: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/></svg>`,
    database: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5"/><path d="M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3"/></svg>`,
    cpu: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="12" height="12" x="6" y="6" rx="2"/><path d="M9 1 9 6"/><path d="M15 1 15 6"/><path d="M9 18 9 23"/><path d="M15 18 15 23"/><path d="M1 9 6 9"/><path d="M1 15 6 15"/><path d="M18 9 23 9"/><path d="M18 15 23 15"/></svg>`,
    settings: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.38a2 2 0 0 0-.73-2.73l-.15-.1a2 2 0 0 1-1-1.72v-.51a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>`,
    plus: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>`,
    trash2: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>`,
    send: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>`,
    user: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`,
    logOut: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>`,
    checkCircle2: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/><path d="m9 12 2 2 4-4"/></svg>`,
    arrowRight: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>`,
    uploadCloud: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M12 12v9"/><path d="m16 16-4-4-4 4"/></svg>`,
    wrench: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>`,
    loader2: `<svg class="${extraClass} animate-spin" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>`,
    copy: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>`,
    check: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`,
    chevronDown: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>`,
    chevronUp: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m18 15-6-6-6 6"/></svg>`,
    zap: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>`,
    x: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>`,
    shieldCheck: `<svg class="${extraClass}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>`
  };
  return icons[name] || "";
}

// Router & App Initialization
window.addEventListener("DOMContentLoaded", () => {
  initApp();
  attachAuthFormListeners();
  window.addEventListener("hashchange", handleRoute);
});

async function initApp() {
  const token = window.getAuthToken();
  const currentHash = window.location.hash || "#dashboard";

  if (!token) {
    currentUser = null;
    if (!currentHash.includes("login") && !currentHash.includes("register")) {
      window.location.hash = "#login";
      return;
    }
  } else {
    try {
      currentUser = await window.api.getMe();
      if (currentHash.includes("login") || currentHash.includes("register")) {
        window.location.hash = "#dashboard";
        return;
      }
    } catch (err) {
      window.removeAuthToken();
      currentUser = null;
      if (!currentHash.includes("login") && !currentHash.includes("register")) {
        window.location.hash = "#login";
        return;
      }
    }
  }

  loadStats();
  handleRoute();
}

// Attach Form Event Listeners for Login & Register
function attachAuthFormListeners() {
  // Login Form
  document.getElementById("form-login")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const emailInput = document.getElementById("login-email");
    const passwordInput = document.getElementById("login-password");
    const errorEl = document.getElementById("login-error");

    if (!emailInput || !passwordInput) return;
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();

    if (errorEl) errorEl.innerHTML = `<div class="p-3 rounded-xl bg-primary-500/10 border border-primary-500/30 text-primary-300 text-xs">Signing in...</div>`;

    try {
      const resp = await window.api.login({ email, password });
      if (resp.access_token) {
        window.setAuthToken(resp.access_token);
        currentUser = resp.user || await window.api.getMe();
        if (errorEl) errorEl.innerHTML = `<div class="p-3 rounded-xl bg-accent-emerald/10 border border-accent-emerald/30 text-accent-emerald text-xs font-semibold">Logged in successfully! Redirecting...</div>`;
        setTimeout(() => {
          window.location.hash = "#dashboard";
          initApp();
        }, 500);
      }
    } catch (err) {
      if (errorEl) {
        errorEl.innerHTML = `<div class="p-3 rounded-xl bg-accent-rose/10 border border-accent-rose/30 text-accent-rose text-xs font-semibold">${err.message || 'Invalid email or password'}</div>`;
      }
    }
  });

  // Register Form
  document.getElementById("form-register")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const emailInput = document.getElementById("reg-email");
    const usernameInput = document.getElementById("reg-username");
    const passwordInput = document.getElementById("reg-password");
    const statusEl = document.getElementById("register-status");

    if (!emailInput || !passwordInput) return;
    const email = emailInput.value.trim();
    const username = usernameInput ? usernameInput.value.trim() : "";
    const password = passwordInput.value.trim();

    if (statusEl) statusEl.innerHTML = `<div class="p-3 rounded-xl bg-primary-500/10 border border-primary-500/30 text-primary-300 text-xs">Creating account...</div>`;

    try {
      await window.api.register({ email, password, full_name: username });
      if (statusEl) {
        statusEl.innerHTML = `<div class="p-3 rounded-xl bg-accent-emerald/10 border border-accent-emerald/30 text-accent-emerald text-xs font-semibold">Account created! Signing in...</div>`;
      }
      const loginResp = await window.api.login({ email, password });
      if (loginResp.access_token) {
        window.setAuthToken(loginResp.access_token);
        currentUser = loginResp.user || await window.api.getMe();
        setTimeout(() => {
          window.location.hash = "#dashboard";
          initApp();
        }, 500);
      }
    } catch (err) {
      if (statusEl) {
        statusEl.innerHTML = `<div class="p-3 rounded-xl bg-accent-rose/10 border border-accent-rose/30 text-accent-rose text-xs font-semibold">${err.message || 'Registration failed'}</div>`;
      }
    }
  });

  // 1-Click Guest / Demo Login Button
  document.getElementById("btn-demo-login")?.addEventListener("click", async () => {
    const errorEl = document.getElementById("login-error");
    if (errorEl) errorEl.innerHTML = `<div class="p-3 rounded-xl bg-primary-500/10 border border-primary-500/30 text-primary-300 text-xs">Logging in with demo account...</div>`;
    try {
      const resp = await window.api.login({ email: "manish@gmail.com", password: "password123" });
      if (resp.access_token) {
        window.setAuthToken(resp.access_token);
        currentUser = resp.user || await window.api.getMe();
        window.location.hash = "#dashboard";
        initApp();
      }
    } catch (err) {
      currentUser = { id: "guest-user", email: "guest@omniagent.ai", full_name: "Guest User", role: "User" };
      window.location.hash = "#dashboard";
      initApp();
    }
  });
}

async function loadStats() {
  try {
    currentStats = await window.api.getStats();
  } catch (err) {
    currentStats = { total_chats: 0, total_documents: 0, total_vector_chunks: 0, active_llm_provider: "Ollama (qwen3)", ollama_status: "online", chroma_status: "online" };
  }
  updateNavbar();
  renderSidebar();
}

// Router Controller
function handleRoute() {
  const hash = window.location.hash || "#dashboard";
  const isPublicRoute = hash.includes("login") || hash.includes("register");
  const token = window.getAuthToken();

  if (!token && !isPublicRoute) {
    window.location.hash = "#login";
    return;
  }

  const header = document.getElementById("app-header");
  const sidebar = document.getElementById("app-sidebar");

  if (isPublicRoute) {
    if (header) header.style.display = "none";
    if (sidebar) sidebar.style.display = "none";
  } else {
    if (header) header.style.display = "flex";
    if (sidebar) sidebar.style.display = "flex";
    updateNavbar();
    renderSidebar();
  }

  document.querySelectorAll(".view-panel").forEach((el) => el.classList.remove("active"));

  if (hash.startsWith("#login")) {
    document.getElementById("view-login")?.classList.add("active");
  } else if (hash.startsWith("#register")) {
    document.getElementById("view-register")?.classList.add("active");
  } else if (hash.startsWith("#chat")) {
    document.getElementById("view-chat")?.classList.add("active");
    const urlParams = new URLSearchParams(hash.split("?")[1] || "");
    const chatId = urlParams.get("id");
    const query = urlParams.get("query");
    initChatView(chatId, query);
  } else if (hash.startsWith("#documents")) {
    document.getElementById("view-documents")?.classList.add("active");
    initDocumentsView();
  } else if (hash.startsWith("#agents")) {
    document.getElementById("view-agents")?.classList.add("active");
    initAgentsView();
  } else if (hash.startsWith("#settings")) {
    document.getElementById("view-settings")?.classList.add("active");
    initSettingsView();
  } else {
    document.getElementById("view-dashboard")?.classList.add("active");
    initDashboardView();
  }
}

// Navbar Renderer
function updateNavbar() {
  const container = document.getElementById("app-header");
  if (!container) return;

  const ollamaOnline = currentStats?.ollama_status === "online";
  const userInitial = (currentUser?.full_name || currentUser?.email || "U")[0].toUpperCase();
  const userName = currentUser?.full_name || currentUser?.email?.split("@")[0] || "User";

  container.innerHTML = `
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-primary-600 via-accent-purple to-accent-cyan flex items-center justify-center shadow-lg shadow-primary-500/20">
        ${getIconSvg("sparkles", "w-5 h-5 text-white animate-pulse")}
      </div>
      <div>
        <div class="flex items-center gap-2">
          <h1 class="font-bold text-lg text-white tracking-wide">
            Omni<span class="gradient-text">Agent AI</span>
          </h1>
          <span class="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-primary-500/10 text-primary-400 border border-primary-500/20">
            v1.0 Local Multi-Agent
          </span>
        </div>
        <p class="text-xs text-gray-400">Zero-Cost LangGraph Agent Platform</p>
      </div>
    </div>

    <div class="hidden md:flex items-center gap-3 text-xs">
      <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-cardLight/50 border border-border">
        ${getIconSvg("cpu", "w-4 h-4 text-accent-cyan")}
        <span class="text-gray-300 font-medium">Ollama LLM:</span>
        <div class="flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full ${ollamaOnline ? 'bg-accent-emerald animate-pulse' : 'bg-accent-amber'}"></span>
          <span class="text-gray-200 capitalize font-mono text-[11px]">${currentStats?.ollama_status || 'online'}</span>
        </div>
      </div>

      <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-cardLight/50 border border-border">
        ${getIconSvg("database", "w-4 h-4 text-accent-purple")}
        <span class="text-gray-300 font-medium">ChromaDB RAG:</span>
        <div class="flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-accent-emerald animate-pulse"></span>
          <span class="text-gray-200 capitalize font-mono text-[11px]">${currentStats?.chroma_status || 'Ready'}</span>
        </div>
      </div>

      <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-cardLight/70 border border-border shadow-sm">
        ${getIconSvg("bot", "w-4 h-4 text-accent-cyan")}
        <span class="text-gray-300 font-medium">Model:</span>
        <select id="select-model" class="bg-transparent text-white font-semibold text-xs focus:outline-none cursor-pointer">
          <option value="llama3.2:latest" class="bg-card text-white">Llama 3.2 (Installed Local)</option>
          <option value="qwen2.5:latest" class="bg-card text-white">Qwen 2.5 (Local)</option>
          <option value="llama3:latest" class="bg-card text-white">Llama 3 (Local)</option>
          <option value="mistral:latest" class="bg-card text-white">Mistral 7B (Local)</option>
          <option value="gemma2:2b" class="bg-card text-white">Gemma 2B (Local)</option>
          <option value="gemini-1.5-flash" class="bg-card text-white">Google Gemini (Cloud Free)</option>
        </select>
      </div>
    </div>

    <div class="flex items-center gap-3">
      <a href="#settings" class="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-cardLight border border-transparent hover:border-border transition-all" title="Settings">
        ${getIconSvg("settings", "w-5 h-5")}
      </a>

      ${currentUser ? `
        <div class="flex items-center gap-3 pl-3 border-l border-border">
          <button id="btn-profile-trigger" class="flex items-center gap-2.5 hover:bg-cardLight/80 p-1.5 rounded-xl border border-transparent hover:border-border transition-all text-left group cursor-pointer" title="View Profile Details">
            <div class="w-8 h-8 rounded-full bg-primary-600/30 border border-primary-500/40 flex items-center justify-center text-primary-300 font-bold text-xs group-hover:scale-105 transition-transform">
              ${userInitial}
            </div>
            <div class="hidden sm:block">
              <div class="text-xs font-semibold text-gray-200 group-hover:text-white">${userName}</div>
              <div class="text-[10px] text-gray-400 truncate max-w-[120px]">${currentUser.email}</div>
            </div>
          </button>
          <button id="btn-logout" class="p-2 rounded-lg text-gray-400 hover:text-accent-rose hover:bg-cardLight border border-transparent hover:border-border transition-all" title="Sign Out">
            ${getIconSvg("logOut", "w-4 h-4")}
          </button>
        </div>
      ` : `
        <a href="#login" class="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-primary-600 hover:bg-primary-500 text-white text-xs font-medium transition-all shadow-md shadow-primary-600/20">
          ${getIconSvg("user", "w-4 h-4")}
          <span>Sign In</span>
        </a>
      `}
    </div>
  `;

  document.getElementById("btn-profile-trigger")?.addEventListener("click", openProfileModal);
  document.getElementById("btn-logout")?.addEventListener("click", () => {
    window.removeAuthToken();
    currentUser = null;
    window.location.hash = "#login";
  });
}

// Sidebar Renderer (Ultra Sleek Modern Layout)
async function renderSidebar() {
  const container = document.getElementById("app-sidebar");
  if (!container) return;

  let chats = [];
  try {
    chats = (await window.api.listChats()) || [];
  } catch (err) {}

  const currentHash = window.location.hash || "#dashboard";

  const navItems = [
    { label: "Dashboard", href: "#dashboard", icon: "barChart3" },
    { label: "Multi-Agent Chat", href: "#chat", icon: "messageSquare" },
    { label: "Document Hub (RAG)", href: "#documents", icon: "fileText" },
    { label: "Agent Orchestrator", href: "#agents", icon: "bot" },
    { label: "Settings & LLMs", href: "#settings", icon: "settings" },
  ];

  container.innerHTML = `
    <div class="p-4 shrink-0">
      <button id="btn-new-chat-sidebar" class="w-full flex items-center justify-center gap-2.5 py-3 px-4 rounded-2xl bg-gradient-to-r from-primary-600 via-primary-500 to-accent-purple hover:from-primary-500 hover:to-primary-600 text-white font-semibold text-sm transition-all shadow-lg shadow-primary-600/30 active:scale-[0.98] cursor-pointer">
        ${getIconSvg("plus", "w-4.5 h-4.5")}
        <span>New Multi-Agent Chat</span>
      </button>
    </div>

    <div class="px-3 py-2 space-y-1 shrink-0">
      <div class="text-[10px] font-extrabold text-gray-400 uppercase tracking-widest px-3 mb-2">Main Menu</div>
      ${navItems.map((item) => {
        const isActive = currentHash === item.href || (item.href !== "#dashboard" && currentHash.startsWith(item.href));
        return `
          <a href="${item.href}" class="relative flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
            isActive
              ? 'bg-primary-600/20 text-primary-300 border border-primary-500/40 shadow-md shadow-primary-600/10'
              : 'text-gray-300 hover:bg-cardLight/70 hover:text-white border border-transparent'
          }">
            ${isActive ? `<span class="absolute left-0 top-2 bottom-2 w-1 bg-gradient-to-b from-accent-cyan to-primary-500 rounded-r"></span>` : ''}
            <div class="flex items-center gap-3">
              ${getIconSvg(item.icon, `w-4 h-4 ${isActive ? 'text-accent-cyan' : 'text-gray-400'}`)}
              <span>${item.label}</span>
            </div>
            ${isActive ? getIconSvg("arrowRight", "w-3.5 h-3.5 text-primary-400") : ''}
          </a>
        `;
      }).join("")}
    </div>

    <div class="flex-1 overflow-y-auto px-3 py-3 mt-3 border-t border-border/60 min-h-0">
      <div class="flex items-center justify-between px-3 mb-2.5">
        <span class="text-[10px] font-extrabold text-gray-400 uppercase tracking-widest">Recent Conversations</span>
        <span class="text-[10px] bg-cardLight/80 border border-border px-2 py-0.5 rounded-full text-gray-300 font-mono font-bold">${chats.length}</span>
      </div>

      ${chats.length === 0 ? `
        <div class="text-center py-8 px-4 rounded-2xl border border-dashed border-border/40 bg-card/20">
          ${getIconSvg("sparkles", "w-6 h-6 text-gray-600 mx-auto mb-2")}
          <p class="text-xs text-gray-400 font-medium">No conversations yet</p>
          <p class="text-[11px] text-gray-500 mt-1">Start a new chat above</p>
        </div>
      ` : `
        <div class="space-y-1.5">
          ${chats.map((c) => {
            const isSelected = currentChatId === c.id || currentHash.includes(c.id);
            return `
              <div class="group relative flex items-center justify-between px-3 py-2.5 rounded-xl text-xs transition-all border cursor-pointer ${
                isSelected
                  ? 'bg-gradient-to-r from-primary-600/30 via-primary-500/20 to-accent-purple/20 text-white font-bold border-primary-500/50 shadow-md shadow-primary-600/10 border-l-4 border-l-accent-cyan'
                  : 'text-gray-300 hover:bg-cardLight/80 hover:text-white border-transparent hover:border-border/60'
              }" onclick="window.location.hash='#chat?id=${c.id}'">
                <div class="flex items-center gap-2.5 truncate">
                  ${isSelected
                    ? `<span class="w-2 h-2 rounded-full bg-accent-cyan animate-ping shrink-0"></span>`
                    : getIconSvg("messageSquare", "w-3.5 h-3.5 text-gray-400 group-hover:text-primary-400 shrink-0")
                  }
                  <span class="truncate ${isSelected ? 'text-primary-200' : ''}">${c.title || "Untitled Conversation"}</span>
                </div>
                <button class="btn-delete-chat ${isSelected ? 'opacity-100 text-gray-300' : 'opacity-0 group-hover:opacity-100 text-gray-400'} p-1.5 hover:text-accent-rose hover:bg-cardLight rounded-lg transition-all shrink-0" data-chat-id="${c.id}" title="Delete chat">
                  ${getIconSvg("trash2", "w-3.5 h-3.5")}
                </button>
              </div>
            `;
          }).join("")}
        </div>
      `}
    </div>

    <div class="p-3.5 border-t border-border/80 bg-card/60 backdrop-blur-md text-xs text-gray-400 flex items-center justify-between shrink-0">
      <div class="flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-accent-emerald animate-pulse"></span>
        <span class="font-medium text-gray-200">OmniAgent Engine</span>
      </div>
      <span class="px-2 py-0.5 rounded-full bg-accent-emerald/10 text-accent-emerald border border-accent-emerald/30 font-mono text-[10px] font-bold">Local Ollama</span>
    </div>
  `;

  document.getElementById("btn-new-chat-sidebar")?.addEventListener("click", async () => {
    try {
      const newChat = await window.api.createChat({ title: "New Conversation" });
      window.location.hash = `#chat?id=${newChat.id}`;
    } catch (err) {
      console.error(err);
    }
  });

  document.querySelectorAll(".btn-delete-chat").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      e.stopPropagation();
      const chatId = btn.getAttribute("data-chat-id");
      if (chatId) {
        try {
          await window.api.deleteChat(chatId);
          renderSidebar();
          if (currentChatId === chatId) {
            window.location.hash = "#chat";
          }
        } catch (err) {}
      }
    });
  });
}

// User Profile Modal Controller
function openProfileModal() {
  if (!currentUser) return;
  const modal = document.getElementById("profile-modal");
  if (!modal) return;

  const displayName = currentUser.full_name || currentUser.email?.split("@")[0] || "OmniUser";
  const userInitial = displayName[0].toUpperCase();

  modal.innerHTML = `
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn">
      <div class="absolute inset-0" id="profile-backdrop"></div>

      <div class="relative w-full max-w-md bg-card border border-border/80 rounded-3xl p-6 shadow-2xl space-y-6 z-10 overflow-hidden">
        <div class="absolute -top-12 -right-12 w-32 h-32 bg-primary-500/20 rounded-full blur-2xl pointer-events-none"></div>
        <div class="absolute -bottom-12 -left-12 w-32 h-32 bg-accent-purple/20 rounded-full blur-2xl pointer-events-none"></div>

        <div class="flex items-center justify-between border-b border-border/60 pb-4">
          <div class="flex items-center gap-2">
            ${getIconSvg("sparkles", "w-5 h-5 text-primary-400")}
            <h3 class="text-base font-bold text-white tracking-wide">User Account Profile</h3>
          </div>
          <button id="close-profile-modal" class="p-1.5 rounded-xl text-gray-400 hover:text-white hover:bg-cardLight transition-all" title="Close">
            ${getIconSvg("x", "w-5 h-5")}
          </button>
        </div>

        <div class="flex items-center gap-4 bg-cardLight/40 p-4 rounded-2xl border border-border/60">
          <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-primary-600 via-primary-500 to-accent-purple flex items-center justify-center text-white text-xl font-extrabold shadow-lg shadow-primary-500/30 shrink-0">
            ${userInitial}
          </div>
          <div class="truncate">
            <h4 class="text-base font-bold text-white truncate">${displayName}</h4>
            <p class="text-xs text-gray-400 truncate">${currentUser.email}</p>
            <div class="flex items-center gap-2 mt-1.5">
              <span class="inline-flex items-center gap-1 text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-accent-emerald/10 text-accent-emerald border border-accent-emerald/30">
                ${getIconSvg("checkCircle2", "w-3 h-3")}
                Active Account
              </span>
              <span class="inline-flex items-center gap-1 text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-primary-500/10 text-primary-400 border border-primary-500/30">
                ${currentUser.role || "User"}
              </span>
            </div>
          </div>
        </div>

        <div class="space-y-3 text-xs">
          <div class="flex items-center justify-between p-3 rounded-xl bg-cardLight/30 border border-border/40">
            <div class="flex items-center gap-2 text-gray-300">
              ${getIconSvg("user", "w-4 h-4 text-primary-400")}
              <span>Full Name</span>
            </div>
            <span class="font-semibold text-white truncate max-w-[200px]">${currentUser.full_name || "Not Specified"}</span>
          </div>

          <div class="flex items-center justify-between p-3 rounded-xl bg-cardLight/30 border border-border/40">
            <div class="flex items-center gap-2 text-gray-300">
              ${getIconSvg("fileText", "w-4 h-4 text-accent-cyan")}
              <span>Email Address</span>
            </div>
            <span class="font-mono text-gray-200 truncate max-w-[200px]">${currentUser.email}</span>
          </div>

          <div class="flex items-center justify-between p-3 rounded-xl bg-cardLight/30 border border-border/40">
            <div class="flex items-center gap-2 text-gray-300">
              ${getIconSvg("database", "w-4 h-4 text-accent-amber")}
              <span>User ID</span>
            </div>
            <span class="font-mono text-[11px] text-gray-400 truncate max-w-[180px]">${currentUser.id}</span>
          </div>
        </div>

        <div class="pt-2 flex items-center justify-between gap-3">
          <button id="close-profile-modal-btn" class="flex-1 py-2.5 px-4 rounded-xl bg-cardLight hover:bg-cardLight/80 text-gray-300 hover:text-white text-xs font-semibold border border-border transition-all">Close</button>
          <button id="modal-logout-btn" class="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-accent-rose/10 hover:bg-accent-rose/20 text-accent-rose text-xs font-semibold border border-accent-rose/30 transition-all">
            ${getIconSvg("logOut", "w-4 h-4")}
            <span>Sign Out</span>
          </button>
        </div>
      </div>
    </div>
  `;

  modal.classList.remove("hidden");

  const closeModal = () => modal.classList.add("hidden");
  document.getElementById("close-profile-modal")?.addEventListener("click", closeModal);
  document.getElementById("close-profile-modal-btn")?.addEventListener("click", closeModal);
  document.getElementById("profile-backdrop")?.addEventListener("click", closeModal);
  document.getElementById("modal-logout-btn")?.addEventListener("click", () => {
    window.removeAuthToken();
    currentUser = null;
    closeModal();
    window.location.hash = "#login";
  });
}

// VIEW 1: Dashboard Controller
async function initDashboardView() {
  const container = document.getElementById("view-dashboard");
  if (!container) return;

  const agentCards = [
    { name: "Supervisor Agent", role: "Query Planner & Synthesizer", icon: "brain", color: "from-indigo-500 to-purple-600", desc: "Routes query to specialized agents using LangGraph." },
    { name: "Web Search Agent", role: "Live Web & DuckDuckGo", icon: "globe", color: "from-cyan-500 to-blue-600", desc: "Fetches live news, documentation, and real-time updates." },
    { name: "Document RAG Agent", role: "ChromaDB Vector Retrieval", icon: "fileText", color: "from-emerald-500 to-teal-600", desc: "Performs semantic search over uploaded PDFs & docs." },
    { name: "Research Agent", role: "ArXiv & Wikipedia Research", icon: "search", color: "from-amber-500 to-orange-600", desc: "Gathers scientific papers and encyclopedic knowledge." },
    { name: "Code Agent", role: "Python REPL & Refactoring", icon: "code2", color: "from-violet-500 to-fuchsia-600", desc: "Executes Python code and generates software solutions." },
    { name: "Data Analysis Agent", role: "Pandas & Data Insights", icon: "barChart3", color: "from-rose-500 to-pink-600", desc: "Processes tabular data, CSVs, and computes statistics." },
  ];

  container.innerHTML = `
    <div class="max-w-6xl mx-auto space-y-8 pb-10">
      <!-- Hero Section -->
      <div class="relative overflow-hidden rounded-3xl bg-gradient-to-r from-primary-900/60 via-card to-accent-purple/20 border border-primary-500/20 p-8 shadow-2xl">
        <div class="relative z-10 max-w-2xl">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-500/10 text-primary-300 border border-primary-500/20 text-xs font-mono mb-4">
            ${getIconSvg("sparkles", "w-3.5 h-3.5")}
            <span>Zero-Cost Local Multi-Agent AI</span>
          </div>
          <h1 class="text-3xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
            Autonomous <span class="gradient-text">LangGraph Multi-Agent</span> Ecosystem
          </h1>
          <p class="mt-3 text-gray-300 text-sm leading-relaxed">
            Run local open-source LLMs (Ollama Qwen3 / Llama3) connected with ChromaDB vector memory, live web search, Python code execution, and document parsing — completely private and free.
          </p>

          <div class="mt-6 flex flex-wrap items-center gap-4">
            <a href="#chat" class="flex items-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-primary-600 to-accent-purple hover:from-primary-500 hover:to-primary-600 text-white font-semibold text-sm transition-all shadow-lg shadow-primary-600/30">
              ${getIconSvg("messageSquare", "w-4 h-4")}
              <span>Launch Multi-Agent Chat</span>
              ${getIconSvg("arrowRight", "w-4 h-4")}
            </a>
            <a href="#documents" class="flex items-center gap-2 px-5 py-3 rounded-xl bg-cardLight/80 hover:bg-cardLight text-gray-200 hover:text-white font-semibold text-sm border border-border transition-all">
              ${getIconSvg("fileText", "w-4 h-4 text-accent-emerald")}
              <span>Upload Documents (RAG)</span>
            </a>
          </div>
        </div>
      </div>

      <!-- Metrics Row -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div class="glass-panel p-5 rounded-2xl border border-border/80 flex items-center justify-between">
          <div>
            <p class="text-xs text-gray-400 font-medium">Active Conversations</p>
            <h3 class="text-2xl font-bold text-white mt-1">${currentStats?.total_chats || 0}</h3>
          </div>
          <div class="w-12 h-12 rounded-xl bg-primary-600/20 border border-primary-500/30 flex items-center justify-center text-primary-400">
            ${getIconSvg("messageSquare", "w-6 h-6")}
          </div>
        </div>

        <div class="glass-panel p-5 rounded-2xl border border-border/80 flex items-center justify-between">
          <div>
            <p class="text-xs text-gray-400 font-medium">Indexed Knowledge Docs</p>
            <h3 class="text-2xl font-bold text-white mt-1">${currentStats?.total_documents || 0}</h3>
          </div>
          <div class="w-12 h-12 rounded-xl bg-accent-emerald/20 border border-accent-emerald/30 flex items-center justify-center text-accent-emerald">
            ${getIconSvg("fileText", "w-6 h-6")}
          </div>
        </div>

        <div class="glass-panel p-5 rounded-2xl border border-border/80 flex items-center justify-between">
          <div>
            <p class="text-xs text-gray-400 font-medium">ChromaDB Chunks</p>
            <h3 class="text-2xl font-bold text-white mt-1">${currentStats?.total_vector_chunks || 0}</h3>
          </div>
          <div class="w-12 h-12 rounded-xl bg-accent-purple/20 border border-accent-purple/30 flex items-center justify-center text-accent-purple">
            ${getIconSvg("database", "w-6 h-6")}
          </div>
        </div>

        <div class="glass-panel p-5 rounded-2xl border border-border/80 flex items-center justify-between">
          <div>
            <p class="text-xs text-gray-400 font-medium">LLM Engine</p>
            <h3 class="text-sm font-bold text-accent-cyan mt-1 truncate max-w-[140px]">${currentStats?.active_llm_provider || "Ollama (qwen3)"}</h3>
          </div>
          <div class="w-12 h-12 rounded-xl bg-accent-cyan/20 border border-accent-cyan/30 flex items-center justify-center text-accent-cyan">
            ${getIconSvg("cpu", "w-6 h-6")}
          </div>
        </div>
      </div>

      <!-- Agents Grid -->
      <div>
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-lg font-bold text-white">Specialized AI Agents Network</h2>
            <p class="text-xs text-gray-400">Autonomous agents collaborating under Supervisor guidance</p>
          </div>
          <a href="#agents" class="text-xs text-primary-400 hover:text-primary-300 font-medium flex items-center gap-1">
            <span>View All Agents</span>
            ${getIconSvg("arrowRight", "w-3.5 h-3.5")}
          </a>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          ${agentCards.map((agent) => `
            <div class="glass-panel glass-panel-hover p-5 rounded-2xl border border-border/80 flex flex-col justify-between">
              <div>
                <div class="flex items-center justify-between mb-3">
                  <div class="w-10 h-10 rounded-xl bg-gradient-to-tr ${agent.color} flex items-center justify-center text-white shadow-md">
                    ${getIconSvg(agent.icon, "w-5 h-5")}
                  </div>
                  <span class="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-cardLight text-gray-300 border border-border">Active Node</span>
                </div>
                <h3 class="font-semibold text-white text-base">${agent.name}</h3>
                <p class="text-xs text-primary-400 font-medium mb-2">${agent.role}</p>
                <p class="text-xs text-gray-400 leading-relaxed">${agent.desc}</p>
              </div>

              <div class="mt-4 pt-3 border-t border-border/50 flex items-center justify-between text-xs text-gray-400">
                <span class="flex items-center gap-1 text-[11px] text-accent-emerald">
                  ${getIconSvg("shieldCheck", "w-3.5 h-3.5")}
                  LangGraph Compatible
                </span>
                <a href="#chat?query=Ask ${encodeURIComponent(agent.name)}" class="text-primary-400 hover:underline">Test Agent</a>
              </div>
            </div>
          `).join("")}
        </div>
      </div>
    </div>
  `;
}

// VIEW 2: Chat Controller
async function initChatView(chatId, queryFromUrl) {
  const container = document.getElementById("view-chat");
  if (!container) return;

  currentChatId = chatId;

  if (chatId) {
    try {
      currentChat = await window.api.getChat(chatId);
      chatMessages = currentChat.messages || [];
    } catch (err) {
      chatMessages = [];
    }
  } else {
    currentChat = null;
    chatMessages = [];
  }

  renderChatInterface();

  // Populate Document Selector Dropdown
  try {
    const docs = await window.api.listDocuments();
    const selectEl = document.getElementById("chat-document-select");
    if (selectEl && docs && docs.length > 0) {
      selectEl.innerHTML = `
        <option value="" class="bg-card text-white">Search All Uploaded Documents (${docs.length} Files RAG)</option>
        ${docs.map(d => `<option value="${d.id}" class="bg-card text-white">📄 ${d.filename} (${d.chunk_count || 0} chunks)</option>`).join("")}
      `;
    }
  } catch (err) {
    console.error("Failed to populate document selector:", err);
  }

  if (queryFromUrl && !isSendingChat) {
    const inputEl = document.getElementById("chat-input");
    if (inputEl) {
      inputEl.value = queryFromUrl;
      handleSendMessage();
    }
  }
}

function renderChatInterface() {
  const container = document.getElementById("view-chat");
  if (!container) return;

  const samplePrompts = [
    { title: "Research Paper Search", prompt: "Find papers on transformer architecture advancements on ArXiv", icon: "search" },
    { title: "Document RAG", prompt: "Summarize and query information from uploaded documents in ChromaDB", icon: "fileText" },
    { title: "Python Code Execution", prompt: "Write a Python script to filter and compute mean sales from CSV", icon: "code2" },
    { title: "Live Web Search", prompt: "What are the latest updates on open-source AI models?", icon: "globe" },
  ];

  container.innerHTML = `
    <div class="flex flex-col h-[calc(100vh-7.5rem)] max-w-6xl mx-auto">
      <!-- Agent Visualizer Container -->
      <div id="visualizer-container"></div>

      <!-- Messages Scroll Area -->
      <div id="messages-scroll-area" class="flex-1 overflow-y-auto pr-2 space-y-4 my-2 pb-6">
        ${chatMessages.length === 0 ? `
          <div class="flex flex-col items-center justify-center h-full text-center py-8 px-4">
            <div class="w-16 h-16 rounded-2xl bg-gradient-to-tr from-primary-600 via-accent-purple to-accent-cyan flex items-center justify-center text-white mb-4 shadow-xl shadow-primary-600/30">
              ${getIconSvg("sparkles", "w-8 h-8 animate-pulse")}
            </div>
            <h3 class="text-xl font-bold text-white mb-2">How can OmniAgent assist you today?</h3>
            <p class="text-sm text-gray-400 max-w-md mb-8">
              Type any query below. Select a target PDF file or let Supervisor auto-route to RAG, Web, Code, or Research agents.
            </p>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-2xl">
              ${samplePrompts.map((item) => `
                <button class="sample-prompt-btn p-3.5 rounded-xl bg-card/60 hover:bg-cardLight border border-border/80 hover:border-primary-500/50 text-left transition-all group" data-prompt="${item.prompt}">
                  <div class="flex items-center gap-2 text-xs font-semibold text-primary-300 mb-1 group-hover:text-primary-200">
                    ${getIconSvg(item.icon, "w-4 h-4 text-accent-cyan")}
                    <span>${item.title}</span>
                  </div>
                  <p class="text-xs text-gray-400 line-clamp-2">${item.prompt}</p>
                </button>
              `).join("")}
            </div>
          </div>
        ` : chatMessages.map((msg) => renderMessageBubbleHtml(msg)).join("")}
      </div>

      <!-- Document Selector & Input Form -->
      <div class="shrink-0 mt-2 mb-1">
        <div class="flex items-center gap-2 mb-2 px-1">
          <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-card/90 backdrop-blur-md border border-border/80 text-xs text-gray-300 shadow-md">
            ${getIconSvg("fileText", "w-4 h-4 text-accent-emerald")}
            <span class="font-semibold text-gray-300">Target PDF / Document:</span>
            <select id="chat-document-select" class="bg-transparent text-accent-emerald font-bold text-xs focus:outline-none cursor-pointer max-w-xs truncate">
              <option value="" class="bg-card text-white">Search All Uploaded Documents (Global RAG)</option>
            </select>
          </div>
        </div>

        <form id="chat-form" class="relative">
          <div class="relative flex items-center bg-card/80 backdrop-blur-md rounded-2xl border border-border/80 focus-within:border-primary-500 shadow-2xl p-2">
            <input type="text" id="chat-input" placeholder="Ask anything about your selected PDF... (e.g., 'Summarize key points from page 1')" class="flex-1 bg-transparent px-4 py-3 text-sm text-gray-100 placeholder-gray-500 focus:outline-none" />
            <div class="flex items-center gap-2 px-2">
              <button type="submit" id="btn-chat-send" class="p-3 rounded-xl bg-gradient-to-r from-primary-600 to-accent-purple hover:from-primary-500 hover:to-primary-600 text-white transition-all shadow-md shadow-primary-600/30">
                ${getIconSvg("send", "w-4 h-4")}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  `;

  renderVisualizer(["supervisor_plan", "supervisor_synthesize"], "supervisor_plan", false, {}, "", []);

  document.getElementById("chat-form")?.addEventListener("submit", (e) => {
    e.preventDefault();
    handleSendMessage();
  });

  document.querySelectorAll(".sample-prompt-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const prompt = btn.getAttribute("data-prompt");
      const input = document.getElementById("chat-input");
      if (input && prompt) {
        input.value = prompt;
        handleSendMessage();
      }
    });
  });

  attachBubbleListeners();
  scrollToBottom();
}

// Pure React-identical Message Renderer (Exact React Colors, Alignment & Dimensions)
function renderMessageBubbleHtml(msg) {
  if (msg.isLoading) {
    return `
      <div class="flex gap-4 my-4 w-full mr-auto max-w-full">
        <div class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 shadow-md bg-gradient-to-tr from-primary-600 via-accent-purple to-accent-cyan text-white animate-pulse">
          ${getIconSvg("brain", "w-5 h-5 text-white")}
        </div>

        <div class="flex-1 flex flex-col items-start w-full">
          <div class="flex items-center gap-2 mb-1.5 px-1">
            <span class="text-xs font-semibold text-primary-300">OmniAgent AI (Supervisor)</span>
            <span class="text-[10px] text-accent-cyan font-mono font-semibold flex items-center gap-1">
              ${getIconSvg("zap", "w-3 h-3 text-accent-cyan animate-bounce")}
              • Executing Multi-Agent Pipeline...
            </span>
          </div>

          <div class="p-4 rounded-2xl rounded-tl-none border text-xs bg-card/80 text-gray-200 border-primary-500/50 shadow-xl glass-panel flex items-center gap-3.5 max-w-xl">
            <div class="w-8 h-8 rounded-xl bg-primary-600/30 border border-primary-500/40 flex items-center justify-center shrink-0">
              ${getIconSvg("loader2", "w-4 h-4 text-accent-cyan animate-spin")}
            </div>
            <div>
              <div class="text-xs font-semibold text-white">Analyzing query semantics & delegating to sub-agents...</div>
              <div class="text-[11px] text-gray-400 mt-0.5 font-mono">Running LangGraph supervisor node routing...</div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  const isUser = msg.sender_role === "user";
  let meta = {};
  if (msg.metadata_json) {
    try { meta = JSON.parse(msg.metadata_json); } catch (e) {}
  }

  const formattedContent = isUser ? msg.content.replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\n/g, "<br/>") : formatMarkdownToHtml(msg.content);
  const timeStr = msg.created_at ? new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';
  const encodedContent = encodeURIComponent(msg.content || "");

  return `
    <div class="flex gap-4 my-4 ${isUser ? 'ml-auto flex-row-reverse max-w-2xl' : 'mr-auto max-w-full'}">
      <div class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 shadow-md ${
        isUser
          ? 'bg-gradient-to-tr from-accent-cyan to-primary-600 text-white'
          : 'bg-gradient-to-tr from-primary-600 via-accent-purple to-accent-emerald text-white'
      }">
        ${getIconSvg(isUser ? "user" : "sparkles", "w-5 h-5")}
      </div>

      <div class="flex flex-col ${isUser ? 'items-end' : 'items-start flex-1'}">
        <div class="flex items-center gap-2 mb-1.5 px-1">
          <span class="text-xs font-semibold text-gray-300">${isUser ? 'You' : 'OmniAgent AI (Supervisor)'}</span>
          ${timeStr ? `<span class="text-[10px] text-gray-400 font-mono">${timeStr}</span>` : ''}
        </div>

        <div class="${
          isUser
            ? 'px-5 py-3 rounded-2xl rounded-tr-none bg-primary-600/90 text-white border border-primary-500/50 shadow-lg shadow-primary-600/20 text-sm leading-relaxed font-medium inline-block break-words max-w-xl'
            : 'p-5 rounded-2xl rounded-tl-none bg-card/80 text-gray-100 border border-border/80 shadow-xl glass-panel text-sm leading-relaxed w-full'
        }">
          ${isUser ? formattedContent : `<div class="space-y-3 w-full">${formattedContent}</div>`}

          ${!isUser ? `
            <div class="mt-4 pt-3 border-t border-border/60 flex flex-col gap-2">
              <div class="flex items-center justify-between">
                <button class="btn-copy-msg flex items-center gap-1.5 text-xs text-gray-400 hover:text-gray-200 transition-colors" data-encoded-text="${encodedContent}">
                  ${getIconSvg("copy", "w-3.5 h-3.5")}
                  <span>Copy response</span>
                </button>

                ${Object.keys(meta).length > 0 ? `
                  <button class="btn-toggle-insights flex items-center gap-1 text-xs text-primary-400 hover:text-primary-300 font-medium transition-colors" data-target="insights-${msg.id}">
                    ${getIconSvg("brain", "w-3.5 h-3.5")}
                    <span>View Sub-Agent Insights (${Object.keys(meta).length})</span>
                    ${getIconSvg("chevronDown", "w-3.5 h-3.5")}
                  </button>
                ` : ''}
              </div>

              ${Object.keys(meta).length > 0 ? `
                <div id="insights-${msg.id}" class="hidden mt-2 space-y-2 bg-background/60 p-3 rounded-xl border border-border/80 text-xs">
                  <div class="font-semibold text-primary-300 flex items-center gap-1.5 border-b border-border/40 pb-1.5">
                    ${getIconSvg("bot", "w-4 h-4 text-accent-purple")}
                    <span>Agent Execution Reasoning & Output Trail</span>
                  </div>

                  ${Object.entries(meta).map(([k, v]) => `
                    <div class="p-2.5 rounded-lg bg-card/70 border border-border/50">
                      <div class="font-mono text-[11px] font-bold text-accent-cyan uppercase mb-1 flex items-center gap-1.5">
                        <span class="w-2 h-2 rounded-full bg-accent-cyan"></span>
                        ${k.replace("_", " ")}
                      </div>
                      <div class="text-gray-300 text-xs whitespace-pre-wrap font-mono max-h-40 overflow-y-auto pr-1">
                        ${typeof v === 'string' ? v : JSON.stringify(v, null, 2)}
                      </div>
                    </div>
                  `).join("")}
                </div>
              ` : ''}
            </div>
          ` : ''}
        </div>
      </div>
    </div>
  `;
}

// Sleek Collapsible Drawer Implementation
function renderVisualizer(activePlan, currentAgent, isExecuting, agentOutputs, stepText, completedAgents) {
  const container = document.getElementById("visualizer-container");
  if (!container) return;

  const allAgents = [
    { id: "supervisor_plan", label: "Supervisor", role: "Planner", icon: "brain", color: "from-indigo-500 via-purple-600 to-primary-600", type: "supervisor" },
    { id: "web_search_agent", label: "Web Search", role: "Live Data", icon: "globe", color: "from-cyan-500 to-blue-600", type: "worker" },
    { id: "rag_agent", label: "Document RAG", role: "Vector DB", icon: "fileText", color: "from-emerald-500 to-teal-600", type: "worker" },
    { id: "research_agent", label: "Research Agent", role: "ArXiv/Wiki", icon: "search", color: "from-amber-500 to-orange-600", type: "worker" },
    { id: "code_agent", label: "Code Agent", icon: "code2", color: "from-violet-500 to-fuchsia-600", type: "worker" },
    { id: "data_analysis_agent", label: "Data Analysis", role: "Pandas/CSV", icon: "barChart3", color: "from-rose-500 to-pink-600", type: "worker" },
    { id: "document_agent", label: "Document Parser", role: "PDF/Office", icon: "fileText", color: "from-sky-500 to-blue-600", type: "worker" },
    { id: "memory_agent", label: "Memory Agent", role: "Context", icon: "database", color: "from-yellow-500 to-amber-600", type: "worker" },
    { id: "supervisor_synthesize", label: "Supervisor", role: "Synthesizer", icon: "sparkles", color: "from-indigo-600 via-accent-purple to-accent-cyan", type: "supervisor" },
  ];

  container.innerHTML = `
    <details class="group bg-card/70 backdrop-blur-md border border-border/80 rounded-2xl my-2 overflow-hidden shadow-lg transition-all" ${isExecuting ? 'open' : ''}>
      <summary class="flex items-center justify-between px-4 py-2.5 cursor-pointer bg-card/90 hover:bg-cardLight/60 select-none transition-colors">
        <div class="flex items-center gap-2.5">
          <div class="w-6 h-6 rounded-lg bg-primary-600/30 border border-primary-500/40 flex items-center justify-center text-primary-400">
            ${getIconSvg("brain", "w-3.5 h-3.5 animate-pulse")}
          </div>
          <span class="text-xs font-bold text-white tracking-wide">LangGraph Multi-Agent Orchestration Flow</span>
          <span class="text-[11px] font-mono text-accent-cyan flex items-center gap-1">
            ${getIconSvg("zap", "w-3 h-3 text-accent-cyan")}
            <span>${stepText || 'Workflow Execution Ready'}</span>
          </span>
        </div>

        <div class="flex items-center gap-2.5 text-xs">
          ${isExecuting ? `
            <span class="flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/30 text-[10px] font-mono animate-pulse">
              ${getIconSvg("loader2", "w-3 h-3 animate-spin")}
              <span>${currentAgent}</span>
            </span>
          ` : `
            <span class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-accent-emerald/10 text-accent-emerald border border-accent-emerald/30 text-[10px] font-mono">
              ${getIconSvg("checkCircle2", "w-3 h-3")}
              <span>9 Nodes Ready</span>
            </span>
          `}
          ${getIconSvg("chevronDown", "w-4 h-4 text-gray-400 group-open:rotate-180 transition-transform")}
        </div>
      </summary>

      <div class="p-3.5 border-t border-border/50 grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-9 gap-2.5">
        ${allAgents.map((agent) => {
          const isCurrent = currentAgent === agent.id;
          const isCompleted = completedAgents.includes(agent.id) || Boolean(agentOutputs[agent.id]);
          const isSelected = activePlan.includes(agent.id) || agent.type === "supervisor";

          return `
            <div class="relative flex flex-col items-center justify-between p-2.5 rounded-xl border transition-all duration-300 text-center ${
              isCurrent
                ? "bg-cardLight/90 border-2 border-accent-cyan shadow-xl shadow-accent-cyan/30 scale-105 ring-2 ring-accent-cyan/40"
                : isCompleted
                ? "bg-card/90 border-accent-emerald/50 shadow-md shadow-accent-emerald/10"
                : isSelected
                ? "bg-card/80 border-primary-500/40 text-gray-200"
                : "bg-card/20 border-border/30 text-gray-500 opacity-50"
            }">
              <div class="w-8 h-8 rounded-lg bg-gradient-to-tr ${agent.color} flex items-center justify-center text-white mb-1.5 shadow-md ${isCurrent ? 'scale-110 animate-pulse' : ''}">
                ${getIconSvg(agent.icon, "w-4 h-4")}
              </div>

              <span class="text-[10px] font-semibold line-clamp-1 text-gray-200">${agent.label}</span>

              <div class="mt-1 flex items-center justify-center h-4">
                ${isCurrent && isExecuting ? `
                  <span class="flex items-center gap-1 text-[9px] text-accent-cyan font-bold font-mono bg-accent-cyan/10 px-1.5 py-0.5 rounded-full border border-accent-cyan/30">
                    <span class="w-1 h-1 rounded-full bg-accent-cyan animate-ping"></span>
                    Executing
                  </span>
                ` : isCompleted ? `
                  <span class="flex items-center gap-1 text-[9px] text-accent-emerald font-semibold font-mono">
                    ${getIconSvg("checkCircle2", "w-3 h-3 text-accent-emerald")}
                    Done
                  </span>
                ` : `
                  <span class="text-[9px] text-gray-500 font-mono">${isSelected ? "Active" : "Idle"}</span>
                `}
              </div>
            </div>
          `;
        }).join("")}
      </div>
    </details>
  `;
}

async function handleSendMessage() {
  const inputEl = document.getElementById("chat-input");
  if (!inputEl || !inputEl.value.trim() || isSendingChat) return;

  const content = inputEl.value.trim();
  inputEl.value = "";
  isSendingChat = true;

  const selectModel = document.getElementById("select-model");
  const selectedModel = selectModel ? selectModel.value : "llama3.2:latest";
  const activeProvider = selectedModel === "gemini-1.5-flash" ? "gemini" : "ollama";

  // Push User Message
  const tempUserMsg = {
    id: "temp-user-" + Date.now(),
    sender_role: "user",
    content: content,
    created_at: new Date().toISOString(),
  };

  // Push Temporary Assistant Executing Loading Bubble (React behavior)
  const tempAssistantLoadingMsg = {
    id: "temp-assistant-loading",
    sender_role: "assistant",
    isLoading: true,
    content: "",
    created_at: new Date().toISOString(),
  };

  chatMessages.push(tempUserMsg);
  chatMessages.push(tempAssistantLoadingMsg);
  renderChatMessagesOnly();
  scrollToBottom();

  let targetChatId = currentChatId;

  renderVisualizer(["supervisor_plan", "supervisor_synthesize"], "supervisor_plan", true, {}, "Step 1: Supervisor Analyzing Query & Building Routing Plan...", []);

  try {
    if (!targetChatId) {
      const newChat = await window.api.createChat({
        title: content.slice(0, 30),
        provider: activeProvider,
        model: selectedModel,
      });
      targetChatId = newChat.id;
      currentChatId = targetChatId;
    }

    const docSelect = document.getElementById("chat-document-select");
    const selectedDocId = docSelect ? docSelect.value : null;

    const response = await window.api.sendMessage({
      chat_id: targetChatId,
      content: content,
      provider: activeProvider,
      model: selectedModel,
      document_id: selectedDocId,
    });

    let plan = [];
    let outputs = {};
    if (response.metadata_json) {
      try {
        const meta = JSON.parse(response.metadata_json);
        outputs = meta;
        if (meta.execution_plan && Array.isArray(meta.execution_plan)) {
          plan = meta.execution_plan;
        }
      } catch (e) {}
    }

    const completed = ["supervisor_plan"];
    renderVisualizer(["supervisor_plan", ...plan, "supervisor_synthesize"], "supervisor_plan", true, outputs, `Executing Execution Plan (${plan.length} agents)...`, completed);

    for (let i = 0; i < plan.length; i++) {
      const agentId = plan[i];
      renderVisualizer(["supervisor_plan", ...plan, "supervisor_synthesize"], agentId, true, outputs, `Step ${i + 2}/${plan.length + 2}: Executing [${agentId.toUpperCase()}]...`, [...completed]);
      await sleep(850);
      completed.push(agentId);
    }

    renderVisualizer(["supervisor_plan", ...plan, "supervisor_synthesize"], "supervisor_synthesize", true, outputs, `Final Step: Supervisor Synthesizing Complete Response...`, [...completed]);
    await sleep(850);
    completed.push("supervisor_synthesize");

    renderVisualizer(["supervisor_plan", ...plan, "supervisor_synthesize"], "supervisor_synthesize", false, outputs, `Execution Complete`, [...completed]);

    // Replace temporary loading messages with actual final response
    chatMessages = chatMessages.filter((m) => m.id !== tempUserMsg.id && m.id !== "temp-assistant-loading");
    chatMessages.push(tempUserMsg);
    chatMessages.push(response);
    renderChatMessagesOnly();
    renderSidebar(); // Update recent chat list sidebar
    scrollToBottom();
  } catch (err) {
    chatMessages = chatMessages.filter((m) => m.id !== "temp-assistant-loading");
    chatMessages.push({
      id: "error-" + Date.now(),
      sender_role: "assistant",
      content: "⚠️ An error occurred while communicating with the agent system. Please verify Ollama service status.",
    });
    renderChatMessagesOnly();
    renderVisualizer(["supervisor_plan", "supervisor_synthesize"], "supervisor_plan", false, {}, "Execution Error", []);
  } finally {
    isSendingChat = false;
  }
}

function renderChatMessagesOnly() {
  const container = document.getElementById("messages-scroll-area");
  if (!container) return;
  container.innerHTML = chatMessages.map((msg) => renderMessageBubbleHtml(msg)).join("");
  attachBubbleListeners();
}

function attachBubbleListeners() {
  document.querySelectorAll(".btn-copy-msg").forEach((btn) => {
    btn.addEventListener("click", () => {
      const raw = btn.getAttribute("data-encoded-text");
      if (raw) {
        try {
          const text = decodeURIComponent(raw);
          navigator.clipboard.writeText(text);
          btn.innerHTML = `${getIconSvg("check", "w-3.5 h-3.5 text-accent-emerald")}<span>Copied</span>`;
          setTimeout(() => {
            btn.innerHTML = `${getIconSvg("copy", "w-3.5 h-3.5")}<span>Copy response</span>`;
          }, 2000);
        } catch (e) {}
      }
    });
  });

  document.querySelectorAll(".btn-copy-code").forEach((btn) => {
    btn.addEventListener("click", () => {
      const raw = btn.getAttribute("data-encoded-code");
      if (raw) {
        try {
          const code = decodeURIComponent(raw);
          navigator.clipboard.writeText(code);
          btn.innerHTML = `${getIconSvg("check", "w-3.5 h-3.5 text-accent-emerald")}<span class="text-[11px]">Copied!</span>`;
          setTimeout(() => {
            btn.innerHTML = `${getIconSvg("copy", "w-3.5 h-3.5")}<span class="text-[11px]">Copy Code</span>`;
          }, 2000);
        } catch (e) {}
      }
    });
  });

  document.querySelectorAll(".btn-toggle-insights").forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-target");
      const target = document.getElementById(targetId);
      if (target) {
        target.classList.toggle("hidden");
      }
    });
  });
}

function scrollToBottom() {
  const container = document.getElementById("messages-scroll-area");
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
}

// VIEW 3: Document Hub & RAG Controller
async function initDocumentsView() {
  const container = document.getElementById("view-documents");
  if (!container) return;

  let docs = [];
  try {
    docs = (await window.api.listDocuments()) || [];
  } catch (err) {}

  const totalChunks = docs.reduce((acc, d) => acc + getDocChunkCount(d), 0);

  container.innerHTML = `
    <div class="max-w-6xl mx-auto space-y-8 pb-10">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold text-white flex items-center gap-2.5">
            ${getIconSvg("fileText", "w-7 h-7 text-accent-emerald")}
            <span>Document Knowledge Hub & RAG Engine</span>
          </h1>
          <p class="text-xs text-gray-400 mt-1">
            Upload PDFs, Office files, and CSVs. Automatically chunked, embedded, and stored in local ChromaDB for RAG Agent retrieval.
          </p>
        </div>

        <div class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-cardLight border border-border text-xs text-gray-300">
          ${getIconSvg("database", "w-4 h-4 text-accent-purple")}
          <span>Vector Index: <strong class="text-white">${totalChunks} Chunks</strong></span>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Upload Card -->
        <div class="lg:col-span-1 glass-panel p-6 rounded-2xl border border-border/80 flex flex-col justify-between">
          <div>
            <h2 class="text-base font-bold text-white mb-2 flex items-center gap-2">
              ${getIconSvg("uploadCloud", "w-5 h-5 text-primary-400")}
              <span>Upload Document</span>
            </h2>
            <p class="text-xs text-gray-400 mb-4">
              Supported formats: PDF, DOCX, XLSX, PPTX, TXT, CSV, Markdown.
            </p>

            <label class="border-2 border-dashed border-border/80 hover:border-primary-500/80 rounded-2xl p-6 flex flex-col items-center justify-center text-center cursor-pointer transition-all bg-card/40 hover:bg-cardLight/50 group">
              <input type="file" id="file-upload-input" accept=".pdf,.docx,.xlsx,.pptx,.txt,.csv,.md" class="hidden" />
              <div class="w-12 h-12 rounded-2xl bg-primary-600/20 text-primary-400 border border-primary-500/30 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                ${getIconSvg("uploadCloud", "w-6 h-6")}
              </div>
              <span class="text-xs font-semibold text-gray-200 group-hover:text-primary-300">Click to select file</span>
              <span class="text-[10px] text-gray-400 mt-1">or drag and drop here</span>
            </label>

            <div id="upload-status" class="mt-3"></div>
          </div>

          <div class="mt-6 pt-4 border-t border-border/60 text-[11px] text-gray-400 flex items-center justify-between">
            <span>RAG Model: nomic-embed-text</span>
            <span class="text-accent-emerald font-mono">ChromaDB</span>
          </div>
        </div>

        <!-- Indexed Documents Table -->
        <div class="lg:col-span-2 glass-panel p-6 rounded-2xl border border-border/80">
          <h2 class="text-base font-bold text-white mb-4 flex items-center justify-between">
            <div class="flex items-center gap-2">
              ${getIconSvg("checkCircle2", "w-5 h-5 text-accent-emerald")}
              <span>Indexed Documents (${docs.length})</span>
            </div>
          </h2>

          ${docs.length === 0 ? `
            <div class="text-center py-12 px-4 border border-dashed border-border/60 rounded-xl">
              ${getIconSvg("fileText", "w-8 h-8 text-gray-500 mx-auto mb-2")}
              <p class="text-sm font-medium text-gray-300">No documents uploaded yet</p>
              <p class="text-xs text-gray-500 mt-1">Upload a file on the left to start semantic RAG search.</p>
            </div>
          ` : `
            <div class="overflow-x-auto">
              <table class="w-full text-left text-xs">
                <thead>
                  <tr class="border-b border-border/80 text-gray-400 uppercase font-mono text-[10px]">
                    <th class="py-3 px-3">Filename</th>
                    <th class="py-3 px-3">Type</th>
                    <th class="py-3 px-3">Size</th>
                    <th class="py-3 px-3">Chunks</th>
                    <th class="py-3 px-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-border/40">
                  ${docs.map((doc) => {
                    const count = getDocChunkCount(doc);
                    return `
                      <tr class="hover:bg-cardLight/50 transition-colors">
                        <td class="py-3 px-3 font-medium text-gray-200 flex items-center gap-2">
                          ${getIconSvg("fileText", "w-4 h-4 text-primary-400 shrink-0")}
                          <span class="truncate max-w-xs">${doc.filename}</span>
                        </td>
                        <td class="py-3 px-3 text-gray-400 uppercase font-mono text-[10px]">${doc.file_type || "File"}</td>
                        <td class="py-3 px-3 text-gray-400 font-mono">${(doc.file_size / 1024).toFixed(1)} KB</td>
                        <td class="py-3 px-3">
                          <span class="px-2 py-0.5 rounded-full bg-accent-purple/10 text-accent-purple border border-accent-purple/20 font-mono text-[11px]">
                            ${count} chunks
                          </span>
                        </td>
                        <td class="py-3 px-3 text-right">
                          <button class="btn-delete-doc p-1.5 text-gray-400 hover:text-accent-rose transition-colors rounded-lg hover:bg-cardLight" data-doc-id="${doc.id}" title="Delete document">
                            ${getIconSvg("trash2", "w-4 h-4")}
                          </button>
                        </td>
                      </tr>
                    `;
                  }).join("")}
                </tbody>
              </table>
            </div>
          `}
        </div>
      </div>

      <!-- Vector Search Playground -->
      <div class="glass-panel p-6 rounded-2xl border border-border/80">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-base font-bold text-white flex items-center gap-2">
              ${getIconSvg("search", "w-5 h-5 text-accent-cyan")}
              <span>ChromaDB RAG Vector Query Playground</span>
            </h2>
            <p class="text-xs text-gray-400">Test semantic vector similarity retrieval across indexed chunks.</p>
          </div>
        </div>

        <form id="vector-search-form" class="flex gap-3 mb-6">
          <input type="text" id="vector-query-input" placeholder="Enter a query to test ChromaDB semantic similarity match..." class="flex-1 bg-cardLight/70 border border-border rounded-xl px-4 py-2.5 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-accent-cyan" />
          <button type="submit" class="px-5 py-2.5 rounded-xl bg-accent-cyan hover:bg-accent-cyan/80 text-background font-bold text-xs transition-all flex items-center gap-2">
            ${getIconSvg("search", "w-4 h-4")}
            <span>Run Vector Query</span>
          </button>
        </form>

        <div id="vector-search-results"></div>
      </div>
    </div>
  `;

  document.getElementById("file-upload-input")?.addEventListener("change", async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const statusEl = document.getElementById("upload-status");
    if (statusEl) {
      statusEl.innerHTML = `<div class="p-3 rounded-xl bg-primary-500/10 border border-primary-500/30 text-primary-300 text-xs">Parsing & embedding file...</div>`;
    }

    try {
      await window.api.uploadDocument(files[0]);
      if (statusEl) {
        statusEl.innerHTML = `<div class="p-3 rounded-xl bg-accent-emerald/10 border border-accent-emerald/30 text-accent-emerald text-xs">Successfully uploaded and indexed!</div>`;
      }
      initDocumentsView();
    } catch (err) {
      if (statusEl) {
        statusEl.innerHTML = `<div class="p-3 rounded-xl bg-accent-rose/10 border border-accent-rose/30 text-accent-rose text-xs">${err.message || 'Upload failed'}</div>`;
      }
    }
  });

  document.querySelectorAll(".btn-delete-doc").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const id = btn.getAttribute("data-doc-id");
      if (id) {
        try {
          await window.api.deleteDocument(id);
          initDocumentsView();
        } catch (err) {}
      }
    });
  });

  document.getElementById("vector-search-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const queryEl = document.getElementById("vector-query-input");
    const resultsEl = document.getElementById("vector-search-results");
    if (!queryEl || !queryEl.value.trim() || !resultsEl) return;

    resultsEl.innerHTML = `<div class="text-xs text-gray-400">Searching ChromaDB vector store...</div>`;
    try {
      const res = await window.api.searchChunks(queryEl.value.trim(), 5);
      if (!res || res.length === 0) {
        resultsEl.innerHTML = `<div class="text-xs text-gray-400">No matching vector chunks found.</div>`;
      } else {
        resultsEl.innerHTML = `
          <div class="space-y-3">
            <h3 class="text-xs font-bold text-gray-300 uppercase tracking-wider">Top Retrieved Document Chunks</h3>
            ${res.map((r, i) => `
              <div class="p-4 rounded-xl bg-cardLight/40 border border-border/60 space-y-2">
                <div class="flex items-center justify-between text-xs">
                  <span class="font-mono text-accent-cyan">Chunk #${i + 1}</span>
                  <span class="px-2 py-0.5 rounded bg-accent-emerald/10 text-accent-emerald font-mono text-[10px]">Similarity Score: ${(r.score || 0.85).toFixed(3)}</span>
                </div>
                <p class="text-xs text-gray-200 leading-relaxed font-mono whitespace-pre-wrap">${r.content}</p>
              </div>
            `).join("")}
          </div>
        `;
      }
    } catch (err) {
      resultsEl.innerHTML = `<div class="text-xs text-accent-rose">Vector search failed: ${err.message}</div>`;
    }
  });
}

// VIEW 4: Agent Orchestrator Controller
async function initAgentsView() {
  const container = document.getElementById("view-agents");
  if (!container) return;

  let agents = [];
  try {
    agents = (await window.api.listAgents()) || [];
  } catch (err) {
    agents = [
      { id: "supervisor", name: "Supervisor Agent", description: "Analyzes user query semantics, crafts LangGraph execution plan, and synthesizes final answers.", capabilities: ["Query Planning", "Multi-Agent Routing", "Synthesis & Formatting"], tools: ["LangGraph StateGraph", "Prompt Injector"], icon: "brain", color: "from-indigo-500 to-purple-600" },
      { id: "web_search", name: "Web Search Agent", description: "Fetches live news, updates, and websites via DuckDuckGo and web parsers.", capabilities: ["DuckDuckGo Live Search", "URL Content Extraction"], tools: ["duckduckgo-search", "BeautifulSoup4"], icon: "globe", color: "from-cyan-500 to-blue-600" },
      { id: "rag", name: "Document RAG Agent", description: "Queries ChromaDB vector database for semantic context matching uploaded user files.", capabilities: ["Vector Search", "ChromaDB Query", "Semantic Chunk Matching"], tools: ["ChromaDB", "nomic-embed-text"], icon: "fileText", color: "from-emerald-500 to-teal-600" },
      { id: "research", name: "Research Agent", description: "Queries academic databases including ArXiv papers and Wikipedia articles.", capabilities: ["ArXiv Paper Retrieval", "Wikipedia Summarization"], tools: ["arxiv-python", "wikipedia-api"], icon: "search", color: "from-amber-500 to-orange-600" },
      { id: "code", name: "Code Agent", description: "Generates, debugs, and executes Python code inside isolated REPL environment.", capabilities: ["Python REPL Execution", "Bug Fixing", "Refactoring"], tools: ["Python REPL", "AST Validator"], icon: "code2", color: "from-violet-500 to-fuchsia-600" },
      { id: "data_analysis", name: "Data Analysis Agent", description: "Performs statistical analysis on CSVs and DataFrames using Pandas & NumPy.", capabilities: ["Pandas Dataframes", "Summary Statistics", "Tabular Parsing"], tools: ["Pandas", "NumPy", "Tabulate"], icon: "barChart3", color: "from-rose-500 to-pink-600" },
      { id: "memory", name: "Memory Agent", description: "Manages conversation context and user preference persistence across sessions.", capabilities: ["Long-term Memory", "Context Summarization"], tools: ["SQLite Session Store"], icon: "database", color: "from-yellow-500 to-amber-600" },
    ];
  }

  container.innerHTML = `
    <div class="max-w-6xl mx-auto space-y-8 pb-10">
      <div>
        <h1 class="text-2xl font-bold text-white flex items-center gap-2.5">
          ${getIconSvg("bot", "w-7 h-7 text-primary-400")}
          <span>Agent Orchestrator & Capabilities</span>
        </h1>
        <p class="text-xs text-gray-400 mt-1">Explore the autonomous sub-agents connected within the LangGraph multi-agent architecture.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        ${agents.map((agent) => `
          <div class="glass-panel p-6 rounded-2xl border border-border/80 flex flex-col justify-between">
            <div>
              <div class="flex items-center justify-between mb-4">
                <div class="flex items-center gap-3">
                  <div class="w-11 h-11 rounded-xl bg-gradient-to-tr ${agent.color || 'from-primary-600 to-accent-purple'} flex items-center justify-center text-white shadow-lg">
                    ${getIconSvg(agent.icon || "bot", "w-6 h-6")}
                  </div>
                  <div>
                    <h3 class="font-bold text-white text-base">${agent.name}</h3>
                    <span class="text-[11px] text-accent-emerald flex items-center gap-1 font-mono">
                      ${getIconSvg("checkCircle2", "w-3.5 h-3.5")}
                      Status: Active Node
                    </span>
                  </div>
                </div>
              </div>

              <p class="text-xs text-gray-300 leading-relaxed mb-4">${agent.description}</p>

              <div class="space-y-3">
                <div>
                  <span class="text-[11px] font-bold text-gray-400 uppercase tracking-wider block mb-1.5">Core Capabilities</span>
                  <div class="flex flex-wrap gap-1.5">
                    ${(agent.capabilities || []).map((c) => `<span class="px-2.5 py-1 rounded-lg bg-cardLight text-gray-200 text-xs border border-border/80">${c}</span>`).join("")}
                  </div>
                </div>

                <div>
                  <span class="text-[11px] font-bold text-gray-400 uppercase tracking-wider block mb-1.5 flex items-center gap-1">
                    ${getIconSvg("wrench", "w-3 h-3 text-accent-cyan")}
                    Assigned Tools
                  </span>
                  <div class="flex flex-wrap gap-1.5">
                    ${(agent.tools || []).map((t) => `<span class="px-2 py-0.5 rounded bg-accent-cyan/10 text-accent-cyan text-[11px] font-mono border border-accent-cyan/20">${t}</span>`).join("")}
                  </div>
                </div>
              </div>
            </div>

            <div class="mt-6 pt-4 border-t border-border/60 flex items-center justify-between">
              <span class="text-[11px] text-gray-400">Framework: LangGraph</span>
              <a href="#chat?query=Run test query for ${encodeURIComponent(agent.name)}" class="flex items-center gap-1.5 text-xs text-primary-400 hover:text-primary-300 font-semibold">
                <span>Test ${agent.name}</span>
                ${getIconSvg("arrowRight", "w-3.5 h-3.5")}
              </a>
            </div>
          </div>
        `).join("")}
      </div>
    </div>
  `;
}

// VIEW 5: Settings Controller
async function initSettingsView() {
  const container = document.getElementById("view-settings");
  if (!container) return;

  let settings = {
    default_provider: "ollama",
    default_model: "llama3.2:latest",
    embedding_model: "nomic-embed-text",
    ollama_url: "http://localhost:11434",
    enable_cloud_gemini: false,
    gemini_api_key: "",
  };

  try {
    const data = await window.api.getSettings();
    settings = { ...settings, ...data };
  } catch (err) {}

  container.innerHTML = `
    <div class="max-w-4xl mx-auto space-y-8 pb-10">
      <div>
        <h1 class="text-2xl font-bold text-white flex items-center gap-2.5">
          ${getIconSvg("settings", "w-7 h-7 text-primary-400")}
          <span>System & LLM Engine Settings</span>
        </h1>
        <p class="text-xs text-gray-400 mt-1">Configure your local Ollama connection, Google Gemini cloud fallback, embedding models, and ChromaDB parameters.</p>
      </div>

      <form id="settings-form" class="space-y-6">
        <div id="settings-feedback"></div>

        <!-- Local Ollama Settings -->
        <div class="glass-panel p-6 rounded-2xl border border-border/80 space-y-4">
          <h2 class="text-base font-bold text-white flex items-center gap-2 border-b border-border/60 pb-3">
            ${getIconSvg("cpu", "w-5 h-5 text-accent-cyan")}
            <span>Local Ollama LLM Connection</span>
          </h2>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-300 mb-1.5">Default LLM Provider</label>
              <select id="set-provider" class="w-full bg-cardLight/70 border border-border rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-primary-500">
                <option value="ollama" ${settings.default_provider === 'ollama' ? 'selected' : ''}>Ollama Local (100% Free & Private)</option>
                <option value="gemini" ${settings.default_provider === 'gemini' ? 'selected' : ''}>Google Gemini Cloud (Free Tier API Key)</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-semibold text-gray-300 mb-1.5">Default Local Model</label>
              <select id="set-model" class="w-full bg-cardLight/70 border border-border rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-primary-500">
                <option value="llama3.2:latest" ${settings.default_model === 'llama3.2:latest' ? 'selected' : ''}>Llama 3.2 (Installed Local)</option>
                <option value="qwen3" ${settings.default_model === 'qwen3' ? 'selected' : ''}>Qwen 3 (Fast Reasoning)</option>
                <option value="llama3" ${settings.default_model === 'llama3' ? 'selected' : ''}>Llama 3 (Meta Open Source)</option>
                <option value="mistral" ${settings.default_model === 'mistral' ? 'selected' : ''}>Mistral 7B</option>
                <option value="gemma" ${settings.default_model === 'gemma' ? 'selected' : ''}>Gemma 2B</option>
              </select>
            </div>

            <div class="sm:col-span-2">
              <label class="block text-xs font-semibold text-gray-300 mb-1.5">Ollama Service Base URL</label>
              <input type="text" id="set-url" value="${settings.ollama_url}" class="w-full bg-cardLight/70 border border-border rounded-xl px-4 py-2.5 text-xs text-white font-mono focus:outline-none focus:border-primary-500" />
            </div>
          </div>
        </div>

        <!-- Cloud Fallback Settings -->
        <div class="glass-panel p-6 rounded-2xl border border-border/80 space-y-4">
          <h2 class="text-base font-bold text-white flex items-center gap-2 border-b border-border/60 pb-3">
            ${getIconSvg("fileText", "w-5 h-5 text-accent-purple")}
            <span>Optional Cloud LLM Fallback (Google Gemini)</span>
          </h2>

          <div class="space-y-4">
            <div class="flex items-center gap-3">
              <input type="checkbox" id="set-gemini-toggle" ${settings.enable_cloud_gemini ? 'checked' : ''} class="w-4 h-4 rounded border-border text-primary-600 focus:ring-primary-500 bg-cardLight cursor-pointer" />
              <label for="set-gemini-toggle" class="text-xs font-medium text-gray-200 cursor-pointer">
                Enable Google Gemini API Cloud Fallback when local Ollama is offline
              </label>
            </div>

            <div>
              <label class="block text-xs font-semibold text-gray-300 mb-1.5">Google Gemini API Key</label>
              <input type="password" id="set-gemini-key" value="${settings.gemini_api_key || ''}" placeholder="AIzaSy..." class="w-full bg-cardLight/70 border border-border rounded-xl px-4 py-2.5 text-xs text-white font-mono focus:outline-none focus:border-primary-500" />
            </div>
          </div>
        </div>

        <div class="flex justify-end">
          <button type="submit" class="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-primary-600 to-accent-purple hover:from-primary-500 hover:to-primary-600 text-white font-semibold text-xs transition-all shadow-lg shadow-primary-600/30">
            ${getIconSvg("check", "w-4 h-4")}
            <span>Save Settings</span>
          </button>
        </div>
      </form>
    </div>
  `;

  document.getElementById("settings-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const feedback = document.getElementById("settings-feedback");

    const updatedData = {
      default_provider: document.getElementById("set-provider").value,
      default_model: document.getElementById("set-model").value,
      ollama_url: document.getElementById("set-url").value,
      enable_cloud_gemini: document.getElementById("set-gemini-toggle").checked,
      gemini_api_key: document.getElementById("set-gemini-key").value,
      embedding_model: settings.embedding_model,
    };

    try {
      await window.api.updateSettings(updatedData);
      if (feedback) {
        feedback.innerHTML = `<div class="p-4 rounded-2xl border text-xs flex items-center gap-2 bg-accent-emerald/10 border-accent-emerald/30 text-accent-emerald"><span>System settings successfully updated!</span></div>`;
      }
    } catch (err) {
      if (feedback) {
        feedback.innerHTML = `<div class="p-4 rounded-2xl border text-xs flex items-center gap-2 bg-accent-rose/10 border-accent-rose/30 text-accent-rose"><span>${err.message || 'Failed to update settings'}</span></div>`;
      }
    }
  });
}

// Markdown Parser Helper Function (Line-by-line parsing matching React FormattedMarkdown)
function formatMarkdownToHtml(content) {
  if (!content) return "";

  const codeBlockRegex = /```([a-zA-Z0-9_+#-]*)\n([\s\S]*?)```/g;
  const parts = [];
  let lastIndex = 0;
  let match;

  while ((match = codeBlockRegex.exec(content)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ type: "text", text: content.slice(lastIndex, match.index) });
    }
    parts.push({
      type: "code",
      lang: match[1] || "code",
      code: match[2].trim(),
    });
    lastIndex = match.index + match[0].length;
  }
  if (lastIndex < content.length) {
    parts.push({ type: "text", text: content.slice(lastIndex) });
  }

  let html = "";
  parts.forEach((part) => {
    if (part.type === "code") {
      const safeCode = part.code.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
      const encodedCode = encodeURIComponent(part.code);
      html += `
        <div class="my-3 rounded-xl border border-border/80 bg-cardLight/90 overflow-hidden shadow-lg">
          <div class="flex items-center justify-between px-4 py-2 bg-card/90 border-b border-border/60 text-xs text-gray-400">
            <div class="flex items-center gap-2 font-mono text-[11px] font-bold text-accent-cyan uppercase">
              ${getIconSvg("code2", "w-3.5 h-3.5 text-accent-cyan")}
              <span>${part.lang}</span>
            </div>
            <button class="btn-copy-code flex items-center gap-1.5 px-2.5 py-1 rounded-lg hover:bg-cardLight text-gray-300 hover:text-white transition-colors" data-encoded-code="${encodedCode}">
              ${getIconSvg("copy", "w-3.5 h-3.5")}
              <span class="text-[11px]">Copy Code</span>
            </button>
          </div>
          <div class="p-4 overflow-x-auto font-mono text-xs text-gray-200 leading-relaxed bg-[#0d1117]/90 selection:bg-primary-600/50">
            <pre>${safeCode}</pre>
          </div>
        </div>
      `;
    } else {
      const lines = part.text.split("\n");
      let inList = false;
      lines.forEach((line) => {
        const trimmed = line.trim();

        if (trimmed.startsWith("### ")) {
          if (inList) { html += "</ul>"; inList = false; }
          html += `<h3 class="text-sm sm:text-base font-bold text-white mt-4 mb-2 border-b border-border/40 pb-1 flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-accent-cyan inline-block"></span>
            ${renderInlineFormatting(trimmed.slice(4))}
          </h3>`;
        } else if (trimmed.startsWith("## ")) {
          if (inList) { html += "</ul>"; inList = false; }
          html += `<h2 class="text-base sm:text-lg font-extrabold text-white mt-5 mb-2 border-b border-border/60 pb-1.5 flex items-center gap-2">
            ${getIconSvg("sparkles", "w-4 h-4 text-primary-400")}
            ${renderInlineFormatting(trimmed.slice(3))}
          </h2>`;
        } else if (trimmed.startsWith("# ")) {
          if (inList) { html += "</ul>"; inList = false; }
          html += `<h1 class="text-lg sm:text-xl font-black text-white mt-6 mb-3 border-b border-primary-500/30 pb-2">
            ${renderInlineFormatting(trimmed.slice(2))}
          </h1>`;
        } else if (trimmed.startsWith("* ") || trimmed.startsWith("- ") || /^\d+\.\s/.test(trimmed)) {
          if (!inList) { html += '<ul class="space-y-1.5 my-2.5 pl-5 list-disc marker:text-primary-400 text-gray-200">'; inList = true; }
          const clean = trimmed.replace(/^(\*|-|\d+\.)\s+/, "");
          html += `<li class="text-gray-200 leading-relaxed text-sm">${renderInlineFormatting(clean)}</li>`;
        } else if (trimmed.startsWith("> ")) {
          if (inList) { html += "</ul>"; inList = false; }
          html += `<blockquote class="my-2 border-l-4 border-primary-500 bg-primary-500/10 p-3 rounded-r-xl text-gray-200 text-xs italic shadow-sm">
            ${renderInlineFormatting(trimmed.slice(2))}
          </blockquote>`;
        } else if (trimmed === "") {
          if (inList) { html += "</ul>"; inList = false; }
          html += '<div class="h-1.5"></div>';
        } else {
          if (inList) { html += "</ul>"; inList = false; }
          html += `<p class="my-2 text-gray-200 leading-relaxed text-sm">${renderInlineFormatting(line)}</p>`;
        }
      });
      if (inList) { html += "</ul>"; }
    }
  });

  return html;
}

function renderInlineFormatting(str) {
  if (!str) return "";
  let res = str.replace(/</g, "&lt;").replace(/>/g, "&gt;");
  res = res.replace(/\*\*(.*?)\*\*(?!\*)/g, '<strong class="font-bold text-white">$1</strong>');
  res = res.replace(/`([^`]+)`/g, '<code class="px-1.5 py-0.5 mx-0.5 rounded-md bg-cardLight text-accent-cyan font-mono text-[12px] border border-border/60">$1</code>');
  res = res.replace(/\*(.*?)\*/g, '<em class="italic text-gray-300">$1</em>');
  return res;
}
