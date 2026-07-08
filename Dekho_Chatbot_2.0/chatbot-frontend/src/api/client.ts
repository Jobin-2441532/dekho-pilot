import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8001'

export const api = axios.create({ baseURL: BASE, timeout: 15000 })

export const STREAM_URL = `${BASE}/api/chat/stream`
export const CHAT_URL   = `${BASE}/api/chat`

// ── Feedback API ──────────────────────────────────────────────────────────────

export interface FeedbackPayload {
  user_id: string
  session_id: string
  message_id: string
  rating: 'up' | 'down'
  correction?: string
  intent?: string
}

export async function submitFeedback(payload: FeedbackPayload): Promise<void> {
  try {
    await api.post('/api/chat/feedback', payload)
  } catch {
    // Feedback errors are non-critical — fail silently
  }
}

// ── Last-session restore API ──────────────────────────────────────────────────

export interface StoredMessage {
  role: 'user' | 'assistant'
  content: string
  intent?: string
  timestamp: string
}

export interface LastSessionResponse {
  user_id: string
  session_id: string | null
  messages: StoredMessage[]
}

export async function fetchLastSession(userId: string): Promise<LastSessionResponse | null> {
  try {
    const { data } = await api.get<LastSessionResponse>(`/api/chat/last-session/${userId}`)
    return data
  } catch {
    return null
  }
}

