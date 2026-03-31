# CLAUDE.md — ha_mqtt_publisher

## What this is

Python library for publishing sensor data to MQTT with Home Assistant auto-discovery.
Published to PyPI as `ha-mqtt-publisher`. Used by `twickenham_events`.

## Type: Library

- PyPI: `ha-mqtt-publisher`
- Current version: see `pyproject.toml`

## Toolchain

Python 3.11+, Poetry, ruff, pytest, pre-commit

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

## Publishing to PyPI

Via GitHub Actions on version tag push. See `.github/workflows/release.yml`.

## Testing

Integration harness: `/root/dev/python/mqtt_test_harness` (`mqtt_test_harness` package).
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
