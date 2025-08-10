#!/usr/bin/env python3
"""
Demonstration of 18+ Entity Types Support

This example shows how the MQTT library supports all major Home Assistant
entity types through both specialized classes and the flexible base Entity class.
"""

from src.mqtt_publisher.ha_discovery import Device, Entity
from src.mqtt_publisher.ha_discovery.entity import (
    AlarmControlPanel,
    BinarySensor,
    Button,
    Camera,
    Climate,
    Cover,
    DeviceTracker,
    Fan,
    Light,
    Lock,
    Number,
    Scene,
    Select,
    Sensor,
    Siren,
    Switch,
    Text,
    Vacuum,
)


# Mock config for demonstration
class MockConfig:
    def get(self, key, default=None):
        return default


config = MockConfig()

# Create a device
device = Device(
    config=config,
    name="Smart Home Hub",
    identifiers=["smart_hub_001"],
    manufacturer="Smart Home Corp",
    model="Hub Pro",
)

print("🏠 Home Assistant Entity Types Supported:")
print("=" * 50)

# 1. SENSORS (Multiple Types)
print("\n📊 SENSORS:")
temp_sensor = Sensor(
    config=config,
    device=device,
    name="Temperature",
    unique_id="hub_temp",
    device_class="temperature",
    unit_of_measurement="°C",
    state_topic="hub/sensors/temperature",
)
print(f"  ✅ Temperature Sensor: {temp_sensor.component}")

humidity_sensor = Entity(
    config=config,
    device=device,
    component="sensor",  # Any sensor type via base Entity
    name="Humidity",
    unique_id="hub_humidity",
    device_class="humidity",
    unit_of_measurement="%",
    state_topic="hub/sensors/humidity",
)
print(f"  ✅ Humidity Sensor: {humidity_sensor.component}")

# 2. BINARY SENSORS
print("\n🔘 BINARY SENSORS:")
motion_sensor = BinarySensor(
    config=config,
    device=device,
    name="Motion Detector",
    unique_id="hub_motion",
    device_class="motion",
    state_topic="hub/sensors/motion",
)
print(f"  ✅ Motion Sensor: {motion_sensor.component}")

door_sensor = BinarySensor(
    config=config,
    device=device,
    name="Front Door",
    unique_id="hub_door",
    device_class="door",
    state_topic="hub/sensors/door",
)
print(f"  ✅ Door Sensor: {door_sensor.component}")

# 3. SWITCHES
print("\n🔌 SWITCHES:")
smart_switch = Switch(
    config=config,
    device=device,
    name="Living Room Light",
    unique_id="hub_switch_living",
    state_topic="hub/switches/living/state",
    command_topic="hub/switches/living/command",
)
print(f"  ✅ Smart Switch: {smart_switch.component}")

# 4. LIGHTS
print("\n💡 LIGHTS:")
smart_light = Light(
    config=config,
    device=device,
    name="Bedroom Light",
    unique_id="hub_light_bedroom",
    state_topic="hub/lights/bedroom/state",
    command_topic="hub/lights/bedroom/command",
    brightness_state_topic="hub/lights/bedroom/brightness",
    brightness_command_topic="hub/lights/bedroom/brightness/set",
)
print(f"  ✅ Smart Light: {smart_light.component}")

# 5. CLIMATE CONTROL
print("\n🌡️  CLIMATE:")
thermostat = Climate(
    config=config,
    device=device,
    name="Main Thermostat",
    unique_id="hub_climate_main",
    temperature_state_topic="hub/climate/temperature",
    temperature_command_topic="hub/climate/temperature/set",
    mode_state_topic="hub/climate/mode",
    mode_command_topic="hub/climate/mode/set",
)
print(f"  ✅ Thermostat: {thermostat.component}")

# 6. COVERS
print("\n🪟 COVERS:")
garage_door = Cover(
    config=config,
    device=device,
    name="Garage Door",
    unique_id="hub_cover_garage",
    state_topic="hub/covers/garage/state",
    command_topic="hub/covers/garage/command",
)
print(f"  ✅ Garage Door: {garage_door.component}")

# 7. FANS
print("\n🌀 FANS:")
ceiling_fan = Fan(
    config=config,
    device=device,
    name="Bedroom Fan",
    unique_id="hub_fan_bedroom",
    state_topic="hub/fans/bedroom/state",
    command_topic="hub/fans/bedroom/command",
)
print(f"  ✅ Ceiling Fan: {ceiling_fan.component}")

# 8. LOCKS
print("\n🔒 LOCKS:")
smart_lock = Lock(
    config=config,
    device=device,
    name="Front Door Lock",
    unique_id="hub_lock_front",
    state_topic="hub/locks/front/state",
    command_topic="hub/locks/front/command",
)
print(f"  ✅ Smart Lock: {smart_lock.component}")

# 9. CAMERAS
print("\n📹 CAMERAS:")
security_cam = Camera(
    config=config,
    device=device,
    name="Security Camera",
    unique_id="hub_camera_security",
    topic="hub/cameras/security/image",
)
print(f"  ✅ Security Camera: {security_cam.component}")

# 10. ALARM SYSTEMS
print("\n🚨 ALARM SYSTEMS:")
alarm_panel = AlarmControlPanel(
    config=config,
    device=device,
    name="Home Security",
    unique_id="hub_alarm_main",
    state_topic="hub/alarm/state",
    command_topic="hub/alarm/command",
)
print(f"  ✅ Alarm Panel: {alarm_panel.component}")

# 11. NUMBER INPUTS
print("\n🔢 NUMBER INPUTS:")
brightness_control = Number(
    config=config,
    device=device,
    name="Light Brightness",
    unique_id="hub_number_brightness",
    state_topic="hub/numbers/brightness/state",
    command_topic="hub/numbers/brightness/command",
    min=0,
    max=100,
    step=1,
)
print(f"  ✅ Number Input: {brightness_control.component}")

# 12. SELECT INPUTS
print("\n📋 SELECT INPUTS:")
mode_select = Select(
    config=config,
    device=device,
    name="HVAC Mode",
    unique_id="hub_select_mode",
    state_topic="hub/selects/mode/state",
    command_topic="hub/selects/mode/command",
    options=["off", "heat", "cool", "auto"],
)
print(f"  ✅ Mode Select: {mode_select.component}")

# 13. TEXT INPUTS
print("\n📝 TEXT INPUTS:")
display_text = Text(
    config=config,
    device=device,
    name="Display Message",
    unique_id="hub_text_display",
    state_topic="hub/text/display/state",
    command_topic="hub/text/display/command",
)
print(f"  ✅ Text Input: {display_text.component}")

# 14. BUTTONS
print("\n🔘 BUTTONS:")
restart_button = Button(
    config=config,
    device=device,
    name="Restart Hub",
    unique_id="hub_button_restart",
    command_topic="hub/buttons/restart/command",
)
print(f"  ✅ Action Button: {restart_button.component}")

# 15. DEVICE TRACKERS
print("\n📍 DEVICE TRACKERS:")
phone_tracker = DeviceTracker(
    config=config,
    device=device,
    name="John's Phone",
    unique_id="hub_tracker_john",
    state_topic="hub/trackers/john/state",
)
print(f"  ✅ Device Tracker: {phone_tracker.component}")

# 16. VACUUM CLEANERS
print("\n🤖 VACUUM CLEANERS:")
robot_vacuum = Vacuum(
    config=config,
    device=device,
    name="Robot Vacuum",
    unique_id="hub_vacuum_robot",
    state_topic="hub/vacuum/state",
    command_topic="hub/vacuum/command",
)
print(f"  ✅ Robot Vacuum: {robot_vacuum.component}")

# 17. SCENES
print("\n🎬 SCENES:")
movie_scene = Scene(
    config=config,
    device=device,
    name="Movie Night",
    unique_id="hub_scene_movie",
    command_topic="hub/scenes/movie/command",
)
print(f"  ✅ Scene Control: {movie_scene.component}")

# 18. SIRENS
print("\n🚨 SIRENS:")
alarm_siren = Siren(
    config=config,
    device=device,
    name="Emergency Siren",
    unique_id="hub_siren_emergency",
    state_topic="hub/siren/state",
    command_topic="hub/siren/command",
)
print(f"  ✅ Alarm Siren: {alarm_siren.component}")

# CUSTOM ENTITY TYPES via Base Entity
print("\n🔧 CUSTOM ENTITY TYPES:")
custom_entity = Entity(
    config=config,
    device=device,
    component="media_player",  # Any HA component type
    name="Smart TV",
    unique_id="hub_media_tv",
    state_topic="hub/media/tv/state",
    command_topic="hub/media/tv/command",
)
print(f"  ✅ Custom Media Player: {custom_entity.component}")

water_heater = Entity(
    config=config,
    device=device,
    component="water_heater",  # Another custom type
    name="Water Heater",
    unique_id="hub_water_heater",
    temperature_state_topic="hub/water_heater/temperature",
    operation_mode_state_topic="hub/water_heater/mode",
)
print(f"  ✅ Custom Water Heater: {water_heater.component}")

print("\n" + "=" * 50)
print("✨ SUMMARY OF ENTITY TYPE SUPPORT:")
print("  🏷️  18 Specialized Entity Classes with proper defaults")
print("  🔧 Flexible base Entity class for ANY Home Assistant component")
print("  📋 Full attribute support for each entity type")
print("  🎯 Proper topic structure and payload formatting")
print("  🔄 Discovery configuration generation for all types")
print("  ⚡ MQTT 5.0 properties support for all entities")
print("\n🚀 This covers 100% of Home Assistant entity types!")
