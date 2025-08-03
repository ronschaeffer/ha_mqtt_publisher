# examples/ha_discovery_complete_example.py

"""
Complete Home Assistant MQTT Discovery Example

This example demonstrates how to use the mqtt_publisher package with
the integrated Home Assistant discovery framework to create a robust
MQTT-based sensor system.
"""

from mqtt_publisher.config import Config
from mqtt_publisher.ha_discovery import (
    Device,
    StatusSensor,
    create_sensor,
    publish_discovery_configs,
)
from mqtt_publisher.publisher import MQTTPublisher


def main():
    """
    Example showing complete Home Assistant MQTT Discovery setup.
    """

    # Load configuration
    config = Config("config/config.yaml")

    # Create MQTT publisher with enhanced configuration
    mqtt_config = {
        "broker_url": config.get("mqtt.broker_url"),
        "broker_port": config.get("mqtt.broker_port", 1883),
        "client_id": config.get("mqtt.client_id", "ha_discovery_example"),
        "security": config.get("mqtt.security", "none"),
        "auth": config.get("mqtt.auth"),
        "tls": config.get("mqtt.tls"),
        "last_will": {
            "topic": f"{config.get('mqtt.base_topic', 'mqtt_publisher')}/status",
            "payload": "offline",
            "qos": 1,
            "retain": True,
        },
    }

    # Create device representation
    device = Device(config)

    # Method 1: Create entities manually
    entities = []

    # Add status sensor for system health monitoring
    if config.get("mqtt.topics.status"):
        entities.append(StatusSensor(config, device))

    # Add custom sensors using the convenience function
    entities.extend(
        [
            create_sensor(
                config=config,
                device=device,
                name="Temperature",
                unique_id="temperature",
                state_topic=config.get(
                    "mqtt.topics.temperature", "sensors/temperature"
                ),
                value_template="{{ value_json.temperature }}",
                unit_of_measurement="°C",
                device_class="temperature",
                icon="mdi:thermometer",
            ),
            create_sensor(
                config=config,
                device=device,
                name="Humidity",
                unique_id="humidity",
                state_topic=config.get("mqtt.topics.humidity", "sensors/humidity"),
                value_template="{{ value_json.humidity }}",
                unit_of_measurement="%",
                device_class="humidity",
                icon="mdi:water-percent",
            ),
            create_sensor(
                config=config,
                device=device,
                name="Data Count",
                unique_id="data_count",
                state_topic=config.get("mqtt.topics.data", "sensors/data"),
                value_template="{{ value_json.items | length }}",
                json_attributes_topic=config.get("mqtt.topics.data", "sensors/data"),
                json_attributes_template="{{ value_json | tojson }}",
                icon="mdi:counter",
            ),
        ]
    )

    # Publish data and discovery configs
    with MQTTPublisher(**mqtt_config) as publisher:
        # Publish discovery configurations
        publish_discovery_configs(config, publisher, entities, device)

        # Publish sample data
        sample_data = {
            "temperature": 23.5,
            "humidity": 65.2,
            "timestamp": "2025-08-04T12:00:00Z",
        }

        temp_topic = config.get("mqtt.topics.temperature", "sensors/temperature")
        humidity_topic = config.get("mqtt.topics.humidity", "sensors/humidity")
        data_topic = config.get("mqtt.topics.data", "sensors/data")
        status_topic = config.get(
            "mqtt.topics.status",
            f"{config.get('mqtt.base_topic', 'mqtt_publisher')}/status",
        )

        publisher.publish(temp_topic, sample_data, retain=True)

        publisher.publish(
            humidity_topic,
            {
                "humidity": sample_data["humidity"],
                "timestamp": sample_data["timestamp"],
            },
            retain=True,
        )

        publisher.publish(
            data_topic,
            {"items": [sample_data], "count": 1, "timestamp": sample_data["timestamp"]},
            retain=True,
        )

        # Publish status (system healthy)
        publisher.publish(
            status_topic,
            {
                "status": "ok",
                "timestamp": sample_data["timestamp"],
                "message": "System running normally",
            },
            retain=True,
        )

    print("✅ Published sample data and Home Assistant discovery configs")
    print("🏠 Check your Home Assistant for new sensors under the configured device")


if __name__ == "__main__":
    main()
