"""SociaHive client: a thin ergonomic wrapper over httpx.

Mirrors the resource grouping in @sociahive/sdk (Node): ``sh.accounts``,
``sh.posts``, ``sh.flows``, ``sh.analytics`` and the scheduler resources in
``resources.py`` (``sh.media``, ``sh.signatures``, ``sh.posting_slots``,
``sh.review_links``, ``sh.plugs``, ``sh.link_clicks``, ``sh.calendar``,
``sh.client_invites``, ``sh.rss_feeds``, ``sh.webhooks``).

Auth: pass exactly one of ``api_key`` (long-lived) or ``oauth_token`` (per-user OAuth).
"""

from __future__ import annotations

from typing import Any, Iterable, Literal, Sequence

import httpx

from .errors import SociaHiveError
from .resources import (
    Calendar,
    ClientInvites,
    LinkClicks,
    Media,
    Plugs,
    PostingSlots,
    ReviewLinks,
    RssFeeds,
    Signatures,
    Webhooks,
)

DEFAULT_BASE_URL = "https://www.sociahive.com/api/v1"
DEFAULT_TIMEOUT = 30.0

# Platform ids are plain strings: the public spec lists only public platforms,
# and a new platform must not need an SDK release.
Platform = str


class _Resource:
    """Base for nested resource accessors (sh.posts, sh.flows, etc.)."""

    def __init__(self, client: "SociaHive") -> None:
        self._client = client


class _Accounts(_Resource):
    def list(self, *, platform: Platform | None = None) -> dict[str, Any]:
        return self._client._request(
            "GET", "/connected-accounts",
            params={"platform": platform} if platform else None,
        )


def _lift_content(payload: dict[str, Any]) -> dict[str, Any]:
    """The v1 ``POST /posts`` endpoint expects ``{ content: { text, media }, ... }``.
    We let SDK callers pass ``text`` and ``media`` at the top level for ergonomics
    and lift them into the ``content`` envelope here. Idempotent: if the caller
    already passed ``content``, we leave their payload alone.
    """
    if "content" in payload:
        return payload
    out = dict(payload)
    text = out.pop("text", None)
    media = out.pop("media", None)
    if text is not None or media is not None:
        content: dict[str, Any] = {}
        if text is not None:
            content["text"] = text
        if media is not None:
            content["media"] = media
        out["content"] = content
    return out


class _Posts(_Resource):
    def list(
        self, *,
        status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client._request("GET", "/posts", params={
            "status": status, "limit": limit, "offset": offset,
        })

    def get(self, post_id: str) -> dict[str, Any]:
        return self._client._request("GET", f"/posts/{post_id}")

    def create(self, **kwargs: Any) -> dict[str, Any]:
        """Create a post. Accepts ``text`` and ``media`` at top level for
        ergonomics; lifts them into the wire format's ``content`` envelope
        before sending. See https://www.sociahive.com/api/v1/docs#tag/Posts.
        """
        return self._client._request("POST", "/posts", json=_lift_content(kwargs))

    def update(self, post_id: str, **patch: Any) -> dict[str, Any]:
        return self._client._request("PUT", f"/posts/{post_id}", json=_lift_content(patch))

    def schedule(self, post_id: str, scheduled_at: str, timezone: str = "UTC") -> dict[str, Any]:
        return self._client._request(
            "POST", f"/posts/{post_id}/schedule",
            json={"scheduled_at": scheduled_at, "timezone": timezone},
        )

    def publish(self, post_id: str) -> dict[str, Any]:
        return self._client._request("POST", f"/posts/{post_id}/publish")

    def cancel(self, post_id: str) -> dict[str, Any]:
        return self._client._request("POST", f"/posts/{post_id}/cancel")

    def delete(self, post_id: str) -> None:
        self._client._request("DELETE", f"/posts/{post_id}")

    def duplicate(self, post_id: str) -> dict[str, Any]:
        """Copy a post as a new draft."""
        return self._client._request("POST", f"/posts/{post_id}/duplicate")

    def bulk(
        self,
        action: Literal["schedule", "delete", "update_status"],
        post_ids: Sequence[str],
        *,
        scheduled_for: str | None = None,
        timezone: str | None = None,
        status: Literal["draft", "scheduled"] | None = None,
    ) -> dict[str, Any]:
        """Apply one action to up to 50 existing posts.

        - ``action="schedule"`` needs ``scheduled_for`` (ISO 8601); ``timezone``
          is optional (the API defaults to UTC).
        - ``action="delete"`` deletes the posts.
        - ``action="update_status"`` needs ``status`` (``"draft"`` or ``"scheduled"``).

        It does not create posts; call :meth:`create` for each one. Returns
        ``{"total", "succeeded", "failed", "errors": [{"post_id", "error"}]}``.
        """
        ids = list(post_ids)
        if not 1 <= len(ids) <= 50:
            raise ValueError("posts.bulk takes 1 to 50 post_ids")
        if action == "schedule" and not scheduled_for:
            raise ValueError('action="schedule" needs scheduled_for')
        if action == "update_status" and not status:
            raise ValueError('action="update_status" needs status')
        body: dict[str, Any] = {"action": action, "post_ids": ids}
        if action == "schedule":
            body["scheduled_for"] = scheduled_for
            if timezone:
                body["timezone"] = timezone
        if action == "update_status":
            body["status"] = status
        return self._client._request("POST", "/posts/bulk", json=body)


class _Flows(_Resource):
    def list(self, *, platform_user_id: str) -> dict[str, Any]:
        """List the flows of one connected account. ``platform_user_id`` is
        required: take it from ``sh.accounts.list()``.
        """
        # v1 quirk: this endpoint returns `{"flows": [...]}` not `{"data": [...]}`.
        # Normalize so every SDK list call exposes the same `.data` key.
        raw = self._client._request(
            "GET", "/flows",
            params={"platform_user_id": platform_user_id},
        )
        if isinstance(raw, dict) and "flows" in raw and "data" not in raw:
            items = [_normalize_id(f) for f in (raw.get("flows") or [])]
            return {"data": items, "pagination": raw.get("pagination") or {
                "limit": len(items), "offset": 0, "total": len(items),
            }}
        # Paginated lists already auto-unwrapped won't reach here normally,
        # but if the response is `{data: [...], pagination: ...}` we still
        # want to normalize each item's id.
        if isinstance(raw, dict) and isinstance(raw.get("data"), list):
            raw = dict(raw)
            raw["data"] = [_normalize_id(f) for f in raw["data"]]
        return raw

    def get(self, flow_id: str) -> dict[str, Any]:
        # v1 quirk: this endpoint returns `{"flow": {...}, "nodes": [...], "edges": [...]}`
        # instead of the standard envelope. Merge into one object so callers see
        # `result["id"]`, `result["nodes"]`, etc. like every other resource.
        raw = self._client._request("GET", f"/flows/{flow_id}")
        if isinstance(raw, dict) and "flow" in raw and isinstance(raw.get("flow"), dict):
            flow = _normalize_id(raw["flow"])
            return {
                **flow,
                "nodes": [_normalize_id(n) for n in (raw.get("nodes") or [])],
                "edges": [_normalize_id(e) for e in (raw.get("edges") or [])],
            }
        return raw

    def create(self, **kwargs: Any) -> dict[str, Any]:
        return self._client._request("POST", "/flows", json=kwargs)

    def update(self, flow_id: str, **patch: Any) -> dict[str, Any]:
        return self._client._request("PATCH", f"/flows/{flow_id}", json=patch)

    def delete(self, flow_id: str) -> None:
        self._client._request("DELETE", f"/flows/{flow_id}")

    def activate(self, flow_id: str) -> dict[str, Any]:
        return self.update(flow_id, status="published")

    def deactivate(self, flow_id: str) -> dict[str, Any]:
        return self.update(flow_id, status="draft")

    def add_node(
        self, flow_id: str, *,
        type: str,
        data: dict[str, Any],
        position: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"type": type, "data": data}
        if position is not None:
            body["position"] = position
        return self._client._request("POST", f"/flows/{flow_id}/nodes", json=body)

    def update_node(self, flow_id: str, node_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._client._request(
            "PUT", f"/flows/{flow_id}/nodes/{node_id}",
            json={"data": data},
        )

    def add_edge(
        self, flow_id: str, *,
        source: str,
        target: str,
        source_handle: str | None = None,
        target_handle: str | None = None,
        type: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"source": source, "target": target}
        if source_handle is not None:
            body["sourceHandle"] = source_handle
        if target_handle is not None:
            body["targetHandle"] = target_handle
        if type is not None:
            body["type"] = type
        if data is not None:
            body["data"] = data
        return self._client._request("POST", f"/flows/{flow_id}/edges", json=body)

    def stats(self, flow_id: str) -> dict[str, Any]:
        return self._client._request("GET", f"/flows/{flow_id}/stats")

    def collected_data(self, flow_id: str) -> dict[str, Any]:
        return self._client._request("GET", f"/flows/{flow_id}/collected-data")

    def generate(
        self, *,
        description: str,
        account_id: str,
        platform_user_id: str,
        platform: Platform | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "description": description,
            "account_id": account_id,
            "platform_user_id": platform_user_id,
        }
        if platform is not None:
            body["platform"] = platform
        return self._client._request("POST", "/flows/generate", json=body)


class _Analytics(_Resource):
    def get(
        self, *,
        post_id: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        platform: Platform | None = None,
    ) -> dict[str, Any]:
        return self._client._request("GET", "/analytics", params={
            "post_id": post_id,
            "start_date": start_date,
            "end_date": end_date,
            "platform": platform,
        })

    def export(
        self, *,
        type: Literal["posts", "flows", "accounts"],
        format: Literal["json", "csv"] = "json",
        from_: str | None = None,
        to: str | None = None,
    ) -> Any:
        return self._client._request("GET", "/analytics/export", params={
            "type": type, "format": format, "from": from_, "to": to,
        })

    def content_insights(self, *, weeks: int | None = None) -> dict[str, Any]:
        """What has worked on your published posts over the last ``weeks`` (1 to 12)."""
        return self._client._request_data("GET", "/analytics/content-insights", params={"weeks": weeks})


class SociaHive:
    """Main entry point. Construct once, reuse for many calls.

    Pass exactly one of ``api_key`` or ``oauth_token``::

        sh = SociaHive(api_key="sk_...")
        sh = SociaHive(oauth_token="sh_at_...")
    """

    def __init__(
        self, *,
        api_key: str | None = None,
        oauth_token: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        client: httpx.Client | None = None,
        upload_client: httpx.Client | None = None,
    ) -> None:
        if not (bool(api_key) ^ bool(oauth_token)):
            raise ValueError("Pass exactly one of `api_key` or `oauth_token`")
        if api_key:
            headers = {"X-API-Key": api_key}
        else:
            headers = {"Authorization": f"Bearer {oauth_token}"}
        headers["Content-Type"] = "application/json"

        self._http = client or httpx.Client(
            base_url=base_url.rstrip("/"),
            headers=headers,
            timeout=timeout,
        )
        # A separate client without the auth headers, for presigned storage URLs.
        self._upload_http = upload_client or httpx.Client(timeout=timeout)
        self.accounts = _Accounts(self)
        self.posts = _Posts(self)
        self.flows = _Flows(self)
        self.analytics = _Analytics(self)
        self.media = Media(self)
        self.signatures = Signatures(self)
        self.posting_slots = PostingSlots(self)
        self.review_links = ReviewLinks(self)
        self.plugs = Plugs(self)
        self.link_clicks = LinkClicks(self)
        self.calendar = Calendar(self)
        self.client_invites = ClientInvites(self)
        self.rss_feeds = RssFeeds(self)
        self.webhooks = Webhooks(self)

    def close(self) -> None:
        self._http.close()
        self._upload_http.close()

    def __enter__(self) -> "SociaHive":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    # ── internal ────────────────────────────────────────────────────

    def _request_data(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
    ) -> Any:
        """Like ``_request`` but also unwraps ``{"data": [...]}`` lists."""
        body = self._request(method, path, params=params, json=json)
        if isinstance(body, dict) and "data" in body and "pagination" not in body:
            return _normalize_id(body["data"])
        return body

    def _put_bytes(self, url: str, data: bytes, headers: dict[str, str]) -> int:
        """PUT to a presigned storage URL. The API key is never sent there."""
        try:
            resp = self._upload_http.put(url, content=data, headers=headers)
        except httpx.RequestError as exc:
            raise SociaHiveError(f"Upload failed: {exc}", status=0, code="upload_failed") from exc
        return resp.status_code

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
    ) -> Any:
        # Drop None query params so they don't render as "key="
        clean_params = (
            {k: v for k, v in params.items() if v is not None}
            if params else None
        )
        try:
            resp = self._http.request(method, path, params=clean_params, json=json)
        except httpx.TimeoutException as exc:
            raise SociaHiveError(
                f"Request timed out: {exc}", status=0, code="timeout",
            ) from exc
        except httpx.RequestError as exc:
            raise SociaHiveError(
                f"Network error: {exc}", status=0, code="network_error",
            ) from exc

        try:
            body = resp.json() if resp.text else None
        except ValueError:
            body = resp.text

        if not resp.is_success:
            err = body if isinstance(body, dict) else {"error": body}
            retry_after: float | None = None
            try:
                parsed = float(resp.headers.get("retry-after", ""))
                retry_after = parsed if parsed > 0 else None
            except ValueError:
                retry_after = None
            raise SociaHiveError(
                err.get("error_description") or err.get("error") or f"HTTP {resp.status_code}",
                status=resp.status_code,
                body=body,
                code=err.get("code") or err.get("error"),
                retry_after=retry_after,
            )
        return _unwrap_envelope(body)


def _unwrap_envelope(body: Any) -> Any:
    """Strip the v1 single-resource ``{"data": {...}}`` envelope so callers see
    the object directly. Paginated lists ``{"data": [...], "pagination": {...}}``
    are left alone; callers expect both fields. Mirrors Node SDK behaviour.
    """
    if (
        isinstance(body, dict)
        and "data" in body
        and "pagination" not in body
        and isinstance(body["data"], dict)
    ):
        return _normalize_id(body["data"])
    if isinstance(body, dict):
        return _normalize_id(body)
    return body


def _normalize_id(value: Any) -> Any:
    """Surface Mongo's ``_id`` under ``id`` when callers expect ``id``.
    Some v1 list endpoints (notably ``/flows``) return raw ``_id`` only.
    """
    if isinstance(value, list):
        return [_normalize_id(v) for v in value]
    if isinstance(value, dict):
        if value.get("id") is None and isinstance(value.get("_id"), str):
            out = dict(value)
            out["id"] = value["_id"]
            return out
    return value
