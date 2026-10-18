# Changelog

All notable changes to the `sociahive` Python package are listed here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `sh.autopilot`: `status`, `generate`, `adjust`, `update_brand_kit`, `approve` and `turn_on`. `approve` and `turn_on` take a required keyword-only `confirm=True`, because both go live. Reads need the `autopilot:read` scope, writes `autopilot:write`.

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

[Unreleased]: https://github.com/sociahive/sociahive-python/compare/85a4d1d...main
[0.1.0]: https://pypi.org/project/sociahive/0.1.0/
