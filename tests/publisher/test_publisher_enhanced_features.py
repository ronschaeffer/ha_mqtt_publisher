"""Tests for enhanced MQTT Publisher features."""

import logging
from unittest.mock import Mock, patch

import pytest

from mqtt_publisher.publisher import MQTTPublisher


class TestPublisherEnhancedFeatures:
    """Test enhanced features: default QoS/retain, logging, loop management."""

    def test_default_qos_retain_settings(self):
        """Test default QoS and retain settings."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
            "default_qos": 1,
            "default_retain": True,
        }

        publisher = MQTTPublisher(**config)

        assert publisher.default_qos == 1
        assert publisher.default_retain

    def test_default_qos_validation(self):
        """Test validation of default QoS values."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
            "default_qos": 3,  # Invalid QoS
        }

        with pytest.raises(ValueError, match="default_qos must be 0, 1, or 2"):
            MQTTPublisher(**config)

    def test_default_retain_validation(self):
        """Test validation of default retain values."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
            "default_retain": "invalid",  # Invalid retain
        }

        with pytest.raises(ValueError, match="default_retain must be boolean"):
            MQTTPublisher(**config)

    def test_publish_uses_defaults(self):
        """Test that publish uses default QoS and retain when not specified."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
            "default_qos": 2,
            "default_retain": True,
        }

        publisher = MQTTPublisher(**config)
        publisher._connected = True

        # Mock the client
        mock_client = Mock()
        publisher.client = mock_client
        mock_client.publish.return_value = Mock(rc=0)  # Success

        # Publish without specifying QoS/retain
        publisher.publish("test/topic", "test payload")

        # Should use defaults
        mock_client.publish.assert_called_once_with(
            "test/topic", "test payload", qos=2, retain=True
        )

    def test_publish_overrides_defaults(self):
        """Test that explicit QoS/retain values override defaults."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
            "default_qos": 2,
            "default_retain": True,
        }

        publisher = MQTTPublisher(**config)
        publisher._connected = True

        # Mock the client
        mock_client = Mock()
        publisher.client = mock_client
        mock_client.publish.return_value = Mock(rc=0)  # Success

        # Publish with explicit QoS/retain
        publisher.publish("test/topic", "test payload", qos=0, retain=False)

        # Should use explicit values
        mock_client.publish.assert_called_once_with(
            "test/topic", "test payload", qos=0, retain=False
        )

    def test_enhanced_logging_configuration(self):
        """Test enhanced logging configuration."""
        logging_config = {
            "connection_level": "DEBUG",
            "publish_level": "WARNING",
            "discovery_level": "ERROR",
            "topic_specific": {"sensors/*": "DEBUG", "status": "INFO"},
        }

        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
            "logging_config": logging_config,
        }

        publisher = MQTTPublisher(**config)

        # Check that loggers are set up
        assert hasattr(publisher, "connection_logger")
        assert hasattr(publisher, "publish_logger")
        assert hasattr(publisher, "discovery_logger")
        assert hasattr(publisher, "topic_loggers")

        # Check logging levels
        assert publisher.connection_logger.level == logging.DEBUG
        assert publisher.publish_logger.level == logging.WARNING
        assert publisher.discovery_logger.level == logging.ERROR

    def test_topic_specific_logging(self):
        """Test topic-specific logging configuration."""
        logging_config = {"topic_specific": {"sensors/*": "DEBUG", "status": "INFO"}}

        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
            "logging_config": logging_config,
        }

        publisher = MQTTPublisher(**config)

        # Test exact match
        status_logger = publisher._get_topic_logger("status")
        assert status_logger.level == logging.INFO

        # Test wildcard match
        sensor_logger = publisher._get_topic_logger("sensors/temperature")
        assert sensor_logger.level == logging.DEBUG

        # Test no match (should return publish_logger)
        default_logger = publisher._get_topic_logger("other/topic")
        assert default_logger == publisher.publish_logger

    def test_loop_management_methods(self):
        """Test loop management methods."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
        }

        publisher = MQTTPublisher(**config)

        # Mock the client
        mock_client = Mock()
        publisher.client = mock_client

        # Test loop_start
        publisher.loop_start()
        mock_client.loop_start.assert_called_once()

        # Test loop_stop
        publisher.loop_stop()
        mock_client.loop_stop.assert_called_once()

    def test_loop_management_error_handling(self):
        """Test error handling in loop management."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
        }

        publisher = MQTTPublisher(**config)

        # Mock the client to raise exceptions
        mock_client = Mock()
        mock_client.loop_start.side_effect = Exception("Loop start failed")
        mock_client.loop_stop.side_effect = Exception("Loop stop failed")
        publisher.client = mock_client

        # Test loop_start error
        with pytest.raises(Exception, match="Loop start failed"):
            publisher.loop_start()

        # Test loop_stop error
        with pytest.raises(Exception, match="Loop stop failed"):
            publisher.loop_stop()

    def test_enhanced_logging_in_publish(self):
        """Test that publish uses enhanced logging."""
        logging_config = {"topic_specific": {"sensors/*": "DEBUG"}}

        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
            "logging_config": logging_config,
        }

        publisher = MQTTPublisher(**config)
        publisher._connected = False  # Not connected

        with patch.object(publisher, "_get_topic_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            # Test publish when not connected
            result = publisher.publish("sensors/temperature", "test")

            # Should use topic-specific logger
            mock_get_logger.assert_called_with("sensors/temperature")
            mock_logger.error.assert_called_once()
            assert result is False

    def test_config_dict_with_enhanced_features(self):
        """Test configuration dictionary with enhanced features."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
            "default_qos": 1,
            "default_retain": True,
            "logging_config": {"connection_level": "DEBUG", "publish_level": "INFO"},
        }

        publisher = MQTTPublisher(config=config)

        assert publisher.default_qos == 1
        assert publisher.default_retain
        assert publisher.logging_config["connection_level"] == "DEBUG"
        assert publisher.logging_config["publish_level"] == "INFO"

    def test_from_config_builder_with_enhanced_features(self):
        """Test MQTTConfig.build_config with enhanced features."""
        from mqtt_publisher.config import MQTTConfig

        config = MQTTConfig.build_config(
            broker_url="test.broker.com",
            client_id="test_client",
            default_qos="2",  # String should be converted
            default_retain="true",  # String should be converted
            logging_config={"connection_level": "DEBUG"},
        )

        assert config["default_qos"] == 2
        assert config["default_retain"]
        assert config["logging_config"]["connection_level"] == "DEBUG"

        # Test creating publisher from config
        publisher = MQTTPublisher(config=config)
        assert publisher.default_qos == 2
        assert publisher.default_retain

    def test_qos_validation_in_config_builder(self):
        """Test QoS validation in MQTTConfig.build_config."""
        from mqtt_publisher.config import MQTTConfig

        with pytest.raises(ValueError, match="default_qos must be 0, 1, or 2"):
            MQTTConfig.build_config(
                broker_url="test.broker.com",
                client_id="test_client",
                default_qos=5,  # Invalid QoS
            )

    def test_retain_string_conversion(self):
        """Test string to boolean conversion for retain."""
        from mqtt_publisher.config import MQTTConfig

        # Test various string representations
        true_values = ["true", "True", "1", "yes", "on"]
        false_values = ["false", "False", "0", "no", "off"]

        for value in true_values:
            config = MQTTConfig.build_config(
                broker_url="test.broker.com",
                client_id="test_client",
                default_retain=value,
            )
            assert config["default_retain"]

        for value in false_values:
            config = MQTTConfig.build_config(
                broker_url="test.broker.com",
                client_id="test_client",
                default_retain=value,
            )
            assert not config["default_retain"]

    def test_exponential_backoff_retry(self):
        """Test exponential backoff in connection retry logic."""
        from unittest.mock import patch

        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
            "max_retries": 3,
        }

        publisher = MQTTPublisher(**config)

        # Mock the client to always fail
        mock_client = Mock()
        mock_client.connect.side_effect = Exception("Connection failed")
        publisher.client = mock_client

        with (
            patch("time.sleep") as mock_sleep,
            patch("random.random", return_value=0.5),
        ):
            result = publisher.connect()

            # Should fail after max retries
            assert result is False

            # Check that sleep was called with increasing delays
            assert mock_sleep.call_count == 2  # max_retries - 1

            # Verify exponential backoff pattern (base_delay * 2^(retries-1))
            sleep_calls = [call.args[0] for call in mock_sleep.call_args_list]

            # First retry: base_delay = 1, should be around 1 second
            assert 0.5 <= sleep_calls[0] <= 2.0

            # Second retry: base_delay * 2 = 2, should be around 2 seconds
            assert 1.0 <= sleep_calls[1] <= 4.0

            # Second delay should be larger than first (exponential growth)
            assert sleep_calls[1] > sleep_calls[0]

    def test_exponential_backoff_with_jitter(self):
        """Test that exponential backoff includes jitter."""
        from unittest.mock import patch

        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
            "max_retries": 2,
        }

        publisher = MQTTPublisher(**config)

        # Mock the client to always fail
        mock_client = Mock()
        mock_client.connect.side_effect = Exception("Connection failed")
        publisher.client = mock_client

        # Test with different random values to ensure jitter is applied
        with (
            patch("time.sleep") as mock_sleep,
            patch("random.random", side_effect=[0.2, 0.8]) as mock_random,
        ):
            result = publisher.connect()

            # Should fail after max retries
            assert result is False

            # Verify random was called for jitter calculation
            assert mock_random.call_count >= 1

            # Sleep should be called at least once
            assert mock_sleep.call_count >= 1

    def test_exponential_backoff_max_delay(self):
        """Test that exponential backoff respects maximum delay."""
        from unittest.mock import patch

        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
            "max_retries": 10,  # High number to test max delay
        }

        publisher = MQTTPublisher(**config)

        # Mock the client to always fail
        mock_client = Mock()
        mock_client.connect.side_effect = Exception("Connection failed")
        publisher.client = mock_client

        with (
            patch("time.sleep") as mock_sleep,
            patch("random.random", return_value=0.0),
        ):  # No jitter
            result = publisher.connect()

            # Should fail after max retries
            assert result is False

            # Check that no delay exceeds max_delay (60 seconds)
            sleep_calls = [call.args[0] for call in mock_sleep.call_args_list]
            for delay in sleep_calls:
                assert delay <= 60.0  # max_delay

    def test_successful_connection_after_retries(self):
        """Test successful connection after some failures with exponential backoff."""
        from unittest.mock import patch

        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
            "max_retries": 3,
        }

        publisher = MQTTPublisher(**config)

        # Mock the client
        mock_client = Mock()
        publisher.client = mock_client

        # Track connection attempts
        connection_attempts = []

        def mock_connect_behavior(*args, **kwargs):
            connection_attempts.append(len(connection_attempts) + 1)
            if len(connection_attempts) == 1:
                # First attempt fails
                raise Exception("Connection failed")
            else:
                # Second attempt succeeds
                publisher._connected = True
                return 0

        mock_client.connect.side_effect = mock_connect_behavior

        with patch("time.sleep") as mock_sleep:
            result = publisher.connect()

            # Should succeed on second attempt
            assert result is True
            assert publisher._connected is True

            # Should have attempted twice
            assert len(connection_attempts) == 2

            # Should have slept once between retries
            assert mock_sleep.call_count == 1
