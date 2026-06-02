import { useNavigate } from 'react-router-dom'
import { ArrowLeft, TrendingUp, Sparkles } from 'lucide-react'
import Button from '../components/ui/Button'

export default function Grow() {
  const navigate = useNavigate()

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--bg-app, #fbf9f6)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '24px',
      boxSizing: 'border-box',
      textAlign: 'center',
      fontFamily: 'var(--font-body, system-ui, sans-serif)'
    }}>
      <div style={{
        maxWidth: '440px',
        width: '100%',
        background: 'var(--bg-surface, #ffffff)',
        border: '1px solid var(--bg-surface-high, #eae5dd)',
        borderRadius: '24px',
        padding: '40px 32px',
        boxShadow: '0 12px 32px rgba(139, 99, 71, 0.06)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '24px',
        boxSizing: 'border-box'
      }}>
        {/* Icon container */}
        <div style={{
          width: '72px',
          height: '72px',
          borderRadius: '24px',
          background: 'rgba(139, 99, 71, 0.08)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--color-primary, #8B6347)',
          marginBottom: '8px'
        }}>
          <TrendingUp size={36} strokeWidth={1.5} />
        </div>

        {/* Text details */}
        <div>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            background: 'rgba(139, 99, 71, 0.1)',
            borderRadius: '20px',
            padding: '4px 12px',
            fontSize: '11px',
            fontWeight: 700,
            color: 'var(--color-primary, #8B6347)',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            marginBottom: '16px'
          }}>
            <Sparkles size={12} /> Coming Soon
          </div>
          
          <h1 style={{
            fontFamily: 'var(--font-headline, Georgia, serif)',
            fontSize: '28px',
            fontWeight: 700,
            color: 'var(--color-on-surface, #2d2621)',
            margin: '0 0 12px 0',
            lineHeight: 1.2
          }}>
            Grow Wealth
          </h1>
          
          <p style={{
            fontSize: '14px',
            lineHeight: '1.6',
            color: 'var(--color-muted, #7e7368)',
            margin: 0,
            padding: '0 8px'
          }}>
            Advanced investment recommendations, SIP planning guides, and long-term compounding pathfinders are being prepared. We are refining these models with financial wisdom.
          </p>
        </div>

        {/* Divider */}
        <div style={{
          width: '40px',
          height: '2px',
          background: 'var(--bg-surface-high, #eae5dd)',
          margin: '8px 0'
        }} />

        {/* CTA buttons */}
        <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <Button fullWidth onClick={() => navigate('/home')}>
            Back to Dashboard
          </Button>
          
          <button
            onClick={() => navigate(-1)}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--color-muted, #7e7368)',
              fontSize: '13px',
              fontWeight: 500,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              padding: '8px',
              fontFamily: 'inherit'
            }}
          >
            <ArrowLeft size={14} /> Go Back
          </button>
        </div>
      </div>
    </div>
  )
}
