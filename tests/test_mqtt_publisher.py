from unittest.mock import patch
from mqtt_publisher.publisher import MQTTPublisher

@patch('paho.mqtt.client.Client')
def test_mqtt_publisher_connection(mock_client):
    publisher = MQTTPublisher(
        broker_url="test.broker.com",
        broker_port=1883,
        client_id="test_client"
    )
    # Assert that connect was called with the correct parameters
    publisher.connect()
    mock_client.return_value.connect.assert_called_once_with(
        "test.broker.com", 1883, keepalive=60
    )

# Add more tests for other methods and scenarios...