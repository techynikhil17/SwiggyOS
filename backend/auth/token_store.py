import time


class TokenExpiredError(Exception):
    """Raised when a user's Swiggy OAuth token is absent or has expired."""


class TokenStore:
    """In-memory store for per-user OAuth access tokens.

    Tokens are held server-side only; never expose them to logs or clients.
    """

    _TOKEN_EXPIRY_BUFFER_SECS = 60  # treat token as expired 60 s before true expiry

    def __init__(self) -> None:
        # {user_id: {"access_token": str, "expires_at": float}}
        self._tokens: dict[str, dict] = {}

    def store(self, user_id: str, access_token: str, expires_in: int) -> None:
        """Persist a fresh token for *user_id*.

        Args:
            access_token: Bearer token — never log this value.
            expires_in:   Lifetime in seconds as returned by the token endpoint.
        """
        self._tokens[user_id] = {
            "access_token": access_token,
            "expires_at": time.time() + expires_in - self._TOKEN_EXPIRY_BUFFER_SECS,
        }

    def get(self, user_id: str) -> str:
        """Return a valid access token or raise TokenExpiredError."""
        entry = self._tokens.get(user_id)
        if not entry:
            raise TokenExpiredError(f"No token on file for user {user_id!r}")
        if time.time() > entry["expires_at"]:
            del self._tokens[user_id]
            raise TokenExpiredError(f"Token expired for user {user_id!r}")
        return entry["access_token"]

    def revoke(self, user_id: str) -> None:
        self._tokens.pop(user_id, None)

    def has_valid_token(self, user_id: str) -> bool:
        try:
            self.get(user_id)
            return True
        except TokenExpiredError:
            return False


# Module-level singleton shared across the FastAPI app.
token_store = TokenStore()
