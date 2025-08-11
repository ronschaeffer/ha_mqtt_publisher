"""
Example: Modern HA bundle-only verification

Prerequisites:
- Your Home Assistant supports device bundle discovery.
- In your config.yaml set:

home_assistant:
  bundle_only_mode: true

This script connects to your MQTT broker, defines a device with two sensors,
and runs ensure_discovery() to verify the retained device bundle config exists.
If it is missing, the bundle will be re-published automatically.
"""

from ha_mqtt_publisher.config import Config
from ha_mqtt_publisher.ha_discovery import (
    Device,
    Sensor,
    ensure_discovery,
)
from ha_mqtt_publisher.publisher import MQTTPublisher


def main() -> None:
    # Load application config (expects mqtt.* and home_assistant.*)
    app_config = Config("config.yaml")

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
    device = Device(app_config, identifiers=["bridge01"], name="MQTT Bridge")
    temp = Sensor(
        app_config, device, name="Temperature", unique_id="temp", state_topic="room/t"
    )
    humid = Sensor(
        app_config, device, name="Humidity", unique_id="humid", state_topic="room/h"
    )

    # Verify the bundle (and republish if missing)
    summary = ensure_discovery(
        config=app_config,
        publisher=publisher,
        entities=[temp, humid],
        device=device,
        device_id="bridge01",  # optional; defaults to first identifier
        one_time_mode=True,
    )
    print(
        f"ensure_discovery: seen={len(summary['seen'])} missing={len(summary['missing'])} republished={len(summary['republished'])}"
    )

    publisher.disconnect()


if __name__ == "__main__":
    main()
