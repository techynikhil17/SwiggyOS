import { X } from 'lucide-react'

export function PlanView({ plans, onOrder, onClose }) {
  if (!plans || plans.length === 0) return null

  return (
    <div
      style={{
        width: 320,
        flexShrink: 0,
        borderLeft: '1px solid var(--border)',
        background: 'var(--bg-secondary)',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        overflowY: 'auto',
      }}
    >
      <div
        style={{
          padding: '16px 20px',
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div>
          <div style={{ fontWeight: 600, fontSize: '14px' }}>Meal plan</div>
          <div style={{ color: 'var(--text-secondary)', fontSize: '12px', marginTop: 2 }}>
            {plans.length} meals
          </div>
        </div>
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
            padding: 4,
            borderRadius: 6,
            display: 'flex',
            alignItems: 'center',
            transition: 'color 0.15s',
          }}
          onMouseOver={e => e.currentTarget.style.color = 'var(--text-primary)'}
          onMouseOut={e => e.currentTarget.style.color = 'var(--text-secondary)'}
        >
          <X size={16} />
        </button>
      </div>

      <div style={{ padding: '12px 16px', display: 'flex', flexDirection: 'column', gap: 10 }}>
        {plans.map((plan, i) => (
          <div
            key={i}
            style={{
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border)',
              borderRadius: 12,
              padding: '12px 14px',
            }}
          >
            <div className="flex items-start justify-between gap-2 mb-2">
              <div>
                <div style={{ fontSize: '14px', fontWeight: 500 }}>
                  {plan.emoji} {plan.meal}
                </div>
                <div style={{ color: 'var(--text-secondary)', fontSize: '12px', marginTop: 3 }}>
                  {plan.source}
                </div>
              </div>
              {plan.cost && (
                <div style={{ color: 'var(--text-secondary)', fontSize: '13px', whiteSpace: 'nowrap', paddingTop: 1 }}>
                  &#8377;{plan.cost}
                </div>
              )}
            </div>
            <button
              onClick={() => onOrder(plan)}
              style={{
                width: '100%',
                background: 'var(--accent)',
                color: '#fff',
                border: 'none',
                borderRadius: 8,
                padding: '7px 0',
                fontSize: '13px',
                fontWeight: 500,
                cursor: 'pointer',
                fontFamily: 'inherit',
                transition: 'background 0.15s',
              }}
              onMouseOver={e => e.target.style.background = 'var(--accent-hover)'}
              onMouseOut={e => e.target.style.background = 'var(--accent)'}
            >
              Order now
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
