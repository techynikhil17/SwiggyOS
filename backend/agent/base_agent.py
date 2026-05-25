from __future__ import annotations

import asyncio
import json
import os
from typing import Any, AsyncGenerator

from openai import AsyncOpenAI

from auth.token_store import TokenExpiredError
from swiggy_mcp.client import MCPServerError, SwiggyMCPClient

_CONFIRMATION_REQUIRED = {
    "place_food_order", "im_checkout", "book_table", "im_delete_address"
}
_IDEMPOTENCY_CHECKS = {
    "place_food_order": "get_food_orders",
    "im_checkout": "im_get_orders",
}


class BaseSwiggyAgent:
    """
    Shared agentic loop. Specialist agents inherit and provide:
    - self._tools: list of OpenAI-format tool dicts
    - self._system_prompt(): str
    - self.name: str (for logging)
    """
    name: str = "base"
    _tools: list = []

    def __init__(self, mcp_client: SwiggyMCPClient, user_context: dict) -> None:
        self._client = AsyncOpenAI(
            api_key=os.environ["CEREBRAS_API_KEY"],
            base_url="https://api.cerebras.ai/v1",
        )
        self._model = os.getenv("CEREBRAS_MODEL", "llama-3.1-8b")
        self._mcp = mcp_client
        self._user_context = user_context

    async def run(
        self,
        user_message: str,
        conversation_history: list | None = None,
        intent: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """
        Async generator. Yields:
        - "__TOOL__:tool_name" before each tool call
        - text chunks from the model
        """
        messages: list[dict] = [
            {"role": "system", "content": self._system_prompt() + self._communication_rules()},
            *self._convert_history(conversation_history or []),
            {"role": "user", "content": user_message},
        ]

        tool_calls_made = 0
        MAX_TOOL_CALLS = 6

        for _iteration in range(10):
            # Safety: if too many tool calls were made, force a plain-text response
            if tool_calls_made >= MAX_TOOL_CALLS:
                try:
                    final = await self._client.chat.completions.create(
                        model=self._model, messages=messages, stream=False
                    )
                    if final.choices[0].message.content:
                        yield final.choices[0].message.content
                except Exception:
                    yield "I've gathered the information. Please connect your Swiggy account to complete the request."
                break

            try:
                response = await self._client.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    tools=self._tools,
                    tool_choice="auto" if self._tools else "none",
                    stream=False,
                )
            except Exception as exc:
                err = str(exc).lower()
                if "rate" in err or "429" in err:
                    yield "I'm being rate-limited by the AI provider. Please wait a moment and try again."
                elif "400" in err:
                    try:
                        fb = await self._client.chat.completions.create(
                            model=self._model, messages=messages, stream=False
                        )
                        if fb.choices[0].message.content:
                            yield fb.choices[0].message.content
                    except Exception:
                        yield "Something went wrong. Please try again."
                else:
                    yield f"AI provider error: {exc}"
                break

            msg = response.choices[0].message
            if not msg.tool_calls:
                if msg.content:
                    yield msg.content
                break

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

            for tc in msg.tool_calls:
                tool_calls_made += 1
                tool_args = json.loads(tc.function.arguments)
                yield f"__TOOL_CALL__:{json.dumps({'name': tc.function.name, 'args': tool_args})}"
                result = await self._execute_tool(tc.function.name, tool_args)
                result_preview = result[:1000] if len(result) > 1000 else result
                yield f"__TOOL_RESULT__:{json.dumps({'name': tc.function.name, 'result': result_preview})}"
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": tc.function.name,
                    "content": result,
                })
        else:
            yield "I've hit my thinking limit on this one. Please try rephrasing."

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        if tool_name in _CONFIRMATION_REQUIRED:
            return (
                "SYSTEM: This action requires explicit user confirmation. "
                "Present the full order/booking summary to the user and wait "
                "for them to say 'yes', 'confirm', or 'go ahead'."
            )
        try:
            return await asyncio.wait_for(
                self._mcp.call_tool(tool_name, tool_input), timeout=8.0
            )
        except asyncio.TimeoutError:
            return json.dumps({"error": f"Tool '{tool_name}' timed out after 8s"})
        except TokenExpiredError:
            raise
        except MCPServerError as exc:
            return await self._handle_server_error(tool_name, exc)
        except Exception as exc:
            return json.dumps({"error": str(exc)})

    async def _handle_server_error(self, tool_name: str, exc: MCPServerError) -> str:
        check_tool = _IDEMPOTENCY_CHECKS.get(tool_name)
        if check_tool:
            try:
                result = await self._mcp.call_tool(check_tool, {})
                return json.dumps({
                    "error": str(exc),
                    "idempotency_check": json.loads(result),
                    "note": "Check whether the order was placed before retrying.",
                })
            except Exception:
                pass
        return json.dumps({"error": str(exc)})

    def _convert_history(self, history: list) -> list:
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
        raise NotImplementedError

    def _communication_rules(self) -> str:
        return """
## COMMUNICATION RULES — NEVER VIOLATE
- NEVER include raw JSON, tool names, parameter names, error codes, or any internal API detail in your response text.
- If a tool fails or returns an error, respond naturally: "I wasn't able to fetch that right now. Please make sure your Swiggy account is connected and try again."
- NEVER say things like "I called get_addresses" or "the tool failed" or show JSON objects to the user.
- NEVER expose addressId, spinId, restaurantId, slotId, or any internal identifier in your replies.
- Respond as a friendly food assistant. If something can't be completed, explain it in plain English without technical details."""

    def _user_ctx(self) -> str:
        ctx = self._user_context
        budget = f"₹{ctx['budget']}/month" if ctx.get("budget") else "not set"
        dietary = ", ".join(ctx.get("dietary") or []) or "none"
        allergies = ", ".join(ctx.get("allergies") or []) or "none"
        return (
            f"User: {ctx.get('name', 'User')} | "
            f"Budget: {budget} | "
            f"Dietary: {dietary} | "
            f"Allergies: {allergies}"
        )
