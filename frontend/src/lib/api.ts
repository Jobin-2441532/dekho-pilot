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

const cache = new Map<string, { data: any, timestamp: number }>();
const CACHE_DURATION = 60 * 1000; // 60 seconds
const clearCache = () => cache.clear();

export const api = {
  get: async <T>(endpoint: string, params?: Record<string, string | number | boolean>) => {
    const key = endpoint + JSON.stringify(params || {});
    const cached = cache.get(key);
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      return cached.data as T;
    }
    const res = await request<T>(endpoint, { method: 'GET', params });
    cache.set(key, { data: res, timestamp: Date.now() });
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
