import { Search, ShoppingCart, MapPin, Package, UtensilsCrossed, CalendarCheck, CreditCard, Loader2 } from 'lucide-react'

const TOOL_CONFIG = {
  search_restaurants:       { label: 'Searching restaurants', Icon: Search },
  get_restaurant_menu:      { label: 'Loading menu', Icon: UtensilsCrossed },
  search_menu:              { label: 'Searching menu', Icon: Search },
  search_restaurants_dineout: { label: 'Finding restaurants', Icon: Search },
  get_restaurant_details:   { label: 'Loading restaurant', Icon: UtensilsCrossed },
  get_available_slots:      { label: 'Checking availability', Icon: CalendarCheck },
  food_get_addresses:       { label: 'Fetching addresses', Icon: MapPin },
  im_get_addresses:         { label: 'Fetching addresses', Icon: MapPin },
  get_saved_locations:      { label: 'Fetching locations', Icon: MapPin },
  im_search_products:       { label: 'Searching groceries', Icon: Search },
  im_get_cart:              { label: 'Checking your cart', Icon: ShoppingCart },
  get_food_cart:            { label: 'Checking your cart', Icon: ShoppingCart },
  im_checkout:              { label: 'Preparing checkout', Icon: CreditCard },
  place_food_order:         { label: 'Placing order', Icon: Package },
  book_table:               { label: 'Booking table', Icon: CalendarCheck },
  get_food_orders:          { label: 'Fetching orders', Icon: Package },
  im_get_orders:            { label: 'Fetching orders', Icon: Package },
  get_booking_status:       { label: 'Checking booking', Icon: CalendarCheck },
}

function getConfig(tool) {
  if (!tool) return { label: 'Thinking', Icon: Loader2 }
  return TOOL_CONFIG[tool] || { label: 'Working', Icon: Loader2 }
}

const dotStyle = (delay) => ({
  width: 4,
  height: 4,
  borderRadius: '50%',
  background: 'var(--accent)',
  display: 'inline-block',
  opacity: 0.6,
  animation: `pulse-dot 1.2s ease-in-out ${delay}s infinite`,
})

export function ToolIndicator({ tool }) {
  const { label, Icon } = getConfig(tool)

  return (
    <div style={{ padding: '4px 16px' }}>
      <div style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 8,
        padding: '7px 14px',
        background: 'rgba(255,102,51,0.07)',
        border: '1px solid rgba(255,102,51,0.15)',
        borderRadius: 20,
        color: 'var(--text-secondary)',
        fontSize: '13px',
      }}>
        <Icon size={13} style={{ color: 'var(--accent)', opacity: 0.85, flexShrink: 0 }} />
        <span className="select-none">{label}</span>
        <span style={{ display: 'flex', gap: 3, alignItems: 'center' }}>
          {[0, 0.2, 0.4].map((delay, i) => (
            <span key={i} style={dotStyle(delay)} />
          ))}
        </span>
      </div>
    </div>
  )
}
