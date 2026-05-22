import { useEffect, useState } from 'react'
import { Zap } from 'lucide-react'
import { Chat } from './components/Chat'
import { PlanView } from './components/PlanView'
import { useChat } from './hooks/useChat'
import { getAuthStatus, loginWithSwiggy } from './api/chat'

function LoginScreen({ offline }) {
  return (
    <div
      style={{
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--bg-primary)',
      }}
    >
      <div style={{ textAlign: 'center', maxWidth: 360, padding: '0 24px' }}>
        <div
          style={{
            width: 64,
            height: 64,
            borderRadius: 18,
            background: 'var(--accent)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '30px',
            margin: '0 auto 20px',
          }}
        >
          🍱
        </div>

        <h1
          style={{
            fontWeight: 700,
            fontSize: '28px',
            letterSpacing: '-0.03em',
            marginBottom: 8,
            color: 'var(--text-primary)',
          }}
        >
          SwiggyOS
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '15px', marginBottom: 32, lineHeight: 1.5 }}>
          Your food life, automated.<br />
          <span style={{ fontSize: '13px' }}>Food delivery, groceries, and dining in one assistant.</span>
        </p>

        {offline ? (
          <div
            style={{
              background: 'rgba(239,68,68,0.1)',
              border: '1px solid rgba(239,68,68,0.2)',
              borderRadius: 10,
              padding: '12px 16px',
              color: '#fca5a5',
              fontSize: '13px',
              lineHeight: 1.5,
            }}
          >
            Backend offline.<br />
            <span style={{ color: 'var(--text-secondary)' }}>
              Run:{' '}
              <code style={{ fontFamily: 'monospace', background: 'rgba(255,255,255,0.05)', padding: '1px 5px', borderRadius: 4 }}>
                cd backend &amp;&amp; uvicorn main:app --reload
              </code>
            </span>
          </div>
        ) : (
          <button
            onClick={loginWithSwiggy}
            style={{
              width: '100%',
              background: 'var(--accent)',
              color: '#fff',
              border: 'none',
              borderRadius: 12,
              padding: '13px 0',
              fontSize: '15px',
              fontWeight: 600,
              cursor: 'pointer',
              fontFamily: 'inherit',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
              transition: 'background 0.15s',
            }}
            onMouseOver={e => e.currentTarget.style.background = 'var(--accent-hover)'}
            onMouseOut={e => e.currentTarget.style.background = 'var(--accent)'}
          >
            <Zap size={17} fill="currentColor" />
            Connect with Swiggy
          </button>
        )}

        <p style={{ color: 'var(--text-secondary)', fontSize: '12px', marginTop: 20 }}>
          Uses Swiggy OAuth 2.1. Your credentials are never stored.
        </p>
      </div>
    </div>
  )
}

export default function App() {
  const [authState, setAuthState] = useState('loading')
  const [plans, setPlans] = useState([])

  const { messages, isStreaming, currentTool, budget, error, sendMessage, clearHistory } = useChat()

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    if (params.get('auth') === 'ok') {
      window.history.replaceState({}, '', '/')
    }

    // TODO: remove DEV_BYPASS before production
    const DEV_BYPASS = true
    if (DEV_BYPASS) { setAuthState('authenticated'); return }

    getAuthStatus().then(status => {
      if (status.offline) {
        setAuthState('offline')
      } else if (status.authenticated) {
        setAuthState('authenticated')
      } else {
        setAuthState('unauthenticated')
      }
    })
  }, [])

  function handleOrderFromPlan(plan) {
    sendMessage(`Order ${plan.meal} from ${plan.source}`)
  }

  if (authState === 'loading') {
    return (
      <div
        style={{
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'var(--bg-primary)',
        }}
      >
        <div
          style={{
            width: 28,
            height: 28,
            borderRadius: '50%',
            border: '2px solid var(--border)',
            borderTopColor: 'var(--accent)',
            animation: 'spin 0.7s linear infinite',
          }}
        />
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    )
  }

  if (authState !== 'authenticated') {
    return <LoginScreen offline={authState === 'offline'} />
  }

  return (
    <div style={{ height: '100%', display: 'flex', overflow: 'hidden' }}>
      <div style={{ flex: 1, overflow: 'hidden' }}>
        <Chat
          messages={messages}
          isStreaming={isStreaming}
          currentTool={currentTool}
          budget={budget}
          error={error}
          onSend={sendMessage}
          onClearHistory={clearHistory}
        />
      </div>
      {plans.length > 0 && (
        <PlanView
          plans={plans}
          onOrder={handleOrderFromPlan}
          onClose={() => setPlans([])}
        />
      )}
    </div>
  )
}
