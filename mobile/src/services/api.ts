/**
 * API Service
 * HTTP client for backend API communication
 */
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// API Base URL - Update with your backend URL
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
      await AsyncStorage.removeItem('authToken');
      // TODO: Navigate to login screen
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  register: (email: string, password: string) =>
    apiClient.post('/auth/register', { email, password }),

  login: (email: string, password: string) =>
    apiClient.post('/auth/login', { email, password }),

  getProfile: () => apiClient.get('/auth/me'),

  updateProfile: (data: any) => apiClient.put('/auth/profile', data),

  deleteAccount: () => apiClient.delete('/auth/account'),
};

// Food API (Mode 1)
export const foodApi = {
  uploadFood: (formData: FormData) =>
    apiClient.post('/food/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      params: {
        hrv: 60.0, // TODO: Get from HealthKit
        heart_rate: 75, // TODO: Get from HealthKit
      },
    }),

  getHistory: (limit = 10) =>
    apiClient.get('/food/history', { params: { limit } }),
};

// Fridge API (Mode 2)
export const fridgeApi = {
  detectIngredients: (formData: FormData) =>
    apiClient.post('/fridge/detect', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      params: {
        hrv: 60.0, // TODO: Get from HealthKit
        heart_rate: 75, // TODO: Get from HealthKit
      },
    }),

  getRecipe: (recipeId: string) => apiClient.get(`/fridge/recipes/${recipeId}`),
};

// Wellness API (Mode 3)
export const wellnessApi = {
  check: () =>
    apiClient.get('/wellness/check', {
      params: {
        hrv: 60.0, // TODO: Get from HealthKit
        heart_rate: 75, // TODO: Get from HealthKit
      },
    }),

  getHistory: (days = 7) =>
    apiClient.get('/wellness/history', { params: { days } }),

  getTrends: (period = 'week') =>
    apiClient.get('/wellness/trends', { params: { period } }),
};

export default apiClient;
