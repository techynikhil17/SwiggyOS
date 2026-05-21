"""Smoke test for the Groq orchestrator.

Run from inside backend/ with GROQ_API_KEY set in backend/.env:

    cd backend
    python smoke_test.py

Does NOT make real Swiggy MCP calls — the MCP client is mocked.
Verifies Groq connectivity, tool schema loading, and streaming output.
"""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock

from dotenv import load_dotenv

# resolve() turns the relative __file__ into an absolute path before traversing
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from auth.token_store import token_store  # noqa: E402
from swiggy_mcp.client import SwiggyMCPClient  # noqa: E402
from agent.orchestrator import SwiggyOSAgent  # noqa: E402


async def main() -> None:
    # Plant a fake Swiggy token so token_store.get() doesn't raise
    token_store.store(user_id="test", access_token="fake-token-smoke-test", expires_in=3600)

    # Mock out the MCP client — zero real Swiggy calls
    mcp_client = AsyncMock(spec=SwiggyMCPClient)
    mcp_client.call_tool.return_value = '{"content": ["mock result"], "isError": false}'

    user_context = {
        "name": "Test User",
        "budget": 5000,
        "dietary": [],
        "health_goals": [],
        "allergies": [],
        "default_address_id": None,
    }

    agent = SwiggyOSAgent(mcp_client=mcp_client, user_context=user_context)

    print("SwiggyOS — Groq smoke test")
    print("-" * 40)
    print("User : hello, what can you do?")
    print("Agent: ", end="", flush=True)

    async for chunk in agent.run("hello, what can you do?"):
        print(chunk, end="", flush=True)

    print("\n" + "-" * 40)
    print("Groq is wired correctly.")


if __name__ == "__main__":
    asyncio.run(main())
