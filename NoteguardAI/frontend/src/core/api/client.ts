import axios from "axios";

const getApiBaseUrl = () => {
  if (typeof import.meta !== "undefined" && import.meta.env?.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  if (typeof import.meta !== "undefined" && import.meta.env?.NEXT_PUBLIC_API_URL) {
    return import.meta.env.NEXT_PUBLIC_API_URL;
  }
  if (typeof process !== "undefined" && process.env?.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  return "http://localhost:8000/api/v1";
};

const API_BASE_URL = getApiBaseUrl();

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Request interceptor to automatically add Authorization header and handle FormData
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // Let browser/Axios compute multipart/form-data with proper boundary for FormData
    if (config.data instanceof FormData) {
      delete config.headers["Content-Type"];
    } else if (!config.headers["Content-Type"]) {
      config.headers["Content-Type"] = "application/json";
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh and automatic logouts
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Check if error is 401 and request was not already a retry attempt
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = localStorage.getItem("refresh_token");
      if (refreshToken) {
        try {
          const refreshUrl = `${API_BASE_URL}/auth/refresh`;
          const res = await axios.post(refreshUrl, {
            refresh_token: refreshToken,
          });
          
          if (res.data?.success) {
            const newAccessToken = res.data.data.access_token;
            const newRefreshToken = res.data.data.refresh_token;
            
            localStorage.setItem("access_token", newAccessToken);
            if (newRefreshToken) {
              localStorage.setItem("refresh_token", newRefreshToken);
            }
            
            // Retry the original failed request
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
            return apiClient(originalRequest);
          }
        } catch (refreshError) {
          // Token refresh failed, logout session
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          localStorage.removeItem("user_profile");
          window.location.href = "/login";
        }
      } else {
        // No refresh token, force redirect to login
        localStorage.removeItem("access_token");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
