from __future__ import annotations

from typing import AsyncGenerator

from agent.food_agent import FoodAgent
from agent.instamart_agent import InstamartAgent
from agent.dineout_agent import DineoutAgent
from swiggy_mcp.client import SwiggyMCPClient

_DOMAIN_SIGNALS = {
    "food": {
        # Specific food-delivery terms only — avoid generic words like "order"
        "food", "restaurant", "food delivery", "food order", "delivery food",
        "menu", "eat out", "eating", "hungry", "pizza", "burger", "biryani",
        "sushi", "pasta", "noodles", "lunch", "dinner", "breakfast",
        "meal", "dish", "cuisine", "food cart", "takeaway", "take away",
    },
    "instamart": {
        "grocery", "groceries", "instamart", "restock", "restocking",
        "vegetable", "vegetables", "fruit", "fruits", "milk", "eggs",
        "bread", "household", "supplies", "pantry", "shopping list",
        "stock up", "supermarket", "go-to items", "usual groceries",
        "usual order", "weekly groceries", "daily essentials",
    },
    "dineout": {
        "dine", "dining", "dineout", "table", "book a table", "reservation",
        "reserve", "going out", "sit-down", "visit", "restaurant tonight",
        "restaurant this", "book",
    },
}


def _count_signals(text: str, domain: str) -> int:
    lower = text.lower()
    return sum(1 for s in _DOMAIN_SIGNALS[domain] if s in lower)


def _detect_domains(text: str) -> list[str]:
    lower = text.lower()
    return [d for d, signals in _DOMAIN_SIGNALS.items() if any(s in lower for s in signals)]


class SupervisorAgent:
    """
    Routes user messages to the correct specialist agent.
    Used by the 'all' tab — handles cross-platform flows.
    For single-domain tabs, use the specialist directly.
    """

    def __init__(self, mcp_client: SwiggyMCPClient, user_context: dict) -> None:
        self._mcp = mcp_client
        self._ctx = user_context
        self._agents = {
            "food": FoodAgent(mcp_client, user_context),
            "instamart": InstamartAgent(mcp_client, user_context),
            "dineout": DineoutAgent(mcp_client, user_context),
        }

    async def run(
        self,
        user_message: str,
        conversation_history: list | None = None,
        intent: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """
        Detects domain from user message and routes to the correct specialist.
        For dineout+food cross-platform requests, runs dineout first.
        """
        # Explicit intent override
        if intent and intent in self._agents:
            async for chunk in self._agents[intent].run(
                user_message, conversation_history, intent
            ):
                yield chunk
            return

        domains = _detect_domains(user_message)

        if len(domains) == 0:
            # No domain detected — default to food (most common query type)
            async for chunk in self._agents["food"].run(
                user_message, conversation_history
            ):
                yield chunk
            return

        if len(domains) == 1:
            async for chunk in self._agents[domains[0]].run(
                user_message, conversation_history
            ):
                yield chunk
            return

        # Multiple domains detected — use signal count to pick the dominant one
        # Exception: dineout + food cross-platform → run dineout (booking) first
        if "dineout" in domains and "food" in domains and "instamart" not in domains:
            yield "__AGENT__:dineout"
            async for chunk in self._agents["dineout"].run(
                user_message, conversation_history
            ):
                yield chunk
            return

        # For all other multi-domain matches, route to the domain with most signals
        dominant = max(domains, key=lambda d: _count_signals(user_message, d))
        async for chunk in self._agents[dominant].run(
            user_message, conversation_history
        ):
            yield chunk
