"""Tests for one-time discovery publication mode."""

import json
import os
import tempfile
from unittest.mock import Mock, patch

from mqtt_publisher.ha_discovery.publisher import (
    clear_discovery_state,
    force_republish_discovery,
    publish_discovery_configs,
)


class TestOneTimeDiscoveryMode:
    """Test one-time discovery publication functionality."""

    def setup_method(self):
        """Set up test environment with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, "test_discovery_state.json")

    def teardown_method(self):
        """Clean up test environment."""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_first_time_discovery_publication(self):
        """Test that discovery configs are published on first run."""
        # Mock config
        mock_config = Mock()
        mock_config.get.side_effect = lambda key, default=None: {
            "home_assistant.enabled": True,
            "home_assistant.discovery_state_file": self.state_file,
            "mqtt.topics.status": "test/status",
        }.get(key, default)

        # Mock publisher
        mock_publisher = Mock()

        # Mock entities
        mock_entity = Mock()
        mock_entity.get_config_topic.return_value = "homeassistant/sensor/test/config"
        mock_entity.get_config_payload.return_value = {"name": "Test Sensor"}

        with patch("builtins.print"):
            publish_discovery_configs(
                config=mock_config,
                publisher=mock_publisher,
                entities=[mock_entity],
                one_time_mode=True,
            )

        # Should publish the config
        mock_publisher.publish.assert_called_once()

        # Should create state file
        assert os.path.exists(self.state_file)

        # Check state file content
        with open(self.state_file) as f:
            state = json.load(f)
        assert "homeassistant/sensor/test/config" in state["published_topics"]
        assert "last_updated" in state

    def test_skip_already_published_discovery(self):
        """Test that already published configs are skipped in one-time mode."""
        # Create existing state file
        state = {
            "published_topics": ["homeassistant/sensor/test/config"],
            "last_updated": "2024-01-01T12:00:00",
        }
        with open(self.state_file, "w") as f:
            json.dump(state, f)

        # Mock config
        mock_config = Mock()
        mock_config.get.side_effect = lambda key, default=None: {
            "home_assistant.enabled": True,
            "home_assistant.discovery_state_file": self.state_file,
            "mqtt.topics.status": "test/status",
        }.get(key, default)

        # Mock publisher
        mock_publisher = Mock()

        # Mock entities
        mock_entity = Mock()
        mock_entity.get_config_topic.return_value = "homeassistant/sensor/test/config"
        mock_entity.get_config_payload.return_value = {"name": "Test Sensor"}

        with patch("builtins.print") as mock_print:
            publish_discovery_configs(
                config=mock_config,
                publisher=mock_publisher,
                entities=[mock_entity],
                one_time_mode=True,
            )

        # Should NOT publish the config
        mock_publisher.publish.assert_not_called()

        # Should print skip message
        mock_print.assert_any_call(
            "Skipping already published discovery config: homeassistant/sensor/test/config"
        )

    def test_mixed_published_and_new_discovery(self):
        """Test publishing only new configs when some are already published."""
        # Create existing state file with one published topic
        state = {
            "published_topics": ["homeassistant/sensor/test1/config"],
            "last_updated": "2024-01-01T12:00:00",
        }
        with open(self.state_file, "w") as f:
            json.dump(state, f)

        # Mock config
        mock_config = Mock()
        mock_config.get.side_effect = lambda key, default=None: {
            "home_assistant.enabled": True,
            "home_assistant.discovery_state_file": self.state_file,
            "mqtt.topics.status": "test/status",
        }.get(key, default)

        # Mock publisher
        mock_publisher = Mock()

        # Mock entities - one already published, one new
        mock_entity1 = Mock()
        mock_entity1.get_config_topic.return_value = "homeassistant/sensor/test1/config"
        mock_entity1.get_config_payload.return_value = {"name": "Test Sensor 1"}

        mock_entity2 = Mock()
        mock_entity2.get_config_topic.return_value = "homeassistant/sensor/test2/config"
        mock_entity2.get_config_payload.return_value = {"name": "Test Sensor 2"}

        with patch("builtins.print"):
            publish_discovery_configs(
                config=mock_config,
                publisher=mock_publisher,
                entities=[mock_entity1, mock_entity2],
                one_time_mode=True,
            )

        # Should publish only the new config
        mock_publisher.publish.assert_called_once()
        call_args = mock_publisher.publish.call_args
        assert call_args[1]["topic"] == "homeassistant/sensor/test2/config"

        # Check final state file
        with open(self.state_file) as f:
            final_state = json.load(f)
        assert "homeassistant/sensor/test1/config" in final_state["published_topics"]
        assert "homeassistant/sensor/test2/config" in final_state["published_topics"]

    def test_normal_mode_always_publishes(self):
        """Test that normal mode (one_time_mode=False) always publishes."""
        # Create existing state file
        state = {
            "published_topics": ["homeassistant/sensor/test/config"],
            "last_updated": "2024-01-01T12:00:00",
        }
        with open(self.state_file, "w") as f:
            json.dump(state, f)

        # Mock config
        mock_config = Mock()
        mock_config.get.side_effect = lambda key, default=None: {
            "home_assistant.enabled": True,
            "home_assistant.discovery_state_file": self.state_file,
            "mqtt.topics.status": "test/status",
        }.get(key, default)

        # Mock publisher
        mock_publisher = Mock()

        # Mock entities
        mock_entity = Mock()
        mock_entity.get_config_topic.return_value = "homeassistant/sensor/test/config"
        mock_entity.get_config_payload.return_value = {"name": "Test Sensor"}

        publish_discovery_configs(
            config=mock_config,
            publisher=mock_publisher,
            entities=[mock_entity],
            one_time_mode=False,  # Normal mode
        )

        # Should publish even though already in state file
        mock_publisher.publish.assert_called_once()

    def test_clear_discovery_state(self):
        """Test clearing the discovery state file."""
        # Create state file
        state = {
            "published_topics": ["homeassistant/sensor/test/config"],
            "last_updated": "2024-01-01T12:00:00",
        }
        with open(self.state_file, "w") as f:
            json.dump(state, f)

        # Mock config
        mock_config = Mock()
        mock_config.get.return_value = self.state_file

        with patch("builtins.print") as mock_print:
            clear_discovery_state(mock_config)

        # State file should be deleted
        assert not os.path.exists(self.state_file)
        mock_print.assert_called_with(
            f"Cleared discovery state file: {self.state_file}"
        )

    def test_clear_nonexistent_discovery_state(self):
        """Test clearing discovery state when file doesn't exist."""
        # Mock config
        mock_config = Mock()
        mock_config.get.return_value = self.state_file

        with patch("builtins.print") as mock_print:
            clear_discovery_state(mock_config)

        # Should handle gracefully
        mock_print.assert_called_with("Discovery state file does not exist")

    def test_force_republish_discovery(self):
        """Test force republishing all discovery configs."""
        # Create state file
        state = {
            "published_topics": ["homeassistant/sensor/test/config"],
            "last_updated": "2024-01-01T12:00:00",
        }
        with open(self.state_file, "w") as f:
            json.dump(state, f)

        # Mock config
        mock_config = Mock()
        mock_config.get.side_effect = lambda key, default=None: {
            "home_assistant.enabled": True,
            "home_assistant.discovery_state_file": self.state_file,
            "mqtt.topics.status": "test/status",
        }.get(key, default)

        # Mock publisher
        mock_publisher = Mock()

        # Mock entities
        mock_entity = Mock()
        mock_entity.get_config_topic.return_value = "homeassistant/sensor/test/config"
        mock_entity.get_config_payload.return_value = {"name": "Test Sensor"}

        with patch("builtins.print"):
            force_republish_discovery(
                config=mock_config, publisher=mock_publisher, entities=[mock_entity]
            )

        # Should clear state file and publish
        assert not os.path.exists(self.state_file)
        mock_publisher.publish.assert_called_once()

    def test_invalid_state_file_handling(self):
        """Test handling of corrupted state file."""
        # Create corrupted state file
        with open(self.state_file, "w") as f:
            f.write("invalid json content")

        # Mock config
        mock_config = Mock()
        mock_config.get.side_effect = lambda key, default=None: {
            "home_assistant.enabled": True,
            "home_assistant.discovery_state_file": self.state_file,
            "mqtt.topics.status": "test/status",
        }.get(key, default)

        # Mock publisher
        mock_publisher = Mock()

        # Mock entities
        mock_entity = Mock()
        mock_entity.get_config_topic.return_value = "homeassistant/sensor/test/config"
        mock_entity.get_config_payload.return_value = {"name": "Test Sensor"}

        # Should handle corrupted file gracefully
        publish_discovery_configs(
            config=mock_config,
            publisher=mock_publisher,
            entities=[mock_entity],
            one_time_mode=True,
        )

        # Should still publish (treating as first time)
        mock_publisher.publish.assert_called_once()

    def test_state_file_write_permission_error(self):
        """Test handling of permission errors when writing state file."""
        # Mock config
        mock_config = Mock()
        mock_config.get.side_effect = lambda key, default=None: {
            "home_assistant.enabled": True,
            "home_assistant.discovery_state_file": "/invalid/path/state.json",
            "mqtt.topics.status": "test/status",
        }.get(key, default)

        # Mock publisher
        mock_publisher = Mock()

        # Mock entities
        mock_entity = Mock()
        mock_entity.get_config_topic.return_value = "homeassistant/sensor/test/config"
        mock_entity.get_config_payload.return_value = {"name": "Test Sensor"}

        with patch("builtins.print") as mock_print:
            # Should handle permission error gracefully
            publish_discovery_configs(
                config=mock_config,
                publisher=mock_publisher,
                entities=[mock_entity],
                one_time_mode=True,
            )

        # Should still publish
        mock_publisher.publish.assert_called_once()

        # Should print warning about state file write failure
        warning_calls = [
            call
            for call in mock_print.call_args_list
            if "Warning: Could not save discovery state" in str(call)
        ]
        assert len(warning_calls) > 0

    def test_default_state_file_location(self):
        """Test using default state file location when not configured."""
        # Mock config without explicit state file
        mock_config = Mock()
        mock_config.get.side_effect = lambda key, default=None: {
            "home_assistant.enabled": True,
            "mqtt.topics.status": "test/status",
        }.get(key, default)

        # Mock publisher
        mock_publisher = Mock()

        # Mock entities
        mock_entity = Mock()
        mock_entity.get_config_topic.return_value = "homeassistant/sensor/test/config"
        mock_entity.get_config_payload.return_value = {"name": "Test Sensor"}

        with patch("builtins.print"):
            publish_discovery_configs(
                config=mock_config,
                publisher=mock_publisher,
                entities=[mock_entity],
                one_time_mode=True,
            )

        # Should use default state file name
        assert os.path.exists(".ha_discovery_state.json")

        # Clean up
        if os.path.exists(".ha_discovery_state.json"):
            os.remove(".ha_discovery_state.json")
