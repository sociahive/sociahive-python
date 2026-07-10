# sociahive

Official Python SDK for the [SociaHive](https://www.sociahive.com) API.

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
        print("Slow down — 1000 req/hr default")
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

## Autopilot

Weekly AI content generation for the scheduler — SociaHive plans, writes,
designs, and schedules a full week of on-brand posts. You review the week
(approve mode) or let it ship (autopublish mode).

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
# Enable autopilot — IRREVERSIBLE
sh.autopilot.turn_on(posts_per_week=7, review_mode="approve", confirm=True)

# Approve this week's batch and schedule it — IRREVERSIBLE go-live
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

## License

MIT
