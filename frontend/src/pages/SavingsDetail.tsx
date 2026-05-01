import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, ArrowUpCircle, ShieldCheck, TrendingUp, Landmark, Lock, Wallet, ArrowRight, Target } from 'lucide-react'
import { api } from '../lib/api'
import styles from './SubPage.module.css'

export default function SavingsDetail() {
  const navigate = useNavigate()
  const [profile, setProfile] = useState<any>(null)

  useEffect(() => {
    api.get('/api/v1/dashboard/profile')
      .then((res: any) => setProfile(res))
      .catch((err: any) => console.error("Failed to load profile", err))
  }, [])

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <button className={styles.backBtn} onClick={() => navigate('/assets')} aria-label="Back">
          <ArrowLeft size={20} strokeWidth={1.75} />
        </button>
        <div style={{ width: 36 }} />
      </div>

      <div className={styles.px}>
        {/* Hero Card */}
        <div className={styles.savingsHeroCard}>
          <p className={styles.savingsHeroLabel}>SAVINGS</p>
          <h1 className={styles.savingsHeroAmt}>₹1,20,000</h1>
          <p className={styles.savingsHeroAdded}>
            <ArrowUpCircle size={16} /> + ₹8,000 added this month
          </p>
          <p className={styles.savingsHeroNote}>
            <em>Safe & accessible money</em>
          </p>
        </div>

        {/* Safety Level Card */}
        <div className={styles.safetyCard}>
          <div className={styles.safetyHeader}>
            <div>
              <h2 className={styles.safetyTitle}>Safety Level: High ✅</h2>
              <p className={styles.safetySub}>Covers 3.2 months of expenses</p>
            </div>
            <div className={styles.safetyIconWrap}>
              <ShieldCheck size={20} color="#1565C0" strokeWidth={2} />
            </div>
          </div>
          <div className={styles.safetyTrack}>
            <div className={styles.safetyFill} style={{ width: '80%' }} />
          </div>
          <p className={styles.safetyText}>
            You have a comfortable safety buffer. This provides a solid foundation for your long-term financial health.
          </p>
        </div>

        {/* Breakdown */}
        <div className={styles.breakdownHeader}>
          <h2 className={styles.sectionTitle} style={{ marginBottom: 0 }}>Breakdown</h2>
          <span className={styles.viewAllBtn}>VIEW ALL</span>
        </div>

        <div className={styles.breakdownList}>
          {/* Bank Account */}
          <div className={styles.bdCard}>
            <div className={styles.bdIcon}><Landmark size={20} color="var(--color-on-surface)" strokeWidth={1.5} /></div>
            <div className={styles.bdBody}>
              <p className={styles.bdName}>Bank Account</p>
              <p className={styles.bdSubBlue}>+₹5,000 added</p>
            </div>
            <p className={styles.bdAmt}>₹70,000</p>
          </div>

          {/* Fixed Deposit */}
          <div className={styles.bdCard}>
            <div className={styles.bdIcon}><Lock size={20} color="var(--color-on-surface)" strokeWidth={1.5} /></div>
            <div className={styles.bdBody}>
              <p className={styles.bdName}>Fixed Deposit</p>
              <p className={styles.bdSubGreen}>+₹1,200 interest</p>
            </div>
            <p className={styles.bdAmt}>₹30,000</p>
          </div>

          {/* Cash / Wallet */}
          <div className={styles.bdCard}>
            <div className={styles.bdIcon}><Wallet size={20} color="var(--color-on-surface)" strokeWidth={1.5} /></div>
            <div className={styles.bdBody}>
              <p className={styles.bdName}>Cash / Wallet</p>
              <p className={styles.bdSubGrey}>Physical currency</p>
            </div>
            <p className={styles.bdAmt}>₹20,000</p>
          </div>

          {/* Dekho Wallet */}
          <div className={styles.bdCard} style={{ background: 'var(--bg-surface-highest)', border: '1px solid var(--color-primary)' }}>
            <div className={styles.bdIcon} style={{ background: 'var(--color-primary)', color: 'white' }}><Target size={20} strokeWidth={1.5} /></div>
            <div className={styles.bdBody}>
              <p className={styles.bdName} style={{ color: 'var(--color-primary)' }}>Dekho Wallet</p>
              <p className={styles.bdSubGrey}>Savings goals funds</p>
            </div>
            <p className={styles.bdAmt}>₹{(profile?.dekhoWalletBalance || 0).toLocaleString('en-IN')}</p>
          </div>
        </div>

        {/* Chart Card */}
        <div className={styles.chartCardWrapper}>
          <h2 className={styles.chartTitleDark}>Your savings over time</h2>
          <p className={styles.chartSub}>LAST 6 MONTHS</p>
          
          <div className={styles.chartArea}>
            <svg viewBox="0 0 100 40" preserveAspectRatio="none" className={styles.chartSvg}>
              <defs>
                <linearGradient id="blueGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#E3F2FD" stopOpacity="1" />
                  <stop offset="100%" stopColor="#E3F2FD" stopOpacity="0" />
                </linearGradient>
              </defs>
              <path d="M0,35 Q15,30 25,36 T50,25 T75,10 L100,5 L100,40 L0,40 Z" fill="url(#blueGrad)" />
              <path d="M0,35 Q15,30 25,36 T50,25 T75,10 L100,5" fill="none" stroke="var(--color-primary)" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </div>

          <div className={styles.chartNoteBox}>
            <TrendingUp size={16} color="var(--color-primary)" className={styles.chartNoteIcon} strokeWidth={2} />
            <p className={styles.chartNoteText}>
              "You've been consistently increasing your savings by 7% month-over-month. You're building excellent momentum."
            </p>
          </div>
        </div>

        {/* AI Insight Card */}
        <div className={styles.aiInsightBox}>
          <p className={styles.aiInsightLabel}>AI INSIGHT</p>
          <h2 className={styles.aiInsightTitle}>
            You're building a strong savings base. You can start moving some money into investments.
          </h2>
          <p className={styles.aiInsightText}>
            With 3 months of expenses covered, your foundation is secure. Transitioning ₹15,000 to a low-risk index fund could yield an additional 8% annually.
          </p>
          <button className={styles.optimizeBtn} onClick={() => navigate('/grow/recommendations')}>
            Optimize My Portfolio
          </button>
        </div>

        {/* Bottom CTA Pill */}
        <button className={styles.bottomCtaPill} onClick={() => navigate('/grow')}>
          <span>Move idle money to grow faster</span>
          <ArrowRight size={20} strokeWidth={1.5} />
        </button>
      </div>
    </div>
  )
}
