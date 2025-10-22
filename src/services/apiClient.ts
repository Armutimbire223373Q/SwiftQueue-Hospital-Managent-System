import axios from 'axios';
import { authService } from './authService';

// API base URL is configurable via Vite env var VITE_API_URL.
// Set VITE_API_URL to e.g. "http://localhost:8000" or "http://localhost:8001" in a .env file.
// The value may include the `/api` suffix; we normalize below to ensure a trailing `/api`.
const _VITE_API = (import.meta as any).env?.VITE_API_URL as string | undefined;
const _DEFAULT_API = 'http://localhost:8001';
const rawBase = (_VITE_API && _VITE_API.length > 0) ? _VITE_API : _DEFAULT_API;
const API_BASE_URL = rawBase.endsWith('/api') ? rawBase : `${rawBase.replace(/\/+$/, '')}/api`;

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // Add timeout
});

// Add request logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`apiClient: Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('apiClient: Request error:', error);
    return Promise.reject(error);
  }
);

// Add response logging
apiClient.interceptors.response.use(
  (response) => {
    console.log(`apiClient: Response from ${response.config.url}:`, response.status, response.data);
    return response;
  },
  (error) => {
    console.error(`apiClient: Response error from ${error.config?.url}:`, error.response?.status, error.message);
    return Promise.reject(error);
  }
);

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = authService.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Try to refresh token
        await authService.refreshToken();

        // Retry the original request with new token
        const newToken = authService.getToken();
        if (newToken) {
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        authService.logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;