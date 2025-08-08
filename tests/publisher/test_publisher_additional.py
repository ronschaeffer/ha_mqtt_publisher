"""Additional tests for publisher.py to improve coverage."""

from unittest.mock import Mock, patch

from src.mqtt_publisher.publisher import MQTTPublisher


class TestPublisherAdditionalCoverage:
    """Additional tests to improve publisher coverage."""

    def test_security_validation_tls_missing_config(self):
        """Test validation error when TLS security is set but no TLS config provided."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
            "security": "tls",
            # Missing tls configuration
        }

        try:
            MQTTPublisher(**config)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "TLS configuration required when security='tls'" in str(e)

    def test_security_validation_tls_client_cert_missing_certs(self):
        """Test validation error when TLS client cert security is set but certs are missing."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
            "security": "tls_with_client_cert",
            "tls": {
                "ca_cert": "/path/to/ca.crt",
                # Missing client_cert and client_key
            },
        }

        try:
            MQTTPublisher(**config)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert (
                "client_cert and client_key required for tls_with_client_cert" in str(e)
            )

    def test_on_disconnect_callback_unexpected(self):
        """Test _on_disconnect callback with unexpected disconnection."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
        }

        publisher = MQTTPublisher(**config)

        # Mock client and userdata
        mock_client = Mock()
        mock_userdata = Mock()

        with patch.object(publisher.connection_logger, "warning") as mock_warning:
            # Simulate unexpected disconnection (reason_code != 0)
            publisher._on_disconnect(mock_client, mock_userdata, {}, 1, {})

            # Verify warning was logged
            mock_warning.assert_called_once()
            assert "Unexpected disconnection" in mock_warning.call_args[0][0]

        # Verify connected state is False
        assert not publisher._connected

    def test_on_disconnect_callback_expected(self):
        """Test _on_disconnect callback with expected disconnection."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
        }

        publisher = MQTTPublisher(**config)

        # Mock client and userdata
        mock_client = Mock()
        mock_userdata = Mock()

        with patch("logging.warning") as mock_warning:
            # Simulate expected disconnection (reason_code == 0)
            publisher._on_disconnect(mock_client, mock_userdata, {}, 0, {})

            # Verify no warning was logged
            mock_warning.assert_not_called()

        # Verify connected state is False
        assert not publisher._connected

    def test_on_publish_callback(self):
        """Test _on_publish callback."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
        }

        publisher = MQTTPublisher(**config)

        # Mock client and userdata
        mock_client = Mock()
        mock_userdata = Mock()

        with patch.object(publisher.publish_logger, "debug") as mock_debug:
            # Simulate publish callback
            publisher._on_publish(mock_client, mock_userdata, 123, None, {})

            # Verify debug message was logged
            mock_debug.assert_called_once()
            assert "Message published with ID: 123" in mock_debug.call_args[0][0]

    def test_on_connect_callback_success(self):
        """Test _on_connect callback with successful connection."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
        }

        publisher = MQTTPublisher(**config)

        # Mock client and userdata
        mock_client = Mock()
        mock_userdata = Mock()

        with patch.object(publisher.connection_logger, "info") as mock_info:
            # Simulate successful connection (reason_code == 0)
            publisher._on_connect(mock_client, mock_userdata, {}, 0, {})

            # Verify info message was logged
            mock_info.assert_called_once()
            assert "Connected to MQTT broker" in mock_info.call_args[0][0]

        # Verify connected state is True
        assert publisher._connected

    def test_on_connect_callback_failure(self):
        """Test _on_connect callback with connection failure."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
        }

        publisher = MQTTPublisher(**config)

        # Mock client and userdata
        mock_client = Mock()
        mock_userdata = Mock()

        with patch.object(publisher.connection_logger, "error") as mock_error:
            # Simulate connection failure (reason_code != 0)
            publisher._on_connect(mock_client, mock_userdata, {}, 5, {})

            # Verify error message was logged
            mock_error.assert_called_once()

        # Verify connected state remains False
        assert not publisher._connected

    def test_validation_errors_username_missing_password(self):
        """Test validation error when username security is set but password is missing."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
            "security": "username",
            "auth": {
                "username": "test_user",
                # Missing password
            },
        }

        try:
            MQTTPublisher(**config)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "username and password required when security='username'" in str(e)

    def test_port_validation_out_of_range(self):
        """Test port validation for out of range values."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
            "broker_port": 70000,  # Invalid port number
        }

        try:
            MQTTPublisher(**config)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "broker_port must be integer 1-65535" in str(e)

    def test_missing_client_id_validation(self):
        """Test validation error when client_id is missing."""
        config = {
            "broker_url": "test.broker.com",
            # Missing client_id
        }

        try:
            MQTTPublisher(**config)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "client_id is required" in str(e)

    def test_connect_with_retries_and_timeout(self):
        """Test connection with retries and timeout scenarios."""
        from unittest.mock import patch

        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
            "max_retries": 2,
        }

        publisher = MQTTPublisher(**config)

        # Mock the client
        mock_client = Mock()
        publisher.client = mock_client

        # Test connection timeout scenario
        mock_client.connect.return_value = 0  # Success
        publisher._connected = False  # Simulate not connected after timeout

        with (
            patch("time.sleep"),
            patch.object(publisher.connection_logger, "warning") as mock_warning,
        ):
            result = publisher.connect()

            # Should timeout and log warning
            assert result is False
            mock_warning.assert_called()
            assert "Connection timeout" in mock_warning.call_args[0][0]

    def test_connect_with_exception_and_retries(self):
        """Test connection with exceptions and retry logic."""
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

        # Test exception during connection
        mock_client.connect.side_effect = [
            Exception("Connection failed"),
            Exception("Connection failed again"),
            0,  # Third attempt succeeds
        ]

        with (
            patch("time.sleep") as mock_sleep,
            patch.object(publisher.connection_logger, "error") as mock_error,
        ):
            publisher.connect()

            # Should retry and eventually fail
            assert mock_error.call_count >= 2  # At least 2 error logs
            # Check that connection attempts were logged (any of the error calls should contain this)
            error_messages = [call.args[0] for call in mock_error.call_args_list]
            connection_attempt_logged = any(
                "Connection attempt" in msg for msg in error_messages
            )
            assert connection_attempt_logged
            assert mock_sleep.call_count >= 1  # Should sleep between retries

    def test_connect_max_retries_exceeded(self):
        """Test connection when max retries are exceeded."""
        from unittest.mock import patch

        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
            "max_retries": 2,
        }

        publisher = MQTTPublisher(**config)

        # Mock the client
        mock_client = Mock()
        publisher.client = mock_client

        # All connection attempts fail
        mock_client.connect.side_effect = Exception("Connection failed")

        with (
            patch("time.sleep") as mock_sleep,
            patch.object(publisher.connection_logger, "error") as mock_error,
        ):
            result = publisher.connect()

            # Should fail after max retries
            assert result is False
            assert (
                mock_error.call_count >= 2
            )  # At least max_retries attempts + final error
            assert mock_sleep.call_count == 1  # Sleep between retries (not after last)

    def test_disconnect_when_connected(self):
        """Test disconnect when client is connected."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
        }

        publisher = MQTTPublisher(**config)
        publisher._connected = True

        # Mock the client
        mock_client = Mock()
        publisher.client = mock_client

        # Test disconnect
        publisher.disconnect()

        # Should call client disconnect
        mock_client.disconnect.assert_called_once()

    def test_disconnect_when_not_connected(self):
        """Test disconnect when client is not connected."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
        }

        publisher = MQTTPublisher(**config)
        publisher._connected = False

        # Mock the client
        mock_client = Mock()
        publisher.client = mock_client

        # Test disconnect
        publisher.disconnect()

        # Should not call client disconnect
        mock_client.disconnect.assert_not_called()

    def test_publish_when_not_connected(self):
        """Test publish when not connected."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
        }

        publisher = MQTTPublisher(**config)
        publisher._connected = False

        # Test publish
        result = publisher.publish("test/topic", "test payload")

        # Should fail when not connected
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

        # Mock the client
        mock_client = Mock()
        publisher.client = mock_client
        # Mock publish result with proper rc attribute
        mock_result = Mock()
        mock_result.rc = 0  # Success
        mock_client.publish.return_value = mock_result

        # Test publish with properties
        properties = {"User Property": [("key", "value")]}
        result = publisher.publish("test/topic", "test payload", properties=properties)

        # Should call publish with properties
        assert result is True
        mock_client.publish.assert_called_once()
        call_args = mock_client.publish.call_args
        assert "properties" in call_args[1]

    def test_publish_failure_return_code(self):
        """Test publish with failure return code."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
        }

        publisher = MQTTPublisher(**config)
        publisher._connected = True

        # Mock the client with failure
        mock_client = Mock()
        publisher.client = mock_client
        mock_client.publish.return_value = (1, 123)  # Failure code

        # Test publish
        result = publisher.publish("test/topic", "test payload")

        # Should return False on failure
        assert result is False

    def test_get_connection_error_message_known_codes(self):
        """Test error message generation for known error codes."""
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

    def test_get_connection_error_message_unknown_code(self):
        """Test error message generation for unknown error codes."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
        }

        publisher = MQTTPublisher(**config)

        # Test unknown error code
        error_msg = publisher._get_connection_error_message(99)
        assert "Unknown connection error" in error_msg
        assert "99" in error_msg

    def test_context_manager_success(self):
        """Test using publisher as context manager successfully."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
        }

        publisher = MQTTPublisher(**config)

        # Mock successful connection
        with (
            patch.object(publisher, "connect", return_value=True) as mock_connect,
            patch.object(publisher, "disconnect") as mock_disconnect,
        ):
            with publisher as pub:
                assert pub is publisher

            mock_connect.assert_called_once()
            mock_disconnect.assert_called_once()

    def test_context_manager_connection_failure(self):
        """Test using publisher as context manager with connection failure."""
        config = {
            "broker_url": "test.broker.com",
            "client_id": "test_client",
        }

        publisher = MQTTPublisher(**config)

        # Mock failed connection
        with patch.object(publisher, "connect", return_value=False) as mock_connect:
            try:
                with publisher:
                    raise AssertionError("Should have raised ConnectionError")
            except ConnectionError as e:
                assert "Failed to connect" in str(e)

            mock_connect.assert_called_once()
