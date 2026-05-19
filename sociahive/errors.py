"""Error types raised by the SDK."""

from __future__ import annotations

from typing import Any


class SociaHiveError(Exception):
    """Raised on every non-2xx response from the SociaHive API."""

    def __init__(
        self,
        message: str,
        *,
        status: int,
        body: Any = None,
        code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.body = body
        self.code = code

    @property
    def is_auth_error(self) -> bool:
        return self.status in (401, 403)

    @property
    def is_rate_limited(self) -> bool:
        return self.status == 429

    @property
    def is_client_error(self) -> bool:
        return 400 <= self.status < 500

    @property
    def is_server_error(self) -> bool:
        return self.status >= 500
