"""
Home Assistant MQTT Discovery module.

This module provides comprehensive Home Assistant MQTT Discovery support,
including entity creation, device management, and discovery lifecycle management.
"""

from .device import Device
from .discovery_manager import DiscoveryManager
from .entity import Entity
from .publisher import create_sensor, create_status_sensor, publish_discovery_configs
from .status_sensor import StatusSensor

__all__ = [
    "Device",
    "DiscoveryManager",
    "Entity",
    "StatusSensor",
    "create_sensor",
    "create_status_sensor",
    "publish_discovery_configs",
]
