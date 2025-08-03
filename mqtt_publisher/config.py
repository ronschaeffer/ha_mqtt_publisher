import yaml


class Config:
    """
    Enhanced configuration class with support for nested key access.

    Supports both dot notation (config.get("mqtt.broker_url")) and
    underscore notation (config.mqtt_broker_url) for accessing nested values.
    """

    def __init__(self, config_path):
        with open(config_path) as config_file:
            self.config = yaml.safe_load(config_file)

    def __getattr__(self, name):
        # First try to get directly from top level
        if name in self.config:
            return self.config[name]

        # If not found, try nested dictionary lookup
        keys = name.split("_")
        value = self.config
        for key in keys:
            if not isinstance(value, dict) or key not in value:
                raise AttributeError(f"Configuration key '{name}' not found")
            value = value[key]
        return value

    def get(self, name, default=None):
        """
        Get configuration value with optional default.

        Supports dot notation: config.get("mqtt.broker_url")
        And underscore notation: config.get("mqtt_broker_url")

        Args:
            name: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        try:
            # Try dot notation first
            if "." in name:
                keys = name.split(".")
                value = self.config
                for key in keys:
                    if not isinstance(value, dict) or key not in value:
                        return default
                    value = value[key]
                return value
            # Fall back to underscore notation
            return self.__getattr__(name)
        except AttributeError:
            return default
