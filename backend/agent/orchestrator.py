from __future__ import annotations

import asyncio
import json
import os
from typing import Any

import groq as groq_lib
from groq import AsyncGroq

from agent.tools import ALL_TOOLS
from auth.token_store import TokenExpiredError
from swiggy_mcp.client import MCPServerError, SwiggyMCPClient

# Tools that place real orders — must be gated behind explicit user confirmation.
_CONFIRMATION_REQUIRED = {"place_food_order", "im_checkout", "book_table"}

# After a 5xx on these tools, check the corresponding "get orders" tool
# before surfacing an error, so we don't re-order something already placed.
_IDEMPOTENCY_CHECKS: dict[str, str] = {
    "place_food_order": "get_food_orders",
    "im_checkout": "im_get_orders",
}

# ALL_TOOLS are already JSON-schema dicts — just wrap them in Groq's function format.
_GROQ_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["input_schema"],
        },
    }
    for t in ALL_TOOLS
]

# Domain membership derived from tool name prefixes / suffixes.
def _tool_domain(name: str) -> str:
    if name.startswith("im_"):
        return "im"
    if name.endswith("_dineout") or name in {
        "get_restaurant_details", "get_available_slots",
        "get_booking_status", "get_saved_locations",
        "dineout_create_cart", "book_table", "dineout_report_error",
    }:
        return "dineout"
    return "food"

_GROQ_TOOLS_BY_DOMAIN: dict[str, list] = {"food": [], "im": [], "dineout": []}
for _t in _GROQ_TOOLS:
    _GROQ_TOOLS_BY_DOMAIN[_tool_domain(_t["function"]["name"])].append(_t)

# Keywords that signal each domain.
_DOMAIN_SIGNALS: dict[str, set[str]] = {
    "food": {
        "food", "restaurant", "order", "delivery", "menu", "eat", "eating",
        "hungry", "hunger", "pizza", "burger", "biryani", "lunch", "dinner",
        "breakfast", "meal", "dish", "cuisine", "swiggy food", "cart",
    },
    "im": {
        "grocery", "groceries", "instamart", "restock", "vegetable", "vegetables",
        "fruit", "fruits", "milk", "eggs", "bread", "household", "supplies",
        "pantry", "shopping", "shop", "buy", "stock",
    },
    "dineout": {
        "dine", "dining", "dineout", "table", "book a table", "reservation",
        "reserve", "going out", "outing", "sit-down", "visit",
    },
}


def _select_tools(messages: list[dict]) -> list[dict]:
    """Return only tools relevant to the recent conversation."""
    recent = " ".join(
        (m.get("content") or "")
        for m in messages[-6:]
        if m.get("role") in ("user", "assistant") and isinstance(m.get("content"), str)
    ).lower()

    active: list[dict] = []
    for domain, signals in _DOMAIN_SIGNALS.items():
        if any(s in recent for s in signals):
            active.extend(_GROQ_TOOLS_BY_DOMAIN[domain])

    # Fall back to all tools only when no domain signal is found.
    return active if active else _GROQ_TOOLS


class SwiggyOSAgent:
    """Agentic loop that talks to Groq and dispatches Swiggy MCP tool calls.

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
        # max_retries=0 — fail fast on rate limits instead of waiting 30-60s for backoff
        self._client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"], max_retries=0)
        self._model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self._mcp = mcp_client
        self._user_context = user_context

    # ── Public interface ──────────────────────────────────────────────────

    async def run(
        self,
        user_message: str,
        conversation_history: list[dict] | None = None,
    ):
        """Async generator that yields response text from the agent loop.

        Intermediate tool-call rounds use stream=False for simplicity.
        The final text response (no tool calls) is yielded via the generator.

        Raises:
            TokenExpiredError: propagated immediately — caller must trigger re-auth.
        """
        messages: list[dict] = [
            {"role": "system", "content": self._system_prompt()},
            *self._convert_history(conversation_history or []),
            {"role": "user", "content": user_message},
        ]

        max_iterations = 10
        for _iteration in range(max_iterations):
            try:
                tools = _select_tools(messages)
                response = await self._client.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    stream=False,
                )
            except groq_lib.RateLimitError:
                yield "I'm being rate-limited by the AI provider right now. Please wait a moment and try again."
                break
            except groq_lib.BadRequestError as exc:
                if "tool_use_failed" in str(exc):
                    # Model generated a malformed tool call (usually missing required params).
                    # Retry as plain text so it asks the user for the missing info instead.
                    try:
                        fallback = await self._client.chat.completions.create(
                            model=self._model,
                            messages=messages,
                            stream=False,
                        )
                        if fallback.choices[0].message.content:
                            yield fallback.choices[0].message.content
                    except Exception:
                        yield "I need a bit more information to help with that. Could you share your delivery address or tell me more about what you're looking for?"
                    break
                yield f"AI provider error (400). Please try again."
                break
            except groq_lib.APIStatusError as exc:
                yield f"AI provider error ({exc.status_code}). Please try again."
                break

            msg = response.choices[0].message

            if not msg.tool_calls:
                # Final response — yield content and exit loop
                if msg.content:
                    yield msg.content
                break

            # ── Append assistant turn with tool calls ─────────────────────
            messages.append({
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ],
            })

            # ── Execute each tool call and inject results ─────────────────
            for tc in msg.tool_calls:
                yield f"__TOOL__:{tc.function.name}"
                tool_args = json.loads(tc.function.arguments)
                result = await self._execute_tool(tc.function.name, tool_args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": tc.function.name,
                    "content": result,
                })
        else:
            yield "I've hit my thinking limit on this one. Please try rephrasing your request."

    # ── Internal helpers ──────────────────────────────────────────────────

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """Call the MCP tool and return a string result for the next LLM message.

        Confirmation-required tools are blocked as a safety backstop.
        On MCPServerError for ordering tools, performs an idempotency check.
        """
        if tool_name in _CONFIRMATION_REQUIRED:
            return (
                "SYSTEM: This action requires explicit user confirmation. "
                "Present the full order/booking details to the user and wait for "
                "them to say 'yes', 'confirm', or similar before proceeding."
            )

        try:
            return await asyncio.wait_for(
                self._mcp.call_tool(tool_name, tool_input),
                timeout=8.0,
            )
        except asyncio.TimeoutError:
            return json.dumps({"error": f"Tool '{tool_name}' timed out — Swiggy MCP server unreachable"})
        except TokenExpiredError:
            raise  # propagate — triggers re-auth flow in the caller
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
                pass
        return json.dumps({"error": str(exc)})

    def _convert_history(self, history: list[dict]) -> list[dict]:
        """Pass through user/assistant history — already OpenAI-compatible format."""
        result = []
        for msg in history:
            content = msg.get("content", "")
            if isinstance(content, str) and content:
                result.append({"role": msg["role"], "content": content})
            elif isinstance(content, list):
                text = " ".join(
                    p["text"] for p in content
                    if isinstance(p, dict) and p.get("type") == "text" and p.get("text")
                )
                if text:
                    result.append({"role": msg["role"], "content": text})
        return result

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
