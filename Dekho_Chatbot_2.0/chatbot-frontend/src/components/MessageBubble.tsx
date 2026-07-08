import React, { useState } from 'react'
import { ThumbsUp, ThumbsDown, X, Send } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import type { Message } from '../store'
import { useUIStore, useUserStore, useChatStore } from '../store'
import { ChatChart } from './ChatChart'
import { TransactionConfirmCard, ResponseJSONViewer } from './RichComponents'
import { submitFeedback } from '../api/client'

interface Props {
  message: Message
  onChipClick: (text: string) => void
}

function formatTime(d: Date) {
  return d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true })
}

// Extract transaction slots from intent+content for the confirm card
function parseTransactionSlots(content: string, intent?: string) {
  if (intent !== 'ADD_TRANSACTION') return null
  const amountMatch = content.match(/₹[\d,]+/)
  if (!amountMatch) return null
  return {
    amount: amountMatch[0],
    description: 'Transaction',
    category: 'Other',
  }
}

// ── Feedback Bar ──────────────────────────────────────────────────────────────

interface FeedbackBarProps {
  messageId: string
  intent?: string
}

function FeedbackBar({ messageId, intent }: FeedbackBarProps) {
  const { userId } = useUserStore()
  const { sessionId } = useChatStore()
  const [rated, setRated] = useState<'up' | 'down' | null>(null)
  const [showCorrection, setShowCorrection] = useState(false)
  const [correction, setCorrection] = useState('')
  const [submitted, setSubmitted] = useState(false)

  const handleRate = async (rating: 'up' | 'down') => {
    if (rated) return
    setRated(rating)
    if (rating === 'up') {
      await submitFeedback({ user_id: userId, session_id: sessionId, message_id: messageId, rating, intent })
      setSubmitted(true)
    } else {
      // Show correction input for thumbs-down
      setShowCorrection(true)
    }
  }

  const handleCorrectionSubmit = async () => {
    await submitFeedback({
      user_id: userId,
      session_id: sessionId,
      message_id: messageId,
      rating: 'down',
      correction: correction.trim() || undefined,
      intent,
    })
    setShowCorrection(false)
    setSubmitted(true)
  }

  if (submitted) {
    return (
      <div className="feedback-bar feedback-bar--done">
        {rated === 'up' ? '👍 Thanks for the feedback!' : '🙏 Got it, I\'ll keep that in mind'}
      </div>
    )
  }

  return (
    <div className="feedback-bar">
      <AnimatePresence>
        {!showCorrection ? (
          <motion.div
            key="buttons"
            className="feedback-bar__buttons"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <span className="feedback-bar__label">Helpful?</span>
            <button
              className={`feedback-btn feedback-btn--up ${rated === 'up' ? 'feedback-btn--active' : ''}`}
              onClick={() => handleRate('up')}
              title="This was helpful"
              disabled={!!rated}
            >
              <ThumbsUp size={13} />
            </button>
            <button
              className={`feedback-btn feedback-btn--down ${rated === 'down' ? 'feedback-btn--active' : ''}`}
              onClick={() => handleRate('down')}
              title="This wasn't helpful"
              disabled={!!rated}
            >
              <ThumbsDown size={13} />
            </button>
          </motion.div>
        ) : (
          <motion.div
            key="correction"
            className="feedback-correction"
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            <input
              className="feedback-correction__input"
              placeholder="What was wrong? (optional)"
              value={correction}
              onChange={(e) => setCorrection(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleCorrectionSubmit()}
              autoFocus
              maxLength={200}
            />
            <button className="feedback-correction__send" onClick={handleCorrectionSubmit} title="Submit">
              <Send size={12} />
            </button>
            <button
              className="feedback-correction__skip"
              onClick={() => handleCorrectionSubmit()}
              title="Skip"
            >
              <X size={12} />
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// ── Message Bubble ────────────────────────────────────────────────────────────

export function MessageBubble({ message, onChipClick }: Props) {
  const isBot = message.role === 'assistant'
  const { showDebug } = useUIStore()

  const txnSlots = parseTransactionSlots(message.content, message.intent)

  const rawPayload = showDebug && isBot ? {
    intent: message.intent,
    chart: message.chart,
    quickReplies: message.quickReplies,
    isFallback: message.isFallback,
    timestamp: message.timestamp,
  } : null

  return (
    <motion.div
      className={`message-row message-row--${isBot ? 'bot' : 'user'}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
    >
      <div className="message-row__avatar">
        {isBot ? '🧭' : '👤'}
      </div>

      <div className="message-row__body">
        {/* Text bubble */}
        {(message.content || message.isStreaming) && (
          <div className={`bubble bubble--${isBot ? 'bot' : 'user'} ${message.isStreaming ? 'bubble--streaming' : ''}`}>
            {isBot ? (
              <>
                <ReactMarkdown>{message.content}</ReactMarkdown>
                {message.isStreaming && <span className="bubble__cursor" />}
              </>
            ) : (
              message.content
            )}
          </div>
        )}

        {/* Transaction confirm card (ADD_TRANSACTION intent) */}
        {!message.isStreaming && isBot && txnSlots && (
          <TransactionConfirmCard
            amount={txnSlots.amount}
            description={txnSlots.description}
            category={txnSlots.category}
          />
        )}

        {/* Chart (only when done streaming) */}
        {!message.isStreaming && message.chart && (
          <ChatChart chart={message.chart} />
        )}

        {/* Quick reply chips */}
        <AnimatePresence>
          {!message.isStreaming && message.quickReplies && message.quickReplies.length > 0 && (
            <motion.div
              className="quick-replies"
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              {message.quickReplies.map((chip) => (
                <button key={chip} className="chip" onClick={() => onChipClick(chip)}>
                  {chip}
                </button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Feedback bar — only on completed bot messages, not fallbacks */}
        {!message.isStreaming && isBot && !message.isFallback && message.content && (
          <FeedbackBar messageId={message.id} intent={message.intent} />
        )}

        {/* Raw JSON viewer (debug mode only) */}
        {rawPayload && !message.isStreaming && (
          <ResponseJSONViewer data={rawPayload as Record<string, unknown>} />
        )}

        <span className="msg-time">{formatTime(message.timestamp)}</span>
      </div>
    </motion.div>
  )
}
