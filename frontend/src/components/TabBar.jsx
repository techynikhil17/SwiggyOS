const TABS = [
  { id: 'food',      label: 'Food',      emoji: '🍱', desc: 'Delivery' },
  { id: 'instamart', label: 'Instamart', emoji: '🛒', desc: 'Groceries' },
  { id: 'dineout',   label: 'Dineout',   emoji: '🍽️', desc: 'Dining' },
  { id: 'all',       label: 'All',       emoji: '⚡', desc: 'Hub' },
]

export function TabBar({ activeTab, onTabChange }) {
  return (
    <div style={{
      display: 'flex',
      background: 'var(--bg-secondary)',
      borderBottom: '1px solid var(--border)',
      height: 48,
      flexShrink: 0,
    }}>
      {TABS.map(tab => {
        const isActive = activeTab === tab.id
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            style={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 6,
              background: 'none',
              border: 'none',
              borderBottom: isActive ? '2px solid var(--accent)' : '2px solid transparent',
              color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
              cursor: 'pointer',
              fontFamily: 'inherit',
              fontSize: '13px',
              fontWeight: isActive ? 600 : 400,
              transition: 'color 0.15s, border-color 0.15s',
              paddingBottom: 0,
              paddingTop: 2,
            }}
            onMouseOver={e => {
              if (!isActive) e.currentTarget.style.color = 'var(--text-primary)'
            }}
            onMouseOut={e => {
              if (!isActive) e.currentTarget.style.color = 'var(--text-secondary)'
            }}
          >
            <span style={{ fontSize: 15 }}>{tab.emoji}</span>
            <span>{tab.label}</span>
            {!isActive && (
              <span style={{
                fontSize: '10px',
                color: 'var(--text-secondary)',
                opacity: 0.6,
              }}>
                {tab.desc}
              </span>
            )}
          </button>
        )
      })}
    </div>
  )
}
