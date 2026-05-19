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

For other endpoints, fall back to `httpx` directly with `X-API-Key`. Full spec:
<https://www.sociahive.com/api/v1/openapi.json>.

## License

MIT
