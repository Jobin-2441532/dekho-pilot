/* Budgets page — Stitch "Budget & Goals Ecosystem" */

import { useState, useEffect } from 'react'
import { Bell, Plus } from 'lucide-react'
import { useAppStore } from '../store/appStore'
import { SkeletonCard } from '../components/ui/LoadingState'
import styles from './Budgets.module.css'

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

interface BudgetCategory {
  label: string
  subtitle: string
  spent: number
  budget: number
}

export default function Budgets() {
  const { toggleChat } = useAppStore()
  const [loading, setLoading] = useState(true)
  const [goals, setGoals] = useState<any[]>([])

  const totalSpent = 34000
  const totalBudget = 48000
  const buffer = Math.max(totalBudget - totalSpent, 0)
  const overallPct = Math.min(Math.round((totalSpent / totalBudget) * 100), 100)

  const [expandedCategory, setExpandedCategory] = useState<string | null>(null)

  // Matches Stitch prototype categories with sub-categories
  const categories = [
    {
      label: 'Essentials',
      subtitle: 'NON-NEGOTIABLE',
      spent: 22000,
      budget: 40000,
      subcategories: [
        { label: 'Housing', emoji: '🏠', amount: 15000 },
        { label: 'Utilities', emoji: '⚡', amount: 2000 },
        { label: 'Food & groceries', emoji: '🛒', amount: 5000 },
        { label: 'Transport', emoji: '🚗', amount: 0 },
        { label: 'Healthcare', emoji: '💊', amount: 0 },
        { label: 'Insurance', emoji: '🛡️', amount: 0 },
        { label: 'Debt / EMIs', emoji: '💳', amount: 0 },
        { label: 'Family support', emoji: '👨‍👩‍👧‍👦', amount: 0 },
      ]
    },
    {
      label: 'Lifestyle',
      subtitle: 'FLEXIBLE',
      spent: 18000,
      budget: 15000,
      subcategories: [
        { label: 'Shopping', emoji: '🛍️', amount: 8000 },
        { label: 'Dining & entertainment', emoji: '🍽️', amount: 6000 },
        { label: 'Travel', emoji: '✈️', amount: 2000 },
        { label: 'Subscriptions', emoji: '📺', amount: 2000 },
      ]
    },
    {
      label: 'Future-oriented',
      subtitle: 'GOALS',
      spent: 10000,
      budget: 10000,
      subcategories: [
        { label: 'Education / learning', emoji: '📚', amount: 2000 },
        { label: 'Taxes / savings instruments', emoji: '💰', amount: 8000 },
      ]
    },
    {
      label: 'Buffer',
      subtitle: 'FLEXIBILITY',
      spent: 5000,
      budget: 20000,
      subcategories: [
        { label: 'Miscellaneous', emoji: '🔮', amount: 5000 },
      ]
    },
  ]

  const narrativeText = 'Cruising smoothly this month'
  const narrativeSub = 'Your lifestyle spending is slightly higher than usual, but covered by your buffer.'

  useEffect(() => {
    fetch(`${API}/api/goals`).then(r => r.ok ? r.json() : []).catch(() => [])
      .then((g) => { if (Array.isArray(g)) setGoals(g) })
      .finally(() => setLoading(false))
  }, [])

  const fmt = (n: number) => '₹' + n.toLocaleString('en-IN')

  if (loading) return (
    <div style={{ padding: 'var(--space-5)' }}>
      <SkeletonCard />
      <div style={{ height: 'var(--space-4)' }} />
      <SkeletonCard />
    </div>
  )

  const displayGoals = goals.length > 0 ? goals : [
    { id: 1, name: 'Trip to Goa', target_amount: 50000, current_amount: 25000, deadline: '2025-12-01', emoji: '🏖️' },
  ]

  return (
    <div className={styles.page}>
      {/* ── Top bar ── */}
      <div className={styles.topBar}>
        <div className={styles.logoBlock}>
          <div className={styles.logoAvatar}>D</div>
          <p className={styles.logoName}>Dekho</p>
        </div>
        <button className={styles.iconBtn} aria-label="Notifications"><Bell size={18} strokeWidth={1.75} /></button>
      </div>

      {/* ── Hero Card ── */}
      <div className={styles.px}>
        <div className={styles.heroCard}>
          <p className={styles.heroCategory}>BUDGET STATUS</p>
          <h1 className={styles.heroTitle}>{narrativeText}</h1>
          <div className={styles.heroMeta}>
            <div>
              <p className={styles.heroMetaLabel}>SPENT</p>
              <p className={styles.heroMetaVal}>{fmt(totalSpent)}</p>
            </div>
            <div>
              <p className={styles.heroMetaLabel}>BUDGET</p>
              <p className={styles.heroMetaVal}>{fmt(totalBudget)}</p>
            </div>
          </div>
          <div className={styles.heroTrack}>
            <div className={styles.heroFill} style={{ width: `${overallPct}%` }} />
          </div>
          <div className={styles.heroBuffer}>
            <p className={styles.heroBufferLabel}>Safe to spend: {fmt(buffer)}</p>
            <p className={styles.heroBufferPct}>{overallPct}%</p>
          </div>
        </div>
      </div>

      {/* ── Narrative text ── */}
      <div className={styles.px}>
        <p className={styles.narrativeSub}>{narrativeSub}</p>
      </div>

      {/* ── Categories ── */}
      <div className={styles.px}>
        <div className={styles.categoryList}>
          {categories.map((cat) => {
            const pct = Math.min(Math.round((cat.spent / cat.budget) * 100), 100)
            const isOver = cat.spent > cat.budget
            const isExpanded = expandedCategory === cat.label
            return (
              <div 
                key={cat.label} 
                className={styles.categoryCard}
                onClick={() => setExpandedCategory(isExpanded ? null : cat.label)}
              >
                <div className={styles.catHeader}>
                  <div className={styles.catTitleRow}>
                    <span className={styles.catLabel}>{cat.label}</span>
                    <span className={styles.catAmts}>{fmt(cat.spent)} / {fmt(cat.budget)}</span>
                  </div>
                  <div className={styles.catSubRow}>
                    <span className={styles.catSub}>{cat.subtitle}</span>
                    <span className={styles.catChevron}>
                      <svg width="12" height="8" viewBox="0 0 12 8" fill="none" style={{ transform: isExpanded ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }}>
                        <path d="M1 1.5L6 6.5L11 1.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </span>
                  </div>
                </div>
                <div className={styles.catTrack}>
                  <div
                    className={styles.catFill}
                    style={{
                      width: `${pct}%`,
                      background: isOver ? 'var(--color-negative)' : 'var(--color-primary)',
                    }}
                  />
                </div>
                {isExpanded && (
                  <div className={styles.subCatList}>
                    {cat.subcategories.map(sub => (
                      <div key={sub.label} className={styles.subCatRow}>
                        <span className={styles.subCatLabel}>{sub.emoji} {sub.label}</span>
                        <span className={styles.subCatAmt}>{fmt(sub.amount)}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* ── Goals ── */}
      <div className={styles.px}>
        <div className={styles.sectionHeader}>
          <p className={styles.sectionTitle}>Your Goals</p>
          <button className={styles.addBtn} onClick={toggleChat} aria-label="Add goal via chat">
            <Plus size={14} />
            Add Goal
          </button>
        </div>

        {displayGoals.map((goal: any) => {
          const pct = Math.min(Math.round((goal.current_amount / goal.target_amount) * 100), 100)
          const deadline = new Date(goal.deadline).toLocaleDateString('en-IN', { month: 'short', year: 'numeric' })
          return (
            <div key={goal.id} className={styles.goalCard}>
              {/* Goal image header */}
              <div className={styles.goalImageWrap}>
                <div className={styles.goalImageBg} style={{ backgroundImage: 'url("https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?q=80&w=800&auto=format&fit=crop")' }} />
                <div className={styles.goalImageOverlay}>
                  <p className={styles.goalImageTitle}>{goal.name} is getting closer ✨</p>
                </div>
              </div>

              {/* Goal details */}
              <div className={styles.goalDetails}>
                <div className={styles.goalMeta}>
                  <p className={styles.goalStatus}>You're on track for your goal.</p>
                  <div className={styles.goalDeadlineWrap}>
                    <span className={styles.goalDeadlineLabel}>TARGET</span>
                    <span className={styles.goalDeadline}>{deadline}</span>
                  </div>
                </div>

                <div className={styles.goalName}>{goal.name}</div>

                <div className={styles.goalProgress}>
                  <span className={styles.goalCurrent}>{fmt(goal.current_amount)}</span>
                  <span className={styles.goalSep}> /{goal.target_amount}</span>
                  <span className={styles.goalPct}>{pct}%</span>
                </div>

                <div className={styles.goalTrack}>
                  <div className={styles.goalFill} style={{ width: `${pct}%` }} />
                </div>

                <div className={styles.goalContribCard}>
                  <div className={styles.goalContribIcon}>⚡</div>
                  <p className={styles.goalContribText}>
                    <strong>₹5,000/month</strong> funded from your budget
                  </p>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
