# Changelog

All notable changes to the `sociahive` Python package are listed here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-10-20

### Added

- New resources: `media` (media library, uploads, AI images), `signatures`, `posting_slots` (with `find_slot`), `link_clicks`, `review_links`, `plugs`, `calendar`, `client_invites`, `rss_feeds` and `webhooks`.
- `posts.delete`, `posts.duplicate` and `analytics.content_insights`.
- `TypedDict` types generated from the OpenAPI spec, in `sociahive.api`.
- `verify_webhook_signature` checks the `X-SociaHive-Signature` header of a webhook delivery.
- `SociaHiveError.retry_after`: seconds from the `Retry-After` header on a 429.

### Changed

- Platform ids are plain `str`, so a platform added later needs no SDK release.
- The documented platform ids cover every public platform, including Telegram channels, Discord, Slack, Mastodon, Lemmy, Tumblr, Dev.to, Hashnode, WordPress, Listmonk, Dribbble, Twitch and Kick.
- `SociaHiveError.code` prefers the server's `code` field and falls back to `error`.
- Package contact is support@sociahive.com.

### Fixed

- `sh.posts.bulk` now matches `POST /posts/bulk`: `bulk(action, post_ids, *, scheduled_for=, timezone=, status=)` runs schedule, delete or update_status on up to 50 existing posts and returns the counts. It used to send `{"posts": [...]}`, which the API refuses. **Breaking** for anyone calling the old signature; create posts with `sh.posts.create` instead.
- `sh.flows.list` requires `platform_user_id`, as the API does.

## [0.1.0] - 2026-05-20

First release on PyPI.

### Added

- `SociaHive` client with API key (`X-API-Key`) or OAuth bearer token auth, built on `httpx`, usable as a context manager.
- `sh.accounts.list`.
- `sh.posts`: `list`, `get`, `create`, `update`, `schedule`, `publish`, `cancel`, `bulk`.
- `sh.flows`: `list`, `get`, `create`, `update`, `delete`, `activate`, `deactivate`, `add_node`, `update_node`, `add_edge`, `stats`, `collected_data`, `generate`.
- `sh.analytics`: `get`, `export`.
- `SociaHiveError` with `status`, `is_auth_error` and `is_rate_limited`.
- Python 3.9 or later.

[0.1.0]: https://pypi.org/project/sociahive/0.1.0/
[0.2.0]: https://pypi.org/project/sociahive/0.2.0/
