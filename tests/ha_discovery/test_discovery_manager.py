"""Test the DiscoveryManager class."""

import json
from unittest.mock import Mock

from ha_mqtt_publisher.ha_discovery.device import Device
from ha_mqtt_publisher.ha_discovery.discovery_manager import DiscoveryManager
from ha_mqtt_publisher.ha_discovery.entity import Entity


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


class TestDiscoveryManager:
    """Test the DiscoveryManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = MockConfig(
            {"home_assistant": {"discovery_prefix": "homeassistant"}}
        )
        self.publisher = Mock()
        self.manager = DiscoveryManager(self.config, self.publisher)

    def test_initialization(self):
        """Test DiscoveryManager initialization."""
        assert self.manager.config == self.config
        assert self.manager.publisher == self.publisher
        assert self.manager.entities == {}
        assert self.manager.devices == {}
        assert self.manager.discovery_prefix == "homeassistant"

    def test_initialization_with_custom_prefix(self):
        """Test DiscoveryManager with custom discovery prefix."""
        config = MockConfig({"home_assistant": {"discovery_prefix": "custom_prefix"}})
        manager = DiscoveryManager(config, self.publisher)
        assert manager.discovery_prefix == "custom_prefix"

    def test_initialization_with_default_prefix(self):
        """Test DiscoveryManager with default discovery prefix."""
        config = MockConfig({})
        manager = DiscoveryManager(config, self.publisher)
        assert manager.discovery_prefix == "homeassistant"

    def test_add_entity_success(self):
        """Test successfully adding an entity."""
        # Create mock entity
        entity = Mock(spec=Entity)
        entity.unique_id = "test_entity_123"
        entity.name = "Test Entity"
        entity.get_config_topic.return_value = (
            "homeassistant/sensor/test_entity_123/config"
        )
        entity.get_config_payload.return_value = {"name": "Test Entity"}

        # Mock successful publish
        self.publisher.publish.return_value = True

        # Test adding entity
        result = self.manager.add_entity(entity)

        # Verify results
        assert result is True
        assert self.manager.entities["test_entity_123"] == entity

        # Verify publish was called correctly
        self.publisher.publish.assert_called_once_with(
            topic="homeassistant/sensor/test_entity_123/config",
            payload=json.dumps({"name": "Test Entity"}),
            retain=True,
        )

    def test_add_entity_publish_failure(self):
        """Test adding entity when publish fails."""
        # Create mock entity
        entity = Mock(spec=Entity)
        entity.unique_id = "test_entity_456"
        entity.name = "Test Entity"
        entity.get_config_topic.return_value = (
            "homeassistant/sensor/test_entity_456/config"
        )
        entity.get_config_payload.return_value = {"name": "Test Entity"}

        # Mock failed publish
        self.publisher.publish.return_value = False

        # Test adding entity
        result = self.manager.add_entity(entity)

        # Verify results
        assert result is False
        assert (
            self.manager.entities["test_entity_456"] == entity
        )  # Still stored locally

    def test_add_entity_exception(self):
        """Test adding entity when exception occurs."""
        # Create mock entity that raises exception
        entity = Mock(spec=Entity)
        entity.unique_id = "test_entity_789"
        entity.get_config_topic.side_effect = Exception("Test error")

        # Test adding entity
        result = self.manager.add_entity(entity)

        # Verify results
        assert result is False
        assert (
            "test_entity_789" in self.manager.entities
        )  # Entity was stored before exception

    def test_remove_entity_success(self):
        """Test successfully removing an entity."""
        # Create and add mock entity
        entity = Mock(spec=Entity)
        entity.unique_id = "test_entity_remove"
        entity.name = "Test Entity"
        entity.get_config_topic.return_value = (
            "homeassistant/sensor/test_entity_remove/config"
        )

        self.manager.entities["test_entity_remove"] = entity

        # Mock successful publish
        self.publisher.publish.return_value = True

        # Test removing entity
        result = self.manager.remove_entity("test_entity_remove")

        # Verify results
        assert result is True
        assert "test_entity_remove" not in self.manager.entities

        # Verify publish was called to remove discovery
        self.publisher.publish.assert_called_once_with(
            topic="homeassistant/sensor/test_entity_remove/config",
            payload="",
            retain=True,
        )

    def test_remove_entity_not_found(self):
        """Test removing entity that doesn't exist."""
        # Test removing non-existent entity
        result = self.manager.remove_entity("non_existent")

        # Verify results
        assert result is False
        self.publisher.publish.assert_not_called()

    def test_remove_entity_publish_failure(self):
        """Test removing entity when publish fails."""
        # Create and add mock entity
        entity = Mock(spec=Entity)
        entity.unique_id = "test_entity_fail"
        entity.name = "Test Entity"
        entity.get_config_topic.return_value = (
            "homeassistant/sensor/test_entity_fail/config"
        )

        self.manager.entities["test_entity_fail"] = entity

        # Mock failed publish
        self.publisher.publish.return_value = False

        # Test removing entity
        result = self.manager.remove_entity("test_entity_fail")

        # Verify results
        assert result is False
        assert "test_entity_fail" in self.manager.entities  # Still in manager

    def test_update_entity_success(self):
        """Test updating an entity."""
        # Create mock entity
        entity = Mock(spec=Entity)
        entity.unique_id = "test_entity_update"
        entity.name = "Test Entity"
        entity.extra_attributes = {}
        entity.get_config_topic.return_value = (
            "homeassistant/sensor/test_entity_update/config"
        )
        entity.get_config_payload.return_value = {"name": "Updated Entity"}

        # Add entity first
        self.manager.entities["test_entity_update"] = entity
        self.publisher.publish.return_value = True

        # Test updating entity
        result = self.manager.update_entity("test_entity_update", name="Updated Name")

        # Verify results
        assert result is True

    def test_update_entity_not_found(self):
        """Test updating entity that doesn't exist."""
        result = self.manager.update_entity("non_existent", name="Updated Name")
        assert result is False

    def test_add_device_success(self):
        """Test adding a device."""
        # Create mock device
        device = Mock(spec=Device)
        device.name = "Test Device"
        device.identifiers = ["test_device_123"]

        # Test adding device
        result = self.manager.add_device(device)

        # Verify device was added
        assert result is True
        assert self.manager.devices["test_device_123"] == device

    def test_add_device_no_identifiers(self):
        """Test adding device without identifiers."""
        # Create mock device without identifiers
        device = Mock(spec=Device)
        device.name = "Test Device"
        device.identifiers = []

        # Test adding device
        result = self.manager.add_device(device)

        # Verify device was added with name as key
        assert result is True
        assert self.manager.devices["Test Device"] == device

    def test_remove_device_success(self):
        """Test removing a device."""
        # Create mock device and entity
        device = Mock(spec=Device)
        device.name = "Test Device"
        device.identifiers = ["test_device_remove"]

        entity = Mock(spec=Entity)
        entity.unique_id = "entity_1"
        entity.name = "Test Entity"
        entity.device = device
        entity.get_config_topic.return_value = "homeassistant/sensor/entity_1/config"

        # Add device and entity
        self.manager.devices["test_device_remove"] = device
        self.manager.entities["entity_1"] = entity

        # Mock successful publish
        self.publisher.publish.return_value = True

        # Test removing device
        result = self.manager.remove_device("test_device_remove")

        # Verify results
        assert result is True
        assert "test_device_remove" not in self.manager.devices
        assert "entity_1" not in self.manager.entities

    def test_remove_device_not_found(self):
        """Test removing device that doesn't exist."""
        result = self.manager.remove_device("non_existent")
        assert result is False

    def test_get_device_entities(self):
        """Test getting entities for a device."""
        # Create mock device and entities
        device = Mock(spec=Device)
        device.name = "Test Device"

        entity1 = Mock(spec=Entity)
        entity1.unique_id = "entity1"
        entity1.device = device

        entity2 = Mock(spec=Entity)
        entity2.unique_id = "entity2"
        entity2.device = device

        other_entity = Mock(spec=Entity)
        other_entity.unique_id = "other"
        other_entity.device = Mock()

        # Add to manager
        self.manager.devices["test_device"] = device
        self.manager.entities["entity1"] = entity1
        self.manager.entities["entity2"] = entity2
        self.manager.entities["other"] = other_entity

        # Test getting device entities
        entities = self.manager.get_device_entities("test_device")

        # Verify results
        assert len(entities) == 2
        assert entity1 in entities
        assert entity2 in entities
        assert other_entity not in entities

    def test_get_device_entities_not_found(self):
        """Test getting entities for non-existent device."""
        entities = self.manager.get_device_entities("non_existent")
        assert entities == []

    def test_publish_all_discoveries(self):
        """Test publishing all discovery configurations."""
        # Create mock entities
        entity1 = Mock(spec=Entity)
        entity1.unique_id = "entity1"
        entity1.name = "Entity 1"
        entity1.get_config_topic.return_value = "homeassistant/sensor/entity1/config"
        entity1.get_config_payload.return_value = {"name": "Entity 1"}

        entity2 = Mock(spec=Entity)
        entity2.unique_id = "entity2"
        entity2.name = "Entity 2"
        entity2.get_config_topic.return_value = "homeassistant/sensor/entity2/config"
        entity2.get_config_payload.return_value = {"name": "Entity 2"}

        # Add entities
        self.manager.entities["entity1"] = entity1
        self.manager.entities["entity2"] = entity2

        # Mock successful publish
        self.publisher.publish.return_value = True

        # Test publishing all discoveries
        result = self.manager.publish_all_discoveries()

        # Verify results
        assert result is True
        assert self.publisher.publish.call_count == 2

    def test_clear_all_discoveries(self):
        """Test clearing all discovery configurations."""
        # Create mock entities
        entity1 = Mock(spec=Entity)
        entity1.unique_id = "entity1"
        entity1.name = "Entity 1"
        entity1.get_config_topic.return_value = "homeassistant/sensor/entity1/config"

        entity2 = Mock(spec=Entity)
        entity2.unique_id = "entity2"
        entity2.name = "Entity 2"
        entity2.get_config_topic.return_value = "homeassistant/sensor/entity2/config"

        # Add entities
        self.manager.entities["entity1"] = entity1
        self.manager.entities["entity2"] = entity2

        # Mock successful publish
        self.publisher.publish.return_value = True

        # Test clearing all discoveries
        result = self.manager.clear_all_discoveries()

        # Verify results
        assert result is True
        assert len(self.manager.entities) == 0
        assert self.publisher.publish.call_count == 2

    def test_get_entity_status(self):
        """Test getting entity status."""
        # Create mock entity with device
        device = Mock(spec=Device)
        device.name = "Test Device"

        entity = Mock(spec=Entity)
        entity.unique_id = "test_entity"
        entity.name = "Test Entity"
        entity.component = "sensor"
        entity.device = device
        entity.get_config_topic.return_value = "homeassistant/sensor/test_entity/config"

        # Add entity
        self.manager.entities["test_entity"] = entity

        # Test getting status
        status = self.manager.get_entity_status("test_entity")

        # Verify results
        assert status is not None
        assert status["unique_id"] == "test_entity"
        assert status["name"] == "Test Entity"
        assert status["component"] == "sensor"
        assert status["device"] == "Test Device"
        assert status["config_topic"] == "homeassistant/sensor/test_entity/config"

    def test_get_entity_status_not_found(self):
        """Test getting status for non-existent entity."""
        status = self.manager.get_entity_status("non_existent")
        assert status is None

    def test_list_entities(self):
        """Test listing all entities."""
        # Create mock entities
        device = Mock(spec=Device)
        device.name = "Test Device"

        entity1 = Mock(spec=Entity)
        entity1.unique_id = "entity1"
        entity1.name = "Entity 1"
        entity1.component = "sensor"
        entity1.device = device
        entity1.get_config_topic.return_value = "homeassistant/sensor/entity1/config"

        entity2 = Mock(spec=Entity)
        entity2.unique_id = "entity2"
        entity2.name = "Entity 2"
        entity2.component = "switch"
        entity2.device = device
        entity2.get_config_topic.return_value = "homeassistant/switch/entity2/config"

        # Add entities
        self.manager.entities["entity1"] = entity1
        self.manager.entities["entity2"] = entity2

        # Test listing entities
        entities = self.manager.list_entities()

        # Verify results
        assert len(entities) == 2
        assert any(e["unique_id"] == "entity1" for e in entities)
        assert any(e["unique_id"] == "entity2" for e in entities)

    def test_list_devices(self):
        """Test listing all devices."""
        # Create mock device
        device = Mock(spec=Device)
        device.name = "Test Device"

        # Add device
        self.manager.devices["test_device"] = device

        # Test listing devices
        devices = self.manager.list_devices()

        # Verify results
        assert len(devices) == 1
        assert devices[0]["device_id"] == "test_device"
        assert devices[0]["name"] == "Test Device"
        assert devices[0]["entity_count"] == 0

    def test_add_entity_publish_failure_with_logging(self):
        """Test adding entity with publish failure and verify logging."""
        from unittest.mock import patch

        # Create mock entity
        entity = Mock(spec=Entity)
        entity.unique_id = "test_entity_fail"
        entity.name = "Test Entity Failed"
        entity.get_config_topic.return_value = (
            "homeassistant/sensor/test_entity_fail/config"
        )
        entity.get_config_payload.return_value = {"name": "Test Entity Failed"}

        # Mock failed publish
        self.publisher.publish.return_value = False

        with patch("logging.error") as mock_error:
            # Test adding entity
            result = self.manager.add_entity(entity)

            # Verify error was logged
            mock_error.assert_called_once()
            assert "Failed to add entity" in mock_error.call_args[0][0]

        # Verify results
        assert result is False

    def test_add_entity_success_with_logging(self):
        """Test adding entity successfully and verify logging."""
        from unittest.mock import patch

        # Create mock entity
        entity = Mock(spec=Entity)
        entity.unique_id = "test_entity_success"
        entity.name = "Test Entity Success"
        entity.get_config_topic.return_value = (
            "homeassistant/sensor/test_entity_success/config"
        )
        entity.get_config_payload.return_value = {"name": "Test Entity Success"}

        # Mock successful publish
        self.publisher.publish.return_value = True

        with patch("logging.info") as mock_info:
            # Test adding entity
            result = self.manager.add_entity(entity)

            # Verify info was logged
            mock_info.assert_called_once()
            assert "Added entity" in mock_info.call_args[0][0]

        # Verify results
        assert result is True

    def test_remove_entity_with_logging_warning(self):
        """Test removing non-existent entity and verify warning logging."""
        from unittest.mock import patch

        with patch("logging.warning") as mock_warning:
            # Test removing non-existent entity
            result = self.manager.remove_entity("non_existent_entity")

            # Verify warning was logged
            mock_warning.assert_called_once()
            assert (
                "Entity 'non_existent_entity' not found" in mock_warning.call_args[0][0]
            )

        # Verify results
        assert result is False

    def test_remove_entity_success_with_logging(self):
        """Test removing entity successfully and verify logging."""
        from unittest.mock import patch

        # Create and add mock entity
        entity = Mock(spec=Entity)
        entity.unique_id = "test_entity_remove_log"
        entity.name = "Test Entity Remove"
        entity.get_config_topic.return_value = (
            "homeassistant/sensor/test_entity_remove_log/config"
        )

        self.manager.entities["test_entity_remove_log"] = entity

        # Mock successful publish
        self.publisher.publish.return_value = True

        with patch("logging.info") as mock_info:
            # Test removing entity
            result = self.manager.remove_entity("test_entity_remove_log")

            # Verify info was logged
            mock_info.assert_called_once()
            assert "Removed entity" in mock_info.call_args[0][0]

        # Verify results
        assert result is True

    def test_remove_entity_failure_with_logging(self):
        """Test removing entity with publish failure and verify logging."""
        from unittest.mock import patch

        # Create and add mock entity
        entity = Mock(spec=Entity)
        entity.unique_id = "test_entity_remove_fail"
        entity.name = "Test Entity Remove Fail"
        entity.get_config_topic.return_value = (
            "homeassistant/sensor/test_entity_remove_fail/config"
        )

        self.manager.entities["test_entity_remove_fail"] = entity

        # Mock failed publish
        self.publisher.publish.return_value = False

        with patch("logging.error") as mock_error:
            # Test removing entity
            result = self.manager.remove_entity("test_entity_remove_fail")

            # Verify error was logged
            mock_error.assert_called_once()
            assert "Failed to remove entity" in mock_error.call_args[0][0]

        # Verify results
        assert result is False

    def test_add_entity_exception_handling(self):
        """Test add_entity with exception and verify error logging."""
        from unittest.mock import patch

        # Create mock entity that raises exception
        entity = Mock(spec=Entity)
        entity.unique_id = "test_entity_exception"
        entity.get_config_topic.side_effect = Exception("Test exception")

        with patch("logging.error") as mock_error:
            # Test adding entity
            result = self.manager.add_entity(entity)

            # Verify error was logged
            mock_error.assert_called_once()
            assert "Error adding entity" in mock_error.call_args[0][0]

        # Verify results
        assert result is False

    def test_remove_entity_exception_handling(self):
        """Test remove_entity with exception and verify error logging."""
        from unittest.mock import patch

        # Create and add mock entity that will cause exception
        entity = Mock(spec=Entity)
        entity.unique_id = "test_entity_exception_remove"
        entity.name = "Test Entity Exception"
        entity.get_config_topic.side_effect = Exception("Test exception")

        self.manager.entities["test_entity_exception_remove"] = entity

        with patch("logging.error") as mock_error:
            # Test removing entity
            result = self.manager.remove_entity("test_entity_exception_remove")

            # Verify error was logged
            mock_error.assert_called_once()
            assert "Error removing entity" in mock_error.call_args[0][0]

        # Verify results
        assert result is False

    def test_update_entity_with_attribute_setting(self):
        """Test updating entity with hasattr vs extra_attributes."""
        # Create mock entity with some attributes
        entity = Mock(spec=Entity)
        entity.unique_id = "test_entity_update_attr"
        entity.name = "Test Entity"
        entity.extra_attributes = {}
        entity.get_config_topic.return_value = (
            "homeassistant/sensor/test_entity_update_attr/config"
        )
        entity.get_config_payload.return_value = {"name": "Updated Entity"}

        # Add entity first
        self.manager.entities["test_entity_update_attr"] = entity
        self.publisher.publish.return_value = True

        # Test updating with existing attribute
        entity.existing_attr = "old_value"
        result = self.manager.update_entity(
            "test_entity_update_attr", existing_attr="new_value"
        )

        # Verify results
        assert result is True
        assert entity.existing_attr == "new_value"

        # Test updating with non-existing attribute (goes to extra_attributes)
        result = self.manager.update_entity(
            "test_entity_update_attr", new_attr="new_value"
        )

        # Verify results
        assert result is True
        assert entity.extra_attributes["new_attr"] == "new_value"

    def test_add_device_exception_handling(self):
        """Test add_device with exception and verify error logging."""
        from unittest.mock import PropertyMock, patch

        # Create mock device that will cause exception
        device = Mock(spec=Device)
        # Make name property raise an exception when accessed
        type(device).name = PropertyMock(side_effect=Exception("Test exception"))

        with patch("logging.error") as mock_error:
            # Test adding device
            result = self.manager.add_device(device)

            # Verify error was logged
            mock_error.assert_called_once()
            assert "Error adding device" in mock_error.call_args[0][0]

        # Verify results
        assert result is False

    def test_add_device_success_with_logging(self):
        """Test adding device successfully and verify logging."""
        from unittest.mock import patch

        # Create mock device
        device = Mock(spec=Device)
        device.name = "Test Device Success"
        device.identifiers = ["test_device_success"]

        with patch("logging.info") as mock_info:
            # Test adding device
            result = self.manager.add_device(device)

            # Verify info was logged
            mock_info.assert_called_once()
            assert "Added device" in mock_info.call_args[0][0]

        # Verify results
        assert result is True

    def test_remove_device_with_logging_warning(self):
        """Test removing non-existent device and verify warning logging."""
        from unittest.mock import patch

        with patch("logging.warning") as mock_warning:
            # Test removing non-existent device
            result = self.manager.remove_device("non_existent_device")

            # Verify warning was logged
            mock_warning.assert_called_once()
            assert (
                "Device 'non_existent_device' not found" in mock_warning.call_args[0][0]
            )

        # Verify results
        assert result is False

    def test_remove_device_success_with_logging(self):
        """Test removing device successfully and verify logging."""
        from unittest.mock import patch

        # Create mock device
        device = Mock(spec=Device)
        device.name = "Test Device Remove"
        device.identifiers = ["test_device_remove_log"]

        # Add device
        self.manager.devices["test_device_remove_log"] = device

        # Mock successful entity removal
        self.publisher.publish.return_value = True

        with patch("logging.info") as mock_info:
            # Test removing device
            result = self.manager.remove_device("test_device_remove_log")

            # Verify info was logged
            mock_info.assert_called_once()
            assert "Removed device" in mock_info.call_args[0][0]

        # Verify results
        assert result is True

    def test_remove_device_exception_handling(self):
        """Test remove_device with exception and verify error logging."""
        from unittest.mock import PropertyMock, patch

        # Create mock device that will cause exception
        device = Mock(spec=Device)
        # Make name property raise an exception when accessed
        type(device).name = PropertyMock(side_effect=Exception("Test exception"))

        self.manager.devices["test_device_exception"] = device

        with patch("logging.error") as mock_error:
            # Test removing device
            result = self.manager.remove_device("test_device_exception")

            # Verify error was logged
            mock_error.assert_called_once()
            assert "Error removing device" in mock_error.call_args[0][0]

        # Verify results
        assert result is False
