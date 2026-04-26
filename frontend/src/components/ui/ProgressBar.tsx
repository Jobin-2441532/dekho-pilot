import styles from './ProgressBar.module.css'

type BarColor = 'brand' | 'positive' | 'warning' | 'negative'
type BarHeight = 'thin' | 'medium' | 'thick'

interface ProgressBarProps {
  label?: string
  current?: number
  target?: number
  percentage?: number   // 0-100, computed if not given
  color?: BarColor | string  // accepts CSS variable strings too
  height?: BarHeight
  showPercentage?: boolean
  showValue?: boolean        // alias for showPercentage
  className?: string
}

export default function ProgressBar({
  label,
  current,
  target,
  percentage,
  color = 'brand',
  height = 'thick',
  showPercentage = false,
  showValue,
  className,
}: ProgressBarProps) {
  const displayPct = showValue ?? showPercentage
  const pct =
    percentage !== undefined
      ? Math.min(Math.max(percentage, 0), 100)
      : target && current !== undefined
      ? Math.min(Math.max((current / target) * 100, 0), 100)
      : 0

  const formatValue = (v: number) =>
    v >= 1000 ? `₹${(v / 1000).toFixed(1)}k` : `₹${v}`

  return (
    <div className={`${styles.wrapper} ${className ?? ''}`}>
      {(label || (current !== undefined && target)) && (
        <div className={styles.header}>
          {label && <span className={styles.label}>{label}</span>}
          {current !== undefined && target && (
            <div className={styles.values}>
              <span className={styles.current}>{formatValue(current)}</span>
              <span className={styles.separator}>/</span>
              <span className={styles.target}>{formatValue(target)}</span>
            </div>
          )}
        </div>
      )}

      <div className={`${styles.track} ${styles[height]}`}>
        <div
          className={`${styles.fill} ${(color in {brand:1,positive:1,warning:1,negative:1}) ? styles[color as BarColor] : ''}`}
          style={{
            width: `${pct}%`,
            ...(!(color in {brand:1,positive:1,warning:1,negative:1}) ? { background: color } : {})
          }}
          role="progressbar"
          aria-valuenow={Math.round(pct)}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>

      {displayPct && (
        <span className={styles.percentage}>{Math.round(pct)}%</span>
      )}
    </div>
  )
}
