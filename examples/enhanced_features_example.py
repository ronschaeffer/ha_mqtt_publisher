#!/usr/bin/env python3
"""
Example demonstrating enhanced MQTT Publisher functionality.

This example s    # Example of TLS validation
    try:
        publisher = MQTTPublisher(  # noqa: F841
            broker_url="mqtt.example.com",
            broker_port=8883,
            client_id="test",
            security="tls",
            auth={"username": "user", "password": "pass"}
            # Missing TLS configuration
        )o use the new features:
1. Port type conversion
2. Configuration builder pattern
3. Enhanced validation with helpful error messages
4. Config dictionary support
"""

from mqtt_publisher import MQTTConfig, MQTTPublisher


def example_1_basic_usage():
    """Example 1: Basic usage with automatic port conversion."""
    print("=== Example 1: Basic Usage ===")

    # String port is automatically converted to int
    publisher = MQTTPublisher(
        broker_url="mqtt.example.com",
        broker_port="1883",  # String port - automatically converted
        client_id="example_client",
        security="none",
    )

    print(f"Broker: {publisher.broker_url}:{publisher.broker_port}")
    print(f"Port type: {type(publisher.broker_port)}")
    print()


def example_2_config_builder():
    """Example 2: Using MQTTConfig builder pattern."""
    print("=== Example 2: Config Builder Pattern ===")

    # Build configuration with automatic validation
    config = MQTTConfig.build_config(
        broker_url="mqtt.example.com",
        broker_port="8883",  # String automatically converted
        client_id="builder_example",
        security="username",
        username="user",
        password="password",
        max_retries="5",  # String automatically converted
    )

    print("Built configuration:")
    for key, value in config.items():
        print(f"  {key}: {value} ({type(value).__name__})")

    # Use the configuration
    publisher = MQTTPublisher(config=config)
    print(f"Publisher created with broker: {publisher.broker_url}")
    print()


def example_3_from_dict():
    """Example 3: Building config from nested dictionary (like YAML)."""
    print("=== Example 3: From Dictionary (YAML-like) ===")

    # Simulate loading from YAML configuration
    yaml_like_config = {
        "mqtt": {
            "broker_url": "mqtt.example.com",
            "broker_port": 8883,
            "client_id": "yaml_example",
            "security": "username",
            "auth": {"username": "user", "password": "pass"},
            "tls": {"verify": True, "ca_cert": "/path/to/ca.pem"},
            "max_retries": 3,
        }
    }

    # Convert to MQTT config
    mqtt_config = MQTTConfig.from_dict(yaml_like_config)

    print("Converted configuration:")
    for key, value in mqtt_config.items():
        print(f"  {key}: {value}")

    # Use the configuration
    publisher = MQTTPublisher(config=mqtt_config)
    print(f"Publisher created with security: {publisher.security}")
    print()


def example_4_validation_errors():
    """Example 4: Demonstrating validation with helpful error messages."""
    print("=== Example 4: Validation Examples ===")

    # Example of helpful validation error
    try:
        MQTTConfig.build_config(
            broker_port="70000",  # Invalid port
            security="username",
            # Missing broker_url, client_id, and auth
        )
    except ValueError as e:
        print("Validation caught multiple errors:")
        print(str(e))

    print()

    # Example of TLS validation
    try:
        publisher = MQTTPublisher(  # noqa: F841
            broker_url="mqtt.example.com",
            broker_port=8883,
            client_id="test",
            security="tls",
            auth={"username": "user", "password": "pass"},
            # Missing TLS configuration
        )
    except ValueError as e:
        print("TLS validation error:")
        print(str(e))

    print()


def example_5_warnings():
    """Example 5: Configuration warnings (non-fatal)."""
    print("=== Example 5: Configuration Warnings ===")

    # This will log a warning but still create the publisher
    print("Creating publisher with TLS/port mismatch (will show warning):")
    publisher = MQTTPublisher(
        broker_url="mqtt.example.com",
        broker_port=1883,  # Non-TLS port
        client_id="warning_example",
        tls={"verify": True},  # TLS enabled
    )

    print(f"Publisher created successfully: {publisher.broker_url}")
    print("(Check logs for warning message)")
    print()


if __name__ == "__main__":
    print("MQTT Publisher Enhancement Examples")
    print("=" * 40)
    print()

    example_1_basic_usage()
    example_2_config_builder()
    example_3_from_dict()
    example_4_validation_errors()
    example_5_warnings()

    print("All examples completed!")
