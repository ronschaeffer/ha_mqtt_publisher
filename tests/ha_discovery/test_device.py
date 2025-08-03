# tests/ha_discovery/test_device.py

"""Tests for the ha_discovery.device module."""

import pytest


class MockConfig:
    """Mock configuration object for testing."""

    def __init__(self, config_dict=None):
        self.config = config_dict or {}

    def get(self, key, default=None):
        """Mock get method that supports dot notation."""
        if "." in key:
            keys = key.split(".")
            value = self.config
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value
        return self.config.get(key, default)


@pytest.fixture
def mock_config():
    """Provides a mock Config object."""
    return MockConfig(
        {
            "app": {
                "unique_id_prefix": "test_device",
                "name": "Test Device",
                "manufacturer": "Test Corp",
                "model": "Test-v1",
            }
        }
    )


@pytest.fixture
def default_config():
    """Provides a mock Config object with no app config."""
    return MockConfig({})


def test_device_initialization_with_config(mock_config):
    """Test that the Device class initializes correctly with full config."""
    from mqtt_publisher.ha_discovery.device import Device

    device = Device(mock_config)
    assert device.name == "Test Device"
    assert device.identifiers == ["test_device"]
    assert device.manufacturer == "Test Corp"
    assert device.model == "Test-v1"


def test_device_initialization_with_defaults(default_config):
    """Test that the Device class initializes correctly with defaults."""
    from mqtt_publisher.ha_discovery.device import Device

    device = Device(default_config)
    assert device.name == "MQTT Publisher"
    assert device.identifiers == ["mqtt_publisher"]
    assert device.manufacturer == "Generic MQTT Publisher"
    assert device.model == "MQTT-Pub-Py"


def test_get_device_info(mock_config):
    """Test the generation of device info dictionary."""
    from mqtt_publisher.ha_discovery.device import Device

    device = Device(mock_config)
    device_info = device.get_device_info()

    expected_info = {
        "identifiers": ["test_device"],
        "name": "Test Device",
        "manufacturer": "Test Corp",
        "model": "Test-v1",
    }

    assert device_info == expected_info
