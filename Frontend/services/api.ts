import axios, { AxiosError } from "axios";
import { API_BASE_URL } from "@/lib/constants";
import { ApiError } from "@/types";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
  headers: { "Content-Type": "application/json" },
});

// ── Request interceptor — attach Bearer token ─────────────────
api.interceptors.request.use((config) => {
  // Dynamically read from localStorage so store hydration isn't required
  try {
    const raw = localStorage.getItem("mockiq-auth");
    if (raw) {
      const parsed = JSON.parse(raw);
      const token = parsed?.state?.accessToken;
      if (token) {
        config.headers["Authorization"] = `Bearer ${token}`;
      }
    }
  } catch {
    // ignore parse errors
  }
  return config;
});

// ── Response interceptor — token refresh + error normalisation ─
let _isRefreshing = false;
let _refreshQueue: Array<(token: string) => void> = [];

api.interceptors.response.use(
  (res) => res,
  async (error: AxiosError<ApiError>) => {
    const originalRequest = error.config as typeof error.config & { _retry?: boolean };

    // Attempt token refresh on 401 (but not for auth endpoints themselves)
    if (
      error.response?.status === 401 &&
      !originalRequest?._retry &&
      originalRequest?.url &&
      !originalRequest.url.includes("/auth/")
    ) {
      if (_isRefreshing) {
        // Queue this request until refresh completes
        return new Promise((resolve) => {
          _refreshQueue.push((newToken: string) => {
            if (originalRequest.headers) {
              originalRequest.headers["Authorization"] = `Bearer ${newToken}`;
            }
            resolve(api(originalRequest));
          });
        });
      }

      originalRequest._retry = true;
      _isRefreshing = true;

      try {
        const raw = localStorage.getItem("mockiq-auth");
        const refreshToken = raw ? JSON.parse(raw)?.state?.refreshToken : null;

        if (!refreshToken) throw new Error("No refresh token");

        const { data } = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        // Update tokens in store
        const { useAuthStore } = await import("@/store/authStore");
        useAuthStore.getState().setAuth(data.user, data.access_token, data.refresh_token);

        // Drain queue
        _refreshQueue.forEach((cb) => cb(data.access_token));
        _refreshQueue = [];

        // Retry original request
        if (originalRequest.headers) {
          originalRequest.headers["Authorization"] = `Bearer ${data.access_token}`;
        }
        return api(originalRequest);
      } catch {
        // Refresh failed — clear auth and redirect to login
        const { useAuthStore } = await import("@/store/authStore");
        useAuthStore.getState().clearAuth();
        _refreshQueue = [];
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
        return Promise.reject(new Error("Session expired. Please log in again."));
      } finally {
        _isRefreshing = false;
      }
    }

    // Normalise all other errors
    const msg =
      error.response?.data?.message ||
      error.message ||
      "An unexpected error occurred.";
    const code = error.response?.data?.error_code || "NETWORK_ERROR";
    const enriched = new Error(msg) as Error & { errorCode: string; status: number };
    enriched.errorCode = code;
    enriched.status = error.response?.status ?? 0;
    return Promise.reject(enriched);
  }
);

export default api;
