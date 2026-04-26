/**
 * Dekho API Client
 * Centralized HTTP client for all backend calls.
 * Uses the Vite proxy in dev (/api -> http://localhost:8000)
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? `http://${window.location.hostname}:8000`

interface ApiOptions extends RequestInit {
  params?: Record<string, string | number | boolean>
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

  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...fetchOptions.headers,
    },
    ...fetchOptions,
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(error || `HTTP ${response.status}`)
  }

  return response.json()
}

export const api = {
  get: <T>(endpoint: string, params?: Record<string, string | number | boolean>) =>
    request<T>(endpoint, { method: 'GET', params }),

  post: <T>(endpoint: string, body: unknown) =>
    request<T>(endpoint, { method: 'POST', body: JSON.stringify(body) }),

  put: <T>(endpoint: string, body: unknown) =>
    request<T>(endpoint, { method: 'PUT', body: JSON.stringify(body) }),

  delete: <T>(endpoint: string) =>
    request<T>(endpoint, { method: 'DELETE' }),
}

export default api
