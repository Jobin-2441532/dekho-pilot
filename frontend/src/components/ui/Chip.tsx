import type { HTMLAttributes, ReactNode } from 'react'
import styles from './Chip.module.css'

type ChipVariant = 'filter' | 'prompt' | 'positive' | 'warning' | 'negative'

interface ChipProps extends HTMLAttributes<HTMLDivElement> {
  variant?: ChipVariant
  active?: boolean
  showDot?: boolean
  icon?: ReactNode
  children: ReactNode
}

export default function Chip({
  variant = 'filter',
  active = false,
  showDot = false,
  icon,
  className,
  children,
  ...rest
}: ChipProps) {
  const classes = [
    styles.chip,
    styles[variant],
    active ? styles.active : '',
    className ?? '',
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <div className={classes} role={rest.onClick ? 'button' : undefined} tabIndex={rest.onClick ? 0 : undefined} {...rest}>
      {showDot && <span className={styles.dot} aria-hidden="true" />}
      {icon}
      {children}
    </div>
  )
}
