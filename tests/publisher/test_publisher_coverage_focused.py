"""Focused tests for publisher.py to reach 90%+ coverage."""

from unittest.mock import Mock, patch

from ha_mqtt_publisher.publisher import MQTTPublisher


class TestPublisherCoverage90:
    """Tests to get publisher.py to 90%+ coverage."""

    def test_connect_success_after_retries(self):
        """Test successful connection after initial failures."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
            "max_retries": 3,
        }

        publisher = MQTTPublisher(**config)

        # Mock the client
        mock_client = Mock()
        publisher.client = mock_client

        # Connection succeeds on third try
        def mock_connect_side_effect(*args, **kwargs):
            if mock_client.connect.call_count <= 2:
                raise Exception("Connection failed")
            else:
                # On successful connection, set connected state
                publisher._connected = True
                return 0

        mock_client.connect.side_effect = mock_connect_side_effect

        with patch("time.sleep"):
            result = publisher.connect()

        assert result is True

    def test_connect_timeout_scenario(self):
        """Test connection timeout scenario."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
        }

        publisher = MQTTPublisher(**config)

        # Mock the client
        mock_client = Mock()
        publisher.client = mock_client
        mock_client.connect.return_value = 0  # Success return code

        # But _connected remains False (timeout scenario)
        publisher._connected = False

        with (
            patch("time.sleep"),
            patch.object(publisher.connection_logger, "warning") as mock_warning,
        ):
            result = publisher.connect()

        assert result is False
        mock_warning.assert_called()

    def test_disconnect_when_connected(self):
        """Test disconnect when actually connected."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
        }

        publisher = MQTTPublisher(**config)
        publisher._connected = True

        # Mock the client
        mock_client = Mock()
        publisher.client = mock_client

        publisher.disconnect()

        mock_client.disconnect.assert_called_once()

    def test_publish_not_connected(self):
        """Test publish when not connected."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
        }

        publisher = MQTTPublisher(**config)
        publisher._connected = False

        result = publisher.publish("test/topic", "payload")

        assert result is False

    def test_publish_failure_result_code(self):
        """Test publish with failure result code."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
        }

        publisher = MQTTPublisher(**config)
        publisher._connected = True

        # Mock client with failure return code
        mock_client = Mock()
        publisher.client = mock_client
        mock_client.publish.return_value = (1, 123)  # Failure

        result = publisher.publish("test/topic", "payload")

        assert result is False

    def test_publish_with_mqtt5_properties(self):
        """Test publish with MQTT 5.0 properties."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
            "protocol": "MQTTv5",
        }

        publisher = MQTTPublisher(**config)
        publisher._connected = True

        # Mock client
        mock_client = Mock()
        publisher.client = mock_client
        # Mock publish result with proper rc attribute
        mock_result = Mock()
        mock_result.rc = 0  # Success
        mock_client.publish.return_value = mock_result

        properties = {"User Property": [("key", "value")]}
        result = publisher.publish("test/topic", "payload", properties=properties)

        assert result is True
        # Verify properties were passed (only if MQTT Properties are available)
        call_args = mock_client.publish.call_args
        import paho.mqtt.client as mqtt

        if hasattr(mqtt, "Properties") and hasattr(mqtt, "PacketTypes"):
            assert "properties" in call_args[1]
        else:
            # In legacy mode, properties should not be passed
            assert "properties" not in call_args[1]

    def test_connection_error_messages(self):
        """Test various connection error message scenarios."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
        }

        publisher = MQTTPublisher(**config)

        # Test known error codes
        assert "Connection refused" in publisher._get_connection_error_message(1)
        assert "protocol version" in publisher._get_connection_error_message(1)
        assert "identifier rejected" in publisher._get_connection_error_message(2)
        assert "server unavailable" in publisher._get_connection_error_message(3)
        assert "username or password" in publisher._get_connection_error_message(4)
        assert "not authorized" in publisher._get_connection_error_message(5)

        # Test unknown error code
        error_msg = publisher._get_connection_error_message(99)
        assert "Unknown connection error" in error_msg
        assert "99" in error_msg

    def test_context_manager_success(self):
        """Test context manager with successful connection."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
        }

        publisher = MQTTPublisher(**config)

        with (
            patch.object(publisher, "connect", return_value=True) as mock_connect,
            patch.object(publisher, "disconnect") as mock_disconnect,
        ):
            with publisher:
                pass

            mock_connect.assert_called_once()
            mock_disconnect.assert_called_once()

    def test_context_manager_connection_failure(self):
        """Test context manager with connection failure."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
        }

        publisher = MQTTPublisher(**config)

        with patch.object(publisher, "connect", return_value=False):
            try:
                with publisher:
                    pass
                raise AssertionError("Should have raised ConnectionError")
            except ConnectionError as e:
                assert "Failed to connect" in str(e)

    def test_on_connect_failure_logging(self):
        """Test _on_connect with failure and error logging."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
        }

        publisher = MQTTPublisher(**config)

        with patch.object(publisher.connection_logger, "error") as mock_error:
            publisher._on_connect(Mock(), Mock(), {}, 5, {})

        mock_error.assert_called_once()
        assert not publisher._connected

    def test_on_disconnect_unexpected(self):
        """Test _on_disconnect with unexpected disconnection."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
        }

        publisher = MQTTPublisher(**config)

        with patch.object(publisher.connection_logger, "warning") as mock_warning:
            publisher._on_disconnect(Mock(), Mock(), {}, 1, {})

        mock_warning.assert_called_once()
        assert not publisher._connected
