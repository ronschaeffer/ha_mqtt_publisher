"""
Tests for the Discovery Manager.

This module tests the comprehensive discovery lifecycle management
functionality including entity and device management.
"""

import json
from unittest.mock import Mock

import pytest

from mqtt_publisher.ha_discovery import Device, DiscoveryManager, Entity


class TestDiscoveryManager:
    """Test the DiscoveryManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_config = Mock()
        self.mock_config.get.return_value = "homeassistant"

        self.mock_publisher = Mock()
        self.mock_publisher.publish.return_value = True

        self.manager = DiscoveryManager(
            config=self.mock_config, publisher=self.mock_publisher
        )

        self.test_device = Device(
            name="Test Device",
            identifiers=["test_device_001"],
            manufacturer="Test Manufacturer",
            model="Test Model v1.0",
        )

        self.test_entity = Entity(
            name="Test Sensor",
            component="sensor",
            unique_id="test_device_001_sensor",
            device=self.test_device,
            state_topic="test/sensor/state",
        )

    def test_initialization(self):
        """Test DiscoveryManager initialization."""
        assert self.manager.config == self.mock_config
        assert self.manager.publisher == self.mock_publisher
        assert self.manager.entities == {}
        assert self.manager.devices == {}
        assert self.manager.discovery_prefix == "homeassistant"

    def test_add_entity_success(self):
        """Test successful entity addition."""
        success = self.manager.add_entity(self.test_entity)

        assert success is True
        assert self.test_entity.unique_id in self.manager.entities
        assert self.manager.entities[self.test_entity.unique_id] == self.test_entity

        # Verify publish was called with correct parameters
        self.mock_publisher.publish.assert_called_once()
        call_args = self.mock_publisher.publish.call_args

        assert call_args[1]["topic"] == self.test_entity.get_config_topic()
        assert call_args[1]["retain"] is True

        # Verify the payload is valid JSON
        payload = call_args[1]["payload"]
        config = json.loads(payload)
        assert config["name"] == "Test Sensor"
        assert config["unique_id"] == "test_device_001_sensor"

    def test_add_entity_publish_failure(self):
        """Test entity addition when publish fails."""
        self.mock_publisher.publish.return_value = False

        success = self.manager.add_entity(self.test_entity)

        assert success is False
        # Entity should not be stored if publish failed
        assert self.test_entity.unique_id not in self.manager.entities

    def test_remove_entity_success(self):
        """Test successful entity removal."""
        # First add the entity
        self.manager.add_entity(self.test_entity)
        self.mock_publisher.publish.reset_mock()

        # Then remove it
        success = self.manager.remove_entity(self.test_entity.unique_id)

        assert success is True
        assert self.test_entity.unique_id not in self.manager.entities

        # Verify empty payload was published
        self.mock_publisher.publish.assert_called_once()
        call_args = self.mock_publisher.publish.call_args

        assert call_args[1]["topic"] == self.test_entity.get_config_topic()
        assert call_args[1]["payload"] == ""
        assert call_args[1]["retain"] is True

    def test_remove_nonexistent_entity(self):
        """Test removing a non-existent entity."""
        success = self.manager.remove_entity("nonexistent_id")

        assert success is False
        self.mock_publisher.publish.assert_not_called()

    def test_update_entity_success(self):
        """Test successful entity update."""
        # Add entity first
        self.manager.add_entity(self.test_entity)
        self.mock_publisher.publish.reset_mock()

        # Update entity
        success = self.manager.update_entity(
            self.test_entity.unique_id,
            name="Updated Sensor",
            device_class="temperature",
        )

        assert success is True

        # Verify entity was updated
        updated_entity = self.manager.entities[self.test_entity.unique_id]
        assert updated_entity.name == "Updated Sensor"
        assert updated_entity.extra_attributes["device_class"] == "temperature"

        # Verify republish happened
        self.mock_publisher.publish.assert_called_once()

    def test_add_device(self):
        """Test device addition."""
        success = self.manager.add_device(self.test_device)

        assert success is True
        device_id = self.test_device.identifiers[0]
        assert device_id in self.manager.devices
        assert self.manager.devices[device_id] == self.test_device

    def test_remove_device_with_entities(self):
        """Test device removal including all its entities."""
        # Add device and entity
        self.manager.add_device(self.test_device)
        self.manager.add_entity(self.test_entity)

        device_id = self.test_device.identifiers[0]

        # Remove device
        success = self.manager.remove_device(device_id)

        assert success is True
        assert device_id not in self.manager.devices
        assert self.test_entity.unique_id not in self.manager.entities

    def test_get_device_entities(self):
        """Test getting entities for a device."""
        self.manager.add_device(self.test_device)
        self.manager.add_entity(self.test_entity)

        # Create another entity for different device
        other_device = Device(name="Other Device", identifiers=["other_device_001"])
        other_entity = Entity(
            name="Other Sensor",
            component="sensor",
            unique_id="other_device_001_sensor",
            device=other_device,
            state_topic="other/sensor/state",
        )

        self.manager.add_device(other_device)
        self.manager.add_entity(other_entity)

        # Get entities for test device
        device_id = self.test_device.identifiers[0]
        entities = self.manager.get_device_entities(device_id)

        assert len(entities) == 1
        assert entities[0] == self.test_entity

    def test_publish_all_discoveries(self):
        """Test publishing all discovery configurations."""
        self.manager.add_entity(self.test_entity)
        self.mock_publisher.publish.reset_mock()

        success = self.manager.publish_all_discoveries()

        assert success is True
        self.mock_publisher.publish.assert_called_once()

    def test_clear_all_discoveries(self):
        """Test clearing all discovery configurations."""
        self.manager.add_entity(self.test_entity)
        self.mock_publisher.publish.reset_mock()

        success = self.manager.clear_all_discoveries()

        assert success is True
        assert len(self.manager.entities) == 0

        # Verify empty payload was published
        self.mock_publisher.publish.assert_called_once()
        call_args = self.mock_publisher.publish.call_args
        assert call_args[1]["payload"] == ""

    def test_get_entity_status(self):
        """Test getting entity status information."""
        self.manager.add_entity(self.test_entity)

        status = self.manager.get_entity_status(self.test_entity.unique_id)

        assert status is not None
        assert status["unique_id"] == self.test_entity.unique_id
        assert status["name"] == self.test_entity.name
        assert status["component"] == self.test_entity.component
        assert status["device"] == self.test_device.name
        assert status["config_topic"] == self.test_entity.get_config_topic()
        assert status["state_topic"] == self.test_entity.state_topic

    def test_get_entity_status_nonexistent(self):
        """Test getting status for non-existent entity."""
        status = self.manager.get_entity_status("nonexistent_id")
        assert status is None

    def test_list_entities(self):
        """Test listing all entities."""
        self.manager.add_entity(self.test_entity)

        entities = self.manager.list_entities()

        assert len(entities) == 1
        assert entities[0]["unique_id"] == self.test_entity.unique_id
        assert entities[0]["name"] == self.test_entity.name

    def test_list_devices(self):
        """Test listing all devices."""
        self.manager.add_device(self.test_device)
        self.manager.add_entity(self.test_entity)

        devices = self.manager.list_devices()

        assert len(devices) == 1
        device_info = devices[0]

        assert device_info["device_id"] == self.test_device.identifiers[0]
        assert device_info["name"] == self.test_device.name
        assert device_info["manufacturer"] == self.test_device.manufacturer
        assert device_info["model"] == self.test_device.model
        assert device_info["entity_count"] == 1

    def test_discovery_prefix_configuration(self):
        """Test custom discovery prefix configuration."""
        self.mock_config.get.return_value = "custom_prefix"

        manager = DiscoveryManager(
            config=self.mock_config, publisher=self.mock_publisher
        )

        assert manager.discovery_prefix == "custom_prefix"

    def test_error_handling_in_add_entity(self):
        """Test error handling when adding entity fails."""
        # Make publish raise an exception
        self.mock_publisher.publish.side_effect = Exception("MQTT error")

        success = self.manager.add_entity(self.test_entity)

        assert success is False
        assert self.test_entity.unique_id not in self.manager.entities

    def test_error_handling_in_remove_entity(self):
        """Test error handling when removing entity fails."""
        # Add entity first
        self.manager.add_entity(self.test_entity)

        # Make publish raise an exception for removal
        self.mock_publisher.publish.side_effect = Exception("MQTT error")

        success = self.manager.remove_entity(self.test_entity.unique_id)

        assert success is False
        # Entity should still be in manager since removal failed
        assert self.test_entity.unique_id in self.manager.entities


@pytest.fixture
def discovery_manager():
    """Fixture providing a configured DiscoveryManager."""
    mock_config = Mock()
    mock_config.get.return_value = "homeassistant"

    mock_publisher = Mock()
    mock_publisher.publish.return_value = True

    return DiscoveryManager(config=mock_config, publisher=mock_publisher)


def test_discovery_manager_integration(discovery_manager):
    """Integration test for the discovery manager."""
    # Create device and multiple entities
    device = Device(
        name="Integration Test Device",
        identifiers=["integration_test_001"],
        manufacturer="Test Corp",
        model="Model X",
    )

    entities = [
        Entity(
            name="Temperature",
            component="sensor",
            unique_id="integration_test_001_temp",
            device=device,
            state_topic="test/temp",
            device_class="temperature",
        ),
        Entity(
            name="Motion",
            component="binary_sensor",
            unique_id="integration_test_001_motion",
            device=device,
            state_topic="test/motion",
            device_class="motion",
        ),
        Entity(
            name="Light",
            component="light",
            unique_id="integration_test_001_light",
            device=device,
            state_topic="test/light/state",
            command_topic="test/light/command",
        ),
    ]

    # Add device
    discovery_manager.add_device(device)

    # Add all entities
    for entity in entities:
        success = discovery_manager.add_entity(entity)
        assert success is True

    # Verify everything is tracked
    assert len(discovery_manager.entities) == 3
    assert len(discovery_manager.devices) == 1

    # Test device entity listing
    device_entities = discovery_manager.get_device_entities(device.identifiers[0])
    assert len(device_entities) == 3

    # Test entity listing
    entity_list = discovery_manager.list_entities()
    assert len(entity_list) == 3

    # Test device listing
    device_list = discovery_manager.list_devices()
    assert len(device_list) == 1
    assert device_list[0]["entity_count"] == 3

    # Update an entity
    temp_entity_id = entities[0].unique_id
    success = discovery_manager.update_entity(
        temp_entity_id, unit_of_measurement="°C", icon="mdi:thermometer"
    )
    assert success is True

    # Verify update
    updated_entity = discovery_manager.entities[temp_entity_id]
    assert updated_entity.extra_attributes["unit_of_measurement"] == "°C"
    assert updated_entity.extra_attributes["icon"] == "mdi:thermometer"

    # Remove one entity
    motion_entity_id = entities[1].unique_id
    success = discovery_manager.remove_entity(motion_entity_id)
    assert success is True
    assert len(discovery_manager.entities) == 2

    # Remove device (should remove remaining entities)
    success = discovery_manager.remove_device(device.identifiers[0])
    assert success is True
    assert len(discovery_manager.entities) == 0
    assert len(discovery_manager.devices) == 0
