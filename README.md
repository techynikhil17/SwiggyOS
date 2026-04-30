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

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        SwiggyOS                              │
│                   (React + FastAPI)                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
          ┌─────────────▼─────────────┐
          │      Agent Orchestrator    │
          │   (Claude Sonnet/Gemini 3 series + custom  │
          │    tool-calling loop)      │
          └──┬──────────┬─────────────┘
             │          │
    ┌────────▼───┐  ┌───▼──────────────────────────┐
    │  User      │  │     MCP Client Layer          │
    │  Profile   │  │  (mcp Python SDK)             │
    │  & Memory  │  └───┬──────────┬───────────┬───┘
    │ (Supabase) │      │          │           │
    └────────────┘      │          │           │
                        ▼          ▼           ▼
              ┌──────────────┐ ┌──────────┐ ┌─────────┐
              │ Swiggy Food  │ │Instamart │ │ Dineout │
              │ MCP Server   │ │   MCP    │ │   MCP   │
              └──────────────┘ └──────────┘ └─────────┘
```

### Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React, Tailwind CSS |
| **Backend** | Python, FastAPI |
| **AI Orchestrator** | Claude Sonnet/Gemini 3 family models |
| **MCP Integration** | `mcp` Python SDK — all 3 Swiggy MCP servers |
| **Database** | Supabase (PostgreSQL) |
| **Auth** | OAuth 2.0 via Swiggy MCP auth flow |
| **Deployment** | AWS (EC2 + RDS) |

---

## MCP Tools Used

### Swiggy Food
- `search_restaurants` — location + cuisine + dietary filters
- `search_menu` — macro/allergy-aware menu filtering
- `get_restaurant_menu` — full menu fetch for meal planning
- `update_food_cart` / `get_food_cart` — cart management
- `place_food_order` — agent-triggered ordering (with user confirmation)
- `track_food_order` — post-order status tracking

### Swiggy Instamart
- `search_products` — ingredient-level grocery search
- `update_cart` / `get_cart` — smart cart management
- `checkout` — confirmed restock execution
- `track_order` / `get_orders` — consumption pattern learning

### Swiggy Dineout
- `search_restaurants_dineout` — group-aware restaurant search
- `get_restaurant_details` — cuisine, pricing, capacity details
- `get_available_slots` — real-time availability check
- `book_table` — confirmed reservation
- `get_booking_status` — post-booking tracking

---

## Agent Flow

```
User Input: "Plan my food week, budget ₹2500, I'm trying to lose weight"
        │
        ▼
┌──────────────────┐
│  Profile Fetch   │  ← Health goals, dietary restrictions, past orders
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Budget Analysis │  ← Check current month spend across all 3 platforms
└────────┬─────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│               Meal Planning Loop                        │
│  → search_menu (calorie-filtered) for weekday dinners  │
│  → search_products for home-cook ingredients           │
│  → Reserve 1 Dineout dinner for the weekend            │
└────────┬───────────────────────────────────────────────┘
         │
         ▼
┌──────────────────┐
│  Plan Presented  │  ← Structured weekly plan, cost breakdown
│  to User         │     One-click confirm per order
└──────────────────┘
```

---

## Key Design Decisions

**Why proactive over reactive?**
Reactive ordering is a solved problem. Every food app does it. The agent value is in *anticipation* - acting on patterns before the user has to think about it.

**Why all 3 MCP servers together?**
Food, groceries, and dining are not separate behaviors - they're one person's food life. The intelligence comes from seeing the full picture. Ordering biryani 4 days in a row *should* trigger a grocery restock of home-cooking ingredients, not another biryani recommendation.

**Why user-controlled confirmation on orders?**
The agent suggests and prepares. The user confirms. This is a non-negotiable trust boundary - no autonomous ordering without explicit approval. Every `place_food_order` and `checkout` call requires a user confirmation step.

**Why Supabase for memory?**
Lightweight, fast to set up, Postgres-compatible, free tier sufficient for a pilot. User profiles, order history summaries, budget tracking, and consumption patterns all live here. The agent gets a structured context object on every session start.

---

## Privacy & Data Handling

- User profiles are stored in Supabase with row-level security (RLS) enabled
- No raw order data is stored - only aggregated patterns (e.g., avg weekly spend, common categories)
- All Swiggy API calls are made server-side - credentials never exposed to the client
- Users can delete their profile and all associated data at any time
- No data is shared with third parties or used for training

---

## Security Architecture

- **Auth**: OAuth 2.0 via Swiggy MCP auth flow; tokens stored server-side, never in localStorage
- **Transport**: All API calls over HTTPS/TLS
- **Input Sanitization**: All user inputs sanitized before being passed to the LLM or MCP tools
- **Rate Limiting**: FastAPI middleware enforces per-user rate limits to prevent abuse
- **Static IPs**: All outbound MCP calls routed through a fixed gateway IP (provided on request)
- **Security Contact**: itsnikhil.tech@gmail.com

---

## Roadmap

- [x] Architecture design & MCP integration plan
- [ ] Core agent loop (FastAPI + Claude + MCP client)
- [ ] User onboarding flow (health profile, budget, dietary preferences)
- [ ] Meal planning feature (Food + Instamart MCPs)
- [ ] Budget governor dashboard
- [ ] Social dining coordinator (Dineout MCP)
- [ ] Proactive restock engine
- [ ] React frontend with chat interface + plan view
- [ ] Production deployment on AWS

---

## Status

> 🚧 **Building in public as part of Swiggy Builders Club application.**
> Architecture finalized. Development in progress.

---

## About the Builder

**Nikhil** — Final-year B.E. ISE student & AI Product Developer at Rooman Technologies.

Currently building production AI systems: real-time multi-persona voice agents (STT→LLM→TTS), full-featured CRM on Django + React + PostgreSQL, and now SwiggyOS.

Target: AI Engineer. Building things that actually work, not just demos.

- 🐙 GitHub: github.com/techynikhil17
- 💼 LinkedIn: https://www.linkedin.com/in/m-nikhil-126690289/

---

*Built on Swiggy's MCP platform. This project is part of the Swiggy Builders Club program.*