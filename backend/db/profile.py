import os
from typing import Any

from supabase import create_client, Client

_supabase: Client | None = None

_DEFAULT_PROFILE: dict[str, Any] = {
    "name": "User",
    "budget": None,
    "dietary": [],
    "health_goals": [],
    "allergies": [],
    "default_address_id": None,
}


def _is_supabase_configured() -> bool:
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    return bool(url and key and "your-project" not in url and "your-" not in key)


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

    Returns safe defaults when Supabase is not configured.
    """
    if not _is_supabase_configured():
        return _DEFAULT_PROFILE.copy()

    try:
        result = (
            _client()
            .table("user_profiles")
            .select("*")
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )
        return result.data if result.data is not None else _DEFAULT_PROFILE.copy()
    except Exception:
        return _DEFAULT_PROFILE.copy()


async def upsert_user_profile(user_id: str, updates: dict[str, Any]) -> None:
    if not _is_supabase_configured():
        return
    try:
        _client().table("user_profiles").upsert(
            {"user_id": user_id, **updates}
        ).execute()
    except Exception:
        pass
