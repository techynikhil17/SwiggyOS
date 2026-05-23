export function BudgetBar({ total, spent }) {
  if (!total) return null

  const pct = Math.min((spent / total) * 100, 100)
  const barColor = pct > 75
    ? 'linear-gradient(90deg, #ef4444, #dc2626)'
    : pct > 50
    ? 'linear-gradient(90deg, #f59e0b, #d97706)'
    : 'linear-gradient(90deg, #ff6633, #e8502a)'

  return (
    <div style={{
      borderBottom: '1px solid var(--border)',
      background: 'var(--bg-secondary)',
      padding: '8px 20px 10px',
    }}>
      <div className="flex justify-between items-center mb-1.5">
        <span style={{ color: 'var(--text-secondary)', fontSize: '12px', fontWeight: 500, letterSpacing: '0.02em' }}>
          Monthly budget
        </span>
        <span style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>
          <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>
            &#8377;{spent.toLocaleString('en-IN')}
          </span>
          {' / '}&#8377;{total.toLocaleString('en-IN')}
        </span>
      </div>
      <div style={{
        height: 4,
        borderRadius: 2,
        background: 'var(--bg-tertiary)',
        overflow: 'hidden',
      }}>
        <div style={{
          height: '100%',
          width: `${pct}%`,
          background: barColor,
          borderRadius: 2,
          transition: 'width 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
        }} />
      </div>
    </div>
  )
}
