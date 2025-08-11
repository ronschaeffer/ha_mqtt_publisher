# ha_discovery/publisher.py

"""
High-level Home Assistant MQTT Discovery publisher.

This module provides convenient functions for publishing discovery configurations
to MQTT brokers for Home Assistant auto-discovery.
"""

import json

from .constants import AvailabilityMode, EntityCategory, SensorStateClass
from .device import Device
from .entity import Sensor
from .status_sensor import StatusSensor


def _slugify(value: str) -> str:
    """Create a HA-friendly slug: lowercase, alnum+underscore only."""
    import re

    value = value.strip().lower()
    value = re.sub(r"[\s\-]+", "_", value)
    value = re.sub(r"[^a-z0-9_]", "", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "device"


def publish_discovery_configs(
    config, publisher, entities=None, device=None, one_time_mode=False
):
    """
    Publishes the MQTT discovery configurations for all defined entities.

    Args:
        config: Configuration object with get() method
        publisher: MQTT publisher instance (must have publish() method)
        entities: Optional list of entities to publish. If None, creates default entities.
        device: Optional Device instance. If None, creates a new device.
        one_time_mode: If True, only publish if not already published (default: False)
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

    # Track published configs for one-time mode
    published_count = 0
    skipped_count = 0

    # Publish the discovery config for each entity
    for entity in entities:
        config_topic = entity.get_config_topic()
        config_payload = entity.get_config_payload()

        if one_time_mode and _is_discovery_already_published(config_topic, config):
            print(f"Skipping already published discovery config: {config_topic}")
            skipped_count += 1
            continue

        publisher.publish(
            topic=config_topic, payload=json.dumps(config_payload), retain=True
        )
        print(f"Published discovery config to {config_topic}")
        published_count += 1

        # Mark as published for one-time mode
        if one_time_mode:
            _mark_discovery_as_published(config_topic, config)

    if one_time_mode:
        print(
            f"One-time discovery mode: Published {published_count}, Skipped {skipped_count}"
        )


def _is_discovery_already_published(config_topic, config):
    """
    Check if a discovery config has already been published.

    Args:
        config_topic: The MQTT topic for the discovery config
        config: Configuration object

    Returns:
        bool: True if already published, False otherwise
    """
    import json
    import os

    # Get the discovery state file path
    state_file = config.get(
        "home_assistant.discovery_state_file", ".ha_discovery_state.json"
    )

    if not os.path.exists(state_file):
        return False

    try:
        with open(state_file) as f:
            published_configs = json.load(f)
        return config_topic in published_configs.get("published_topics", [])
    except (OSError, json.JSONDecodeError):
        return False


def _mark_discovery_as_published(config_topic, config):
    """
    Mark a discovery config as published.

    Args:
        config_topic: The MQTT topic for the discovery config
        config: Configuration object
    """
    from datetime import datetime
    import json
    import os

    # Get the discovery state file path
    state_file = config.get(
        "home_assistant.discovery_state_file", ".ha_discovery_state.json"
    )

    # Load existing state
    published_configs = {"published_topics": [], "last_updated": None}
    if os.path.exists(state_file):
        try:
            with open(state_file) as f:
                published_configs = json.load(f)
        except (OSError, json.JSONDecodeError):
            pass

    # Add the new topic if not already present
    if config_topic not in published_configs.get("published_topics", []):
        published_configs.setdefault("published_topics", []).append(config_topic)
        published_configs["last_updated"] = datetime.now().isoformat()

        # Save the updated state
        try:
            with open(state_file, "w") as f:
                json.dump(published_configs, f, indent=2)
        except OSError as e:
            print(f"Warning: Could not save discovery state: {e}")


def clear_discovery_state(config):
    """
    Clear the discovery state file to force republication of all configs.

    Args:
        config: Configuration object
    """
    import os

    state_file = config.get(
        "home_assistant.discovery_state_file", ".ha_discovery_state.json"
    )

    if os.path.exists(state_file):
        try:
            os.remove(state_file)
            print(f"Cleared discovery state file: {state_file}")
        except OSError as e:
            print(f"Warning: Could not remove discovery state file: {e}")
    else:
        print("Discovery state file does not exist")


def force_republish_discovery(config, publisher, entities=None, device=None):
    """
    Force republication of all discovery configs, ignoring one-time mode state.

    Args:
        config: Configuration object with get() method
        publisher: MQTT publisher instance (must have publish() method)
        entities: Optional list of entities to publish
        device: Optional Device instance
    """
    clear_discovery_state(config)
    publish_discovery_configs(config, publisher, entities, device, one_time_mode=False)


def publish_device_config(
    config,
    publisher,
    device: Device,
    *,
    device_id: str | None = None,
    retain: bool = True,
) -> bool:
    """
    Publish a device-centric discovery message.

    Topic format: <discovery_prefix>/device/<device_id>/config

    Args:
        config: Configuration object with get() method
        publisher: MQTT publisher instance (must have publish() method)
        device: Device instance to serialize
        device_id: Optional device identifier for the topic. If not provided,
                   uses the first identifier from the device or a slugified name.
        retain: Retain flag for the config message (default True)

    Returns:
        bool: Success status from publisher.publish
    """
    discovery_prefix = config.get("home_assistant.discovery_prefix", "homeassistant")

    # Determine device_id for topic
    if not device_id:
        if isinstance(device.identifiers, list) and device.identifiers:
            device_id = str(device.identifiers[0])
        else:
            device_id = _slugify(device.name)

    topic = f"{discovery_prefix}/device/{device_id}/config"
    payload = device.get_device_info()
    return publisher.publish(topic=topic, payload=json.dumps(payload), retain=retain)


def create_sensor(
    config,
    device: Device,
    name: str,
    unique_id: str,
    state_topic: str,
    *,
    entity_category: EntityCategory | None = None,
    availability_mode: AvailabilityMode | None = None,
    state_class: SensorStateClass | None = None,
    **kwargs,
):
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
        entity_category=entity_category,
        availability_mode=availability_mode,
        state_class=state_class,
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
