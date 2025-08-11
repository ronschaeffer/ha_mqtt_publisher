"""Tests for strict validation, extra_allowed, slugification, and exports."""

import importlib
import types
from unittest.mock import MagicMock

import pytest

from ha_mqtt_publisher.ha_discovery.device import Device
from ha_mqtt_publisher.ha_discovery.entity import BinarySensor, Sensor


class MockConfig:
    """Mock configuration with dot-notation get()."""

    def __init__(self, data=None):
        self.data = data or {}

    def get(self, key, default=None):
        parts = key.split(".")
        cur = self.data
        for p in parts:
            if isinstance(cur, dict) and p in cur:
                cur = cur[p]
            else:
                return default
        return cur


def make_device() -> Device:
    device = MagicMock(spec=Device)
    device.get_device_info.return_value = {
        "identifiers": ["test_device"],
        "name": "Test Device",
        "manufacturer": "Test Corp",
    }
    return device


def test_strict_validation_blocks_invalid_state_class():
    """With strict_validation=True (default), invalid sensor.state_class errors."""
    config = MockConfig(
        {
            "app": {"unique_id_prefix": "test"},
            "mqtt": {"base_topic": "test"},
            # strict_validation defaults to True; keep explicit for clarity
            "home_assistant": {"strict_validation": True},
        }
    )
    device = make_device()

    with pytest.raises(ValueError):
        Sensor(
            config,
            device,
            name="Bad State Class",
            unique_id="bad_state",
            state_topic="test/state",
            state_class="not_a_real_state_class",
        )


def test_lenient_validation_allows_invalid_when_disabled():
    """With strict_validation=False, invalid values should not raise."""
    config = MockConfig(
        {
            "app": {"unique_id_prefix": "test"},
            "mqtt": {"base_topic": "test"},
            "home_assistant": {"strict_validation": False},
        }
    )
    device = make_device()

    # Should not raise
    Sensor(
        config,
        device,
        name="Lenient Sensor",
        unique_id="ok_lenient",
        state_topic="test/state",
        state_class="not_a_real_state_class",
    )


def test_extra_allowed_extends_sets_in_strict_mode():
    """extra_allowed.* extends allowed sets even when strict_validation=True."""
    config = MockConfig(
        {
            "app": {"unique_id_prefix": "test"},
            "mqtt": {"base_topic": "test"},
            "home_assistant": {
                "strict_validation": True,
                "extra_allowed": {"sensor_state_classes": ["weird_custom_state"]},
            },
        }
    )
    device = make_device()

    # Should not raise because extra_allowed added the custom value
    Sensor(
        config,
        device,
        name="Custom State",
        unique_id="custom_state",
        state_topic="test/state",
        state_class="weird_custom_state",
    )


def test_binary_sensor_device_class_validation():
    """Invalid binary_sensor device_class should raise in strict mode."""
    config = MockConfig(
        {
            "app": {"unique_id_prefix": "test"},
            "mqtt": {"base_topic": "test"},
            "home_assistant": {"strict_validation": True},
        }
    )
    device = make_device()

    with pytest.raises(ValueError):
        BinarySensor(
            config,
            device,
            name="Bad Binary Class",
            unique_id="bad_bin",
            state_topic="test/bin",
            device_class="made_up",
        )


def test_object_id_slugification_preserves_unique_id():
    """object_id is slugified, but unique_id preserves the prefix and original text."""
    config = MockConfig(
        {
            "app": {"unique_id_prefix": "My App"},
            "mqtt": {"base_topic": "test"},
            "home_assistant": {"strict_validation": True},
        }
    )
    device = make_device()

    sensor = Sensor(
        config,
        device,
        name="Temp Sensor",
        unique_id="Room 1/2",
        state_topic="test/temp",
    )

    payload = sensor.get_config_payload()
    # unique_id keeps prefix + original text with spaces and slash
    assert payload["unique_id"] == "My App_Room 1/2"
    # object_id is slugified: lowercase, spaces/slashes/hyphens -> underscore, non-alnum removed
    # "My App_Room 1/2" -> "my_app_room_12"
    assert payload["object_id"] == "my_app_room_12"


def test_public_exports_expected_and_not_exposing_internal():
    """Ensure key public classes are exported and internal ones are not."""
    mod = importlib.import_module("ha_mqtt_publisher.ha_discovery")
    assert isinstance(mod, types.ModuleType)

    # Expected exports (a representative subset)
    for name in [
        "Device",
        "Sensor",
        "BinarySensor",
        "DiscoveryManager",
        "StatusSensor",
    ]:
        assert hasattr(mod, name), f"Missing expected export: {name}"

    # Internal-only types should not be exported at top-level
    for internal_name in ["Vacuum", "Scene", "Siren"]:
        assert not hasattr(mod, internal_name), f"Should not export: {internal_name}"
