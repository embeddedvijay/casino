const HOST = window.location.hostname;
const API = `http://${HOST}:8005`;

export async function api(path, options = {}) {
  const token = localStorage.getItem("casino_admin_token");

  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });

  const data = await response.json().catch(() => ({}));

  if (response.status === 401) {
    localStorage.removeItem("casino_admin_token");
    throw new Error(data.detail || "Session expired. Login again.");
  }

  if (!response.ok) {
    throw new Error(data.detail || "Request failed.");
  }

  return data;
}