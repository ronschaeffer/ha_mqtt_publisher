"""Test the ha_discovery publisher module."""

import json
from unittest.mock import Mock

from src.mqtt_publisher.ha_discovery.device import Device
from src.mqtt_publisher.ha_discovery.entity import Sensor
from src.mqtt_publisher.ha_discovery.publisher import (
    create_sensor,
    create_status_sensor,
    publish_discovery_configs,
)
from src.mqtt_publisher.ha_discovery.status_sensor import StatusSensor


class MockConfig:
    """Mock configuration for testing."""

    def __init__(self, data=None):
        self.data = data or {}

    def get(self, key, default=None):
        """Get configuration value with dot notation support."""
        keys = key.split(".")
        value = self.data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value


class TestHADiscoveryPublisher:
    """Test the ha_discovery publisher functions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = MockConfig(
            {
                "home_assistant": {
                    "enabled": True,
                    "discovery_prefix": "homeassistant",
                },
                "mqtt": {"topics": {"status": "test/status"}},
                "device": {"name": "Test Device", "identifier": "test_device_123"},
            }
        )
        self.publisher = Mock()

    def test_publish_discovery_configs_disabled(self):
        """Test publish_discovery_configs when HA is disabled."""
        config = MockConfig({"home_assistant": {"enabled": False}})

        publish_discovery_configs(config, self.publisher)

        # Should not call publish when disabled
        self.publisher.publish.assert_not_called()

    def test_publish_discovery_configs_default_entities(self):
        """Test publish_discovery_configs with default entities (status sensor)."""
        publish_discovery_configs(self.config, self.publisher)

        # Should publish at least one entity (status sensor)
        assert self.publisher.publish.call_count >= 1

        # Verify the call was made with correct parameters
        call_args = self.publisher.publish.call_args
        assert call_args[1]["retain"] is True
        assert "topic" in call_args[1]
        assert "payload" in call_args[1]

    def test_publish_discovery_configs_no_status_topic(self):
        """Test publish_discovery_configs when no status topic is configured."""
        config = MockConfig(
            {
                "home_assistant": {
                    "enabled": True,
                    "discovery_prefix": "homeassistant",
                },
                "mqtt": {"topics": {}},
                "device": {"name": "Test Device", "identifier": "test_device_123"},
            }
        )

        publish_discovery_configs(config, self.publisher)

        # Should not publish anything when no entities are created
        self.publisher.publish.assert_not_called()

    def test_publish_discovery_configs_custom_entities(self):
        """Test publish_discovery_configs with custom entities."""
        # Create a mock device
        device = Mock(spec=Device)

        # Create mock entities
        entity1 = Mock(spec=Sensor)
        entity1.get_config_topic.return_value = "homeassistant/sensor/entity1/config"
        entity1.get_config_payload.return_value = {"name": "Entity 1"}

        entity2 = Mock(spec=Sensor)
        entity2.get_config_topic.return_value = "homeassistant/sensor/entity2/config"
        entity2.get_config_payload.return_value = {"name": "Entity 2"}

        entities = [entity1, entity2]

        publish_discovery_configs(
            self.config, self.publisher, entities=entities, device=device
        )

        # Should publish discovery config for each entity
        assert self.publisher.publish.call_count == 2

        # Verify the calls
        calls = self.publisher.publish.call_args_list

        # First entity
        assert calls[0][1]["topic"] == "homeassistant/sensor/entity1/config"
        assert calls[0][1]["payload"] == json.dumps({"name": "Entity 1"})
        assert calls[0][1]["retain"] is True

        # Second entity
        assert calls[1][1]["topic"] == "homeassistant/sensor/entity2/config"
        assert calls[1][1]["payload"] == json.dumps({"name": "Entity 2"})
        assert calls[1][1]["retain"] is True

    def test_publish_discovery_configs_custom_device(self):
        """Test publish_discovery_configs with custom device."""
        # Create a mock device
        device = Mock(spec=Device)

        # Create mock entity
        entity = Mock(spec=Sensor)
        entity.get_config_topic.return_value = "homeassistant/sensor/test/config"
        entity.get_config_payload.return_value = {"name": "Test Entity"}

        publish_discovery_configs(
            self.config, self.publisher, entities=[entity], device=device
        )

        # Should publish discovery config
        self.publisher.publish.assert_called_once()

    def test_create_sensor(self):
        """Test create_sensor function."""
        device = Mock(spec=Device)

        sensor = create_sensor(
            config=self.config,
            device=device,
            name="Test Sensor",
            unique_id="test_sensor_123",
            state_topic="test/sensor/state",
            icon="mdi:temperature",
            unit_of_measurement="°C",
        )

        # Verify sensor is created with correct properties
        assert isinstance(sensor, Sensor)
        assert sensor.name == "Test Sensor"
        assert sensor.unique_id == "test_sensor_123"
        assert sensor.state_topic == "test/sensor/state"
        assert sensor.icon == "mdi:temperature"
        assert sensor.unit_of_measurement == "°C"

    def test_create_status_sensor(self):
        """Test create_status_sensor function."""
        device = Mock(spec=Device)

        status_sensor = create_status_sensor(self.config, device)

        # Verify status sensor is created
        assert isinstance(status_sensor, StatusSensor)
        assert status_sensor.device == device
