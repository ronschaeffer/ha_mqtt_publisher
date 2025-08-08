#!/usr/bin/env python3
"""
Configuration Methods Demonstration

This example shows the different ways to configure:
1. Broker/MQTT settings
2. Device information
3. Entity definitions

The library supports both YAML/config files AND programmatic configuration.
"""

# Method 1: Configuration via YAML files
print("🔧 METHOD 1: YAML Configuration Files")
print("=" * 50)

print("\n📁 YAML Config File Structure:")
print("config/")
print("├── config.yaml              # Main configuration")
print("├── config.yaml.example      # Template with examples")
print("└── config_ha_discovery.yaml.example  # HA-specific template")

# Show YAML configuration content
yaml_broker_config = """
# config/config.yaml - User creates this file
mqtt:
  broker_url: "mqtt.home.local"
  broker_port: 1883
  client_id: "smart_sensor_001"
  security: "username"
  auth:
    username: "mqtt_user"
    password: "mqtt_pass"
  base_topic: "sensors/living_room"

# Application identity (used for HA device registration)
app:
  name: "Living Room Sensor Hub"
  unique_id_prefix: "living_room_hub"
  manufacturer: "Smart Home Corp"
  model: "SensorHub Pro v2.1"
  sw_version: "0.2.0-a735d30-dirty"
  hw_version: "1.0"
  serial_number: "SH2024001"

# Home Assistant Integration
home_assistant:
  enabled: true
  discovery_prefix: "homeassistant"
"""

print("\n📝 Example config.yaml content:")
print(yaml_broker_config)

print("\n" + "=" * 50)
print("🐍 METHOD 2: Programmatic Configuration")
print("=" * 50)

# Show programmatic configuration
programmatic_example = """
from mqtt_publisher import MQTTPublisher, Config
from mqtt_publisher.ha_discovery import Device, Entity, DiscoveryManager

# Method 2A: Load from YAML file
config = Config("config/config.yaml")

# Method 2B: Programmatic configuration (no YAML needed)
config_dict = {
    "mqtt": {
        "broker_url": "mqtt.home.local",
        "broker_port": 1883,
        "client_id": "smart_sensor_001",
        "auth": {"username": "user", "password": "pass"}
    },
    "app": {
        "name": "Living Room Sensors",
        "unique_id_prefix": "living_room",
        "manufacturer": "Smart Corp"
    },
    "home_assistant": {"enabled": True}
}
config = Config(config_dict)

# Initialize MQTT with configuration
publisher = MQTTPublisher(config)

# Device creation (programmatic - not in YAML)
device = Device(
    config=config,  # Uses config for defaults
    name="Living Room Hub",  # Override config
    identifiers=["living_room_001"],
    manufacturer="Smart Home Corp",
    model="Hub Pro v2"
)

# Entity creation (programmatic - not in YAML)
temp_sensor = Entity(
    config=config,
    device=device,
    component="sensor",
    name="Temperature",
    unique_id="living_temp",
    state_topic="sensors/living_room/temperature",
    device_class="temperature",
    unit_of_measurement="°C"
)

# Discovery management
discovery_manager = DiscoveryManager(config, publisher)
discovery_manager.add_device(device)
discovery_manager.add_entity(temp_sensor)
"""

print("📝 Programmatic Configuration Example:")
print(programmatic_example)

print("\n" + "=" * 70)
print("🎯 CONFIGURATION APPROACH BREAKDOWN")
print("=" * 70)

print("\n1️⃣  BROKER/MQTT CONFIGURATION:")
print("   📁 YAML File:")
print("      ✅ User creates config/config.yaml")
print("      ✅ Sets broker_url, port, credentials")
print("      ✅ Environment variable support: ${MQTT_BROKER_URL}")
print("      ✅ TLS/security settings")
print("   🐍 Programmatic:")
print("      ✅ Pass config dict to Config() constructor")
print("      ✅ Override settings in code")

print("\n2️⃣  DEVICE CONFIGURATION:")
print("   📁 YAML File:")
print("      ✅ app.name, app.manufacturer, etc. in config.yaml")
print("      ✅ Used as defaults for Device creation")
print("   🐍 Programmatic:")
print("      ✅ Create Device objects in code")
print("      ✅ Override YAML defaults with kwargs")
print("      ✅ Multiple devices per application")

print("\n3️⃣  ENTITY CONFIGURATION:")
print("   🚫 NOT in YAML files - Always programmatic!")
print("   🐍 Programmatic Only:")
print("      ✅ Create Entity objects in application code")
print("      ✅ Dynamic entity creation based on hardware")
print("      ✅ Runtime entity management via DiscoveryManager")

print("\n" + "=" * 70)
print("📋 TYPICAL WORKFLOW")
print("=" * 70)

workflow = """
1. 📁 User creates config/config.yaml:
   - MQTT broker settings
   - Device defaults (name, manufacturer, etc.)
   - Home Assistant settings

2. 🐍 Application imports library and:
   - Loads config: config = Config("config/config.yaml")
   - Creates MQTTPublisher: publisher = MQTTPublisher(config)
   - Creates Device objects programmatically
   - Creates Entity objects based on actual hardware/sensors
   - Uses DiscoveryManager for dynamic entity management

3. 🔄 Runtime:
   - Entities can be added/removed/updated dynamically
   - No config file changes needed for entity changes
   - Discovery configurations published to MQTT automatically
"""

print(workflow)

print("\n🎨 DESIGN PHILOSOPHY:")
print("   📁 YAML Config: Infrastructure & connection settings")
print("   🐍 Python Code: Business logic & entity definitions")
print("   🔄 Runtime: Dynamic entity lifecycle management")

print("\n✨ This provides the perfect balance of:")
print("   📋 Easy deployment configuration (YAML)")
print("   🎯 Flexible entity management (Python)")
print("   🚀 Dynamic runtime control (DiscoveryManager)")
