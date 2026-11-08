import { ResponsiveContainer, AreaChart, Area, CartesianGrid, XAxis, YAxis, Tooltip, ReferenceLine } from 'recharts'
import type { Point } from '../types'

export default function LightCurve({ points, compact = false }: { points: Point[]; compact?: boolean }) {
  const data = points.filter((_, i) => !compact || i % 2 === 0)
  return <div className={`chart-wrap ${compact ? 'compact-chart' : ''}`}>
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data} margin={{ top: 8, right: 8, left: -18, bottom: 0 }}>
        <defs><linearGradient id="fluxGradient" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#9B8CFF" stopOpacity={0.25}/><stop offset="100%" stopColor="#9B8CFF" stopOpacity={0}/></linearGradient></defs>
        <CartesianGrid stroke="#202b40" strokeDasharray="3 5" vertical={false}/>
        <XAxis dataKey="time" tick={{ fill: '#71809c', fontSize: 10 }} tickLine={false} axisLine={false} tickFormatter={v => Number(v).toFixed(1)} />
        <YAxis domain={['auto', 'auto']} tick={{ fill: '#71809c', fontSize: 10 }} tickLine={false} axisLine={false} tickFormatter={v => Number(v).toFixed(3)} />
        <Tooltip contentStyle={{ background: '#111a2b', border: '1px solid #293650', borderRadius: 10, color: '#e8edfa', fontSize: 12 }} labelFormatter={v => `Time: ${Number(v).toFixed(3)}`} formatter={(v: number) => [v.toFixed(5), 'Normalized flux']}/>
        <ReferenceLine y={1} stroke="#56647d" strokeDasharray="4 5"/>
        <Area type="monotone" dataKey="flux" stroke="#a99aff" strokeWidth={1.7} fill="url(#fluxGradient)" dot={false} activeDot={{ r: 3, fill: '#d7ceff' }}/>
      </AreaChart>
    </ResponsiveContainer>
  </div>
}
