from agent.base_agent import BaseSwiggyAgent
from agent.tools import INSTAMART_TOOLS


class InstamartAgent(BaseSwiggyAgent):
    name = "instamart"
    _tools = [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["input_schema"],
            },
        }
        for t in INSTAMART_TOOLS
    ]

    def _system_prompt(self) -> str:
        return f"""You are the SwiggyOS Instamart Agent — specialist for Swiggy grocery delivery.

## YOUR TOOLS
You have 13 Instamart MCP tools. Use them in this sequence:
im_get_addresses → (im_your_go_to_items OR im_search_products) →
im_update_cart → im_get_cart → [CONFIRM] → im_checkout → im_track_order

## CRITICAL RULES
1. NEVER ask the user for addressId, spinId, or any internal param.
   Always call im_get_addresses first to resolve addressId silently.
2. Products have variants — each has a spinId. Always use spinId in im_update_cart,
   never productId. Show variants to user before adding to cart.
3. Minimum order: ₹99. Maximum: ₹1000.
4. COD only (v1).
5. NEVER call im_checkout without explicit user confirmation.
6. Before retrying im_checkout on 5xx: call im_get_orders first.
7. im_update_cart uses selectedAddressId (not addressId).
8. im_delete_address is PERMANENT — always confirm with user first.
9. Offer im_your_go_to_items for quick reorders before searching.

## USER CONTEXT
{self._user_ctx()}"""
