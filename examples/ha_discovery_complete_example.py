#!/usr/bin/env python3
"""
Complete Home Assistant MQTT Discovery Example

This example demonstrates how to use the mqtt_publisher package with
the integrated Home Assistant discovery framework to create a robust
MQTT-based sensor system.

Prerequisites:
1. Create config/config.yaml based on config/config.yaml.example
2. Set up environment variables in .env file
3. Install dependencies: poetry install

Usage:
    python examples/ha_discovery_complete_example.py
"""

from datetime import datetime
import json
from pathlib import Path
import time

from mqtt_publisher.config import Config
from mqtt_publisher.ha_discovery import (
    Device,
    StatusSensor,
    create_sensor,
    publish_discovery_configs,
)
from mqtt_publisher.publisher import MQTTPublisher


def load_environment():
    """Load environment variables from .env file using hierarchical loading."""
    try:
        from dotenv import load_dotenv

        # Load shared environment first (if exists)
        parent_env = Path(__file__).parent.parent.parent / ".env"
        if parent_env.exists():
            load_dotenv(parent_env, verbose=False)
            print(f"✅ Loaded shared environment from: {parent_env}")

        # Load project-specific environment second
        project_env = Path(__file__).parent.parent / ".env"
        if project_env.exists():
            load_dotenv(project_env, override=True, verbose=False)
            print(f"✅ Loaded project environment from: {project_env}")

    except ImportError:
        print("⚠️  python-dotenv not installed. Install with: poetry add python-dotenv")


def main():
    """
    Example showing complete Home Assistant MQTT Discovery setup.
    """
    print("🚀 Starting Home Assistant MQTT Discovery Example")

    # Load environment variables
    load_environment()

    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        print(
            "   Copy config/config.yaml.example to config/config.yaml and update settings"
        )
        return

    config = Config(str(config_path))

    # Create device representing your application
    device_config = Device(
        identifiers=["weather_station_01"],
        name="Weather Station",
        model="WS-1000",
        manufacturer="Example Corp",
        sw_version="0.2.0-c3c3476-dirty",
        configuration_url="http://weather-station.local/config",
    )
    device = device_config  # For backward compatibility with examples below
    print(f"📱 Created device: {device.name}")

    # Create various sensors to demonstrate capabilities

    # 1. Temperature sensor with value template
    temp_sensor = create_sensor(
        device=device,
        name="Temperature",
        unique_id="temp_example_001",
        state_topic="mqtt_publisher/sensors/temperature",
        value_template="{{ value_json.value }}",
        unit_of_measurement="°C",
        device_class="temperature",
        icon="mdi:thermometer",
    )

    # 2. Humidity sensor
    humidity_sensor = create_sensor(
        device=device,
        name="Humidity",
        unique_id="humidity_example_001",
        state_topic="mqtt_publisher/sensors/humidity",
        value_template="{{ value_json.value }}",
        unit_of_measurement="%",
        device_class="humidity",
        icon="mdi:water-percent",
    )

    # 3. Status sensor for system health monitoring
    status_sensor = StatusSensor(
        device=device, name="System Status", unique_id="status_example_001"
    )

    # 4. Counter sensor to demonstrate numerical data
    counter_sensor = create_sensor(
        device=device,
        name="Message Count",
        unique_id="counter_example_001",
        state_topic="mqtt_publisher/sensors/counter",
        value_template="{{ value_json.count }}",
        icon="mdi:counter",
    )

    # Prepare MQTT configuration
    mqtt_config = {
        "broker_url": config.get("mqtt.broker_url"),
        "broker_port": config.get("mqtt.broker_port", 8883),
        "client_id": config.get("mqtt.client_id", "mqtt_publisher_example"),
        "security": config.get("mqtt.security", "username"),
        "auth": {
            "username": config.get("mqtt.auth.username"),
            "password": config.get("mqtt.auth.password"),
        },
        "last_will": {
            "topic": "mqtt_publisher/status",
            "payload": "offline",
            "qos": 1,
            "retain": True,
        },
        "max_retries": 3,
    }

    print(
        f"🔗 Connecting to MQTT broker: {mqtt_config['broker_url']}:{mqtt_config['broker_port']}"
    )

    try:
        # Connect to MQTT and publish discovery configurations
        with MQTTPublisher(**mqtt_config) as publisher:
            print("✅ Connected to MQTT broker")

            # Publish Home Assistant discovery configurations
            entities = [temp_sensor, humidity_sensor, status_sensor, counter_sensor]
            publish_discovery_configs(publisher, entities)
            print(f"📡 Published discovery configurations for {len(entities)} entities")

            # Publish online status
            status_sensor.publish_online(publisher)
            print("🟢 Published online status")

            # Simulate publishing sensor data over time
            counter = 0
            for i in range(5):
                counter += 1
                timestamp = datetime.now().isoformat()

                # Temperature data (simulate varying temperature)
                temp_data = {
                    "value": 20.0 + (i * 2.5),
                    "timestamp": timestamp,
                    "unit": "°C",
                }
                publisher.publish(
                    "mqtt_publisher/sensors/temperature",
                    json.dumps(temp_data),
                    retain=True,
                )

                # Humidity data (simulate varying humidity)
                humidity_data = {
                    "value": 45 + (i * 5),
                    "timestamp": timestamp,
                    "unit": "%",
                }
                publisher.publish(
                    "mqtt_publisher/sensors/humidity",
                    json.dumps(humidity_data),
                    retain=True,
                )

                # Counter data
                counter_data = {"count": counter, "timestamp": timestamp}
                publisher.publish(
                    "mqtt_publisher/sensors/counter",
                    json.dumps(counter_data),
                    retain=True,
                )

                print(
                    f"📊 Published sensor data (iteration {i + 1}/5) - Temp: {temp_data['value']}°C, Humidity: {humidity_data['value']}%"
                )

                if i < 4:  # Don't sleep after the last iteration
                    time.sleep(2)  # Wait 2 seconds between updates

            print("🎉 Example completed successfully!")
            print("\n📋 Check Home Assistant for:")
            print("   - Device: 'MQTT Publisher Example'")
            print("   - Sensors: Temperature, Humidity, System Status, Message Count")
            print(
                "   - All sensors should show current values and be grouped under the device"
            )

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check MQTT broker is running and accessible")
        print("   2. Verify credentials in config/config.yaml")
        print("   3. Ensure environment variables are set correctly")
        print("   4. Check network connectivity to MQTT broker")
        return


if __name__ == "__main__":
    main()
