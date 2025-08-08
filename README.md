# MQTT Publisher

[![PyPI version](https://badge.fury.io/py/ronschaeffer-mqtt-publisher.svg)](https://badge.fury.io/py/ronschaeffer-mqtt-publisher)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![CI](https://github.com/ronschaeffer/mqtt_publisher/workflows/CI/badge.svg)](https://github.com/ronschaeffer/mqtt_publisher/actions)

MQTT publishing library with MQTT 5.0 support and Home Assistant MQTT Discovery integration.

## Features

### MQTT Publishing

- MQTT 5.0, 3.1.1, and 3.1 protocol support with backwards compatibility for paho-mqtt versions
- Default QoS and retain flag configuration for publish operations
- Exponential backoff retry logic with configurable maximum attempts
- Non-blocking loop management with proper cleanup
- Connection state tracking with timeout handling

### Configuration Management

- Automatic type conversion for string values from environment variables
- Configuration validation with specific error messages
- Multiple security modes: none, username/password, TLS, TLS with client certificates
- Environment variable support with `${VARIABLE_NAME}` syntax
- YAML configuration file support

### Enhanced Logging

- Topic-specific logging levels with pattern matching
- Module-specific loggers for connection, publishing, and discovery operations
- Structured logging with configurable levels
- Connection error messages with configuration guidance

### Home Assistant Integration

- MQTT Discovery framework for automatic entity creation
- Device and entity management with lifecycle support
- 18+ Home Assistant entity types supported
- Status sensor publishing for application health monitoring
- One-time discovery publishing to prevent configuration flooding

### Connection Management

- Last Will and Testament (LWT) support for offline detection
- SSL/TLS encryption with certificate verification
- Multiple authentication methods
- Automatic reconnection with connection state callbacks

## Installation

### Using pip

```bash
pip install ronschaeffer-mqtt-publisher
```

### Using Poetry

```bash
poetry add ronschaeffer-mqtt-publisher
```

### Development Installation

```bash
git clone https://github.com/ronschaeffer/mqtt_publisher.git
cd mqtt_publisher
poetry install
```

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# MQTT Broker Configuration
MQTT_BROKER_URL=localhost
MQTT_BROKER_PORT=1883
MQTT_CLIENT_ID=my_mqtt_client

# Authentication (for username security mode)
MQTT_USERNAME=your_username
MQTT_PASSWORD=your_password

# Home Assistant Discovery (optional)
HA_DISCOVERY_PREFIX=homeassistant
```

### Configuration File

Create `config/config.yaml`:

```yaml
mqtt:
  broker_url: "${MQTT_BROKER_URL}"
  broker_port: "${MQTT_BROKER_PORT}"
  client_id: "${MQTT_CLIENT_ID}"
  security: "username" # Options: none, username, tls, tls_with_client_cert

  # Default publishing settings
  default_qos: 1
  default_retain: false

  # Connection settings
  max_retries: 3
  protocol: "MQTTv311" # Options: MQTTv31, MQTTv311, MQTTv5

  # Authentication
  auth:
    username: "${MQTT_USERNAME}"
    password: "${MQTT_PASSWORD}"

  # TLS Configuration (for tls security modes)
  tls:
    ca_cert: null
    client_cert: null
    client_key: null
    verify: false

  # Last Will and Testament
  last_will:
    topic: "status/${MQTT_CLIENT_ID}"
    payload: "offline"
    qos: 1
    retain: true

  # Enhanced Logging Configuration
  logging_config:
    connection_level: "INFO"
    publish_level: "DEBUG"
    discovery_level: "WARNING"
    topic_specific:
      "sensors/*": "DEBUG"
      "status": "INFO"

# Home Assistant Discovery (optional)
ha_discovery:
  discovery_prefix: "${HA_DISCOVERY_PREFIX}"
  device:
    name: "My MQTT Device"
    identifier: "mqtt_device_001"
    manufacturer: "Custom"
    model: "MQTT Publisher"
    sw_version: "1.0.0"
```

### Security Modes

| Mode                   | Description                           | Required Settings                |
| ---------------------- | ------------------------------------- | -------------------------------- |
| `none`                 | No authentication                     | None                             |
| `username`             | Username/password authentication      | `auth.username`, `auth.password` |
| `tls`                  | TLS encryption with username/password | `auth.*`, `tls.verify`           |
| `tls_with_client_cert` | TLS with client certificates          | `auth.*`, `tls.*`                |

## Usage

### Basic Publishing

```python
from mqtt_publisher import MQTTPublisher

# Direct parameter initialization
publisher = MQTTPublisher(
    broker_url="localhost",
    broker_port=1883,
    client_id="my_client",
    security="none"
)

# Connect and publish
if publisher.connect():
    # Basic message publishing
    publisher.publish("sensors/temperature", "23.5")

    # JSON data publishing with retain flag
    publisher.publish("sensors/humidity", {"value": 65.2, "unit": "%"}, retain=True)

    # Custom QoS level
    publisher.publish("alerts/motion", "detected", qos=2)

    publisher.disconnect()
```

### Configuration-Based Setup

```python
from mqtt_publisher import MQTTConfig, MQTTPublisher

# Load from YAML configuration
config = MQTTConfig.from_yaml_file("config/config.yaml")

# Context manager ensures proper cleanup
with MQTTPublisher(config=config) as publisher:
    # Publisher automatically connects and disconnects
    publisher.publish("sensors/temperature", {"value": 23.5, "unit": "°C"})
```

### Home Assistant Discovery

```python
from mqtt_publisher.ha_discovery import HADiscoveryPublisher, Device, Entity

# Initialize discovery publisher
discovery = HADiscoveryPublisher(
    publisher=publisher,
    discovery_prefix="homeassistant"
)

# Create device
device = Device(
    name="Weather Station",
    identifier="weather_001",
    manufacturer="Custom",
    model="ESP32"
)

# Create sensor entity
temperature_sensor = Entity(
    entity_type="sensor",
    object_id="temperature",
    name="Temperature",
    device_class="temperature",
    unit_of_measurement="°C",
    state_topic="weather/temperature"
)

# Publish discovery configuration
discovery.publish_entity_config(device, temperature_sensor)

# Publish sensor data
publisher.publish("weather/temperature", "23.5")
```

### Error Handling

```python
from mqtt_publisher import MQTTPublisher

try:
    publisher = MQTTPublisher(
        broker_url="localhost",
        broker_port="invalid_port"  # Will be validated
    )
except ValueError as e:
    print(f"Configuration error: {e}")
    # Output: broker_port must be integer 1-65535, got: invalid_port

try:
    publisher = MQTTPublisher(
        broker_url="",  # Invalid empty URL
        broker_port=1883,
        client_id="test"
    )
except ValueError as e:
    print(f"Configuration error: {e}")
    # Output: broker_url is required
```

## Testing

### Run All Tests

```bash
poetry run pytest
```

### Run with Coverage

```bash
poetry run pytest --cov=mqtt_publisher --cov-report=html
```

### Run Specific Test Module

```bash
poetry run pytest tests/test_mqtt_publisher_enhanced.py -v
```

### Test Configuration

```bash
# Test environment variables
export MQTT_BROKER_URL=test.mosquitto.org
export MQTT_BROKER_PORT=1883
export MQTT_CLIENT_ID=test_client

poetry run pytest tests/test_environment_handling.py
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/ronschaeffer/mqtt_publisher.git
cd mqtt_publisher
poetry install --with dev
```

### Code Quality Checks

```bash
# Linting and formatting
poetry run ruff check .
poetry run ruff format .

# Spell checking
poetry run codespell
```

### Version Management

```bash
# Update version and create release
./release.sh patch  # or minor, major
```

## Troubleshooting

### Common Connection Issues

**Connection Refused - Bad Username/Password**

```
Error: Connection refused - bad username or password
```

- Verify `MQTT_USERNAME` and `MQTT_PASSWORD` environment variables
- Check broker authentication settings
- Ensure security mode is set to "username"

**TLS Port Mismatch Warnings**

```
Warning: TLS enabled but using non-TLS port 1883. Consider port 8883 for TLS
```

- Use port 8883 for TLS connections
- Use port 1883 for non-TLS connections
- Update `MQTT_BROKER_PORT` environment variable

**Connection Timeout**

```
Warning: Connection timeout after 5 seconds
```

- Verify broker URL and port accessibility
- Check network connectivity
- Increase `max_retries` in configuration

### Configuration Validation

The library validates configuration and provides specific error messages:

```python
# Missing required fields
ValueError: broker_url is required

# Invalid port range
ValueError: broker_port must be integer 1-65535, got: 99999

# Security/authentication mismatch
ValueError: username and password required when security='username'
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes with tests
4. Run quality checks: `poetry run ruff check . && poetry run pytest`
5. Submit a pull request

See [GitHub Issues](https://github.com/ronschaeffer/mqtt_publisher/issues) for bug reports and feature requests.

## Support

- **Issues**: [GitHub Issues](https://github.com/ronschaeffer/mqtt_publisher/issues)
- **Documentation**: [Examples Directory](examples/)
- **Source Code**: [GitHub Repository](https://github.com/ronschaeffer/mqtt_publisher)
