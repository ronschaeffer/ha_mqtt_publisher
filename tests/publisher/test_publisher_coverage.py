"""
Focused coverage tests for MQTT Publisher to improve coverage.
These tests target specific uncovered lines without causing infinite loops.
"""

from unittest.mock import patch

import pytest

from mqtt_publisher.publisher import MQTTPublisher


class TestMQTTPublisherCoverage:
    """Test class focusing on improving publisher coverage."""

    def test_convert_port_none(self):
        """Test _convert_port with None returns default port."""
        publisher = MQTTPublisher(broker_url="test.broker.com", client_id="test_client")
        assert publisher._convert_port(None) == 1883

    def test_convert_port_string_valid(self):
        """Test _convert_port with valid string."""
        publisher = MQTTPublisher(broker_url="test.broker.com", client_id="test_client")
        assert publisher._convert_port("8883") == 8883

    def test_convert_port_string_invalid(self):
        """Test _convert_port with invalid string raises ValueError."""
        publisher = MQTTPublisher(broker_url="test.broker.com", client_id="test_client")
        with pytest.raises(ValueError, match="Invalid port value"):
            publisher._convert_port("invalid_port")

    def test_convert_port_integer(self):
        """Test _convert_port with integer returns as-is."""
        publisher = MQTTPublisher(broker_url="test.broker.com", client_id="test_client")
        assert publisher._convert_port(8883) == 8883

    def test_validate_config_missing_broker_url(self):
        """Test validation fails when broker_url is missing."""
        with pytest.raises(ValueError, match="broker_url is required"):
            MQTTPublisher(broker_url=None, client_id="test_client")

    def test_validate_config_invalid_port_range(self):
        """Test validation fails for invalid port range."""
        with pytest.raises(ValueError, match="broker_port must be integer"):
            MQTTPublisher(
                broker_url="test.broker.com",
                broker_port=99999,  # Invalid port
                client_id="test_client",
            )

    def test_validate_config_missing_client_id(self):
        """Test validation fails when client_id is missing."""
        with pytest.raises(ValueError, match="client_id is required"):
            MQTTPublisher(broker_url="test.broker.com", client_id=None)

    def test_validate_config_username_security_missing_auth(self):
        """Test validation fails when username security requires auth."""
        with pytest.raises(ValueError, match="username and password required"):
            MQTTPublisher(
                broker_url="test.broker.com",
                client_id="test_client",
                security="username",
                auth=None,
            )

    def test_validate_config_username_security_missing_password(self):
        """Test validation fails when username security missing password."""
        with pytest.raises(ValueError, match="username and password required"):
            MQTTPublisher(
                broker_url="test.broker.com",
                client_id="test_client",
                security="username",
                auth={"username": "user"},  # Missing password
            )

    def test_validate_config_tls_security_missing_tls_config(self):
        """Test validation fails when TLS security requires TLS config."""
        with pytest.raises(ValueError, match="TLS configuration required"):
            MQTTPublisher(
                broker_url="test.broker.com",
                client_id="test_client",
                security="tls",
                tls=None,
            )

    def test_validate_config_tls_client_cert_missing_certs(self):
        """Test validation fails when client cert security missing cert files."""
        with pytest.raises(ValueError, match="client_cert and client_key required"):
            MQTTPublisher(
                broker_url="test.broker.com",
                client_id="test_client",
                security="tls_with_client_cert",
                tls={"ca_cert": "ca.pem"},  # Missing client_cert and client_key
            )

    @patch("mqtt_publisher.publisher.logging.warning")
    @patch("paho.mqtt.client.Client.tls_insecure_set")
    @patch("paho.mqtt.client.Client.tls_set")
    def test_validate_config_tls_port_warning(
        self, mock_tls_set, mock_tls_insecure, mock_warning
    ):
        """Test validation warns about TLS with non-TLS port."""
        MQTTPublisher(
            broker_url="test.broker.com",
            client_id="test_client",
            broker_port=1883,  # Non-TLS port
            security="tls",
            tls={"ca_cert": "ca.pem"},
        )
        mock_warning.assert_called_once()
        assert "TLS enabled but using non-TLS port 1883" in mock_warning.call_args[0][0]

    @patch("mqtt_publisher.publisher.logging.warning")
    def test_validate_config_non_tls_port_warning(self, mock_warning):
        """Test validation warns about non-TLS with TLS port."""
        MQTTPublisher(
            broker_url="test.broker.com",
            client_id="test_client",
            broker_port=8883,  # TLS port
            security="none",  # No TLS
            tls=None,
        )
        mock_warning.assert_called_once()
        assert "TLS disabled but using TLS port 8883" in mock_warning.call_args[0][0]

    def test_init_with_config_dict(self):
        """Test initialization using config dictionary."""
        config = {
            "broker_url": "test.broker.com",
            "broker_port": "1883",
            "client_id": "test_client",
            "security": "none",
            "max_retries": 5,
            "protocol": "MQTTv5",
            "properties": {"session_expiry_interval": 60},
        }

        publisher = MQTTPublisher(config=config)

        assert publisher.broker_url == "test.broker.com"
        assert publisher.broker_port == 1883
        assert publisher.client_id == "test_client"
        assert publisher.max_retries == 5
        assert publisher.protocol == "MQTTv5"
        assert publisher.properties["session_expiry_interval"] == 60

    def test_init_individual_parameters(self):
        """Test initialization with individual parameters."""
        publisher = MQTTPublisher(
            broker_url="test.broker.com",
            broker_port="8883",
            client_id="test_client",
            protocol="MQTTv5",
            properties={"clean_start": True},
        )

        assert publisher.broker_url == "test.broker.com"
        assert publisher.broker_port == 8883
        assert publisher.client_id == "test_client"
        assert publisher.protocol == "MQTTv5"
        assert publisher.properties["clean_start"] is True

    def test_init_properties_default_empty_dict(self):
        """Test initialization with properties defaults to empty dict."""
        publisher = MQTTPublisher(broker_url="test.broker.com", client_id="test_client")

        assert publisher.properties == {}

    def test_security_none_settings(self):
        """Test security=none sets correct attributes."""
        publisher = MQTTPublisher(
            broker_url="test.broker.com", client_id="test_client", security="none"
        )

        assert publisher.security == "none"
        assert publisher.auth == {}  # Auth defaults to empty dict, not None
        assert publisher.tls is None

    def test_security_username_settings(self):
        """Test security=username sets correct attributes."""
        auth = {"username": "user", "password": "pass"}
        publisher = MQTTPublisher(
            broker_url="test.broker.com",
            client_id="test_client",
            security="username",
            auth=auth,
        )

        assert publisher.security == "username"
        assert publisher.auth == auth

    @patch("paho.mqtt.client.Client.tls_insecure_set")
    @patch("paho.mqtt.client.Client.tls_set")
    def test_security_tls_settings(self, mock_tls_set, mock_tls_insecure):
        """Test security=tls sets correct attributes."""
        tls = {"ca_cert": "ca.pem"}
        publisher = MQTTPublisher(
            broker_url="test.broker.com",
            client_id="test_client",
            security="tls",
            tls=tls,
        )

        assert publisher.security == "tls"
        assert publisher.tls == tls

    def test_init_with_last_will(self):
        """Test initialization with last will testament."""
        last_will = {
            "topic": "status/offline",
            "payload": "offline",
            "qos": 1,
            "retain": True,
        }

        # This should not raise an exception
        publisher = MQTTPublisher(
            broker_url="test.broker.com", client_id="test_client", last_will=last_will
        )

        # Verify publisher was created successfully
        assert publisher.broker_url == "test.broker.com"
        assert publisher.client_id == "test_client"

    def test_max_retries_setting(self):
        """Test max_retries parameter is stored correctly."""
        publisher = MQTTPublisher(
            broker_url="test.broker.com", client_id="test_client", max_retries=10
        )

        assert publisher.max_retries == 10

    def test_get_connection_error_message(self):
        """Test _get_connection_error_message for different error codes."""
        publisher = MQTTPublisher(broker_url="test.broker.com", client_id="test_client")

        # Test known error codes (based on actual implementation)
        assert "protocol version" in publisher._get_connection_error_message(1)
        assert "identifier rejected" in publisher._get_connection_error_message(2)
        assert "server unavailable" in publisher._get_connection_error_message(3)
        assert "username or password" in publisher._get_connection_error_message(4)
        assert "not authorized" in publisher._get_connection_error_message(5)

        # Test unknown error code
        error_msg = publisher._get_connection_error_message(99)
        assert "Unknown connection error: 99" in error_msg
