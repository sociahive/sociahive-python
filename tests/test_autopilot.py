"""Tests for the ``sh.autopilot`` resource.

These use an ``httpx.MockTransport`` so no network is touched — each test
captures the outgoing request and asserts the method, path, and JSON body
the SDK produced, plus the unwrapped response.
"""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from sociahive import SociaHive, SociaHiveError


def _make_client(handler: Any) -> SociaHive:
    transport = httpx.MockTransport(handler)
    http = httpx.Client(
        base_url="https://www.sociahive.com/api/v1",
        headers={"X-API-Key": "sk_test", "Content-Type": "application/json"},
        transport=transport,
    )
    return SociaHive(api_key="sk_test", client=http)


def _capture(response: dict[str, Any], status: int = 200):
    """Build a MockTransport handler that records the last request."""
    seen: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["method"] = request.method
        seen["path"] = request.url.path
        seen["body"] = json.loads(request.content) if request.content else None
        return httpx.Response(status, json=response)

    return handler, seen


def test_autopilot_is_wired_on_the_client() -> None:
    sh = SociaHive(api_key="sk_test")
    assert hasattr(sh, "autopilot")
    for method in ("status", "generate", "adjust", "update_brand_kit", "approve", "turn_on"):
        assert callable(getattr(sh.autopilot, method))
    sh.close()


def test_status_gets_config() -> None:
    payload = {
        "enabled": True,
        "configured": True,
        "review_mode": "approve",
        "posts_per_week": 7,
        "account_ids": ["acc_1"],
        "paused_reason": None,
        "last_generated_at": "2026-07-01T00:00:00Z",
    }
    handler, seen = _capture(payload)
    sh = _make_client(handler)
    result = sh.autopilot.status()
    assert seen["method"] == "GET"
    assert seen["path"] == "/api/v1/autopilot/config"
    assert result["posts_per_week"] == 7
    assert result["review_mode"] == "approve"
    sh.close()


def test_generate_posts_and_returns_batch() -> None:
    payload = {"week_start": "2026-07-06", "batch_id": "batch_1", "generating": True}
    handler, seen = _capture(payload, status=202)
    sh = _make_client(handler)
    result = sh.autopilot.generate()
    assert seen["method"] == "POST"
    assert seen["path"] == "/api/v1/autopilot/generate"
    assert result["batch_id"] == "batch_1"
    assert result["generating"] is True
    sh.close()


def test_adjust_without_feedback_sends_empty_body() -> None:
    handler, seen = _capture({"ok": True}, status=202)
    sh = _make_client(handler)
    sh.autopilot.adjust()
    assert seen["method"] == "POST"
    assert seen["path"] == "/api/v1/autopilot/adjust"
    assert seen["body"] == {}
    sh.close()


def test_adjust_with_feedback() -> None:
    handler, seen = _capture({"ok": True}, status=202)
    sh = _make_client(handler)
    sh.autopilot.adjust("more reels please")
    assert seen["body"] == {"feedback": "more reels please"}
    sh.close()


def test_update_brand_kit_maps_to_api_snake_case_body() -> None:
    handler, seen = _capture({"ok": True, "brand_kit": {}})
    sh = _make_client(handler)
    sh.autopilot.update_brand_kit(
        business_name="Acme Co",
        what_you_do="We sell widgets",
        audience="SMB owners",
        voice_preset="warm",
        voice_note="approachable but sharp",
        banned_words=["cheap", "spam"],
        content_pillars=["education", "product"],
    )
    assert seen["method"] == "PUT"
    assert seen["path"] == "/api/v1/autopilot/brand-kit"
    assert seen["body"] == {
        "voice": {"preset": "warm", "custom_note": "approachable but sharp"},
        "business_name": "Acme Co",
        "what_you_do": "We sell widgets",
        "audience": "SMB owners",
        "banned_words": ["cheap", "spam"],
        "pillars": ["education", "product"],
    }
    sh.close()


def test_update_brand_kit_only_sends_provided_fields() -> None:
    handler, seen = _capture({"ok": True, "brand_kit": {}})
    sh = _make_client(handler)
    # voice is required by the API, so it is always present.
    sh.autopilot.update_brand_kit(voice_preset="expert", business_name="Acme Co")
    assert seen["body"] == {"voice": {"preset": "expert"}, "business_name": "Acme Co"}
    sh.close()


def test_approve_requires_confirm_keyword() -> None:
    sh = SociaHive(api_key="sk_test")
    with pytest.raises(TypeError):
        sh.autopilot.approve("batch_1")  # missing required keyword-only `confirm`
    sh.close()


def test_approve_sends_confirm_and_batch_id() -> None:
    handler, seen = _capture({"ok": True, "scheduled": 7, "failed": 0})
    sh = _make_client(handler)
    result = sh.autopilot.approve("batch_1", confirm=True)
    assert seen["method"] == "POST"
    assert seen["path"] == "/api/v1/autopilot/approve"
    assert seen["body"] == {"confirm": True, "batch_id": "batch_1"}
    assert result["scheduled"] == 7
    sh.close()


def test_approve_without_batch_id_omits_it() -> None:
    handler, seen = _capture({"ok": True, "scheduled": 0, "failed": 0})
    sh = _make_client(handler)
    sh.autopilot.approve(confirm=True)
    assert seen["body"] == {"confirm": True}
    sh.close()


def test_approve_surfaces_confirmation_required_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"error": "confirmation_required"})

    sh = _make_client(handler)
    with pytest.raises(SociaHiveError) as excinfo:
        sh.autopilot.approve("batch_1", confirm=False)
    assert excinfo.value.status == 400
    assert excinfo.value.code == "confirmation_required"
    sh.close()


def test_turn_on_requires_confirm_keyword() -> None:
    sh = SociaHive(api_key="sk_test")
    with pytest.raises(TypeError):
        sh.autopilot.turn_on(posts_per_week=7)  # missing required `confirm`
    sh.close()


def test_turn_on_sends_all_fields() -> None:
    payload = {"ok": True, "enabled": True, "clamped": False, "config": {}}
    handler, seen = _capture(payload)
    sh = _make_client(handler)
    result = sh.autopilot.turn_on(
        posts_per_week=14,
        review_mode="autopublish",
        account_ids=["acc_1", "acc_2"],
        confirm=True,
    )
    assert seen["method"] == "POST"
    assert seen["path"] == "/api/v1/autopilot/turn-on"
    assert seen["body"] == {
        "confirm": True,
        "posts_per_week": 14,
        "review_mode": "autopublish",
        "account_ids": ["acc_1", "acc_2"],
    }
    assert result["enabled"] is True
    sh.close()


def test_turn_on_minimal_sends_only_confirm() -> None:
    payload = {"ok": True, "enabled": True, "clamped": True, "config": {}}
    handler, seen = _capture(payload)
    sh = _make_client(handler)
    sh.autopilot.turn_on(confirm=True)
    assert seen["body"] == {"confirm": True}
    sh.close()
