import type { HTMLAttributes, ReactNode } from 'react'
import styles from './Card.module.css'

type CardVariant = 'default' | 'elevated' | 'flat' | 'brand'
type CardPadding = 'default' | 'compact' | 'spacious'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant
  padding?: CardPadding
  hoverable?: boolean
  children: ReactNode
}

export default function Card({
  variant = 'default',
  padding = 'default',
  hoverable = false,
  className,
  children,
  ...rest
}: CardProps) {
  const classes = [
    styles.card,
    variant !== 'default' ? styles[variant] : '',
    padding !== 'default' ? styles[padding] : '',
    hoverable ? styles.hoverable : '',
    className ?? '',
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <div className={classes} {...rest}>
      {children}
    </div>
  )
}
