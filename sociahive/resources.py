"""Scheduler resources: media, signatures, posting slots, review links, plugs,
link clicks, calendar, client invites, RSS feeds and webhooks.

Return types are the TypedDicts in ``_generated.py``, generated from the v1
OpenAPI spec. Each method returns the ``data`` of the response envelope.

Several features roll out per account: until a feature reaches your account its
endpoints raise ``SociaHiveError`` with ``status == 403`` and
``code == "feature_disabled"``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable, Literal, Union
from urllib.parse import quote

from . import _generated as api
from .errors import SociaHiveError

if TYPE_CHECKING:
    from .client import SociaHive

MimeType = Literal["image/jpeg", "image/png", "image/webp", "video/mp4", "video/quicktime"]


def _ids(account_ids: Iterable[str] | None) -> str | None:
    if account_ids is None:
        return None
    return ",".join(account_ids)


def _seg(value: str) -> str:
    return quote(value, safe="")


class _Base:
    def __init__(self, client: "SociaHive") -> None:
        self._client = client

    def _data(self, method: str, path: str, *, params: dict[str, Any] | None = None, json: Any = None) -> Any:
        return self._client._request_data(method, path, params=params, json=json)


class Media(_Base):
    def list(
        self, *,
        kind: Literal["image", "video"] | None = None,
        tag: str | None = None,
        q: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> api.MediaLibraryPage:
        """Your media library, newest first. Pass ``next_cursor`` as ``cursor`` for the next page."""
        return self._data("GET", "/media-library", params={
            "kind": kind, "tag": tag, "q": q, "limit": limit, "cursor": cursor,
        })

    def upload_from_url(self, url: str) -> api.UploadFromUrlResponse:
        """Copy a public image or video URL into SociaHive storage."""
        return self._data("POST", "/uploads/from-url", json={"url": url})

    def presign(self, *, filename: str, mime_type: MimeType, size_bytes: int) -> api.PresignUploadResponse:
        return self._data("POST", "/uploads/presign", json={
            "filename": filename, "mime_type": mime_type, "size_bytes": size_bytes,
        })

    def verify(self, *, key: str, purpose: Literal["scheduler"] | None = None, filename: str | None = None) -> api.VerifyUploadResponse:
        body: dict[str, Any] = {"key": key}
        if purpose is not None:
            body["purpose"] = purpose
        if filename is not None:
            body["filename"] = filename
        return self._data("POST", "/uploads/verify", json=body)

    def upload(self, data: bytes, *, filename: str, mime_type: MimeType) -> dict[str, Any]:
        """Upload bytes in one call (presign, PUT, verify). The file is added to
        the media library. Returns the verify result plus ``key`` and ``public_url``."""
        presigned = self.presign(filename=filename, mime_type=mime_type, size_bytes=len(data))
        headers = {"Content-Type": mime_type, **(presigned.get("required_headers") or {})}
        put = self._client._put_bytes(presigned["upload_url"], data, headers)
        if not 200 <= put < 300:
            raise SociaHiveError(f"Upload failed with HTTP {put}", status=put, code="upload_failed")
        verified = dict(self.verify(key=presigned["key"], purpose="scheduler", filename=filename))
        verified["key"] = presigned["key"]
        verified["public_url"] = verified.get("public_url") or presigned["public_url"]
        return verified

    def generate_image(self, *, aspect: Literal["square", "portrait", "landscape"], **kwargs: Any) -> api.GenerateImageResponse:
        """Up to 4 AI images from ``prompt`` or ``caption``. Added to the media library."""
        return self._data("POST", "/media/generate-image", json={"aspect": aspect, **kwargs})

    def image_allowance(self) -> api.AiImageAllowance:
        return self._data("GET", "/media/generate-image")["allowance"]


class Signatures(_Base):
    def list(self) -> api.SignatureList:
        return self._data("GET", "/signatures")

    def create(self, *, name: str, text: str, **kwargs: Any) -> api.Signature:
        return self._data("POST", "/signatures", json={"name": name, "text": text, **kwargs})

    def update(self, signature_id: str, **patch: Any) -> api.Signature:
        return self._data("PATCH", f"/signatures/{_seg(signature_id)}", json=patch)

    def delete(self, signature_id: str) -> dict[str, Any]:
        return self._data("DELETE", f"/signatures/{_seg(signature_id)}")


class PostingSlots(_Base):
    def list(self, *, account_ids: Iterable[str] | None = None) -> list[api.PostingSlot]:
        return self._data("GET", "/posting-slots", params={"account_ids": _ids(account_ids)})

    def create(self, *, account_ids: list[str], weekday: int, timezone: str, **kwargs: Any) -> api.PostingSlot:
        """A weekly posting time. Pass ``time="09:00"`` or ``minutes=540``."""
        return self._data("POST", "/posting-slots", json={
            "account_ids": account_ids, "weekday": weekday, "timezone": timezone, **kwargs,
        })

    def update(self, slot_id: str, **patch: Any) -> api.PostingSlot:
        return self._data("PATCH", f"/posting-slots/{_seg(slot_id)}", json=patch)

    def delete(self, slot_id: str) -> dict[str, Any]:
        return self._data("DELETE", f"/posting-slots/{_seg(slot_id)}")

    def occurrences(
        self, *, from_: str, to: str, timezone: str | None = None, account_ids: Iterable[str] | None = None,
    ) -> list[api.SlotOccurrence]:
        return self._data("GET", "/posting-slots/occurrences", params={
            "from": from_, "to": to, "timezone": timezone, "account_ids": _ids(account_ids),
        })

    def find_slot(self, *, account_ids: Iterable[str], after: str | None = None) -> api.FreeSlot:
        """The next free slot of these accounts, held for you for 10 minutes.
        Create the post with ``scheduled_at`` = ``at`` to keep it."""
        return self._data("GET", "/find-slot", params={"account_ids": _ids(account_ids), "after": after})


class ReviewLinks(_Base):
    def list(self, post_id: str) -> api.ReviewSummary:
        return self._data("GET", f"/posts/{_seg(post_id)}/review-links")

    def create(self, post_id: str, *, reviewer_name: str | None = None) -> api.ReviewLink:
        """Make a client review link. The URL is returned once; store it."""
        body = {"reviewer_name": reviewer_name} if reviewer_name else {}
        return self._data("POST", f"/posts/{_seg(post_id)}/review-links", json=body)

    def revoke(self, post_id: str, link_id: str) -> api.ReviewLink:
        return self._data("DELETE", f"/posts/{_seg(post_id)}/review-links", params={"link_id": link_id})


class Plugs(_Base):
    def list(self, post_id: str) -> api.PostPlugs:
        return self._data("GET", f"/posts/{_seg(post_id)}/plugs")

    def arm(self, post_id: str, *, account_id: str, trigger: dict[str, Any], action: dict[str, Any]) -> api.Plug:
        """Repost or comment once when the metric reaches the threshold. This acts on a real audience."""
        return self._data("POST", f"/posts/{_seg(post_id)}/plugs", json={
            "account_id": account_id, "trigger": trigger, "action": action,
        })

    def delete(self, post_id: str, plug_id: str) -> dict[str, Any]:
        return self._data("DELETE", f"/posts/{_seg(post_id)}/plugs", params={"plug_id": plug_id})


class LinkClicks(_Base):
    def get(self, post_id: str) -> api.LinkClicks:
        return self._data("GET", f"/posts/{_seg(post_id)}/link-clicks")


class Calendar(_Base):
    def month(self, *, year: int | None = None, month: int | None = None, timezone: str | None = None, **kwargs: Any) -> dict[str, Any]:
        return self._data("GET", "/calendar", params={"year": year, "month": month, "timezone": timezone, **kwargs})

    def duplicate(self, post_id: str) -> api.Post:
        return self._data("POST", f"/posts/{_seg(post_id)}/duplicate")

    def stats(self, post_id: str) -> dict[str, Any]:
        return self._data("GET", f"/calendar-actions/posts/{_seg(post_id)}/stats")


class ClientInvites(_Base):
    def list(self, *, group_id: str | None = None) -> list[api.ClientInvite]:
        return self._data("GET", "/client-invites", params={"group_id": group_id})

    def create(self, *, group_id: str, **kwargs: Any) -> api.ClientInvite:
        """Invite a client to connect accounts to an account group. The URL is returned once."""
        return self._data("POST", "/client-invites", json={"group_id": group_id, **kwargs})

    def revoke(self, invite_id: str) -> api.ClientInvite:
        return self._data("DELETE", "/client-invites", params={"invite_id": invite_id})


class RssFeeds(_Base):
    def list(self) -> list[api.RssFeed]:
        return self._data("GET", "/rss-feeds")

    def create(self, *, url: str, **kwargs: Any) -> api.RssFeed:
        return self._data("POST", "/rss-feeds", json={"url": url, **kwargs})

    def update(self, feed_id: str, **patch: Any) -> api.RssFeed:
        return self._data("PATCH", f"/rss-feeds/{_seg(feed_id)}", json=patch)

    def pause(self, feed_id: str, paused: bool = True) -> api.RssFeed:
        return self._data("POST", f"/rss-feeds/{_seg(feed_id)}/pause", json={"paused": paused})


WebhookEvent = Union[
    Literal[
        "post.published", "post.failed", "post.review_decision", "post.plug_fired",
        "flow.triggered", "flow.completed", "flow.error", "message.received",
        "comment.received", "account.disconnected", "whatsapp.template_status",
    ],
    str,
]


class Webhooks(_Base):
    """Outbound webhook subscriptions. ``create`` returns ``signing_secret`` once."""

    def list(self) -> list[dict[str, Any]]:
        return self._data("GET", "/webhooks")

    def create(
        self, *,
        target_url: str,
        events: list[WebhookEvent],
        integration_type: str | None = None,
        account_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"target_url": target_url, "events": events}
        if integration_type is not None:
            body["integration_type"] = integration_type
        if account_ids is not None:
            body["account_ids"] = account_ids
        return self._data("POST", "/webhooks", json=body)

    def update(self, webhook_id: str, **patch: Any) -> dict[str, Any]:
        return self._data("PATCH", f"/webhooks/{_seg(webhook_id)}", json=patch)

    def delete(self, webhook_id: str) -> None:
        self._data("DELETE", f"/webhooks/{_seg(webhook_id)}")
