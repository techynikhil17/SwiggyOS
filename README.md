# SwiggyOS 🍱

> **Your Personal Food & Life Operating System** — powered by Swiggy's MCP platform.

SwiggyOS is a proactive, context-aware AI agent that manages your food delivery, grocery restocking, and dining reservations as a **unified intelligent system**. Instead of waiting for you to ask, it learns your health goals, spending habits, and consumption patterns — and acts on your behalf across Swiggy Food, Instamart, and Dineout.

---

## The Problem

Every day, millions of people open Swiggy and make the same reactive decisions:

- 🤔 *"What should I eat tonight?"* — decision fatigue, every single day
- 💸 *"Wait, I spent how much on food this month?"* — no visibility until it's too late
- 🥦 *"We're out of milk again"* — grocery blind spots, constant last-minute orders
- 🍽️ *"Picking a restaurant for 6 people with different diets"* — a 30-minute group chat

SwiggyOS eliminates all of this. One agent. All three platforms. Proactive, not reactive.

---

## What It Does

### 🧠 Meal Intelligence Loop
Tracks what you've ordered via Food, what groceries you have via Instamart, and plans your week accordingly. Spots unhealthy patterns, suggests balanced alternatives, and auto-populates grocery carts for home-cooked meals.

### 💰 Budget Governor
You set a monthly food budget. SwiggyOS tracks spend across food delivery, groceries, and dining out in real time — and proactively shifts your strategy before you overspend.

> *"You're at 78% of your October budget. Want me to plan a home-cooking week? I'll restock ingredients."*

### 🛒 Proactive Restock
Learns your household's consumption rhythm from Instamart order history. Triggers reorders before you run out — no more midnight "we're out of eggs" emergencies.

### 🍽️ Social Dining Coordinator
Tell it: *"Dinner for 5 on Friday, ₹600/head, two vegetarians, somewhere in Koramangala."*

It searches Dineout, filters by availability + cuisine + budget, books the table — and can even coordinate a pre-dinner group Swiggy order if needed.

### 🥗 Health-Context Ordering
Set your macros, allergies, and dietary preferences once. Every restaurant and menu suggestion is filtered accordingly — not as a gimmick, but as a first-class constraint on every `search_menu` call.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                         │
│   Landing Page  ·  Tab UI (Food / Instamart / Dineout / All)    │
│   SSE stream consumer  ·  Inline Tool Call Cards                 │
└─────────────────────────┬───────────────────────────────────────┘
                          │  POST /chat  (SSE stream)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                               │
│                                                                  │
│   OAuth 2.1 PKCE           SwiggyOSAgent (Orchestrator)         │
│   /auth/login              tab="food"  → FoodAgent              │
│   /auth/callback           tab="instamart" → InstamartAgent     │
│   /auth/status             tab="dineout"   → DineoutAgent       │
│   /auth/logout             tab="all"   → SupervisorAgent        │
│                                    ↓                            │
│                         BaseSwiggyAgent (agentic loop)          │
│                         · Cerebras gpt-oss-120b via OpenAI SDK  │
│                         · Tool call guard (max 6 per turn)      │
│                         · Intent-gated system prompts           │
│                         · JSON sanitizer on all outputs         │
└─────────────────────────┬───────────────────────────────────────┘
                          │
              ┌───────────▼───────────┐
              │   SwiggyMCPClient     │
              │   (mcp Python SDK)    │
              │   35 tools, routing   │
              │   table per domain    │
              └──┬────────┬──────────┬┘
                 │        │          │
                 ▼        ▼          ▼
           ┌──────────┐ ┌────────┐ ┌─────────┐
           │  /food   │ │  /im   │ │/dineout │
           │ 14 tools │ │13 tools│ │ 8 tools │
           └──────────┘ └────────┘ └─────────┘
                 Swiggy MCP Servers
```

### Agent Routing

The **SupervisorAgent** (All tab) uses keyword + signal-count domain detection to route messages to the right specialist without an LLM call:

```
"Restock my groceries"  → InstamartAgent
"Find a restaurant"     → DineoutAgent  
"Order biryani"         → FoodAgent
"Book dinner and order dessert delivery" → DineoutAgent (cross-platform)
```

Each specialist agent runs an **intent-gated agentic loop** — the system prompt maps query types to exact tool sequences with hard STOP rules, preventing the model from chaining the entire ordering pipeline on a simple query.

### SSE Streaming Protocol

Every `/chat` response is a Server-Sent Events stream. The frontend renders tool calls inline as they happen:

| Event | Payload | UI |
|---|---|---|
| `text` | `{"text": "..."}` | Chat bubble |
| `tool_call` | `{"name": "...", "args": {...}}` | ToolCallCard (pending) |
| `tool_result` | `{"name": "...", "result": "..."}` | ToolCallCard (resolved) |
| `agent` | `{"agent": "dineout"}` | Agent badge |
| `done` | `{"done": true}` | Stream closed |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, Vite, Tailwind CSS v4, React Router v7, Lucide React |
| **Backend** | Python 3.11+, FastAPI, Uvicorn, SSE-Starlette |
| **AI Model** | Cerebras `gpt-oss-120b` via OpenAI-compatible SDK |
| **MCP Integration** | `mcp` Python SDK v1.12 — all 3 Swiggy MCP servers |
| **Auth** | OAuth 2.1 PKCE — Swiggy Builders Club credentials |
| **Database** | Supabase (PostgreSQL) — user profiles, budget tracking |
| **HTTP Client** | `httpx` for token exchange |

---

## MCP Tools Used

### Swiggy Food (14 tools)
`get_addresses` · `search_restaurants` · `get_restaurant_menu` · `search_menu` · `get_food_cart` · `update_food_cart` · `flush_food_cart` · `fetch_food_coupons` · `apply_food_coupon` · `place_food_order` · `get_food_orders` · `get_food_order_details` · `track_food_order` · `report_error`

### Swiggy Instamart (13 tools)
`get_addresses` · `create_address` · `delete_address` · `search_products` · `your_go_to_items` · `get_cart` · `update_cart` · `clear_cart` · `checkout` · `get_orders` · `get_order_details` · `track_order` · `report_error`

### Swiggy Dineout (8 tools)
`get_saved_locations` · `search_restaurants_dineout` · `get_restaurant_details` · `get_available_slots` · `create_cart` · `book_table` · `get_booking_status` · `report_error`

---

## Key Design Decisions

**Why proactive over reactive?**
Reactive ordering is a solved problem. Every food app does it. The agent value is in *anticipation* — acting on patterns before the user has to think about it.

**Why all 3 MCP servers together?**
Food, groceries, and dining are not separate behaviors — they're one person's food life. The intelligence comes from seeing the full picture. Ordering biryani 4 days in a row *should* trigger a grocery restock of home-cooking ingredients, not another biryani recommendation.

**Why user-controlled confirmation on orders?**
The agent suggests and prepares. The user confirms. This is a non-negotiable trust boundary — no autonomous ordering without explicit approval. Every `place_food_order` and `checkout` call requires a user confirmation step.

**Why Cerebras instead of a larger provider?**
Ultra-low latency inference (<500ms to first token) on `gpt-oss-120b` keeps the agentic loop fast. The model is capable enough for structured tool-calling without the rate-limit constraints of larger frontier models.

**Why specialist agents over one mega-agent?**
Each domain has distinct tool sets, parameter conventions, and confirmation requirements. Splitting them keeps system prompts focused, reduces hallucinated tool calls, and makes the routing logic transparent and debuggable.

---

## Running Locally

### Prerequisites

- Python 3.11+
- Node.js 18+
- A [Swiggy Builders Club](https://www.swiggy.com/builders) account with approved `client_id` and `client_secret`
- A [Cerebras](https://cloud.cerebras.ai/) API key
- A [Supabase](https://supabase.com/) project (free tier is fine)

### 1. Clone the repo

```bash
git clone https://github.com/techynikhil17/SwiggyOS.git
cd SwiggyOS
```

### 2. Backend setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn[standard] openai mcp httpx python-dotenv supabase sse-starlette pydantic
```

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp ../.env.example ../.env
```

```env
# Cerebras — https://cloud.cerebras.ai/
CEREBRAS_API_KEY=your_cerebras_api_key
CEREBRAS_MODEL=gpt-oss-120b

# Supabase — https://supabase.com/
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-or-service-role-key

# Swiggy MCP servers
SWIGGY_FOOD_MCP_URL=https://mcp.swiggy.com/food
SWIGGY_IM_MCP_URL=https://mcp.swiggy.com/im
SWIGGY_DINEOUT_MCP_URL=https://mcp.swiggy.com/dineout

# Swiggy OAuth 2.1 PKCE — Swiggy Builders Club portal
SWIGGY_CLIENT_ID=your-client-id
SWIGGY_CLIENT_SECRET=your-client-secret
SWIGGY_REDIRECT_URI=http://localhost:8000/auth/callback
SWIGGY_AUTH_URL=https://www.swiggy.com/mcp/oauth/authorize
SWIGGY_TOKEN_URL=https://www.swiggy.com/mcp/oauth/token

# App
APP_SECRET_KEY=change-me-in-production
FRONTEND_URL=http://localhost:5173

# Dev mode — set true to skip Swiggy OAuth during local development
DEV_BYPASS_AUTH=true
```

> **Note:** With `DEV_BYPASS_AUTH=true` the backend issues a placeholder token automatically, so you can test the UI and agent loop without completing the OAuth flow. All MCP tool calls will still fail until real Swiggy credentials are provided — but the agent, routing, and tool card UI are fully functional.

Start the backend:

```bash
# From the backend/ directory with venv active
uvicorn main:app --reload --port 8000
```

The API is now live at `http://localhost:8000`. Check `http://localhost:8000/health`.

### 3. Frontend setup

```bash
# From the repo root
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The landing page loads at `/` and the chat UI at `/app`.

### 4. Connecting a real Swiggy account

Once you have Builders Club credentials set in `.env`:

1. Set `DEV_BYPASS_AUTH=false`
2. Open `http://localhost:8000/auth/login?user_id=me` — this redirects to Swiggy's OAuth page
3. After approval, Swiggy redirects back to `/auth/callback`, tokens are stored server-side
4. The frontend at `/app` is now fully connected to your Swiggy account

---

## Project Structure

```
SwiggyOS/
├── frontend/
│   ├── src/
│   │   ├── LandingPage.jsx          # Marketing / entry page
│   │   ├── AppShell.jsx             # Tab layout wrapper
│   │   ├── App.jsx                  # React Router (/ → landing, /app → shell)
│   │   ├── api/chat.js              # SSE client, onToolCall / onToolResult
│   │   ├── hooks/
│   │   │   ├── useTabChats.js       # 4 independent chat states
│   │   │   └── useChat.js           # Stateless message + streaming logic
│   │   └── components/
│   │       ├── Chat.jsx             # Per-tab chat + suggestion chips
│   │       ├── ToolCallCard.jsx     # Inline developer tool panel
│   │       ├── TabBar.jsx           # Food / Instamart / Dineout / All
│   │       ├── Message.jsx          # Chat bubble renderer
│   │       └── CrossPlatformPicker.jsx  # Continue-from context card
│   └── package.json
│
├── backend/
│   ├── main.py                      # FastAPI app, /auth/* routes, /chat SSE
│   ├── agent/
│   │   ├── base_agent.py            # Agentic loop, sanitizer, tool execution
│   │   ├── orchestrator.py          # tab → agent class mapping
│   │   ├── supervisor.py            # Domain detection + routing
│   │   ├── food_agent.py            # Food specialist
│   │   ├── instamart_agent.py       # Instamart specialist
│   │   ├── dineout_agent.py         # Dineout specialist
│   │   └── tools.py                 # All 35 tool definitions (OpenAI format)
│   ├── swiggy_mcp/
│   │   └── client.py                # MCP SSE client, tool routing table
│   ├── auth/
│   │   └── token_store.py           # In-memory token store (server-side)
│   └── db/
│       └── profile.py               # Supabase user profile fetch
│
└── .env.example
```

---

## Privacy & Data Handling

- User profiles are stored in Supabase with row-level security (RLS) enabled
- No raw order data is stored — only aggregated patterns (avg weekly spend, common categories)
- All Swiggy API calls are made server-side — credentials never exposed to the client
- Access tokens are stored in-memory server-side only, never in localStorage or cookies
- Users can delete their profile and all associated data at any time

---

## Security Architecture

- **Auth**: OAuth 2.1 PKCE via Swiggy MCP — tokens stored server-side only, never logged
- **Transport**: All API calls over HTTPS/TLS
- **CORS**: Locked to `FRONTEND_URL` — no wildcard origins in production
- **Rate Limiting**: Per-user tool call guard (max 6 tool calls per agent turn)
- **Input Handling**: User input passed as plain text to the LLM — no shell execution, no eval
- **Security Contact**: itsnikhil.tech@gmail.com

---

## Roadmap

- [x] Architecture design & MCP integration plan
- [x] Core agent loop (FastAPI + Cerebras + MCP client)
- [x] 4-agent system — Food, Instamart, Dineout, Supervisor
- [x] Tab-based UI with independent chat history per domain
- [x] Real-time tool call visualization (inline ToolCallCards)
- [x] Intent-gated prompts — no pipeline over-calling
- [x] OAuth 2.1 PKCE auth flow (scaffolded, pending real credentials)
- [x] Landing page with animations
- [ ] User onboarding flow (health profile, budget, dietary preferences)
- [ ] Budget governor dashboard
- [ ] Proactive restock engine
- [ ] Meal planning feature (Food + Instamart cross-platform)
- [ ] Social dining coordinator (group Dineout + Food flow)
- [ ] Production deployment

---

## Status

> ✅ **Architecture complete and running locally. All 35 MCP tools wired. Pending real Swiggy Builders Club credentials for live data.**

---

## About the Builder

**Nikhil** — Final-year B.E. ISE student & AI Product Developer at Rooman Technologies.

Currently building production AI systems: real-time multi-persona voice agents (STT→LLM→TTS), full-featured CRM on Django + React + PostgreSQL, and now SwiggyOS.

Target: AI Engineer. Building things that actually work, not just demos.

- 🐙 GitHub: [github.com/techynikhil17](https://github.com/techynikhil17)
- 💼 LinkedIn: [linkedin.com/in/m-nikhil-126690289](https://www.linkedin.com/in/m-nikhil-126690289/)

---

*Built on Swiggy's MCP platform. This project is part of the Swiggy Builders Club program.*
