import { useEffect, useState } from 'react'
import { Zap } from 'lucide-react'
import { Chat } from './components/Chat'
import { PlanView } from './components/PlanView'
import { TabBar } from './components/TabBar'
import { useTabChats } from './hooks/useTabChats'
import { getAuthStatus, loginWithSwiggy } from './api/chat'

const IS_DEV = import.meta.env.DEV

const CAPABILITIES = ['Food delivery', 'Groceries', 'Dining']

function LoginScreen({ offline, onDevBypass }) {
  return (
    <div
      style={{
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: `
          radial-gradient(ellipse 600px 500px at 50% 30%, rgba(255,102,51,0.08) 0%, transparent 70%),
          var(--bg-primary)
        `,
      }}
    >
      <div
        className="animate-fade-in-up"
        style={{ textAlign: 'center', maxWidth: 360, padding: '0 28px', width: '100%' }}
      >
        <div
          style={{
            width: 68,
            height: 68,
            borderRadius: 20,
            background: 'linear-gradient(135deg, #ff6633 0%, #e84e22 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '32px',
            margin: '0 auto 24px',
            boxShadow: '0 8px 32px rgba(255,102,51,0.28)',
          }}
        >
          🍱
        </div>

        <h1
          className="gradient-text"
          style={{
            fontWeight: 700,
            fontSize: '36px',
            letterSpacing: '-0.04em',
            marginBottom: 10,
            lineHeight: 1.1,
          }}
        >
          SwiggyOS
        </h1>

        <p style={{ color: 'var(--text-secondary)', fontSize: '15px', marginBottom: 20, lineHeight: 1.5 }}>
          Your food life, automated.
        </p>

        <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap', marginBottom: 32 }}>
          {CAPABILITIES.map(cap => (
            <span
              key={cap}
              style={{
                fontSize: '12px',
                color: 'var(--text-secondary)',
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border)',
                borderRadius: 20,
                padding: '4px 12px',
                letterSpacing: '0.01em',
              }}
            >
              {cap}
            </span>
          ))}
        </div>

        {offline ? (
          <div
            style={{
              background: 'rgba(239,68,68,0.08)',
              border: '1px solid rgba(239,68,68,0.2)',
              borderRadius: 12,
              padding: '12px 16px',
              color: '#fca5a5',
              fontSize: '13px',
              lineHeight: 1.5,
            }}
          >
            Backend offline.{' '}
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
              background: 'linear-gradient(135deg, #ff6633 0%, #e8502a 100%)',
              color: '#fff',
              border: 'none',
              borderRadius: 12,
              padding: '14px 0',
              fontSize: '15px',
              fontWeight: 600,
              cursor: 'pointer',
              fontFamily: 'inherit',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
              transition: 'opacity 0.15s, transform 0.15s',
              boxShadow: '0 4px 20px rgba(255,102,51,0.25)',
            }}
            onMouseOver={e => {
              e.currentTarget.style.opacity = '0.9'
              e.currentTarget.style.transform = 'translateY(-1px)'
            }}
            onMouseOut={e => {
              e.currentTarget.style.opacity = '1'
              e.currentTarget.style.transform = 'translateY(0)'
            }}
          >
            <Zap size={17} fill="currentColor" />
            Connect with Swiggy
          </button>
        )}

        <p style={{ color: 'var(--text-secondary)', fontSize: '12px', marginTop: 16, opacity: 0.6 }}>
          Uses Swiggy OAuth 2.1 · Your credentials are never stored.
        </p>

        {IS_DEV && !offline && (
          <button
            onClick={onDevBypass}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-secondary)',
              fontSize: '11px',
              marginTop: 14,
              cursor: 'pointer',
              fontFamily: 'inherit',
              textDecoration: 'underline',
              opacity: 0.45,
              transition: 'opacity 0.15s',
            }}
            onMouseOver={e => e.currentTarget.style.opacity = '0.8'}
            onMouseOut={e => e.currentTarget.style.opacity = '0.45'}
          >
            Dev: skip auth
          </button>
        )}
      </div>
    </div>
  )
}

export default function AppShell() {
  const [authState, setAuthState] = useState('loading')
  const [plans, setPlans] = useState([])

  const { chats, activeTab, setActiveTab, updateChat, getTabContext } = useTabChats()

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    if (params.get('auth') === 'ok') {
      window.history.replaceState({}, '', '/app')
    }

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

  if (authState === 'loading') {
    return (
      <div style={{
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--bg-primary)',
      }}>
        <div style={{
          width: 28,
          height: 28,
          borderRadius: '50%',
          border: '2px solid var(--border)',
          borderTopColor: 'var(--accent)',
          animation: 'spin 0.7s linear infinite',
        }} />
      </div>
    )
  }

  if (authState !== 'authenticated') {
    return (
      <LoginScreen
        offline={authState === 'offline'}
        onDevBypass={() => setAuthState('authenticated')}
      />
    )
  }

  return (
    <div style={{ height: '100%', display: 'flex', overflow: 'hidden' }}>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <TabBar activeTab={activeTab} onTabChange={setActiveTab} />
        <div style={{ flex: 1, overflow: 'hidden' }}>
          <Chat
            tab={activeTab}
            chatState={chats[activeTab]}
            updateChat={(updater) => updateChat(activeTab, updater)}
            getTabContext={getTabContext}
            foodMessages={chats.food.messages}
            instamartMessages={chats.instamart.messages}
            dineoutMessages={chats.dineout.messages}
          />
        </div>
      </div>
      {plans.length > 0 && (
        <PlanView
          plans={plans}
          onOrder={(plan) => {
            const chat = chats[activeTab]
            if (chat) updateChat(activeTab, prev => ({ ...prev }))
          }}
          onClose={() => setPlans([])}
        />
      )}
    </div>
  )
}
