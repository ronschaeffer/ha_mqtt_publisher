"""An MQTT publisher package with Home Assistant Discovery support"""

__version__ = "0.2.1"
__author__ = "ronschaeffer"

# Import main components for easy access
from .config import Config, MQTTConfig

# Import HA discovery components
from .ha_discovery import (
    Device,
    DiscoveryManager,
    Entity,
    StatusSensor,
    publish_discovery_configs,
)
from .publisher import MQTTPublisher

__all__ = [
    "Config",
    "Device",
    "DiscoveryManager",
    "Entity",
    "MQTTConfig",
    "MQTTPublisher",
    "StatusSensor",
    "publish_discovery_configs",
]
