"""Home Assistant-compatible constants and type hints for MQTT Discovery.

These are not imported from Home Assistant; they mirror HA docs to guide users
and enable light validation while keeping runtime payloads as plain strings.
"""

from __future__ import annotations

from typing import Literal

# Entity category
EntityCategory = Literal["config", "diagnostic"]
ENTITY_CATEGORIES: set[str] = {"config", "diagnostic"}

# Availability mode
AvailabilityMode = Literal["all", "any", "latest"]
AVAILABILITY_MODES: set[str] = {"all", "any", "latest"}

# Sensor state_class
SensorStateClass = Literal["measurement", "total", "total_increasing"]
SENSOR_STATE_CLASSES: set[str] = {"measurement", "total", "total_increasing"}

# Binary sensor device_class (subset maintained from HA docs)
BinarySensorDeviceClass = Literal[
    "battery",
    "battery_charging",
    "carbon_monoxide",
    "cold",
    "connectivity",
    "door",
    "garage_door",
    "gas",
    "heat",
    "light",
    "lock",
    "moisture",
    "moving",
    "occupancy",
    "opening",
    "plug",
    "power",
    "presence",
    "problem",
    "safety",
    "smoke",
    "sound",
    "tamper",
    "update",
    "vibration",
    "window",
]
_BS_DEV_CLASSES = [
    "battery",
    "battery_charging",
    "carbon_monoxide",
    "cold",
    "connectivity",
    "door",
    "garage_door",
    "gas",
    "heat",
    "light",
    "lock",
    "moisture",
    "moving",
    "occupancy",
    "opening",
    "plug",
    "power",
    "presence",
    "problem",
    "safety",
    "smoke",
    "sound",
    "tamper",
    "update",
    "vibration",
    "window",
]
BINARY_SENSOR_DEVICE_CLASSES: set[str] = set(_BS_DEV_CLASSES)

__all__ = [
    "AVAILABILITY_MODES",
    "BINARY_SENSOR_DEVICE_CLASSES",
    "ENTITY_CATEGORIES",
    "SENSOR_STATE_CLASSES",
    "AvailabilityMode",
    "BinarySensorDeviceClass",
    "EntityCategory",
    "SensorStateClass",
]
