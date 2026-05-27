# Tool definitions for the three Swiggy MCP servers.
#
# Claude-facing names for tools that would collide across servers:
#   get_addresses (food)  vs  im_get_addresses (instamart)
#   report_error (food)   →  food_report_error
#   report_error (dineout) → dineout_report_error
#   create_cart (dineout) kept as-is (no food/im collision)
#
# The SwiggyMCPClient routing table in swiggy_mcp/client.py maps every
# Claude-facing name back to the real MCP tool name on the correct server.

# ─── Food ─────────────────────────────────────────────────────────────────────

FOOD_TOOLS = [
    {
        "name": "get_addresses",
        "server": "food",
        "description": "Get user's saved delivery addresses. Always call this first before any food tool that needs addressId. Returns list of addresses sorted by last order date.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "search_restaurants",
        "server": "food",
        "description": "Search for restaurants near a saved address. Only show restaurants with availabilityStatus='OPEN'. Requires addressId from get_addresses.",
        "input_schema": {
            "type": "object",
            "properties": {
                "addressId": {"type": "string", "description": "Address ID from get_addresses"},
                "query": {"type": "string", "description": "Search query e.g. 'biryani', 'pizza', 'Chinese'"},
                "offset": {"type": "number", "description": "Pagination offset (optional)"},
            },
            "required": ["addressId", "query"],
        },
    },
    {
        "name": "get_restaurant_menu",
        "server": "food",
        "description": "Get paginated menu for a restaurant. Use search_menu for finding specific dishes with variant detail. Max 8 categories per page.",
        "input_schema": {
            "type": "object",
            "properties": {
                "addressId": {"type": "string", "description": "Address ID from get_addresses"},
                "restaurantId": {"type": "string", "description": "Restaurant ID from search_restaurants"},
                "page": {"type": "number", "description": "Page number (default 1)"},
                "pageSize": {"type": "number", "description": "Categories per page (default 5, max 8)"},
            },
            "required": ["addressId", "restaurantId"],
        },
    },
    {
        "name": "search_menu",
        "server": "food",
        "description": "Search for specific dishes across or within a restaurant. Returns items with variantsV2 OR variations (never both). Use restaurantIdOfAddedItem to scope to one restaurant.",
        "input_schema": {
            "type": "object",
            "properties": {
                "addressId": {"type": "string", "description": "Address ID from get_addresses"},
                "query": {"type": "string", "description": "Dish search query e.g. 'paneer butter masala'"},
                "restaurantIdOfAddedItem": {"type": "string", "description": "Scope search to this restaurant (optional)"},
                "vegFilter": {"type": "number", "description": "1 = veg only, 0 = mixed (optional)"},
                "offset": {"type": "number", "description": "Pagination offset (optional)"},
            },
            "required": ["addressId", "query"],
        },
    },
    {
        "name": "get_food_cart",
        "server": "food",
        "description": "Get current food cart contents, billing breakdown, and available payment methods. Call before place_food_order to show user summary.",
        "input_schema": {
            "type": "object",
            "properties": {
                "addressId": {"type": "string", "description": "Address ID from get_addresses"},
                "restaurantName": {"type": "string", "description": "Restaurant name for display (optional)"},
            },
            "required": ["addressId"],
        },
    },
    {
        "name": "update_food_cart",
        "server": "food",
        "description": "Add or update items in the food cart. Use cartItems (not items). Each item needs itemId, quantity, and either variants or variantsV2 (never both). Call get_food_cart after to display result.",
        "input_schema": {
            "type": "object",
            "properties": {
                "restaurantId": {"type": "string", "description": "Restaurant ID"},
                "cartItems": {
                    "type": "array",
                    "description": "Array of cart items. Each item: { itemId, quantity, variants OR variantsV2 (not both) }",
                    "items": {
                        "type": "object",
                        "properties": {
                            "itemId": {"type": "string"},
                            "quantity": {"type": "number"},
                            "variants": {"type": "object", "description": "Use for legacy items"},
                            "variantsV2": {"type": "object", "description": "Use for new items"},
                        },
                        "required": ["itemId", "quantity"],
                    },
                },
                "addressId": {"type": "string", "description": "Address ID from get_addresses"},
            },
            "required": ["restaurantId", "cartItems", "addressId"],
        },
    },
    {
        "name": "flush_food_cart",
        "server": "food",
        "description": "Clear the entire food cart.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "fetch_food_coupons",
        "server": "food",
        "description": "Get available coupons for the current cart. Only show COD-compatible coupons to user (v1 is COD only).",
        "input_schema": {
            "type": "object",
            "properties": {
                "restaurantId": {"type": "string", "description": "Restaurant ID"},
                "addressId": {"type": "string", "description": "Address ID from get_addresses"},
                "couponCode": {"type": "string", "description": "Check specific coupon applicability (optional)"},
            },
            "required": ["restaurantId", "addressId"],
        },
    },
    {
        "name": "apply_food_coupon",
        "server": "food",
        "description": "Apply a coupon code to the current cart.",
        "input_schema": {
            "type": "object",
            "properties": {
                "couponCode": {"type": "string", "description": "Coupon code to apply"},
                "addressId": {"type": "string", "description": "Address ID from get_addresses"},
                "cartId": {"type": "string", "description": "Cart ID (optional)"},
            },
            "required": ["couponCode", "addressId"],
        },
    },
    {
        "name": "place_food_order",
        "server": "food",
        "description": "Place the food order. NON-IDEMPOTENT — call get_food_orders before retrying on 5xx. Cart cap ₹1000. COD only in v1. REQUIRES explicit user confirmation before calling.",
        "input_schema": {
            "type": "object",
            "properties": {
                "addressId": {"type": "string", "description": "Address ID from get_addresses"},
                "paymentMethod": {"type": "string", "description": "Payment method (optional, defaults to available method)"},
            },
            "required": ["addressId"],
        },
    },
    {
        "name": "get_food_orders",
        "server": "food",
        "description": "Get active food orders. Use for idempotency check before retrying place_food_order on 5xx. Not for order history.",
        "input_schema": {
            "type": "object",
            "properties": {
                "addressId": {"type": "string", "description": "Address ID from get_addresses"},
                "orderCount": {"type": "number", "description": "Number of orders to return (default 5, max 20, optional)"},
            },
            "required": ["addressId"],
        },
    },
    {
        "name": "get_food_order_details",
        "server": "food",
        "description": "Get full details of a specific food order including items, pricing, delivery address, and status.",
        "input_schema": {
            "type": "object",
            "properties": {
                "orderId": {"type": "string", "description": "Order ID from place_food_order or get_food_orders"},
            },
            "required": ["orderId"],
        },
    },
    {
        "name": "track_food_order",
        "server": "food",
        "description": "Track active food order(s). Poll no faster than every 10 seconds. Omit orderId to get all active orders.",
        "input_schema": {
            "type": "object",
            "properties": {
                "orderId": {"type": "string", "description": "Order ID to track (optional — omit to get all active orders)"},
            },
            "required": [],
        },
    },
    {
        "name": "food_report_error",
        "server": "food",
        "description": "Report an error with a Food MCP tool call.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tool": {"type": "string", "description": "Name of the tool that failed"},
                "errorMessage": {"type": "string", "description": "Error message"},
                "domain": {"type": "string", "description": "Error domain (optional)"},
                "flowDescription": {"type": "string", "description": "Flow description (optional)"},
                "userNotes": {"type": "string", "description": "User notes (optional)"},
            },
            "required": ["tool", "errorMessage"],
        },
    },
]

# ─── Instamart ────────────────────────────────────────────────────────────────

INSTAMART_TOOLS = [
    {
        "name": "im_get_addresses",
        "server": "instamart",
        "description": "Get user's saved addresses for Instamart delivery. Only call this when the next tool explicitly requires an addressId (im_your_go_to_items, im_search_products, im_update_cart, im_checkout). Do NOT call before im_get_cart, im_clear_cart, or im_get_orders — those need no address.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "im_create_address",
        "server": "instamart",
        "description": "Create a new delivery address. Requires full address details including lat/lng.",
        "input_schema": {
            "type": "object",
            "properties": {
                "fullAddress": {"type": "string"},
                "addressLine": {"type": "string"},
                "addressLine2": {"type": "string"},
                "city": {"type": "string"},
                "postalCode": {"type": "string"},
                "latitude": {"type": "number"},
                "longitude": {"type": "number"},
                "category": {
                    "type": "string",
                    "enum": ["HOME", "WORK", "OFFICE", "FRIENDS_AND_FAMILY", "OTHER"],
                },
                "accountHolderName": {"type": "string"},
                "phone": {"type": "string"},
            },
            "required": ["fullAddress", "addressLine", "city", "postalCode", "latitude", "longitude", "category", "accountHolderName", "phone"],
        },
    },
    {
        "name": "im_delete_address",
        "server": "instamart",
        "description": "Delete a saved address. PERMANENT and IRREVERSIBLE. MUST confirm with user before calling.",
        "input_schema": {
            "type": "object",
            "properties": {
                "addressId": {"type": "string", "description": "Address ID to delete"},
            },
            "required": ["addressId"],
        },
    },
    {
        "name": "im_search_products",
        "server": "instamart",
        "description": "Search for grocery products. Returns products with variants, each variant has a spinId. Always search first, then ask user which variant before adding to cart.",
        "input_schema": {
            "type": "object",
            "properties": {
                "addressId": {"type": "string", "description": "Address ID from im_get_addresses"},
                "query": {"type": "string", "description": "Product search query e.g. 'milk', 'eggs', 'bread'"},
                "offset": {"type": "number", "description": "Pagination offset (optional)"},
            },
            "required": ["addressId", "query"],
        },
    },
    {
        "name": "im_your_go_to_items",
        "server": "instamart",
        "description": "Get user's frequently and recently ordered grocery items with variants and spinId. Use for quick reorder suggestions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "addressId": {"type": "string", "description": "Address ID from im_get_addresses"},
                "offset": {"type": "number", "description": "Pagination offset (default 0, optional)"},
            },
            "required": ["addressId"],
        },
    },
    {
        "name": "im_get_cart",
        "server": "instamart",
        "description": "Get current Instamart cart contents, bill breakdown, and available payment methods. Takes NO parameters — call directly without im_get_addresses.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "im_update_cart",
        "server": "instamart",
        "description": "Add or update items in Instamart cart. Use spinId (not productId). Replaces entire cart contents.",
        "input_schema": {
            "type": "object",
            "properties": {
                "selectedAddressId": {"type": "string", "description": "Address ID from im_get_addresses"},
                "items": {
                    "type": "array",
                    "description": "Array of items with spinId and quantity",
                    "items": {
                        "type": "object",
                        "properties": {
                            "spinId": {"type": "string", "description": "Variant spinId from im_search_products or im_your_go_to_items"},
                            "quantity": {"type": "number"},
                        },
                        "required": ["spinId", "quantity"],
                    },
                },
            },
            "required": ["selectedAddressId", "items"],
        },
    },
    {
        "name": "im_clear_cart",
        "server": "instamart",
        "description": "Clear the entire Instamart cart. Takes NO parameters — call directly without im_get_addresses. Use before switching delivery address.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "im_checkout",
        "server": "instamart",
        "description": "Place Instamart grocery order. NON-IDEMPOTENT — check im_get_orders before retrying on 5xx. Minimum ₹99, cap ₹1000. COD only in v1. REQUIRES explicit user confirmation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "addressId": {"type": "string", "description": "Address ID from im_get_addresses"},
                "paymentMethod": {"type": "string", "description": "Payment method (optional, auto-defaults)"},
            },
            "required": ["addressId"],
        },
    },
    {
        "name": "im_get_orders",
        "server": "instamart",
        "description": "Get Instamart order history (last 15 days). Takes NO required parameters — call directly without im_get_addresses. Use for idempotency check before retrying im_checkout.",
        "input_schema": {
            "type": "object",
            "properties": {
                "count": {"type": "number", "description": "Number of orders (default 10, max 20, optional)"},
                "orderType": {"type": "string", "description": "Order type (default 'DASH', optional)"},
                "activeOnly": {"type": "boolean", "description": "Return only active orders (optional)"},
            },
            "required": [],
        },
    },
    {
        "name": "im_get_order_details",
        "server": "instamart",
        "description": "Get full details of a specific Instamart order.",
        "input_schema": {
            "type": "object",
            "properties": {
                "orderId": {"type": "string", "description": "Order ID from im_checkout or im_get_orders"},
            },
            "required": ["orderId"],
        },
    },
    {
        "name": "im_track_order",
        "server": "instamart",
        "description": "Track an active Instamart order in real-time. Poll max every 10 seconds. Requires orderId AND lat/lng.",
        "input_schema": {
            "type": "object",
            "properties": {
                "orderId": {"type": "string", "description": "Order ID to track"},
                "lat": {"type": "number", "description": "User latitude"},
                "lng": {"type": "number", "description": "User longitude"},
            },
            "required": ["orderId", "lat", "lng"],
        },
    },
    {
        "name": "im_report_error",
        "server": "instamart",
        "description": "Report an error with an Instamart MCP tool call.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tool": {"type": "string"},
                "errorMessage": {"type": "string"},
                "domain": {"type": "string"},
                "flowDescription": {"type": "string"},
                "userNotes": {"type": "string"},
            },
            "required": ["tool", "errorMessage"],
        },
    },
]

# ─── Dineout ──────────────────────────────────────────────────────────────────

DINEOUT_TOOLS = [
    {
        "name": "get_saved_locations",
        "server": "dineout",
        "description": "Get user's saved locations for Dineout. Returns addressIds with lat/lng for search_restaurants_dineout. Use when user says 'near me' or 'my location'.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "search_restaurants_dineout",
        "server": "dineout",
        "description": "Search for dine-in restaurants. Use lat/lng from get_saved_locations. Returns restaurants with cuisines, ratings, cost, distance, and available offers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query e.g. 'Italian', 'rooftop', 'family restaurant'"},
                "entityType": {
                    "type": "string",
                    "enum": ["locality", "CUISINE", "RESTAURANT_CATEGORY"],
                    "description": "Entity type (optional)",
                },
                "addressId": {"type": "string", "description": "Address ID from get_saved_locations (optional)"},
                "latitude": {"type": "number", "description": "Latitude from get_saved_locations (optional)"},
                "longitude": {"type": "number", "description": "Longitude from get_saved_locations (optional)"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_restaurant_details",
        "server": "dineout",
        "description": "Get full details of a dine-in restaurant including deals, timings, and amenities.",
        "input_schema": {
            "type": "object",
            "properties": {
                "restaurantId": {"type": "string", "description": "Restaurant ID from search_restaurants_dineout"},
                "latitude": {"type": "number", "description": "User latitude"},
                "longitude": {"type": "number", "description": "User longitude"},
            },
            "required": ["restaurantId", "latitude", "longitude"],
        },
    },
    {
        "name": "get_available_slots",
        "server": "dineout",
        "description": "Get available booking slots for a restaurant. Returns slots up to 7 days out. ONLY use FREE slots (isFree=true, bookingPrice=0). Each slot has slotId, itemId, reservationTime (epoch), slotGroupName.",
        "input_schema": {
            "type": "object",
            "properties": {
                "restaurantId": {"type": "string", "description": "Restaurant ID"},
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format or epoch timestamp"},
                "latitude": {"type": "number", "description": "User latitude"},
                "longitude": {"type": "number", "description": "User longitude"},
            },
            "required": ["restaurantId", "date", "latitude", "longitude"],
        },
    },
    {
        "name": "create_cart",
        "server": "dineout",
        "description": "Create a Dineout cart for standalone cart operations. Note: book_table creates its own cart internally — only call this for standalone cart operations outside of table booking.",
        "input_schema": {
            "type": "object",
            "properties": {
                "restaurantId": {"type": "string"},
                "cartType": {"type": "string", "enum": ["DEAL_TICKET_PURCHASE", "DINEOUT"]},
                "latitude": {"type": "number"},
                "longitude": {"type": "number"},
                "slotId": {"type": "string", "description": "Required for booking carts"},
                "itemId": {"type": "string", "description": "Format: restaurantId-ticketId. Required for booking carts"},
                "reservationTime": {"type": "number", "description": "Unix epoch. Required for booking carts"},
                "guestCount": {"type": "number", "description": "1-20. Required for booking carts"},
            },
            "required": ["restaurantId", "cartType", "latitude", "longitude"],
        },
    },
    {
        "name": "book_table",
        "server": "dineout",
        "description": "Book a table at a restaurant. NON-IDEMPOTENT. FREE reservations only (isFree=true, bookingPrice=0). REQUIRES explicit user confirmation before calling.",
        "input_schema": {
            "type": "object",
            "properties": {
                "restaurantId": {"type": "string", "description": "Restaurant ID"},
                "slotId": {"type": "number", "description": "Slot ID from get_available_slots"},
                "itemId": {"type": "string", "description": "Format: restaurantId-ticketId from get_available_slots"},
                "reservationTime": {"type": "number", "description": "Unix epoch from get_available_slots"},
                "guestCount": {"type": "integer", "description": "Number of guests (1-20)"},
                "latitude": {"type": "number", "description": "User latitude"},
                "longitude": {"type": "number", "description": "User longitude"},
            },
            "required": ["restaurantId", "slotId", "itemId", "reservationTime", "guestCount", "latitude", "longitude"],
        },
    },
    {
        "name": "get_booking_status",
        "server": "dineout",
        "description": "Get status of a Dineout table booking.",
        "input_schema": {
            "type": "object",
            "properties": {
                "orderId": {"type": "string", "description": "Order ID from book_table"},
            },
            "required": ["orderId"],
        },
    },
    {
        "name": "dineout_report_error",
        "server": "dineout",
        "description": "Report an error with a Dineout MCP tool call.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tool": {"type": "string"},
                "errorMessage": {"type": "string"},
                "domain": {"type": "string"},
                "flowDescription": {"type": "string"},
                "userNotes": {"type": "string"},
            },
            "required": ["tool", "errorMessage"],
        },
    },
]

# Flat list passed to the LLM's tools parameter.
ALL_TOOLS = FOOD_TOOLS + INSTAMART_TOOLS + DINEOUT_TOOLS
