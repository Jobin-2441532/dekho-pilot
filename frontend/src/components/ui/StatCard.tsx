import styles from './StatCard.module.css'

interface StatCardProps {
  label: string
  value: string
  trend?: {
    value: string
    positive: boolean
  }
}

export default function StatCard({ label, value, trend }: StatCardProps) {
  return (
    <div className={styles.card}>
      <p className={styles.label}>{label}</p>
      <p className={styles.value}>{value}</p>
      {trend && (
        <div className={`${styles.trend} ${trend.positive ? styles.positive : styles.negative}`}>
          {trend.positive ? '↑' : '↓'} {trend.value}
        </div>
      )}
    </div>
  )
}
