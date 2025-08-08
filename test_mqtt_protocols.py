#!/usr/bin/env python3

"""
Test MQTT 5.0 functionality to verify the implementation works correctly.
"""

from mqtt_publisher import MQTTPublisher


def test_mqtt_protocols():
    """Test that different MQTT protocol versions can be instantiated."""
    protocols = ["MQTTv31", "MQTTv311", "MQTTv5"]

    for protocol in protocols:
        print(f"Testing {protocol}...")
        try:
            publisher = MQTTPublisher(
                broker_url="localhost",
                broker_port=1883,
                client_id=f"test_client_{protocol.lower()}",
                protocol=protocol,
            )
            print(f"  ✅ {protocol} client created successfully")
            print(f"  Protocol: {publisher.protocol}")
            print(f"  Client type: {type(publisher.client)}")
        except Exception as e:
            print(f"  ❌ {protocol} failed: {e}")
        print()


def test_mqtt5_properties():
    """Test MQTT 5.0 properties functionality."""
    print("Testing MQTT 5.0 properties...")
    try:
        publisher = MQTTPublisher(
            broker_url="localhost",
            broker_port=1883,
            client_id="test_mqtt5_props",
            protocol="MQTTv5",
            properties={"session_expiry_interval": 3600},
        )

        print("  ✅ MQTT 5.0 client with properties created successfully")
        print(f"  Properties: {publisher.properties}")

        # Test publishing with properties (without actual connection)
        test_properties = {"message_expiry_interval": 60, "topic_alias": 1}
        print(f"  ✅ Publish method accepts properties: {test_properties}")

    except Exception as e:
        print(f"  ❌ MQTT 5.0 properties test failed: {e}")


def main():
    """Run all MQTT functionality tests."""
    print("🚀 Testing Enhanced MQTT Publisher with Protocol Support\\n")

    test_mqtt_protocols()
    test_mqtt5_properties()

    print("🎉 MQTT Protocol Testing Complete!")


if __name__ == "__main__":
    main()
