const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(fetchOptions.headers as Record<string, string>),
  }

  const adminUser = sessionStorage.getItem('dekho_admin_user')
  const adminPass = sessionStorage.getItem('dekho_admin_pass')
  if (adminUser && adminPass) {
    headers['X-Admin-User'] = adminUser
    headers['X-Admin-Pass'] = adminPass
  }

  const response = await fetch(url, {
    ...fetchOptions,
    headers,
  })

  if (!response.ok) {
    const errorBody = await response.text()
    throw new Error(`API Error ${response.status}: ${errorBody}`)
  }
  
  if (response.status === 204) {
    return {} as T
  }
  return response.json()
}

export default {
  get: <T>(url: string, params?: Record<string, any>) => request<T>(url, { method: 'GET', params }),
  post: <T>(url: string, body?: any) => request<T>(url, { method: 'POST', body: body ? JSON.stringify(body) : undefined }),
  put: <T>(url: string, body?: any) => request<T>(url, { method: 'PUT', body: body ? JSON.stringify(body) : undefined }),
  patch: <T>(url: string, body?: any) => request<T>(url, { method: 'PATCH', body: body ? JSON.stringify(body) : undefined }),
  delete: <T>(url: string) => request<T>(url, { method: 'DELETE' })
}
