import React, { useState } from 'react'
import { motion } from 'framer-motion'

// ── InsightCard ───────────────────────────────────────────────────────────────

interface InsightCardProps {
  icon: string
  value: string
  label: string
  sublabel?: string
  color?: string
}

export function InsightCard({ icon, value, label, sublabel, color = 'var(--accent-primary)' }: InsightCardProps) {
  return (
    <motion.div
      className="insight-card"
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div className="insight-card__icon">{icon}</div>
      <div className="insight-card__content">
        <div className="insight-card__value" style={{ color }}>{value}</div>
        <div className="insight-card__label">{label}</div>
        {sublabel && <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>{sublabel}</div>}
      </div>
    </motion.div>
  )
}

// ── TransactionConfirmCard ────────────────────────────────────────────────────

interface TransactionConfirmProps {
  amount: string
  description: string
  category: string
  type?: 'expense' | 'income'
}

export function TransactionConfirmCard({ amount, description, category, type = 'expense' }: TransactionConfirmProps) {
  const isIncome = type === 'income'
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        background: isIncome ? 'rgba(82,183,136,0.1)' : 'rgba(231,111,81,0.1)',
        border: `1px solid ${isIncome ? 'rgba(82,183,136,0.3)' : 'rgba(231,111,81,0.3)'}`,
        borderRadius: 'var(--radius-md)',
        padding: '12px 14px',
        display: 'flex',
        alignItems: 'center',
        gap: 12,
      }}
    >
      <span style={{ fontSize: 22 }}>{isIncome ? '💸' : '🧾'}</span>
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 600, fontSize: 14, color: 'var(--text-primary)' }}>
          {isIncome ? '+' : '-'}{amount}
        </div>
        <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>
          {description} · <span style={{ color: 'var(--accent-primary)' }}>{category}</span>
        </div>
      </div>
      <div style={{
        fontSize: 11,
        padding: '3px 8px',
        borderRadius: 'var(--radius-full)',
        background: isIncome ? 'rgba(82,183,136,0.2)' : 'rgba(231,111,81,0.2)',
        color: isIncome ? 'var(--accent-green)' : 'var(--accent-warm)',
        fontWeight: 600,
      }}>
        Noted ✓
      </div>
    </motion.div>
  )
}

// ── ResponseJSONViewer ────────────────────────────────────────────────────────

interface JSONViewerProps {
  data: Record<string, unknown>
}

export function ResponseJSONViewer({ data }: JSONViewerProps) {
  const [open, setOpen] = useState(false)
  return (
    <div style={{ marginTop: 4 }}>
      <button
        onClick={() => setOpen(o => !o)}
        style={{
          background: 'none', border: 'none',
          color: 'var(--accent-blue)', fontSize: 11,
          cursor: 'pointer', padding: '2px 0',
          fontFamily: 'var(--font-body)',
        }}
      >
        {open ? '▲ Hide' : '▾ Show'} raw JSON
      </button>
      {open && (
        <motion.pre
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          style={{
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            padding: '10px 12px',
            fontSize: 11,
            color: 'var(--text-secondary)',
            overflowX: 'auto',
            marginTop: 6,
            fontFamily: 'monospace',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-all',
          }}
        >
          {JSON.stringify(data, null, 2)}
        </motion.pre>
      )}
    </div>
  )
}

// ── ProgressiveDisclosure ─────────────────────────────────────────────────────

interface DisclosureProps {
  summary: React.ReactNode
  detail: React.ReactNode
}

export function ProgressiveDisclosure({ summary, detail }: DisclosureProps) {
  const [expanded, setExpanded] = useState(false)
  return (
    <div>
      {summary}
      <button
        onClick={() => setExpanded(e => !e)}
        style={{
          background: 'none', border: 'none',
          color: 'var(--accent-primary)', fontSize: 12,
          cursor: 'pointer', marginTop: 6,
          fontFamily: 'var(--font-body)',
          display: 'flex', alignItems: 'center', gap: 4,
        }}
      >
        {expanded ? '▲ Show less' : '▾ See full breakdown'}
      </button>
      {expanded && (
        <motion.div
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25 }}
          style={{ marginTop: 8 }}
        >
          {detail}
        </motion.div>
      )}
    </div>
  )
}
