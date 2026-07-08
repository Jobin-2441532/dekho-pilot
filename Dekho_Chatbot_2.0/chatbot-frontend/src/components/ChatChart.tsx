import React from 'react'
import { PieChart, Pie, Cell, BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import type { ChartData } from '../store'
import { motion } from 'framer-motion'

const COLORS = ['#F4A261', '#E76F51', '#52B788', '#457B9D', '#8D99AE', '#A8DADC', '#5C3D2E']

interface Props { chart: ChartData }

const CustomTooltip = ({ active, payload, label }: Record<string, unknown>) => {
  if (active && Array.isArray(payload) && payload.length) {
    return (
      <div style={{ background: '#1E2235', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, padding: '8px 12px', fontSize: 12 }}>
        {label && <p style={{ color: '#A0AABB', marginBottom: 4 }}>{label as string}</p>}
        {(payload as Array<{name:string,value:number,color:string}>).map((p, i) => (
          <p key={i} style={{ color: p.color }}>
            {p.name}: <strong style={{ color: '#F0F4F8' }}>₹{Number(p.value).toLocaleString('en-IN')}</strong>
          </p>
        ))}
      </div>
    )
  }
  return null
}

export function ChatChart({ chart }: Props) {
  return (
    <motion.div
      className="chart-wrapper"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <p className="chart-wrapper__title">{chart.title}</p>

      {chart.type === 'pie' && (
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={chart.data as {name:string,value:number}[]}
              cx="50%" cy="50%"
              innerRadius={50} outerRadius={80}
              paddingAngle={3}
              dataKey="value"
            >
              {chart.data.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      )}

      {chart.type === 'bar' && (
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={chart.data as Record<string,unknown>[]} barCategoryGap="30%">
            <XAxis dataKey="category" tick={{ fill: '#8D99AE', fontSize: 10 }} axisLine={false} tickLine={false} />
            <YAxis hide />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="thisMonth" name="This Month" fill="#F4A261" radius={[4,4,0,0]} />
            <Bar dataKey="lastMonth" name="Last Month" fill="#8D99AE" radius={[4,4,0,0]} />
          </BarChart>
        </ResponsiveContainer>
      )}

      {chart.type === 'line' && (
        <ResponsiveContainer width="100%" height={160}>
          <LineChart data={chart.data as Record<string,unknown>[]}>
            <XAxis dataKey="date" tick={{ fill: '#8D99AE', fontSize: 9 }} axisLine={false} tickLine={false}
              tickFormatter={(v: string) => v.slice(5)} />
            <YAxis hide />
            <Tooltip content={<CustomTooltip />} />
            <Line type="monotone" dataKey="spend" stroke="#F4A261" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      )}

      {chart.type === 'progress' && chart.data[0] && (() => {
        const d = chart.data[0] as {name:string,pct:number,current:number,target:number,remaining:number,daysLeft?:number}
        const r = 28, circ = 2 * Math.PI * r
        const offset = circ * (1 - d.pct / 100)
        return (
          <div className="goal-card">
            <div className="goal-ring">
              <svg width="64" height="64" viewBox="0 0 64 64">
                <circle cx="32" cy="32" r={r} fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth="6" />
                <circle cx="32" cy="32" r={r} fill="none" stroke="#F4A261" strokeWidth="6"
                  strokeDasharray={circ} strokeDashoffset={offset}
                  strokeLinecap="round" transform="rotate(-90 32 32)"
                  style={{ transition: 'stroke-dashoffset 0.8s ease' }} />
              </svg>
              <div className="goal-ring__pct">{d.pct}%</div>
            </div>
            <div className="goal-card__info">
              <div className="goal-card__name">{d.name}</div>
              <div className="goal-card__meta">
                ₹{Number(d.current).toLocaleString('en-IN')} of ₹{Number(d.target).toLocaleString('en-IN')}<br />
                ₹{Number(d.remaining).toLocaleString('en-IN')} remaining
                {d.daysLeft != null && <> · {d.daysLeft} days left</>}
              </div>
            </div>
          </div>
        )
      })()}
    </motion.div>
  )
}
