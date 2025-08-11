import json

from ha_mqtt_publisher.ha_discovery import Device, Sensor
from ha_mqtt_publisher.ha_discovery.publisher import publish_discovery_configs


class StubConfig:
    def __init__(self, values: dict | None = None):
        self._values = values or {}

    def get(self, name, default=None):
        return self._values.get(name, default)


class PublisherSpy:
    def __init__(self):
        self.calls = []

    def publish(self, *, topic: str, payload: str, retain: bool):
        self.calls.append((topic, json.loads(payload), retain))
        return True


def test_publish_discovery_configs_can_emit_device_bundle_first():
    cfg = StubConfig({"home_assistant.discovery_prefix": "homeassistant"})
    pub = PublisherSpy()

    device = Device(cfg, identifiers=["devx"], name="Demo")
    s1 = Sensor(cfg, device, name="T", unique_id="t1", state_topic="x/t")

    publish_discovery_configs(
        config=cfg,
        publisher=pub,
        entities=[s1],
        device=device,
        emit_device_bundle=True,
        device_id="devx",
    )

    # Expect first publish is the bundle, then the entity topic
    assert len(pub.calls) == 2
    assert pub.calls[0][0] == "homeassistant/device/devx/config"
    assert pub.calls[1][0].endswith("/config")
