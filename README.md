# MQTT Publisher

This project is an MQTT publisher that connects to an MQTT broker and publishes messages to specified topics.

## Features

- Connect to an MQTT broker with optional security settings
- Publish messages to specified topics
- Retry logic for connection attempts
- Context manager support for easy resource management
- Last Will and Testament (LWT) support

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

### Basic Example

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
    "last_will_topic": "your_last_will_topic",
    "last_will_payload": "your_last_will_payload",
    "last_will_qos": 1,
    "last_will_retain": True
}

publisher = MQTTPublisher(**config)

if publisher.connect():
    publisher.publish("your_topic", {"message": "Hello, MQTT!"})
    publisher.disconnect()
```

### Using Context Manager

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
    "last_will_topic": "your_last_will_topic",
    "last_will_payload": "your_last_will_payload",
    "last_will_qos": 1,
    "last_will_retain": True
}

with MQTTPublisher(**config) as publisher:
    publisher.publish("your_topic", {"message": "Hello, MQTT!"})
```

## Running Tests

To run the tests, use the following command:

```sh
poetry run pytest
```

## License

This project is licensed under the GPL License.
