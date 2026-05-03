import type { ReactNode } from 'react'
import ProgressBar from '../ui/ProgressBar'
import MetricBlock from '../ui/MetricBlock'
import PremiumChart from '../ui/PremiumChart'
import Card from '../ui/Card'
import styles from './ChatBubble.module.css'

type Role = 'user' | 'assistant'

type ChatBubbleProps =
  | {
      role: Role
      content: string | ReactNode
      timestamp?: string
      showAvatar?: boolean
      isTyping?: false
    }
  | {
      role?: never
      content?: never
      timestamp?: never
      showAvatar?: boolean
      isTyping: true
    }

function formatTime(ts?: string): string {
  if (!ts) return new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true })
  // Ensure the string is parsed as UTC (append Z if missing)
  const raw = ts.endsWith('Z') || ts.includes('+') ? ts : ts + 'Z'
  return new Date(raw).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true })
}

export default function ChatBubble({
  role,
  content,
  timestamp,
  showAvatar = false,
  isTyping = false,
}: ChatBubbleProps) {
  if (isTyping) {
    return (
      <div className={`${styles.wrapper} ${styles.assistant}`}>
        {showAvatar && (
          <div className={styles.avatarRow}>
            <div className={styles.avatar}>D</div>
            <div className={styles.typing}>
              <span className={styles.dot} />
              <span className={styles.dot} />
              <span className={styles.dot} />
            </div>
          </div>
        )}
        {!showAvatar && (
          <div className={styles.typing}>
            <span className={styles.dot} />
            <span className={styles.dot} />
            <span className={styles.dot} />
          </div>
        )}
      </div>
    )
  }

function renderParsedContent(rawContent: string | ReactNode): ReactNode {
  if (typeof rawContent !== 'string') return rawContent

  const lines = rawContent.split('\n')
  const nodes: ReactNode[] = []
  let keyCount = 0

  lines.forEach((line) => {
    keyCount++
    const trimmed = line.trim()

    // Skip empty lines but add spacing between paragraphs
    if (!trimmed) {
      nodes.push(<div key={keyCount} style={{ height: '0.5rem' }} />)
      return
    }

    // [UI: PROGRESS | Title | Current | Target]
    const progMatch = trimmed.match(/\[UI:\s*PROGRESS\s*\|\s*([^|\]]+)\s*\|\s*([^|\]]+)\s*\|\s*([^\]]+)\]/i)
    if (progMatch) {
      nodes.push(
        <div key={keyCount} style={{ margin: 'var(--space-3) 0', width: '100%', minWidth: '240px' }}>
          <Card variant="flat" padding="compact">
            <ProgressBar
              label={progMatch[1].trim()}
              current={parseFloat(progMatch[2].replace(/[₹,]/g, ''))}
              target={parseFloat(progMatch[3].replace(/[₹,]/g, ''))}
              showValue
              color="var(--color-brand-mid)"
            />
          </Card>
        </div>
      )
      return
    }

    // [UI: METRIC | Title | Value]
    const metricMatch = trimmed.match(/\[UI:\s*METRIC\s*\|\s*([^|\]]+)\s*\|\s*([^\]]+)\]/i)
    if (metricMatch) {
      nodes.push(
        <div key={keyCount} style={{ margin: 'var(--space-3) 0', width: '100%', minWidth: '200px' }}>
          <Card variant="flat" padding="compact">
            <MetricBlock label={metricMatch[1].trim()} value={metricMatch[2].trim()} size="sm" />
          </Card>
        </div>
      )
      return
    }

    // [UI: CHART | Type | Title | data]
    const chartMatch = trimmed.match(/\[UI:\s*CHART\s*\|\s*([^|\]]+)\s*\|\s*([^|\]]+)\s*\|\s*([^\]]+)\]/i)
    if (chartMatch) {
      const type = chartMatch[1].trim()
      const title = chartMatch[2].trim()
      const parsedData = chartMatch[3].split(',').map(pair => {
        const [lbl, val] = pair.split(':')
        return {
          label: lbl ? lbl.trim() : 'Unknown',
          value: val ? parseFloat(val.replace(/[₹,]/g, '').trim()) || 0 : 0,
        }
      }).filter(d => d.value > 0)

      nodes.push(
        <div key={keyCount} style={{ margin: 'var(--space-3) 0', width: '100%', minWidth: '240px' }}>
          <Card variant="flat" padding="compact">
            <PremiumChart type={type.toLowerCase() === 'pie' ? 'Pie' : 'Bar'} title={title} data={parsedData} />
          </Card>
        </div>
      )
      return
    }

    // Skip hidden action tags entirely — never show them to the user
    if (/^\[ACTION:/i.test(trimmed)) return

    // Strip markdown decoration from plain text:
    // Remove leading ###, ##, # (headers)
    // Remove **bold** and *italic* markers
    // Remove leading bullet markers (*, -, •, %) but keep the text
    let cleaned = trimmed
      .replace(/^#{1,3}\s*/, '')           // ### headers
      .replace(/\*\*(.+?)\*\*/g, '$1')     // **bold**
      .replace(/\*(.+?)\*/g, '$1')         // *italic*
      .replace(/^[*\-•%]\s+/, '')          // leading bullet/decorative symbols

    nodes.push(
      <span key={keyCount} style={{ display: 'block', marginBottom: '0.4rem', lineHeight: '1.55' }}>
        {cleaned}
      </span>
    )
  })

  return <>{nodes}</>
}

  // After this point isTyping is false, so role and content are guaranteed
  const safeRole = role as Role
  const parsed = renderParsedContent(content)
  
  const bubble = (
    <div className={`${styles.wrapper} ${styles[safeRole]}`}>
      {showAvatar && safeRole === 'assistant' ? (
        <div className={styles.avatarRow}>
          <div className={styles.avatar}>D</div>
          <div className={styles.bubble}>{parsed}</div>
        </div>
      ) : (
        <div className={styles.bubble}>{parsed}</div>
      )}
      <span className={styles.timestamp}>{formatTime(timestamp)}</span>
    </div>
  )

  return bubble
}
