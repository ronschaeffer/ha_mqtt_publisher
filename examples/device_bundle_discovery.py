from ha_mqtt_publisher.config import Config
from ha_mqtt_publisher.ha_discovery import Device, Sensor, publish_device_bundle
from ha_mqtt_publisher.publisher import MQTTPublisher


def main():
    app_config = Config("config.yaml")

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

    device = Device(app_config)
    t = Sensor(
        app_config, device, name="Temperature", unique_id="temp", state_topic="room/t"
    )
    h = Sensor(
        app_config, device, name="Humidity", unique_id="humid", state_topic="room/h"
    )

    publish_device_bundle(app_config, publisher, device, [t, h])

    publisher.disconnect()


if __name__ == "__main__":
    main()
