import React, { useRef, useEffect } from 'react'
import { Send, Trash2, Bug, ChevronDown } from 'lucide-react'
import { useUserStore, useUIStore, useChatStore } from '../store'

const MOCK_USERS = [
  { id: 'user_priya', name: 'Priya' },
  { id: 'user_arjun', name: 'Arjun' },
  { id: 'user_meera', name: 'Meera' },
]

const PRESET_QUERIES = [
  'How am I doing this month?',
  'How much did I spend on food?',
  'Am I over budget?',
  'How\'s my vacation fund?',
  'Anything unusual in my spending?',
  'How can I save more?',
  'Compare this month to last month',
  'I spent ₹500 at Zomato',
]

interface Props {
  onSend: (text: string) => void
  isLoading: boolean
}

export function ChatHeader({ onSend, isLoading }: Props) {
  const { userId, userName, setUser } = useUserStore()
  const { toggleDebug, togglePresets } = useUIStore()
  const { clearChat, switchUser, persistHistory } = useChatStore()

  return (
    <header className="chat-header">
      <div className="chat-header__brand">
        <div className="chat-header__avatar">🧭</div>
        <div>
          <div className="chat-header__name">Dekho</div>
          <div className="chat-header__subtitle">Online · {userName}</div>
        </div>
      </div>

      <div className="chat-header__actions">
        <select
          className="user-switcher"
          value={userId}
          onChange={(e) => {
            const u = MOCK_USERS.find(u => u.id === e.target.value)
            if (u) {
              // Save current user's history before switching
              persistHistory(userId)
              setUser(u.id, u.name)
              // Restore the new user's saved history (or start fresh)
              switchUser(u.id)
            }
          }}
          title="Switch test user"
        >
          {MOCK_USERS.map(u => (
            <option key={u.id} value={u.id}>{u.name}</option>
          ))}
        </select>

        <button className="icon-btn" onClick={togglePresets} title="Toggle preset queries">
          <ChevronDown size={16} />
        </button>

        <button className="icon-btn" onClick={toggleDebug} title="Toggle debug panel">
          <Bug size={16} />
        </button>

        <button className="icon-btn" onClick={clearChat} title="Clear chat">
          <Trash2 size={16} />
        </button>
      </div>
    </header>
  )
}

export function PresetQueries({ onSend }: { onSend: (t: string) => void }) {
  const { showPresets } = useUIStore()
  if (!showPresets) return null
  return (
    <div className="preset-queries">
      {PRESET_QUERIES.map(q => (
        <button key={q} className="preset-btn" onClick={() => onSend(q)}>
          {q}
        </button>
      ))}
    </div>
  )
}

export function ChatInputBar({ onSend, isLoading }: Props) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSend = () => {
    const val = textareaRef.current?.value.trim()
    if (!val || isLoading) return
    onSend(val)
    if (textareaRef.current) textareaRef.current.value = ''
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleInput = () => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 120) + 'px'
  }

  return (
    <div className="chat-input-bar">
      <div className="chat-input-wrap">
        <textarea
          ref={textareaRef}
          placeholder="Ask me about your spending, goals, or budget…"
          onKeyDown={handleKeyDown}
          onInput={handleInput}
          rows={1}
          disabled={isLoading}
        />
        <button className="send-btn" onClick={handleSend} disabled={isLoading}>
          <Send size={16} />
        </button>
      </div>
    </div>
  )
}

export function DebugPanel() {
  const { showDebug } = useUIStore()
  const { debugInfo } = useChatStore()
  if (!showDebug) return null

  return (
    <aside className="debug-panel">
      <h3>🔍 Debug Panel</h3>
      {debugInfo ? (
        <>
          <div className="debug-field">
            <div className="debug-label">Intent</div>
            <div className="debug-value" style={{ color: '#F4A261', fontWeight: 600 }}>{debugInfo.intent}</div>
          </div>
          <div className="debug-field">
            <div className="debug-label">Latency</div>
            <div className="debug-value">{debugInfo.latencyMs}ms</div>
          </div>
          <div className="debug-field">
            <div className="debug-label">Session ID</div>
            <code className="debug-value debug-value--code">{debugInfo.sessionId}</code>
          </div>
        </>
      ) : (
        <div style={{ color: 'var(--text-muted)', fontSize: 12 }}>Send a message to see debug info</div>
      )}
    </aside>
  )
}

export function AlertBanner() {
  const { activeAlert, setAlert } = useChatStore()
  if (!activeAlert) return null

  return (
    <div className={`alert-banner alert-banner--${activeAlert.severity}`}>
      <span style={{ flex: 1 }}>{activeAlert.message}</span>
      <button className="alert-banner__dismiss" onClick={() => setAlert(null)}>✕</button>
    </div>
  )
}

export function EmptyState({ onSend }: { onSend: (t: string) => void }) {
  const { userName } = useUserStore()
  const starters = [
    'How am I doing this month? 📊',
    'Check my budget 💰',
    'View my goals 🎯',
    'Any unusual spending? 🔍',
  ]
  return (
    <div className="empty-state">
      <div className="empty-state__emoji">🧭</div>
      <div className="empty-state__title">Hey {userName}! I'm Dekho</div>
      <div className="empty-state__subtitle">
        Your personal finance companion. Ask me anything about your spending, goals, or budget.
      </div>
      <div className="empty-state__chips">
        {starters.map(s => (
          <button key={s} className="chip" onClick={() => onSend(s)}>{s}</button>
        ))}
      </div>
    </div>
  )
}
