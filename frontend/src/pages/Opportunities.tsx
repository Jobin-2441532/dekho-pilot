import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Card from '../components/ui/Card'
import Chip from '../components/ui/Chip'
import Button from '../components/ui/Button'
import { PageHeader, Section } from '../components/layout/AppShell'
import { SkeletonCard, ErrorState } from '../components/ui/LoadingState'
import { api } from '../lib/api'
import { ArrowRight } from 'lucide-react'

export default function Opportunities() {
  const navigate = useNavigate()
  
  const [opportunities, setOpportunities] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.get<any[]>('/api/opportunities')
      .then(setOpportunities)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div><PageHeader title="Opportunities" subtitle="Next steps that fit where you are" /><Section><SkeletonCard /></Section></div>
  if (error) return <div><PageHeader title="Opportunities" subtitle="Next steps that fit where you are" /><ErrorState message={error} /></div>

  return (
    <div>
      <PageHeader
        title="Opportunities"
        subtitle="Next steps that fit where you are"
      />

      <Section>
        <Card variant="flat" padding="compact">
          <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', lineHeight: 1.6 }}>
            These suggestions are based on your spending profile and financial stage. They are informational — not financial advice.
          </p>
        </Card>
      </Section>

      <Section label="Suggested for you">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          {opportunities.map(op => (
            <Card key={op.id} hoverable>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                {/* Header */}
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--space-3)' }}>
                  <span style={{
                    fontSize: 'var(--text-2xl)', flexShrink: 0,
                    width: '48px', height: '48px', borderRadius: '12px',
                    background: 'var(--color-surface-2)', display: 'flex',
                    alignItems: 'center', justifyContent: 'center', lineHeight: 1,
                  }}>
                    {op.emoji}
                  </span>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', flexWrap: 'wrap', marginBottom: 'var(--space-1)' }}>
                      <p style={{ fontFamily: 'var(--font-headline)', fontWeight: 700, fontSize: 'var(--text-base)', color: 'var(--color-text-primary)' }}>
                        {op.title}
                      </p>
                      <Chip variant={op.tagColor as 'positive' | 'warning' | 'filter'}>{op.tag}</Chip>
                    </div>
                    <p style={{ fontFamily: 'var(--font-body)', fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
                      {op.description}
                    </p>
                  </div>
                </div>

                {/* Why this fits */}
                <div style={{
                  background: 'var(--color-surface-2)', borderRadius: 'var(--radius-md)',
                  padding: 'var(--space-3)', borderLeft: '3px solid var(--color-brand-light)',
                }}>
                  <p style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-brand-mid)', fontFamily: 'var(--font-body)', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>WHY THIS FITS YOU</p>
                  <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>{op.why}</p>
                </div>

                <Button
                  variant="secondary"
                  size="sm"
                  iconRight={<ArrowRight size={14} />}
                  onClick={() => navigate('/ask', { state: { prompt: op.cta } })}
                >
                  {op.cta}
                </Button>
              </div>
            </Card>
          ))}
        </div>
      </Section>
    </div>
  )
}
