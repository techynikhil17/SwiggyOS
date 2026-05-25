import { useState } from 'react'
import { ChevronRight, ChevronDown } from 'lucide-react'

const DOMAIN_MAP = {
  food: new Set([
    'get_addresses', 'search_restaurants', 'get_restaurant_menu', 'search_menu',
    'get_food_cart', 'update_food_cart', 'flush_food_cart', 'fetch_food_coupons',
    'apply_food_coupon', 'place_food_order', 'get_food_orders', 'get_food_order_details',
    'track_food_order', 'food_report_error',
  ]),
  dineout: new Set([
    'get_saved_locations', 'search_restaurants_dineout', 'get_restaurant_details',
    'get_available_slots', 'create_cart', 'book_table', 'get_booking_status', 'dineout_report_error',
  ]),
}

function getDomain(name) {
  if (name.startsWith('im_')) return 'INSTAMART'
  if (DOMAIN_MAP.dineout.has(name)) return 'DINEOUT'
  return 'FOOD'
}

const DOMAIN_COLORS = {
  FOOD:      { bg: 'rgba(255,102,51,0.08)', text: 'rgba(255,102,51,0.9)' },
  INSTAMART: { bg: 'rgba(34,197,94,0.08)',  text: 'rgba(34,197,94,0.9)' },
  DINEOUT:   { bg: 'rgba(168,85,247,0.08)', text: 'rgba(168,85,247,0.9)' },
}

function isErrorResult(result) {
  if (!result) return false
  try {
    const p = JSON.parse(result)
    return !!(p.error || p.isError)
  } catch {
    return false
  }
}

function formatJson(str) {
  try { return JSON.stringify(JSON.parse(str), null, 2) }
  catch { return str }
}

export function ToolCallCard({ name, args, result }) {
  const [expanded, setExpanded] = useState(false)

  const pending = result === null || result === undefined
  const hasError = !pending && isErrorResult(result)
  const domain = getDomain(name)
  const domainColor = DOMAIN_COLORS[domain]

  const borderColor = pending
    ? 'rgba(255,102,51,0.35)'
    : hasError
      ? 'rgba(239,68,68,0.45)'
      : 'rgba(34,197,94,0.35)'

  const statusIcon = pending ? '·' : hasError ? '✗' : '✓'
  const statusColor = pending ? 'var(--accent)' : hasError ? '#ef4444' : '#22c55e'

  const hasArgs = args && Object.keys(args).length > 0

  return (
    <div style={{
      margin: '3px 16px 3px 52px',
      borderLeft: `2px solid ${borderColor}`,
      borderRadius: '0 6px 6px 0',
      background: 'rgba(255,255,255,0.015)',
      overflow: 'hidden',
      transition: 'border-color 0.4s',
      fontSize: '12px',
    }}>
      <button
        onClick={() => setExpanded(v => !v)}
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          gap: 7,
          padding: '6px 10px',
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          fontFamily: 'inherit',
          textAlign: 'left',
        }}
      >
        {expanded
          ? <ChevronDown size={11} color="var(--text-secondary)" />
          : <ChevronRight size={11} color="var(--text-secondary)" />
        }

        {/* Domain badge */}
        <span style={{
          fontSize: '9px',
          fontWeight: 700,
          letterSpacing: '0.12em',
          color: domainColor.text,
          background: domainColor.bg,
          borderRadius: 3,
          padding: '2px 5px',
          flexShrink: 0,
        }}>
          {domain}
        </span>

        {/* Tool name */}
        <span style={{
          fontFamily: 'monospace',
          fontSize: '12px',
          color: 'var(--text-primary)',
          flex: 1,
          opacity: 0.85,
        }}>
          {name}
        </span>

        {/* Status */}
        <span style={{
          fontSize: pending ? '16px' : '11px',
          color: statusColor,
          fontWeight: 700,
          lineHeight: 1,
          animation: pending ? 'pulse-dot 1.4s ease infinite' : 'none',
          flexShrink: 0,
        }}>
          {statusIcon}
        </span>
      </button>

      {expanded && (
        <div style={{ padding: '0 10px 10px 28px', display: 'flex', flexDirection: 'column', gap: 8 }}>

          {/* Parameters */}
          <div>
            <div style={{
              fontSize: '9px',
              fontWeight: 700,
              letterSpacing: '0.12em',
              color: 'var(--text-secondary)',
              textTransform: 'uppercase',
              marginBottom: 4,
            }}>
              Parameters
            </div>
            <pre style={{
              margin: 0,
              fontFamily: 'monospace',
              fontSize: '11px',
              color: hasArgs ? 'rgba(255,255,255,0.6)' : 'var(--text-secondary)',
              background: 'var(--bg-primary)',
              borderRadius: 4,
              padding: '6px 10px',
              overflowX: 'auto',
              lineHeight: 1.5,
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-all',
            }}>
              {hasArgs ? JSON.stringify(args, null, 2) : '{ }'}
            </pre>
          </div>

          {/* Result */}
          {!pending && (
            <div>
              <div style={{
                fontSize: '9px',
                fontWeight: 700,
                letterSpacing: '0.12em',
                color: hasError ? '#ef4444' : 'var(--text-secondary)',
                textTransform: 'uppercase',
                marginBottom: 4,
              }}>
                {hasError ? 'Error' : 'Result'}
              </div>
              <pre style={{
                margin: 0,
                fontFamily: 'monospace',
                fontSize: '11px',
                color: hasError ? '#fca5a5' : 'rgba(255,255,255,0.55)',
                background: 'var(--bg-primary)',
                borderRadius: 4,
                padding: '6px 10px',
                overflowX: 'auto',
                lineHeight: 1.5,
                maxHeight: 160,
                overflowY: 'auto',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-all',
              }}>
                {formatJson(result)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
