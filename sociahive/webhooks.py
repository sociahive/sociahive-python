"""Verify a SociaHive webhook delivery.

    X-SociaHive-Signature: t=<unix seconds>,v1=<hex HMAC-SHA256 of "<t>.<raw body>">
"""

from __future__ import annotations

import hashlib
import hmac
import time

DEFAULT_TOLERANCE_SEC = 300


def verify_webhook_signature(
    *,
    body: str | bytes,
    signature: str | None,
    secret: str,
    tolerance_sec: int = DEFAULT_TOLERANCE_SEC,
    now: float | None = None,
) -> bool:
    """True when the signature matches the raw body and the timestamp is within tolerance."""
    if not signature or not secret:
        return False
    timestamp: int | None = None
    candidates: list[str] = []
    for part in signature.split(","):
        key, _, value = part.strip().partition("=")
        if key == "t" and value.isdigit():
            timestamp = int(value)
        elif key == "v1" and value:
            candidates.append(value.lower())
    if timestamp is None or not candidates:
        return False
    current = time.time() if now is None else now
    if abs(current - timestamp) > tolerance_sec:
        return False
    raw = body.decode("utf-8") if isinstance(body, bytes) else body
    expected = hmac.new(secret.encode(), f"{timestamp}.{raw}".encode(), hashlib.sha256).hexdigest()
    return any(hmac.compare_digest(c, expected) for c in candidates)
