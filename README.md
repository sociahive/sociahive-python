<p align="center">
  <a href="https://www.sociahive.com">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/sociahive/.github/main/assets/brand/logo-dark.svg">
      <img alt="SociaHive" src="https://raw.githubusercontent.com/sociahive/.github/main/assets/brand/logo-light.svg" width="220">
    </picture>
  </a>
</p>

<p align="center">Run your social media from your AI tool: schedule posts, build DM and comment automations, and read analytics.</p>
<p align="center">This is the official Python SDK for the SociaHive API.</p>

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

Official Python SDK for the [SociaHive](https://www.sociahive.com) API: schedule and publish posts, build and run DM and comment automations and read analytics from your own code.

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
    scheduled_at="2027-03-01T09:00:00Z",  # any future time
    timezone="UTC",
)
print(f"Scheduled post {post['id']}")
```

## Auth

Pass exactly one of `api_key` (long-lived) or `oauth_token` (per-user OAuth):

```python
sh = SociaHive(api_key="sk_...")
sh = SociaHive(oauth_token="mcp_at_...")
```

Generate keys at <https://www.sociahive.com/settings?tab=api-keys>.

## Context manager

The client holds an `httpx.Client` connection pool. Use `with` for tight scopes:

```python
with SociaHive(api_key="sk_...") as sh:
    account = sh.accounts.list()["data"][0]
    # flows.list needs the account's platform_user_id
    for flow in sh.flows.list(platform_user_id=account["platform_user_id"])["data"]:
        print(flow["name"], flow["status"])
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
        print(f"Rate limited, retry in {err.retry_after}s")
    else:
        print(f"HTTP {err.status}: {err}")
```

## Rate limits

Limits are per user, across all your keys: 120 reads and 30 writes a minute, 5 a minute for AI generation, and 1,000 requests a day in total. A `429` carries a `Retry-After` header (`err.retry_after`); wait that long before retrying. See [rate limits](https://docs.sociahive.com/rate-limits).

## Bulk actions on posts

`sh.posts.bulk` applies one action to up to 50 existing posts. It does not create posts; call `sh.posts.create` for each one.

```python
sh.posts.bulk("schedule", ["p1", "p2"], scheduled_for="2027-03-01T09:00:00Z")
sh.posts.bulk("update_status", ["p3"], status="draft")
sh.posts.bulk("delete", ["p4"])
```

## What's covered

| Domain | Methods |
|---|---|
| `sh.accounts` | `list` |
| `sh.posts` | `list`, `get`, `create`, `update`, `schedule`, `publish`, `cancel`, `bulk` |
| `sh.flows` | `list`, `get`, `create`, `update`, `delete`, `activate`, `deactivate`, `add_node`, `update_node`, `add_edge`, `stats`, `collected_data`, `generate` |
| `sh.analytics` | `get`, `export` |

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

- An API key only reaches what its scopes allow (for example `posts:read`, `posts:write`, `flows:write`). Revoke a key any time in **Settings > API keys**.
- Accounts connect through each platform's official login and APIs. SociaHive does not scrape and never asks for your account password (Bluesky uses an app password, Telegram a bot token).
- Platform tokens are stored encrypted on SociaHive's servers and are never returned by the API.

## Links

- [Developer quickstart](https://docs.sociahive.com/developer-quickstart) · [API reference (OpenAPI)](https://www.sociahive.com/api/v1/openapi.json)
- [Node.js SDK](https://github.com/sociahive/sociahive-node) · [Cookbook](https://github.com/sociahive/cookbook) · [MCP server and plugins](https://github.com/sociahive/sociahive-mcp)
- [Changelog](CHANGELOG.md)

## License

[MIT](LICENSE)
