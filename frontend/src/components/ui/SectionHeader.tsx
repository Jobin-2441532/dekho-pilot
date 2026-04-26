import styles from './SectionHeader.module.css'

interface SectionHeaderProps {
  title: string
  actionLabel?: string
  onActionClick?: () => void
  subtitle?: string
}

export default function SectionHeader({ title, actionLabel, onActionClick, subtitle }: SectionHeaderProps) {
  return (
    <div className={styles.header}>
      <div className={styles.titleContainer}>
        <h2 className={styles.title}>{title}</h2>
        {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
      </div>
      {actionLabel && (
        <button className={styles.actionBtn} onClick={onActionClick}>
          {actionLabel} ↗
        </button>
      )}
    </div>
  )
}
