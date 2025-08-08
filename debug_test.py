#!/usr/bin/env python3

import sys

sys.path.insert(0, "/home/ron/projects/mqtt_publisher/src")

from unittest.mock import Mock, patch

from mqtt_publisher.publisher import MQTTPublisher


def test_debug():
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
        attempt_num = len(connection_attempts) + 1
        connection_attempts.append(attempt_num)
        print(f"DEBUG: Mock connect called - attempt {attempt_num}")
        print(f"DEBUG: Args: {args}, Kwargs: {kwargs}")

        if attempt_num == 1:
            # First attempt fails
            print("DEBUG: First attempt - raising exception")
            raise Exception("Connection failed")
        else:
            # Second attempt succeeds
            print(
                f"DEBUG: Attempt {attempt_num} - setting _connected=True and returning 0"
            )
            publisher._connected = True
            return 0

    mock_client.connect.side_effect = mock_connect_behavior

    with patch("time.sleep"):
        print("DEBUG: Starting connect() call")
        result = publisher.connect()
        print(f"DEBUG: connect() returned: {result}")
        print(f"DEBUG: _connected state: {publisher._connected}")
        print(f"DEBUG: Connection attempts: {connection_attempts}")


if __name__ == "__main__":
    test_debug()
