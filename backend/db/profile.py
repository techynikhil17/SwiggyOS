import os
from typing import Any

from supabase import create_client, Client

_supabase: Client | None = None


def _client() -> Client:
    global _supabase
    if _supabase is None:
        _supabase = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_KEY"],
        )
    return _supabase


async def get_user_profile(user_id: str) -> dict[str, Any]:
    """Fetch the user's profile from Supabase.

    Returns a dict with keys: name, budget, dietary, health_goals,
    allergies, default_address_id.  Missing rows return safe defaults.
    """
    result = (
        _client()
        .table("user_profiles")
        .select("*")
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
    )
    if result.data is None:
        return {
            "name": "User",
            "budget": None,
            "dietary": [],
            "health_goals": [],
            "allergies": [],
            "default_address_id": None,
        }
    return result.data


async def upsert_user_profile(user_id: str, updates: dict[str, Any]) -> None:
    _client().table("user_profiles").upsert(
        {"user_id": user_id, **updates}
    ).execute()
