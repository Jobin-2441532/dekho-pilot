import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, TrendingUp, PieChart, ShieldCheck, Lightbulb } from 'lucide-react'
import styles from './SubPage.module.css'

const HOLDINGS = [
  { name: 'Nifty 50 Index Fund', type: 'Index Fund', value: 85000, returns: 14.2, units: 42.5, change: '+🟢' },
  { name: 'Parag Parikh Flexi Cap', type: 'Mutual Fund', value: 62000, returns: 18.6, units: 15.2, change: '+🟢' },
  { name: 'HDFC Mid-Cap Fund', type: 'Mutual Fund', value: 38000, returns: 22.1, units: 8.9, change: '+🟢' },
  { name: 'SGB 2.5% 2032', type: 'Sovereign Gold Bond', value: 20000, returns: 8.4, units: 2.0, change: '+🟢' },
]

const CHART_DATA = [155000, 162000, 170000, 178000, 196000, 205000]

function MiniSparkline() {
  const min = Math.min(...CHART_DATA)
  const max = Math.max(...CHART_DATA)
  const range = max - min
  const w = 280, h = 120
  const pts = CHART_DATA.map((v, i) => {
    const x = (i / (CHART_DATA.length - 1)) * w
    const y = h - ((v - min) / range) * (h - 20) + 10 // added padding
    return `${x},${y}`
  }).join(' ')
  
  const fillPath = `M0,${h} L${pts.split(' ').join(' L')} L${w},${h} Z`

  return (
    <div className={styles.growthChartArea}>
      <svg viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" className={styles.growthChartSvg} aria-hidden="true">
        <defs>
          <linearGradient id="growthGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#A1887F" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#A1887F" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path d={fillPath} fill="url(#growthGrad)" />
        <polyline points={pts} fill="none" stroke="#795548" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </div>
  )
}

export default function InvestmentsDetail() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'1M' | '3M' | '6M' | '1Y'>('6M')
  const fmt = (n: number) => '₹' + n.toLocaleString('en-IN')

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.header}>
        <button className={styles.backBtn} onClick={() => navigate('/assets')} aria-label="Back">
          <ArrowLeft size={20} strokeWidth={1.75} />
        </button>
        <div style={{ width: 36 }} />
      </div>

      <div className={styles.px}>
        {/* Hero */}
        <div className={styles.invHeroCard}>
          <p className={styles.invHeroLabel}>INVESTMENTS</p>
          <h1 className={styles.invHeroAmt}>₹2,50,000</h1>
          <p className={styles.invHeroAdded}>+₹9,400 this month (+3.9%)</p>
          
          <div className={styles.invHeroDivider} />
          
          <div className={styles.invHeroCols}>
            <div className={styles.invHeroCol}>
              <span className={styles.invHeroColLabel}>YOU INVESTED</span>
              <span className={styles.invHeroColAmt}>₹2,20,000</span>
            </div>
            <div className={styles.invHeroCol}>
              <span className={styles.invHeroColLabel}>CURRENT VALUE</span>
              <span className={styles.invHeroColAmt}>₹2,50,000</span>
            </div>
          </div>
        </div>

        {/* Portfolio Growth Chart */}
        <div className={styles.growthCard}>
          <div className={styles.growthHeader}>
            <div>
              <p className={styles.growthTitle}>Portfolio Growth</p>
              <p className={styles.growthSub}>Your investments are growing steadily</p>
            </div>
            <div className={styles.growthTabs}>
              {(['1M', '3M', '6M', '1Y'] as const).map(t => (
                <button key={t} className={`${styles.growthTab} ${activeTab === t ? styles.growthTabActive : ''}`} onClick={() => setActiveTab(t)}>{t}</button>
              ))}
            </div>
          </div>
          <MiniSparkline />
        </div>

        {/* Total Growth */}
        <div className={styles.totalGrowthCard}>
          <p className={styles.totalGrowthTitle}>Total Growth</p>
          <h2 className={styles.totalGrowthAmt}>₹30,000</h2>
          
          <div className={styles.totalGrowthBars}>
            <div className={styles.totalGrowthBar1} />
            <div className={styles.totalGrowthBar2} />
          </div>
          
          <div className={styles.totalGrowthLegends}>
            <div className={styles.totalGrowthLegend}>
              <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#A1887F' }} />
              ₹20K INVESTED
            </div>
            <div className={styles.totalGrowthLegend}>
              <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--color-primary)' }} />
              ₹10K MARKET
            </div>
          </div>
        </div>

        {/* Insight Card */}
        <div className={styles.invInsightCard}>
          <p className={styles.invInsightLabel}><TrendingUp size={14} /> INSIGHT</p>
          <p className={styles.invInsightText}>
            Most of your growth comes from <strong>Mutual Funds</strong>. Your stock investments are currently showing slightly higher <a href="#" className={styles.invInsightLink}>volatility</a> than last quarter.
          </p>
        </div>

        {/* Category Breakdown */}
        <p className={styles.catBreakdownHeader}>CATEGORY BREAKDOWN</p>
        <div className={styles.catBreakdownList}>
          {/* Mutual Funds */}
          <div className={`${styles.catCard} ${styles.catCardPrimary}`}>
            <div className={styles.catIcon}><PieChart size={20} strokeWidth={1.5} /></div>
            <div className={styles.catBody}>
              <p className={styles.catName}>Mutual Funds</p>
              <p className={styles.catSub}>56% OF PORTFOLIO</p>
            </div>
            <div className={styles.catRight}>
              <p className={styles.catAmt}>₹1,40,000</p>
              <p className={styles.catReturnGreen}>+₹12,000 (+9.3%)</p>
            </div>
          </div>

          {/* Stocks */}
          <div className={styles.catCard}>
            <div className={styles.catIcon} style={{ background: '#F5F5F5', color: 'var(--color-on-surface)' }}><TrendingUp size={20} strokeWidth={1.5} /></div>
            <div className={styles.catBody}>
              <p className={styles.catName}>Stocks</p>
              <p className={styles.catSub}>32% OF PORTFOLIO</p>
            </div>
            <div className={styles.catRight}>
              <p className={styles.catAmt}>₹80,000</p>
              <p className={styles.catReturnRed}>-₹2,500 (-3.1%)</p>
            </div>
          </div>

          {/* Gold */}
          <div className={styles.catCard}>
            <div className={styles.catIcon} style={{ background: '#F5F5F5', color: 'var(--color-on-surface)' }}>
              <div style={{ width: 14, height: 14, borderRadius: '50%', border: '2px solid currentColor', position: 'relative' }}>
                <div style={{ position: 'absolute', top: -4, right: -4, width: 10, height: 10, borderRadius: '50%', border: '2px solid currentColor', background: '#F5F5F5' }} />
              </div>
            </div>
            <div className={styles.catBody}>
              <p className={styles.catName}>Gold</p>
              <p className={styles.catSub}>12% OF PORTFOLIO</p>
            </div>
            <div className={styles.catRight}>
              <p className={styles.catAmt}>₹30,000</p>
              <p className={styles.catReturnGreen}>+₹1,900 (+6.7%)</p>
            </div>
          </div>
        </div>

        {/* Risk Level */}
        <div className={styles.riskLevelCard}>
          <div className={styles.riskLevelLeft}>
            <ShieldCheck size={20} className={styles.riskLevelIcon} strokeWidth={1.5} />
            <p className={styles.riskLevelTitle}>Risk Level: Moderate</p>
          </div>
          <div className={styles.riskLevelPills}>
            <div className={`${styles.riskLevelPill} ${styles.riskLevelPillActive}`} />
            <div className={`${styles.riskLevelPill} ${styles.riskLevelPillActive}`} />
            <div className={styles.riskLevelPill} />
            <div className={styles.riskLevelPill} />
          </div>
        </div>

        {/* Rebalance Note */}
        <div className={styles.rebalanceCard}>
          <Lightbulb size={18} className={styles.rebalanceIcon} />
          <p className={styles.rebalanceText}>
            Consider rebalancing your portfolio to maintain your moderate risk target.
          </p>
        </div>

        {/* Holdings (Preserved as requested) */}
        <p className={styles.sectionTitle} style={{ marginTop: 'var(--space-6)' }}>Your Holdings</p>
        <div className={styles.list}>
          {HOLDINGS.map((h) => (
            <div key={h.name} className={styles.holdingRow}>
              <div className={styles.holdingLeft}>
                <div className={styles.holdingIcon}>📈</div>
                <div>
                  <p className={styles.holdingName}>{h.name}</p>
                  <p className={styles.holdingType}>{h.type} · {h.units} units</p>
                </div>
              </div>
              <div className={styles.holdingRight}>
                <p className={styles.holdingAmt}>{fmt(h.value)}</p>
                <p className={styles.holdingReturn}>+{h.returns}%</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
