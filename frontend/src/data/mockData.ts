// ─────────────────────────────────────────────
// Dekho — Shared Mock Data (Synthetic / Sample)
// All data is fabricated for prototype use only.
// ─────────────────────────────────────────────

export interface Transaction {
  id: string
  date: string        // ISO date string
  merchant: string
  amount: number
  category: string
  paymentMode: string
  notes?: string
  direction?: 'debit' | 'credit'
}

export interface SavingsGoal {
  id: string
  name: string
  emoji: string
  targetAmount: number
  currentAmount: number
  deadline: string
  color: string
}

export interface Budget {
  category: string
  limit: number
  spent: number
}

export interface Asset {
  id: string
  name: string
  type: 'savings' | 'investment' | 'ppf' | 'fd' | 'other'
  balance: number
  change: number        // % change this month
  institution: string
}

export const USER_PROFILE = {
  name: 'Arjun',
  fullName: 'Arjun Sharma',
  stage: 'Early career',
  purposes: ['Track spending', 'Build emergency fund', 'Save for a goal'],
  monthlyBudget: 45000,
}

export const CATEGORY_COLOR: Record<string, string> = {
  Food:           '#C2562A',
  Travel:         '#2563EB',
  Shopping:       '#7C3AED',
  Bills:          '#B45309',
  Entertainment:  '#BE185D',
  Health:         '#065F46',
  Subscriptions:  '#0E7490',
  Rent:           '#57534E',
  Other:          '#6B7280',
}

export const CATEGORY_BG: Record<string, string> = {
  Food:           '#FEF0E7',
  Travel:         '#EFF6FF',
  Shopping:       '#F5F3FF',
  Bills:          '#FFFBEB',
  Entertainment:  '#FDF2F8',
  Health:         '#ECFDF5',
  Subscriptions:  '#ECFEFF',
  Rent:           '#F5F5F4',
  Other:          '#F3F4F6',
}

export const CATEGORY_EMOJI: Record<string, string> = {
  Food:           '🍱',
  Travel:         '✈️',
  Shopping:       '🛍️',
  Bills:          '⚡',
  Entertainment:  '🎬',
  Health:         '💊',
  Subscriptions:  '📱',
  Rent:           '🏠',
  Other:          '💰',
}

// ── March 2026 Transactions ───────────────────
export const MARCH_TRANSACTIONS: Transaction[] = [
  { id: 'm01', date: '2026-03-01', merchant: 'Zomato',          amount: 420,  category: 'Food',          paymentMode: 'UPI' },
  { id: 'm02', date: '2026-03-01', merchant: 'House Rent',       amount: 18000, category: 'Rent',         paymentMode: 'Net Banking' },
  { id: 'm03', date: '2026-03-02', merchant: 'Swiggy',           amount: 315,  category: 'Food',          paymentMode: 'UPI' },
  { id: 'm04', date: '2026-03-03', merchant: 'BigBasket',        amount: 2850, category: 'Food',          paymentMode: 'UPI' },
  { id: 'm05', date: '2026-03-04', merchant: 'Uber',             amount: 280,  category: 'Travel',        paymentMode: 'UPI' },
  { id: 'm06', date: '2026-03-05', merchant: 'Amazon',           amount: 1499, category: 'Shopping',      paymentMode: 'Card' },
  { id: 'm07', date: '2026-03-06', merchant: 'Zomato',           amount: 550,  category: 'Food',          paymentMode: 'UPI' },
  { id: 'm08', date: '2026-03-07', merchant: 'Netflix',          amount: 649,  category: 'Subscriptions', paymentMode: 'Card' },
  { id: 'm09', date: '2026-03-08', merchant: 'Swiggy',           amount: 390,  category: 'Food',          paymentMode: 'UPI' },
  { id: 'm10', date: '2026-03-09', merchant: 'Rapido',           amount: 120,  category: 'Travel',        paymentMode: 'UPI' },
  { id: 'm11', date: '2026-03-10', merchant: 'Gym — Cult.fit',   amount: 1999, category: 'Health',        paymentMode: 'UPI' },
  { id: 'm12', date: '2026-03-11', merchant: 'Zomato',           amount: 680,  category: 'Food',          paymentMode: 'UPI' },
  { id: 'm12b',date: '2026-03-11', merchant: 'PhonePe — BBPS',  amount: 850,  category: 'Bills',         paymentMode: 'UPI', notes: 'Electricity bill' },
  { id: 'm13', date: '2026-03-12', merchant: 'Indiabulls',       amount: 2500, category: 'Bills',         paymentMode: 'Net Banking', notes: 'Internet + OTT bundle' },
  { id: 'm14', date: '2026-03-13', merchant: 'Swiggy',           amount: 275,  category: 'Food',          paymentMode: 'UPI' },
  { id: 'm15', date: '2026-03-14', merchant: 'Hyderabad Metro',  amount: 180,  category: 'Travel',        paymentMode: 'UPI' },
  { id: 'm16', date: '2026-03-15', merchant: 'Myntra',           amount: 2199, category: 'Shopping',      paymentMode: 'Card' },
  { id: 'm17', date: '2026-03-16', merchant: 'Zomato',           amount: 495,  category: 'Food',          paymentMode: 'UPI' },
  { id: 'm18', date: '2026-03-17', merchant: 'Spotify',          amount: 119,  category: 'Subscriptions', paymentMode: 'Card' },
  { id: 'm19', date: '2026-03-18', merchant: 'Nykaa',            amount: 880,  category: 'Shopping',      paymentMode: 'UPI' },
  { id: 'm20', date: '2026-03-19', merchant: 'BookMyShow',       amount: 720,  category: 'Entertainment', paymentMode: 'Card' },
  { id: 'm21', date: '2026-03-20', merchant: 'Swiggy',           amount: 420,  category: 'Food',          paymentMode: 'UPI' },
  { id: 'm22', date: '2026-03-21', merchant: 'Uber',             amount: 350,  category: 'Travel',        paymentMode: 'UPI' },
  { id: 'm23', date: '2026-03-22', merchant: 'D-Mart',           amount: 3200, category: 'Food',          paymentMode: 'UPI' },
  { id: 'm24', date: '2026-03-23', merchant: 'Amazon',           amount: 3499, category: 'Shopping',      paymentMode: 'Card' },
  { id: 'm25', date: '2026-03-24', merchant: 'Zomato',           amount: 580,  category: 'Food',          paymentMode: 'UPI' },
  { id: 'm26', date: '2026-03-25', merchant: 'PharmEasy',        amount: 650,  category: 'Health',        paymentMode: 'UPI' },
  { id: 'm27', date: '2026-03-26', merchant: 'Swiggy',           amount: 340,  category: 'Food',          paymentMode: 'UPI' },
  { id: 'm28', date: '2026-03-27', merchant: 'Rapido',           amount: 95,   category: 'Travel',        paymentMode: 'UPI' },
  { id: 'm29', date: '2026-03-28', merchant: 'IRCTC',            amount: 1450, category: 'Travel',        paymentMode: 'Net Banking' },
  { id: 'm30', date: '2026-03-29', merchant: 'Zomato',           amount: 610,  category: 'Food',          paymentMode: 'UPI' },
  { id: 'm31', date: '2026-03-30', merchant: 'YouTube Premium',  amount: 189,  category: 'Subscriptions', paymentMode: 'Card' },
  { id: 'm32', date: '2026-03-31', merchant: 'Swiggy',           amount: 290,  category: 'Food',          paymentMode: 'UPI' },
]

// ── April 2026 Transactions (1–14) ────────────
export const APRIL_TRANSACTIONS: Transaction[] = [
  { id: 'a01', date: '2026-04-01', merchant: 'House Rent',      amount: 18000, category: 'Rent',          paymentMode: 'Net Banking' },
  { id: 'a02', date: '2026-04-01', merchant: 'Zomato',          amount: 390,  category: 'Food',           paymentMode: 'UPI' },
  { id: 'a03', date: '2026-04-02', merchant: 'Swiggy',          amount: 260,  category: 'Food',           paymentMode: 'UPI' },
  { id: 'a04', date: '2026-04-03', merchant: 'Netflix',         amount: 649,  category: 'Subscriptions',  paymentMode: 'Card' },
  { id: 'a05', date: '2026-04-04', merchant: 'Uber',            amount: 220,  category: 'Travel',         paymentMode: 'UPI' },
  { id: 'a06', date: '2026-04-05', merchant: 'BigBasket',       amount: 2400, category: 'Food',           paymentMode: 'UPI' },
  { id: 'a07', date: '2026-04-06', merchant: 'BookMyShow',      amount: 540,  category: 'Entertainment',  paymentMode: 'Card' },
  { id: 'a08', date: '2026-04-07', merchant: 'PhonePe — BBPS', amount: 820,  category: 'Bills',          paymentMode: 'UPI', notes: 'Electricity' },
  { id: 'a09', date: '2026-04-08', merchant: 'Swiggy',          amount: 310,  category: 'Food',           paymentMode: 'UPI' },
  { id: 'a10', date: '2026-04-09', merchant: 'Rapido',          amount: 90,   category: 'Travel',         paymentMode: 'UPI' },
  { id: 'a11', date: '2026-04-10', merchant: 'Gym — Cult.fit',  amount: 1999, category: 'Health',         paymentMode: 'UPI' },
  { id: 'a12', date: '2026-04-11', merchant: 'Amazon',          amount: 1299, category: 'Shopping',       paymentMode: 'Card' },
  { id: 'a13', date: '2026-04-12', merchant: 'Zomato',          amount: 520,  category: 'Food',           paymentMode: 'UPI' },
  { id: 'a14', date: '2026-04-13', merchant: 'Spotify',         amount: 119,  category: 'Subscriptions',  paymentMode: 'Card' },
  { id: 'a15', date: '2026-04-14', merchant: 'Swiggy',          amount: 285,  category: 'Food',           paymentMode: 'UPI' },
]

export const ALL_TRANSACTIONS = [...APRIL_TRANSACTIONS, ...MARCH_TRANSACTIONS]

// ── Computed summaries ────────────────────────
export const APRIL_TOTAL   = APRIL_TRANSACTIONS.reduce((s, t) => s + t.amount, 0)   // ≈ 27,901
export const MARCH_TOTAL   = MARCH_TRANSACTIONS.reduce((s, t) => s + t.amount, 0)   // ≈ 44,488

export function getCategoryTotals(txns: Transaction[]): { category: string; total: number }[] {
  const map: Record<string, number> = {}
  txns.forEach(t => { map[t.category] = (map[t.category] ?? 0) + t.amount })
  return Object.entries(map)
    .map(([category, total]) => ({ category, total }))
    .sort((a, b) => b.total - a.total)
}

// ── Savings Goals ─────────────────────────────
export const SAVINGS_GOALS: SavingsGoal[] = [
  {
    id: 'g1',
    name: 'Emergency Fund',
    emoji: '🛡️',
    targetAmount: 90000,
    currentAmount: 45000,
    deadline: '2026-09-30',
    color: '#5C3D2E',
  },
  {
    id: 'g2',
    name: 'Goa Trip',
    emoji: '🏖️',
    targetAmount: 25000,
    currentAmount: 18000,
    deadline: '2026-06-15',
    color: '#2563EB',
  },
  {
    id: 'g3',
    name: 'New Laptop',
    emoji: '💻',
    targetAmount: 80000,
    currentAmount: 12000,
    deadline: '2026-12-31',
    color: '#7C3AED',
  },
]

// ── Budgets ───────────────────────────────────
export const BUDGETS: Budget[] = [
  { category: 'Food',          limit: 8000,  spent: getCategoryTotals(APRIL_TRANSACTIONS).find(c => c.category === 'Food')?.total  ?? 0 },
  { category: 'Shopping',      limit: 4000,  spent: getCategoryTotals(APRIL_TRANSACTIONS).find(c => c.category === 'Shopping')?.total ?? 0 },
  { category: 'Entertainment', limit: 2000,  spent: getCategoryTotals(APRIL_TRANSACTIONS).find(c => c.category === 'Entertainment')?.total ?? 0 },
  { category: 'Travel',        limit: 3000,  spent: getCategoryTotals(APRIL_TRANSACTIONS).find(c => c.category === 'Travel')?.total ?? 0 },
  { category: 'Subscriptions', limit: 1500,  spent: getCategoryTotals(APRIL_TRANSACTIONS).find(c => c.category === 'Subscriptions')?.total ?? 0 },
  { category: 'Health',        limit: 3000,  spent: getCategoryTotals(APRIL_TRANSACTIONS).find(c => c.category === 'Health')?.total ?? 0 },
]

// ── Assets ────────────────────────────────────
export const ASSETS: Asset[] = [
  { id: 'asset1', name: 'Savings Account',      type: 'savings',    balance: 128000, change: 4.2,  institution: 'HDFC Bank' },
  { id: 'asset2', name: 'Fixed Deposit',         type: 'fd',         balance: 54000,  change: 0,    institution: 'SBI' },
  { id: 'asset3', name: 'Mutual Fund (SIP)',      type: 'investment', balance: 45000,  change: 3.8,  institution: 'Zerodha Coin' },
  { id: 'asset4', name: 'PPF',                   type: 'ppf',        balance: 28000,  change: 0,    institution: 'India Post' },
]

export const NET_WORTH = ASSETS.reduce((s, a) => s + a.balance, 0) // 255,000

// ── Opportunities ─────────────────────────────
export const OPPORTUNITIES = [
  {
    id: 'op1',
    emoji: '🛡️',
    title: 'Complete your emergency fund',
    description: 'You\'re 50% there. Adding ₹5,000/month gets you fully covered in 9 months.',
    why: 'Your rent is ₹18,000/month — having 3 months covered means ₹54,000 minimum.',
    cta: 'Set a top-up goal',
    tag: 'Safety first',
    tagColor: 'positive' as const,
  },
  {
    id: 'op2',
    emoji: '📈',
    title: 'Start a small SIP',
    description: 'Even ₹1,000/month in a diversified index fund builds wealth quietly over time.',
    why: 'Your spending suggests ₹1,000–2,000 room for savings after rent and bills.',
    cta: 'Learn about SIPs',
    tag: 'Wealth building',
    tagColor: 'filter' as const,
  },
  {
    id: 'op3',
    emoji: '💳',
    title: 'Review your subscriptions',
    description: 'You\'re spending ₹957/month on subscriptions. That\'s ₹11,484 a year.',
    why: 'Netflix + Spotify + YouTube — are you using all three regularly?',
    cta: 'See subscriptions',
    tag: 'Quick saving',
    tagColor: 'warning' as const,
  },
  {
    id: 'op4',
    emoji: '🏠',
    title: 'Track your rent-to-expense ratio',
    description: 'Your rent is a significant portion of your expenses.',
    why: 'Keeping housing costs balanced gives room for other goals.',
    cta: 'See full breakdown',
    tag: 'You\'re on track',
    tagColor: 'positive' as const,
  },
]

// ── Pre-loaded chat messages ──────────────────
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  sources?: Array<{ label: string; text: string; type: 'data' | 'knowledge' }>
}

export const INITIAL_CHAT: ChatMessage[] = [
  {
    id: 'c0',
    role: 'assistant',
    content: 'Hi Arjun 👋 I\'m Ask Dekho — your personal finance companion. I can help you understand your spending, track savings goals, and answer finance questions. What would you like to know?',
    timestamp: '2026-04-14T08:00:00',
  },
  {
    id: 'c1',
    role: 'user',
    content: 'Where did I spend the most this month?',
    timestamp: '2026-04-14T08:01:00',
  },
  {
    id: 'c2',
    role: 'assistant',
    content: 'Your top categories in April so far are:\n\n🏠 Rent — ₹18,000 (biggest fixed cost)\n🍱 Food — ₹4,165 across 6 orders\n💊 Health — ₹1,999 (gym)\n\nFood is your most frequent spend — 6 transactions in 14 days. That\'s roughly every 2 days. Zomato and Swiggy alone account for ₹1,765 this month.',
    timestamp: '2026-04-14T08:01:15',
    sources: [
      { label: 'April Transactions (1–14)', text: 'Food: ₹4,165 across 6 orders. Rent: ₹18,000 fixed.', type: 'data' },
    ],
  },
]

export const QUICK_PROMPTS = [
  'Where did I spend most?',
  'How much can I save?',
  'Am I on track for my goals?',
  'What changed vs last month?',
  'Review my subscriptions',
]
