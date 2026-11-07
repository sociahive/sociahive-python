# Changelog

All notable changes to the `sociahive` Python package are listed here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2026-11-07

### Added

- `sh.approvals`: `list` (posts waiting for your approval), `get`, `approve`, `request_changes` and `undo`. `approve` returns the whole response, because `undo` (a `batch_id`, valid 30 seconds) sits next to `data`. Send `content_hash` from `list` or `get` so a post edited since is refused instead of approved.
- `sh.comments`: `list`, `add` (team or client visibility, replies with `parent_id`), `resolve`, `inbox` and `mark_seen`.
- `sh.notifications`: `matrix`, `update_matrix`, `mute_client` and `unmute_client`.
- TypedDicts for these endpoints in `sociahive.api` (`WaitingApproval`, `ApprovalView`, `PostComment`, `PostCommentThreads`, `CommentsInboxItem`, `NotificationMatrixPatch` and others).

## [0.3.0] - 2026-11-05

### Added

- Unpublished changes of a live flow. Edits to a published or paused flow wait as unpublished changes while people keep getting the live version.
  - `sh.flows.pending(flow_id)` previews what publishing them would change: steps added, removed and changed, and how many people are partway through a removed step.
  - `sh.flows.publish_changes(flow_id, expected_rev=...)` publishes them with the same checks as turning a flow on, and returns the flow and an `undo` token.
  - `sh.flows.discard_changes(flow_id, expected_rev=None)` drops them; the live version is unchanged.
  - `sh.flows.get(flow_id, version="pending")` returns the unpublished version of the graph, with `pending` (its `rev`, or `None` when there are none) and `target`.
  - `sh.flows.list()` items carry `hasPendingChanges`.
- Generated types: `FlowPendingChanges`, `FlowPendingPublished`, `FlowPendingDiscarded`, `FlowPendingSummary`, and the other fields the API added since 0.2.1 (for example `reconnect_to_publish` on connected accounts and PDF uploads for flow messages).

## [0.2.1] - 2026-10-26

### Changed

- Releases are published from GitHub Actions through PyPI trusted publishing. No code changes.

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
[0.3.0]: https://pypi.org/project/sociahive/0.3.0/
