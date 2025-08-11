import json

from ha_mqtt_publisher.ha_discovery import Device, Sensor, publish_device_bundle


class StubConfig:
    def __init__(self, values: dict | None = None):
        self._values = values or {}

    def get(self, name, default=None):
        return self._values.get(name, default)


class PublisherMock:
    def __init__(self, should_succeed: bool = True):
        self.calls: list[tuple[str, str, bool]] = []
        self._should_succeed = should_succeed

    def publish(self, *, topic: str, payload: str, retain: bool):
        self.calls.append((topic, payload, retain))
        return self._should_succeed


def test_publish_device_bundle_builds_cmps_and_dev():
    cfg = StubConfig(
        {
            "home_assistant.discovery_prefix": "homeassistant",
            "mqtt.default_qos": 1,
            "mqtt.default_retain": True,
            "app.name": "mqtt_pub",
            "app.sw_version": "0.0.1",
            "app.configuration_url": "https://example.com",
        }
    )
    pub = PublisherMock()

    device = Device(cfg, identifiers=["dev01"], name="Demo")
    s1 = Sensor(cfg, device, name="T", unique_id="t1", state_topic="x/t")
    s2 = Sensor(cfg, device, name="H", unique_id="h1", state_topic="x/h")

    ok = publish_device_bundle(cfg, pub, device, [s1, s2])
    assert ok is True
    assert len(pub.calls) == 1

    topic, payload, retain = pub.calls[0]
    assert topic == "homeassistant/device/dev01/config"
    assert retain is True

    bundle = json.loads(payload)
    assert "dev" in bundle and "cmps" in bundle
    assert bundle["dev"]["identifiers"] == ["dev01"]
    assert set(bundle["cmps"].keys()) == {"t1", "h1"}
    assert bundle["cmps"]["t1"]["p"] == "sensor"
    assert bundle["qos"] == 1
    assert bundle["retain"] is True
