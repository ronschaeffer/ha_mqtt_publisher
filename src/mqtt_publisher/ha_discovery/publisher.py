# ha_discovery/publisher.py

"""
High-level Home Assistant MQTT Discovery publisher.

This module provides convenient functions for publishing discovery configurations
to MQTT brokers for Home Assistant auto-discovery.
"""

import json

from .device import Device
from .entity import Sensor
from .status_sensor import StatusSensor


def publish_discovery_configs(config, publisher, entities=None, device=None):
    """
    Publishes the MQTT discovery configurations for all defined entities.

    Args:
        config: Configuration object with get() method
        publisher: MQTT publisher instance (must have publish() method)
        entities: Optional list of entities to publish. If None, creates default entities.
        device: Optional Device instance. If None, creates a new device.
    """
    if not config.get("home_assistant.enabled", True):
        return

    # Create a single device instance to be shared by all entities
    if device is None:
        device = Device(config)

    # If no entities provided, create default entities
    if entities is None:
        entities = []

        # Conditionally add the Status Sensor
        if config.get("mqtt.topics.status"):
            entities.append(StatusSensor(config, device))

    # Publish the discovery config for each entity
    for entity in entities:
        config_topic = entity.get_config_topic()
        config_payload = entity.get_config_payload()
        publisher.publish(
            topic=config_topic, payload=json.dumps(config_payload), retain=True
        )
        print(f"Published discovery config to {config_topic}")


def create_sensor(config, device, name, unique_id, state_topic, **kwargs):
    """
    Convenience function to create a Sensor entity.

    Args:
        config: Configuration object
        device: Device instance
        name: Display name for the sensor
        unique_id: Unique identifier for the sensor
        state_topic: MQTT topic where sensor publishes its state
        **kwargs: Additional sensor attributes (value_template, icon, etc.)

    Returns:
        Sensor: Configured sensor entity
    """
    return Sensor(
        config=config,
        device=device,
        name=name,
        unique_id=unique_id,
        state_topic=state_topic,
        **kwargs,
    )


def create_status_sensor(config, device):
    """
    Convenience function to create a StatusSensor.

    Args:
        config: Configuration object
        device: Device instance

    Returns:
        StatusSensor: Configured status sensor
    """
    return StatusSensor(config, device)
