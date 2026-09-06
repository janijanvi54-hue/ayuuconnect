import axios from "axios";

// Axios instance shared by the whole SPA.
// Base URL can be overridden at build time with VITE_API_BASE_URL.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  headers: { "Content-Type": "application/json" },
  withCredentials: true,
});

// Attach the JWT when present (Phase 3 wires real login).
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("ayuconnect_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Uniform handling of auth failures.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem("ayuconnect_token");
      localStorage.removeItem("ayuconnect_user");
      if (!window.location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;