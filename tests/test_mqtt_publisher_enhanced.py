"""Tests for enhanced MQTTPublisher functionality."""

from unittest.mock import Mock, patch

import pytest

from mqtt_publisher import MQTTConfig, MQTTPublisher


class TestMQTTPublisherPortConversion:
    """Test port type conversion functionality."""

    def test_string_port_conversion(self):
        """Test automatic port conversion from string to int."""
        publisher = MQTTPublisher(
            broker_url="localhost",
            broker_port="1883",  # String port
            client_id="test",
        )

        assert publisher.broker_port == 1883
        assert isinstance(publisher.broker_port, int)

    def test_int_port_unchanged(self):
        """Test that integer ports remain unchanged."""
        publisher = MQTTPublisher(
            broker_url="localhost",
            broker_port=8883,  # Integer port
            client_id="test",
        )

        assert publisher.broker_port == 8883
        assert isinstance(publisher.broker_port, int)

    def test_none_port_default(self):
        """Test that None port defaults to 1883."""
        publisher = MQTTPublisher(
            broker_url="localhost", broker_port=None, client_id="test"
        )

        assert publisher.broker_port == 1883

    def test_invalid_string_port(self):
        """Test error for invalid string port."""
        with pytest.raises(ValueError, match="Invalid port value: invalid"):
            MQTTPublisher(
                broker_url="localhost", broker_port="invalid", client_id="test"
            )


class TestMQTTPublisherConfigDict:
    """Test MQTTPublisher with config dictionary."""

    def test_config_dict_basic(self):
        """Test using config dictionary for initialization."""
        config = {
            "broker_url": "mqtt.example.com",
            "broker_port": 8883,
            "client_id": "test_client",
            "security": "username",
            "auth": {"username": "user", "password": "pass"},
            "max_retries": 5,
        }

        publisher = MQTTPublisher(config=config)

        assert publisher.broker_url == "mqtt.example.com"
        assert publisher.broker_port == 8883
        assert publisher.client_id == "test_client"
        assert publisher.security == "username"
        assert publisher.auth["username"] == "user"
        assert publisher.auth["password"] == "pass"
        assert publisher.max_retries == 5

    def test_config_dict_with_string_port(self):
        """Test config dict with string port conversion."""
        config = {
            "broker_url": "mqtt.example.com",
            "broker_port": "8883",  # String port
            "client_id": "test_client",
        }

        publisher = MQTTPublisher(config=config)

        assert publisher.broker_port == 8883
        assert isinstance(publisher.broker_port, int)

    def test_config_dict_overrides_params(self):
        """Test that config dict takes precedence over individual parameters."""
        config = {
            "broker_url": "config.example.com",
            "broker_port": 8883,
            "client_id": "config_client",
        }

        # These parameters should be ignored when config is provided
        publisher = MQTTPublisher(
            broker_url="param.example.com",
            broker_port=1883,
            client_id="param_client",
            config=config,
        )

        assert publisher.broker_url == "config.example.com"
        assert publisher.broker_port == 8883
        assert publisher.client_id == "config_client"

    def test_mqtt_config_integration(self):
        """Test integration with MQTTConfig.build_config()."""
        config = MQTTConfig.build_config(
            broker_url="mqtt.example.com",
            broker_port="8883",  # String should be converted
            client_id="test_client",
            security="username",
            username="user",
            password="pass",
        )

        publisher = MQTTPublisher(config=config)

        assert publisher.broker_url == "mqtt.example.com"
        assert publisher.broker_port == 8883
        assert publisher.client_id == "test_client"
        assert publisher.security == "username"
        assert publisher.auth["username"] == "user"
        assert publisher.auth["password"] == "pass"


class TestMQTTPublisherValidation:
    """Test MQTTPublisher configuration validation."""

    def test_missing_broker_url(self):
        """Test validation error for missing broker_url."""
        with pytest.raises(ValueError, match="broker_url is required"):
            MQTTPublisher(broker_url=None, broker_port=1883, client_id="test")

    def test_missing_client_id(self):
        """Test validation error for missing client_id."""
        with pytest.raises(ValueError, match="client_id is required"):
            MQTTPublisher(broker_url="localhost", broker_port=1883, client_id=None)

    def test_invalid_port_range(self):
        """Test validation error for invalid port range."""
        with pytest.raises(ValueError, match="broker_port must be integer 1-65535"):
            MQTTPublisher(broker_url="localhost", broker_port=70000, client_id="test")

    def test_username_security_missing_auth(self):
        """Test validation error for username security without auth."""
        with pytest.raises(ValueError, match="username and password required"):
            MQTTPublisher(
                broker_url="localhost",
                broker_port=1883,
                client_id="test",
                security="username",
            )

    def test_tls_port_warning(self):
        """Test warning for TLS/port mismatch."""
        # This should succeed but log a warning
        publisher = MQTTPublisher(
            broker_url="localhost",
            broker_port=1883,
            client_id="test",
            tls={"verify": True},
        )

        # Publisher should be created successfully despite the warning
        assert publisher.broker_url == "localhost"
        assert publisher.broker_port == 1883
        assert publisher.tls == {"verify": True}

    def test_valid_configuration_passes(self):
        """Test that valid configuration doesn't raise errors."""
        # This should not raise any exceptions
        publisher = MQTTPublisher(
            broker_url="localhost", broker_port=1883, client_id="test", security="none"
        )

        assert publisher.broker_url == "localhost"
        assert publisher.broker_port == 1883
        assert publisher.client_id == "test"


class TestMQTTPublisherErrorHandling:
    """Test enhanced error handling in MQTTPublisher."""

    def test_connection_error_messages(self):
        """Test enhanced connection error messages."""
        publisher = MQTTPublisher(
            broker_url="localhost", broker_port=1883, client_id="test"
        )

        # Test various error codes
        assert "Connection successful" in publisher._get_connection_error_message(0)
        assert "incorrect protocol version" in publisher._get_connection_error_message(
            1
        )
        assert "invalid client identifier" in publisher._get_connection_error_message(2)
        assert "server unavailable" in publisher._get_connection_error_message(3)
        assert "bad username or password" in publisher._get_connection_error_message(4)
        assert "not authorized" in publisher._get_connection_error_message(5)

    def test_tls_port_mismatch_error_message(self):
        """Test specific error message for TLS/port mismatch."""
        publisher = MQTTPublisher(
            broker_url="localhost",
            broker_port=1883,
            client_id="test",
            tls={"verify": True},
        )

        # Mock a connection refused error (code 1) to trigger port guidance
        error_msg = publisher._get_connection_error_message(1)
        assert "TLS enabled but using non-TLS port 1883" in error_msg
        assert "Try port 8883" in error_msg

    def test_no_tls_port_mismatch_error_message(self):
        """Test specific error message for no TLS with TLS port."""
        publisher = MQTTPublisher(
            broker_url="localhost", broker_port=8883, client_id="test"
        )

        # Mock a connection refused error (code 1) to trigger port guidance
        error_msg = publisher._get_connection_error_message(1)
        assert "TLS disabled but using TLS port 8883" in error_msg
        assert "Try port 1883 or enable TLS" in error_msg

    def test_unknown_error_code(self):
        """Test handling of unknown error codes."""
        publisher = MQTTPublisher(
            broker_url="localhost", broker_port=1883, client_id="test"
        )

        error_msg = publisher._get_connection_error_message(99)
        assert "Connection failed with error code: 99" in error_msg


class TestMQTTPublisherSecurityConfiguration:
    """Test security configuration in enhanced MQTTPublisher."""

    @patch("paho.mqtt.client.Client")
    def test_username_security_configuration(self, mock_client_class):
        """Test username security configuration."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        publisher = MQTTPublisher(  # noqa: F841
            broker_url="localhost",
            broker_port=1883,
            client_id="test",
            security="username",
            auth={"username": "user", "password": "pass"},
        )

        mock_client.username_pw_set.assert_called_once_with("user", "pass")

    @patch("paho.mqtt.client.Client")
    def test_tls_security_configuration(self, mock_client_class):
        """Test TLS security configuration."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        tls_config = {"ca_cert": "/path/to/ca.pem", "verify": True}

        publisher = MQTTPublisher(  # noqa: F841
            broker_url="localhost",
            broker_port=8883,
            client_id="test",
            security="tls",
            auth={"username": "user", "password": "pass"},
            tls=tls_config,
        )

        # Should call both username_pw_set and tls_set
        mock_client.username_pw_set.assert_called_once_with("user", "pass")
        mock_client.tls_set.assert_called_once()

    def test_tls_security_missing_config(self):
        """Test error when TLS security is specified without TLS config."""
        with pytest.raises(
            ValueError, match="TLS configuration required when security='tls'"
        ):
            MQTTPublisher(
                broker_url="localhost",
                broker_port=8883,
                client_id="test",
                security="tls",
                auth={"username": "user", "password": "pass"},
                # Missing tls parameter
            )
