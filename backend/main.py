import hashlib
import json
import os
import secrets
import urllib.parse
from base64 import urlsafe_b64encode
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, StreamingResponse
from pydantic import BaseModel

from agent.orchestrator import SwiggyOSAgent
from auth.token_store import TokenExpiredError, token_store
from db.profile import get_user_profile
from swiggy_mcp.client import SwiggyMCPClient

load_dotenv()

app = FastAPI(title="SwiggyOS", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary in-memory PKCE state store: {state: {user_id, code_verifier}}
_pkce_state: dict[str, dict] = {}


# ─── Health ──────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok"}


# ─── Auth ────────────────────────────────────────────────────────────────────

@app.get("/auth/login")
async def auth_login(user_id: str = Query(..., description="Application user identifier")):
    """Generate a PKCE challenge and redirect the user to Swiggy's auth page."""
    code_verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = urlsafe_b64encode(digest).rstrip(b"=").decode()
    state = secrets.token_urlsafe(32)

    _pkce_state[state] = {"user_id": user_id, "code_verifier": code_verifier}

    params = urllib.parse.urlencode({
        "response_type": "code",
        "client_id": os.environ["SWIGGY_CLIENT_ID"],
        "redirect_uri": os.environ["SWIGGY_REDIRECT_URI"],
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "state": state,
    })
    return RedirectResponse(f"{os.environ['SWIGGY_AUTH_URL']}?{params}")


@app.get("/auth/callback")
async def auth_callback(code: str = Query(...), state: str = Query(...)):
    """Exchange the auth code for tokens and store them server-side."""
    entry = _pkce_state.pop(state, None)
    if entry is None:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")

    async with httpx.AsyncClient() as http:
        resp = await http.post(
            os.environ["SWIGGY_TOKEN_URL"],
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": os.environ["SWIGGY_REDIRECT_URI"],
                "client_id": os.environ["SWIGGY_CLIENT_ID"],
                "client_secret": os.environ["SWIGGY_CLIENT_SECRET"],
                "code_verifier": entry["code_verifier"],
            },
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Token exchange failed")

    payload = resp.json()
    # Never log payload["access_token"].
    token_store.store(
        user_id=entry["user_id"],
        access_token=payload["access_token"],
        expires_in=payload.get("expires_in", 3600),
    )

    frontend = os.getenv("FRONTEND_URL", "http://localhost:5173")
    return RedirectResponse(f"{frontend}?auth=ok&user_id={entry['user_id']}")


@app.get("/auth/status")
async def auth_status(user_id: str = Query(...)):
    return {"authenticated": token_store.has_valid_token(user_id)}


@app.post("/auth/logout")
async def auth_logout(user_id: str = Query(...)):
    token_store.revoke(user_id)
    return {"status": "logged_out"}


# ─── Chat ─────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    conversation_history: list[dict[str, Any]] = []
    user_id: str


def _make_mcp_client(user_id: str) -> SwiggyMCPClient:
    """Build a SwiggyMCPClient bound to the current user's token."""
    return SwiggyMCPClient(
        get_token=lambda: token_store.get(user_id),
        food_url=os.environ["SWIGGY_FOOD_MCP_URL"],
        im_url=os.environ["SWIGGY_IM_MCP_URL"],
        dineout_url=os.environ["SWIGGY_DINEOUT_MCP_URL"],
    )


@app.post("/chat")
async def chat(req: ChatRequest):
    """Stream the SwiggyOS agent response as Server-Sent Events.

    Each event is a JSON object: {"text": "<chunk>"}.
    Final event: {"done": true}.

    Returns 401 when the user's Swiggy token is absent or expired.
    """
    if not token_store.has_valid_token(req.user_id):
        # Auto-issue a dev token when Swiggy OAuth isn't wired up yet.
        # Set DEV_BYPASS_AUTH=false in production to enforce real tokens.
        dev_bypass = os.getenv("DEV_BYPASS_AUTH", "false").lower() == "true"
        if dev_bypass:
            token_store.store(user_id=req.user_id, access_token="dev-bypass-token", expires_in=86400)
        else:
            raise HTTPException(status_code=401, detail="Swiggy token expired — re-authenticate")

    user_profile = await get_user_profile(req.user_id)
    mcp_client = _make_mcp_client(req.user_id)
    agent = SwiggyOSAgent(mcp_client=mcp_client, user_context=user_profile)

    async def event_stream():
        try:
            async for chunk in agent.run(req.message, req.conversation_history):
                if chunk.startswith("__TOOL__:"):
                    yield f"data: {json.dumps({'tool': chunk[9:]})}\n\n"
                else:
                    yield f"data: {json.dumps({'text': chunk})}\n\n"
        except TokenExpiredError:
            yield f"data: {json.dumps({'error': 'auth_expired', 'detail': 'Swiggy session expired. Please re-authenticate.'})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'error': 'agent_error', 'detail': str(exc)})}\n\n"
        finally:
            yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
