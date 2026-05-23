function formatTime(ts) {
  return new Date(ts).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })
}

function renderContent(text) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g)
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i} style={{ fontWeight: 600, color: 'inherit' }}>{part.slice(2, -2)}</strong>
    }
    return part.split('\n').map((line, j, arr) => (
      <span key={`${i}-${j}`}>
        {line}
        {j < arr.length - 1 && <br />}
      </span>
    ))
  })
}

function needsConfirmButtons(content) {
  const lower = content.toLowerCase()
  return (
    lower.includes('shall i place') ||
    lower.includes('shall i order') ||
    lower.includes('confirm this order') ||
    lower.includes('want me to place') ||
    lower.includes('shall i book') ||
    lower.includes('shall i checkout') ||
    lower.includes('should i place')
  )
}

export function Message({ message, onConfirm, onCancel }) {
  const isUser = message.role === 'user'
  const showConfirm = !isUser && needsConfirmButtons(message.content)

  if (isUser) {
    return (
      <div className="flex justify-end px-4 py-1 animate-fade-in-up">
        <div style={{ maxWidth: '72%' }}>
          <div style={{
            background: 'linear-gradient(135deg, #ff6633 0%, #e8502a 100%)',
            color: '#fff',
            borderRadius: '18px 18px 4px 18px',
            padding: '10px 14px',
            fontSize: '14px',
            lineHeight: 1.5,
            fontWeight: 400,
            boxShadow: '0 2px 12px rgba(255,102,51,0.2)',
          }}>
            {renderContent(message.content)}
          </div>
          <div style={{
            textAlign: 'right',
            color: 'var(--text-secondary)',
            fontSize: '11px',
            marginTop: 4,
            paddingRight: 2,
          }}>
            {formatTime(message.timestamp)}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex justify-start px-4 py-1 animate-fade-in-up" style={{ gap: 8 }}>
      {/* Avatar */}
      <div style={{
        width: 28,
        height: 28,
        borderRadius: 8,
        background: 'var(--accent-subtle)',
        border: '1px solid rgba(255,102,51,0.18)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '13px',
        flexShrink: 0,
        marginTop: 6,
      }}>
        🍱
      </div>

      <div style={{ maxWidth: '74%' }}>
        <div style={{
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border)',
          color: 'var(--text-primary)',
          borderRadius: '4px 18px 18px 18px',
          padding: '10px 14px',
          fontSize: '14px',
          lineHeight: 1.6,
        }}>
          {message.content ? renderContent(message.content) : (
            <span style={{ color: 'var(--text-secondary)' }}>...</span>
          )}
        </div>

        {showConfirm && (
          <div className="flex gap-2 mt-2 pl-1">
            <button
              onClick={onConfirm}
              style={{
                background: 'var(--success)',
                color: '#fff',
                border: 'none',
                borderRadius: 8,
                padding: '7px 16px',
                fontSize: '13px',
                fontWeight: 500,
                cursor: 'pointer',
                fontFamily: 'inherit',
                transition: 'opacity 0.15s',
              }}
              onMouseOver={e => e.target.style.opacity = '0.85'}
              onMouseOut={e => e.target.style.opacity = '1'}
            >
              Confirm
            </button>
            <button
              onClick={onCancel}
              style={{
                background: 'transparent',
                color: 'var(--danger)',
                border: '1px solid var(--danger)',
                borderRadius: 8,
                padding: '7px 16px',
                fontSize: '13px',
                fontWeight: 500,
                cursor: 'pointer',
                fontFamily: 'inherit',
                opacity: 0.8,
                transition: 'opacity 0.15s',
              }}
              onMouseOver={e => e.target.style.opacity = '1'}
              onMouseOut={e => e.target.style.opacity = '0.8'}
            >
              Cancel
            </button>
          </div>
        )}

        <div style={{
          color: 'var(--text-secondary)',
          fontSize: '11px',
          marginTop: showConfirm ? 6 : 4,
          paddingLeft: 2,
        }}>
          {formatTime(message.timestamp)}
        </div>
      </div>
    </div>
  )
}
