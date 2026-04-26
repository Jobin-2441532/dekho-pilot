import styles from './SpendingHeatmap.module.css'

interface SpendingHeatmapProps {
  data: number[][] // 5 weeks × 7 days
}

export default function SpendingHeatmap({ data }: SpendingHeatmapProps) {
  const flatData = data.flat().filter(Boolean)
  const max = flatData.length > 0 ? Math.max(...flatData) : 0
  const days = ['M', 'T', 'W', 'T', 'F', 'S', 'S']

  return (
    <div className={styles.heatmap}>
      <div className={styles.heatmapDays}>
        {days.map((d, i) => (
          <span key={i} className={styles.heatmapDay}>{d}</span>
        ))}
      </div>
      <div className={styles.heatmapGrid}>
        {data.map((week, wi) =>
          week.map((val, di) => {
            const intensity = max > 0 ? val / max : 0
            return (
              <div
                key={`${wi}-${di}`}
                className={styles.heatmapCell}
                title={`₹${val.toLocaleString('en-IN')}`}
                style={{
                  background: val === 0
                    ? 'var(--bg-surface-high)'
                    : `rgba(108,72,45,${0.15 + intensity * 0.85})`, // uses color-primary roughly
                }}
              />
            )
          })
        )}
      </div>
    </div>
  )
}
