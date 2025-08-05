# MQTT Publisher

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

An MQTT publishing library with **MQTT 5.0 support** and integrated **Home Assistant MQTT Discovery**. This package provides both a modern MQTT publishing engine and a framework for creating Home Assistant auto-discovery configurations.

## 🚀 Quick Start

```python
from mqtt_publisher import MQTTConfig, MQTTPublisher

# Enhanced configuration with automatic validation and type conversion
config = MQTTConfig.build_config(
    broker_url="mqtt.home.local",
    broker_port="8883",  # String automatically converted to int
    client_id="my_device",
    security="username",
    username="mqtt_user",
    password="mqtt_pass"
)

# Context manager ensures proper cleanup
with MQTTPublisher(config=config) as publisher:
    # Publish sensor data with automatic JSON serialization
    publisher.publish("sensors/temperature", {
        "value": 23.5,
        "unit": "°C"
    }, retain=True)
```

## ✨ Features

### 🚀 MQTT Publishing Engine

- **MQTT 5.0 Protocol Support** with properties, reason codes, and enhanced error handling
- **Enhanced Configuration Handling** with automatic type conversion and validation
- **Flexible Constructor** supporting both individual parameters and config dictionaries
- **Automatic Port Type Conversion** (strings automatically converted to integers)
- **Configuration Builder Pattern** with `MQTTConfig` utility class
- **Comprehensive Validation** with helpful error messages for common misconfigurations
- **Connection Management** with retry logic and exponential backoff
- **Multiple Security Modes**: None, Username/Password, TLS, TLS with client certificates
- **Context Manager Support** for automatic resource cleanup
- **Last Will and Testament (LWT)** support for offline detection
- **Configurable Logging** with multiple levels and detailed error reporting
- **Connection State Tracking** with timeout handling

### 🏠 Home Assistant Integration

- **MQTT Discovery Framework**: Object-oriented system for creating HA entities
- **Device Grouping**: Groups sensors under logical devices
- **Status Monitoring**: Binary sensor for system health monitoring
- **Entity Support**: Sensors with templates, units, device classes, and icons
- **Configuration Publishing**: Handles discovery topic generation and payload creation

## 📦 Installation

### Option 1: Git Dependency (Recommended)

Add to your `pyproject.toml`:

```toml
[tool.poetry.dependencies]
mqtt-publisher = {git = "https://github.com/ronschaeffer/mqtt_publisher.git"}
```

### Option 2: Local Development

```bash
git clone https://github.com/ronschaeffer/mqtt_publisher.git
cd mqtt_publisher
poetry install
```

## ⚙️ Configuration

### Environment Variables Setup

This project supports **optional hierarchical environment variable loading** for flexible configuration management. You can use any of these approaches:

**Option 1: Direct Configuration** - Edit `config/config.yaml` with your values
**Option 2: Environment Variables** - Use `.env` files or system environment
**Option 3: Hierarchical Loading** - Combine shared and project-specific settings

#### Option 1: Direct Configuration

Copy and edit the configuration file:

```bash
cp config/config.yaml.example config/config.yaml
# Edit config/config.yaml with your actual values
```

#### Option 2: Environment Variables

Set these environment variables (via `.env` file or system):

```bash
# Required MQTT settings
MQTT_BROKER_URL=your-broker.example.com
MQTT_BROKER_PORT=8883
MQTT_CLIENT_ID=your_unique_client_id
MQTT_USERNAME=your_mqtt_username
MQTT_PASSWORD=your_mqtt_password
```

#### Option 3: Hierarchical Environment Loading

For multi-project workspaces, you can use hierarchical loading:

1. **Shared environment** (optional): Create `../shared/.env` with common MQTT settings
2. **Project-specific overrides**: Create `.env` in project root for project-specific settings
3. **System environment**: System variables have highest priority

**Shared Environment Example** (`../shared/.env`):

```bash
# Shared MQTT configuration across all projects
MQTT_BROKER_URL=your-broker.example.com
MQTT_BROKER_PORT=8883
MQTT_USERNAME=your_mqtt_username
MQTT_PASSWORD=your_mqtt_password
```

**Project-Specific Environment** (`.env`):

```bash
# Project-specific client ID (overrides shared settings)
MQTT_CLIENT_ID=mqtt_publisher_client_001

# Project-specific overrides (if needed)
# MQTT_BROKER_URL=different-broker.example.com
DEBUG=false
LOG_LEVEL=INFO
```

### Configuration File

The configuration supports environment variable substitution using `${VARIABLE}` syntax:

```yaml
# MQTT Configuration with environment variable substitution
mqtt:
  broker_url: "${MQTT_BROKER_URL}" # your-broker.example.com
  broker_port: "${MQTT_BROKER_PORT}" # 8883, 1883, etc.
  client_id: "${MQTT_CLIENT_ID}" # unique client identifier
  security: "username" # none, username, tls, tls_with_client_cert

  auth:
    username: "${MQTT_USERNAME}" # MQTT username
    password: "${MQTT_PASSWORD}" # MQTT password
```

### 🔧 MQTT Security Options

Choose the appropriate security configuration:

| Security Mode          | Port      | Description               | Use Case                 |
| ---------------------- | --------- | ------------------------- | ------------------------ |
| `none`                 | 1883      | No authentication         | Testing/development      |
| `username`             | 1883/8883 | Username/password only    | Basic authentication     |
| `tls`                  | 8883      | TLS encryption + auth     | Production (recommended) |
| `tls_with_client_cert` | 8884      | TLS + client certificates | High security            |

### 🌐 Common MQTT Ports

- **1883**: Standard MQTT (unencrypted)
- **8883**: MQTT over TLS/SSL (encrypted)
- **8884**: MQTT over TLS/SSL with client certificates

#### ⚡ Quick Setup

1. Copy the example: `cp .env.example .env`
2. Edit `.env` with your actual values
3. The configuration automatically uses environment variables with `${VARIABLE_NAME}` syntax

### Configuration File

Create `config/config.yaml` based on `config/config.yaml.example`:

```yaml
# MQTT Configuration with environment variable support
mqtt:
  broker_url: "${MQTT_BROKER_URL}"
  broker_port: "${MQTT_BROKER_PORT}"
  client_id: "${MQTT_CLIENT_ID}"
  security: "username"  # Options: "none", "username", "tls", "tls_with_client_cert"

  # Authentication settings
  auth:
    username: "${MQTT_USERNAME}"
    password: "${MQTT_PASSWORD}"

  # TLS settings (for security: "tls" or "tls_with_client_cert")
  tls:
    ca_cert: null              # Path to CA certificate
    client_cert: null          # Path to client certificate
    client_key: null           # Path to client key
    verify: false              # Verify server certificate
  auth:
    username: "your_username"
    password: "your_password"
  tls:
    ca_cert: null
    client_cert: null
    client_key: null
    verify: false
  topics:
    next: "your_topic/next"
    all_upcoming: "your_topic/all_upcoming"
  last_will:
    topic: "your_last_will_topic"
    payload: "your_last_will_payload"
    qos: 1
    retain: true
```

## 🚀 Usage

### Basic MQTT Publishing

```python
from mqtt_publisher.publisher import MQTTPublisher

# Method 1: Individual parameters (with automatic type conversion)
publisher = MQTTPublisher(
    broker_url="your-broker.example.com",
    broker_port="8883",  # String ports automatically converted to int
    client_id="your_client_id",
    security="username",
    auth={
        "username": "your_username",
        "password": "your_password"
    }
)

# Method 2: Configuration dictionary (recommended)
config = {
    "broker_url": "your-broker.example.com",
    "broker_port": "8883",  # String automatically converted
    "client_id": "your_client_id",
    "security": "username",
    "auth": {
        "username": "your_username",
        "password": "your_password"
    }
}

# Context manager usage (recommended)
with MQTTPublisher(config=config) as publisher:
    publisher.publish("your/topic", {"message": "Hello, MQTT!"}, retain=True)
```

### Enhanced Configuration with MQTTConfig Builder

```python
from mqtt_publisher import MQTTConfig, MQTTPublisher

# Method 3: Builder pattern with automatic validation
config = MQTTConfig.build_config(
    broker_url="your-broker.example.com",
    broker_port="8883",  # Automatically converted to int
    client_id="your_client_id",
    security="username",
    username="your_username",
    password="your_password",
    max_retries="3"  # Also automatically converted
)

with MQTTPublisher(config=config) as publisher:
    publisher.publish("sensors/temperature", {"value": 23.5, "unit": "°C"})
```

### Using with YAML Configuration and Environment Variables

```python
from mqtt_publisher import MQTTConfig, MQTTPublisher
from mqtt_publisher.config import Config
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load YAML configuration (with environment variable substitution)
yaml_config = Config("config/config.yaml")

# Method 4: From nested configuration dictionary
config_dict = yaml_config.config  # Your YAML config as dict
mqtt_config = MQTTConfig.from_dict(config_dict)

with MQTTPublisher(config=mqtt_config) as publisher:
    publisher.publish("sensors/temperature", {"value": 23.5, "unit": "°C"})
```

### Error Handling and Validation

The library provides enhanced error handling with helpful messages:

```python
from mqtt_publisher import MQTTPublisher

try:
    # This will provide helpful error message
    publisher = MQTTPublisher(
        broker_url="mqtt.example.com",
        broker_port=8883,
        client_id="test",
        security="tls",
        # Missing TLS configuration - will show helpful error
    )
except ValueError as e:
    print(f"Configuration Error: {e}")
    # Output: "TLS configuration required when security='tls'"

try:
    # This will warn about port/TLS mismatch
    publisher = MQTTPublisher(
        broker_url="mqtt.example.com",
        broker_port=1883,  # Non-TLS port
        client_id="test",
        tls={"verify": True}  # TLS enabled
    )
except Exception as e:
    # Warning logged: "TLS enabled but using non-TLS port 1883. Consider port 8883 for TLS"
    pass
```

## 🎯 Enhanced Features

### Automatic Type Conversion

String values from environment variables or configuration files are automatically converted:

```python
# These are equivalent - strings automatically convert to integers
publisher1 = MQTTPublisher(broker_port="8883")    # String
publisher2 = MQTTPublisher(broker_port=8883)      # Integer
```

### Configuration Validation

Comprehensive validation with helpful error messages:

```python
# Missing required field
try:
    MQTTPublisher(broker_port=8883, client_id="test")  # Missing broker_url
except ValueError as e:
    print(e)  # "broker_url is required"

# Invalid port range
try:
    MQTTPublisher(broker_url="test", broker_port=99999)  # Invalid port
except ValueError as e:
    print(e)  # "broker_port must be integer 1-65535, got: 99999"

# Security/TLS mismatches (warnings, not errors)
publisher = MQTTPublisher(
    broker_url="test",
    broker_port=1883,  # Non-TLS port
    tls={"verify": True}  # TLS enabled
)
# Logs warning: "TLS enabled but using non-TLS port 1883. Consider port 8883 for TLS"
```

### Configuration Builder Pattern

Use `MQTTConfig` for complex configurations:

```python
from mqtt_publisher import MQTTConfig

# Build from individual parameters
config = MQTTConfig.build_config(
    broker_url="mqtt.example.com",
    broker_port="8883",
    client_id="my_client",
    security="tls",
    username="user",
    password="pass"
)

# Or from nested dictionary (like YAML config)
yaml_style_config = {
    "mqtt": {
        "broker_url": "mqtt.example.com",
        "broker_port": 8883,
        "auth": {"username": "user", "password": "pass"}
    }
}
config = MQTTConfig.from_dict(yaml_style_config)

# Both return validated config ready for MQTTPublisher
publisher = MQTTPublisher(config=config)
```

### 🏠 Home Assistant MQTT Discovery

```python
from mqtt_publisher.ha_discovery import (
    Device,
    StatusSensor,
    create_sensor,
    publish_discovery_configs
)
from mqtt_publisher.config import Config
from mqtt_publisher.publisher import MQTTPublisher

# Load configuration
config = Config("config/config.yaml")

# Create device representing your application
device = Device(
    name="My IoT Device",
    identifier="my_iot_device_001",
    manufacturer="Your Company",
    model="Sensor Hub v1.0"
)

# Create sensors
temp_sensor = create_sensor(
    device=device,
    name="Temperature",
    unique_id="temp_001",
    state_topic="sensors/temperature",
    value_template="{{ value_json.value }}",
    unit_of_measurement="°C",
    device_class="temperature"
)

status_sensor = StatusSensor(
    device=device,
    name="Device Status",
    unique_id="status_001"
)

# Publish discovery configurations to Home Assistant
entities = [temp_sensor, status_sensor]

mqtt_config = {
    "broker_url": config.get("mqtt.broker_url"),
    "broker_port": config.get("mqtt.broker_port"),
    "client_id": config.get("mqtt.client_id"),
    "security": config.get("mqtt.security"),
    "auth": {
        "username": config.get("mqtt.auth.username"),
        "password": config.get("mqtt.auth.password")
    }
}

with MQTTPublisher(**mqtt_config) as publisher:
    publish_discovery_configs(publisher, entities)

    # Publish sensor data
    publisher.publish("sensors/temperature", {"value": 23.5, "timestamp": "2024-01-01T12:00:00Z"})

    # Update status
    status_sensor.publish_online(publisher)
```

## 📖 Usage Example

See [`examples/ha_discovery_complete_example.py`](examples/ha_discovery_complete_example.py) for an example showing:

- Environment variable configuration
- Device and sensor creation
- Discovery configuration publishing
- Data publishing with error handling
- Status monitoring

## 🔧 Configuration Options

### Security Modes

| Mode                     | Description                        | Required Settings                |
| ------------------------ | ---------------------------------- | -------------------------------- |
| `"none"`                 | No authentication                  | None                             |
| `"username"`             | Username/password                  | `auth.username`, `auth.password` |
| `"tls"`                  | TLS encryption + username/password | `auth.*`, `tls.verify`           |
| `"tls_with_client_cert"` | TLS + client certificates          | `auth.*`, `tls.*`                |

### MQTT Publisher Parameters

```python
MQTTPublisher(
    broker_url: str,                    # MQTT broker hostname/IP
    broker_port: int,                   # MQTT broker port (1883, 8883, etc.)
    client_id: str,                     # Unique client identifier
    security: str = "none",             # Security mode (see table above)
    auth: dict | None = None,           # Authentication credentials
    tls: dict | None = None,            # TLS configuration
    max_retries: int = 3,              # Connection retry attempts
    last_will: dict | None = None       # Last Will and Testament message
)
```

### Home Assistant Discovery

The discovery framework automatically:

- ✅ Creates device entries in Home Assistant
- ✅ Groups related sensors under devices
- ✅ Handles discovery topic formatting
- ✅ Manages entity uniqueness
- ✅ Provides status monitoring capabilities

## 📚 Examples

### Complete Examples

See the `examples/` directory for comprehensive examples:

- **`enhanced_features_example.py`** - Demonstrates enhanced configuration features
- **`ha_discovery_complete_example.py`** - Full Home Assistant discovery setup
- **`config/config.yaml.example`** - Complete configuration template

### Real-World Usage Patterns

```python
# Pattern 1: Simple sensor publishing with validation
from mqtt_publisher import MQTTConfig, MQTTPublisher

config = MQTTConfig.build_config(
    broker_url="mqtt.home.local",
    broker_port="8883",  # String auto-converted
    client_id="temperature_sensor",
    security="username",
    username="mqtt_user",
    password="mqtt_pass"
)

with MQTTPublisher(config=config) as publisher:
    publisher.publish("sensors/living_room/temperature", {
        "value": 23.5,
        "unit": "°C",
        "timestamp": "2025-08-04T21:00:00Z"
    }, retain=True)

# Pattern 2: From YAML configuration
from mqtt_publisher.config import Config

yaml_config = Config("config/config.yaml")
mqtt_config = yaml_config.get("mqtt")  # Extract MQTT section

with MQTTPublisher(config=mqtt_config) as publisher:
    # Publish multiple sensors
    for sensor_name, value in sensors.items():
        topic = f"sensors/{sensor_name}"
        publisher.publish(topic, {"value": value}, retain=True)
```

## 🧪 Testing

Run the test suite:

```bash
poetry run pytest
```

Run with coverage:

```bash
poetry run pytest --cov=mqtt_publisher --cov-report=html
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For questions, issues, or contributions, please open an issue on GitHub.
