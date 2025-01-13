import logging
from unittest.mock import patch, MagicMock
from mqtt_publisher.publisher import MQTTPublisher

# Set up logging
logging.basicConfig(level=logging.DEBUG)

@patch('paho.mqtt.client.Client')
def test_mqtt_publisher_connection(mock_client):
    logging.debug("Starting test_mqtt_publisher_connection")
    
    # Mock the connect and loop_start methods to simulate a successful connection
    mock_client.return_value.connect.return_value = 0
    mock_client.return_value.loop_start = MagicMock()
    mock_client.return_value.loop_stop = MagicMock()
    mock_client.return_value.disconnect = MagicMock()

    publisher = MQTTPublisher(
        broker_url="test.broker.com",
        broker_port=1883,
        client_id="test_client"
    )

    # Simulate successful connection
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

# Add more tests for other methods and scenarios...