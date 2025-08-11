"""
Example: Entity-centric verification (per-entity discovery topics)

This script verifies per-entity discovery topics exist (retained) and republishes
any that are missing. It does not use the device bundle mode.
"""

from ha_mqtt_publisher.config import Config
from ha_mqtt_publisher.ha_discovery import Device, Sensor, ensure_discovery
from ha_mqtt_publisher.publisher import MQTTPublisher


def main() -> None:
    # Load application config (expects mqtt.* and home_assistant.*)
    app_config = Config("config.yaml")

    # Ensure bundle_only_mode is disabled in YAML if present
    # home_assistant:\n    #   bundle_only_mode: false

    # Build MQTT client from YAML
    publisher = MQTTPublisher(
        config={
            "broker_url": app_config.get("mqtt.broker_url"),
            "broker_port": app_config.get("mqtt.broker_port", 1883),
            "client_id": app_config.get("mqtt.client_id", "ha-mqtt-pub"),
            "security": app_config.get("mqtt.security", "none"),
            "auth": app_config.get("mqtt.auth"),
            "tls": app_config.get("mqtt.tls"),
            "default_qos": app_config.get("mqtt.default_qos", 1),
            "default_retain": app_config.get("mqtt.default_retain", True),
        }
    )
    publisher.connect()

    # Define a device and two sensors
    device = Device(app_config, identifiers=["room01"], name="Room Sensors")
    temp = Sensor(
        app_config,
        device,
        name="Temperature",
        unique_id="room_temp",
        state_topic="room/t",
    )
    humid = Sensor(
        app_config,
        device,
        name="Humidity",
        unique_id="room_humid",
        state_topic="room/h",
    )

    # Verify per-entity discovery topics (and republish if missing)
    summary = ensure_discovery(
        config=app_config,
        publisher=publisher,
        entities=[temp, humid],
        device=device,
        one_time_mode=True,
    )
    print(
        f"ensure_discovery: seen={len(summary['seen'])} missing={len(summary['missing'])} republished={len(summary['republished'])}"
    )

    publisher.disconnect()


if __name__ == "__main__":
    main()
