/* ── Path Detail: Index Fund SIP — Stitch match ── */
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, CheckCircle2, Info } from 'lucide-react'
import styles from './SubPage.module.css'

const RETURNS_DATA = [
  { year: '1Y', returns: 12.4 },
  { year: '3Y', returns: 15.2 },
  { year: '5Y', returns: 14.8 },
  { year: '10Y', returns: 13.6 },
]

const CHECKLIST = [
  'Invests in all 50 top Indian companies',
  'Very low expense ratio (~0.1%)',
  'Fully passive — no fund manager bias',
  'SIP from ₹1,000/month',
  'Highly liquid — redeem anytime',
]

const PROJECTIONS = [
  { duration: '5 years', monthly: 5000, projected: 415000 },
  { duration: '10 years', monthly: 5000, projected: 1162000 },
  { duration: '15 years', monthly: 5000, projected: 2508000 },
]

export default function PathDetailIndexFundSIP() {
  const navigate = useNavigate()
  const fmt = (n: number) => '₹' + n.toLocaleString('en-IN')

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <button className={styles.backBtn} onClick={() => navigate('/grow')} aria-label="Back">
          <ArrowLeft size={20} strokeWidth={1.75} />
        </button>
        <p className={styles.headerTitle}>Index Fund SIP</p>
        <div style={{ width: 36 }} />
      </div>

      {/* Hero */}
      <div className={styles.px}>
        <div className={styles.heroCard}>
          <p className={styles.heroLabel}>GROWTH PATH</p>
          <h1 style={{ fontFamily: 'var(--font-headline)', fontSize: 'var(--text-2xl)', fontWeight: 'var(--font-bold)', color: '#fff', lineHeight: 1.2 }}>
            Nifty 50 Index Fund SIP
          </h1>
          <div className={styles.heroMeta}>
            <span className={styles.heroBadge}>LOW RISK</span>
            <span className={styles.heroSub}>~13-15% p.a. historically</span>
          </div>
        </div>
      </div>

      {/* Returns */}
      <div className={styles.px}>
        <p className={styles.sectionTitle}>Historical Returns</p>
        <div className={styles.returnsGrid}>
          {RETURNS_DATA.map(r => (
            <div key={r.year} className={styles.returnCell}>
              <p className={styles.returnPct}>+{r.returns}%</p>
              <p className={styles.returnPeriod}>{r.year} CAGR</p>
            </div>
          ))}
        </div>
      </div>

      {/* Why this fund */}
      <div className={styles.px}>
        <p className={styles.sectionTitle}>Why this path?</p>
        <div className={styles.list}>
          {CHECKLIST.map((item) => (
            <div key={item} className={styles.checkRow}>
              <CheckCircle2 size={16} color="var(--color-positive)" strokeWidth={2} />
              <p className={styles.checkText}>{item}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Projections */}
      <div className={styles.px}>
        <p className={styles.sectionTitle}>If you invest {fmt(5000)}/mo</p>
        <div className={styles.list}>
          {PROJECTIONS.map(p => (
            <div key={p.duration} className={styles.holdingRow}>
              <div>
                <p className={styles.holdingName}>After {p.duration}</p>
                <p className={styles.holdingType}>at ~14% CAGR</p>
              </div>
              <p className={styles.holdingAmt}>{fmt(p.projected)}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Disclaimer */}
      <div className={styles.px}>
        <div className={styles.alertCard}>
          <Info size={14} strokeWidth={1.75} style={{ color: 'var(--color-muted)', flexShrink: 0 }} />
          <p className={styles.alertText} style={{ fontSize: 'var(--text-xs)' }}>
            Past returns are not indicative of future results. Mutual fund investments are subject to market risk.
          </p>
        </div>
      </div>

      {/* CTA */}
      <div className={styles.px}>
        <button className={styles.ctaBtn} onClick={() => alert('Redirecting to Groww… (coming soon)')}>
          Start SIP via Groww →
        </button>
        <p className={styles.poweredBy}>POWERED BY GROWW BROKERAGE SERVICES</p>
      </div>
    </div>
  )
}
