"""Tests for MQTTConfig utility class."""

import pytest

from ha_mqtt_publisher.config import MQTTConfig


class TestMQTTConfigBuildConfig:
    """Test MQTTConfig.build_config() functionality."""

    def test_minimal_config(self):
        """Test building minimal valid configuration."""
        config = MQTTConfig.build_config(broker_url="test.broker.com")

        assert config["broker_url"] == "test.broker.com"
        assert config["broker_port"] == 1883  # Default
        assert config["client_id"] == "mqtt_client"  # Default
        assert config["security"] == "none"  # Default
        assert config["max_retries"] == 3  # Default
        assert "auth" not in config  # No auth by default

    def test_port_conversion(self):
        """Test automatic port type conversion."""
        config = MQTTConfig.build_config(
            broker_url="test.broker.com",
            broker_port="8883",  # String should be converted
        )

        assert config["broker_port"] == 8883
        assert isinstance(config["broker_port"], int)

    def test_max_retries_conversion(self):
        """Test max_retries type conversion."""
        config = MQTTConfig.build_config(
            broker_url="test.broker.com",
            max_retries="5",  # String should be converted
        )

        assert config["max_retries"] == 5
        assert isinstance(config["max_retries"], int)

    def test_auth_configuration(self):
        """Test authentication configuration."""
        config = MQTTConfig.build_config(
            broker_url="test.broker.com", username="testuser", password="testpass"
        )

        assert config["auth"]["username"] == "testuser"
        assert config["auth"]["password"] == "testpass"

    def test_tls_configuration(self):
        """Test TLS configuration."""
        tls_config = {"ca_cert": "/path/to/ca.pem", "verify": True}

        config = MQTTConfig.build_config(broker_url="test.broker.com", tls=tls_config)

        assert config["tls"] == tls_config

    def test_last_will_configuration(self):
        """Test Last Will and Testament configuration."""
        lwt_config = {
            "topic": "device/status",
            "payload": "offline",
            "qos": 1,
            "retain": True,
        }

        config = MQTTConfig.build_config(
            broker_url="test.broker.com", last_will=lwt_config
        )

        assert config["last_will"] == lwt_config

    def test_missing_broker_url(self):
        """Test error when broker_url is missing."""
        with pytest.raises(ValueError, match="broker_url is required"):
            MQTTConfig.build_config()

    def test_complete_configuration(self):
        """Test building complete configuration with all options."""
        tls_config = {"verify": True}
        lwt_config = {
            "topic": "device/status",
            "payload": "offline",
            "qos": 1,
            "retain": True,
        }

        config = MQTTConfig.build_config(
            broker_url="mqtt.example.com",
            broker_port="8883",
            client_id="test_client",
            security="username",
            username="user",
            password="pass",
            tls=tls_config,
            max_retries="5",
            last_will=lwt_config,
        )

        assert config["broker_url"] == "mqtt.example.com"
        assert config["broker_port"] == 8883
        assert config["client_id"] == "test_client"
        assert config["security"] == "username"
        assert config["auth"]["username"] == "user"
        assert config["auth"]["password"] == "pass"
        assert config["tls"] == tls_config
        assert config["max_retries"] == 5
        assert config["last_will"] == lwt_config


class TestMQTTConfigFromDict:
    """Test MQTTConfig.from_dict() functionality."""

    def test_basic_from_dict(self):
        """Test building config from nested dictionary."""
        config_dict = {
            "mqtt": {
                "broker_url": "mqtt.example.com",
                "broker_port": 8883,
                "client_id": "my_client",
                "security": "username",
                "auth": {"username": "user", "password": "pass"},
            }
        }

        config = MQTTConfig.from_dict(config_dict)

        assert config["broker_url"] == "mqtt.example.com"
        assert config["broker_port"] == 8883
        assert config["client_id"] == "my_client"
        assert config["security"] == "username"
        assert config["auth"]["username"] == "user"
        assert config["auth"]["password"] == "pass"

    def test_empty_dict(self):
        """Test handling empty dictionary."""
        with pytest.raises(ValueError, match="broker_url is required"):
            MQTTConfig.from_dict({})

    def test_missing_mqtt_section(self):
        """Test handling missing mqtt section."""
        config_dict = {"other": {"key": "value"}}

        with pytest.raises(ValueError, match="broker_url is required"):
            MQTTConfig.from_dict(config_dict)

    def test_tls_and_last_will_from_dict(self):
        """Test TLS and Last Will configuration from dict."""
        config_dict = {
            "mqtt": {
                "broker_url": "mqtt.example.com",
                "broker_port": 8883,
                "client_id": "my_client",
                "tls": {"verify": True, "ca_cert": "/path/to/ca.pem"},
                "last_will": {
                    "topic": "device/status",
                    "payload": "offline",
                    "qos": 1,
                    "retain": True,
                },
            }
        }

        config = MQTTConfig.from_dict(config_dict)

        assert config["tls"]["verify"] is True
        assert config["tls"]["ca_cert"] == "/path/to/ca.pem"
        assert config["last_will"]["topic"] == "device/status"
        assert config["last_will"]["payload"] == "offline"


class TestMQTTConfigValidateConfig:
    """Test MQTTConfig.validate_config() functionality."""

    def test_valid_minimal_config(self):
        """Test validation of minimal valid config."""
        config = {
            "broker_url": "mqtt.example.com",
            "broker_port": 1883,
            "client_id": "test_client",
            "security": "none",
        }

        # Should not raise any exception
        MQTTConfig.validate_config(config)

    def test_missing_broker_url(self):
        """Test validation error for missing broker_url."""
        config = {"broker_port": 1883, "client_id": "test_client"}

        with pytest.raises(ValueError, match="broker_url is required"):
            MQTTConfig.validate_config(config)

    def test_invalid_port(self):
        """Test validation error for invalid port."""
        config = {
            "broker_url": "mqtt.example.com",
            "broker_port": 70000,  # Invalid port
            "client_id": "test_client",
        }

        with pytest.raises(ValueError, match="broker_port must be integer 1-65535"):
            MQTTConfig.validate_config(config)

    def test_missing_client_id(self):
        """Test validation error for missing client_id."""
        config = {"broker_url": "mqtt.example.com", "broker_port": 1883}

        with pytest.raises(ValueError, match="client_id is required"):
            MQTTConfig.validate_config(config)

    def test_username_security_missing_auth(self):
        """Test validation error for username security without auth."""
        config = {
            "broker_url": "mqtt.example.com",
            "broker_port": 1883,
            "client_id": "test_client",
            "security": "username",
        }

        with pytest.raises(
            ValueError, match="username and password required when security='username'"
        ):
            MQTTConfig.validate_config(config)

    def test_tls_security_missing_tls_config(self):
        """Test validation error for TLS security without TLS config."""
        config = {
            "broker_url": "mqtt.example.com",
            "broker_port": 8883,
            "client_id": "test_client",
            "security": "tls",
            "auth": {"username": "user", "password": "pass"},
        }

        with pytest.raises(
            ValueError, match="TLS configuration required when security='tls'"
        ):
            MQTTConfig.validate_config(config)

    def test_tls_client_cert_missing_certs(self):
        """Test validation error for TLS client cert security without client certs."""
        config = {
            "broker_url": "mqtt.example.com",
            "broker_port": 8884,
            "client_id": "test_client",
            "security": "tls_with_client_cert",
            "auth": {"username": "user", "password": "pass"},
            "tls": {
                "ca_cert": "/path/to/ca.pem"
                # Missing client_cert and client_key
            },
        }

        with pytest.raises(
            ValueError,
            match="client_cert and client_key required for tls_with_client_cert",
        ):
            MQTTConfig.validate_config(config)

    def test_tls_port_mismatch_warning(self):
        """Test warning for TLS enabled with non-TLS port."""
        config = {
            "broker_url": "mqtt.example.com",
            "broker_port": 1883,  # Non-TLS port
            "client_id": "test_client",
            "security": "none",
            "tls": {"verify": True},  # TLS enabled
        }

        with pytest.raises(ValueError, match="TLS enabled but using non-TLS port 1883"):
            MQTTConfig.validate_config(config)

    def test_no_tls_port_mismatch_warning(self):
        """Test warning for TLS disabled with TLS port."""
        config = {
            "broker_url": "mqtt.example.com",
            "broker_port": 8883,  # TLS port
            "client_id": "test_client",
            "security": "none",
            # No TLS config
        }

        with pytest.raises(ValueError, match="TLS disabled but using TLS port 8883"):
            MQTTConfig.validate_config(config)

    def test_multiple_validation_errors(self):
        """Test multiple validation errors in one call."""
        config = {
            "broker_port": 70000,  # Invalid port
            "security": "username",
            # Missing broker_url, client_id, and auth
        }

        with pytest.raises(ValueError) as exc_info:
            MQTTConfig.validate_config(config)

        error_message = str(exc_info.value)
        assert "broker_url is required" in error_message
        assert "broker_port must be integer 1-65535" in error_message
        assert "client_id is required" in error_message
        assert "username and password required" in error_message
