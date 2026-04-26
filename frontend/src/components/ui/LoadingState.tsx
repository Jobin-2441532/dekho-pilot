import type { ReactNode } from 'react'
import { InboxIcon, AlertCircle } from 'lucide-react'
import styles from './LoadingState.module.css'

/* ------------------------------------------------------------------ */
/* Skeleton primitives                                                   */
/* ------------------------------------------------------------------ */
interface SkeletonProps {
  width?: string
  height?: string
  className?: string
  circle?: boolean
}

export function Skeleton({ width, height = '14px', className, circle }: SkeletonProps) {
  return (
    <div
      className={`${styles.skeleton} ${circle ? styles.circle : styles.rect} ${className ?? ''}`}
      style={{ width, height, ...(circle ? { width: height, height } : {}) }}
      aria-hidden="true"
    />
  )
}

export function SkeletonLine({ short, medium }: { short?: boolean; medium?: boolean }) {
  const cls = short ? styles.short : medium ? styles.medium : styles.long
  return <div className={`${styles.skeleton} ${styles.line} ${cls}`} aria-hidden="true" />
}

/* ------------------------------------------------------------------ */
/* Skeleton Card                                                         */
/* ------------------------------------------------------------------ */
export function SkeletonCard() {
  return (
    <div className={styles.card} aria-busy="true" aria-label="Loading…">
      <div className={styles.header}>
        <Skeleton circle height="40px" />
        <div style={{ flex: 1 }}>
          <SkeletonLine medium />
          <SkeletonLine short />
        </div>
      </div>
      <div className={styles.lines}>
        <SkeletonLine />
        <SkeletonLine medium />
        <SkeletonLine short />
      </div>
    </div>
  )
}

/* ------------------------------------------------------------------ */
/* Spinner                                                               */
/* ------------------------------------------------------------------ */
export function Spinner() {
  return <div className={styles.spinner} role="status" aria-label="Loading" />
}

/* ------------------------------------------------------------------ */
/* Empty State                                                           */
/* ------------------------------------------------------------------ */
interface EmptyStateProps {
  icon?: ReactNode
  title: string
  description?: string
  action?: ReactNode
}

export function EmptyState({
  icon,
  title,
  description,
  action,
}: EmptyStateProps) {
  return (
    <div className={styles.empty} role="status">
      <div className={styles.emptyIcon}>{icon ?? <InboxIcon size={28} />}</div>
      <p className={styles.emptyTitle}>{title}</p>
      {description && (
        <p className={styles.emptyText}>{description}</p>
      )}
      {action}
    </div>
  )
}

/* ------------------------------------------------------------------ */
/* Error State                                                           */
/* ------------------------------------------------------------------ */
export function ErrorState({ message }: { message?: string }) {
  return (
    <EmptyState
      icon={<AlertCircle size={28} color="var(--color-negative)" />}
      title="Something went wrong"
      description={message ?? 'We could not load this information. Please try again.'}
    />
  )
}
