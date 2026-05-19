"""Official Python SDK for the SociaHive API.

Quickstart:

    from sociahive import SociaHive

    sh = SociaHive(api_key="sk_...")
    accounts = sh.accounts.list()
    print(accounts)
"""

from .client import SociaHive
from .errors import SociaHiveError

__all__ = ["SociaHive", "SociaHiveError"]
__version__ = "0.1.0"
