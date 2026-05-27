import json
from collections.abc import Callable

from mcp import ClientSession
from mcp.client.sse import sse_client

from auth.token_store import TokenExpiredError


class MCPServerError(Exception):
    """Raised when a Swiggy MCP server returns a 5xx response."""


# Maps the Claude-facing tool name → (server_key, real_mcp_tool_name).
# server_key must match a key in SwiggyMCPClient._server_urls.
_TOOL_ROUTING: dict[str, tuple[str, str]] = {
    # ── Food ──────────────────────────────────────────────────────────────────
    "get_addresses":          ("food", "get_addresses"),
    "search_restaurants":     ("food", "search_restaurants"),
    "get_restaurant_menu":    ("food", "get_restaurant_menu"),
    "search_menu":            ("food", "search_menu"),
    "get_food_cart":          ("food", "get_food_cart"),
    "update_food_cart":       ("food", "update_food_cart"),
    "flush_food_cart":        ("food", "flush_food_cart"),
    "fetch_food_coupons":     ("food", "fetch_food_coupons"),
    "apply_food_coupon":      ("food", "apply_food_coupon"),
    "place_food_order":       ("food", "place_food_order"),
    "get_food_orders":        ("food", "get_food_orders"),
    "get_food_order_details": ("food", "get_food_order_details"),
    "track_food_order":       ("food", "track_food_order"),
    "food_report_error":      ("food", "report_error"),
    # ── Instamart ─────────────────────────────────────────────────────────────
    "im_get_addresses":       ("im", "get_addresses"),
    "im_create_address":      ("im", "create_address"),
    "im_delete_address":      ("im", "delete_address"),
    "im_search_products":     ("im", "search_products"),
    "im_your_go_to_items":    ("im", "your_go_to_items"),
    "im_get_cart":            ("im", "get_cart"),
    "im_update_cart":         ("im", "update_cart"),
    "im_clear_cart":          ("im", "clear_cart"),
    "im_checkout":            ("im", "checkout"),
    "im_get_orders":          ("im", "get_orders"),
    "im_get_order_details":   ("im", "get_order_details"),
    "im_track_order":         ("im", "track_order"),
    "im_report_error":        ("im", "report_error"),
    # ── Dineout ───────────────────────────────────────────────────────────────
    "get_saved_locations":        ("dineout", "get_saved_locations"),
    "search_restaurants_dineout": ("dineout", "search_restaurants_dineout"),
    "get_restaurant_details":     ("dineout", "get_restaurant_details"),
    "get_available_slots":        ("dineout", "get_available_slots"),
    "create_cart":                ("dineout", "create_cart"),
    "book_table":                 ("dineout", "book_table"),
    "get_booking_status":         ("dineout", "get_booking_status"),
    "dineout_report_error":       ("dineout", "report_error"),
}


class SwiggyMCPClient:
    """Thin wrapper around the MCP Python SDK for the three Swiggy servers.

    All tool calls MUST go through this class — never call MCP directly from
    the orchestrator or routes.

    Security note: the access token is fetched on every call via *get_token*
    and is never stored as an instance attribute or written to any log.
    """

    def __init__(
        self,
        get_token: Callable[[], str],
        food_url: str,
        im_url: str,
        dineout_url: str,
    ) -> None:
        self._get_token = get_token
        self._server_urls = {
            "food": food_url,
            "im": im_url,
            "dineout": dineout_url,
        }

    async def call_tool(self, claude_tool_name: str, arguments: dict) -> str:
        """Call a Swiggy MCP tool and return the result as a JSON string.

        Raises:
            TokenExpiredError: on HTTP 401 from the MCP server.
            MCPServerError:    on HTTP 5xx from the MCP server.
            ValueError:        if *claude_tool_name* is not in the routing table.
        """
        if claude_tool_name not in _TOOL_ROUTING:
            raise ValueError(f"Unknown tool: {claude_tool_name!r}")

        server_key, mcp_tool_name = _TOOL_ROUTING[claude_tool_name]
        server_url = self._server_urls[server_key]

        # Fetch token immediately before use; never cache on self.
        token = self._get_token()
        headers = {"Authorization": f"Bearer {token}"}

        try:
            async with sse_client(url=server_url, headers=headers) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(mcp_tool_name, arguments)
        except Exception as exc:
            msg = str(exc)
            if "401" in msg or "unauthorized" in msg.lower():
                raise TokenExpiredError(
                    "Swiggy access token rejected — re-auth required"
                ) from exc
            if any(code in msg for code in ("500", "502", "503", "504")):
                raise MCPServerError(
                    f"{server_key}/{mcp_tool_name} server error: {msg}"
                ) from exc
            # Catch asyncio TaskGroup / connection errors (e.g. MCP server unreachable)
            if "taskgroup" in msg.lower() or "sub-exception" in msg.lower() or "connect" in msg.lower():
                raise MCPServerError(
                    f"{server_key}/{mcp_tool_name}: Swiggy MCP server unreachable — no credentials or server down"
                ) from exc
            raise

        content_blocks = [
            (block.text if hasattr(block, "text") else str(block))
            for block in result.content
        ]
        payload = {"content": content_blocks, "isError": result.isError}
        return json.dumps(payload)
