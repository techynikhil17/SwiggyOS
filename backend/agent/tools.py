# Tool definitions for the three Swiggy MCP servers, in Anthropic tool-call format.
#
# Naming convention:
#   - Food tools keep their exact MCP names (most already contain "food").
#   - Instamart tools are prefixed "im_" to avoid collisions.
#   - Dineout tools keep their exact MCP names (already unique).
#   - The two ambiguous names are disambiguated:
#       get_addresses  → food_get_addresses | im_get_addresses
#       report_error   → food_report_error  | im_report_error | dineout_report_error
#
# The SwiggyMCPClient routing table in backend/mcp/client.py maps every name
# here back to the real MCP tool name on the correct server.

# ─── Food ────────────────────────────────────────────────────────────────────

food_tools: list[dict] = [
    {
        "name": "search_restaurants",
        "description": (
            "Search for food delivery restaurants by location and cuisine/dish. "
            "Use this to find restaurants before building a cart."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "addressId": {
                    "type": "string",
                    "description": "User's saved address ID for the delivery location.",
                },
                "query": {
                    "type": "string",
                    "description": "Cuisine, restaurant name, or dish name to search for.",
                },
            },
            "required": ["addressId", "query"],
        },
    },
    {
        "name": "get_restaurant_menu",
        "description": "Retrieve the full menu (with items, variants, and add-ons) for a specific restaurant.",
        "input_schema": {
            "type": "object",
            "properties": {
                "restaurantId": {
                    "type": "string",
                    "description": "Unique restaurant identifier returned by search_restaurants.",
                },
            },
            "required": ["restaurantId"],
        },
    },
    {
        "name": "search_menu",
        "description": (
            "Search for dishes within a specific restaurant's menu by keyword. "
            "Apply dietary and allergy filters here before adding to cart."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "restaurantId": {
                    "type": "string",
                    "description": "Restaurant to search within.",
                },
                "query": {
                    "type": "string",
                    "description": "Dish name or ingredient keyword.",
                },
            },
            "required": ["restaurantId", "query"],
        },
    },
    {
        "name": "get_food_cart",
        "description": "Retrieve the current food delivery cart state including items, totals, and addon options.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "food_get_addresses",
        "description": "Retrieve the user's saved food delivery addresses.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "fetch_food_coupons",
        "description": "List available discount coupons and their eligibility criteria for food delivery.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_food_orders",
        "description": "Retrieve the user's food delivery order history and any active orders.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_food_order_details",
        "description": "Retrieve full details for a specific food delivery order.",
        "input_schema": {
            "type": "object",
            "properties": {
                "orderId": {"type": "string", "description": "Order identifier."},
            },
            "required": ["orderId"],
        },
    },
    {
        "name": "track_food_order",
        "description": (
            "Track a food delivery order's live status and delivery-partner ETA. "
            "Poll at most once every 10 seconds."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "orderId": {"type": "string", "description": "Order identifier to track."},
            },
            "required": ["orderId"],
        },
    },
    {
        "name": "update_food_cart",
        "description": "Add, update, or remove items in the food delivery cart.",
        "input_schema": {
            "type": "object",
            "properties": {
                "restaurantId": {
                    "type": "string",
                    "description": "Restaurant the items belong to.",
                },
                "items": {
                    "type": "array",
                    "description": "Items to add or update.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "itemId": {"type": "string"},
                            "quantity": {"type": "integer", "minimum": 0},
                        },
                        "required": ["itemId", "quantity"],
                    },
                },
            },
            "required": ["restaurantId", "items"],
        },
    },
    {
        "name": "flush_food_cart",
        "description": "Clear the entire food delivery cart.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "apply_food_coupon",
        "description": "Apply a coupon code to the food delivery cart. Only COD-compatible coupons work in v1.",
        "input_schema": {
            "type": "object",
            "properties": {
                "couponCode": {"type": "string", "description": "Discount code to apply."},
                "addressId": {"type": "string", "description": "Delivery address ID."},
                "cartId": {
                    "type": "string",
                    "description": "Optional cart ID if multiple carts exist.",
                },
            },
            "required": ["couponCode", "addressId"],
        },
    },
    {
        "name": "place_food_order",
        "description": (
            "CONFIRMATION REQUIRED — Place the food delivery order. "
            "You MUST present the full order summary (restaurant, items, total) to the user "
            "and receive explicit confirmation before calling this tool. "
            "This call is non-idempotent: call get_food_orders before retrying on failure. "
            "Maximum cart value ₹1,000 in v1. Payment method: COD only."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "paymentMethod": {
                    "type": "string",
                    "enum": ["COD"],
                    "description": "Payment method — COD only in v1.",
                },
            },
            "required": ["paymentMethod"],
        },
    },
    {
        "name": "food_report_error",
        "description": "Generate a diagnostic error report for the Swiggy Food MCP server.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tool": {"type": "string", "description": "Tool name where the error occurred."},
                "errorMessage": {"type": "string", "description": "Error description."},
                "flowDescription": {"type": "string"},
                "toolContext": {"type": "object"},
                "userNotes": {"type": "string"},
            },
            "required": ["tool", "errorMessage"],
        },
    },
]

# ─── Instamart ────────────────────────────────────────────────────────────────

instamart_tools: list[dict] = [
    {
        "name": "im_search_products",
        "description": "Search the Instamart grocery catalog by keyword at a specific delivery address.",
        "input_schema": {
            "type": "object",
            "properties": {
                "addressId": {"type": "string", "description": "Delivery address ID."},
                "query": {"type": "string", "description": "Product name or ingredient keyword."},
            },
            "required": ["addressId", "query"],
        },
    },
    {
        "name": "im_go_to_items",
        "description": "Fetch the user's frequently and recently ordered Instamart items for quick reorder.",
        "input_schema": {
            "type": "object",
            "properties": {
                "addressId": {"type": "string", "description": "Delivery address ID."},
            },
            "required": ["addressId"],
        },
    },
    {
        "name": "im_get_cart",
        "description": "Retrieve the current Instamart grocery cart with billing breakdown.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "im_get_addresses",
        "description": "Retrieve the user's saved Instamart delivery addresses.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "im_get_orders",
        "description": "Retrieve Instamart grocery order history.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "im_get_order_details",
        "description": "Retrieve full details for a specific Instamart order.",
        "input_schema": {
            "type": "object",
            "properties": {
                "orderId": {"type": "string"},
            },
            "required": ["orderId"],
        },
    },
    {
        "name": "im_track_order",
        "description": (
            "Track an Instamart order's live status and ETA. "
            "Poll at most once every 10 seconds; typical window is 10–20 minutes post-checkout."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "orderId": {"type": "string"},
            },
            "required": ["orderId"],
        },
    },
    {
        "name": "im_update_cart",
        "description": "Add or modify products in the Instamart cart using variant-level SKU identifiers (spinId).",
        "input_schema": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "spinId": {"type": "string", "description": "Variant-level SKU ID."},
                            "quantity": {"type": "integer", "minimum": 0},
                        },
                        "required": ["spinId", "quantity"],
                    },
                },
            },
            "required": ["items"],
        },
    },
    {
        "name": "im_clear_cart",
        "description": "Flush the Instamart cart. Call this before switching delivery address to avoid serviceability errors.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "im_checkout",
        "description": (
            "CONFIRMATION REQUIRED — Place the Instamart grocery order. "
            "You MUST present the full cart summary and receive explicit user confirmation before calling this. "
            "Non-idempotent: call im_get_orders before retrying on 5xx. "
            "Minimum order ₹99. Payment method: COD only in v1."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "paymentMethod": {
                    "type": "string",
                    "enum": ["COD"],
                    "description": "Payment method — COD only in v1.",
                },
            },
            "required": ["paymentMethod"],
        },
    },
    {
        "name": "im_create_address",
        "description": "Add a new delivery address to the user's Instamart saved locations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "addressLine": {"type": "string"},
                "label": {"type": "string", "description": "e.g. Home, Office."},
                "latitude": {"type": "number"},
                "longitude": {"type": "number"},
            },
            "required": ["addressLine", "label", "latitude", "longitude"],
        },
    },
    {
        "name": "im_delete_address",
        "description": "Remove a saved address from the user's Instamart saved locations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "addressId": {"type": "string", "description": "ID of the address to delete."},
            },
            "required": ["addressId"],
        },
    },
    {
        "name": "im_report_error",
        "description": "Generate a diagnostic error report for the Swiggy Instamart MCP server.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tool": {"type": "string"},
                "errorMessage": {"type": "string"},
                "flowDescription": {"type": "string"},
                "toolContext": {"type": "object"},
                "userNotes": {"type": "string"},
            },
            "required": ["tool", "errorMessage"],
        },
    },
]

# ─── Dineout ─────────────────────────────────────────────────────────────────

dineout_tools: list[dict] = [
    {
        "name": "search_restaurants_dineout",
        "description": (
            "Search restaurants for table reservations (Dineout). "
            "Returns cuisines, ratings, cost, highlights, and free deals. "
            "Only free reservations (isFree=true) are supported in v1."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Restaurant name, cuisine, or locality.",
                },
                "entityType": {
                    "type": "string",
                    "enum": ["locality", "CUISINE", "RESTAURANT_CATEGORY"],
                    "description": "Optional filter type for the query.",
                },
                "addressId": {"type": "string", "description": "User's saved address ID."},
                "latitude": {"type": "number"},
                "longitude": {"type": "number"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_restaurant_details",
        "description": "Get ratings, deals, timings, and address for a specific Dineout restaurant.",
        "input_schema": {
            "type": "object",
            "properties": {
                "restaurantId": {"type": "string"},
                "latitude": {"type": "number", "description": "User's current latitude."},
                "longitude": {"type": "number", "description": "User's current longitude."},
            },
            "required": ["restaurantId", "latitude", "longitude"],
        },
    },
    {
        "name": "get_available_slots",
        "description": (
            "Check available table booking slots at a restaurant (up to 7 days ahead). "
            "Returns breakfast/lunch/dinner bands. Return free slots only (isFree=true)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "restaurantId": {"type": "string"},
                "date": {
                    "type": "string",
                    "description": "Date as YYYY-MM-DD or Unix epoch string.",
                },
                "latitude": {"type": "number"},
                "longitude": {"type": "number"},
            },
            "required": ["restaurantId", "date", "latitude", "longitude"],
        },
    },
    {
        "name": "get_booking_status",
        "description": "Retrieve reservation details including date, time, guests, and deal title.",
        "input_schema": {
            "type": "object",
            "properties": {
                "orderId": {"type": "string", "description": "Booking/order identifier."},
            },
            "required": ["orderId"],
        },
    },
    {
        "name": "get_saved_locations",
        "description": "Retrieve the user's saved addresses with lat/lng — useful for 'near me' Dineout queries.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "dineout_create_cart",
        "description": (
            "Create a Dineout cart for a table booking or bill payment. "
            "Note: book_table creates a cart internally — only call this separately if needed."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "restaurantId": {"type": "string"},
                "cartType": {
                    "type": "string",
                    "enum": ["DEAL_TICKET_PURCHASE", "DINEOUT"],
                },
                "latitude": {"type": "number"},
                "longitude": {"type": "number"},
            },
            "required": ["restaurantId", "cartType", "latitude", "longitude"],
        },
    },
    {
        "name": "book_table",
        "description": (
            "CONFIRMATION REQUIRED — Book a table at a Dineout restaurant. "
            "You MUST present the booking details (restaurant, date, time, guests) and receive "
            "explicit user confirmation before calling this. "
            "Non-idempotent: call get_booking_status before retrying on failure. "
            "Only free reservations are supported (bookingPrice must be 0)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "restaurantId": {"type": "string"},
                "slotId": {"type": "number", "description": "Slot ID from get_available_slots."},
                "itemId": {"type": "string", "description": "Deal/item ID for the booking."},
                "reservationTime": {"type": "number", "description": "Unix epoch of the reservation time."},
                "guestCount": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 20,
                    "description": "Number of guests.",
                },
                "latitude": {"type": "number"},
                "longitude": {"type": "number"},
            },
            "required": ["restaurantId", "slotId", "itemId", "reservationTime", "guestCount", "latitude", "longitude"],
        },
    },
    {
        "name": "dineout_report_error",
        "description": "Generate a diagnostic error report for the Swiggy Dineout MCP server.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tool": {"type": "string"},
                "domain": {"type": "string"},
                "errorMessage": {"type": "string"},
                "flowDescription": {"type": "string"},
                "toolContext": {"type": "object"},
                "userNotes": {"type": "string"},
            },
            "required": ["tool", "errorMessage"],
        },
    },
]

# Flat list passed to Claude's `tools` parameter.
ALL_TOOLS = food_tools + instamart_tools + dineout_tools
