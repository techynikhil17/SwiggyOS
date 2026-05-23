import { useRef, useEffect, useState } from 'react'
import { Send, Trash2 } from 'lucide-react'
import { BudgetBar } from './BudgetBar'
import { Message } from './Message'
import { ToolIndicator } from './ToolIndicator'

const SUGGESTIONS = [
  { label: 'Plan my week', emoji: '📅' },
  { label: 'Restock groceries', emoji: '🛒' },
  { label: 'Find a restaurant', emoji: '🍽️' },
]

function SwiggyOSLogo() {
  return (
    <div className="flex flex-col items-center gap-3 mb-8">
      <div style={{
        width: 56,
        height: 56,
        borderRadius: 16,
        background: 'linear-gradient(135deg, #ff6633 0%, #e84e22 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '26px',
        boxShadow: '0 6px 24px rgba(255,102,51,0.25)',
      }}>
        🍱
      </div>
      <div style={{ textAlign: 'center' }}>
        <div className="gradient-text" style={{ fontWeight: 700, fontSize: '22px', letterSpacing: '-0.03em' }}>
          SwiggyOS
        </div>
        <div style={{ color: 'var(--text-secondary)', fontSize: '14px', marginTop: 4 }}>
          Your food life, automated.
        </div>
      </div>
    </div>
  )
}

export function Chat({ onSend, messages, isStreaming, currentTool, budget, error, onClearHistory }) {
  const [input, setInput] = useState('')
  const [inputFocused, setInputFocused] = useState(false)
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isStreaming])

  function adjustHeight() {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = Math.min(ta.scrollHeight, 116) + 'px'
  }

  function handleSend() {
    const text = input.trim()
    if (!text || isStreaming) return
    onSend(text)
    setInput('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  function handleConfirm() { onSend('Yes, confirm') }
  function handleCancel() { onSend('Cancel') }

  const isEmpty = messages.length === 0

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      <BudgetBar total={budget.total} spent={budget.spent} />

      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '12px 20px',
        borderBottom: '1px solid var(--border)',
        flexShrink: 0,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 32,
            height: 32,
            borderRadius: 9,
            background: 'linear-gradient(135deg, #ff6633 0%, #e84e22 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '15px',
            flexShrink: 0,
            boxShadow: '0 2px 8px rgba(255,102,51,0.3)',
          }}>
            🍱
          </div>
          <div>
            <div style={{ fontWeight: 600, fontSize: '14px', lineHeight: 1.2 }}>SwiggyOS</div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>
              {isStreaming ? (
                <span style={{ color: 'var(--accent)', fontSize: '11px' }}>Responding...</span>
              ) : 'AI food assistant'}
            </div>
          </div>
        </div>

        {messages.length > 0 && (
          <button
            onClick={onClearHistory}
            title="Clear conversation"
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              padding: 6,
              borderRadius: 6,
              display: 'flex',
              transition: 'color 0.15s',
            }}
            onMouseOver={e => e.currentTarget.style.color = 'var(--text-primary)'}
            onMouseOut={e => e.currentTarget.style.color = 'var(--text-secondary)'}
          >
            <Trash2 size={15} />
          </button>
        )}
      </div>

      {/* Error banner */}
      {error && (
        <div style={{
          background: 'rgba(239,68,68,0.08)',
          border: '1px solid rgba(239,68,68,0.2)',
          color: '#fca5a5',
          padding: '10px 20px',
          fontSize: '13px',
          flexShrink: 0,
        }}>
          {error}
        </div>
      )}

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', paddingTop: 12, paddingBottom: 12 }}>
        {isEmpty ? (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            padding: '40px 24px',
          }}>
            <SwiggyOSLogo />
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', justifyContent: 'center' }}>
              {SUGGESTIONS.map(s => (
                <button
                  key={s.label}
                  onClick={() => onSend(s.label)}
                  style={{
                    background: 'var(--bg-secondary)',
                    border: '1px solid var(--border)',
                    borderRadius: 20,
                    padding: '8px 16px',
                    fontSize: '13px',
                    color: 'var(--text-primary)',
                    cursor: 'pointer',
                    fontFamily: 'inherit',
                    transition: 'border-color 0.15s, background 0.15s, transform 0.15s',
                  }}
                  onMouseOver={e => {
                    e.currentTarget.style.borderColor = 'rgba(255,102,51,0.4)'
                    e.currentTarget.style.background = 'var(--bg-tertiary)'
                    e.currentTarget.style.transform = 'translateY(-1px)'
                  }}
                  onMouseOut={e => {
                    e.currentTarget.style.borderColor = 'var(--border)'
                    e.currentTarget.style.background = 'var(--bg-secondary)'
                    e.currentTarget.style.transform = 'translateY(0)'
                  }}
                >
                  {s.emoji} {s.label}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {messages.map((msg, i) => (
              <Message
                key={i}
                message={msg}
                onConfirm={handleConfirm}
                onCancel={handleCancel}
              />
            ))}
            {isStreaming && currentTool && <ToolIndicator tool={currentTool} />}
            {isStreaming && !currentTool && messages[messages.length - 1]?.role === 'user' && (
              <ToolIndicator tool={null} />
            )}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div style={{
        borderTop: '1px solid var(--border)',
        padding: '12px 16px',
        flexShrink: 0,
        background: 'var(--bg-primary)',
      }}>
        <div
          style={{
            display: 'flex',
            gap: 10,
            alignItems: 'flex-end',
            background: 'var(--bg-secondary)',
            border: `1px solid ${inputFocused ? 'rgba(255,102,51,0.4)' : 'var(--border)'}`,
            borderRadius: 14,
            padding: '8px 8px 8px 14px',
            transition: 'border-color 0.15s, box-shadow 0.15s',
            boxShadow: inputFocused ? '0 0 0 3px rgba(255,102,51,0.07)' : 'none',
          }}
        >
          <textarea
            ref={textareaRef}
            value={input}
            onChange={e => { setInput(e.target.value); adjustHeight() }}
            onKeyDown={handleKeyDown}
            onFocus={() => setInputFocused(true)}
            onBlur={() => setInputFocused(false)}
            placeholder="Ask anything about food, groceries, or dining..."
            disabled={isStreaming}
            rows={1}
            style={{
              flex: 1,
              background: 'none',
              border: 'none',
              outline: 'none',
              color: 'var(--text-primary)',
              fontSize: '14px',
              fontFamily: 'inherit',
              resize: 'none',
              lineHeight: '1.5',
              padding: '2px 0',
              maxHeight: 116,
              overflowY: 'auto',
              opacity: isStreaming ? 0.5 : 1,
            }}
          />
          <button
            onClick={handleSend}
            disabled={isStreaming || !input.trim()}
            style={{
              width: 34,
              height: 34,
              borderRadius: 9,
              border: 'none',
              background: isStreaming || !input.trim()
                ? 'var(--bg-tertiary)'
                : 'linear-gradient(135deg, #ff6633 0%, #e8502a 100%)',
              color: isStreaming || !input.trim() ? 'var(--text-secondary)' : '#fff',
              cursor: isStreaming || !input.trim() ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
              transition: 'background 0.15s, transform 0.1s',
              boxShadow: isStreaming || !input.trim() ? 'none' : '0 2px 8px rgba(255,102,51,0.25)',
            }}
            onMouseOver={e => {
              if (!isStreaming && input.trim()) e.currentTarget.style.transform = 'scale(1.05)'
            }}
            onMouseOut={e => { e.currentTarget.style.transform = 'scale(1)' }}
          >
            {isStreaming ? (
              <span style={{
                width: 14,
                height: 14,
                borderRadius: '50%',
                border: '2px solid var(--text-secondary)',
                borderTopColor: 'transparent',
                animation: 'spin 0.7s linear infinite',
                display: 'block',
              }} />
            ) : (
              <Send size={15} />
            )}
          </button>
        </div>
        <div style={{ textAlign: 'center', color: 'var(--text-secondary)', fontSize: '11px', marginTop: 8 }}>
          Enter to send · Shift+Enter for new line
        </div>
      </div>
    </div>
  )
}
