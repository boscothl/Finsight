import axios, { AxiosHeaders } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Use EXPO_PUBLIC_API_BASE_URL for device testing.
// Example for iOS physical device: http://192.168.1.100:8000/api
const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';
const ACCESS_TOKEN_KEY = 'finsight_access_token';
const REFRESH_TOKEN_KEY = 'finsight_refresh_token';
let refreshPromise: Promise<string | null> | null = null;

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const saveTokens = async (access: string, refresh: string) => {
  await AsyncStorage.multiSet([
    [ACCESS_TOKEN_KEY, access],
    [REFRESH_TOKEN_KEY, refresh],
  ]);
};

export const clearTokens = async () => {
  await AsyncStorage.multiRemove([ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY]);
};

export const getAccessToken = async () => AsyncStorage.getItem(ACCESS_TOKEN_KEY);
export const getRefreshToken = async () => AsyncStorage.getItem(REFRESH_TOKEN_KEY);

export const login = async (username: string, password: string) => {
  const response = await api.post('/auth/login/', { username, password });
  const { access, refresh } = response.data;
  await saveTokens(access, refresh);
  return response.data;
};

const refreshAccessToken = async (): Promise<string | null> => {
  const refresh = await getRefreshToken();
  if (!refresh) {
    return null;
  }

  try {
    const response = await api.post('/auth/refresh/', { refresh });
    const nextAccess = response.data?.access;
    if (!nextAccess) {
      return null;
    }
    await AsyncStorage.setItem(ACCESS_TOKEN_KEY, nextAccess);
    return nextAccess;
  } catch {
    await clearTokens();
    return null;
  }
};

api.interceptors.request.use(async (config) => {
  const token = await getAccessToken();
  if (token) {
    const headers = AxiosHeaders.from(config.headers);
    headers.set('Authorization', `Bearer ${token}`);
    config.headers = headers;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error?.config;
    const status = error?.response?.status;

    if (status !== 401 || !originalRequest || originalRequest._retry) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    if (!refreshPromise) {
      refreshPromise = refreshAccessToken();
    }

    const nextAccess = await refreshPromise;
    refreshPromise = null;

    if (!nextAccess) {
      return Promise.reject(error);
    }

    const retryHeaders = AxiosHeaders.from(originalRequest.headers);
    retryHeaders.set('Authorization', `Bearer ${nextAccess}`);
    originalRequest.headers = retryHeaders;

    return api(originalRequest);
  }
);

export const fetchHomeData = async () => {
  const response = await api.get('/mobile/home/');
  return response.data;
};

export const fetchBudgetPools = async () => {
  const response = await api.get('/mobile/budget-pools/');
  return response.data;
};

export const fetchClaims = async () => {
  const response = await api.get('/mobile/claims/');
  return response.data;
};

export const uploadReceipt = async (imageUri: string) => {
  try {
    const formData: any = new FormData();
    formData.append('receipt', {
      uri: imageUri,
      name: 'receipt.jpg',
      type: 'image/jpeg',
    });

    const response = await api.post('/mobile/upload-receipt/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 120000, // Explicitly set longer timeout for upload
    });
    
    return response.data;
  } catch (error) {
    console.error('Error uploading receipt:', error);
    throw error;
  }
};

export const sendComplianceQuestion = async (query: string) => {
  const response = await api.post('/chat/compliance/', { query });
  return response.data;
};

export const fetchBudgetPools = async () => {
  const response = await api.get('/mobile/budget-pools/');
  return response.data;
};

export const submitClaimData = async (claimData: any) => {
  const response = await api.post('/mobile/claims/', claimData);
  return response.data;
};

export default api;

export const logout = async () => {
  await AsyncStorage.multiRemove([ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY]);
};
