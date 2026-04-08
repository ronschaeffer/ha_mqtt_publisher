# CLAUDE.md — ha_mqtt_publisher

## What this is

Python library for publishing sensor data to MQTT with Home Assistant auto-discovery.
Published to PyPI as `ha-mqtt-publisher`. Used by `twickenham_events`.

## Type: Library

- PyPI: `ha-mqtt-publisher`
- Current version: see `pyproject.toml`

## Toolchain

Python 3.10+, Poetry, ruff, pytest, pre-commit

## Key commands

```bash
poetry install      # install deps
make fix            # lint + format
make test           # run tests
make ci-check       # lint + test
make install-hooks  # install pre-commit hooks
```

## Structure

```
src/ha_mqtt_publisher/   main package
tests/                   pytest tests
docs/                    documentation
examples/                usage examples
config/                  example config files
```

## Health module (since v0.4.0)

`src/ha_mqtt_publisher/health.py` provides three primitives that downstream
services consume to expose real MQTT-broker liveness to Docker HEALTHCHECK
and other monitoring: `HealthTracker`, `HeartbeatFile`, `make_fastapi_router`.
Plus `healthcheck_cli.py` for cron-style consumers.

`HealthTracker` has TWO callsite patterns. Any change to the API needs to
preserve both:

1. **`attach()` pattern** (used by `flights`) — monkey-patches the
   publisher's `_on_connect`, `_on_disconnect`, and `publish` methods so
   the tracker is updated automatically. Only works with the wrapped
   `MQTTPublisher` class.

2. **Manual-population pattern** (used by `twickenham_events`) — caller
   writes directly to `tracker.state.connected`,
   `tracker.state.last_publish_success_at`, etc. from their own paho
   callbacks. Used when the long-lived MQTT client is raw `paho.mqtt.Client`
   (not the wrapped `MQTTPublisher`), or when the publisher is short-lived
   inside a `with` block.

Both patterns need to keep working. If you ever need to refactor `attach()`,
keep `tracker.state.*` as a public API so the manual pattern survives.

`HeartbeatFile` is the third pattern, used by `hounslow_bin_collection`
(cron-driven, no long-running process). The job touches the file after
every successful publish; the healthcheck CLI verifies it's recent enough.

## Publishing to PyPI

Via GitHub Actions on version tag push. See `.github/workflows/release.yml`.

## Testing

Integration harness: `mqtt_test_harness` package (sibling repo).
Subscribe with `MQTTHarness`, publish via `MQTTPublisher`, assert with `collect()`.

```python
from mqtt_test_harness import MQTTHarness

async with MQTTHarness() as h:
    # publish via ha_mqtt_publisher, then:
    msgs = await h.collect("topic", count=1, timeout=5.0)
```

## Coding conventions

- Line length: 88, quote style: double
- ruff isort with `force-sort-within-sections`
- Type hints on all public API
