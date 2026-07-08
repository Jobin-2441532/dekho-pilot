import React, { useEffect, useRef, useMemo, useCallback } from 'react'
import './index.css'
import { useChatStore } from './store'
import { useChatStream } from './hooks/useChatStream'
import { MessageBubble } from './components/MessageBubble'
import { TypingIndicator } from './components/TypingIndicator'
import {
  ChatHeader, ChatInputBar, PresetQueries,
  DebugPanel, AlertBanner, EmptyState,
} from './components/ChatShell'

function App() {
  const { messages, isLoading, streamingId } = useChatStore()
  const { sendMessage } = useChatStream()
  const bottomRef = useRef<HTMLDivElement>(null)

  // Memoize send to avoid re-renders on child components
  const handleSend = useCallback((text: string) => {
    sendMessage(text)
  }, [sendMessage])

  // Auto-scroll to bottom on new message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length, streamingId])

  const hasMessages = messages.length > 0

  // Memoize message list to avoid full re-render on every token
  const messageList = useMemo(() => (
    messages.map((msg) => (
      <MessageBubble
        key={msg.id}
        message={msg}
        onChipClick={handleSend}
      />
    ))
  ), [messages, handleSend])

  return (
    <div style={{ display: 'flex', height: '100vh', background: 'var(--bg-base)' }}>
      <div className="chat-shell">
        <ChatHeader onSend={handleSend} isLoading={isLoading} />
        <AlertBanner />
        <PresetQueries onSend={handleSend} />

        <div className="messages-area">
          {!hasMessages && <EmptyState onSend={handleSend} />}

          {messageList}

          {isLoading && !streamingId && <TypingIndicator />}

          <div ref={bottomRef} />
        </div>

        <ChatInputBar onSend={handleSend} isLoading={isLoading} />
      </div>

      <DebugPanel />
    </div>
  )
}

export default App
