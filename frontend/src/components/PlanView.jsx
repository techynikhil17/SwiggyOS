import { X } from 'lucide-react'

export function PlanView({ plans, onOrder, onClose }) {
  if (!plans || plans.length === 0) return null

  return (
    <div style={{
      width: 320,
      flexShrink: 0,
      borderLeft: '1px solid var(--border)',
      background: 'var(--bg-secondary)',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      overflowY: 'auto',
      animation: 'fadeInUp 0.2s ease forwards',
    }}>
      {/* Header */}
      <div style={{
        padding: '16px 20px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: `linear-gradient(180deg, rgba(255,102,51,0.04) 0%, transparent 100%)`,
      }}>
        <div>
          <div style={{ fontWeight: 600, fontSize: '14px' }}>Meal plan</div>
          <div style={{ color: 'var(--text-secondary)', fontSize: '12px', marginTop: 2 }}>
            {plans.length} {plans.length === 1 ? 'meal' : 'meals'}
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

      {/* Cards */}
      <div style={{ padding: '12px 16px', display: 'flex', flexDirection: 'column', gap: 10 }}>
        {plans.map((plan, i) => (
          <div
            key={i}
            style={{
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border)',
              borderRadius: 12,
              padding: '12px 14px',
              transition: 'transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease',
              cursor: 'default',
            }}
            onMouseOver={e => {
              e.currentTarget.style.transform = 'translateY(-2px)'
              e.currentTarget.style.boxShadow = '0 6px 20px rgba(0,0,0,0.25)'
              e.currentTarget.style.borderColor = 'rgba(255,102,51,0.2)'
            }}
            onMouseOut={e => {
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = 'none'
              e.currentTarget.style.borderColor = 'var(--border)'
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
                background: 'linear-gradient(135deg, #ff6633 0%, #e8502a 100%)',
                color: '#fff',
                border: 'none',
                borderRadius: 8,
                padding: '7px 0',
                fontSize: '13px',
                fontWeight: 500,
                cursor: 'pointer',
                fontFamily: 'inherit',
                transition: 'opacity 0.15s',
              }}
              onMouseOver={e => e.target.style.opacity = '0.85'}
              onMouseOut={e => e.target.style.opacity = '1'}
            >
              Order now
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
