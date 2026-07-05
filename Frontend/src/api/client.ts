import axios from 'axios';
import { logger } from '../utils/logger';

export const apiClient = axios.create({
  // Dev: falls back to the same-origin "/api" proxy (see vite.config.ts), which
  // forwards to the root-mounted FastAPI backend. Prod: set VITE_API_URL to the
  // backend's base URL (root — the backend has no /api or /api/v1 prefix).
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    logger.error('Request interceptor error', error);
    return Promise.reject(error);
  }
);

// Response Interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // Handle standardized error format
      logger.error('API Error', error.response.data);
      if (error.response.status === 401) {
        // Handle unauthorized (e.g., redirect to login)
      }
    } else if (error.request) {
      logger.error('Network Error - No response received', error.request);
    } else {
      logger.error('Error setting up request', error.message);
    }
    return Promise.reject(error);
  }
);
