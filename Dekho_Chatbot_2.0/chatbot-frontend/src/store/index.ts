import { create } from 'zustand'

export type Role = 'user' | 'assistant'

export interface ChartData {
  type: 'pie' | 'bar' | 'line' | 'progress'
  title: string
  data: Record<string, unknown>[]
  config?: Record<string, unknown>
}

export interface AlertPayload {
  type: string
  message: string
  severity: 'info' | 'warning' | 'critical'
}

export interface Message {
  id: string
  role: Role
  content: string
  intent?: string
  chart?: ChartData
  quickReplies?: string[]
  timestamp: Date
  isStreaming?: boolean
  isFallback?: boolean
}

export interface DebugInfo {
  intent: string
  confidence: number
  latencyMs: number
  sessionId: string
}

// ── Per-user conversation persistence ─────────────────────────────────────────

const STORAGE_KEY = 'dekho_chat_history'

/** Serialize messages to localStorage (strip streaming state, convert Date to ISO) */
function saveHistory(userId: string, messages: Message[], sessionId: string) {
  try {
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')
    stored[userId] = {
      sessionId,
      messages: messages
        .filter((m) => !m.isStreaming)
        .map((m) => ({ ...m, timestamp: m.timestamp.toISOString() })),
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(stored))
  } catch {
    // localStorage may be full or unavailable — fail silently
  }
}

/** Load saved messages for a user, rehydrating timestamps */
function loadHistory(userId: string): { messages: Message[]; sessionId: string } | null {
  try {
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')
    const entry = stored[userId]
    if (!entry) return null
    return {
      sessionId: entry.sessionId,
      messages: (entry.messages as Array<Message & { timestamp: string }>).map((m) => ({
        ...m,
        timestamp: new Date(m.timestamp),
      })),
    }
  } catch {
    return null
  }
}

// ── Chat Store ─────────────────────────────────────────────────────────────────

const genId = () => Math.random().toString(36).slice(2, 10)

interface ChatState {
  messages: Message[]
  sessionId: string
  isLoading: boolean
  streamingId: string | null
  debugInfo: DebugInfo | null
  activeAlert: AlertPayload | null

  // Actions
  addMessage: (msg: Message) => void
  updateStreamingMessage: (id: string, token: string) => void
  finalizeMessage: (id: string, extras: Partial<Message>) => void
  setLoading: (v: boolean) => void
  setStreamingId: (id: string | null) => void
  setDebugInfo: (info: DebugInfo) => void
  setAlert: (alert: AlertPayload | null) => void
  clearChat: () => void
  newSessionId: () => void
  /** Load saved conversation for a user, or start fresh if none exists */
  switchUser: (userId: string) => Promise<void>
  /** Persist current messages to localStorage for the given userId */
  persistHistory: (userId: string) => void
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  sessionId: genId(),
  isLoading: false,
  streamingId: null,
  debugInfo: null,
  activeAlert: null,

  addMessage: (msg) =>
    set((s) => ({ messages: [...s.messages, msg] })),

  updateStreamingMessage: (id, token) =>
    set((s) => ({
      messages: s.messages.map((m) =>
        m.id === id ? { ...m, content: m.content + token } : m,
      ),
    })),

  finalizeMessage: (id, extras) =>
    set((s) => ({
      messages: s.messages.map((m) =>
        m.id === id ? { ...m, ...extras, isStreaming: false } : m,
      ),
    })),

  setLoading: (v) => set({ isLoading: v }),
  setStreamingId: (id) => set({ streamingId: id }),
  setDebugInfo: (info) => set({ debugInfo: info }),
  setAlert: (alert) => set({ activeAlert: alert }),

  clearChat: () =>
    set({ messages: [], activeAlert: null, debugInfo: null, sessionId: genId() }),

  newSessionId: () => set({ sessionId: genId() }),

  persistHistory: (userId) => {
    const { messages, sessionId } = get()
    saveHistory(userId, messages, sessionId)
  },

  switchUser: async (userId) => {
    const saved = loadHistory(userId)
    if (saved) {
      set({
        messages: saved.messages,
        sessionId: saved.sessionId,
        activeAlert: null,
        debugInfo: null,
        isLoading: false,
        streamingId: null,
      })
    } else {
      // Fallback: try fetching from backend DB
      try {
        const res = await fetch(`http://localhost:8001/api/chat/last-session/${userId}`)
        if (res.ok) {
          const data = await res.json()
          if (data.messages && data.messages.length > 0) {
            const rehydrated = data.messages.map((m: Record<string, unknown>) => ({
              id: String(Math.random()),
              role: m.role,
              content: m.content,
              intent: m.intent,
              timestamp: new Date(m.timestamp as string),
            }))
            set({
              messages: rehydrated,
              sessionId: data.session_id || genId(),
              activeAlert: null,
              debugInfo: null,
              isLoading: false,
              streamingId: null,
            })
            return
          }
        }
      } catch { /* ignore — start fresh */ }
      set({
        messages: [],
        sessionId: genId(),
        activeAlert: null,
        debugInfo: null,
        isLoading: false,
        streamingId: null,
      })
    }
  },
}))

// ── User Store ─────────────────────────────────────────────────────────────────

interface UserState {
  userId: string
  userName: string
  setUser: (id: string, name: string) => void
}

export const useUserStore = create<UserState>((set) => ({
  userId: 'user_priya',
  userName: 'Priya',
  setUser: (id, name) => set({ userId: id, userName: name }),
}))

// ── UI Store ───────────────────────────────────────────────────────────────────

interface UIState {
  showDebug: boolean
  showPresets: boolean
  toggleDebug: () => void
  togglePresets: () => void
}

export const useUIStore = create<UIState>((set) => ({
  showDebug: false,
  showPresets: true,
  toggleDebug: () => set((s) => ({ showDebug: !s.showDebug })),
  togglePresets: () => set((s) => ({ showPresets: !s.showPresets })),
}))
