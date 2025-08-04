"""An MQTT publisher package with Home Assistant Discovery support"""

__version__ = "0.1.0"
__author__ = "ronschaeffer"
__email__ = "ron@ronschaeffer.com"

# Import main components for easy access
from .config import Config, MQTTConfig

# Import HA discovery components
from .ha_discovery import (
    Device,
    Entity,
    Sensor,
    StatusSensor,
    publish_discovery_configs,
)
from .publisher import MQTTPublisher

__all__ = [
    "Config",
    "Device",
    "Entity",
    "MQTTConfig",
    "MQTTPublisher",
    "Sensor",
    "StatusSensor",
    "publish_discovery_configs",
]
