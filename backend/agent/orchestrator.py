from __future__ import annotations

import json
import os
from typing import Any

from google import genai
from google.genai import types

from agent.tools import ALL_TOOLS
from auth.token_store import TokenExpiredError
from swiggy_mcp.client import MCPServerError, SwiggyMCPClient

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Tools that place real orders — Gemini must confirm with the user first.
_CONFIRMATION_REQUIRED = {"place_food_order", "im_checkout", "book_table"}

# After a 5xx on these tools, check the corresponding "get orders" tool
# before surfacing an error, so we don't re-order something already placed.
_IDEMPOTENCY_CHECKS: dict[str, str] = {
    "place_food_order": "get_food_orders",
    "im_checkout": "im_get_orders",
}

# JSON Schema type name → google.genai Schema type string
_TYPE_MAP = {
    "string": "STRING",
    "integer": "INTEGER",
    "number": "NUMBER",
    "boolean": "BOOLEAN",
    "array": "ARRAY",
    "object": "OBJECT",
}


def _to_gemini_schema(schema: dict) -> types.Schema:
    """Recursively convert a JSON Schema dict to google.genai types.Schema."""
    kwargs: dict[str, Any] = {}
    if "type" in schema:
        kwargs["type"] = _TYPE_MAP.get(schema["type"], schema["type"].upper())
    if "description" in schema:
        kwargs["description"] = schema["description"]
    if "properties" in schema:
        kwargs["properties"] = {k: _to_gemini_schema(v) for k, v in schema["properties"].items()}
    if "required" in schema:
        kwargs["required"] = schema["required"]
    if "items" in schema:
        kwargs["items"] = _to_gemini_schema(schema["items"])
    if "enum" in schema:
        kwargs["enum"] = schema["enum"]
    return types.Schema(**kwargs)


class SwiggyOSAgent:
    """Agentic loop that talks to Gemini and dispatches Swiggy MCP tool calls.

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
        self._client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self._mcp = mcp_client
        self._user_context = user_context

        declarations = [
            types.FunctionDeclaration(
                name=t["name"],
                description=t["description"],
                parameters=_to_gemini_schema(t["input_schema"]),
            )
            for t in ALL_TOOLS
        ]

        self._config = types.GenerateContentConfig(
            system_instruction=self._system_prompt(),
            tools=[types.Tool(function_declarations=declarations)],
        )

    # ── Public interface ──────────────────────────────────────────────────

    async def run(
        self,
        user_message: str,
        conversation_history: list[dict] | None = None,
    ):
        """Async generator that streams text chunks from the agent loop.

        Streams text as Gemini produces it.  Internally handles multiple
        tool-call rounds until Gemini returns a final text-only response.

        Raises:
            TokenExpiredError: propagated immediately — caller must trigger re-auth.
        """
        contents = self._convert_history(conversation_history or [])
        contents.append(types.Content(role="user", parts=[types.Part(text=user_message)]))

        while True:
            text_buffer: list[str] = []
            function_calls: list = []
            seen_calls: set[tuple] = set()

            async for chunk in await self._client.aio.models.generate_content_stream(
                model=MODEL,
                contents=contents,
                config=self._config,
            ):
                # Yield text chunks as they arrive
                try:
                    if chunk.text:
                        yield chunk.text
                        text_buffer.append(chunk.text)
                except (ValueError, AttributeError):
                    pass

                # Collect function calls — they arrive as complete parts
                if chunk.candidates:
                    for part in chunk.candidates[0].content.parts:
                        if part.function_call and part.function_call.name:
                            key = (part.function_call.name, str(dict(part.function_call.args)))
                            if key not in seen_calls:
                                seen_calls.add(key)
                                function_calls.append(part.function_call)

            if not function_calls:
                break

            # ── Build model Content for history from streamed data ────────
            model_parts: list[types.Part] = []
            if text_buffer:
                model_parts.append(types.Part(text="".join(text_buffer)))
            for fc in function_calls:
                model_parts.append(types.Part(function_call=fc))
            contents.append(types.Content(role="model", parts=model_parts))

            # ── Execute tool calls and collect results ────────────────────
            fn_parts: list[types.Part] = []
            for fc in function_calls:
                result = await self._execute_tool(fc.name, dict(fc.args))
                fn_parts.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=fc.name,
                            response={"result": result},
                        )
                    )
                )
            contents.append(types.Content(role="user", parts=fn_parts))

    # ── Internal helpers ──────────────────────────────────────────────────

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """Call the MCP tool and return a string result for the next Gemini message.

        Confirmation-required tools are blocked here as a safety backstop.
        On MCPServerError for ordering tools, performs an idempotency check.
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

    def _convert_history(self, history: list[dict]) -> list[types.Content]:
        """Convert simple user/assistant history to google.genai Content format."""
        result: list[types.Content] = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            content = msg.get("content", "")
            if isinstance(content, str) and content:
                result.append(types.Content(role=role, parts=[types.Part(text=content)]))
            elif isinstance(content, list):
                parts = [
                    types.Part(text=p["text"])
                    for p in content
                    if isinstance(p, dict) and p.get("type") == "text" and p.get("text")
                ]
                if parts:
                    result.append(types.Content(role=role, parts=parts))
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
