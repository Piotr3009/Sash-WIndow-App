const API_BASE = "/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    const message = detail?.detail || response.statusText;
    throw new Error(message || "Wystąpił błąd połączenia z API");
  }

  return response.json();
}

export async function calculateProject(payload) {
  return request("/calculate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function exportProject(format, payload) {
  return request(`/export/${format}`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function downloadUrl(fileId) {
  return `${API_BASE}/download/${fileId}`;
}
