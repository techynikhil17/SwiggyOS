from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from typing import Any

import anthropic

from backend.agent.tools import ALL_TOOLS
from backend.auth.token_store import TokenExpiredError
from backend.mcp.client import MCPServerError, SwiggyMCPClient

MODEL = "claude-sonnet-4-6"

# Tools that place real orders — Claude must confirm with the user first.
_CONFIRMATION_REQUIRED = {"place_food_order", "im_checkout", "book_table"}

# After a 5xx on these tools, check the corresponding "get orders" tool
# before surfacing an error, so we don't re-order something already placed.
_IDEMPOTENCY_CHECKS: dict[str, str] = {
    "place_food_order": "get_food_orders",
    "im_checkout": "im_get_orders",
}


class SwiggyOSAgent:
    """Agentic loop that talks to Claude and dispatches Swiggy MCP tool calls.

    Usage::

        agent = SwiggyOSAgent(mcp_client=client, user_context=profile)
        async for chunk in agent.run("What's nearby for dinner?", history):
            print(chunk, end="", flush=True)
    """

    def __init__(
        self,
        mcp_client: SwiggyMCPClient,
        user_context: dict[str, Any],
    ) -> None:
        self._claude = anthropic.AsyncAnthropic()
        self._mcp = mcp_client
        self._user_context = user_context

    # ── Public interface ──────────────────────────────────────────────────

    async def run(
        self,
        user_message: str,
        conversation_history: list[dict] | None = None,
    ) -> AsyncGenerator[str, None]:
        """Async generator that streams text chunks from the agent loop.

        Yields text as Claude produces it.  Internally handles multiple
        tool-call rounds until Claude returns stop_reason == 'end_turn'.

        Raises:
            TokenExpiredError: propagated immediately — caller must trigger re-auth.
        """
        messages: list[dict] = list(conversation_history or [])
        messages.append({"role": "user", "content": user_message})

        while True:
            text_yielded_this_round = False

            async with self._claude.messages.stream(
                model=MODEL,
                max_tokens=4096,
                system=self._system_prompt(),
                tools=ALL_TOOLS,
                messages=messages,
            ) as stream:
                async for chunk in stream.text_stream:
                    yield chunk
                    text_yielded_this_round = True

                response = await stream.get_final_message()

            if response.stop_reason != "tool_use":
                break

            # ── Process tool calls ────────────────────────────────────────
            messages.append({"role": "assistant", "content": response.content})

            tool_results: list[dict] = []
            for block in response.content:
                if block.type != "tool_use":
                    continue

                result_content = await self._execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result_content,
                })

            messages.append({"role": "user", "content": tool_results})

    # ── Internal helpers ──────────────────────────────────────────────────

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """Call the MCP tool and return a string result for the next Claude message.

        Confirmation-required tools are blocked here as a safety backstop —
        the system prompt should have already prompted Claude to ask the user
        before reaching this point.

        On MCPServerError for ordering tools, we perform an idempotency check
        (get_food_orders / im_get_orders) before returning the error context,
        so Claude can inform the user whether the order actually went through.
        """
        if tool_name in _CONFIRMATION_REQUIRED:
            return (
                "SYSTEM: This action requires explicit user confirmation. "
                "Present the full order/booking details to the user and wait for "
                "them to say 'yes', 'confirm', or similar before proceeding."
            )

        try:
            return await self._mcp.call_tool(tool_name, tool_input)
        except TokenExpiredError:
            raise  # propagate to caller — triggers re-auth flow
        except MCPServerError as exc:
            return await self._handle_server_error(tool_name, exc)
        except Exception as exc:
            return json.dumps({"error": str(exc)})

    async def _handle_server_error(self, tool_name: str, exc: MCPServerError) -> str:
        """On 5xx for ordering tools, check whether the order exists before failing."""
        check_tool = _IDEMPOTENCY_CHECKS.get(tool_name)
        if check_tool:
            try:
                orders_result = await self._mcp.call_tool(check_tool, {})
                return json.dumps({
                    "error": str(exc),
                    "idempotency_check": json.loads(orders_result),
                    "note": (
                        "Server error occurred. Current order list is attached. "
                        "Check whether the order was placed before retrying."
                    ),
                })
            except Exception:
                pass  # idempotency check itself failed — return original error
        return json.dumps({"error": str(exc)})

    def _system_prompt(self) -> str:
        ctx = self._user_context
        budget = f"₹{ctx['budget']}/month" if ctx.get("budget") else "not set"
        dietary = ", ".join(ctx.get("dietary") or []) or "none"
        health_goals = ", ".join(ctx.get("health_goals") or []) or "none"
        allergies = ", ".join(ctx.get("allergies") or []) or "none"

        return f"""You are SwiggyOS, a proactive AI food and life management assistant \
with access to Swiggy Food (delivery), Instamart (groceries), and Dineout (table bookings).

## User profile
- Name: {ctx.get("name", "User")}
- Monthly food budget: {budget}
- Dietary preferences: {dietary}
- Health goals: {health_goals}
- Allergies: {allergies}
- Default address ID: {ctx.get("default_address_id") or "ask the user"}

## Critical rules
1. **No autonomous ordering.** Before calling `place_food_order`, `im_checkout`, or \
`book_table`, you MUST:
   - Show the full order/booking summary (items, restaurant, total cost, date/time for \
bookings) in your text response.
   - Explicitly ask the user to confirm (e.g., "Shall I place this order?").
   - Wait for a clear "yes", "confirm", "go ahead", or equivalent in the NEXT user message.
   Never call these tools in the same turn you present the summary.

2. **Apply user context to every recommendation.** Filter menus, restaurants, and grocery \
items by dietary preferences, allergies, and health goals on every call.

3. **Budget awareness.** If spending is tracking toward the monthly budget limit, proactively \
mention it and suggest home-cooking alternatives.

4. **Dineout — free reservations only.** Only suggest bookings where isFree=true and \
bookingPrice=0. Paid deals are not supported.

5. **Do not share tokens or internal errors** verbatim with the user. Summarise errors \
in plain language.

Today's context: you can call Swiggy Food, Instamart, and Dineout tools as needed to \
answer the user's request. Always start with read tools (search, get) before write tools \
(update cart, checkout, place order)."""
