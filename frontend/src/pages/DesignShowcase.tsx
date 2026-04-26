import { useState } from 'react'
import {
  Card,
  Button,
  Chip,
  MetricBlock,
  ProgressBar,
  FloatingInput,
  ChatBubble,
  SourceInspector,
  SkeletonCard,
  EmptyState,
  Spinner,
  PageHeader,
  Section,
  Grid2,
  Grid3,
  ScrollRow,
} from '../components'
import { Sparkles, ArrowRight, Wallet, TrendingUp } from 'lucide-react'

const SAMPLE_SOURCES = [
  { label: 'October Transactions', text: 'Food spend: ₹8,200 across 23 transactions', type: 'data' as const },
  { label: 'Budgeting Guide', text: 'The 50/30/20 rule recommends 50% on needs, 30% wants, 20% savings', type: 'knowledge' as const },
]

export default function DesignShowcase() {
  const [activeChip, setActiveChip]   = useState('All')
  const [inputVal, setInputVal]       = useState('')
  const [btnLoading, setBtnLoading]   = useState(false)

  const chips = ['All', 'Food', 'Travel', 'Shopping', 'Bills', 'Entertainment']

  const handleBtnClick = () => {
    setBtnLoading(true)
    setTimeout(() => setBtnLoading(false), 2000)
  }

  return (
    <div>
      <PageHeader
        title="Design System"
        subtitle="Phase 1 — Component library showcase"
        action={
          <Button size="sm" variant="secondary" iconRight={<ArrowRight size={14} />}>
            Phase 2 →
          </Button>
        }
      />

      {/* ── Metric Blocks ───────────────────────────── */}
      <Section label="Metric Blocks">
        <Grid3>
          <Card>
            <MetricBlock
              label="This month's spend"
              value={24850}
              size="md"
              change={{ value: '12% vs last month', direction: 'up' }}
              subtext="Oct 1 – Oct 31"
            />
          </Card>
          <Card variant="brand">
            <MetricBlock
              label="Total savings"
              value={182000}
              size="md"
              inverted
              change={{ value: '₹8k added', direction: 'up' }}
              subtext="Across 3 goals"
            />
          </Card>
          <Card variant="elevated">
            <MetricBlock
              label="EMI & bills"
              value={11200}
              size="md"
              change={{ value: 'Same as last month', direction: 'neutral' }}
              subtext="Fixed commitments"
            />
          </Card>
        </Grid3>
      </Section>

      {/* ── Progress Bars ───────────────────────────── */}
      <Section label="Progress Bars">
        <Card>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
            <ProgressBar
              label="Emergency Fund"
              current={45000}
              target={90000}
              color="brand"
              height="thick"
              showPercentage
            />
            <ProgressBar
              label="Travel Goal — Goa"
              current={18000}
              target={25000}
              color="positive"
              height="thick"
              showPercentage
            />
            <ProgressBar
              label="Food budget used"
              current={8200}
              target={8000}
              color="warning"
              height="medium"
              showPercentage
            />
          </div>
        </Card>
      </Section>

      {/* ── Buttons ─────────────────────────────────── */}
      <Section label="Buttons">
        <Card>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-3)', alignItems: 'center' }}>
            <Button onClick={handleBtnClick} loading={btnLoading} iconLeft={<Sparkles size={16} />}>
              Ask Dekho
            </Button>
            <Button variant="secondary">Set a goal</Button>
            <Button variant="ghost">See all</Button>
            <Button variant="surface" iconRight={<ArrowRight size={14} />}>
              View details
            </Button>
            <Button size="sm" variant="primary">Small</Button>
            <Button size="lg" variant="primary">Large</Button>
          </div>
        </Card>
      </Section>

      {/* ── Chips ───────────────────────────────────── */}
      <Section label="Chips">
        <Card>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <div>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginBottom: 'var(--space-2)' }}>Filter chips</p>
              <ScrollRow>
                {chips.map(c => (
                  <Chip
                    key={c}
                    variant="filter"
                    active={activeChip === c}
                    onClick={() => setActiveChip(c)}
                  >
                    {c}
                  </Chip>
                ))}
              </ScrollRow>
            </div>
            <div>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginBottom: 'var(--space-2)' }}>Status chips</p>
              <div style={{ display: 'flex', gap: 'var(--space-2)', flexWrap: 'wrap' }}>
                <Chip variant="positive" showDot>On track</Chip>
                <Chip variant="warning" showDot>Over budget</Chip>
                <Chip variant="negative" showDot>Missed goal</Chip>
              </div>
            </div>
            <div>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginBottom: 'var(--space-2)' }}>Quick prompt chips</p>
              <ScrollRow>
                {['Where did I spend most?', 'How much can I save?', 'What changed this month?', 'Show my patterns'].map(p => (
                  <Chip key={p} variant="prompt">{p}</Chip>
                ))}
              </ScrollRow>
            </div>
          </div>
        </Card>
      </Section>

      {/* ── Floating Input ──────────────────────────── */}
      <Section label="Form Inputs">
        <Grid2>
          <FloatingInput
            label="Monthly income"
            type="number"
            value={inputVal}
            onChange={e => setInputVal(e.target.value)}
            iconRight={<Wallet size={16} />}
          />
          <FloatingInput
            label="Savings goal name"
            type="text"
            helper="e.g. Emergency fund, Travel, New phone"
          />
          <FloatingInput
            label="Error example"
            type="email"
            error="Please enter a valid email"
          />
          <FloatingInput
            label="Notes (textarea)"
            multiline
            helper="Optional — add context about this goal"
          />
        </Grid2>
      </Section>

      {/* ── Chat Bubbles ────────────────────────────── */}
      <Section label="Chat Bubbles">
        <Card>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
            <ChatBubble role="user" content="Where did I spend the most this month?" />
            <ChatBubble
              role="assistant"
              content={
                <span>
                  Your top category this month is <strong>Food & Dining</strong> at ₹8,200 across 23 transactions. That's about 33% of your total spend — slightly above your usual 28%.
                </span>
              }
              showAvatar
            />
            <SourceInspector sources={SAMPLE_SOURCES} />
            <ChatBubble role="user" content="Should I cut down?" />
            <ChatBubble isTyping showAvatar />
          </div>
        </Card>
      </Section>

      {/* ── States ──────────────────────────────────── */}
      <Section label="Loading & Empty States">
        <Grid2>
          <SkeletonCard />
          <Card>
            <EmptyState
              icon={<TrendingUp size={28} />}
              title="No goals yet"
              description="Set a savings goal to start tracking your progress."
              action={<Button size="sm">Create goal</Button>}
            />
          </Card>
        </Grid2>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)', marginTop: 'var(--space-4)' }}>
          <Spinner />
          <span style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)' }}>Loading your financial data…</span>
        </div>
      </Section>

      {/* ── Cards ───────────────────────────────────── */}
      <Section label="Card Variants">
        <Grid3>
          <Card hoverable>
            <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginBottom: 'var(--space-2)' }}>Default (hoverable)</p>
            <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)' }}>Warm surface with soft shadow. Hover to lift.</p>
          </Card>
          <Card variant="elevated">
            <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginBottom: 'var(--space-2)' }}>Elevated</p>
            <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)' }}>Slightly deeper surface tone with a stronger shadow.</p>
          </Card>
          <Card variant="flat">
            <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginBottom: 'var(--space-2)' }}>Flat</p>
            <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)' }}>No shadow — for nested or secondary content areas.</p>
          </Card>
        </Grid3>
      </Section>
    </div>
  )
}
