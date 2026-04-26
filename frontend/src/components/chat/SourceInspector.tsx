import { useState } from 'react'
import { ChevronDown, Database, BookOpen } from 'lucide-react'
import styles from './SourceInspector.module.css'

interface Source {
  label: string
  text: string
  type?: 'data' | 'knowledge'
}

interface SourceInspectorProps {
  sources: Source[]
}

export default function SourceInspector({ sources }: SourceInspectorProps) {
  const [open, setOpen] = useState(false)

  if (!sources.length) return null

  return (
    <div className={styles.wrapper}>
      <button
        className={styles.toggle}
        onClick={() => setOpen(o => !o)}
        aria-expanded={open}
        aria-label="View data sources"
      >
        <Database size={12} />
        {sources.length} source{sources.length > 1 ? 's' : ''} used
        <ChevronDown
          size={12}
          className={`${styles.chevron} ${open ? styles.open : ''}`}
        />
      </button>

      <div className={`${styles.panel} ${open ? styles.open : ''}`} aria-hidden={!open}>
        <div className={styles.panelInner}>
          {sources.map((s, i) => (
            <div key={i} className={styles.source}>
              <span className={styles.sourceIcon}>
                {s.type === 'knowledge' ? (
                  <BookOpen size={12} />
                ) : (
                  <Database size={12} />
                )}
              </span>
              <div className={styles.sourceText}>
                <span className={styles.sourceLabel}>{s.label}</span>
                {s.text}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
