#!/usr/bin/env python3
"""
Real-World Configuration Example

This shows a complete example of how a user would configure:
1. Broker settings (YAML)
2. Device info (YAML defaults + code override)
3. Entities (code only)
"""


def demonstrate_yaml_config():
    """Show how configuration works with YAML files."""
    print("📁 YAML Configuration Approach")
    print("=" * 40)

    # User creates this config file
    config_content = """
# config/config.yaml - User creates this
mqtt:
  broker_url: "192.168.1.100"
  broker_port: 1883
  client_id: "smart_sensor_hub"
  auth:
    username: "homeassistant"
    password: "mqtt_password"
  base_topic: "smart_home"

app:
  name: "Smart Sensor Hub"
  unique_id_prefix: "sensor_hub"
  manufacturer: "DIY Smart Home"
  model: "ESP32 Hub v1.0"
  sw_version: "0.1.3-8ad5608-dirty"

home_assistant:
  enabled: true
  discovery_prefix: "homeassistant"
"""

    print("📝 User creates config/config.yaml:")
    print(config_content)

    print("\n🐍 Application code:")
    app_code = """
# main.py - Application code
from mqtt_publisher import Config, MQTTPublisher
from mqtt_publisher.ha_discovery import Device, Entity, DiscoveryManager

# Load YAML configuration
config = Config("config/config.yaml")

# Initialize MQTT (uses YAML settings)
publisher = MQTTPublisher(config)

# Create device (uses YAML defaults, can override)
device = Device(
    config=config,  # Gets name, manufacturer from YAML
    identifiers=["sensor_hub_001"],
    # name and manufacturer come from config.yaml app section
    # Can override: name="Custom Name"
)

# Create entities (always in code, not YAML)
entities = [
    Sensor(config=config, device=device,
           name="Temperature", unique_id="hub_temp",
           state_topic="smart_home/sensors/temperature",
           device_class="temperature", unit_of_measurement="°C"),

    BinarySensor(config=config, device=device,
                name="Motion", unique_id="hub_motion",
                state_topic="smart_home/sensors/motion",
                device_class="motion"),

    Light(config=config, device=device,
          name="Status LED", unique_id="hub_led",
          state_topic="smart_home/lights/status/state",
          command_topic="smart_home/lights/status/command")
]

# Dynamic management
discovery_manager = DiscoveryManager(config, publisher)
discovery_manager.add_device(device)
for entity in entities:
    discovery_manager.add_entity(entity)
"""

    print(app_code)


def demonstrate_programmatic_config():
    """Show pure programmatic configuration."""
    print("\n🐍 Programmatic Configuration Approach")
    print("=" * 40)

    print("📝 No YAML files needed - everything in code:")

    programmatic_code = """
from mqtt_publisher import Config, MQTTPublisher
from mqtt_publisher.ha_discovery import Device, Entity

# Pure programmatic config (no files needed)
config_data = {
    "mqtt": {
        "broker_url": "mqtt.home.local",
        "broker_port": 1883,
        "client_id": "greenhouse_monitor",
        "auth": {"username": "mqtt_user", "password": "secret123"}
    },
    "app": {
        "name": "Greenhouse Monitor",
        "manufacturer": "Garden Tech Solutions"
    },
    "home_assistant": {"enabled": True}
}

config = Config(config_data)
publisher = MQTTPublisher(config)

# Multiple devices in one application
greenhouse_device = Device(
    config=config,
    name="Greenhouse Sensors",
    identifiers=["greenhouse_001"],
    model="Environmental Monitor v2"
)

irrigation_device = Device(
    config=config,
    name="Irrigation System",
    identifiers=["irrigation_001"],
    model="Smart Sprinkler v1"
)

# Entities for each device
greenhouse_entities = [
    Entity(config=config, device=greenhouse_device,
           component="sensor", name="Soil Moisture",
           state_topic="greenhouse/soil/moisture",
           device_class="moisture", unit_of_measurement="%"),

    Entity(config=config, device=greenhouse_device,
           component="sensor", name="Light Level",
           state_topic="greenhouse/light/level",
           device_class="illuminance", unit_of_measurement="lx")
]

irrigation_entities = [
    Entity(config=config, device=irrigation_device,
           component="switch", name="Zone 1 Sprinkler",
           state_topic="irrigation/zone1/state",
           command_topic="irrigation/zone1/command"),

    Entity(config=config, device=irrigation_device,
           component="sensor", name="Water Pressure",
           state_topic="irrigation/pressure",
           unit_of_measurement="PSI")
]

# Manage everything programmatically
discovery_manager = DiscoveryManager(config, publisher)
discovery_manager.add_device(greenhouse_device)
discovery_manager.add_device(irrigation_device)

for entity in greenhouse_entities + irrigation_entities:
    discovery_manager.add_entity(entity)
"""

    print(programmatic_code)


def show_configuration_summary():
    """Show the configuration decision matrix."""
    print("\n📊 CONFIGURATION DECISION MATRIX")
    print("=" * 50)

    matrix = """
WHAT TO CONFIGURE          | YAML FILE | PROGRAMMATIC | BEST PRACTICE
---------------------------|-----------|--------------|---------------
MQTT Broker URL/Port       |    ✅     |      ✅      | YAML + ENV vars
MQTT Credentials          |    ✅     |      ✅      | YAML + ENV vars
TLS/Security Settings     |    ✅     |      ✅      | YAML
Device Defaults           |    ✅     |      ✅      | YAML defaults
Device Instances          |    ❌     |      ✅      | Code only
Entity Definitions        |    ❌     |      ✅      | Code only
Entity Management         |    ❌     |      ✅      | Code only
Runtime Changes           |    ❌     |      ✅      | Code only

🎯 RECOMMENDED APPROACH:
   📁 YAML: Infrastructure (broker, credentials, device defaults)
   🐍 CODE: Business logic (devices, entities, runtime management)
"""

    print(matrix)

    print("\n🔄 CONFIGURATION INHERITANCE:")
    inheritance = """
config.yaml (app section)
    ↓ (provides defaults)
Device(config=config, **overrides)
    ↓ (provides device context)
Entity(config=config, device=device, **specific_attrs)
"""
    print(inheritance)


if __name__ == "__main__":
    demonstrate_yaml_config()
    demonstrate_programmatic_config()
    show_configuration_summary()

    print("\n✨ KEY BENEFITS OF THIS APPROACH:")
    print("   🎯 Deployment flexibility (YAML for ops, code for logic)")
    print("   🔒 Secure credential management (environment variables)")
    print("   🚀 Dynamic entity management (runtime add/remove/update)")
    print("   📱 Multiple devices per application")
    print("   🔄 Configuration inheritance (YAML → Device → Entity)")
    print("   🛠️  No restart needed for entity changes")
