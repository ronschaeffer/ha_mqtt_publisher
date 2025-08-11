"""Test the DiscoveryManager class."""

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


class TestDiscoveryManagerBasic:
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

        # Add entity
        self.manager.entities["entity1"] = entity1

        # Test listing entities
        entities = self.manager.list_entities()

        # Verify results
        assert len(entities) == 1
        assert entities[0]["unique_id"] == "entity1"

    def test_clear_all_discoveries(self):
        """Test clearing all discovery configurations."""
        # Create mock entity
        entity1 = Mock(spec=Entity)
        entity1.unique_id = "entity1"
        entity1.name = "Entity 1"
        entity1.get_config_topic.return_value = "homeassistant/sensor/entity1/config"

        # Add entity
        self.manager.entities["entity1"] = entity1

        # Mock successful publish
        self.publisher.publish.return_value = True

        # Test clearing all discoveries
        result = self.manager.clear_all_discoveries()

        # Verify results
        assert result is True
        assert len(self.manager.entities) == 0

    def test_add_entity_with_error_logging(self):
        """Test adding entity with publish failure and verify error logging."""
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

        with patch(
            "ha_mqtt_publisher.ha_discovery.discovery_manager.logging.error"
        ) as mock_error:
            # Test adding entity
            result = self.manager.add_entity(entity)

            # Verify error was logged
            mock_error.assert_called_once()

        # Verify results
        assert result is False

    def test_add_entity_with_success_logging(self):
        """Test adding entity successfully and verify info logging."""
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

        with patch(
            "ha_mqtt_publisher.ha_discovery.discovery_manager.logging.info"
        ) as mock_info:
            # Test adding entity
            result = self.manager.add_entity(entity)

            # Verify info was logged
            mock_info.assert_called_once()

        # Verify results
        assert result is True

    def test_remove_entity_not_found_with_logging(self):
        """Test removing non-existent entity and verify warning logging."""
        from unittest.mock import patch

        with patch(
            "ha_mqtt_publisher.ha_discovery.discovery_manager.logging.warning"
        ) as mock_warning:
            # Test removing non-existent entity
            result = self.manager.remove_entity("non_existent_entity")

            # Verify warning was logged
            mock_warning.assert_called_once()

        # Verify results
        assert result is False

    def test_remove_entity_success_with_logging(self):
        """Test removing entity successfully and verify info logging."""
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

        with patch(
            "ha_mqtt_publisher.ha_discovery.discovery_manager.logging.info"
        ) as mock_info:
            # Test removing entity
            result = self.manager.remove_entity("test_entity_remove_log")

            # Verify info was logged
            mock_info.assert_called_once()

        # Verify results
        assert result is True

    def test_remove_entity_failure_with_logging(self):
        """Test removing entity with publish failure and verify error logging."""
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

        with patch(
            "ha_mqtt_publisher.ha_discovery.discovery_manager.logging.error"
        ) as mock_error:
            # Test removing entity
            result = self.manager.remove_entity("test_entity_remove_fail")

            # Verify error was logged
            mock_error.assert_called_once()

        # Verify results
        assert result is False

    def test_add_entity_exception_handling(self):
        """Test add_entity with exception and verify error logging."""
        from unittest.mock import patch

        # Create mock entity that raises exception
        entity = Mock(spec=Entity)
        entity.unique_id = "test_entity_exception"
        entity.get_config_topic.side_effect = Exception("Test exception")

        with patch(
            "ha_mqtt_publisher.ha_discovery.discovery_manager.logging.error"
        ) as mock_error:
            # Test adding entity
            result = self.manager.add_entity(entity)

            # Verify error was logged
            mock_error.assert_called_once()

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

        with patch(
            "ha_mqtt_publisher.ha_discovery.discovery_manager.logging.error"
        ) as mock_error:
            # Test removing entity
            result = self.manager.remove_entity("test_entity_exception_remove")

            # Verify error was logged
            mock_error.assert_called_once()

        # Verify results
        assert result is False

    def test_update_entity_with_hasattr_logic(self):
        """Test updating entity with hasattr vs extra_attributes logic."""
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
        from unittest.mock import patch

        # Create mock device that will cause exception during access
        device = Mock(spec=Device)
        # Use a property that exists but raise exception when accessing identifiers
        device.identifiers = []
        device.name = Mock()
        device.name.__str__ = Mock(side_effect=Exception("Test exception"))

        with patch(
            "ha_mqtt_publisher.ha_discovery.discovery_manager.logging.error"
        ) as mock_error:
            # Test adding device
            result = self.manager.add_device(device)

            # Verify error was logged
            mock_error.assert_called_once()

        # Verify results
        assert result is False

    def test_add_device_with_success_logging(self):
        """Test adding device successfully and verify info logging."""
        from unittest.mock import patch

        # Create mock device
        device = Mock(spec=Device)
        device.name = "Test Device Success"
        device.identifiers = ["test_device_success"]

        with patch(
            "ha_mqtt_publisher.ha_discovery.discovery_manager.logging.info"
        ) as mock_info:
            # Test adding device
            result = self.manager.add_device(device)

            # Verify info was logged
            mock_info.assert_called_once()

        # Verify results
        assert result is True

    def test_remove_device_not_found_with_logging(self):
        """Test removing non-existent device and verify warning logging."""
        from unittest.mock import patch

        with patch(
            "ha_mqtt_publisher.ha_discovery.discovery_manager.logging.warning"
        ) as mock_warning:
            # Test removing non-existent device
            result = self.manager.remove_device("non_existent_device")

            # Verify warning was logged
            mock_warning.assert_called_once()

        # Verify results
        assert result is False

    def test_remove_device_success_with_logging(self):
        """Test removing device successfully and verify info logging."""
        from unittest.mock import patch

        # Create mock device
        device = Mock(spec=Device)
        device.name = "Test Device Remove"
        device.identifiers = ["test_device_remove_log"]

        # Add device
        self.manager.devices["test_device_remove_log"] = device

        # Mock successful entity removal
        self.publisher.publish.return_value = True

        with patch(
            "ha_mqtt_publisher.ha_discovery.discovery_manager.logging.info"
        ) as mock_info:
            # Test removing device
            result = self.manager.remove_device("test_device_remove_log")

            # Verify info was logged
            mock_info.assert_called_once()

        # Verify results
        assert result is True

    def test_device_removal_exception_handling(self):
        """Test _remove_device_entities with exception and verify error logging."""
        from unittest.mock import patch

        # Create mock device
        device = Mock(spec=Device)
        device.name = "Test Device"

        # Add the device
        self.manager.devices["test_device_exception"] = device

        with (
            patch(
                "ha_mqtt_publisher.ha_discovery.discovery_manager.logging.error"
            ) as mock_error,
            patch.object(self.manager, "entities") as mock_entities,
        ):
            # Make entities.items() raise an exception to trigger error path
            mock_entities.items.side_effect = Exception(
                "Test exception during entity removal"
            )

            # Call the internal method that should handle exceptions
            try:
                # This might call through remove_device which calls _remove_device_entities
                self.manager.remove_device("test_device_exception")
            except Exception:
                pass

            # Verify error was logged
            mock_error.assert_called_once()
