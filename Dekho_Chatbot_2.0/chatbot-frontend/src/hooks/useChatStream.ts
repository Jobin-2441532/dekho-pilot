import { useCallback, useRef } from 'react'
import { useChatStore, useUserStore } from '../store'
import type { Message, ChartData, AlertPayload } from '../store'
import { STREAM_URL } from '../api/client'

const genId = () => Math.random().toString(36).slice(2, 10)

export function useChatStream() {
  const abortRef = useRef<AbortController | null>(null)
  const {
    sessionId, addMessage, updateStreamingMessage,
    finalizeMessage, setLoading, setStreamingId, setDebugInfo, setAlert, persistHistory,
  } = useChatStore()
  const { userId } = useUserStore()

  const sendMessage = useCallback(async (text: string, isSessionStart = false) => {
    if (!text.trim()) return

    // Add user message
    const userMsgId = genId()
    addMessage({
      id: userMsgId,
      role: 'user',
      content: text.trim(),
      timestamp: new Date(),
    })

    // Add placeholder bot message (streaming)
    const botMsgId = genId()
    addMessage({
      id: botMsgId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true,
    })
    setStreamingId(botMsgId)
    setLoading(true)

    abortRef.current = new AbortController()

    try {
      const res = await fetch(STREAM_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, message: text, session_id: sessionId, is_session_start: isSessionStart }),
        signal: abortRef.current.signal,
      })

      if (!res.ok || !res.body) {
        throw new Error(`HTTP ${res.status}`)
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let chart: ChartData | undefined
      let quickReplies: string[] = []
      let intent = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        const events = buffer.split('\n\n')
        buffer = events.pop() ?? ''

        for (const eventStr of events) {
          if (!eventStr.trim()) continue
          const lines = eventStr.split('\n')
          let evType = 'message'
          let evData = ''

          for (const line of lines) {
            if (line.startsWith('event: ')) evType = line.slice(7).trim()
            if (line.startsWith('data: ')) evData = line.slice(6).trim()
          }

          if (!evData) continue

          try {
            const payload = JSON.parse(evData)

            if (evType === 'token') {
              updateStreamingMessage(botMsgId, payload.text ?? '')
            } else if (evType === 'intent') {
              intent = payload.intent ?? ''
              setDebugInfo({
                intent: payload.intent,
                confidence: payload.confidence,
                latencyMs: 0,
                sessionId,
              })
            } else if (evType === 'chart_data') {
              chart = payload as ChartData
            } else if (evType === 'quick_replies') {
              quickReplies = payload.items ?? []
            } else if (evType === 'alert') {
              setAlert(payload as AlertPayload)
            } else if (evType === 'done') {
              setDebugInfo({
                intent,
                confidence: 0,
                latencyMs: payload.latency_ms ?? 0,
                sessionId: payload.session_id ?? sessionId,
              })
            } else if (evType === 'error') {
              updateStreamingMessage(botMsgId, payload.message ?? 'Something went wrong.')
            }
          } catch { /* ignore parse errors */ }
        }
      }

      finalizeMessage(botMsgId, { chart, quickReplies, intent })
      // Persist this user's conversation to localStorage
      persistHistory(userId)
    } catch (err: unknown) {
      if ((err as Error).name !== 'AbortError') {
        finalizeMessage(botMsgId, {
          content: "I'm having a brief slowdown ⏳ — please try again in a moment!",
          isFallback: true,
        })
      }
    } finally {
      setLoading(false)
      setStreamingId(null)
      abortRef.current = null
    }
  }, [userId, sessionId, addMessage, updateStreamingMessage, finalizeMessage, setLoading, setStreamingId, setDebugInfo, setAlert, persistHistory])

  const abort = useCallback(() => {
    abortRef.current?.abort()
  }, [])

  return { sendMessage, abort }
}
