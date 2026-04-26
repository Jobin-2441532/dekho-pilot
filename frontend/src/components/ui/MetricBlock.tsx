import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import styles from './MetricBlock.module.css'

type MetricSize = 'sm' | 'md' | 'lg'
type ChangeDirection = 'up' | 'down' | 'neutral'

interface MetricBlockProps {
  label: string
  value: string | number
  currency?: string
  size?: MetricSize
  inverted?: boolean
  change?: {
    value: string
    direction: ChangeDirection
  }
  subtext?: string
  className?: string
}

const changeIcon: Record<ChangeDirection, typeof TrendingUp> = {
  up: TrendingUp,
  down: TrendingDown,
  neutral: Minus,
}

export default function MetricBlock({
  label,
  value,
  currency = '₹',
  size = 'md',
  inverted = false,
  change,
  subtext,
  className,
}: MetricBlockProps) {
  const wrapperClass = [
    styles.wrapper,
    styles[`size-${size}`],
    inverted ? styles.inverted : '',
    className ?? '',
  ]
    .filter(Boolean)
    .join(' ')

  const ChangeIcon = change ? changeIcon[change.direction] : null

  return (
    <div className={wrapperClass}>
      <span className={styles.label}>{label}</span>
      <div className={styles.valueRow}>
        {currency && <span className={styles.currency}>{currency}</span>}
        <span className={styles.value}>
          {typeof value === 'number' ? value.toLocaleString('en-IN') : value}
        </span>
        {change && (
          <span className={`${styles.change} ${styles[change.direction]}`}>
            {ChangeIcon && <ChangeIcon size={12} strokeWidth={2.5} />}
            {change.value}
          </span>
        )}
      </div>
      {subtext && <span className={styles.subtext}>{subtext}</span>}
    </div>
  )
}
