"""Official Python SDK for the SociaHive API.

Quickstart:

    from sociahive import SociaHive

    sh = SociaHive(api_key="sk_...")
    accounts = sh.accounts.list()
    print(accounts)
"""

from . import _generated as api
from .client import SociaHive
from .errors import SociaHiveError
from .webhooks import verify_webhook_signature

__all__ = ["SociaHive", "SociaHiveError", "api", "verify_webhook_signature"]
__version__ = "0.2.1"
