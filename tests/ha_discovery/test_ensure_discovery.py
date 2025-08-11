import json

from ha_mqtt_publisher.ha_discovery import Device, Sensor, ensure_discovery


class StubConfig:
    def __init__(self, data):
        self._d = data

    def get(self, key, default=None):
        return self._d.get(key, default)


class Msg:
    def __init__(self, topic: str):
        self.topic = topic


class PubMock:
    def __init__(self, present: set[str] | None = None):
        self.present = present or set()
        self.subs: list[tuple[str, int]] = []
        self.unsubs: list[str] = []
        self.publishes: list[tuple[str, str, bool]] = []

    def subscribe(self, topic, qos=0, callback=None, properties=None):
        self.subs.append((topic, qos))
        if topic in self.present and callback:
            # Immediately simulate retained delivery
            callback(None, None, Msg(topic))
        return True

    def unsubscribe(self, topic, properties=None):
        self.unsubs.append(topic)
        return True

    def publish(self, *, topic, payload, retain=True):
        self.publishes.append((topic, payload, retain))
        return True


def test_ensure_discovery_republishes_missing_entity():
    cfg = StubConfig({"home_assistant.discovery_prefix": "homeassistant"})
    device = Device(cfg, identifiers=["dev01"], name="Demo")

    s1 = Sensor(cfg, device, name="T", unique_id="t1", state_topic="x/t")
    s2 = Sensor(cfg, device, name="H", unique_id="h1", state_topic="x/h")

    present = {s1.get_config_topic()}  # s2 is missing
    pub = PubMock(present=present)

    summary = ensure_discovery(
        config=cfg,
        publisher=pub,
        entities=[s1, s2],
        device=device,
        timeout=0.05,
        one_time_mode=True,
    )

    assert s1.get_config_topic() in summary["seen"]
    assert s2.get_config_topic() in summary["missing"]

    # One publish for the missing entity topic
    assert len(pub.publishes) == 1
    topic, payload, retain = pub.publishes[0]
    assert topic == s2.get_config_topic()
    assert json.loads(payload)["name"] == "H"
    assert retain is True


def test_ensure_discovery_bundle_only_republishes_bundle():
    cfg = StubConfig(
        {
            "home_assistant.discovery_prefix": "homeassistant",
            "home_assistant.bundle_only_mode": True,
        }
    )
    device = Device(cfg, identifiers=["dev01"], name="Demo")
    s = Sensor(cfg, device, name="T", unique_id="t1", state_topic="x/t")

    pub = PubMock(present=set())  # bundle missing

    summary = ensure_discovery(
        config=cfg,
        publisher=pub,
        entities=[s],
        device=device,
        device_id="dev01",
        timeout=0.05,
        one_time_mode=True,
    )

    # Should republish a single bundle topic
    assert any(call[0] == "homeassistant/device/dev01/config" for call in pub.publishes)
    assert "homeassistant/device/dev01/config" in summary["republished"]
