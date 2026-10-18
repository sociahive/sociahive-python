"""Tests for ``sh.posts.bulk``, ``sh.flows.list`` and rate-limit errors.

Each test uses an ``httpx.MockTransport`` and checks the request the SDK sends.
"""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from sociahive import SociaHive, SociaHiveError


def _client(handler: Any) -> SociaHive:
    http = httpx.Client(
        base_url="https://www.sociahive.com/api/v1",
        headers={"X-API-Key": "sk_test", "Content-Type": "application/json"},
        transport=httpx.MockTransport(handler),
    )
    return SociaHive(api_key="sk_test", client=http)


def test_bulk_schedule_sends_the_action_body() -> None:
    seen: dict[str, Any] = {}
    result = {"total": 2, "succeeded": 2, "failed": 0, "errors": []}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["method"] = request.method
        seen["path"] = request.url.path
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"data": result})

    out = _client(handler).posts.bulk(
        "schedule", ["a", "b"], scheduled_for="2027-03-01T09:00:00Z", timezone="Europe/London",
    )

    assert seen["method"] == "POST"
    assert seen["path"] == "/api/v1/posts/bulk"
    assert seen["body"] == {
        "action": "schedule",
        "post_ids": ["a", "b"],
        "scheduled_for": "2027-03-01T09:00:00Z",
        "timezone": "Europe/London",
    }
    assert out == result


def test_bulk_update_status_and_delete_bodies() -> None:
    bodies: list[Any] = []

    def handler(request: httpx.Request) -> httpx.Response:
        bodies.append(json.loads(request.content))
        return httpx.Response(200, json={"data": {"total": 1, "succeeded": 1, "failed": 0, "errors": []}})

    sh = _client(handler)
    sh.posts.bulk("update_status", ["p1"], status="draft")
    sh.posts.bulk("delete", ["p2"])
    assert bodies == [
        {"action": "update_status", "post_ids": ["p1"], "status": "draft"},
        {"action": "delete", "post_ids": ["p2"]},
    ]


@pytest.mark.parametrize(
    "args,kwargs",
    [
        (("delete", [f"p{i}" for i in range(51)]), {}),
        (("delete", []), {}),
        (("schedule", ["p1"]), {}),
        (("update_status", ["p1"]), {}),
    ],
)
def test_bulk_refuses_bad_input_before_calling_the_api(args: Any, kwargs: Any) -> None:
    def handler(request: httpx.Request) -> httpx.Response:  # pragma: no cover
        raise AssertionError("no request expected")

    with pytest.raises(ValueError):
        _client(handler).posts.bulk(*args, **kwargs)


def test_flows_list_sends_platform_user_id() -> None:
    seen: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["params"] = dict(request.url.params)
        return httpx.Response(200, json={"flows": [{"_id": "f1"}]})

    out = _client(handler).flows.list(platform_user_id="1784")
    assert seen["params"] == {"platform_user_id": "1784"}
    assert out["data"][0]["id"] == "f1"


def test_rate_limit_error_carries_retry_after() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": "rate_limit"}, headers={"Retry-After": "23"})

    with pytest.raises(SociaHiveError) as info:
        _client(handler).posts.list()
    assert info.value.is_rate_limited
    assert info.value.retry_after == 23
