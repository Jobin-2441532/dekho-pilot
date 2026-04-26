/* ── Mutual Fund Detail — Stitch match ── */
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Info } from 'lucide-react'
import styles from './SubPage.module.css'

const NAV_DATA = [
  { month: 'Nov', nav: 98.4 }, { month: 'Dec', nav: 102.1 },
  { month: 'Jan', nav: 108.6 }, { month: 'Feb', nav: 112.3 },
  { month: 'Mar', nav: 119.8 }, { month: 'Apr', nav: 124.5 },
]

const TOP_HOLDINGS = [
  { name: 'HDFC Bank', allocation: 9.2 },
  { name: 'Infosys', allocation: 7.8 },
  { name: 'Reliance Industries', allocation: 6.9 },
  { name: 'ICICI Bank', allocation: 5.4 },
  { name: 'TCS', allocation: 4.8 },
]

export default function MutualFundDetail() {
  const navigate = useNavigate()
  const curNav = NAV_DATA[NAV_DATA.length - 1].nav
  const minNav = Math.min(...NAV_DATA.map(d => d.nav))
  const maxNav = Math.max(...NAV_DATA.map(d => d.nav))
  const w = 280, h = 70
  const pts = NAV_DATA.map((d, i) => {
    const x = (i / (NAV_DATA.length - 1)) * w
    const y = h - ((d.nav - minNav) / (maxNav - minNav)) * h
    return `${x},${y}`
  }).join(' ')

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <button className={styles.backBtn} onClick={() => navigate(-1)} aria-label="Back">
          <ArrowLeft size={20} strokeWidth={1.75} />
        </button>
        <p className={styles.headerTitle}>Fund Detail</p>
        <div style={{ width: 36 }} />
      </div>

      {/* Hero */}
      <div className={styles.px}>
        <div className={styles.heroCard}>
          <p className={styles.heroLabel}>MUTUAL FUND</p>
          <h1 style={{ fontFamily: 'var(--font-headline)', fontSize: 'var(--text-xl)', fontWeight: 'var(--font-bold)', color: '#fff', lineHeight: 1.3 }}>
            Parag Parikh Flexi Cap Fund
          </h1>
          <div className={styles.heroMeta}>
            <span className={styles.heroBadge}>NAV ₹{curNav}</span>
            <span className={styles.heroSub}>+18.6% (1Y)</span>
          </div>
        </div>
      </div>

      {/* NAV chart */}
      <div className={styles.px}>
        <div className={styles.chartCard}>
          <p className={styles.chartTitle}>NAV Movement (6M)</p>
          <svg viewBox={`0 0 ${w} ${h}`} style={{ width: '100%', height: 70, marginTop: 8, marginBottom: 8 }} aria-hidden>
            <polyline points={pts} fill="none" stroke="var(--color-positive)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            {NAV_DATA.map(d => (
              <span key={d.month} className={styles.chartLabel}>{d.month}</span>
            ))}
          </div>
        </div>
      </div>

      {/* Key stats */}
      <div className={styles.px}>
        <div className={styles.statsGrid}>
          {[
            { label: 'Category', value: 'Flexi Cap' },
            { label: 'Risk', value: 'Moderate-High' },
            { label: 'Expense', value: '0.58%' },
            { label: 'AUM', value: '₹72,000 Cr' },
          ].map(stat => (
            <div key={stat.label} className={styles.statCell}>
              <p className={styles.statAmt} style={{ fontSize: 'var(--text-sm)' }}>{stat.value}</p>
              <p className={styles.statLabel}>{stat.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Top Holdings */}
      <div className={styles.px}>
        <p className={styles.sectionTitle}>Top Holdings</p>
        <div className={styles.list}>
          {TOP_HOLDINGS.map(h => (
            <div key={h.name} className={styles.holdingRow}>
              <p className={styles.holdingName}>{h.name}</p>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                <div style={{ width: 60, height: 6, background: 'var(--bg-surface-high)', borderRadius: 99 }}>
                  <div style={{ width: `${(h.allocation / 10) * 100}%`, height: '100%', background: 'var(--color-primary)', borderRadius: 99 }} />
                </div>
                <p className={styles.holdingAmt} style={{ fontSize: 'var(--text-sm)' }}>{h.allocation}%</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Disclaimer */}
      <div className={styles.px}>
        <div className={styles.alertCard}>
          <Info size={14} style={{ color: 'var(--color-muted)', flexShrink: 0 }} />
          <p className={styles.alertText} style={{ fontSize: 'var(--text-xs)' }}>
            Mutual fund investments are subject to market risks. Read all scheme related documents carefully.
          </p>
        </div>
      </div>
    </div>
  )
}
