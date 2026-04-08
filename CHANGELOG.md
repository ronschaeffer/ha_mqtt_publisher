# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.1] — 2026-04-08

### Added

- Comprehensive README documentation for the v0.4.0 health module: new
  "Health & Liveness" section covering `HealthTracker` (with both
  `attach()` and manual-population patterns), `HeartbeatFile`, and
  `make_fastapi_router`. Plus a "when to use which" decision table.
- This CHANGELOG file (backfilled with 0.4.0 entry).
- Mention of the `[fastapi]` extra in the Installation section.

### Fixed

- Lint cleanup on `health.py` and `healthcheck_cli.py` (ruff format
  + import sort) that should have been part of 0.4.0.

## [0.4.0] — 2026-04-07

### Added

- New `health` module with three primitives for exposing real MQTT-broker
  liveness to external healthchecks (Docker `HEALTHCHECK`, Kubernetes probes,
  monitoring systems):
  - `HealthTracker` — wraps an `MQTTPublisher` via `attach()` (monkey-patches
    `_on_connect`/`_on_disconnect`/`publish`) to record connection state,
    publish success/failure counts, and last-success timestamps. Exposes
    `is_healthy` and `status_dict()`.
  - `HeartbeatFile` — filesystem heartbeat for cron-style services with no
    long-running process. `touch()` after each successful publish; `is_fresh()`
    for the healthcheck side.
  - `make_fastapi_router(tracker)` — drop-in FastAPI `APIRouter` exposing
    `GET /health` (always 200, process liveness) and `GET /health/mqtt`
    (200 when `tracker.is_healthy`, 503 otherwise).
- New `healthcheck_cli` module providing `python -m ha_mqtt_publisher.healthcheck_cli`
  for use directly in Docker `HEALTHCHECK` directives by services using
  `HeartbeatFile`. Exits 0 if the heartbeat exists and is younger than
  `--max-age` seconds, 1 otherwise.
- New optional `[fastapi]` extra. Install with
  `pip install "ha-mqtt-publisher[fastapi]"` to use `make_fastapi_router`.
- 18 new tests in `tests/test_health.py`. Full suite: 287 passing.

### Why

Addresses a failure mode observed on 2026-04-07 where the EMQX broker
crash-looped for hours and three downstream services (`flights`,
`twickenham_events`, `hounslow_bin_collection`) all kept reporting "healthy"
because their Docker `HEALTHCHECK` probes only verified a local HTTP `/health`
endpoint, not whether MQTT was actually working. With the new primitives,
the health endpoint reflects real broker liveness.

## [0.3.6] — earlier

Version bump only.

## [0.3.5] — earlier

Initial public PyPI release with the v0.3.x feature set: device bundle
discovery, command processor, status sensor, availability publisher,
service runner.
