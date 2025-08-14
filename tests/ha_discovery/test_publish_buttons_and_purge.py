import json

from ha_mqtt_publisher.ha_discovery.device import Device
from ha_mqtt_publisher.ha_discovery.publisher import (
    publish_command_buttons,
    purge_legacy_discovery,
)


class MockConfig:
    def __init__(self, data=None):
        self.data = data or {}

    def get(self, key, default=None):
        keys = key.split(".")
        value = self.data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value


class PublisherSpy:
    def __init__(self):
        self.calls = []

    def publish(
        self, *, topic: str, payload: str, retain: bool, qos: int | None = None
    ):
        self.calls.append(
            {"topic": topic, "payload": payload, "retain": retain, "qos": qos}
        )
        return True


def test_publish_command_buttons_publishes_expected_configs():
    cfg = MockConfig(
        {
            "home_assistant": {"discovery_prefix": "homeassistant"},
            "app": {"unique_id_prefix": "testprefix"},
        }
    )
    dev = Device(cfg, identifiers=["dev1"], name="Demo")
    pub = PublisherSpy()

    buttons = {"refresh": "Refresh", "sync": "Sync"}

    entities = publish_command_buttons(
        cfg,
        pub,
        dev,
        base_unique_id="svc",
        base_name="Service",
        command_topic_base="app/cmd",
        buttons=buttons,
    )

    # One publish per button
    assert len(pub.calls) == len(buttons)
    # Entities returned match
    assert len(entities) == len(buttons)
    # Check topics and payloads
    seen_keys = set()
    for c in pub.calls:
        t = c["topic"]
        p = json.loads(c["payload"])
        assert c["retain"] is True
        # Topic should align with discovery_prefix and component
        prefix = cfg.get("home_assistant.discovery_prefix", "homeassistant")
        assert t.startswith(f"{prefix}/button/") and t.endswith("/config")
        # Extract key part from topic
        segment = t.split("/")[-2]
        key = segment.split("_")[-1]
        seen_keys.add(key)
        # Ensure unique segment matches base_unique_id + key
        assert segment == f"svc_{key}"
        assert p["name"].startswith("Service: ")
        # Unique_id is prefixed by app.unique_id_prefix
        uid_prefix = cfg.get("app.unique_id_prefix")
        assert p["unique_id"].startswith(f"{uid_prefix}_")
        assert p["command_topic"].endswith(f"/{key}")
        # Button payload should not include a state_topic
        assert "state_topic" not in p
        # Payload must include device block with identifiers and name
        assert (
            "device" in p
            and p["device"]["identifiers"] == ["dev1"]
            and p["device"]["name"] == "Demo"
        )
    # Ensure returned entities are Buttons
    for ent in entities:
        assert getattr(ent, "component", None) == "button"
    assert seen_keys == set(buttons.keys())


def test_purge_legacy_discovery_publishes_empty_payloads_retained():
    cfg = MockConfig({"home_assistant": {"discovery_prefix": "homeassistant"}})
    pub = PublisherSpy()

    topics = [
        "homeassistant/sensor/old/config",
        "homeassistant/switch/legacy/config",
    ]

    purge_legacy_discovery(cfg, pub, topics=topics)

    # Two retained empty publishes
    assert len(pub.calls) == 2
    published_topics = [c["topic"] for c in pub.calls]
    payloads = [c["payload"] for c in pub.calls]
    retains = [c["retain"] for c in pub.calls]

    assert published_topics == topics
    assert payloads == ["", ""]
    assert retains == [True, True]
