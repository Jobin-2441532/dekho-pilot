/* ── Personalized Recommendations — Stitch match ── */
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Sparkles, TrendingUp, ShieldCheck, AlertCircle } from 'lucide-react'
import styles from './SubPage.module.css'

export default function PersonalizedRecommendations() {
  const navigate = useNavigate()

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <button className={styles.backBtn} onClick={() => navigate('/grow')} aria-label="Back">
          <ArrowLeft size={20} strokeWidth={1.75} />
        </button>
        <div style={{ width: 36 }} />
      </div>

      <div className={styles.px}>
        <p className={styles.pageSubtitle}>PERSONALIZED RECOMMENDATIONS</p>
        <h1 className={styles.pageTitle}>Recommended for you</h1>
        <p className={styles.pageDesc}>
          Based on your recent financial profile and goal trajectory, we've curated assets that balance growth with your specific liquidity needs.
        </p>

        {/* Why this fits you card */}
        <div className={styles.rationaleCard}>
          <div className={styles.rationaleHeader}>
            <Sparkles size={18} color="var(--color-on-primary)" />
            <span>Why this fits you</span>
          </div>
          <div className={styles.rationaleBody}>
            <div className={styles.rationaleSection}>
              <p className={styles.rationaleLabel}>STABILITY PROFILE</p>
              <p className={styles.rationaleText}>Your <strong>stable income</strong> patterns suggest a higher capacity for consistent monthly compounding.</p>
            </div>
            <div className={styles.rationaleSection}>
              <p className={styles.rationaleLabel}>SAFETY NET</p>
              <p className={styles.rationaleText}>You have maintained a <strong>3 months savings buffer</strong>, allowing for long-term equity exposure.</p>
            </div>
          </div>
        </div>

        {/* Fund cards */}
        <div className={styles.fundList}>
          {/* Liquid Fund */}
          <div className={styles.fundCard}>
            <div className={styles.fundHeader}>
              <div>
                <div className={styles.suitabilityPill}>
                  <ShieldCheck size={14} /> HIGH SUITABILITY
                </div>
                <h2 className={styles.fundName}>Liquid Fund</h2>
              </div>
              <div className={styles.fundSipBlock}>
                <p className={styles.fundSipLabel}>SUGGESTED SIP</p>
                <p className={styles.fundSipAmt}>₹5,000</p>
              </div>
            </div>
            <div className={styles.fundGrid}>
              <div className={styles.fundStat}>
                <p className={styles.fundStatLabel}>RISK LEVEL</p>
                <p className={styles.fundStatVal}><ShieldCheck size={14} color="var(--color-positive)"/> Low risk</p>
              </div>
              <div className={styles.fundStat}>
                <p className={styles.fundStatLabel}>USE CASE</p>
                <p className={styles.fundStatVal}>High liquidity</p>
              </div>
            </div>
            <div className={styles.fundFooter}>
              <p className={styles.fundDesc}>Ideal for short-term parking of idle cash with instant access.</p>
              <button className={styles.fundInvestBtn} onClick={() => navigate('/assets/investments/mutual-fund')}>
                INVEST NOW <span style={{marginLeft: 4}}>➔</span>
              </button>
            </div>
          </div>

          {/* Index Fund SIP */}
          <div className={styles.fundCardActive}>
            <div className={styles.fundHeader}>
              <div>
                <div className={styles.wealthCreatorPill}>
                  <TrendingUp size={14} /> WEALTH CREATOR
                </div>
                <h2 className={styles.fundName}>Index Fund SIP</h2>
              </div>
              <div className={styles.fundSipBlock}>
                <p className={styles.fundSipLabel}>SUGGESTED SIP</p>
                <p className={styles.fundSipAmt}>₹12,500</p>
              </div>
            </div>
            <div className={styles.fundGrid}>
              <div className={styles.fundStat}>
                <p className={styles.fundStatLabel}>RISK LEVEL</p>
                <p className={styles.fundStatVal}><AlertCircle size={14} color="#B45309"/> Moderate risk</p>
              </div>
              <div className={styles.fundStat}>
                <p className={styles.fundStatLabel}>USE CASE</p>
                <p className={styles.fundStatVal}>Long-term</p>
              </div>
            </div>
            <div className={styles.fundFooter}>
              <p className={styles.fundDesc}>Optimized for capital appreciation over a 5-10 year horizon.</p>
              <button className={styles.fundInvestBtn} onClick={() => navigate('/grow/index-fund-sip')}>
                INVEST NOW <span style={{marginLeft: 4}}>➔</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
