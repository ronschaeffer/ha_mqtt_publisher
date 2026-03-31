HA MQTT Publisher

[![PyPI](https://img.shields.io/pypi/v/ha-mqtt-publisher.svg)](https://pypi.org/project/ha-mqtt-publisher/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A Python MQTT publishing library with Home Assistant MQTT Discovery support.

## Features

- MQTT publish support using paho-mqtt 2.x (username/password, TLS, client_id, keepalive, Last Will)
- MQTT protocol selection (3.1, 3.1.1, 5.0)
- Default QoS and retain settings per configuration
- Configuration via YAML with environment variable substitution
- Home Assistant Discovery helpers: Device/Entity classes, Status sensor, DiscoveryManager
- Device bundle discovery (single-topic, multi-entity)
- One-time discovery publication with state tracking
- Command processing with ack/result topics and command registry
- Availability publishing (online/offline with LWT)
- Status payload tracking with error history
- JSON publish helpers with optional timestamp injection
- Service runner for periodic loops with graceful shutdown
- Validation of HA fields with optional extension lists
- Configurable logging levels for connection, publish, and discovery

## Installation

- Requires Python 3.10+
- pip: `pip install ha-mqtt-publisher`

## Configuration

Provide a YAML configuration and use environment variables for sensitive values. The library reads nested keys like `mqtt.*` and `home_assistant.*`.

Example `config.yaml`:

```yaml
mqtt:
	broker_url: "${MQTT_BROKER_URL}"
	broker_port: "${MQTT_BROKER_PORT}"
	client_id: "${MQTT_CLIENT_ID}"
	security: "${MQTT_SECURITY}"           # none | username | tls | tls_with_client_cert
	auth:
		username: "${MQTT_USERNAME}"
		password: "${MQTT_PASSWORD}"
	tls:
		verify: "${MQTT_TLS_VERIFY}"         # true | false
		ca_cert: "${MQTT_TLS_CA_CERT}"
		client_cert: "${MQTT_TLS_CLIENT_CERT}"
		client_key: "${MQTT_TLS_CLIENT_KEY}"
	max_retries: "${MQTT_MAX_RETRIES}"
	default_qos: "${MQTT_DEFAULT_QOS}"
	default_retain: "${MQTT_DEFAULT_RETAIN}"

home_assistant:
	discovery_prefix: "${HA_DISCOVERY_PREFIX}"      # default: homeassistant
	strict_validation: "${HA_STRICT_VALIDATION}"     # true | false (default true)
	discovery_state_file: "${HA_DISCOVERY_STATE_FILE}"
	extra_allowed: {}  # optional extension lists (entity categories, etc.)

	# Optional self-heal verification (one-time mode)
	ensure_discovery_on_startup: "${HA_ENSURE_DISCOVERY_ON_STARTUP}"  # true | false (default false)
	ensure_discovery_timeout: "${HA_ENSURE_DISCOVERY_TIMEOUT}"        # seconds (default 2.0)

		# Optional device-bundle behavior for modern HA
		bundle_only_mode: "${HA_BUNDLE_ONLY_MODE}"        # true | false (default false). When true:
			# - publish_discovery_configs emits only the device bundle config and skips per-entity
			# - ensure_discovery verifies the bundle topic only and can republish it if missing

app:
	# Optional metadata used for bundle origin info (o)
	name: "${APP_NAME}"
	sw_version: "${APP_SW_VERSION}"
	configuration_url: "${APP_CONFIGURATION_URL}"
```

**Notes:**

- Use `${VAR}` placeholders and set environment variables for your runtime.
- `mqtt.*` is used by the `MQTTPublisher`. `home_assistant.*` is used by discovery helpers.
- `app.*` is optional and only used to populate origin metadata in bundled device configs.

### Quick reference: configuration keys

Home Assistant (`home_assistant.*`)

| Key | Type | Default | Purpose |
|-----|------|---------|---------|
| discovery_prefix | string | homeassistant | Base discovery topic prefix |
| strict_validation | bool | true | Validate entity fields against known enums |
| discovery_state_file | string | — | JSON file path for one-time mode state |
| extra_allowed | dict | {} | Extend allowed values (entity categories, etc.) |
| ensure_discovery_on_startup | bool | false | Verify retained discovery topics and republish missing ones before publishing (one-time mode) |
| ensure_discovery_timeout | float | 2.0 | Wait time for retained discovery messages |
| bundle_only_mode | bool | false | For modern HA: verify/publish only the device bundle topic |

Application metadata (`app.*`) used in bundled device origin block (optional)

| Key | Type | Purpose |
|-----|------|---------|
| name | string | App name for origin (`o.name`) |
| sw_version | string | App/software version (`o.sw`) |
| configuration_url | string | URL to docs/config (`o.url`) |

## Usage

### Publish messages with `MQTTPublisher`

```python
from ha_mqtt_publisher.config import MQTTConfig
from ha_mqtt_publisher.publisher import MQTTPublisher

# Build a config dict (could also load from YAML and call MQTTConfig.from_dict)
mqtt_cfg = MQTTConfig.build_config(
		broker_url="${MQTT_BROKER_URL}",
		broker_port="${MQTT_BROKER_PORT}",
		client_id="${MQTT_CLIENT_ID}",
		security="${MQTT_SECURITY}",
		username="${MQTT_USERNAME}",
		password="${MQTT_PASSWORD}",
		tls={"verify": True} if "${MQTT_SECURITY}" in ("tls", "tls_with_client_cert") else None,
		default_qos=1,
		default_retain=True,
)

publisher = MQTTPublisher(config=mqtt_cfg)
publisher.connect()

publisher.publish(
		topic="demo/hello",
		payload="{\"msg\": \"hello\"}",
		qos=1,
		retain=True,
)

publisher.disconnect()
```

The publisher also supports context manager usage:

```python
with MQTTPublisher(broker_url="localhost", broker_port=1883) as pub:
    pub.publish("topic", "payload")
```

### JSON publish helpers

```python
from ha_mqtt_publisher.json_publish import publish_json, publish_many

# Publish a dict as JSON with optional automatic timestamp
publish_json(publisher, "sensors/reading", {"temperature": 22.5}, ensure_ts_field="ts")

# Batch publish multiple messages
publish_many(publisher, [
    ("sensors/temp", {"value": 22.5}, 1, True),
    ("sensors/humidity", {"value": 65}, 1, True),
])
```

### Home Assistant Discovery

Declare a device and entities, then publish discovery configs. Use one-time mode to avoid re-publishing.

```python
from ha_mqtt_publisher.config import Config
from ha_mqtt_publisher.publisher import MQTTPublisher
from ha_mqtt_publisher.ha_discovery import Device, Sensor
from ha_mqtt_publisher.ha_discovery import publish_discovery_configs, create_status_sensor

# Load full application config for discovery (reads mqtt.* and home_assistant.*)
app_config = Config("config.yaml")

# MQTT client using the same YAML (mqtt.* section)
publisher = MQTTPublisher(config={
		"broker_url": app_config.get("mqtt.broker_url"),
		"broker_port": app_config.get("mqtt.broker_port", 1883),
		"client_id": app_config.get("mqtt.client_id", "ha-mqtt-pub"),
		"security": app_config.get("mqtt.security", "none"),
		"auth": app_config.get("mqtt.auth"),
		"tls": app_config.get("mqtt.tls"),
		"default_qos": app_config.get("mqtt.default_qos", 1),
		"default_retain": app_config.get("mqtt.default_retain", True),
})
publisher.connect()

device = Device(app_config)
temp = Sensor(
		config=app_config,
		device=device,
		name="Room Temperature",
		unique_id="room_temp_1",
		state_topic="home/room/temperature",
		unit_of_measurement="°C",
)

status = create_status_sensor(app_config, device)

publish_discovery_configs(
		config=app_config,
		publisher=publisher,
		entities=[temp, status],
		device=device,
		one_time_mode=True,
)

# After discovery, publish state values
publisher.publish("home/room/temperature", "23.4", qos=1, retain=True)
```

### Discovery modes: entity-centric and device-centric

- Entity-centric (default): Publish per-entity config to `<prefix>/<component>/.../config`. Each payload includes a device block for grouping.
- Device-centric (optional): Publish one device config to `<prefix>/device/<device_id>/config`, then publish entities as needed.
	- Optionally, publish a single bundled message that includes all entities. You can also request the bundle be emitted before per-entity topics via `emit_device_bundle=True` in `publish_discovery_configs`.

#### Which mode should I use?

- Use entity-centric when you need maximum backward compatibility with all HA versions or want explicit per-entity config topics.
- Use device bundle when your HA supports the bundled device config for faster provisioning, single-topic idempotency, and cleaner device metadata. You can still publish per-entity topics alongside the bundle by default.

**Key differences:**

- Topic shape: entity-centric uses component topics per entity; bundle uses one device topic plus runtime state topics.
- Device block: per-entity configs repeat device metadata; bundle has a single `dev` block.
- Keys inside bundle: entities are keyed by `unique_id`; entity-centric uses `object_id` in topic paths.
- Transport defaults: bundle may include `qos`/`retain` as top-level hints; per-entity uses transport options only.

Device-centric publish example

```python
from ha_mqtt_publisher.ha_discovery import Device, publish_device_config

device = Device(app_config)

# Choose topic device_id explicitly, or omit to use the first identifier
ok = publish_device_config(
	config=app_config,
	publisher=publisher,
	device=device,
	device_id="living_room_bridge",
)
```

Bundled device-centric publish (single message)

```python
from ha_mqtt_publisher.ha_discovery import Device, Sensor, publish_device_bundle

device = Device(app_config)
temp = Sensor(app_config, device, name="Temperature", unique_id="temp", state_topic="room/t")
humid = Sensor(app_config, device, name="Humidity", unique_id="humid", state_topic="room/h")

# Publishes one config message containing device (dev) and components (cmps)
publish_device_bundle(
	config=app_config,
	publisher=publisher,
	device=device,
	entities=[temp, humid],
)
```

### Availability publishing

```python
from ha_mqtt_publisher.availability import AvailabilityPublisher

avail = AvailabilityPublisher(publisher, "myapp/availability")
avail.online()   # publishes "online" (retained)
# ... do work ...
avail.offline()  # publishes "offline" (retained)
```

Combine with Last Will for automatic offline on disconnect:

```python
publisher = MQTTPublisher(
    broker_url="localhost",
    last_will={"topic": "myapp/availability", "payload": "offline", "qos": 1, "retain": True},
)
```

### Command processing

```python
from ha_mqtt_publisher.commands import CommandProcessor

cp = CommandProcessor(
    client=publisher,
    ack_topic="myapp/cmd/ack",
    result_topic="myapp/cmd/result",
)

def handle_refresh(args):
    # do work...
    return ("ok", "refreshed 42 items", {"count": 42})

cp.register("refresh", handle_refresh, description="Refresh data")

# Process incoming command (from MQTT subscription callback)
cp.handle_raw('{"command": "refresh", "args": {}}')

# Publish command registry for HA button discovery
cp.publish_registry("myapp/cmd/registry")
```

### Status tracking

```python
from ha_mqtt_publisher.status import StatusPayload
from ha_mqtt_publisher.json_publish import publish_json

status = StatusPayload(status="ok", event_count=0)
status.mark_run()
status.add_error("api_error", "Upstream API returned 503")
status.cap_errors(max_items=20)

publish_json(publisher, "myapp/status", status.as_dict(), retain=True)
```

### Topic conventions

```python
from ha_mqtt_publisher.topic_map import TopicMap

topics = TopicMap(base="myapp")
topics.status        # "myapp/status"
topics.availability  # "myapp/availability"
topics.commands      # "myapp/cmd"
topics.cmd("refresh") # "myapp/cmd/refresh"
```

### Service runner

```python
from ha_mqtt_publisher.service_runner import run_service_loop

async def on_tick():
    # publish sensor data, check commands, etc.
    pass

run_service_loop(interval_s=60, on_tick=on_tick, availability=avail)
```

### One-time publication

- Enabled by passing `one_time_mode=True` to `publish_discovery_configs`.
- Tracks published topics in `home_assistant.discovery_state_file`.

### Discovery verification (optional self-heal)

If you want the library to verify retained discovery topics exist on the broker and republish any that are missing, enable the verification pass when using one-time mode.

- Config flags:
  - `home_assistant.ensure_discovery_on_startup`: `true`|`false` (default `false`)
  - `home_assistant.ensure_discovery_timeout`: float seconds (default `2.0`)
  - `home_assistant.bundle_only_mode`: `true`|`false` (default `false`). When true, verification checks only the device bundle topic and republishes it if missing.

```python
from ha_mqtt_publisher.ha_discovery import ensure_discovery

ensure_discovery(
	config=app_config,
	publisher=publisher,
	entities=[temp, status],
	device=device,
	timeout=app_config.get("home_assistant.ensure_discovery_timeout", 2.0),
	one_time_mode=True,
)
```

Bundle-only mode

If your HA supports device bundles and you don't want per-entity discovery topics, set:

```yaml
home_assistant:
	bundle_only_mode: true
```

Then a normal call to `publish_discovery_configs` with entities will publish only the bundle and skip per-entity configs.

## Supported Home Assistant components

### About "Device" (registry grouping)

- `Device` is metadata included in each entity's discovery payload; it is not a standalone component or topic.
- Home Assistant uses it to group entities in the Device Registry and display manufacturer/model, versions, and links.
- Create one `Device` per physical/logical device and pass it to all related entities; removal happens when all related entities are removed.

### Components

| Type            | Component key       | Notes |
|-----------------|---------------------|-------|
| Sensor          | sensor              | `state_topic` required |
| Binary Sensor   | binary_sensor       | `state_topic` required; `device_class` supported |
| Switch          | switch              | `command`/`state` topics supported |
| Light           | light               | `payload_on`/`off` defaults; `command`/`state` |
| Cover           | cover               | `payload_open`/`close`/`stop` defaults |
| Climate         | climate             | topic fields per HA spec |
| Fan             | fan                 | `payload_on`/`off` defaults |
| Lock            | lock                | `payload_lock`/`unlock` defaults |
| Number          | number              | numeric set/get |
| Select          | select              | options via extra attributes |
| Text            | text                | text set/get |
| Button          | button              | stateless trigger |
| Device Tracker  | device_tracker      | presence/location topics |
| Alarm Control   | alarm_control_panel | arm/disarm topics as applicable |
| Camera          | camera              | image/stream topics as applicable |
| Status Sensor   | sensor (helper)     | convenience entity for app status |

**Notes:**

- Validation covers `entity_category`, `availability_mode`, sensor `state_class`, and `device_class`.
- Additional allowed values can be provided via `home_assistant.extra_allowed`.

## Testing

```bash
make test           # run 269 unit tests
make ci-check       # lint + test
```

## Development

```bash
poetry install      # install dependencies
make fix            # lint + format
make install-hooks  # install pre-commit hooks
```

## Troubleshooting

- Connection refused with TLS/non-TLS port mismatch: ensure TLS settings align with `broker_port` (1883 non-TLS, 8883 TLS).
- Discovery not appearing: verify `discovery_prefix` and that MQTT messages are retained on config topics.

## License

MIT

## Contributing

Issues and pull requests are welcome in the GitHub repository.

## Support

Open a GitHub issue for questions and problems.
