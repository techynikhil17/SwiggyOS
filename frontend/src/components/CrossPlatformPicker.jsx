export function CrossPlatformPicker({ foodMessages, instamartMessages, dineoutMessages, onContinue }) {
  const tabs = [
    { id: 'food',      label: 'Food',      emoji: '🍱', messages: foodMessages },
    { id: 'instamart', label: 'Instamart', emoji: '🛒', messages: instamartMessages },
    { id: 'dineout',   label: 'Dineout',   emoji: '🍽️', messages: dineoutMessages },
  ]
  const active = tabs.filter(t => t.messages && t.messages.length > 0)
  if (active.length === 0) return null

  return (
    <div style={{ marginTop: 32, width: '100%', maxWidth: 480 }}>
      <div style={{
        color: 'var(--text-secondary)',
        fontSize: '11px',
        letterSpacing: '0.1em',
        marginBottom: 12,
        textAlign: 'center',
        textTransform: 'uppercase',
      }}>
        Continue from
      </div>
      {active.map(tab => {
        const lastMsg = tab.messages.filter(m => m.role === 'user').slice(-1)[0]
        if (!lastMsg) return null
        return (
          <button
            key={tab.id}
            onClick={() => onContinue(tab.id, tab.messages)}
            style={{
              width: '100%',
              marginBottom: 8,
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border)',
              borderRadius: 10,
              padding: '12px 16px',
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              cursor: 'pointer',
              fontFamily: 'inherit',
              transition: 'border-color 0.15s, background 0.15s',
              textAlign: 'left',
            }}
            onMouseOver={e => {
              e.currentTarget.style.borderColor = 'rgba(255,102,51,0.4)'
              e.currentTarget.style.background = 'var(--bg-tertiary)'
            }}
            onMouseOut={e => {
              e.currentTarget.style.borderColor = 'var(--border)'
              e.currentTarget.style.background = 'var(--bg-secondary)'
            }}
          >
            <span style={{ fontSize: 20 }}>{tab.emoji}</span>
            <div style={{ flex: 1, overflow: 'hidden' }}>
              <div style={{
                fontSize: 12,
                color: 'var(--accent)',
                fontWeight: 600,
                marginBottom: 2,
              }}>
                {tab.label}
              </div>
              <div style={{
                fontSize: 13,
                color: 'var(--text-primary)',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}>
                "{lastMsg.content}"
              </div>
            </div>
            <span style={{ color: 'var(--text-secondary)', fontSize: 13, flexShrink: 0 }}>
              Continue →
            </span>
          </button>
        )
      })}
    </div>
  )
}
