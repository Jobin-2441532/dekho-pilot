/* ── Monthly Wrap — Stitch "Monthly Wrap with Story Carousel" ── */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, ChevronLeft, ChevronRight } from 'lucide-react'
import styles from './SubPage.module.css'

const SLIDES = [
  {
    id: 'income',
    label: 'INCOME',
    title: 'You earned ₹82,000 this month',
    subtitle: '↑ ₹5,000 more than last month',
    emoji: '💼',
    color: '#2E7D32',
  },
  {
    id: 'expenses',
    label: 'SPENDING',
    title: 'You spent ₹24,500',
    subtitle: 'Food & Dining was your top category (₹8,400)',
    emoji: '🍴',
    color: '#6C482D',
  },
  {
    id: 'savings',
    label: 'SAVINGS',
    title: 'You saved ₹57,500 (70%)!',
    subtitle: '★ Above your 60% savings goal — great job!',
    emoji: '⭐',
    color: '#1565C0',
  },
  {
    id: 'net_worth',
    label: 'NET WORTH',
    title: 'Net worth grew to ₹3,42,500',
    subtitle: '+₹12,400 this month',
    emoji: '📈',
    color: '#6C482D',
  },
]

const HIGHLIGHTS = [
  { label: 'Income', value: '₹82,000', icon: '💼', positive: true },
  { label: 'Expenses', value: '₹24,500', icon: '💸', positive: false },
  { label: 'Saved', value: '₹57,500', icon: '🏦', positive: true },
  { label: 'Net Worth', value: '₹3,42,500', icon: '📊', positive: true },
]

export default function MonthlyWrap() {
  const navigate = useNavigate()
  const [slide, setSlide] = useState(0)
  const current = SLIDES[slide]

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <button className={styles.backBtn} onClick={() => navigate('/home')} aria-label="Back">
          <ArrowLeft size={20} strokeWidth={1.75} />
        </button>
        <p className={styles.headerTitle}>April Wrap</p>
        <div style={{ width: 36 }} />
      </div>

      {/* Story Carousel */}
      <div className={styles.px}>
        <div className={styles.storyCard} style={{ '--story-color': current.color } as React.CSSProperties}>
          {/* Progress dots */}
          <div className={styles.storyDots}>
            {SLIDES.map((_, i) => (
              <div
                key={i}
                className={`${styles.storyDot} ${i === slide ? styles.storyDotActive : ''}`}
              />
            ))}
          </div>

          <div className={styles.storyContent}>
            <p className={styles.storyLabel}>{current.label}</p>
            <p className={styles.storyEmoji}>{current.emoji}</p>
            <h2 className={styles.storyTitle}>{current.title}</h2>
            <p className={styles.storySub}>{current.subtitle}</p>
          </div>

          {/* Nav arrows */}
          <button
            className={styles.storyPrev}
            onClick={() => setSlide(s => Math.max(0, s - 1))}
            disabled={slide === 0}
            aria-label="Previous"
          >
            <ChevronLeft size={20} />
          </button>
          <button
            className={styles.storyNext}
            onClick={() => setSlide(s => Math.min(SLIDES.length - 1, s + 1))}
            disabled={slide === SLIDES.length - 1}
            aria-label="Next"
          >
            <ChevronRight size={20} />
          </button>
        </div>
      </div>

      {/* Quick stats grid */}
      <div className={styles.px}>
        <p className={styles.sectionTitle}>April at a Glance</p>
        <div className={styles.statsGrid}>
          {HIGHLIGHTS.map((h) => (
            <div key={h.label} className={styles.statCell}>
              <span className={styles.statEmoji}>{h.icon}</span>
              <p className={`${styles.statAmt} ${h.positive ? styles.statPos : styles.statNeg}`}>{h.value}</p>
              <p className={styles.statLabel}>{h.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Narrative insight */}
      <div className={styles.px}>
        <div className={styles.heroCard} style={{ gap: 'var(--space-3)' }}>
          <p className={styles.heroLabel}>DEKHO SAYS</p>
          <p style={{ fontFamily: 'var(--font-headline)', fontSize: 'var(--text-lg)', fontWeight: 'var(--font-bold)', color: '#fff', lineHeight: 1.3 }}>
            April was a strong month 💪
          </p>
          <p style={{ fontFamily: 'var(--font-body)', fontSize: 'var(--text-sm)', color: 'rgba(255,255,255,0.8)', lineHeight: 1.6 }}>
            You hit a 70% savings rate and grew your net worth by ₹12,400. Your biggest win was keeping lifestyle spending under control.
          </p>
        </div>
      </div>

      {/* Goal progress in month */}
      <div className={styles.px}>
        <div className={styles.insightCard}>
          <p className={styles.insightText}>
            🎯 Goal progress: You added ₹5,000 to your Goa trip fund. You're 50% there!
          </p>
        </div>
      </div>
    </div>
  )
}
