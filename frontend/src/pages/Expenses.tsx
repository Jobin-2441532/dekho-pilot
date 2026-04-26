/* ── Expenses Page — Stitch "Expenses with Spending Heatmap" ── */

import { useState, useEffect } from 'react'
import { ArrowLeft, Filter, Search } from 'lucide-react'
import { SkeletonCard } from '../components/ui/LoadingState'
import styles from './Expenses.module.css'

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

type InsightTab = 'Total' | 'By Category' | 'Ad hoc Period' | 'None'

const CATEGORY_EMOJI: Record<string, string> = {
  'Food & Dining': '🍴', 'Shopping': '🛍️', 'Transport': '🚗',
  'Entertainment': '🎬', 'Bills': '⚡', 'Health': '💊',
  'Housing': '🏠', 'Travel': '✈️', 'Others': '💰',
}

const CATEGORY_COLOR: Record<string, string> = {
  'Food & Dining': '#8B6347', 'Shopping': '#6C482D', 'Transport': '#A0785A',
  'Entertainment': '#C49478', 'Bills': '#D4B8A0', 'Health': '#B89070',
  'Housing': '#9E7355', 'Travel': '#7A5840', 'Others': '#E8D5C4',
}

/* Heatmap — 5 weeks × 7 days grid */
function SpendingHeatmap({ data }: { data: number[][] }) {
  const max = Math.max(...data.flat().filter(Boolean))
  const days = ['S', 'M', 'T', 'W', 'T', 'F', 'S']
  return (
    <div className={styles.heatmap}>
      <div className={styles.heatmapDays}>
        {days.map((d, i) => <span key={i} className={styles.heatmapDay}>{d}</span>)}
      </div>
      <div className={styles.heatmapGrid}>
        {data.map((week, wi) =>
          week.map((val, di) => {
            const cellDate = (wi * 7) + di + 1
            if (cellDate > 30) {
               return <div key={`${wi}-${di}`} className={styles.heatmapCellEmpty} />
            }
            const intensity = max > 0 ? val / max : 0
            return (
              <div
                key={`${wi}-${di}`}
                className={styles.heatmapCell}
                title={`₹${val.toLocaleString('en-IN')}`}
                style={{
                  background: val === 0
                    ? 'var(--bg-surface-high)'
                    : `rgba(108,72,45,${0.15 + intensity * 0.85})`,
                  color: intensity > 0.5 ? '#FFFFFF' : 'var(--color-muted)'
                }}
              >
                <span className={styles.heatmapDate}>{cellDate}</span>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}

/* Category bar (horizontal) */
function CategoryBar({ label, amount, total, emoji }: { label: string; amount: number; total: number; emoji: string }) {
  const pct = total > 0 ? (amount / total) * 100 : 0
  return (
    <div className={styles.catRow}>
      <div className={styles.catLeft}>
        <span className={styles.catEmoji}>{emoji}</span>
        <div>
          <p className={styles.catName}>{label}</p>
          <div className={styles.catTrack}>
            <div
              className={styles.catFill}
              style={{ width: `${pct}%`, background: CATEGORY_COLOR[label] ?? 'var(--color-primary)' }}
            />
          </div>
        </div>
      </div>
      <p className={styles.catAmt}>₹{amount.toLocaleString('en-IN')}</p>
    </div>
  )
}

export default function Expenses() {
  const [loading, setLoading] = useState(true)
  const [insightTab, setInsightTab] = useState<InsightTab>('Total')
  const [transactions, setTransactions] = useState<any[]>([])
  const [summary, setSummary] = useState<any[]>([])
  const [monthTotal, setMonthTotal] = useState(24500)

  // 5×7 heatmap data (5 weeks, Mon-Sun)
  const heatmapData: number[][] = [
    [800, 1200, 0, 600, 2100, 3400, 1800],
    [400, 0, 900, 1100, 700, 4290, 2200],
    [1200, 600, 0, 1850, 800, 1600, 900],
    [0, 1100, 800, 0, 1400, 2800, 1200],
    [340, 0, 0, 0, 0, 0, 0],
  ]

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/transactions`).then(r => r.ok ? r.json() : []).catch(() => []),
      fetch(`${API}/api/summary`).then(r => r.ok ? r.json() : []).catch(() => []),
    ]).then(([txList, sumList]) => {
      if (Array.isArray(txList)) {
        const thisMon = txList.filter((t: any) => t.date?.startsWith('2026-04'))
        setTransactions(thisMon.slice(0, 10))
        const total = thisMon.reduce((s: number, t: any) => s + (t.amount ?? 0), 0)
        if (total > 0) setMonthTotal(total)
      }
      if (Array.isArray(sumList) && sumList.length > 0) setSummary(sumList)
    }).finally(() => setLoading(false))
  }, [])

  const topCategories = summary.length > 0
    ? summary.sort((a, b) => b.total - a.total).slice(0, 3)
    : [
        { category: 'Food & Dining', total: 8400 },
        { category: 'Transport', total: 3500 },
        { category: 'Housing', total: 3500 },
      ]

  const committedSpend = 12500
  const topCat = topCategories[0]
  const topCatPct = Math.round((topCat.total / monthTotal) * 100)

  if (loading) return (
    <div style={{ padding: 'var(--space-5)' }}>
      <SkeletonCard />
      <div style={{ height: 'var(--space-4)' }} />
      <SkeletonCard />
    </div>
  )

  return (
    <div className={styles.page}>
      {/* ── Header ── */}
      <div className={styles.header}>
        <p className={styles.pageTitle}>Expenses</p>
        <div className={styles.headerRight}>
          <button className={styles.monthPill}>Apr 2026 ▾</button>
          <button className={styles.iconBtn} aria-label="Search"><Search size={16} /></button>
          <button className={styles.iconBtn} aria-label="Filter"><Filter size={16} /></button>
        </div>
      </div>

      {/* ── Total Outflow Card ── */}
      <div className={styles.px}>
        <div className={styles.outflowCard}>
          <div className={styles.outflowHeader}>
            <span className={styles.outflowLabel}>TOTAL OUTFLOW</span>
            <div className={styles.trendBadge}>
              <span className={styles.trendIcon}>↗</span> 12% higher
            </div>
          </div>
          <div className={styles.outflowAmounts}>
            <p className={styles.bigAmount}>₹{monthTotal.toLocaleString('en-IN')}</p>
            <p className={styles.bigAmountSub}>Spent this month</p>
          </div>
          <div className={styles.barChart}>
            {[20, 35, 30, 50, 45, 100].map((h, i) => {
              const months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN']
              return (
                <div key={i} className={styles.barCol}>
                  <div
                    className={styles.bar}
                    style={{ height: `${h}%`, background: i === 5 ? 'var(--color-primary)' : 'var(--bg-surface-highest)' }}
                  />
                  <span className={styles.barLabel}>{months[i]}</span>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* ── Insight Tabs + Categories ── */}
      <div className={styles.px}>
        <div className={styles.sectionHeader}>
          <p className={styles.sectionTitle}>Spending Insights</p>
          <button className={styles.seeAll}>↗</button>
        </div>
        <div className={styles.insightTabs} role="group">
          {(['Total', 'By Category', 'Ad hoc Period', 'None'] as InsightTab[]).map(t => (
            <button
              key={t}
              className={`${styles.insightTab} ${insightTab === t ? styles.insightTabActive : ''}`}
              onClick={() => setInsightTab(t)}
            >
              {t}
            </button>
          ))}
        </div>
        <div className={styles.catList}>
          {topCategories.map(cat => (
            <CategoryBar
              key={cat.category}
              label={cat.category}
              amount={cat.total}
              total={monthTotal}
              emoji={CATEGORY_EMOJI[cat.category] ?? '💰'}
            />
          ))}
        </div>
      </div>

      {/* ── Committed Spend & Review Cards ── */}
      <div className={styles.px}>
        <div className={styles.committedCardsContainer}>
          <div className={styles.committedCard}>
            <div className={styles.committedTop}>
              <div className={styles.committedIcon}>📅</div>
              <div className={styles.committedHeaderData}>
                <p className={styles.committedLabel}>COMMITTED SPEND</p>
                <p className={styles.committedAmt}>₹{committedSpend.toLocaleString('en-IN')}</p>
              </div>
            </div>
            
            <div className={styles.committedBreakdown}>
              <div className={styles.progressRow}>
                <div className={styles.progressLabels}>
                  <span>Subscriptions</span>
                  <span>₹4,500</span>
                </div>
                <div className={styles.progressTrack}>
                  <div className={styles.progressFillSub} style={{ width: '45%' }} />
                </div>
              </div>
              <div className={styles.progressRow}>
                <div className={styles.progressLabels}>
                  <span>EMI / Bills</span>
                  <span>₹8,000</span>
                </div>
                <div className={styles.progressTrack}>
                  <div className={styles.progressFillEmi} style={{ width: '70%' }} />
                </div>
              </div>
            </div>
          </div>

          <div className={styles.reviewCard}>
            <div className={styles.reviewLeft}>
              <div className={styles.reviewIcon}>📝</div>
              <div>
                <div className={styles.reviewDots}>
                  <span /> <span /> <span />
                </div>
                <p className={styles.reviewText}>3 transactions need review</p>
              </div>
            </div>
            <div className={styles.reviewChevron}>›</div>
          </div>
        </div>
      </div>

      {/* ── AI Insight card ── */}
      <div className={styles.px}>
        <div className={styles.aiCard}>
          <div className={styles.aiWatermark}>🍴</div>
          <p className={styles.aiCardLabel}>INSIGHT</p>
          <div className={styles.aiCardContent}>
            <p className={styles.aiCardTitle}>
              {topCat.category} is your highest expense (₹{topCat.total.toLocaleString('en-IN')})
            </p>
            <div className={styles.aiCardBadgeWrap}>
              <span className={styles.aiCardBadge}>+{topCatPct}%</span>
            </div>
          </div>
          <p className={styles.aiCardSub}>
            Try reducing Swiggy orders by 15% to save ₹1,200 this month.
          </p>

          <div className={styles.aiTarget}>
            <div className={styles.aiTargetHeader}>
              <span>TARGET SAVINGS</span>
              <span>₹1,200</span>
            </div>
            <div className={styles.aiTargetTrack}>
              <div className={styles.aiTargetFill} style={{ width: '25%' }} />
            </div>
          </div>
        </div>
      </div>

      {/* ── Heatmap ── */}
      <div className={styles.px}>
        <div className={styles.sectionHeader}>
          <p className={styles.sectionTitle}>Spending Pattern</p>
          <p className={styles.heatmapSub}>You tend to spend more on weekends</p>
        </div>
        <div className={styles.heatmapCard}>
          <SpendingHeatmap data={heatmapData} />
          <p className={styles.heatmapLegend}>↳ Darker = higher spend</p>
        </div>
      </div>

      {/* ── Transactions ── */}
      <div className={styles.px}>
        <div className={styles.sectionHeader}>
          <p className={styles.sectionTitle}>Transactions</p>
          <button className={styles.seeAll}>See All</button>
        </div>
        
        {/* Transaction Filters */}
        <div className={styles.scrollRow}>
          <button className={`${styles.filterPill} ${styles.filterPillActive}`}>Month</button>
          <button className={styles.filterPill}>By Category</button>
          <button className={styles.filterPill}>vs Prev Period</button>
          <button className={styles.filterPill}>Yearly</button>
        </div>

        <div className={styles.txList}>
          {(transactions.length > 0 ? transactions : [
            { id: 1, merchant: 'Blue Tokai Coffee', category: 'Food & Dining', amount: 340, date: 'Today' },
            { id: 2, merchant: 'ZARA India', category: 'Shopping', amount: 4290, date: 'Yesterday' },
            { id: 3, merchant: 'BESCOM Utility', category: 'Bills', amount: 1850, date: '2 days ago' },
          ]).map((tx: any) => (
            <div key={tx.id} className={styles.txRow}>
              <div className={styles.txIcon}>
                {CATEGORY_EMOJI[tx.category] ?? '💰'}
              </div>
              <div className={styles.txInfo}>
                <p className={styles.txMerchant}>{tx.merchant}</p>
                <p className={styles.txMeta}>
                  {tx.category} • {typeof tx.date === 'string' && !tx.date.includes('-')
                    ? tx.date
                    : new Date(tx.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
                </p>
              </div>
              <span className={styles.txAmt}>−₹{tx.amount.toLocaleString('en-IN')}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
