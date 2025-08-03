# ha_discovery/__init__.py

"""
Home Assistant MQTT Discovery Framework

This module provides a sophisticated object-oriented framework for creating
Home Assistant MQTT discovery configurations. It includes:

- Device: Groups entities under a single device
- Entity: Base class for all Home Assistant entities
- Sensor: Regular sensor entities with rich configuration
- StatusSensor: Binary sensor for monitoring system health
- Discovery Publisher: High-level interface for publishing discovery configs

Usage:
    from mqtt_publisher.ha_discovery import Device, Sensor, StatusSensor, publish_discovery_configs
    from mqtt_publisher.publisher import MQTTPublisher

    device = Device(config)
    publisher = MQTTPublisher(**mqtt_config)
    publish_discovery_configs(config, publisher, device)
"""

from .device import Device
from .entity import Entity, Sensor
from .publisher import create_sensor, create_status_sensor, publish_discovery_configs
from .status_sensor import StatusSensor

__all__ = [
    "Device",
    "Entity",
    "Sensor",
    "StatusSensor",
    "create_sensor",
    "create_status_sensor",
    "publish_discovery_configs",
]
