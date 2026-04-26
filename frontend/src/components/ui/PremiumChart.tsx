import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import styles from './SimpleChart.module.css'

interface DataPoint {
  label: string
  value: number
}

interface PremiumChartProps {
  type: 'Bar' | 'Pie'
  title?: string
  data: DataPoint[]
}

const COLORS = ['#10b981', '#f59e0b', '#3b82f6', '#ec4899', '#8b5cf6', '#f43f5e']

export default function PremiumChart({ type, title, data }: PremiumChartProps) {
  const isPie = type === 'Pie'

  // Standardize the data for Recharts
  const chartData = data.map((d) => ({
    name: d.label,
    amount: d.value
  }))

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div style={{ background: '#27272a', border: '1px solid #3f3f46', padding: '8px 12px', borderRadius: '8px', color: '#fff', fontSize: '12px' }}>
          <p style={{ margin: 0, fontWeight: 600 }}>{payload[0].name}</p>
          <p style={{ margin: 0, color: '#10b981' }}>₹{payload[0].value.toLocaleString('en-IN')}</p>
        </div>
      )
    }
    return null
  }

  return (
    <div className={styles.container} style={{ height: '220px' }}>
      {title && <div className={styles.title} style={{ marginBottom: '8px' }}>{title}</div>}
      
      <ResponsiveContainer width="100%" height="100%">
        {isPie ? (
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={50}
              outerRadius={70}
              paddingAngle={5}
              dataKey="amount"
              stroke="none"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        ) : (
          <BarChart data={chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
            <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#a1a1aa' }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 10, fill: '#a1a1aa' }} axisLine={false} tickLine={false} tickFormatter={(v) => `₹${v}`} />
            <Tooltip cursor={{ fill: '#27272a' }} content={<CustomTooltip />} />
            <Bar dataKey="amount" fill="#10b981" radius={[4, 4, 0, 0]} />
          </BarChart>
        )}
      </ResponsiveContainer>
    </div>
  )
}
