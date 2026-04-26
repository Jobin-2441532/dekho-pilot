import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Send, Sparkles } from 'lucide-react'
import { useAppStore } from '../../store/appStore'
import ChatBubble from './ChatBubble'
import styles from './ChatPanel.module.css'

interface Message {
  role: 'user' | 'assistant'
  content: string
  id?: string
  timestamp?: string
}

const WELCOME: Message = {
  role: 'assistant',
  content:
    "Hey! 👋 I'm Dekho, your finance buddy. Ask me anything about your spending, savings, or goals — I'm here to help! 💸",
  id: 'welcome',
  timestamp: new Date().toISOString(),
}

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export default function ChatPanel() {
  const { isChatOpen, closeChat } = useAppStore()
  const [messages, setMessages] = useState<Message[]>([WELCOME])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Scroll to bottom on new message
  useEffect(() => {
    if (isChatOpen) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, isChatOpen])

  // Focus input when panel opens
  useEffect(() => {
    if (isChatOpen) {
      setTimeout(() => inputRef.current?.focus(), 350)
    }
  }, [isChatOpen])

  const sendMessage = async () => {
    const text = input.trim()
    if (!text || isLoading) return

    const userMsg: Message = {
      role: 'user',
      content: text,
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setIsLoading(true)

    try {
      const history = [...messages, userMsg].map(({ role, content, id, timestamp }) => ({
        role,
        content,
        id: id ?? crypto.randomUUID(),
        timestamp: timestamp ?? new Date().toISOString(),
      }))

      const res = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: history }),
      })

      if (!res.ok) throw new Error(`HTTP ${res.status}`)

      const data = await res.json()
      const assistantMsg: Message = {
        role: 'assistant',
        content: data.message.content,
        id: data.message.id,
        timestamp: data.message.timestamp,
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content:
            "Hmm, I couldn't connect to the backend right now. Make sure the server is running! 🛑",
          id: crypto.randomUUID(),
          timestamp: new Date().toISOString(),
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const QUICK_PROMPTS = [
    'How much did I spend this month?',
    'What are my top spending categories?',
    'How are my savings goals doing?',
    'Am I on budget?',
  ]

  return (
    <AnimatePresence>
      {isChatOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className={styles.backdrop}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={closeChat}
            aria-hidden="true"
          />

          {/* Panel */}
          <motion.div
            className={styles.panel}
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            role="dialog"
            aria-label="Ask Dekho chatbot"
            aria-modal="true"
          >
            {/* Header */}
            <div className={styles.header}>
              <div className={styles.headerLeft}>
                <div className={styles.avatar}>
                  <Sparkles size={16} strokeWidth={2} />
                </div>
                <div>
                  <p className={styles.headerTitle}>Ask Dekho</p>
                  <p className={styles.headerSubtitle}>Your AI finance buddy</p>
                </div>
              </div>
              <button
                className={styles.closeBtn}
                onClick={closeChat}
                aria-label="Close chat"
              >
                <X size={18} strokeWidth={2} />
              </button>
            </div>

            {/* Messages */}
            <div className={styles.messages}>
              {messages.map((msg) => (
                <ChatBubble
                  key={msg.id}
                  role={msg.role}
                  content={msg.content}
                  timestamp={msg.timestamp}
                  showAvatar={msg.role === 'assistant'}
                />
              ))}
              {isLoading && <ChatBubble isTyping showAvatar />}
              <div ref={bottomRef} />
            </div>

            {/* Quick prompts — shown only on welcome state */}
            {messages.length === 1 && (
              <div className={styles.quickPrompts}>
                {QUICK_PROMPTS.map((q) => (
                  <button
                    key={q}
                    className={styles.quickBtn}
                    onClick={() => {
                      setInput(q)
                      setTimeout(() => sendMessage(), 50)
                    }}
                  >
                    {q}
                  </button>
                ))}
              </div>
            )}

            {/* Input */}
            <div className={styles.inputRow}>
              <input
                ref={inputRef}
                className={styles.input}
                type="text"
                placeholder="Ask about your finances..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKey}
                disabled={isLoading}
                aria-label="Chat message input"
                maxLength={500}
              />
              <button
                className={`${styles.sendBtn} ${input.trim() && !isLoading ? styles.sendActive : ''}`}
                onClick={sendMessage}
                disabled={!input.trim() || isLoading}
                aria-label="Send message"
              >
                <Send size={18} strokeWidth={2} />
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
