import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useInView } from './hooks/useInView'

const MARQUEE_ITEMS = [
  'FOOD DELIVERY', 'GROCERIES', 'TABLE BOOKING', 'ORDER TRACKING',
  'MEAL PLANNING', 'SMART REORDER', 'COUPON SEARCH', 'CART MANAGEMENT',
  'FOOD DELIVERY', 'GROCERIES', 'TABLE BOOKING', 'ORDER TRACKING',
  'MEAL PLANNING', 'SMART REORDER', 'COUPON SEARCH', 'CART MANAGEMENT',
]

const SYSTEM_CARDS = [
  {
    num: '01',
    label: 'FOOD',
    title: 'Food Delivery',
    lines: [
      'Search restaurants near you.',
      'Build a cart, apply coupons.',
      'Confirm once, order placed.',
    ],
    tools: ['search_restaurants', 'get_restaurant_menu', 'update_food_cart', 'place_food_order'],
  },
  {
    num: '02',
    label: 'INSTAMART',
    title: 'Grocery Runs',
    lines: [
      'Restock from your go-to list.',
      'Search products, update cart.',
      'Checkout in one message.',
    ],
    tools: ['im_your_go_to_items', 'im_search_products', 'im_update_cart', 'im_checkout'],
  },
  {
    num: '03',
    label: 'DINEOUT',
    title: 'Table Reservations',
    lines: [
      'Find restaurants with open slots.',
      'Pick a time, review details.',
      'Book the table. Done.',
    ],
    tools: ['search_restaurants_dineout', 'get_available_slots', 'book_table', 'get_booking_status'],
  },
]

const FLOW_STEPS = [
  { n: '01', title: 'You say it', body: 'Plain language. "Order biryani for two" or "restock milk and eggs." No forms, no menus.' },
  { n: '02', title: 'Agent resolves', body: 'Fetches your addresses, finds restaurants, checks availability — all without asking you for IDs.' },
  { n: '03', title: 'You confirm', body: 'Full summary: items, restaurant, price. One word to confirm. Never ordered without explicit approval.' },
  { n: '04', title: 'Tracked live', body: 'Real-time order tracking streamed back to you. No app switching.' },
]

const TECH_STACK = [
  { name: 'Groq', sub: 'LLM inference' },
  { name: 'Swiggy MCP', sub: '35 tools' },
  { name: 'FastAPI', sub: 'Backend' },
  { name: 'React', sub: 'Frontend' },
  { name: 'OAuth 2.1', sub: 'PKCE auth' },
  { name: 'Supabase', sub: 'Profiles' },
]

function RevealBlock({ children, delay = 0, className = '' }) {
  const [ref, inView] = useInView()
  return (
    <div
      ref={ref}
      className={className}
      style={{
        opacity: inView ? 1 : 0,
        transform: inView ? 'translateY(0)' : 'translateY(28px)',
        transition: `opacity 0.7s ease ${delay}ms, transform 0.7s ease ${delay}ms`,
      }}
    >
      {children}
    </div>
  )
}

export default function LandingPage() {
  const navigate = useNavigate()
  const [navScrolled, setNavScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setNavScrolled(window.scrollY > 40)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <div className="landing" style={{ minHeight: '100vh' }}>

      {/* ── NAV ── */}
      <nav style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 40px',
        height: 60,
        borderBottom: navScrolled ? '1px solid var(--border-raw)' : '1px solid transparent',
        background: navScrolled ? 'rgba(8,8,8,0.92)' : 'transparent',
        backdropFilter: navScrolled ? 'blur(12px)' : 'none',
        transition: 'all 0.3s ease',
      }}>
        <span style={{
          fontFamily: "'Space Grotesk', sans-serif",
          fontWeight: 700,
          fontSize: '17px',
          letterSpacing: '-0.03em',
          color: 'var(--ink)',
        }}>
          SWIGGY<span style={{ color: 'var(--orange)' }}>OS</span>
        </span>

        <span style={{
          fontFamily: "'Space Grotesk', sans-serif",
          fontSize: '11px',
          fontWeight: 600,
          letterSpacing: '0.1em',
          textTransform: 'uppercase',
          color: 'var(--ink-3)',
          border: '1px solid var(--border-raw)',
          borderRadius: 3,
          padding: '4px 10px',
        }}>
          Builders Club
        </span>

        <button
          className="btn-cta"
          style={{ fontSize: '11px', padding: '9px 18px' }}
          onClick={() => navigate('/app')}
        >
          Launch App →
        </button>
      </nav>

      {/* ── HERO ── */}
      <section style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden',
        padding: '100px 24px 0',
      }}>
        {/* grid overlay */}
        <div className="grid-overlay" style={{
          position: 'absolute',
          inset: 0,
          pointerEvents: 'none',
        }} />

        {/* radial glow */}
        <div style={{
          position: 'absolute',
          top: '20%',
          left: '50%',
          transform: 'translateX(-50%)',
          width: 700,
          height: 500,
          borderRadius: '50%',
          background: 'radial-gradient(ellipse at center, rgba(255,102,51,0.12) 0%, transparent 70%)',
          pointerEvents: 'none',
          filter: 'blur(40px)',
        }} />

        <div style={{ position: 'relative', zIndex: 1, maxWidth: 900 }}>
          <div className="landing-label" style={{ marginBottom: 24 }}>
            AI-POWERED FOOD AGENT
          </div>

          <h1 style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontWeight: 700,
            letterSpacing: '-0.04em',
            lineHeight: 0.95,
            fontSize: 'clamp(56px, 10vw, 120px)',
            marginBottom: 0,
          }}>
            <span className="outline-text" style={{ display: 'block' }}>YOUR FOOD LIFE,</span>
            <span style={{ display: 'block', color: 'var(--orange)' }}>AUTOMATED.</span>
          </h1>

          <p style={{
            color: 'var(--ink-2)',
            fontSize: 'clamp(15px, 2vw, 18px)',
            lineHeight: 1.6,
            maxWidth: 520,
            margin: '28px auto 40px',
          }}>
            One AI that handles food delivery, grocery runs, and table reservations
            across Swiggy's full platform — in plain language.
          </p>

          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
            <button className="btn-cta" onClick={() => navigate('/app')}>
              Launch SwiggyOS →
            </button>
            <a
              href="#how-it-works"
              className="btn-outline"
              onClick={e => {
                e.preventDefault()
                document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })
              }}
            >
              See how it works
            </a>
          </div>

          {/* Stats strip */}
          <div style={{
            display: 'flex',
            gap: 0,
            justifyContent: 'center',
            marginTop: 72,
            borderTop: '1px solid var(--border-raw)',
            borderBottom: '1px solid var(--border-raw)',
          }}>
            {[
              { val: '35', label: 'MCP Tools' },
              { val: '3', label: 'Platforms' },
              { val: '0', label: 'Forms filled' },
            ].map((s, i) => (
              <div
                key={i}
                style={{
                  flex: 1,
                  padding: '20px 0',
                  borderRight: i < 2 ? '1px solid var(--border-raw)' : 'none',
                  textAlign: 'center',
                }}
              >
                <div style={{
                  fontFamily: "'Space Grotesk', sans-serif",
                  fontWeight: 700,
                  fontSize: 'clamp(28px, 5vw, 40px)',
                  letterSpacing: '-0.04em',
                  color: 'var(--orange)',
                }}>
                  {s.val}
                </div>
                <div style={{ color: 'var(--ink-3)', fontSize: '12px', letterSpacing: '0.08em', textTransform: 'uppercase', marginTop: 4 }}>
                  {s.label}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Marquee */}
        <div style={{
          width: '100%',
          overflow: 'hidden',
          borderTop: '1px solid var(--border-raw)',
          borderBottom: '1px solid var(--border-raw)',
          background: 'rgba(255,102,51,0.03)',
          padding: '12px 0',
          marginTop: 0,
          position: 'relative',
          zIndex: 1,
        }}>
          <div className="marquee-track">
            {MARQUEE_ITEMS.map((item, i) => (
              <span
                key={i}
                style={{
                  display: 'inline-block',
                  fontFamily: "'Space Grotesk', sans-serif",
                  fontSize: '11px',
                  fontWeight: 600,
                  letterSpacing: '0.14em',
                  textTransform: 'uppercase',
                  color: i % 4 === 0 ? 'var(--orange)' : 'var(--ink-3)',
                  padding: '0 24px',
                  whiteSpace: 'nowrap',
                }}
              >
                {item}
                <span style={{ marginLeft: 24, color: 'var(--border-raw)' }}>◆</span>
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* ── THE SYSTEM ── */}
      <section id="how-it-works" style={{ padding: 'clamp(80px, 10vw, 120px) clamp(20px, 5vw, 80px)' }}>
        <RevealBlock>
          <div className="landing-label" style={{ marginBottom: 16 }}>The System</div>
          <h2 style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontWeight: 700,
            fontSize: 'clamp(36px, 5vw, 56px)',
            letterSpacing: '-0.04em',
            lineHeight: 1,
            marginBottom: 60,
            maxWidth: 600,
          }}>
            THREE DOMAINS.
            <span className="outline-text" style={{ display: 'block' }}>ONE INTERFACE.</span>
          </h2>
        </RevealBlock>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: 0,
          border: '1px solid var(--border-raw)',
        }}>
          {SYSTEM_CARDS.map((card, i) => (
            <RevealBlock key={i} delay={i * 100}>
              <div style={{
                padding: '36px 32px',
                borderRight: i < SYSTEM_CARDS.length - 1 ? '1px solid var(--border-raw)' : 'none',
                height: '100%',
                background: 'var(--surface)',
                transition: 'background 0.2s',
              }}
              onMouseOver={e => e.currentTarget.style.background = 'var(--surface-hover)'}
              onMouseOut={e => e.currentTarget.style.background = 'var(--surface)'}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 24 }}>
                  <div className="landing-label" style={{ color: 'var(--orange)' }}>{card.label}</div>
                  <div style={{
                    fontFamily: "'Space Grotesk', sans-serif",
                    fontSize: '11px',
                    fontWeight: 700,
                    color: 'var(--border-raw)',
                    letterSpacing: '0.06em',
                  }}>
                    {card.num}
                  </div>
                </div>

                <h3 style={{
                  fontFamily: "'Space Grotesk', sans-serif",
                  fontWeight: 700,
                  fontSize: '22px',
                  letterSpacing: '-0.03em',
                  marginBottom: 16,
                }}>
                  {card.title}
                </h3>

                <div style={{ marginBottom: 28 }}>
                  {card.lines.map((line, j) => (
                    <p key={j} style={{
                      color: 'var(--ink-2)',
                      fontSize: '14px',
                      lineHeight: 1.7,
                      marginBottom: 0,
                    }}>
                      {line}
                    </p>
                  ))}
                </div>

                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {card.tools.map(t => (
                    <span key={t} style={{
                      fontFamily: 'monospace',
                      fontSize: '10px',
                      color: 'var(--ink-3)',
                      background: 'rgba(255,255,255,0.04)',
                      border: '1px solid var(--border-raw)',
                      borderRadius: 3,
                      padding: '3px 8px',
                      letterSpacing: '0.02em',
                    }}>
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            </RevealBlock>
          ))}
        </div>
      </section>

      {/* ── THE FLOW ── */}
      <section style={{
        padding: 'clamp(80px, 10vw, 120px) clamp(20px, 5vw, 80px)',
        borderTop: '1px solid var(--border-raw)',
      }}>
        <RevealBlock>
          <div className="landing-label" style={{ marginBottom: 16 }}>The Flow</div>
          <h2 style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontWeight: 700,
            fontSize: 'clamp(36px, 5vw, 56px)',
            letterSpacing: '-0.04em',
            lineHeight: 1,
            marginBottom: 60,
          }}>
            HOW IT
            <span className="outline-text-orange"> WORKS.</span>
          </h2>
        </RevealBlock>

        <div style={{ maxWidth: 640, position: 'relative' }}>
          {/* connector line */}
          <div style={{
            position: 'absolute',
            left: 19,
            top: 24,
            bottom: 0,
            width: 1,
            background: 'linear-gradient(to bottom, var(--orange), transparent)',
            opacity: 0.25,
          }} />

          {FLOW_STEPS.map((step, i) => (
            <RevealBlock key={i} delay={i * 120}>
              <div style={{
                display: 'flex',
                gap: 28,
                marginBottom: i < FLOW_STEPS.length - 1 ? 48 : 0,
                position: 'relative',
              }}>
                {/* step dot */}
                <div style={{
                  width: 40,
                  height: 40,
                  borderRadius: 4,
                  border: '1px solid var(--border-raw)',
                  background: i === 0 ? 'rgba(255,102,51,0.15)' : 'var(--surface)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  fontFamily: "'Space Grotesk', sans-serif",
                  fontSize: '11px',
                  fontWeight: 700,
                  color: i === 0 ? 'var(--orange)' : 'var(--ink-3)',
                  letterSpacing: '0.04em',
                }}>
                  {step.n}
                </div>
                <div>
                  <div style={{
                    fontFamily: "'Space Grotesk', sans-serif",
                    fontWeight: 600,
                    fontSize: '17px',
                    letterSpacing: '-0.02em',
                    marginBottom: 8,
                  }}>
                    {step.title}
                  </div>
                  <p style={{
                    color: 'var(--ink-2)',
                    fontSize: '14px',
                    lineHeight: 1.7,
                    margin: 0,
                  }}>
                    {step.body}
                  </p>
                </div>
              </div>
            </RevealBlock>
          ))}
        </div>
      </section>

      {/* ── BUILT ON ── */}
      <section style={{
        padding: 'clamp(80px, 10vw, 120px) clamp(20px, 5vw, 80px)',
        borderTop: '1px solid var(--border-raw)',
      }}>
        <RevealBlock>
          <div className="landing-label" style={{ marginBottom: 40 }}>Built on</div>
        </RevealBlock>

        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: 0,
          border: '1px solid var(--border-raw)',
        }}>
          {TECH_STACK.map((tech, i) => (
            <RevealBlock key={i} delay={i * 60}>
              <div style={{
                padding: '28px 36px',
                borderRight: '1px solid var(--border-raw)',
                borderBottom: '1px solid var(--border-raw)',
                minWidth: 160,
                background: 'var(--surface)',
                transition: 'background 0.2s',
              }}
              onMouseOver={e => e.currentTarget.style.background = 'var(--surface-hover)'}
              onMouseOut={e => e.currentTarget.style.background = 'var(--surface)'}
              >
                <div style={{
                  fontFamily: "'Space Grotesk', sans-serif",
                  fontWeight: 700,
                  fontSize: '18px',
                  letterSpacing: '-0.03em',
                  marginBottom: 4,
                }}>
                  {tech.name}
                </div>
                <div style={{
                  fontSize: '12px',
                  color: 'var(--ink-3)',
                  letterSpacing: '0.05em',
                  textTransform: 'uppercase',
                }}>
                  {tech.sub}
                </div>
              </div>
            </RevealBlock>
          ))}
        </div>
      </section>

      {/* ── CTA ── */}
      <section style={{
        padding: 'clamp(100px, 12vw, 160px) clamp(20px, 5vw, 80px)',
        borderTop: '1px solid var(--border-raw)',
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* glow */}
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: 600,
          height: 400,
          background: 'radial-gradient(ellipse at center, rgba(255,102,51,0.1) 0%, transparent 70%)',
          pointerEvents: 'none',
          filter: 'blur(60px)',
        }} />

        <div style={{ position: 'relative', zIndex: 1 }}>
          <RevealBlock>
            <div className="landing-label" style={{ marginBottom: 24 }}>Ready?</div>
            <h2 style={{
              fontFamily: "'Space Grotesk', sans-serif",
              fontWeight: 700,
              fontSize: 'clamp(48px, 8vw, 88px)',
              letterSpacing: '-0.04em',
              lineHeight: 0.95,
              marginBottom: 40,
            }}>
              <span className="outline-text" style={{ display: 'block' }}>YOUR FOOD LIFE?</span>
              <span style={{ display: 'block', color: 'var(--orange)' }}>AUTOMATED.</span>
            </h2>

            <button
              className="btn-cta"
              style={{ fontSize: '14px', padding: '16px 36px' }}
              onClick={() => navigate('/app')}
            >
              LAUNCH SWIGGYOS →
            </button>
          </RevealBlock>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer style={{
        borderTop: '1px solid var(--border-raw)',
        padding: '32px clamp(20px, 5vw, 80px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 16,
      }}>
        <span style={{
          fontFamily: "'Space Grotesk', sans-serif",
          fontWeight: 700,
          fontSize: '15px',
          letterSpacing: '-0.03em',
        }}>
          SWIGGY<span style={{ color: 'var(--orange)' }}>OS</span>
        </span>
        <span style={{ color: 'var(--ink-3)', fontSize: '12px', letterSpacing: '0.04em' }}>
          Built for Swiggy Builders Club · learn@rooman.com
        </span>
      </footer>

    </div>
  )
}
