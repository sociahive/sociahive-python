"""Contract test: each resource method sends the request the v1 spec describes,
against a mocked server, and returns the unwrapped ``data``.

Run: python -m unittest discover -s tests (from sdks/python, with httpx installed)
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
import unittest
from pathlib import Path
from typing import Any, Callable

import httpx

from sociahive import SociaHive, SociaHiveError, verify_webhook_signature

ID = "507f1f77bcf86cd799439011"
ID2 = "507f1f77bcf86cd799439012"


def make(respond: Callable[[httpx.Request], httpx.Response] | None = None):
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if respond:
            return respond(request)
        return httpx.Response(200, json={"success": True, "data": {"ok": True}})

    transport = httpx.MockTransport(handler)
    client = httpx.Client(base_url="https://api.test/api/v1", headers={"X-API-Key": "sk_test"}, transport=transport)
    upload = httpx.Client(transport=transport)
    sh = SociaHive(api_key="sk_test", client=client, upload_client=upload)
    return sh, calls


# (spec operation key, call, expected path, expected query, expected body)
CASES: list[tuple[str, Callable[[SociaHive], Any], str, dict[str, str], Any]] = [
    ("GET /connected-accounts", lambda sh: sh.accounts.list(platform="new-platform"), "/connected-accounts", {"platform": "new-platform"}, None),
    ("GET /posts", lambda sh: sh.posts.list(status="draft"), "/posts", {"status": "draft"}, None),
    ("POST /posts", lambda sh: sh.posts.create(text="hi", platforms=[]), "/posts", {}, {"platforms": [], "content": {"text": "hi"}}),
    ("GET /posts/{id}", lambda sh: sh.posts.get(ID), f"/posts/{ID}", {}, None),
    ("PUT /posts/{id}", lambda sh: sh.posts.update(ID, text="x"), f"/posts/{ID}", {}, {"content": {"text": "x"}}),
    ("DELETE /posts/{id}", lambda sh: sh.posts.delete(ID), f"/posts/{ID}", {}, None),
    ("POST /posts/{id}/schedule", lambda sh: sh.posts.schedule(ID, "2026-11-01T09:00:00Z"), f"/posts/{ID}/schedule", {}, {"scheduled_at": "2026-11-01T09:00:00Z", "timezone": "UTC"}),
    ("POST /posts/{id}/publish", lambda sh: sh.posts.publish(ID), f"/posts/{ID}/publish", {}, None),
    ("POST /posts/{id}/cancel", lambda sh: sh.posts.cancel(ID), f"/posts/{ID}/cancel", {}, None),
    ("POST /posts/bulk", lambda sh: sh.posts.bulk("schedule", [ID, ID2], scheduled_for="2026-11-01T09:00:00Z"), "/posts/bulk", {}, {"action": "schedule", "post_ids": [ID, ID2], "scheduled_for": "2026-11-01T09:00:00Z"}),
    ("POST /posts/{id}/duplicate", lambda sh: sh.calendar.duplicate(ID), f"/posts/{ID}/duplicate", {}, None),
    ("GET /calendar", lambda sh: sh.calendar.month(year=2026, month=11), "/calendar", {"year": "2026", "month": "11"}, None),
    ("GET /calendar-actions/posts/{id}/stats", lambda sh: sh.calendar.stats(ID), f"/calendar-actions/posts/{ID}/stats", {}, None),
    ("GET /analytics", lambda sh: sh.analytics.get(platform="instagram"), "/analytics", {"platform": "instagram"}, None),
    ("GET /analytics/export", lambda sh: sh.analytics.export(type="posts"), "/analytics/export", {"type": "posts", "format": "json"}, None),
    ("GET /analytics/content-insights", lambda sh: sh.analytics.content_insights(weeks=4), "/analytics/content-insights", {"weeks": "4"}, None),
    ("GET /media-library", lambda sh: sh.media.list(kind="video", limit=5), "/media-library", {"kind": "video", "limit": "5"}, None),
    ("POST /uploads/from-url", lambda sh: sh.media.upload_from_url("https://x.test/a.png"), "/uploads/from-url", {}, {"url": "https://x.test/a.png"}),
    ("POST /uploads/presign", lambda sh: sh.media.presign(filename="a.png", mime_type="image/png", size_bytes=3), "/uploads/presign", {}, {"filename": "a.png", "mime_type": "image/png", "size_bytes": 3}),
    ("POST /uploads/verify", lambda sh: sh.media.verify(key="k", purpose="scheduler"), "/uploads/verify", {}, {"key": "k", "purpose": "scheduler"}),
    ("POST /media/generate-image", lambda sh: sh.media.generate_image(aspect="square", prompt="a cat"), "/media/generate-image", {}, {"aspect": "square", "prompt": "a cat"}),
    ("GET /media/generate-image", lambda sh: sh.media.image_allowance(), "/media/generate-image", {}, None),
    ("GET /signatures", lambda sh: sh.signatures.list(), "/signatures", {}, None),
    ("POST /signatures", lambda sh: sh.signatures.create(name="S", text="-- us"), "/signatures", {}, {"name": "S", "text": "-- us"}),
    ("PATCH /signatures/{id}", lambda sh: sh.signatures.update(ID, is_default=True), f"/signatures/{ID}", {}, {"is_default": True}),
    ("DELETE /signatures/{id}", lambda sh: sh.signatures.delete(ID), f"/signatures/{ID}", {}, None),
    ("GET /posting-slots", lambda sh: sh.posting_slots.list(account_ids=[ID, ID2]), "/posting-slots", {"account_ids": f"{ID},{ID2}"}, None),
    ("POST /posting-slots", lambda sh: sh.posting_slots.create(account_ids=[ID], weekday=1, timezone="UTC", time="09:00"), "/posting-slots", {}, {"account_ids": [ID], "weekday": 1, "timezone": "UTC", "time": "09:00"}),
    ("PATCH /posting-slots/{id}", lambda sh: sh.posting_slots.update(ID, weekday=2), f"/posting-slots/{ID}", {}, {"weekday": 2}),
    ("DELETE /posting-slots/{id}", lambda sh: sh.posting_slots.delete(ID), f"/posting-slots/{ID}", {}, None),
    ("GET /posting-slots/occurrences", lambda sh: sh.posting_slots.occurrences(from_="2026-11-01", to="2026-11-07"), "/posting-slots/occurrences", {"from": "2026-11-01", "to": "2026-11-07"}, None),
    ("GET /find-slot", lambda sh: sh.posting_slots.find_slot(account_ids=[ID]), "/find-slot", {"account_ids": ID}, None),
    ("GET /posts/{id}/link-clicks", lambda sh: sh.link_clicks.get(ID), f"/posts/{ID}/link-clicks", {}, None),
    ("GET /posts/{id}/review-links", lambda sh: sh.review_links.list(ID), f"/posts/{ID}/review-links", {}, None),
    ("POST /posts/{id}/review-links", lambda sh: sh.review_links.create(ID, reviewer_name="Ana"), f"/posts/{ID}/review-links", {}, {"reviewer_name": "Ana"}),
    ("DELETE /posts/{id}/review-links", lambda sh: sh.review_links.revoke(ID, ID2), f"/posts/{ID}/review-links", {"link_id": ID2}, None),
    ("GET /posts/{id}/plugs", lambda sh: sh.plugs.list(ID), f"/posts/{ID}/plugs", {}, None),
    ("POST /posts/{id}/plugs", lambda sh: sh.plugs.arm(ID, account_id=ID2, trigger={"metric": "likes", "threshold": 10}, action={"kind": "repost"}), f"/posts/{ID}/plugs", {}, {"account_id": ID2, "trigger": {"metric": "likes", "threshold": 10}, "action": {"kind": "repost"}}),
    ("DELETE /posts/{id}/plugs", lambda sh: sh.plugs.delete(ID, ID2), f"/posts/{ID}/plugs", {"plug_id": ID2}, None),
    ("GET /client-invites", lambda sh: sh.client_invites.list(group_id=ID), "/client-invites", {"group_id": ID}, None),
    ("POST /client-invites", lambda sh: sh.client_invites.create(group_id=ID), "/client-invites", {}, {"group_id": ID}),
    ("DELETE /client-invites", lambda sh: sh.client_invites.revoke(ID2), "/client-invites", {"invite_id": ID2}, None),
    ("GET /rss-feeds", lambda sh: sh.rss_feeds.list(), "/rss-feeds", {}, None),
    ("POST /rss-feeds", lambda sh: sh.rss_feeds.create(url="https://b.test/feed"), "/rss-feeds", {}, {"url": "https://b.test/feed"}),
    ("PATCH /rss-feeds/{id}", lambda sh: sh.rss_feeds.update(ID, daily_cap=2), f"/rss-feeds/{ID}", {}, {"daily_cap": 2}),
    ("POST /rss-feeds/{id}/pause", lambda sh: sh.rss_feeds.pause(ID, False), f"/rss-feeds/{ID}/pause", {}, {"paused": False}),
    ("GET /webhooks", lambda sh: sh.webhooks.list(), "/webhooks", {}, None),
    ("POST /webhooks", lambda sh: sh.webhooks.create(target_url="https://n8n.test/h", events=["post.published"]), "/webhooks", {}, {"target_url": "https://n8n.test/h", "events": ["post.published"]}),
    ("PATCH /webhooks/{id}", lambda sh: sh.webhooks.update(ID, active=False), f"/webhooks/{ID}", {}, {"active": False}),
    ("DELETE /webhooks/{id}", lambda sh: sh.webhooks.delete(ID), f"/webhooks/{ID}", {}, None),
]


def _default(request: httpx.Request) -> httpx.Response:
    if request.method == "GET" and request.url.path.endswith("/media/generate-image"):
        return httpx.Response(200, json={"allowance": {"used": 1, "limit": 50}})
    return httpx.Response(200, json={"success": True, "data": {"ok": True}})


class ContractTest(unittest.TestCase):
    def test_each_method_sends_the_spec_request(self) -> None:
        for key, invoke, path, query, body in CASES:
            with self.subTest(key):
                sh, calls = make(_default)
                invoke(sh)
                self.assertEqual(len(calls), 1)
                req = calls[0]
                self.assertEqual(req.method, key.split(" ")[0])
                self.assertEqual(req.url.path.replace("/api/v1", "", 1), path)
                self.assertEqual(dict(req.url.params), query)
                if body is not None:
                    self.assertEqual(json.loads(req.content), body)
                self.assertEqual(req.headers.get("x-api-key"), "sk_test")

    def test_unwraps_lists_and_keeps_pages(self) -> None:
        sh, _ = make(lambda r: httpx.Response(200, json={"success": True, "data": [{"_id": ID}]}))
        self.assertEqual(sh.posting_slots.list(), [{"_id": ID, "id": ID}])
        page = {"items": [], "next_cursor": None}
        sh, _ = make(lambda r: httpx.Response(200, json=page))
        self.assertEqual(sh.media.list(), page)

    def test_error_code_prefers_code(self) -> None:
        sh, _ = make(lambda r: httpx.Response(404, json={"error": "No posting slots", "code": "no_slots"}))
        with self.assertRaises(SociaHiveError) as ctx:
            sh.posting_slots.find_slot(account_ids=[ID])
        self.assertEqual(ctx.exception.status, 404)
        self.assertEqual(ctx.exception.code, "no_slots")

    def test_retry_after_from_header(self) -> None:
        sh, _ = make(lambda r: httpx.Response(429, json={"error": "rate_limited"}, headers={"Retry-After": "12"}))
        with self.assertRaises(SociaHiveError) as ctx:
            sh.signatures.list()
        self.assertTrue(ctx.exception.is_rate_limited)
        self.assertEqual(ctx.exception.retry_after, 12.0)
        sh, _ = make(lambda r: httpx.Response(429, json={"error": "rate_limited"}))
        with self.assertRaises(SociaHiveError) as ctx:
            sh.signatures.list()
        self.assertIsNone(ctx.exception.retry_after)

    def test_flows_list_sends_only_the_account(self) -> None:
        sh, calls = make(lambda r: httpx.Response(200, json={"flows": [{"_id": ID, "name": "Price DM"}]}))
        out = sh.flows.list(platform_user_id="17841400000000000")
        self.assertEqual(dict(calls[0].url.params), {"platform_user_id": "17841400000000000"})
        self.assertEqual(out["data"][0]["id"], ID)

    def test_bulk_checks_its_input_before_sending(self) -> None:
        sh, calls = make()
        with self.assertRaises(ValueError):
            sh.posts.bulk("delete", [])
        with self.assertRaises(ValueError):
            sh.posts.bulk("delete", [ID] * 51)
        with self.assertRaises(ValueError):
            sh.posts.bulk("schedule", [ID])
        with self.assertRaises(ValueError):
            sh.posts.bulk("update_status", [ID])
        self.assertEqual(calls, [])
        sh.posts.bulk("update_status", [ID], status="draft")
        self.assertEqual(json.loads(calls[0].content), {"action": "update_status", "post_ids": [ID], "status": "draft"})

    def test_upload_presigns_puts_without_key_and_verifies(self) -> None:
        def respond(r: httpx.Request) -> httpx.Response:
            if r.url.path.endswith("/uploads/presign"):
                return httpx.Response(200, json={"key": "k1", "upload_url": "https://r2.test/put", "public_url": "https://cdn.test/k1", "expires_at": "x"})
            if r.url.host == "r2.test":
                return httpx.Response(200)
            return httpx.Response(200, json={"verified": True, "size_bytes": 3, "asset_id": ID})

        sh, calls = make(respond)
        out = sh.media.upload(b"abc", filename="a.png", mime_type="image/png")
        self.assertEqual([f"{c.method} {c.url.host}{c.url.path}" for c in calls], [
            "POST api.test/api/v1/uploads/presign", "PUT r2.test/put", "POST api.test/api/v1/uploads/verify",
        ])
        self.assertIsNone(calls[1].headers.get("x-api-key"))
        self.assertEqual(calls[1].content, b"abc")
        self.assertEqual(out["public_url"], "https://cdn.test/k1")

    def test_upload_failure_raises(self) -> None:
        def respond(r: httpx.Request) -> httpx.Response:
            if r.url.path.endswith("/uploads/presign"):
                return httpx.Response(200, json={"key": "k", "upload_url": "https://r2.test/put", "public_url": "p", "expires_at": "x"})
            return httpx.Response(403)

        sh, _ = make(respond)
        with self.assertRaises(SociaHiveError) as ctx:
            sh.media.upload(b"a", filename="a.png", mime_type="image/png")
        self.assertEqual(ctx.exception.code, "upload_failed")

    def test_every_program_operation_is_covered(self) -> None:
        generated = Path(__file__).resolve().parents[2] / "node" / "src" / "generated.ts"
        if not generated.exists():
            self.skipTest("run inside the monorepo")
        keys = re.findall(r'^  "((?:GET|POST|PUT|PATCH|DELETE) /[^"]*)": \{', generated.read_text(), re.M)
        program = re.compile(r"^(GET|POST|PUT|PATCH|DELETE) /(media-library|media/|uploads/|signatures|posting-slots|find-slot|client-invites|rss-feeds|calendar|webhooks|connected-accounts$|analytics|posts(/bulk|/\{id\}(/(schedule|publish|cancel|duplicate|link-clicks|review-links|plugs))?)?$)")
        covered = {c[0] for c in CASES}
        self.assertEqual([k for k in keys if program.match(k) and k not in covered], [])


class WebhookSignatureTest(unittest.TestCase):
    def test_verify(self) -> None:
        secret, body, t = "s" * 64, '{"event":"post.failed"}', 1791532800
        sig = hmac.new(secret.encode(), f"{t}.{body}".encode(), hashlib.sha256).hexdigest()
        header = f"t={t},v1={sig}"
        self.assertTrue(verify_webhook_signature(body=body, signature=header, secret=secret, now=t))
        self.assertFalse(verify_webhook_signature(body=body + "x", signature=header, secret=secret, now=t))
        self.assertFalse(verify_webhook_signature(body=body, signature=header, secret=secret, now=t + 301))


class GeneratedTypesTest(unittest.TestCase):
    def test_generated_module_imports(self) -> None:
        from sociahive import api

        self.assertIn("next_cursor", api.MediaLibraryPage.__annotations__)
        self.assertIn("slot_id", api.FreeSlot.__annotations__)


if __name__ == "__main__":
    unittest.main()
