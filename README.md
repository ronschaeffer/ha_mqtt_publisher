# MQTT Publisher

A Python MQTT publishing library with integrated **Home Assistant MQTT Discovery** support. This package provides an MQTT publishing engine and a framework for creating Home Assistant auto-discovery configurations.

## ✨ Features

### 🚀 MQTT Publishing Engine

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

### MQTT Security Options

Choose the appropriate security configuration:

| Security Mode          | Port      | Description               | Use Case                 |
| ---------------------- | --------- | ------------------------- | ------------------------ |
| `none`                 | 1883      | No authentication         | Testing/development      |
| `username`             | 1883/8883 | Username/password only    | Basic authentication     |
| `tls`                  | 8883      | TLS encryption + auth     | Production (recommended) |
| `tls_with_client_cert` | 8884      | TLS + client certificates | High security            |

### Common MQTT Ports

- **1883**: Standard MQTT (unencrypted)
- **8883**: MQTT over TLS/SSL (encrypted)
- **8884**: MQTT over TLS/SSL with client certificates

#### Quick Setup

1. Copy the example: `cp .env.example .env`
2. Edit `.env` with your actual values
3. The configuration automatically uses environment variables with `${VARIABLE_NAME}` syntax

### Configuration File

Create `config/config.yaml` based on `config/config.yaml.example`:

```yaml
# MQTT Configuration with environment variable support
mqtt:
  broker_url: "${MQTT_BROKER_URL}"
  broker_port: 8883
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

## Usage

### Basic MQTT Publishing

```python
from mqtt_publisher.publisher import MQTTPublisher
```

## 🚀 Usage

### Basic MQTT Publishing

```python
from mqtt_publisher.publisher import MQTTPublisher

# Configuration
config = {
    "broker_url": "your-broker.example.com",
    "broker_port": 8883,
    "client_id": "your_client_id",
    "security": "username",
    "auth": {
        "username": "your_username",
        "password": "your_password"
    }
}

# Method 1: Manual connection management
publisher = MQTTPublisher(**config)
if publisher.connect():
    publisher.publish("your/topic", {"message": "Hello, MQTT!"})
    publisher.disconnect()

# Method 2: Context manager (recommended)
with MQTTPublisher(**config) as publisher:
    publisher.publish("your/topic", {"message": "Hello, MQTT!"}, retain=True)
```

### Using with Environment Variables

```python
from mqtt_publisher.config import Config
from mqtt_publisher.publisher import MQTTPublisher
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load configuration (automatically uses environment variables)
config = Config("config/config.yaml")

# Create MQTT publisher
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
    publisher.publish("sensors/temperature", {"value": 23.5, "unit": "°C"})
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

---

For questions, issues, or contributions, please open an issue on GitHub.

# Create device and sensors

device = Device(config)
sensors = [
create_sensor(
config=config,
device=device,
name="Temperature",
unique_id="temperature",
state_topic="sensors/temperature",
value_template="{{ value_json.temperature }}",
unit_of_measurement="°C",
device_class="temperature",
icon="mdi:thermometer"
)
]

# Publish discovery configurations and data

with MQTTPublisher(\*\*mqtt_config) as publisher:
publish_discovery_configs(config, publisher, sensors, device)
publisher.publish("sensors/temperature", {"temperature": 23.5})

````

### Custom Entity Configuration

```python
from ha_discovery import Device, StatusSensor, Sensor

# Create device
device = Device(config)

# Create status sensor for system health
status_sensor = StatusSensor(config, device)

# Create custom sensor with rich configuration
custom_sensor = Sensor(
    config=config,
    device=device,
    name="System Load",
    unique_id="system_load",
    state_topic="system/load",
    value_template="{{ value_json.load_1m }}",
    json_attributes_topic="system/load",
    json_attributes_template="{{ value_json | tojson }}",
    unit_of_measurement="%",
    icon="mdi:speedometer"
)

entities = [status_sensor, custom_sensor]
publish_discovery_configs(config, publisher, entities, device)
````

## Running Tests

To run the tests, use the following command:

```sh
poetry run pytest
```

## License

This project is licensed under the MIT License.
