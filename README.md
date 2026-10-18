<p align="center">
  <a href="https://www.sociahive.com">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/sociahive/.github/main/assets/brand/logo-dark.svg">
      <img alt="SociaHive" src="https://raw.githubusercontent.com/sociahive/.github/main/assets/brand/logo-light.svg" width="220">
    </picture>
  </a>
</p>

<p align="center">The official Python SDK for the SociaHive API.</p>

<p align="center">
  <a href="https://www.sociahive.com">Website</a> ·
  <a href="https://www.sociahive.com/developers">Developers</a> ·
  <a href="https://docs.sociahive.com">Docs</a> ·
  <a href="https://www.sociahive.com/connect-ai">Connect your AI</a> ·
  <a href="https://www.sociahive.com/auth/login?view=sign_up">Sign up</a>
</p>

<p align="center">
  <a href="https://pypi.org/project/sociahive/"><img alt="PyPI: sociahive" src="https://img.shields.io/pypi/v/sociahive"></a>
  <a href="https://pypi.org/project/sociahive/"><img alt="Python versions" src="https://img.shields.io/pypi/pyversions/sociahive"></a>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-blue"></a>
</p>

# sociahive

Official Python SDK for the [SociaHive](https://www.sociahive.com) API: schedule and publish posts, build and run DM and comment automations, run Autopilot and read analytics from your own code.

API access is part of the 7-day trial and every paid plan. On the free plan the API answers `403 upgrade_required`.

```bash
pip install sociahive
```

## Quickstart

```python
from sociahive import SociaHive

sh = SociaHive(api_key="sk_...")

accounts = sh.accounts.list()
print(f"Connected: {[a['platform'] for a in accounts['data']]}")

post = sh.posts.create(
    text="Hello from Python!",
    platforms=[{"platform": "instagram", "account_id": accounts["data"][0]["id"]}],
    schedule_type="scheduled",
    scheduled_at="2026-06-01T09:00:00Z",
    timezone="UTC",
)
print(f"Scheduled post {post['id']}")
```

## Auth

Pass exactly one of `api_key` (long-lived) or `oauth_token` (per-user OAuth):

```python
sh = SociaHive(api_key="sk_...")
sh = SociaHive(oauth_token="sh_at_...")
```

Generate keys at <https://www.sociahive.com/settings?tab=api-keys>.

## Context manager

The client holds an `httpx.Client` connection pool. Use `with` for tight scopes:

```python
with SociaHive(api_key="sk_...") as sh:
    for flow in sh.flows.list()["data"]:
        if flow["status"] == "draft":
            sh.flows.activate(flow["id"])
```

Outside a `with` block, call `sh.close()` when you're done.

## Error handling

```python
from sociahive import SociaHive, SociaHiveError

try:
    sh.posts.create(text="...", platforms=[...])
except SociaHiveError as err:
    if err.is_auth_error:
        print("Bad API key or insufficient scope")
    elif err.is_rate_limited:
        print("Slow down, 1000 req/hr default")
    else:
        print(f"HTTP {err.status}: {err}")
```

## What's covered

| Domain | Methods |
|---|---|
| `sh.accounts` | `list` |
| `sh.posts` | `list`, `get`, `create`, `update`, `schedule`, `publish`, `cancel`, `bulk` |
| `sh.flows` | `list`, `get`, `create`, `update`, `delete`, `activate`, `deactivate`, `add_node`, `update_node`, `add_edge`, `stats`, `collected_data`, `generate` |
| `sh.analytics` | `get`, `export` |
| `sh.autopilot` | `status`, `generate`, `adjust`, `update_brand_kit`, `approve`, `turn_on` |

## Platforms

### Publish to

<p align="center">
  <a href="https://www.sociahive.com/features/content-scheduler"><img src="https://raw.githubusercontent.com/sociahive/.github/main/assets/platforms/instagram.svg" alt="Instagram" title="Instagram" width="24"></a>&nbsp;&nbsp;
  <a href="https://www.sociahive.com/features/content-scheduler"><img src="https://raw.githubusercontent.com/sociahive/.github/main/assets/platforms/facebook.svg" alt="Facebook" title="Facebook" width="24"></a>&nbsp;&nbsp;
  <a href="https://www.sociahive.com/features/content-scheduler"><img src="https://raw.githubusercontent.com/sociahive/.github/main/assets/platforms/linkedin.svg" alt="LinkedIn" title="LinkedIn" width="24"></a>&nbsp;&nbsp;
  <a href="https://www.sociahive.com/features/content-scheduler"><img src="https://raw.githubusercontent.com/sociahive/.github/main/assets/platforms/x.svg" alt="X" title="X" width="24"></a>&nbsp;&nbsp;
  <a href="https://www.sociahive.com/features/content-scheduler"><img src="https://raw.githubusercontent.com/sociahive/.github/main/assets/platforms/threads.svg" alt="Threads" title="Threads" width="24"></a>&nbsp;&nbsp;
  <a href="https://www.sociahive.com/features/content-scheduler"><img src="https://raw.githubusercontent.com/sociahive/.github/main/assets/platforms/tiktok.svg" alt="TikTok" title="TikTok" width="24"></a>&nbsp;&nbsp;
  <a href="https://www.sociahive.com/features/content-scheduler"><img src="https://raw.githubusercontent.com/sociahive/.github/main/assets/platforms/youtube.svg" alt="YouTube" title="YouTube" width="24"></a>&nbsp;&nbsp;
  <a href="https://www.sociahive.com/features/content-scheduler"><img src="https://raw.githubusercontent.com/sociahive/.github/main/assets/platforms/bluesky.svg" alt="Bluesky" title="Bluesky" width="24"></a>&nbsp;&nbsp;
  <a href="https://www.sociahive.com/features/content-scheduler"><img src="https://raw.githubusercontent.com/sociahive/.github/main/assets/platforms/pinterest.svg" alt="Pinterest" title="Pinterest" width="24"></a>
</p>

### Automate DMs and comments on

<p align="center">
  <a href="https://www.sociahive.com/automation/instagram"><img src="https://raw.githubusercontent.com/sociahive/.github/main/assets/platforms/instagram.svg" alt="Instagram" title="Instagram" width="24"></a>&nbsp;&nbsp;
  <a href="https://www.sociahive.com/automation/facebook"><img src="https://raw.githubusercontent.com/sociahive/.github/main/assets/platforms/facebook.svg" alt="Facebook" title="Facebook" width="24"></a>&nbsp;&nbsp;
  <a href="https://www.sociahive.com/features/messenger"><img src="https://raw.githubusercontent.com/sociahive/.github/main/assets/platforms/messenger.svg" alt="Messenger" title="Messenger" width="24"></a>&nbsp;&nbsp;
  <a href="https://www.sociahive.com/automation/whatsapp"><img src="https://raw.githubusercontent.com/sociahive/.github/main/assets/platforms/whatsapp.svg" alt="WhatsApp" title="WhatsApp" width="24"></a>&nbsp;&nbsp;
  <a href="https://www.sociahive.com/automation/telegram"><img src="https://raw.githubusercontent.com/sociahive/.github/main/assets/platforms/telegram.svg" alt="Telegram" title="Telegram" width="24"></a>
</p>

## Autopilot

Weekly AI content generation for the scheduler: SociaHive plans, writes,
designs, and schedules a full week of on-brand posts. You review the week
(approve mode) or let it ship (autopublish mode). The `sh.autopilot`
methods are on `main` and not in the published 0.1.0 yet.

```python
# Where things stand (autopilot:read)
state = sh.autopilot.status()
print(state["enabled"], state["review_mode"], state["posts_per_week"])

# Ground generation in your brand (autopilot:write)
sh.autopilot.update_brand_kit(
    business_name="Acme Studio",
    what_you_do="Hand-poured candles",
    audience="home-decor lovers",
    voice_preset="warm",
    banned_words=["cheap"],
    content_pillars=["behind the scenes", "product", "education"],
)

# Kick off this week's batch, then nudge the planner
batch = sh.autopilot.generate()   # -> { week_start, batch_id, generating }
sh.autopilot.adjust("lean into the holiday theme")
```

Two calls go irreversibly live, so `confirm` is a **required keyword-only**
argument. Without `confirm=True` the API returns `400 confirmation_required`:

```python
# Enable autopilot. IRREVERSIBLE
sh.autopilot.turn_on(posts_per_week=7, review_mode="approve", confirm=True)

# Approve this week's batch and schedule it. IRREVERSIBLE go-live
sh.autopilot.approve(batch["batch_id"], confirm=True)
```

**Scopes:** `status()` needs `autopilot:read`; every write method
(`generate`, `adjust`, `update_brand_kit`, `approve`, `turn_on`) needs
`autopilot:write`.

## Development

```bash
pip install -e ".[dev]"
pytest
```

For other endpoints, fall back to `httpx` directly with `X-API-Key`. Full spec:
<https://www.sociahive.com/api/v1/openapi.json>.

## Works with your AI tool

Prefer to ask instead of writing code? The same account works from your AI tool through the [SociaHive MCP server](https://www.sociahive.com/mcp).

<p align="center">
  <a href="https://www.sociahive.com/connect-ai/chatgpt"><img src="https://raw.githubusercontent.com/sociahive/.github/main/assets/agents/chatgpt.svg" alt="ChatGPT" title="ChatGPT" width="28"></a>&nbsp;&nbsp;
  <a href="https://www.sociahive.com/connect-ai/claude"><img src="https://raw.githubusercontent.com/sociahive/.github/main/assets/agents/claude.svg" alt="Claude" title="Claude" width="28"></a>&nbsp;&nbsp;
  <a href="https://www.sociahive.com/connect-ai/claude-code"><img src="https://raw.githubusercontent.com/sociahive/.github/main/assets/agents/claude-code.svg" alt="Claude Code" title="Claude Code" width="28"></a>&nbsp;&nbsp;
  <a href="https://www.sociahive.com/connect-ai/cursor"><img src="https://raw.githubusercontent.com/sociahive/.github/main/assets/agents/cursor.svg" alt="Cursor" title="Cursor" width="28"></a>&nbsp;&nbsp;
  <a href="https://www.sociahive.com/connect-ai/codex"><img src="https://raw.githubusercontent.com/sociahive/.github/main/assets/agents/codex.svg" alt="Codex" title="Codex" width="28"></a>&nbsp;&nbsp;
  <a href="https://www.sociahive.com/connect-ai/gemini"><img src="https://raw.githubusercontent.com/sociahive/.github/main/assets/agents/gemini.svg" alt="Gemini" title="Gemini" width="28"></a>&nbsp;&nbsp;
  <a href="https://www.sociahive.com/connect-ai/grok"><img src="https://raw.githubusercontent.com/sociahive/.github/main/assets/agents/grok.svg" alt="Grok" title="Grok" width="28"></a>&nbsp;&nbsp;
  <a href="https://www.sociahive.com/mcp"><img src="https://raw.githubusercontent.com/sociahive/.github/main/assets/agents/mcp.svg" alt="MCP" title="Any MCP client" width="28"></a>
</p>

## Data and permissions

- Accounts connect through each platform's official login and APIs. SociaHive does not scrape and never asks for your account password (Bluesky uses an app password, Telegram a bot token).
- Platform tokens are stored encrypted on SociaHive's servers. They are never sent to your AI tool and never returned by the API.
- Access is limited to the scopes you grant: API key scopes (for example `posts:read`, `posts:write`, `flows:write`) or the permissions you approve at OAuth sign-in, where you can choose read-only access.
- You can revoke access at any time: revoke a key in **Settings > API keys**, or disconnect an AI tool in **Settings > Connected apps**.

## Links

- [Developer quickstart](https://docs.sociahive.com/developer-quickstart) · [API reference (OpenAPI)](https://www.sociahive.com/api/v1/openapi.json)
- [Node.js SDK](https://github.com/sociahive/sociahive-node) · [Cookbook](https://github.com/sociahive/cookbook) · [MCP server and plugins](https://github.com/sociahive/sociahive-mcp)
- [Changelog](CHANGELOG.md)

## License

[MIT](LICENSE)
