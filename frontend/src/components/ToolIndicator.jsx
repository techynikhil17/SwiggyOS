const TOOL_LABELS = {
  search_restaurants: 'Searching restaurants',
  get_restaurant_menu: 'Loading menu',
  get_addresses: 'Fetching your addresses',
  food_get_addresses: 'Fetching your addresses',
  im_get_addresses: 'Fetching your addresses',
  search_products: 'Searching groceries',
  get_cart: 'Checking your cart',
  im_checkout: 'Preparing checkout',
  place_food_order: 'Placing order',
  book_table: 'Booking table',
  search_restaurants_dineout: 'Finding restaurants',
  get_food_orders: 'Fetching your orders',
  im_get_orders: 'Fetching your orders',
}

function getLabel(tool) {
  if (!tool) return 'Thinking'
  return TOOL_LABELS[tool] || 'Thinking'
}

export function ToolIndicator({ tool }) {
  return (
    <div className="flex items-center gap-2 px-4 py-2">
      <span
        style={{ color: 'var(--text-secondary)', fontSize: '13px' }}
        className="select-none"
      >
        {getLabel(tool)}
      </span>
      <span className="flex gap-[3px] items-center">
        {[0, 1, 2].map(i => (
          <span
            key={i}
            style={{
              width: 4,
              height: 4,
              borderRadius: '50%',
              background: 'var(--text-secondary)',
              display: 'inline-block',
              animation: `pulse-dot 1.2s ease-in-out ${i * 0.2}s infinite`,
            }}
          />
        ))}
      </span>
      <style>{`
        @keyframes pulse-dot {
          0%, 80%, 100% { opacity: 0.2; transform: scale(0.8); }
          40% { opacity: 1; transform: scale(1); }
        }
      `}</style>
    </div>
  )
}
