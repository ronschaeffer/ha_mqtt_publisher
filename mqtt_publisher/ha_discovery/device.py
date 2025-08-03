# ha_discovery/device.py

"""
Device representation for Home Assistant MQTT Discovery.

This module provides the Device class which represents a physical or logical
device in Home Assistant that groups multiple entities together.
"""


class Device:
    """
    Represents a Home Assistant device. This class is used to create a device
    that groups multiple entities (sensors, binary_sensors, etc.) together.
    """

    def __init__(self, config):
        """
        Initializes the Device object.

        Args:
            config: The application's configuration object with get() method.
        """
        self._config = config
        self.identifiers = [self._config.get("app.unique_id_prefix", "mqtt_publisher")]
        self.name = self._config.get("app.name", "MQTT Publisher")
        self.manufacturer = self._config.get(
            "app.manufacturer", "Generic MQTT Publisher"
        )
        self.model = self._config.get("app.model", "MQTT-Pub-Py")

    def get_device_info(self) -> dict:
        """
        Returns a dictionary containing the device information, which is used
        in the discovery payload for each entity.
        """
        return {
            "identifiers": self.identifiers,
            "name": self.name,
            "manufacturer": self.manufacturer,
            "model": self.model,
        }
