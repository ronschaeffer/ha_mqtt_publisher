"""Tests for enhanced device discovery functionality using Entity objects."""

import json

from ha_mqtt_publisher.ha_discovery import (
    Device,
    Sensor,
    create_command_entities,
    publish_device_level_discovery,
)


class StubConfig:
    def __init__(self, data=None):
        self.data = data or {}

    def get(self, key, default=None):
        return self.data.get(key, default)


class PublisherMock:
    def __init__(self):
        self.calls = []

    def publish(self, topic, payload, retain=False):
        self.calls.append((topic, payload, retain))
        return True


def test_create_command_entities():
    """Test creating command system entities using Entity objects."""
    config = StubConfig()
    device = Device(config, identifiers=["test"], name="Test Device")

    entities = create_command_entities(
        config,
        device,
        "test_app",
        {
            "ack_topic": "test/ack",
            "result_topic": "test/result",
        },
    )

    assert len(entities) == 2
    assert all(isinstance(e, Sensor) for e in entities)

    ack_entity = next(e for e in entities if e.unique_id.endswith("_cmd_ack"))
    assert ack_entity.name == "Command Ack"
    assert ack_entity.state_topic == "test/ack"


def test_publish_with_entity_objects():
    """Test basic device discovery publishing with Entity objects."""
    config = StubConfig({"home_assistant.discovery_prefix": "homeassistant"})
    publisher = PublisherMock()
    device = Device(config, identifiers=["test_device"], name="Test Device")

    entities = [
        Sensor(
            config=config,
            device=device,
            name="Status",
            unique_id="test_status",
            state_topic="test/status",
            icon="mdi:information",
        )
    ]

    topic = publish_device_level_discovery(
        config=config,
        publisher=publisher,
        device=device,
        entities=entities,
    )

    assert topic == "homeassistant/device/test_device/config"
    assert len(publisher.calls) == 1

    payload = json.loads(publisher.calls[0][1])
    assert "cmps" in payload
    assert "test_status" in payload["cmps"]
    assert payload["cmps"]["test_status"]["p"] == "sensor"


if __name__ == "__main__":
    test_create_command_entities()
    test_publish_with_entity_objects()
    print("✅ All tests passed!")
