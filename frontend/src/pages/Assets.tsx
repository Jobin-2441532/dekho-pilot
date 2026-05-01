/* ── Assets Page — Stitch "Assets Overview - Updated Nav" ── */

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ChevronRight, Settings } from 'lucide-react'
import { SkeletonCard } from '../components/ui/LoadingState'
import { api } from '../lib/api'
import styles from './Assets.module.css'

const API = import.meta.env.VITE_API_URL ?? `http://${window.location.hostname}:8000`

/* Mini sparkline using SVG */
function Sparkline({ data, color = '#6C482D' }: { data: number[]; color?: string }) {
  if (data.length < 2) return null
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  const w = 200, h = 60
  const pts = data.map((v, i) => {
    const x = (i / (data.length - 1)) * w
    const y = h - ((v - min) / range) * h
    return `${x},${y}`
  }).join(' ')

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className={styles.sparkline} aria-hidden="true">
      <polyline
        points={pts}
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

export default function Assets() {
  const navigate = useNavigate()
  const [profile, setProfile] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'1W' | '1M' | '3M' | '1Y'>('1M')

  // Static data matching Stitch prototype values
  const netWorth = 342500
  const savings = 120000
  const investments = 205000
  const liabilities = 17500
  const monthGrowth = 12400

  const sparkData: Record<string, number[]> = {
    '1W': [335000, 337200, 336800, 338000, 340000, 341500, 342500],
    '1M': [320000, 324000, 322500, 328000, 331000, 338000, 342500],
    '3M': [295000, 305000, 310000, 315000, 325000, 335000, 342500],
    '1Y': [240000, 260000, 270000, 285000, 300000, 320000, 342500],
  }

  const growthBreakdown = [
    { label: 'Contributions', amount: 8000, bar: 65 },
    { label: 'Market growth', amount: 3200, bar: 26 },
    { label: 'Interest', amount: 1200, bar: 10 },
  ]

  useEffect(() => {
    api.get('/api/v1/dashboard/profile')
      .then((res: any) => setProfile(res))
      .catch((err: any) => console.error("Failed to load profile", err))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div style={{ padding: 'var(--space-5)' }}>
      <SkeletonCard />
      <div style={{ height: 'var(--space-4)' }} />
      <SkeletonCard />
    </div>
  )

  const fmt = (n: number) => '₹' + n.toLocaleString('en-IN')

  return (
    <div className={styles.page}>
      {/* ── Top Bar ── */}
      <div className={styles.topBar}>
        <p style={{ fontFamily: 'var(--font-headline)', fontSize: '24px', fontWeight: 'bold', color: 'var(--color-on-surface)', margin: 0 }}>Assets</p>
        <button className={styles.iconBtn} onClick={() => navigate('/settings')} aria-label="Settings">
          <Settings size={18} strokeWidth={1.75} />
        </button>
      </div>

      {/* ── Net Worth Hero ── */}
      <div className={styles.px}>
        <div className={styles.heroCard}>
          <p className={styles.heroLabel}>YOUR NET WORTH</p>
          <h1 className={styles.heroAmount}>{fmt(netWorth)}</h1>
          <div className={styles.heroChange}>
            <span className={styles.heroPct}>+{fmt(monthGrowth)}</span>
            <span className={styles.heroChangeSub}>this month</span>
          </div>
          <button className={styles.heroCTA}>Tap to see details →</button>
        </div>
      </div>

      {/* ── Performance Chart ── */}
      <div className={styles.px}>
        <div className={styles.chartCard}>
          <div className={styles.chartHeader}>
            <p className={styles.chartTitle}>Performance</p>
            <div className={styles.tabRow} role="group" aria-label="Time period">
              {(['1W', '1M', '3M', '1Y'] as const).map(t => (
                <button
                  key={t}
                  className={`${styles.tab} ${activeTab === t ? styles.tabActive : ''}`}
                  onClick={() => setActiveTab(t)}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>
          <div className={styles.chartArea}>
            <Sparkline data={sparkData[activeTab]} color="var(--color-primary)" />
          </div>
          <p className={styles.chartInsight}>
            💡 Most growth came from your investments this month
          </p>
        </div>
      </div>

      {/* ── Asset Category Cards ── */}
      <div className={styles.px}>
        <div className={styles.assetList}>
          <button
            className={styles.assetCard}
            onClick={() => navigate('/assets/savings')}
          >
            <div className={styles.assetLeft}>
              <div className={styles.assetDot} data-type="savings" />
              <div>
                <p className={styles.assetName}>Savings</p>
                <p className={styles.assetDesc}>Safe &amp; accessible</p>
              </div>
            </div>
            <div className={styles.assetRight}>
              <p className={styles.assetAmt}>{fmt(savings)}</p>
              <ChevronRight size={16} className={styles.chevron} />
            </div>
          </button>

          <div className={styles.assetDivider} />

          <button
            className={styles.assetCard}
            onClick={() => navigate('/assets/investments')}
          >
            <div className={styles.assetLeft}>
              <div className={styles.assetDot} data-type="investments" />
              <div>
                <p className={styles.assetName}>Investments</p>
                <p className={styles.assetDesc}>Growing your money</p>
              </div>
            </div>
            <div className={styles.assetRight}>
              <p className={`${styles.assetAmt} ${styles.assetAmtGreen}`}>{fmt(investments)}</p>
              <ChevronRight size={16} className={styles.chevron} />
            </div>
          </button>

          <div className={styles.assetDivider} />

          <button
            className={styles.assetCard}
            onClick={() => navigate('/assets/liabilities')}
          >
            <div className={styles.assetLeft}>
              <div className={styles.assetDot} data-type="liabilities" />
              <div>
                <p className={styles.assetName}>Liabilities</p>
                <p className={styles.assetDesc}>Money you owe</p>
              </div>
            </div>
            <div className={styles.assetRight}>
              <p className={`${styles.assetAmt} ${styles.assetAmtRed}`}>{fmt(liabilities)}</p>
              <ChevronRight size={16} className={styles.chevron} />
            </div>
          </button>
        </div>
      </div>

      {/* ── Growth Breakdown ── */}
      <div className={styles.px}>
        <div className={styles.breakdownCard}>
          <div className={styles.breakdownHeader}>
            <p className={styles.breakdownTitle}>Growth breakdown</p>
            <p className={styles.breakdownSub}>{fmt(monthGrowth)} earned this month</p>
          </div>
          {growthBreakdown.map(item => (
            <div key={item.label} className={styles.breakdownRow}>
              <div className={styles.breakdownMeta}>
                <p className={styles.breakdownLabel}>• {item.label}</p>
                <p className={styles.breakdownAmt}>{fmt(item.amount)}</p>
              </div>
              <div className={styles.breakdownTrack}>
                <div className={styles.breakdownFill} style={{ width: `${item.bar}%` }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Insight Card ── */}
      <div className={styles.px}>
        <div className={styles.insightCard}>
          <p className={styles.insightLabel}>TODAY'S INSIGHT</p>
          <p className={styles.insightText}>
            Your investments are performing well. 60% of your growth came from market gains this period.
          </p>
          <button className={styles.insightCTA}>Read full report</button>
        </div>
      </div>
    </div>
  )
}
