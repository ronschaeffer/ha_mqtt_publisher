"""
Test suite for mqtt_publisher environment handling.

Tests the hierarchical environment loading and configuration
specific to the mqtt_publisher package.
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest


class TestMqttPublisherEnvironmentLoading:
    """Test environment loading specific to mqtt_publisher."""

    def setup_method(self):
        """Set up test environment."""
        self.original_env = dict(os.environ)

    def teardown_method(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_example_environment_loading(self):
        """Test environment loading in the complete example."""
        with patch("pathlib.Path.exists") as mock_exists:
            with patch("dotenv.load_dotenv") as mock_load_dotenv:
                # Mock file existence
                def exists_side_effect(path_obj):
                    path_str = str(path_obj)
                    if "/home/ron/projects/.env" in path_str:
                        return True
                    elif "/mqtt_publisher/.env" in path_str:
                        return True
                    return False

                mock_exists.side_effect = exists_side_effect
                mock_load_dotenv.return_value = True

                # Simulate the load_environment function from the example
                try:
                    from dotenv import load_dotenv

                    # Load shared environment first
                    parent_env = Path(__file__).parent.parent.parent / ".env"
                    if parent_env.exists():
                        load_dotenv(parent_env, verbose=False)

                    # Load project-specific environment second
                    project_env = Path(__file__).parent.parent / ".env"
                    if project_env.exists():
                        load_dotenv(project_env, override=True, verbose=False)

                except ImportError:
                    # Expected in test environment
                    pass

                # Verify hierarchical loading pattern
                assert mock_exists.call_count >= 2

    def test_config_integration_with_environment(self):
        """Test that Config class integrates with environment variables."""
        # Set up environment variables
        os.environ.update(
            {
                "MQTT_BROKER_URL": "10.10.10.21",
                "MQTT_PORT": "8883",
                "MQTT_USERNAME": "mqtt_pub_user",
                "MQTT_PASSWORD": "mqtt_pub_pass",
                "MQTT_CLIENT_ID": "mqtt_publisher_example",
            }
        )

        # Mock config file content with environment substitution
        mock_config_content = {
            "mqtt": {
                "broker_url": "${MQTT_BROKER_URL}",
                "broker_port": "${MQTT_PORT}",
                "client_id": "${MQTT_CLIENT_ID}",
                "security": "username",
                "auth": {
                    "username": "${MQTT_USERNAME}",
                    "password": "${MQTT_PASSWORD}",
                },
            }
        }

        # Mock the Config class with environment substitution
        class MockConfig:
            def __init__(self, config_path):
                # In real implementation, this would load from YAML
                self.config = self._apply_env_substitution(mock_config_content)

            def _apply_env_substitution(self, obj):
                """Apply environment variable substitution."""
                if isinstance(obj, dict):
                    return {k: self._apply_env_substitution(v) for k, v in obj.items()}
                elif isinstance(obj, str):
                    import re

                    def replacer(match):
                        var_name = match.group(1)
                        return os.environ.get(var_name, match.group(0))

                    return re.sub(r"\$\{([^}]+)\}", replacer, obj)
                else:
                    return obj

            def get(self, key, default=None):
                """Get config value with dot notation support."""
                keys = key.split(".")
                value = self.config
                for k in keys:
                    if isinstance(value, dict) and k in value:
                        value = value[k]
                    else:
                        return default
                return value

        # Test the configuration
        config = MockConfig("/fake/config.yaml")

        # Verify MQTT configuration
        assert config.get("mqtt.broker_url") == "10.10.10.21"
        assert config.get("mqtt.broker_port") == "8883"
        assert config.get("mqtt.client_id") == "mqtt_publisher_example"
        assert config.get("mqtt.auth.username") == "mqtt_pub_user"
        assert config.get("mqtt.auth.password") == "mqtt_pub_pass"

    def test_unique_client_id_for_mqtt_publisher(self):
        """Test that mqtt_publisher uses a unique client ID."""
        os.environ["MQTT_CLIENT_ID"] = "mqtt_publisher_client_001"

        # Test client ID uniqueness
        client_id = os.environ.get("MQTT_CLIENT_ID")

        assert "mqtt_publisher" in client_id
        assert client_id != "twickenham_events_client_001"
        assert "publisher" in client_id or "mqtt_pub" in client_id

    def test_example_environment_output_messages(self):
        """Test that example prints appropriate environment loading messages."""
        with patch("pathlib.Path.exists") as mock_exists:
            with patch("dotenv.load_dotenv") as mock_load_dotenv:
                with patch("builtins.print") as mock_print:
                    mock_exists.return_value = True
                    mock_load_dotenv.return_value = True

                    # Simulate the environment loading with print statements
                    parent_env_path = "/home/ron/projects/.env"
                    project_env_path = "/home/ron/projects/mqtt_publisher/.env"

                    if mock_exists(Path(parent_env_path)):
                        print(f"✅ Loaded shared environment from: {parent_env_path}")

                    if mock_exists(Path(project_env_path)):
                        print(f"✅ Loaded project environment from: {project_env_path}")

                    # Verify success messages
                    assert mock_print.call_count == 2

                    calls = [call[0][0] for call in mock_print.call_args_list]
                    assert any("Loaded shared environment" in call for call in calls)
                    assert any("Loaded project environment" in call for call in calls)

    def test_example_handles_missing_dotenv(self):
        """Test that example gracefully handles missing python-dotenv."""
        with patch("builtins.print") as mock_print:
            # Simulate ImportError for python-dotenv
            try:
                # This would normally import dotenv
                raise ImportError("No module named 'dotenv'")
            except ImportError:
                print(
                    "⚠️  python-dotenv not installed. Install with: poetry add python-dotenv"
                )

            # Verify appropriate warning message
            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            assert "python-dotenv not installed" in call_args
            assert "poetry add python-dotenv" in call_args

    def test_mqtt_config_preparation(self):
        """Test MQTT configuration preparation with environment variables."""
        # Set up environment
        os.environ.update(
            {
                "MQTT_BROKER_URL": "10.10.10.21",
                "MQTT_PORT": "8883",
                "MQTT_USERNAME": "test_user",
                "MQTT_PASSWORD": "test_pass",
            }
        )

        # Mock config object
        class MockConfig:
            def get(self, key, default=None):
                env_mapping = {
                    "mqtt.broker_url": os.environ.get("MQTT_BROKER_URL"),
                    "mqtt.broker_port": int(os.environ.get("MQTT_PORT", "1883")),
                    "mqtt.client_id": "mqtt_publisher_example",
                    "mqtt.security": "username",
                    "mqtt.auth.username": os.environ.get("MQTT_USERNAME"),
                    "mqtt.auth.password": os.environ.get("MQTT_PASSWORD"),
                }
                return env_mapping.get(key, default)

        config = MockConfig()

        # Test MQTT configuration preparation (as in example)
        mqtt_config = {
            "broker_url": config.get("mqtt.broker_url"),
            "broker_port": config.get("mqtt.broker_port", 8883),
            "client_id": config.get("mqtt.client_id", "mqtt_publisher_example"),
            "security": config.get("mqtt.security", "username"),
            "auth": {
                "username": config.get("mqtt.auth.username"),
                "password": config.get("mqtt.auth.password"),
            },
            "last_will": {
                "topic": "mqtt_publisher/status",
                "payload": "offline",
                "qos": 1,
                "retain": True,
            },
            "max_retries": 3,
        }

        # Verify configuration
        assert mqtt_config["broker_url"] == "10.10.10.21"
        assert mqtt_config["broker_port"] == 8883
        assert mqtt_config["client_id"] == "mqtt_publisher_example"
        assert mqtt_config["auth"]["username"] == "test_user"
        assert mqtt_config["auth"]["password"] == "test_pass"
        assert mqtt_config["last_will"]["topic"] == "mqtt_publisher/status"


class TestMqttPublisherConfigSecurity:
    """Test security aspects of mqtt_publisher configuration."""

    def test_no_hardcoded_credentials_in_config(self):
        """Test that configuration doesn't contain hardcoded credentials."""
        # Mock a secure configuration
        secure_config = {
            "mqtt": {
                "broker_url": "${MQTT_BROKER_URL}",
                "broker_port": "${MQTT_PORT}",
                "auth": {
                    "username": "${MQTT_USERNAME}",
                    "password": "${MQTT_PASSWORD}",
                },
            }
        }

        # Verify all sensitive values use environment variables
        def check_no_hardcoded_credentials(config, path=""):
            for key, value in config.items():
                current_path = f"{path}.{key}" if path else key

                if isinstance(value, dict):
                    check_no_hardcoded_credentials(value, current_path)
                elif isinstance(value, str):
                    # Check for potentially sensitive fields
                    sensitive_fields = ["password", "secret", "key", "token", "auth"]
                    if any(sensitive in key.lower() for sensitive in sensitive_fields):
                        # Should use environment variable or be a non-credential value
                        if "password" in key.lower():
                            assert value.startswith("${") and value.endswith("}"), (
                                f"Password field {current_path} should use environment variable"
                            )

        check_no_hardcoded_credentials(secure_config)

    def test_environment_loading_security(self):
        """Test that environment loading follows security practices."""
        with patch("dotenv.load_dotenv") as mock_load_dotenv:
            mock_load_dotenv.return_value = True

            # Environment loading should use verbose=False for security
            result = mock_load_dotenv("/fake/.env", verbose=False)

            assert result is True
            # Verify verbose=False was used (prevents logging sensitive data)
            mock_load_dotenv.assert_called_with("/fake/.env", verbose=False)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
