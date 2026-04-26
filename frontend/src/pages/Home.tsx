/* ── Home Page — Daily Reflection (Stitch: "Daily Reflection Updated Nav") ── */

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bell, ChevronDown, ChevronUp, Settings } from 'lucide-react'
import { SkeletonCard } from '../components/ui/LoadingState'
import styles from './Home.module.css'

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

function getGreeting() {
  const h = new Date().getHours()
  if (h < 12) return 'Good morning'
  if (h < 17) return 'Good afternoon'
  return 'Good evening'
}

function fmtINR(n: number) {
  return '₹' + n.toLocaleString('en-IN')
}

export default function Home() {
  const navigate = useNavigate()
  const [loading, setLoading]       = useState(true)
  const [showWhy, setShowWhy]       = useState(false)
  const [profile, setProfile]       = useState<any>({ name: 'Arjun', monthly_budget: 45000 })
  const [todaySpend, setTodaySpend] = useState(1420)
  const [avgSpend]                  = useState(1750)
  const [monthTotal, setMonthTotal] = useState(0)
  const [savingGoals, setSavingGoals] = useState<any[]>([])
  const [topCategory, setTopCategory] = useState<{ name: string; total: number; pct: number }>({ name: 'Dining', total: 8400, pct: 12 })
  const [transactions, setTransactions] = useState<any[]>([])

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/profile`).then(r => r.ok ? r.json() : null).catch(() => null),
      fetch(`${API}/api/transactions`).then(r => r.ok ? r.json() : []).catch(() => []),
      fetch(`${API}/api/goals`).then(r => r.ok ? r.json() : []).catch(() => []),
      fetch(`${API}/api/summary`).then(r => r.ok ? r.json() : []).catch(() => []),
    ]).then(([prof, txList, goals, summary]) => {
      if (prof) setProfile(prof)
      if (Array.isArray(txList)) {
        setTransactions(txList)
        const thisMonth = txList.filter((t: any) => t.date?.startsWith('2026-04'))
        const total = thisMonth.reduce((s: number, t: any) => s + (t.amount ?? 0), 0)
        setMonthTotal(total)
        // Estimate today
        const today = new Date().toISOString().slice(0, 10)
        const todayTx = txList.filter((t: any) => t.date === today)
        const todayTotal = todayTx.reduce((s: number, t: any) => s + (t.amount ?? 0), 0)
        if (todayTotal > 0) setTodaySpend(todayTotal)
      }
      if (Array.isArray(goals)) setSavingGoals(goals)
      if (Array.isArray(summary) && summary.length > 0) {
        const top = summary.sort((a: any, b: any) => b.total - a.total)[0]
        if (top) setTopCategory({ name: top.category, total: top.total, pct: 12 })
      }
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div style={{ padding: 'var(--space-5)' }}>
      <SkeletonCard />
      <div style={{ height: 'var(--space-4)' }} />
      <SkeletonCard />
    </div>
  )

  const budget = profile?.monthly_budget ?? 45000
  const budgetPct = Math.min(Math.round((monthTotal / budget) * 100), 100)
  const goalPct = savingGoals.length > 0 ?
    Math.min(Math.round((savingGoals[0].current_amount / savingGoals[0].target_amount) * 100), 100) : 42
  const remaining = Math.max(budget - monthTotal, 0)

  const narrativeText = todaySpend > avgSpend
    ? 'Today was a comfort spending day.'
    : 'Today was a controlled spending day.'
  const narrativeSub = todaySpend > avgSpend
    ? 'You spent more on food than usual.'
    : "You're building a healthy rhythm."

  return (
    <div className={styles.page}>
      {/* ── Top Bar ── */}
      <div className={styles.topBar}>
        <div className={styles.logoBlock}>
          <div className={styles.logoAvatar}>D</div>
          <div>
            <p className={styles.logoName}>DEKHO</p>
            <p className={styles.logoSub}>{getGreeting()}, {(profile?.name ?? 'Arjun').split(' ')[0]}</p>
          </div>
        </div>
        <button className={styles.iconBtn} onClick={() => navigate('/settings')} aria-label="Notifications">
          <Bell size={18} strokeWidth={1.75} />
        </button>
      </div>

      {/* ── Hero Narrative Card ── */}
      <div className={styles.px}>
        <div className={styles.heroCard}>
          <h1 className={styles.heroTitle}>{narrativeText}</h1>
          <p className={styles.heroSub}>{narrativeSub}</p>
          <button className={styles.tapWhy} onClick={() => setShowWhy(v => !v)}>
            Tap to see why
            {showWhy ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
          {showWhy && (
            <p className={styles.whyText}>
              Your {topCategory.name} spending is ₹{topCategory.total.toLocaleString('en-IN')} this month — {topCategory.pct}% higher than last month. Weekends tend to be your bigger spend days.
            </p>
          )}
        </div>
      </div>

      {/* ── 2-col Mini Stats ── */}
      <div className={styles.px}>
        <div className={styles.statsGrid}>
          <div className={styles.statCard}>
            <p className={styles.statLabel}>TODAY</p>
            <p className={styles.statValue}>{fmtINR(todaySpend)}</p>
          </div>
          <div className={styles.statCard}>
            <p className={styles.statLabel}>AVERAGE</p>
            <p className={styles.statValue}>
              {fmtINR(avgSpend)}
              <span className={styles.statUnit}>/day</span>
            </p>
          </div>
        </div>
      </div>

      {/* ── Top Focus + vs Last Month ── */}
      <div className={styles.px}>
        <div className={styles.focusRow}>
          <div className={styles.focusCard}>
            <p className={styles.focusLabel}>TOP FOCUS</p>
            <div className={styles.focusVal}>
              <span className={styles.focusCat}>{topCategory.name}</span>
              <span className={styles.focusIcon}>🍽️</span>
            </div>
          </div>
          <div className={styles.focusCard}>
            <p className={styles.focusLabel}>VS LAST MONTH</p>
            <div className={styles.focusVal}>
              <span className={styles.focusPct} data-up={topCategory.pct > 0}>
                +{topCategory.pct}%
              </span>
              <span className={styles.trendArrow} data-up={topCategory.pct > 0}>
                {topCategory.pct > 0 ? '↗' : '↘'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* ── Progress Bars ── */}
      <div className={styles.px}>
        <div className={styles.progressCard}>
          <div className={styles.progressRow}>
            <p className={styles.progressLabel}>MONTHLY SAVING TARGET</p>
            <p className={styles.progressPct}>{budgetPct}%</p>
          </div>
          <div className={styles.track}>
            <div className={styles.fill} style={{ width: `${budgetPct}%` }} />
          </div>

          <div style={{ height: 'var(--space-4)' }} />

          <div className={styles.progressRow}>
            <p className={styles.progressLabel}>INVESTMENT GOAL</p>
            <p className={styles.progressPct}>{goalPct}%</p>
          </div>
          <div className={styles.track}>
            <div className={styles.fill} style={{ width: `${goalPct}%` }} />
          </div>

          <div className={styles.remainingRow}>
            <p className={styles.progressLabel}>Remaining Budget</p>
            <p className={styles.remainingAmt}>{fmtINR(remaining)}</p>
          </div>
        </div>
      </div>

      {/* ── AI Nudge Card ── */}
      <div className={styles.px}>
        <div className={styles.nudgeCard}>
          <div className={styles.nudgeLeft}>
            <div className={styles.nudgeIconWrap}>
              <span className={styles.nudgeEmoji}>🎯</span>
            </div>
            <div>
              <p className={styles.nudgeTitle}>
                {transactions.length > 0
                  ? `${Math.min(transactions.filter((t: any) => t.date?.startsWith('2026-04')).length, 3)} days of controlled spending`
                  : '3 days of controlled spending'}
              </p>
              <p className={styles.nudgeSub}>You're building a healthy rhythm.</p>
            </div>
          </div>
          <button
            className={styles.nudgeBtn}
            onClick={() => navigate('/ask')}
            aria-label="Open AI chat"
          >
            💬
          </button>
        </div>
      </div>
    </div>
  )
}
