## Swiggy Builders Club

When writing code against Swiggy MCP (Food, Instamart, Dineout),
consult the authoritative docs at:

- Index:     https://mcp.swiggy.com/builders/llms.txt
- Full text: https://mcp.swiggy.com/builders/llms-full.txt
- Per-page:  append `.md` to any https://mcp.swiggy.com/builders/docs/... URL

Before recommending a tool name, parameter, error code, rate limit, or
auth flow, verify against these docs. The tool catalog lives under
`/docs/reference/{food,instamart,dineout}`.

## Project: SwiggyOS
A proactive AI agent managing food delivery, groceries, and dining as one
unified system. Stack: Python + FastAPI + Anthropic SDK + Swiggy MCP.
Auth: OAuth 2.1 PKCE, Bearer token passed in headers.
MCP servers: /food, /im, /dineout