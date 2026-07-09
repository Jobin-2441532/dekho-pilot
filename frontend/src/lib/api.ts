/**
 * Dekho API Client
 * Centralised HTTP client for all backend calls.
 * Automatically attaches JWT Bearer token from localStorage.
 * Uses the Vite proxy in dev (/api → http://localhost:8000)
 */
const BASE_URL = import.meta.env.PROD ? (import.meta.env.VITE_API_URL || '') : ''

interface ApiOptions extends RequestInit {
  params?: Record<string, string | number | boolean>
}

/** Get the stored JWT token */
function getToken(): string | null {
  return localStorage.getItem('dekho_token')
}

/** Clear auth state and redirect to login */
export function logout(): void {
  localStorage.removeItem('dekho_token')
  localStorage.removeItem('dekho_onboarded')
  window.location.href = '/login'
}

async function request<T>(endpoint: string, options: ApiOptions = {}): Promise<T> {
  const { params, ...fetchOptions } = options

  let url = `${BASE_URL}${endpoint}`
  if (params) {
    const searchParams = new URLSearchParams(
      Object.entries(params).map(([k, v]) => [k, String(v)])
    )
    url += `?${searchParams}`
  }

  // Inject JWT token automatically
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(fetchOptions.headers as Record<string, string>),
  }
  if (token) headers['Authorization'] = `Bearer ${token}`



  const response = await fetch(url, {
    ...fetchOptions,
    headers,
  })

  // Auto-logout on 401 (token expired / invalid)
  if (response.status === 401) {
    logout()
    throw new Error('Session expired. Please log in again.')
  }

  if (!response.ok) {
    const error = await response.text()
    throw new Error(error || `HTTP ${response.status}`)
  }

  return response.json()
}

const CACHE_KEY_PREFIX = 'dekho_cache_';
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

const getCache = (key: string) => {
  try {
    const item = localStorage.getItem(CACHE_KEY_PREFIX + key);
    if (item) {
      const parsed = JSON.parse(item);
      if (Date.now() - parsed.timestamp < CACHE_DURATION) {
        return parsed.data;
      }
    }
  } catch (e) {}
  return null;
}

const setCache = (key: string, data: any) => {
  try {
    localStorage.setItem(CACHE_KEY_PREFIX + key, JSON.stringify({ data, timestamp: Date.now() }));
  } catch (e) {}
}

const clearCache = () => {
  try {
    const keysToRemove = [];
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i);
      if (k?.startsWith(CACHE_KEY_PREFIX)) {
        keysToRemove.push(k);
      }
    }
    keysToRemove.forEach(k => localStorage.removeItem(k));
  } catch (e) {}
}

export const api = {
  get: async <T>(endpoint: string, params?: Record<string, string | number | boolean>) => {
    const key = endpoint + JSON.stringify(params || {});
    const cached = getCache(key);
    if (cached) {
      return cached as T;
    }
    const res = await request<T>(endpoint, { method: 'GET', params });
    setCache(key, res);
    return res;
  },

  post: <T>(endpoint: string, body: unknown) => {
    clearCache();
    return request<T>(endpoint, { method: 'POST', body: JSON.stringify(body) });
  },

  put: <T>(endpoint: string, body: unknown) => {
    clearCache();
    return request<T>(endpoint, { method: 'PUT', body: JSON.stringify(body) });
  },

  patch: <T>(endpoint: string, body: unknown) => {
    clearCache();
    return request<T>(endpoint, { method: 'PATCH', body: JSON.stringify(body) });
  },

  delete: <T>(endpoint: string) => {
    clearCache();
    return request<T>(endpoint, { method: 'DELETE' });
  },
}

export default api
