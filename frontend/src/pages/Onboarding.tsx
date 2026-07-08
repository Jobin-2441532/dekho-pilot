import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Lock } from 'lucide-react'
import Button from '../components/ui/Button'
import FloatingInput from '../components/ui/FloatingInput'
import styles from './Onboarding.module.css'

const PURPOSES = [
  { emoji: '📊', label: 'Track my spending' },
  { emoji: '🛡️', label: 'Build emergency fund' },
  { emoji: '🏖️', label: 'Save for a goal' },
  { emoji: '🧠', label: 'Understand my habits' },
  { emoji: '📋', label: 'Plan my budget' },
  { emoji: '📈', label: 'Learn investing' },
]

const STAGES = ['Just starting out', 'Growing my savings', 'Building wealth']

export default function Onboarding() {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [purposes, setPurposes] = useState<string[]>([])
  const [stage, setStage] = useState('')
  const [budget, setBudget] = useState('')

  const togglePurpose = (label: string) =>
    setPurposes(p => p.includes(label) ? p.filter(x => x !== label) : [...p, label])

  const finish = () => {
    localStorage.setItem('dekho_onboarded', 'true')
    navigate('/home')
  }

  return (
    <div className={styles.screen}>
      <div className={styles.inner}>
        {/* Step indicators */}
        <div className={styles.dots}>
          {[0, 1, 2].map(i => (
            <div key={i} className={`${styles.dot} ${step === i ? styles.active : ''}`} />
          ))}
        </div>

        {/* ── Step 0: Welcome ── */}
        {step === 0 && (
          <>
            <div className={styles.logo}>
              <div className={styles.logoMark}>D</div>
              <span className={styles.logoName}>Dekho</span>
            </div>

            <div className={styles.heading}>
              <h1>Your calm finance companion</h1>
              <p>Understand your money habits. Build better ones.</p>
            </div>

            <div className={styles.features}>
              {[
                { emoji: '💬', title: 'Ask anything',       desc: 'Chat with Ask Dekho about your spending in plain language.' },
                { emoji: '📊', title: 'See your patterns',  desc: 'Discover how, when, and where your money moves.' },
                { emoji: '🎯', title: 'Build real goals',   desc: 'Set savings goals and track progress without pressure.' },
                { emoji: '🔒', title: 'Sample data only',   desc: 'No bank access. No live data. Safe to explore.' },
              ].map(f => (
                <div key={f.emoji} className={styles.featureRow}>
                  <span className={styles.featureEmoji}>{f.emoji}</span>
                  <div className={styles.featureText}>
                    <strong>{f.title}</strong>
                    <span>{f.desc}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className={styles.navRow}>
              <Button fullWidth onClick={() => setStep(1)}>Get started</Button>
              <div className={styles.privacyNote}>
                <Lock size={12} />
                <span>This is a prototype — all data is synthetic and fictional.</span>
              </div>
            </div>
          </>
        )}

        {/* ── Step 1: Purpose ── */}
        {step === 1 && (
          <>
            <div className={styles.heading}>
              <h1>What matters to you right now?</h1>
              <p>Pick one or more — we'll personalise your experience around these.</p>
            </div>

            <div className={styles.purposeGrid}>
              {PURPOSES.map(({ emoji, label }) => (
                <div
                  key={label}
                  className={`${styles.purposeCard} ${purposes.includes(label) ? styles.selected : ''}`}
                  onClick={() => togglePurpose(label)}
                  role="checkbox"
                  aria-checked={purposes.includes(label)}
                  tabIndex={0}
                  onKeyDown={e => e.key === 'Enter' && togglePurpose(label)}
                >
                  <span className={styles.purposeEmoji}>{emoji}</span>
                  <span className={styles.purposeLabel}>{label}</span>
                </div>
              ))}
            </div>

            <div className={styles.navRow}>
              <Button
                fullWidth
                onClick={() => setStep(2)}
                disabled={purposes.length === 0}
              >
                Continue
              </Button>
              <button className={styles.backBtn} onClick={() => setStep(0)}>
                <ArrowLeft size={14} /> Back
              </button>
            </div>
          </>
        )}

        {/* ── Step 2: Profile ── */}
        {step === 2 && (
          <>
            <div className={styles.heading}>
              <h1>A little about your finances</h1>
              <p>This helps personalise insights. You can always change this later.</p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
              <div className={styles.optionGroup}>
                <p className={styles.optionGroupLabel}>Financial stage</p>
                <div className={styles.optionRow}>
                  {STAGES.map(s => (
                    <div
                      key={s}
                      className={`${styles.option} ${stage === s ? styles.selected : ''}`}
                      onClick={() => setStage(s)}
                      role="radio"
                      aria-checked={stage === s}
                      tabIndex={0}
                      onKeyDown={e => e.key === 'Enter' && setStage(s)}
                    >
                      {s}
                    </div>
                  ))}
                </div>
              </div>

              <FloatingInput
                label="Monthly spending budget (optional)"
                type="number"
                value={budget}
                onChange={e => setBudget(e.target.value)}
                helper="e.g. 40000 — your target for monthly expenses"
              />
            </div>

            <div className={styles.navRow}>
              <Button fullWidth onClick={finish}>
                Start exploring →
              </Button>
              <button className={styles.backBtn} onClick={() => setStep(1)}>
                <ArrowLeft size={14} /> Back
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
