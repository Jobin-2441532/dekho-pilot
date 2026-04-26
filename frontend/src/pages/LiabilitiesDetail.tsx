import { useNavigate } from 'react-router-dom'
import { ArrowLeft, TrendingDown, Calendar, CreditCard, Landmark, User, Sparkles, ArrowRight } from 'lucide-react'
import styles from './SubPage.module.css'

export default function LiabilitiesDetail() {
  const navigate = useNavigate()

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <button className={styles.backBtn} onClick={() => navigate('/assets')} aria-label="Back">
          <ArrowLeft size={20} strokeWidth={1.75} />
        </button>
        <div style={{ width: 36 }} />
      </div>

      <div className={styles.px}>
        {/* Hero */}
        <div className={styles.liabHeroCard}>
          <p className={styles.liabHeroLabel}>MONEY YOU OWE</p>
          <h1 className={styles.liabHeroAmt}>₹27,500</h1>
          <div className={styles.liabHeroBadgeWrap}>
            <span className={styles.liabHeroBadge}><TrendingDown size={14} /> ₹3,000</span>
            reduced this month
          </div>
        </div>

        {/* Steady Progress */}
        <div className={styles.steadyCard}>
          <div className={styles.steadyHeader}>
            <div>
              <p className={styles.steadyTitle}>Steady Progress</p>
              <p className={styles.steadySub}>You're making steady progress</p>
            </div>
            <span className={styles.steadyPct}>18%</span>
          </div>
          <div className={styles.steadyTrack}>
            <div className={styles.steadyFill} style={{ width: '18%' }} />
          </div>
          <p className={styles.steadyNote}>You've reduced 18% of your total dues since January.</p>
        </div>

        {/* Upcoming Payments */}
        <div className={styles.upcomingCard}>
          <div className={styles.upcomingIconWrap}>
            <Calendar size={20} strokeWidth={2} />
          </div>
          <div>
            <p className={styles.upcomingLabel}>UPCOMING PAYMENTS</p>
            <p className={styles.upcomingTitle}>₹12,500 due this week</p>
          </div>
        </div>

        {/* Your Dues */}
        <p className={styles.sectionTitle} style={{ marginTop: 'var(--space-2)' }}>Your Dues</p>
        <div className={styles.duesList}>
          {/* Credit Card */}
          <div className={styles.dueCard}>
            <div className={styles.dueIcon}><CreditCard size={20} strokeWidth={1.5} /></div>
            <div className={styles.dueBody}>
              <p className={styles.dueName}>Credit Card</p>
              <span className={styles.dueSubPill}>Due in 8 days</span>
            </div>
            <p className={styles.dueAmt}>₹12,500</p>
          </div>
          
          {/* Personal Loan */}
          <div className={styles.dueCard}>
            <div className={styles.dueIcon}><Landmark size={20} strokeWidth={1.5} /></div>
            <div className={styles.dueBody}>
              <p className={styles.dueName}>Personal Loan</p>
              <span className={styles.dueSubText}>₹2,000 EMI monthly</span>
            </div>
            <p className={styles.dueAmt}>₹10,000</p>
          </div>

          {/* Friend */}
          <div className={styles.dueCard}>
            <div className={styles.dueIcon}><User size={20} strokeWidth={1.5} /></div>
            <div className={styles.dueBody}>
              <p className={styles.dueName}>Borrowed from Friend</p>
              <span className={styles.dueSubText}>No interest</span>
            </div>
            <p className={styles.dueAmt}>₹5,000</p>
          </div>
        </div>

        {/* Liabilities over time */}
        <div className={styles.liabChartCard}>
          <p className={styles.liabChartTitle}>Your liabilities over time</p>
          <div className={styles.liabBars}>
            <div className={styles.liabBar} style={{ height: '100%', background: 'rgba(141, 110, 99, 0.15)' }} />
            <div className={styles.liabBar} style={{ height: '90%', background: 'rgba(141, 110, 99, 0.25)' }} />
            <div className={styles.liabBar} style={{ height: '85%', background: 'rgba(141, 110, 99, 0.4)' }} />
            <div className={styles.liabBar} style={{ height: '70%', background: 'rgba(141, 110, 99, 0.6)' }} />
            <div className={styles.liabBar} style={{ height: '60%', background: 'rgba(141, 110, 99, 0.8)' }} />
            <div className={styles.liabBar} style={{ height: '50%', background: 'var(--color-primary)' }} />
          </div>
          <div className={styles.liabChartLegend}>
            <TrendingDown size={16} color="#81C784" strokeWidth={2} />
            Your liabilities are decreasing over time
          </div>
        </div>

        {/* Insight */}
        <div className={styles.invInsightCard} style={{ position: 'relative', overflow: 'hidden' }}>
          <p className={styles.invInsightLabel}><Sparkles size={14} /> INSIGHT</p>
          <p className={styles.invInsightText}>
            You are consistently reducing your liabilities. By maintaining this pace, you could be debt-free in 14 months.
          </p>
          {/* Subtle watermark circle */}
          <div style={{ position: 'absolute', bottom: -24, right: -12, width: 80, height: 80, borderRadius: '50%', border: '12px solid rgba(255,255,255,0.06)' }} />
        </div>

        {/* Smart Actions */}
        <p className={styles.sectionTitle}>Smart Actions</p>
        <div className={styles.actionList}>
          <div className={styles.actionCard}>
            Pay high-interest dues first
            <ArrowRight size={18} color="var(--color-muted)" />
          </div>
          <div className={styles.actionCard}>
            Reduce credit usage
            <ArrowRight size={18} color="var(--color-muted)" />
          </div>
        </div>

      </div>
    </div>
  )
}
