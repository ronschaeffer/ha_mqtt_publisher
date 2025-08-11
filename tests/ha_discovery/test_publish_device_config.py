import json

import pytest

from ha_mqtt_publisher.ha_discovery import Device, publish_device_config


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


@pytest.fixture
def config_default():
    return StubConfig({"home_assistant.discovery_prefix": "homeassistant"})


def test_publish_device_config_uses_first_identifier_as_device_id(config_default):
    pub = PublisherMock()
    device = Device(config_default, identifiers=["dev123"], name="Demo")

    ok = publish_device_config(config_default, pub, device)

    assert ok is True
    assert len(pub.calls) == 1
    topic, payload, retain = pub.calls[0]

    assert topic == "homeassistant/device/dev123/config"
    assert retain is True

    payload_dict = json.loads(payload)
    assert payload_dict["identifiers"] == ["dev123"]
    assert payload_dict["name"] == "Demo"


def test_publish_device_config_with_explicit_device_id(config_default):
    pub = PublisherMock()
    device = Device(config_default, identifiers=["dev123"], name="Demo")

    ok = publish_device_config(config_default, pub, device, device_id="explicit_id")

    assert ok is True
    topic, payload, retain = pub.calls[0]
    assert topic == "homeassistant/device/explicit_id/config"
    assert json.loads(payload)["identifiers"] == ["dev123"]


def test_publish_device_config_slugifies_name_when_no_identifier(config_default):
    pub = PublisherMock()
    # Force empty identifiers to trigger slug from name
    device = Device(config_default, identifiers=[], name="My Device 01!")

    ok = publish_device_config(config_default, pub, device)
    assert ok is True
    topic, payload, _ = pub.calls[0]
    # Expect slug: my_device_01
    assert topic == "homeassistant/device/my_device_01/config"
    assert json.loads(payload)["name"] == "My Device 01!"
