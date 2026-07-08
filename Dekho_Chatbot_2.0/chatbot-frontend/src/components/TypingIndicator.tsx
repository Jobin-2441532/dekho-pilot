import React from 'react'

export function TypingIndicator() {
  return (
    <div className="message-row message-row--bot" style={{ marginBottom: 4 }}>
      <div className="message-row__avatar">🧭</div>
      <div className="message-row__body">
        <div className="typing-indicator">
          <div className="typing-indicator__dot" />
          <div className="typing-indicator__dot" />
          <div className="typing-indicator__dot" />
        </div>
      </div>
    </div>
  )
}
