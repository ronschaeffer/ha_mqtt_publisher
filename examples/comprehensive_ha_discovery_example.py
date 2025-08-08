#!/usr/bin/env python3

"""
Comprehensive Home Assistant MQTT Discovery Example

This example demonstrates how to use the enhanced mqtt_publisher library
to create all supported Home Assistant entity types with full device information.

Key Features Demonstrated:
- Complete device information with all supported fields
- All 18+ entity types (sensors, switches, lights, covers, etc.)
- Proper topic structure and payload configuration
- Advanced entity attributes and device classes
"""

import json
import time

from mqtt_publisher.config import Config
from mqtt_publisher.ha_discovery import (
    AlarmControlPanel,
    BinarySensor,
    Button,
    Camera,
    Climate,
    Cover,
    Device,
    DeviceTracker,
    Fan,
    Light,
    Lock,
    Number,
    Scene,
    Select,
    Sensor,
    Siren,
    Switch,
    Text,
    Vacuum,
    publish_discovery_configs,
)
from mqtt_publisher.publisher import MQTTPublisher


def create_comprehensive_device(config: Config) -> Device:
    """Create a device with all supported Home Assistant fields."""
    device = Device(
        config,
        identifiers=["smart_home_hub_001"],
        name="Smart Home Hub",
        manufacturer="Example Corp",
        model="Hub Pro v2",
        sw_version="0.1.3-2e988e2-dirty",
        hw_version="1.4",
        serial_number="SH001234567",
        configuration_url="http://192.168.1.100:8080/config",
        suggested_area="Living Room",
        connections=[["mac", "02:42:ac:11:00:02"], ["ip", "192.168.1.100"]],
    )
    return device


def create_all_entity_types(config: Config, device: Device) -> list:
    """Create examples of all supported Home Assistant entity types."""
    base_topic = config.get("mqtt.base_topic", "smart_hub")
    entities = []

    # 1. Temperature Sensor with device class and unit
    entities.append(
        Sensor(
            config,
            device,
            name="Living Room Temperature",
            unique_id="temp_living_room",
            state_topic=f"{base_topic}/sensors/temperature",
            device_class="temperature",
            unit_of_measurement="°C",
            state_class="measurement",
            value_template="{{ value_json.temperature }}",
            icon="mdi:thermometer",
        )
    )

    # 2. Humidity Sensor
    entities.append(
        Sensor(
            config,
            device,
            name="Living Room Humidity",
            unique_id="humidity_living_room",
            state_topic=f"{base_topic}/sensors/humidity",
            device_class="humidity",
            unit_of_measurement="%",
            state_class="measurement",
            value_template="{{ value_json.humidity }}",
        )
    )

    # 3. Motion Binary Sensor
    entities.append(
        BinarySensor(
            config,
            device,
            name="Living Room Motion",
            unique_id="motion_living_room",
            state_topic=f"{base_topic}/sensors/motion",
            device_class="motion",
            payload_on="detected",
            payload_off="clear",
            availability_topic=f"{base_topic}/status",
            availability_template="{{ 'online' if value_json.status == 'ok' else 'offline' }}",
        )
    )

    # 4. Door/Window Binary Sensor
    entities.append(
        BinarySensor(
            config,
            device,
            name="Front Door",
            unique_id="door_front",
            state_topic=f"{base_topic}/sensors/door_front",
            device_class="door",
            payload_on="open",
            payload_off="closed",
        )
    )

    # 5. Light Switch
    entities.append(
        Switch(
            config,
            device,
            name="Living Room Light",
            unique_id="light_living_room",
            state_topic=f"{base_topic}/lights/living_room/state",
            command_topic=f"{base_topic}/lights/living_room/set",
            payload_on="ON",
            payload_off="OFF",
            optimistic=False,
            qos=1,
            retain=True,
        )
    )

    # 6. Dimmable Light
    entities.append(
        Light(
            config,
            device,
            name="Bedroom Light",
            unique_id="light_bedroom",
            state_topic=f"{base_topic}/lights/bedroom/state",
            command_topic=f"{base_topic}/lights/bedroom/set",
            brightness_state_topic=f"{base_topic}/lights/bedroom/brightness",
            brightness_command_topic=f"{base_topic}/lights/bedroom/brightness/set",
            brightness_scale=255,
            payload_on="ON",
            payload_off="OFF",
        )
    )

    # 7. RGB Light with Effects
    entities.append(
        Light(
            config,
            device,
            name="RGB Strip",
            unique_id="light_rgb_strip",
            state_topic=f"{base_topic}/lights/rgb_strip/state",
            command_topic=f"{base_topic}/lights/rgb_strip/set",
            brightness_state_topic=f"{base_topic}/lights/rgb_strip/brightness",
            brightness_command_topic=f"{base_topic}/lights/rgb_strip/brightness/set",
            rgb_state_topic=f"{base_topic}/lights/rgb_strip/rgb",
            rgb_command_topic=f"{base_topic}/lights/rgb_strip/rgb/set",
            effect_list=["rainbow", "colorloop", "strobe", "solid"],
            effect_state_topic=f"{base_topic}/lights/rgb_strip/effect",
            effect_command_topic=f"{base_topic}/lights/rgb_strip/effect/set",
        )
    )

    # 8. Window Cover/Blind
    entities.append(
        Cover(
            config,
            device,
            name="Living Room Blinds",
            unique_id="cover_living_room",
            state_topic=f"{base_topic}/covers/living_room/state",
            command_topic=f"{base_topic}/covers/living_room/set",
            position_topic=f"{base_topic}/covers/living_room/position",
            set_position_topic=f"{base_topic}/covers/living_room/position/set",
            device_class="blind",
            payload_open="OPEN",
            payload_close="CLOSE",
            payload_stop="STOP",
        )
    )

    # 9. Thermostat/Climate Control
    entities.append(
        Climate(
            config,
            device,
            name="Living Room Thermostat",
            unique_id="climate_living_room",
            current_temperature_topic=f"{base_topic}/climate/living_room/current_temp",
            temperature_command_topic=f"{base_topic}/climate/living_room/target_temp/set",
            temperature_state_topic=f"{base_topic}/climate/living_room/target_temp",
            mode_command_topic=f"{base_topic}/climate/living_room/mode/set",
            mode_state_topic=f"{base_topic}/climate/living_room/mode",
            modes=["off", "heat", "cool", "auto", "fan_only"],
            fan_mode_command_topic=f"{base_topic}/climate/living_room/fan/set",
            fan_mode_state_topic=f"{base_topic}/climate/living_room/fan",
            fan_modes=["auto", "low", "medium", "high"],
        )
    )

    # 10. Ceiling Fan
    entities.append(
        Fan(
            config,
            device,
            name="Bedroom Fan",
            unique_id="fan_bedroom",
            state_topic=f"{base_topic}/fans/bedroom/state",
            command_topic=f"{base_topic}/fans/bedroom/set",
            speed_state_topic=f"{base_topic}/fans/bedroom/speed",
            speed_command_topic=f"{base_topic}/fans/bedroom/speed/set",
            oscillation_state_topic=f"{base_topic}/fans/bedroom/oscillation",
            oscillation_command_topic=f"{base_topic}/fans/bedroom/oscillation/set",
            speeds=["low", "medium", "high"],
            payload_on="ON",
            payload_off="OFF",
        )
    )

    # 11. Smart Lock
    entities.append(
        Lock(
            config,
            device,
            name="Front Door Lock",
            unique_id="lock_front_door",
            state_topic=f"{base_topic}/locks/front_door/state",
            command_topic=f"{base_topic}/locks/front_door/set",
            payload_lock="LOCK",
            payload_unlock="UNLOCK",
            state_locked="locked",
            state_unlocked="unlocked",
        )
    )

    # 12. Volume Control (Number)
    entities.append(
        Number(
            config,
            device,
            name="Speaker Volume",
            unique_id="volume_speaker",
            state_topic=f"{base_topic}/audio/volume",
            command_topic=f"{base_topic}/audio/volume/set",
            min=0,
            max=100,
            step=5,
            unit_of_measurement="%",
            icon="mdi:volume-high",
        )
    )

    # 13. Input Source Select
    entities.append(
        Select(
            config,
            device,
            name="TV Input Source",
            unique_id="tv_input_source",
            state_topic=f"{base_topic}/tv/input",
            command_topic=f"{base_topic}/tv/input/set",
            options=["HDMI1", "HDMI2", "HDMI3", "USB", "Cable", "Netflix"],
        )
    )

    # 14. Message Display (Text)
    entities.append(
        Text(
            config,
            device,
            name="Display Message",
            unique_id="display_message",
            state_topic=f"{base_topic}/display/message",
            command_topic=f"{base_topic}/display/message/set",
            min=0,
            max=200,
            mode="text",
        )
    )

    # 15. Doorbell Button
    entities.append(
        Button(
            config,
            device,
            name="Doorbell",
            unique_id="doorbell_button",
            command_topic=f"{base_topic}/doorbell/press",
            device_class="doorbell",
            icon="mdi:doorbell",
        )
    )

    # 16. Device Tracker for Phone
    entities.append(
        DeviceTracker(
            config,
            device,
            name="John's Phone",
            unique_id="phone_john",
            state_topic=f"{base_topic}/presence/john_phone",
            payload_home="home",
            payload_not_home="away",
            source_type="bluetooth_le",
        )
    )

    # 17. Security System
    entities.append(
        AlarmControlPanel(
            config,
            device,
            name="Home Security",
            unique_id="alarm_home_security",
            state_topic=f"{base_topic}/alarm/state",
            command_topic=f"{base_topic}/alarm/set",
            code_arm_required=False,
            code_disarm_required=True,
            supported_features=["arm_home", "arm_away", "arm_night", "trigger"],
        )
    )

    # 18. Security Camera
    entities.append(
        Camera(
            config,
            device,
            name="Front Door Camera",
            unique_id="camera_front_door",
            topic=f"{base_topic}/camera/front_door/image",
        )
    )

    # 19. Robot Vacuum
    entities.append(
        Vacuum(
            config,
            device,
            name="Robot Vacuum",
            unique_id="vacuum_robot",
            state_topic=f"{base_topic}/vacuum/state",
            command_topic=f"{base_topic}/vacuum/command",
            send_command_topic=f"{base_topic}/vacuum/send_command",
            supported_features=[
                "start",
                "pause",
                "stop",
                "return_home",
                "battery",
                "status",
                "locate",
            ],
        )
    )

    # 20. Good Night Scene
    entities.append(
        Scene(
            config,
            device,
            name="Good Night",
            unique_id="scene_good_night",
            command_topic=f"{base_topic}/scenes/good_night/activate",
            icon="mdi:weather-night",
        )
    )

    # 21. Security Siren
    entities.append(
        Siren(
            config,
            device,
            name="Security Siren",
            unique_id="siren_security",
            state_topic=f"{base_topic}/siren/state",
            command_topic=f"{base_topic}/siren/set",
            available_tones=["emergency", "fire", "burglar"],
            support_volume_set=True,
            support_duration_set=True,
        )
    )

    return entities


def simulate_sensor_data(publisher: MQTTPublisher, base_topic: str):
    """Simulate some sensor data being published."""
    # Temperature and humidity data
    sensor_data = {"temperature": 21.5, "humidity": 45.2, "timestamp": int(time.time())}

    publisher.publish(f"{base_topic}/sensors/temperature", json.dumps(sensor_data))
    publisher.publish(f"{base_topic}/sensors/humidity", json.dumps(sensor_data))

    # Status data
    status_data = {
        "status": "ok",
        "uptime": 3600,
        "sensors_active": 21,
        "last_update": int(time.time()),
    }
    publisher.publish(f"{base_topic}/status", json.dumps(status_data))

    # Motion sensor
    publisher.publish(f"{base_topic}/sensors/motion", "clear")

    # Door sensor
    publisher.publish(f"{base_topic}/sensors/door_front", "closed")


def main():
    """Main function demonstrating comprehensive Home Assistant discovery."""
    # Load configuration
    config = Config("config/config_ha_discovery.yaml")

    # Create MQTT publisher
    mqtt_config = {
        "broker": config.get("mqtt.broker_url"),
        "port": config.get("mqtt.broker_port", 1883),
        "client_id": config.get("mqtt.client_id"),
        "username": config.get("mqtt.auth.username"),
        "password": config.get("mqtt.auth.password"),
        "use_tls": config.get("mqtt.security") in ["tls", "tls_with_client_cert"],
    }

    publisher = MQTTPublisher(**mqtt_config)

    try:
        publisher.connect()
        print("Connected to MQTT broker")

        # Create device with all supported fields
        device = create_comprehensive_device(config)
        print(f"Created device: {device.name}")
        print(f"Device info: {json.dumps(device.get_device_info(), indent=2)}")

        # Create all entity types
        entities = create_all_entity_types(config, device)
        print(f"Created {len(entities)} entities of various types")

        # Publish discovery configurations
        print("Publishing Home Assistant discovery configurations...")
        publish_discovery_configs(config, publisher, entities, device)

        print("Discovery configurations published successfully!")
        print("Check your Home Assistant under:")
        print("  - Settings > Devices & Services > MQTT")
        print("  - Look for 'Smart Home Hub' device")

        # Simulate some data
        print("Publishing sample sensor data...")
        base_topic = config.get("mqtt.base_topic", "smart_hub")
        simulate_sensor_data(publisher, base_topic)

        print(
            "Example complete! Your entities should now be available in Home Assistant."
        )
        print("\nEntity Summary:")
        for entity in entities:
            print(f"  - {entity.component}: {entity.name} ({entity.unique_id})")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        publisher.disconnect()


if __name__ == "__main__":
    main()
