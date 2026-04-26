import styles from './SimpleChart.module.css'

interface DataPoint {
  label: string
  value: number
}

interface SimpleChartProps {
  title?: string
  data: DataPoint[]
  color?: string
}

export default function SimpleChart({ title, data, color = 'var(--color-brand-primary)' }: SimpleChartProps) {
  // Find the maximum value to base the 100% width on
  const maxVal = Math.max(...data.map(d => d.value), 1)

  return (
    <div className={styles.container}>
      {title && <div className={styles.title}>{title}</div>}
      
      {data.map((item, idx) => {
        const percentage = Math.min(100, Math.max(0, (item.value / maxVal) * 100))
        return (
          <div key={idx} className={styles.barContainer}>
            <div className={styles.barHeader}>
              <span className={styles.label}>{item.label}</span>
              <span className={styles.value}>
                {new Intl.NumberFormat('en-IN', {
                  style: 'currency',
                  currency: 'INR',
                  maximumFractionDigits: 0
                }).format(item.value)}
              </span>
            </div>
            <div className={styles.track}>
              <div 
                className={styles.fill} 
                style={{ width: `${percentage}%`, backgroundColor: color }} 
              />
            </div>
          </div>
        )
      })}
    </div>
  )
}
