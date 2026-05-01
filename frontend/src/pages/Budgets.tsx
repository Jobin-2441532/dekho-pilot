import { useState, useEffect } from 'react'
import { Bell, Plus, Edit2, Trash2 } from 'lucide-react'
import { useAppStore } from '../store/appStore'
import { SkeletonCard } from '../components/ui/LoadingState'
import { useInsights } from '../hooks/useInsights'
import api from '../lib/api'
import styles from './Budgets.module.css'

const API = import.meta.env.VITE_API_BASE_URL ?? `http://${window.location.hostname}:8000`

interface BudgetCategory {
  label: string
  subtitle: string
  spent: number
  budget: number
}

const GOAL_IMAGES = [
  "https://picsum.photos/seed/dekho_goal1/800/400",
  "https://picsum.photos/seed/dekho_goal2/800/400",
  "https://picsum.photos/seed/dekho_goal3/800/400",
  "https://picsum.photos/seed/dekho_goal4/800/400",
  "https://picsum.photos/seed/dekho_goal5/800/400"
];

export default function Budgets() {
  const { toggleChat } = useAppStore()
  const [loading, setLoading] = useState(true)
  const [goals, setGoals] = useState<any[]>([])
  const [transactions, setTransactions] = useState<any[]>([])
  const [profile, setProfile] = useState<any>(null)

  const { insights, loading: insightsLoading } = useInsights()

  const [totalSpent, setTotalSpent] = useState(0)
  const [totalBudget, setTotalBudget] = useState(45000)

  // Edit Budget State
  const [isEditingBudget, setIsEditingBudget] = useState(false)
  const [newBudget, setNewBudget] = useState("")
  
  // Edit Category Budget State
  const [editCategoryBudget, setEditCategoryBudget] = useState<{label: string, budget: string} | null>(null)

  // Add Goal State
  const [isAddingGoal, setIsAddingGoal] = useState(false)
  const [goalName, setGoalName] = useState("")
  const [goalTarget, setGoalTarget] = useState("")
  const [goalDeadline, setGoalDeadline] = useState("")

  const buffer = Math.max(totalBudget - totalSpent, 0)
  const overallPct = Math.min(Math.round((totalSpent / (totalBudget || 1)) * 100), 100)

  const [expandedCategory, setExpandedCategory] = useState<string | null>(null)

  const [categoriesData, setCategoriesData] = useState<any[]>([
    {
      label: 'Essentials', subtitle: 'NON-NEGOTIABLE', spent: 0, budget: 25000,
      subcategories: [
        { label: 'Housing & Household', emoji: '🏠', amount: 0, match: ['Housing', 'Household'] },
        { label: 'Utilities', emoji: '⚡', amount: 0, match: ['Utilities'] },
        { label: 'Bills', emoji: '🧾', amount: 0, match: ['Bills'] },
        { label: 'Food & Dining', emoji: '🍴', amount: 0, match: ['Food & Dining'] },
        { label: 'Groceries', emoji: '🛒', amount: 0, match: ['Groceries'] },
        { label: 'Transport', emoji: '🚗', amount: 0, match: ['Transport'] },
        { label: 'Health', emoji: '💊', amount: 0, match: ['Health'] },
        { label: 'Personal Care', emoji: '🧴', amount: 0, match: ['Personal Care'] },
        { label: 'Insurance', emoji: '🛡️', amount: 0, match: ['Insurance'] },
        { label: 'Loan EMI', emoji: '💳', amount: 0, match: ['Loan EMI'] },
        { label: 'Credit Card', emoji: '💳', amount: 0, match: ['Credit Card'] },
      ]
    },
    {
      label: 'Lifestyle', subtitle: 'FLEXIBLE', spent: 0, budget: 10000,
      subcategories: [
        { label: 'Shopping', emoji: '🛍️', amount: 0, match: ['Shopping'] },
        { label: 'Entertainment', emoji: '🎬', amount: 0, match: ['Entertainment'] },
        { label: 'Travel', emoji: '✈️', amount: 0, match: ['Travel'] },
        { label: 'Subscriptions', emoji: '📺', amount: 0, match: ['Subscriptions'] },
        { label: 'Telecom', emoji: '📱', amount: 0, match: ['Telecom'] },
      ]
    },
    {
      label: 'Future-oriented', subtitle: 'GOALS', spent: 0, budget: 5000,
      subcategories: [
        { label: 'Investment', emoji: '💰', amount: 0, match: ['Investment'] },
      ]
    },
    {
      label: 'Buffer', subtitle: 'FLEXIBILITY', spent: 0, budget: 5000,
      subcategories: [
        { label: 'Others', emoji: '🔮', amount: 0, match: ['Others'] },
        { label: 'Services', emoji: '🛠️', amount: 0, match: ['Services'] },
        { label: 'Uncategorised', emoji: '❓', amount: 0, match: ['Uncategorised'] },
      ]
    },
  ])

  const narrativeText = totalSpent > totalBudget ? 'You have exceeded your budget' : 'Cruising smoothly this month'
  const narrativeSub = totalSpent > totalBudget ? 'You might need to dip into savings to cover this month.' : 'Your lifestyle spending is slightly higher than usual, but covered by your buffer.'

  const loadData = () => {
    Promise.all([
      api.get<any[]>('/api/v1/dashboard/goals').catch(() => []),
      api.get<any>('/api/v1/dashboard/profile').catch(() => null),
      api.get<any>('/api/v1/dashboard/transactions', { limit: 200 }).catch(() => ({ data: [] })),
    ]).then(([g, p, txRes]) => {
      if (Array.isArray(g)) setGoals(g)
      if (p) {
        setProfile(p)
        setTotalBudget(p.monthlyBudget || p.monthly_budget || 45000)
      }
      const txList = txRes?.data || []
      if (Array.isArray(txList)) {
        const now = new Date()
        const thisMonthTxs = txList.filter((tx: any) => {
          const d = new Date(tx.date)
          return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear()
        })
        setTransactions(thisMonthTxs)

        const total = thisMonthTxs.reduce((s: number, tx: any) =>
          s + (tx.direction === 'credit' ? 0 : (tx.amount ?? 0)), 0
        )
        setTotalSpent(total)

        // Calculate categories from real transaction data
        const newCats = [...categoriesData]
        newCats.forEach(cat => {
          const savedBudget = localStorage.getItem(`dekho_budget_${cat.label}`)
          if (savedBudget) cat.budget = parseFloat(savedBudget)
          cat.spent = 0
          cat.subcategories.forEach((sub: any) => { sub.amount = 0 })
        })
        thisMonthTxs.forEach((tx: any) => {
          if (tx.direction === 'credit' || (tx.amount ?? 0) < 0) return
          let found = false
          newCats.forEach(cat => {
            cat.subcategories.forEach((sub: any) => {
              if (sub.match.includes(tx.category)) {
                sub.amount += (tx.amount || 0)
                cat.spent += (tx.amount || 0)
                found = true
              }
            })
          })
          if (!found) {
            newCats[3].subcategories[0].amount += (tx.amount || 0)
            newCats[3].spent += (tx.amount || 0)
          }
        })
        setCategoriesData(newCats)
      }
    }).finally(() => setLoading(false))
  }

  useEffect(() => {
    loadData()
  }, [])

  const fmt = (n: number | null | undefined) => {
    if (n == null || isNaN(n)) return '₹0';
    return '₹' + n.toLocaleString('en-IN');
  }

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
        <p style={{ fontFamily: 'var(--font-headline)', fontSize: '24px', fontWeight: 'bold', color: 'var(--color-on-surface)', margin: 0 }}>Budgets & Goals</p>
        <button className={styles.iconBtn} aria-label="Notifications"><Bell size={18} strokeWidth={1.75} /></button>
      </div>

      {/* ── Pulse Card ── */}
      <div className={styles.px}>
        <div className={styles.pulseCard}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <div className={styles.pulseLabel} style={{ margin: 0 }}>MONTHLY PULSE</div>
            <button 
              onClick={() => { setNewBudget(totalBudget.toString()); setIsEditingBudget(true); }}
              style={{ background: 'none', border: 'none', color: '#FFF', fontSize: '12px', cursor: 'pointer', fontWeight: 'bold', textDecoration: 'underline' }}
            >
              EDIT BUDGET
            </button>
          </div>
          <div className={styles.pulseHeadline}>
            {insightsLoading ? 'Calculating...' : insights?.budgets.monthly_pulse.headline}
          </div>
          <div className={styles.pulseMeta}>
            <span>SPENT: {fmt(totalSpent)}</span>
            <span>BUDGET: {fmt(totalBudget)}</span>
          </div>
          <div className={styles.pulseBar}>
            <div
              className={styles.pulseBarFill}
              style={{ width: `${overallPct}%` }}
            />
          </div>
          <div className={styles.pulseSafe}>
            Safe to spend: {insights?.budgets.monthly_pulse.safe_to_spend}
          </div>
          <div className={styles.pulseSubtext}>{insights?.budgets.monthly_pulse.subtext}</div>
        </div>
      </div>

      {/* ── Categories ── */}
      <div className={styles.px}>
        <div className={styles.categoryList}>
          {categoriesData.map((cat) => {
            const pct = Math.min(Math.round((cat.spent / (cat.budget || 1)) * 100), 100)
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
                    <span className={styles.catLabel} style={{ display: 'flex', alignItems: 'center' }}>
                      {cat.label}
                      <button 
                        onClick={(e) => { e.stopPropagation(); setEditCategoryBudget({ label: cat.label, budget: cat.budget.toString() }) }}
                        style={{ background: 'none', border: 'none', marginLeft: '8px', cursor: 'pointer', color: 'var(--color-primary)', display: 'flex', alignItems: 'center', opacity: 0.7 }}
                        aria-label="Edit Section Budget"
                      >
                        <Edit2 size={12} />
                      </button>
                    </span>
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
                    {cat.subcategories.map((sub: any) => (
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
          <button className={styles.addBtn} onClick={() => setIsAddingGoal(true)} aria-label="Add goal">
            <Plus size={14} />
            Add Goal
          </button>
        </div>

        {insights?.budgets.goal_card && (
          <div className={styles.goalHeadline}>
            {insights.budgets.goal_card.headline}
          </div>
        )}

        {displayGoals.map((goal: any, index: number) => {
          const currentAmt = goal.currentAmount ?? goal.current_amount ?? 0;
          const targetAmt = goal.targetAmount ?? goal.target_amount ?? 1;
          const pct = Math.min(Math.round((currentAmt / targetAmt) * 100), 100)
          let deadline = 'No date'
          try {
            if (goal.deadline) {
              deadline = new Date(goal.deadline).toLocaleDateString('en-IN', { month: 'short', year: 'numeric' })
            }
          } catch (e) {
            console.error("Invalid date for goal:", goal)
          }
          return (
            <div key={goal.id} className={styles.goalCard}>
              {/* Goal image header */}
              <div className={styles.goalImageWrap}>
                <div className={styles.goalImageBg} style={{ backgroundImage: `url(${GOAL_IMAGES[index % GOAL_IMAGES.length]})` }} />
                <div className={styles.goalImageOverlay}>
                  <p className={styles.goalImageTitle}>{goal.name} is getting closer ✨</p>
                </div>
                {currentAmt <= 0 && (
                  <button 
                    onClick={async (e) => {
                      e.stopPropagation();
                      if (window.confirm('Are you sure you want to delete this goal?')) {
                        try {
                          const rawId = String(goal.id).replace(/^g/, '')
                          await api.delete(`/api/v1/dashboard/goals/${rawId}`)
                          loadData()
                        } catch (err) {
                          console.error('Failed to delete goal', err)
                        }
                      }
                    }}
                    style={{ position: 'absolute', top: '16px', right: '16px', background: 'rgba(0,0,0,0.6)', border: 'none', borderRadius: '50%', width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', cursor: 'pointer', zIndex: 10 }}
                    aria-label="Delete Goal"
                  >
                    <Trash2 size={16} />
                  </button>
                )}
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
                  <span className={styles.goalCurrent}>{fmt(currentAmt)}</span>
                  <span className={styles.goalSep}> /{fmt(targetAmt).replace('₹', '')}</span>
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

      {/* Modals */}
      {isEditingBudget && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
          <div style={{ background: 'var(--bg-surface)', padding: '24px', borderRadius: '16px', width: '100%', maxWidth: '400px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <h3 style={{ margin: 0 }}>Edit Monthly Budget</h3>
            <input type="number" value={newBudget} onChange={e => setNewBudget(e.target.value)} placeholder="Amount (e.g. 50000)" style={{ padding: '12px', borderRadius: '8px', border: '1px solid var(--color-outline)' }} />
            <div style={{ display: 'flex', gap: '12px' }}>
              <button onClick={() => setIsEditingBudget(false)} style={{ flex: 1, padding: '12px', borderRadius: '8px', border: '1px solid var(--color-outline)', background: 'transparent' }}>Cancel</button>
              <button onClick={async () => {
                try {
                  await api.post('/api/v1/dashboard/profile/budget', { monthly_budget: parseFloat(newBudget) })
                } catch { /* non-fatal */ }
                setTotalBudget(parseFloat(newBudget) || totalBudget)
                setIsEditingBudget(false)
                loadData()
              }} style={{ flex: 1, padding: '12px', borderRadius: '8px', border: 'none', background: 'var(--color-primary)', color: 'white', fontWeight: 'bold' }}>Save</button>
            </div>
          </div>
        </div>
      )}

      {editCategoryBudget && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
          <div style={{ background: 'var(--bg-surface)', padding: '24px', borderRadius: '16px', width: '100%', maxWidth: '400px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <h3 style={{ margin: 0 }}>Edit {editCategoryBudget.label} Budget</h3>
            <input type="number" value={editCategoryBudget.budget} onChange={e => setEditCategoryBudget({...editCategoryBudget, budget: e.target.value})} placeholder="Amount" style={{ padding: '12px', borderRadius: '8px', border: '1px solid var(--color-outline)' }} />
            <div style={{ display: 'flex', gap: '12px' }}>
              <button onClick={() => setEditCategoryBudget(null)} style={{ flex: 1, padding: '12px', borderRadius: '8px', border: '1px solid var(--color-outline)', background: 'transparent' }}>Cancel</button>
              <button onClick={() => {
                const updatedCats = categoriesData.map(c => 
                  c.label === editCategoryBudget.label ? { ...c, budget: parseFloat(editCategoryBudget.budget) || 0 } : c
                )
                setCategoriesData(updatedCats)
                localStorage.setItem(`dekho_budget_${editCategoryBudget.label}`, editCategoryBudget.budget)
                setEditCategoryBudget(null)
              }} style={{ flex: 1, padding: '12px', borderRadius: '8px', border: 'none', background: 'var(--color-primary)', color: 'white', fontWeight: 'bold' }}>Save</button>
            </div>
          </div>
        </div>
      )}

      {isAddingGoal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
          <div style={{ background: 'var(--bg-surface)', padding: '24px', borderRadius: '16px', width: '100%', maxWidth: '400px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <h3 style={{ margin: 0 }}>Add New Goal</h3>
            <input type="text" value={goalName} onChange={e => setGoalName(e.target.value)} placeholder="Goal Name (e.g. New Laptop)" style={{ padding: '12px', borderRadius: '8px', border: '1px solid var(--color-outline)' }} />
            <input type="number" value={goalTarget} onChange={e => setGoalTarget(e.target.value)} placeholder="Target Amount" style={{ padding: '12px', borderRadius: '8px', border: '1px solid var(--color-outline)' }} />
            <input type="date" value={goalDeadline} onChange={e => setGoalDeadline(e.target.value)} style={{ padding: '12px', borderRadius: '8px', border: '1px solid var(--color-outline)' }} />
            <div style={{ display: 'flex', gap: '12px' }}>
              <button onClick={() => setIsAddingGoal(false)} style={{ flex: 1, padding: '12px', borderRadius: '8px', border: '1px solid var(--color-outline)', background: 'transparent' }}>Cancel</button>
              <button onClick={async () => {
                try {
                  await api.post('/api/v1/dashboard/goals', {
                    name: goalName,
                    target_amount: parseFloat(goalTarget),
                    deadline: goalDeadline || null,
                  })
                  setIsAddingGoal(false)
                  setGoalName(''); setGoalTarget(''); setGoalDeadline('')
                  loadData()
                } catch { alert('Failed to save goal') }
              }} style={{ flex: 1, padding: '12px', borderRadius: '8px', border: 'none', background: 'var(--color-primary)', color: 'white', fontWeight: 'bold' }}>Save Goal</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
