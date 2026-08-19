// Dynamic API Base URL resolution for local and cloud deployments
let activeApiBaseUrl = null;

function getApiBaseUrl() {
  if (activeApiBaseUrl) return activeApiBaseUrl;
  if (typeof window !== "undefined" && window.location) {
    if (window.location.protocol === "file:") {
      return "http://localhost:8000/api/v1";
    }
    const host = window.location.host;
    if (host.includes("localhost") || host.includes("127.0.0.1")) {
      const port = window.location.port || "8000";
      return `${window.location.protocol}//localhost:${port}/api/v1`;
    }
    return `${window.location.protocol}//${host}/api/v1`;
  }
  return "http://localhost:8000/api/v1";
}

function getAuthToken() {
  if (typeof window !== "undefined") {
    return sessionStorage.getItem("token");
  }
  return null;
}

function setAuthToken(token) {
  if (typeof window !== "undefined") {
    sessionStorage.setItem("token", token);
    localStorage.removeItem("token");
  }
}

function removeAuthToken() {
  if (typeof window !== "undefined") {
    sessionStorage.removeItem("token");
    localStorage.removeItem("token");
  }
}

// Request with automatic retry loop & dual-port detection (8000 <-> 8001)
async function request(endpoint, options = {}, retries = 3) {
  const token = getAuthToken();
  const headers = {
    ...(options.headers || {}),
  };

  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let baseUrl = getApiBaseUrl();
  const candidateUrls = [baseUrl];
  if (baseUrl.includes(":8000")) {
    candidateUrls.push(baseUrl.replace(":8000", ":8001"));
  } else if (baseUrl.includes(":8001")) {
    candidateUrls.push(baseUrl.replace(":8001", ":8000"));
  }

  let lastError = null;
  for (let candidate of candidateUrls) {
    for (let attempt = 0; attempt < retries; attempt++) {
      try {
        const response = await fetch(`${candidate}${endpoint}`, {
          ...options,
          headers,
        });

        if (!response.ok) {
          if (
            response.status === 401 &&
            !endpoint.includes("/auth/login") &&
            !endpoint.includes("/auth/register")
          ) {
            removeAuthToken();
            if (
              typeof window !== "undefined" &&
              !window.location.hash.includes("login") &&
              !window.location.hash.includes("register")
            ) {
              window.location.hash = "#login";
            }
          }
          const errorData = await response.json().catch(() => ({ detail: "An error occurred" }));
          let msg = "An error occurred";
          if (typeof errorData.detail === "string") {
            msg = errorData.detail;
          } else if (Array.isArray(errorData.detail) && errorData.detail.length > 0) {
            msg = errorData.detail[0]?.msg || JSON.stringify(errorData.detail[0]);
          } else if (errorData.detail) {
            msg = JSON.stringify(errorData.detail);
          }
          throw new Error(msg || `HTTP Error ${response.status}`);
        }

        // Cache working base URL for subsequent requests
        activeApiBaseUrl = candidate;
        return await response.json();
      } catch (err) {
        lastError = err;
        if (err.name === "TypeError" || err.message.includes("fetch") || err.message.includes("Failed to fetch")) {
          if (attempt < retries - 1) {
            await new Promise((r) => setTimeout(r, 500));
            continue;
          }
        } else {
          // Non-fetch error (e.g. 400 Bad Request, 401, 422 validation error) — don't try next port
          throw err;
        }
      }
    }
  }
  throw lastError || new Error("Failed to communicate with server");
}

const api = {
  // Auth
  login: (data) =>
    request("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  register: (data) =>
    request("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getMe: () => request("/auth/me"),

  // Chats
  listChats: (search) =>
    request(`/chats${search ? `?search=${encodeURIComponent(search)}` : ""}`),

  getChat: (chatId) => request(`/chats/${chatId}`),

  createChat: (data) =>
    request("/chats", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  deleteChat: (chatId) =>
    request(`/chats/${chatId}`, {
      method: "DELETE",
    }),

  sendMessage: (data) =>
    request("/chats/messages", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Documents
  uploadDocument: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return request("/documents/upload", {
      method: "POST",
      body: formData,
    });
  },

  listDocuments: () => request("/documents"),

  deleteDocument: (documentId) =>
    request(`/documents/${documentId}`, {
      method: "DELETE",
    }),

  searchChunks: (query, limit = 5) =>
    request(`/documents/search?query=${encodeURIComponent(query)}&limit=${limit}`),

  // Agents
  listAgents: () => request("/agents"),

  // Dashboard
  getStats: () => request("/dashboard/stats"),

  // Settings
  getSettings: () => request("/settings"),

  updateSettings: (data) =>
    request("/settings", {
      method: "PUT",
      body: JSON.stringify(data),
    }),
};

// Make accessible globally on window object
window.getAuthToken = getAuthToken;
window.setAuthToken = setAuthToken;
window.removeAuthToken = removeAuthToken;
window.api = api;
