import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios';
import { AUTH_TOKEN_KEY } from '../utils/constants';

/**
 * Singleton Axios instance for all API calls.
 *
 * Responsibilities (SRP):
 *  - Attach Authorization header on every request
 *  - Redirect to /login on 401 responses
 *
 * Base URL is intentionally empty: Vite proxy (dev) and Nginx (prod)
 * forward /api/* to the .NET backend, avoiding CORS issues.
 */
const apiClient = axios.create({
  baseURL: '',
  headers: { 'Content-Type': 'application/json' },
});

/** Request interceptor — inject JWT Bearer token if present */
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  try {
    const storageStr = localStorage.getItem(AUTH_TOKEN_KEY);
    if (storageStr) {
      const parsed = JSON.parse(storageStr);
      const token = parsed?.state?.token;
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
  } catch (e) {
    // Ignore JSON parse errors gracefully
  }
  return config;
});

/** Response interceptor — handle 401 Unauthorized globally */
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear stale auth state and redirect to login
      localStorage.removeItem(AUTH_TOKEN_KEY);
      window.location.href = '/login';
    }
    return Promise.reject(error);
  },
);

export default apiClient;
