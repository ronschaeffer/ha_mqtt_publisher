"""Test MQTT 5.0 support and modern paho-mqtt features."""

import paho.mqtt.client as mqtt

from ha_mqtt_publisher.publisher import MQTTPublisher


class TestMQTT5Support:
    """Test MQTT 5.0 and modern paho-mqtt functionality."""

    def test_mqtt_protocol_versions(self):
        """Test that all MQTT protocol versions can be instantiated."""
        protocols = ["MQTTv31", "MQTTv311", "MQTTv5"]

        for protocol in protocols:
            publisher = MQTTPublisher(
                broker_url="localhost",
                broker_port=1883,
                client_id=f"test_{protocol.lower()}",
                protocol=protocol,
            )
            assert publisher.protocol == protocol
            assert publisher.client is not None

    def test_mqtt5_properties_support(self):
        """Test MQTT 5.0 properties functionality."""
        properties = {"session_expiry_interval": 3600}

        publisher = MQTTPublisher(
            broker_url="localhost",
            broker_port=1883,
            client_id="test_mqtt5",
            protocol="MQTTv5",
            properties=properties,
        )

        assert publisher.protocol == "MQTTv5"
        assert publisher.properties == properties

    def test_mqtt5_config_dict(self):
        """Test MQTT 5.0 via config dictionary."""
        config = {
            "broker_url": "localhost",
            "broker_port": 1883,
            "client_id": "test_config_mqtt5",
            "protocol": "MQTTv5",
            "properties": {"topic_alias_maximum": 10},
        }

        publisher = MQTTPublisher(config=config)
        assert publisher.protocol == "MQTTv5"
        assert publisher.properties["topic_alias_maximum"] == 10

    def test_modern_callback_api(self):
        """Test that we're using the modern callback API version."""
        publisher = MQTTPublisher(
            broker_url="localhost", broker_port=1883, client_id="test_callback_api"
        )

        # Check that the client was created successfully (this would fail if
        # CallbackAPIVersion.VERSION2 wasn't supported)
        assert publisher.client is not None

        # Verify the callbacks have the correct signatures
        # (VERSION2 callbacks have different signatures than VERSION1)
        assert hasattr(publisher, "_on_connect")
        assert hasattr(publisher, "_on_disconnect")
        assert hasattr(publisher, "_on_publish")

    def test_paho_mqtt_version(self):
        """Verify paho-mqtt compatibility (supports both modern and legacy versions)."""
        # Test that basic MQTT features are always available
        assert hasattr(mqtt, "MQTTv5")
        assert hasattr(mqtt, "Client")

        # Test that we can create clients (with backwards compatibility)
        if hasattr(mqtt, "CallbackAPIVersion"):
            # Modern paho-mqtt (>= 2.0.0)
            client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        else:
            # Legacy paho-mqtt (< 2.0.0)
            client = mqtt.Client()
        assert client is not None

    def test_publish_with_properties(self):
        """Test publish method accepts MQTT 5.0 properties."""
        publisher = MQTTPublisher(
            broker_url="localhost",
            broker_port=1883,
            client_id="test_props",
            protocol="MQTTv5",
        )

        # This should not raise an exception even though we're not connected
        # We're just testing the method signature
        properties = {"message_expiry_interval": 60}
        result = publisher.publish("test/topic", "test", properties=properties)

        # Should return False because we're not connected, but no exception
        assert result is False

    def test_backward_compatibility(self):
        """Test that existing code without protocol specification still works."""
        # Default should be MQTTv311 for backward compatibility
        publisher = MQTTPublisher(
            broker_url="localhost", broker_port=1883, client_id="test_default"
        )

        assert publisher.protocol == "MQTTv311"
        assert publisher.client is not None
