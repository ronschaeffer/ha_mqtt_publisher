# MQTT Publisher

This project is a comprehensive MQTT publisher library with integrated **Home Assistant MQTT Discovery** support. It provides both a robust MQTT publishing engine and a sophisticated framework for creating Home Assistant auto-discovery configurations.

## Features

### MQTT Publishing
- Connect to an MQTT broker with optional security settings
- Publish messages to specified topics
- Retry logic for connection attempts
- Context manager support for easy resource management
- Last Will and Testament (LWT) support
- Professional logging with configurable levels

### Home Assistant Integration 🏠
- **Complete MQTT Discovery Framework**: Object-oriented system for creating HA entities
- **Device Grouping**: Automatically groups sensors under logical devices
- **Status Monitoring**: Built-in binary sensor for system health monitoring
- **Rich Entity Support**: Sensors with templates, units, device classes, and icons
- **Automatic Configuration Publishing**: Handles discovery topic generation and payload creation

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/mqtt_publisher.git
   cd mqtt_publisher
   ```

2. Install dependencies using Poetry:
   ```sh
   poetry install
   ```

## Configuration

Create a `config.yaml` file in the `config` directory based on the provided `config.yaml.example` file. Update the configuration with your MQTT broker details and authentication settings.

### Example `config.yaml`

```yaml
# MQTT Configuration
mqtt:
  broker_url: "your_broker_url"
  broker_port: 8883
  client_id: "your_client_id"
  security: "username"
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

config = {
    "broker_url": "your_broker_url",
    "broker_port": 8883,
    "client_id": "your_client_id",
    "security": "username",
    "auth": {
        "username": "your_username",
        "password": "your_password"
    },
    "tls": {
        "ca_cert": "path/to/ca_cert",
        "client_cert": "path/to/client_cert",
        "client_key": "path/to/client_key",
        "verify": True
    },
    "last_will": {
        "topic": "your_last_will_topic",
        "payload": "offline",
        "qos": 1,
        "retain": True
    }
}

publisher = MQTTPublisher(**config)

if publisher.connect():
    publisher.publish("your_topic", {"message": "Hello, MQTT!"})
    publisher.disconnect()
```

### Using Context Manager

```python
from mqtt_publisher.publisher import MQTTPublisher

with MQTTPublisher(**config) as publisher:
    publisher.publish("your_topic", {"message": "Hello, MQTT!"})
```

### Home Assistant MQTT Discovery 🏠

```python
from ha_discovery import Device, create_sensor, publish_discovery_configs
from mqtt_publisher.config import Config
from mqtt_publisher.publisher import MQTTPublisher

# Load configuration
config = Config("config/config.yaml")

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
with MQTTPublisher(**mqtt_config) as publisher:
    publish_discovery_configs(config, publisher, sensors, device)
    publisher.publish("sensors/temperature", {"temperature": 23.5})
```

### Advanced: Custom Entity Configuration

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
```

## Running Tests

To run the tests, use the following command:

```sh
poetry run pytest
```

## License

This project is licensed under the MIT License.
