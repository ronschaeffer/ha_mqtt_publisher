import logging
import ssl
from unittest.mock import MagicMock, patch

import paho.mqtt.client as mqtt

from mqtt_publisher.publisher import MQTTPublisher

# Set up logging
logging.basicConfig(level=logging.DEBUG)


@patch("paho.mqtt.client.Client")
def test_mqtt_publisher_connection(mock_client):
    logging.debug("Starting test_mqtt_publisher_connection")

    # Mock connect and loop_start methods to simulate a successful connection
    mock_client.return_value.connect.return_value = 0
    mock_client.return_value.loop_start = MagicMock()
    mock_client.return_value.loop_stop = MagicMock()
    mock_client.return_value.disconnect = MagicMock()

    publisher = MQTTPublisher(
        broker_url="test.broker.com",
        broker_port=1883,
        client_id="test_client",
    )

    # Simulate successful connection (important for this test)
    publisher._connected = True

    # Assert that connect was called with the correct parameters
    logging.debug("Calling connect")
    assert publisher.connect() is True
    mock_client.return_value.connect.assert_called_once_with(
        "test.broker.com", 1883, keepalive=60
    )

    # Test disconnect
    logging.debug("Calling disconnect")
    publisher.disconnect()
    mock_client.return_value.loop_stop.assert_called_once()
    mock_client.return_value.disconnect.assert_called_once()

    logging.debug("Finished test_mqtt_publisher_connection")


@patch("paho.mqtt.client.Client")
def test_mqtt_publisher_publish(mock_client):
    logging.debug("Starting test_mqtt_publisher_publish")

    # Mock the connect, loop_start, and publish methods
    mock_client.return_value.connect.return_value = 0
    mock_client.return_value.loop_start = MagicMock()
    mock_client.return_value.publish.return_value.rc = mqtt.MQTT_ERR_SUCCESS

    publisher = MQTTPublisher(
        broker_url="test.broker.com",
        broker_port=1883,
        client_id="test_client",
    )

    # Simulate successful connection (important for this test)
    publisher._connected = True

    # Test publish
    logging.debug("Calling publish")
    assert publisher.publish("test/topic", {"message": "Hello, MQTT!"}) is True
    mock_client.return_value.publish.assert_called_once_with(
        "test/topic",
        '{"message": "Hello, MQTT!"}',
        qos=0,
        retain=False,  # Fixed assertion
    )

    logging.debug("Finished test_mqtt_publisher_publish")


@patch("paho.mqtt.client.Client")
def test_mqtt_publisher_tls(mock_client):
    logging.debug("Starting test_mqtt_publisher_tls")

    # Mock the connect, tls_set, and tls_insecure_set methods
    mock_client.return_value.connect.return_value = 0
    mock_client.return_value.tls_set = MagicMock()
    mock_client.return_value.tls_insecure_set = MagicMock()
    mock_client.return_value.loop_start = MagicMock()
    mock_client.return_value.loop_stop = MagicMock()
    mock_client.return_value.disconnect = MagicMock()

    tls_config = {
        "ca_cert": "path/to/ca_cert",
        "client_cert": "path/to/client_cert",
        "client_key": "path/to/client_key",
        "verify": True,
    }

    publisher = MQTTPublisher(
        broker_url="test.broker.com",
        broker_port=8883,  # Use a typical port for TLS
        client_id="test_client",
        security="tls",
        tls=tls_config,
    )

    # Simulate successful connection (important for this test)
    publisher._connected = True

    # Call connect() to trigger the TLS setup
    try:
        assert publisher.connect() is True
    except Exception as e:
        logging.error(f"An error occurred during connect(): {e}")
        raise  # Re-raise the exception to fail the test

    # Assert that tls_set, tls_insecure_set were called with correct parameters
    mock_client.return_value.tls_set.assert_called_once_with(
        ca_certs="path/to/ca_cert",
        certfile="path/to/client_cert",
        keyfile="path/to/client_key",
        cert_reqs=ssl.CERT_REQUIRED,
        tls_version=ssl.PROTOCOL_TLS,
    )
    mock_client.return_value.tls_insecure_set.assert_called_once_with(False)

    # Assert that loop_start was called
    mock_client.return_value.loop_start.assert_called_once()

    logging.debug("Finished test_mqtt_publisher_tls")


# ... (other test functions) ...


@patch("paho.mqtt.client.Client")
def test_mqtt_publisher_last_will(mock_client):
    logging.debug("Starting test_mqtt_publisher_last_will")

    # Mock connect, will_set, loop_start, loop_stop, and disconnect methods
    mock_client.return_value.connect.return_value = 0
    mock_client.return_value.will_set = MagicMock()
    mock_client.return_value.loop_start = MagicMock()
    mock_client.return_value.loop_stop = MagicMock()
    mock_client.return_value.disconnect = MagicMock()

    last_will_config = {
        "topic": "last/will/topic",
        "payload": "Last will message",
        "qos": 1,
        "retain": True,
    }

    publisher = MQTTPublisher(
        broker_url="test.broker.com",
        broker_port=1883,
        client_id="test_client",
        last_will=last_will_config,  # Pass the last will config
    )

    # Simulate successful connection (important for this test)
    publisher._connected = True

    # Assert that will_set was called with the correct parameters
    logging.debug("Setting last will")
    try:
        assert publisher.connect() is True
    except Exception as e:
        logging.error(f"An error occurred during connect(): {e}")
        raise  # Re-raise the exception to fail the test

    mock_client.return_value.will_set.assert_called_once_with(
        "last/will/topic", "Last will message", qos=1, retain=True
    )

    # Assert that loop_start was called
    mock_client.return_value.loop_start.assert_called_once()

    logging.debug("Finished test_mqtt_publisher_last_will")


@patch("paho.mqtt.client.Client")
def test_mqtt_publisher_basic_init(mock_client):
    """Test basic initialization of MQTTPublisher."""
    publisher = MQTTPublisher(
        broker_url="test.broker.com",
        broker_port=1883,
        client_id="test_client",
    )

    assert publisher.broker_url == "test.broker.com"
    assert publisher.broker_port == 1883
    assert publisher._connected is False
