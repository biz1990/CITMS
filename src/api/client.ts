import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { v4 as uuidv4 } from 'uuid';
import { useAuthStore } from '@/store/useAuthStore';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Auth & Tracing
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // OpenTelemetry Trace ID for backend correlation
    config.headers['X-Trace-Id'] = uuidv4();
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Global Error Handling (RFC 7807) & Token Refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any;
    const { response } = error;
    
    // Handle 401 Unauthorized - Token Expiration
    if (response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = useAuthStore.getState().refreshToken;
      
      if (refreshToken) {
        try {
          // Attempt to refresh token
          const refreshResponse = await axios.post(`${apiClient.defaults.baseURL}/auth/refresh`, {
            refresh_token: refreshToken
          });
          
          const { access_token, refresh_token: newRefreshToken } = refreshResponse.data;
          
          // Update store
          useAuthStore.getState().setTokens(access_token, newRefreshToken);
          
          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        } catch (refreshError) {
          // Refresh failed - logout
          useAuthStore.getState().logout();
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token - logout
        useAuthStore.getState().logout();
        window.location.href = '/login';
      }
    }
    
    // RFC 7807 Error Structure
    const rfcError = response?.data as any;
    const errorMessage = rfcError?.detail || rfcError?.title || 'An unexpected error occurred';
    
    console.error(`[API Error] ${response?.status}: ${errorMessage}`, rfcError);
    
    return Promise.reject({
      ...error,
      message: errorMessage,
      rfc7807: rfcError,
    });
  }
);

export default apiClient;
