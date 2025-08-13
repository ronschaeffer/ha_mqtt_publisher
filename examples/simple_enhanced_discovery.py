#!/usr/bin/env python3

"""
Simple Home Assistant MQTT Discovery Example

This example demonstrates the enhanced capabilities of the mqtt_publisher library:
- Complete device information with all Home Assistant fields
- Multiple entity types (sensors, switches, lights, etc.)
- Flexible entity creation with proper topics and configuration

Run this after configuring your MQTT broker settings in config/config.yaml
"""

import json
import time

from ha_mqtt_publisher import MQTTConfig, MQTTPublisher
from ha_mqtt_publisher.config import Config
from ha_mqtt_publisher.ha_discovery import (
    BinarySensor,
    Device,
    Light,
    Sensor,
    Switch,
    publish_discovery_configs,
)


def main():
    """Demonstrate the enhanced Home Assistant discovery capabilities."""

    # Load configuration
    config = Config("config/config.yaml")  # Use basic config file

    # Create enhanced device with more fields
    device = Device(
        config,
        name="Smart Room Controller",
        manufacturer="Example Corp",
        model="Room-1000",
        sw_version="0.3.2-b496354-dirty",  # Now supported!
        configuration_url="http://192.168.1.50:8080",  # Now supported!
    )

    print("Created device with enhanced info:")
    print(f"  Name: {device.name}")
    print(f"  Manufacturer: {device.manufacturer}")
    print(f"  Model: {device.model}")
    print(f"  Software Version: {device.sw_version}")
    print(f"  Configuration URL: {device.configuration_url}")

    # Create MQTT publisher from YAML config
    mqtt_config = MQTTConfig.from_dict({"mqtt": config.get("mqtt")})
    publisher = MQTTPublisher(config=mqtt_config)

    try:
        publisher.connect()
        print("\\nConnected to MQTT broker")

        # Create different entity types - all now supported!
        base_topic = config.get("mqtt.base_topic", "smart_room")

        entities = [
            # Temperature sensor with device class and state class
            Sensor(
                config,
                device,
                name="Room Temperature",
                unique_id="temp_room",
                state_topic=f"{base_topic}/temperature",
                device_class="temperature",
                unit_of_measurement="°C",
                state_class="measurement",  # Now supported!
                icon="mdi:thermometer",
            ),
            # Motion sensor
            BinarySensor(
                config,
                device,
                name="Room Motion",
                unique_id="motion_room",
                state_topic=f"{base_topic}/motion",
                device_class="motion",
                payload_on="detected",
                payload_off="clear",
            ),
            # Light switch with command topic
            Switch(
                config,
                device,
                name="Room Light",
                unique_id="light_room",
                state_topic=f"{base_topic}/light/state",
                command_topic=f"{base_topic}/light/set",  # Now supported!
                payload_on="ON",
                payload_off="OFF",
            ),
            # Dimmable light with brightness
            Light(
                config,
                device,
                name="Desk Lamp",
                unique_id="lamp_desk",
                state_topic=f"{base_topic}/lamp/state",
                command_topic=f"{base_topic}/lamp/set",
                brightness_state_topic=f"{base_topic}/lamp/brightness",  # Now supported!
                brightness_command_topic=f"{base_topic}/lamp/brightness/set",  # Now supported!
                brightness_scale=255,  # Now supported!
            ),
        ]

        print(f"\\nCreated {len(entities)} entities:")
        for entity in entities:
            print(f"  - {entity.component}: {entity.name}")

        # Publish discovery configurations
        print("\\nPublishing Home Assistant discovery configurations...")
        publish_discovery_configs(config, publisher, entities, device)

        # Publish some sample data
        print("\\nPublishing sample sensor data...")
        sample_data = {"temperature": 22.5, "timestamp": int(time.time())}
        publisher.publish(f"{base_topic}/temperature", json.dumps(sample_data))
        publisher.publish(f"{base_topic}/motion", "clear")
        publisher.publish(f"{base_topic}/light/state", "OFF")
        publisher.publish(f"{base_topic}/lamp/state", "ON")
        publisher.publish(f"{base_topic}/lamp/brightness", "128")

        print("\\n✅ Example complete!")
        print("Check Home Assistant > Settings > Devices & Services > MQTT")
        print("You should see 'Smart Room Controller' device with 4 entities")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        publisher.disconnect()


if __name__ == "__main__":
    main()
