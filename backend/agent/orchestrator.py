"""
Backward-compatible orchestrator wrapper.
main.py imports SwiggyOSAgent from here — this wrapper
routes to the correct specialist based on the 'tab' field.
"""
from __future__ import annotations

from agent.food_agent import FoodAgent
from agent.instamart_agent import InstamartAgent
from agent.dineout_agent import DineoutAgent
from agent.supervisor import SupervisorAgent
from swiggy_mcp.client import SwiggyMCPClient

_AGENT_MAP = {
    "food": FoodAgent,
    "instamart": InstamartAgent,
    "dineout": DineoutAgent,
    "all": SupervisorAgent,
}


class SwiggyOSAgent:
    """
    Tab-aware wrapper. Instantiates the correct specialist agent
    based on the 'tab' parameter from the /chat request.
    Default tab is 'all' (supervisor) for backward compatibility.
    """

    def __init__(
        self,
        mcp_client: SwiggyMCPClient,
        user_context: dict,
        tab: str = "all",
    ) -> None:
        agent_class = _AGENT_MAP.get(tab, SupervisorAgent)
        self._agent = agent_class(mcp_client, user_context)

    async def run(
        self,
        user_message: str,
        conversation_history=None,
        intent=None,
    ):
        async for chunk in self._agent.run(user_message, conversation_history, intent):
            yield chunk
