# MQTT Publisher Examples

Usage examples for the `ha-mqtt-publisher` library.

## Prerequisites

```bash
poetry install
cp config/config.yaml.example config/config.yaml
cp .env.example .env
# Edit .env with your MQTT broker settings
```

## Examples

### Device Bundle Discovery (`device_bundle_discovery.py`)

The recommended approach for Home Assistant integration. Demonstrates:

- Device and entity creation using `Device` and `Entity` classes
- Publishing a device bundle to HA MQTT discovery
- Availability (LWT) publishing

```bash
poetry run python examples/device_bundle_discovery.py
```

### Message Handler (`message_handler_example.py`)

Demonstrates inbound MQTT message handling:

- Subscribing to command topics
- Processing incoming messages
- Publishing acknowledgments

```bash
poetry run python examples/message_handler_example.py
```

### Twickenham Migration (`twickenham_migration_example.py`)

Real-world migration example showing how `twickenham_events` uses the library.

```bash
poetry run python examples/twickenham_migration_example.py
```

## Configuration

See `config/` for YAML configuration templates:

- `config.yaml.example` — basic MQTT configuration
- `config_ha_discovery.yaml.example` — extended config with HA discovery context
