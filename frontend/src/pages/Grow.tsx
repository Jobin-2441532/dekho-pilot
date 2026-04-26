/* Grow page — Stitch "Grow Home" + "Readiness Guardrail" */

import { useNavigate } from 'react-router-dom'
import { ShieldCheck, TrendingUp, Leaf, BarChart2, AlertTriangle, CheckCircle2, Sparkles } from 'lucide-react'
import { useAppStore } from '../store/appStore'
import styles from './Grow.module.css'

const RECS = [
  {
    id: 'sip',
    emoji: '📈',
    title: 'Start a ₹5,000/mo SIP',
    subtitle: 'Nifty 50 Index Fund',
    risk: 'LOW RISK',
    riskColor: '#2E7D32',
    horizon: '7+ years',
    why: 'Based on your savings buffer and income stability, you can start compounding now.',
    to: '/grow/recommendations',
  },
  {
    id: 'fd',
    emoji: '🔒',
    title: 'Open a 1-Year FD',
    subtitle: 'HDFC Bank · 7.1% p.a.',
    risk: 'NO RISK',
    riskColor: '#1565C0',
    horizon: '1 year',
    why: 'Your emergency fund is sufficient — park extra cash in a high-yield FD.',
    to: '/assets/savings',
  },
  {
    id: 'cc',
    emoji: '💳',
    title: 'Clear Credit Card First',
    subtitle: 'SBI Card · 36% p.a.',
    risk: 'PRIORITY',
    riskColor: '#B45309',
    horizon: 'This month',
    why: 'Paying 36% interest is worse than any investment return. Clear this first.',
    to: '/assets/liabilities',
  },
]

const READINESS_CHECKLIST = [
  { label: '3+ months emergency fund', done: false },
  { label: 'Consistent monthly savings > 20%', done: false },
  { label: 'No high-interest debt (>12% p.a.)', done: true },
  { label: 'Monthly income stable for 6 months', done: true },
  { label: 'Basic insurance coverage', done: false },
]

function GrowHome() {
  const navigate = useNavigate()
  const suggestedAmount = 5000

  return (
    <div className={styles.page}>
      {/* Top bar */}
      <div className={styles.topBar}>
        <p className={styles.pageTitle}>Grow</p>
        <div className={styles.avatarBtn}>AK</div>
      </div>

      {/* Action center */}
      <div className={styles.px}>
        <div className={styles.actionCenterCard}>
          <p className={styles.actionLabel}>ACTION CENTER</p>
          <h1 className={styles.actionTitle}>Your next growth step</h1>
        
        <div className={styles.readinessBadge}>
          <ShieldCheck size={18} className={styles.readinessIcon} strokeWidth={2} />
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span className={styles.readinessBadgeLabel}>AI READINESS STATUS</span>
            <span className={styles.readinessBadgeText}>You are ready to start investing</span>
          </div>
        </div>

        <p className={styles.suggestedLabel}>Suggested monthly amount</p>
        <p className={styles.suggestedAmt}>₹{suggestedAmount.toLocaleString('en-IN')}</p>
        </div>
      </div>

      <div className={styles.px} style={{ marginTop: 'var(--space-4)' }}>
        <div className={styles.insightCard}>
          <div className={styles.insightIconWrap}>✨</div>
          <div>
            <p className={styles.insightCardLabel}>SMART INSIGHT</p>
            <p className={styles.insightCardText}>
              Because your savings buffer is stable, you can safely start growing your wealth.
            </p>
          </div>
        </div>
      </div>

      {/* AI Recommendations block */}
      <div className={styles.px} style={{ marginTop: 'var(--space-5)' }}>
        <div className={styles.aiRecCard}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-2)' }}>
            <Sparkles size={18} color="rgba(255,255,255,0.8)" strokeWidth={1.75} />
            <p className={styles.aiRecLabel}>AI RECOMMENDATIONS</p>
          </div>
          <h1 className={styles.aiRecTitle}>
            Based on your financial health
          </h1>
          <p className={styles.aiRecSub}>
            Dekho analysed your income, expenses, savings, and goals to suggest these next steps.
          </p>
        </div>
      </div>

      {/* Your Next Steps */}
      <div className={styles.px} style={{ marginTop: 'var(--space-5)' }}>
        <p className={styles.pathsTitle}>Your Next Steps</p>
        <div className={styles.recList}>
          {RECS.map((rec, i) => (
            <button
              key={rec.id}
              className={styles.recCard}
              onClick={() => navigate(rec.to)}
            >
              <div className={styles.recNum}>{i + 1}</div>
              <div className={styles.recBody}>
                <div className={styles.recHeader}>
                  <div className={styles.recTitleRow}>
                    <span className={styles.recEmoji}>{rec.emoji}</span>
                    <div>
                      <p className={styles.recTitle}>{rec.title}</p>
                      <p className={styles.recSub}>{rec.subtitle}</p>
                    </div>
                  </div>
                  <span className={styles.recRisk} style={{ color: rec.riskColor }}>{rec.risk}</span>
                </div>
                <p className={styles.recWhy}>{rec.why}</p>
                <div className={styles.recMeta}>
                  <span>⏱ {rec.horizon}</span>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* CTA button */}
      <div className={styles.px} style={{ marginTop: 'var(--space-6)' }}>
        <button
          className={styles.ctaBtn}
          onClick={() => navigate('/grow/recommendations')}
        >
          Get Personalized recommendations by<br/>Dekho
        </button>
        <p className={styles.poweredBy}>POWERED BY GROWW BROKERAGE SERVICES</p>
      </div>
    </div>
  )
}

function ReadinessGuardrail() {
  const navigate = useNavigate()
  const doneCount = READINESS_CHECKLIST.filter(c => c.done).length
  const pct = Math.round((doneCount / READINESS_CHECKLIST.length) * 100)

  return (
    <div className={styles.page}>
      <div className={styles.topBar}>
        <p className={styles.pageTitle}>Grow</p>
        <div className={styles.avatarBtn}>AK</div>
      </div>

      {/* Not ready card */}
      <div className={styles.px}>
        <div className={styles.guardrailCard}>
          <AlertTriangle size={24} color="#B45309" strokeWidth={1.75} />
          <h1 className={styles.guardrailTitle}>Almost ready to invest</h1>
          <p className={styles.guardrailSub}>
            Complete a few financial health checks before you start growing your wealth.
          </p>
          <div className={styles.guardrailTrack}>
            <div className={styles.guardrailFill} style={{ width: `${pct}%` }} />
          </div>
          <p className={styles.guardrailPct}>{doneCount} of {READINESS_CHECKLIST.length} criteria met ({pct}%)</p>
        </div>
      </div>

      {/* Checklist */}
      <div className={styles.px}>
        <p className={styles.pathsTitle}>Your Readiness Checklist</p>
        <div className={styles.checkList}>
          {READINESS_CHECKLIST.map((item, i) => (
            <div key={i} className={`${styles.checkItem} ${item.done ? styles.checkDone : ''}`}>
              {item.done
                ? <CheckCircle2 size={18} color="var(--color-positive)" strokeWidth={1.75} />
                : <div className={styles.checkCircle} />
              }
              <p className={styles.checkLabel}>{item.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Go to budgets CTA */}
      <div className={styles.px}>
        <button className={styles.ctaBtn} onClick={() => navigate('/budgets')}>
          Work on missing criteria →
        </button>
      </div>
    </div>
  )
}

export default function Grow() {
  const { user } = useAppStore()
  return user.isInvestmentEligible ? <GrowHome /> : <ReadinessGuardrail />
}
