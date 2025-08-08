#!/usr/bin/env python3
"""
Comprehensive Full-Featured MQTT Library Example.

This example demonstrates all the full-featured capabilities of the MQTT library:
- MQTT 5.0 protocol support with properties
- Bidirectional communication (publish + subscribe)
- Complete Home Assistant discovery management
- Discovery lifecycle management
- Modern callback handling
- Topic-specific callbacks
- Comprehensive device and entity management

This showcases a truly full-featured MQTT library implementation.
"""

import asyncio
import json
import logging
from pathlib import Path
import time

from mqtt_publisher.config import load_config
from mqtt_publisher.ha_discovery import Device, DiscoveryManager, Entity, StatusSensor
from mqtt_publisher.publisher import MQTTPublisher

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class FullFeaturedMQTTApplication:
    """
    Demonstrates a complete full-featured MQTT application with:
    - MQTT 5.0 protocol support
    - Bidirectional communication
    - Home Assistant discovery management
    - Discovery lifecycle management
    - Modern callback architecture
    """

    def __init__(self, config_path: str):
        self.config = load_config(config_path)
        self.publisher = None
        self.discovery_manager = None
        self.device = None
        self.entities = {}

    async def initialize(self):
        """Initialize the MQTT connection and discovery manager."""
        try:
            # Initialize MQTT publisher with MQTT 5.0 support
            self.publisher = MQTTPublisher(
                config=self.config,
                protocol_version="MQTTv5",  # Use MQTT 5.0 for full features
            )

            # Set up modern callback handling
            self.setup_callbacks()

            # Connect to MQTT broker
            if self.publisher.connect():
                logger.info("Connected to MQTT broker with MQTT 5.0")
            else:
                raise Exception("Failed to connect to MQTT broker")

            # Initialize discovery manager for lifecycle management
            self.discovery_manager = DiscoveryManager(
                config=self.config, publisher=self.publisher
            )

            # Create main device
            self.create_device()

            # Set up subscriptions for bidirectional communication
            await self.setup_subscriptions()

            logger.info("Full-featured MQTT application initialized")

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise

    def setup_callbacks(self):
        """Set up modern callback handling with topic-specific callbacks."""

        # Global message callback
        def on_message_received(client, userdata, message):
            logger.info(
                f"Received message on {message.topic}: {message.payload.decode()}"
            )

        self.publisher.set_message_callback(on_message_received)

        # Topic-specific callbacks for different functionality
        def on_command_received(client, userdata, message):
            """Handle commands sent to this device."""
            try:
                command = json.loads(message.payload.decode())
                logger.info(f"Command received: {command}")
                self.handle_command(command)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON command: {message.payload.decode()}")

        def on_config_received(client, userdata, message):
            """Handle configuration updates."""
            try:
                config_update = json.loads(message.payload.decode())
                logger.info(f"Configuration update: {config_update}")
                self.handle_config_update(config_update)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON config: {message.payload.decode()}")

        # Add topic-specific callbacks
        self.publisher.add_topic_callback("device/+/command", on_command_received)
        self.publisher.add_topic_callback("device/+/config", on_config_received)

    def create_device(self):
        """Create a comprehensive device with all supported fields."""
        self.device = Device(
            name="Full-Featured MQTT Device",
            identifiers=["mqtt_device_001"],
            manufacturer="MQTT Publisher Library",
            model="Full-Featured Device v2.0",
            sw_version="0.1.3-2e988e2-dirty",
            hw_version="1.0",
            configuration_url="http://192.168.1.100:8080/config",
            connections=[["ip", "192.168.1.100"], ["mac", "AA:BB:CC:DD:EE:FF"]],
            suggested_area="Living Room",
            via_device="gateway_001",
            serial_number="MFD2024001",
        )

        # Add device to discovery manager
        self.discovery_manager.add_device(self.device)

    async def setup_subscriptions(self):
        """Set up subscriptions for bidirectional communication."""

        # Subscribe to command topics
        command_topics = [
            "device/mqtt_device_001/command",
            "device/mqtt_device_001/config",
            "homeassistant/device/mqtt_device_001/+/command",
        ]

        # Subscribe with MQTT 5.0 properties
        mqtt5_properties = {
            "subscription_identifier": 1,
            "user_properties": [("client", "full_featured_mqtt")],
        }

        for topic in command_topics:
            success = self.publisher.subscribe(
                topic=topic, qos=1, properties=mqtt5_properties
            )
            if success:
                logger.info(f"Subscribed to {topic}")
            else:
                logger.error(f"Failed to subscribe to {topic}")

    def create_comprehensive_entities(self):
        """Create a comprehensive set of entities demonstrating all capabilities."""

        # Temperature sensor with full configuration
        temp_sensor = Entity(
            name="Temperature",
            component="sensor",
            unique_id="mqtt_device_001_temperature",
            device=self.device,
            device_class="temperature",
            unit_of_measurement="°C",
            state_topic="device/mqtt_device_001/temperature",
            value_template="{{ value_json.temperature }}",
            availability_topic="device/mqtt_device_001/availability",
            expire_after=300,
            force_update=True,
            extra_attributes={
                "icon": "mdi:thermometer",
                "suggested_display_precision": 1,
            },
        )

        # Binary sensor for motion detection
        motion_sensor = Entity(
            name="Motion Detector",
            component="binary_sensor",
            unique_id="mqtt_device_001_motion",
            device=self.device,
            device_class="motion",
            state_topic="device/mqtt_device_001/motion",
            availability_topic="device/mqtt_device_001/availability",
            payload_on="detected",
            payload_off="clear",
            off_delay=30,
            extra_attributes={"icon": "mdi:motion-sensor"},
        )

        # Light switch with command capability
        light_switch = Entity(
            name="Smart Light",
            component="light",
            unique_id="mqtt_device_001_light",
            device=self.device,
            state_topic="device/mqtt_device_001/light/state",
            command_topic="device/mqtt_device_001/light/command",
            availability_topic="device/mqtt_device_001/availability",
            brightness_state_topic="device/mqtt_device_001/light/brightness",
            brightness_command_topic="device/mqtt_device_001/light/brightness/set",
            brightness_scale=255,
            payload_on="ON",
            payload_off="OFF",
            optimistic=False,
            extra_attributes={"supported_features": ["brightness"]},
        )

        # Climate control entity
        climate_control = Entity(
            name="Climate Control",
            component="climate",
            unique_id="mqtt_device_001_climate",
            device=self.device,
            temperature_state_topic="device/mqtt_device_001/climate/temperature",
            temperature_command_topic="device/mqtt_device_001/climate/temperature/set",
            mode_state_topic="device/mqtt_device_001/climate/mode",
            mode_command_topic="device/mqtt_device_001/climate/mode/set",
            availability_topic="device/mqtt_device_001/availability",
            min_temp=10,
            max_temp=35,
            temp_step=0.5,
            modes=["off", "heat", "cool", "auto"],
            extra_attributes={"icon": "mdi:thermostat"},
        )

        # Status sensor using the specialized StatusSensor class
        status_sensor = StatusSensor(
            device=self.device,
            unique_id_suffix="status",
            additional_attributes={
                "version": "2.0.0",
                "protocol": "MQTT 5.0",
                "features": [
                    "bidirectional",
                    "discovery_management",
                    "modern_callbacks",
                ],
            },
        )

        # Store entities
        self.entities = {
            "temperature": temp_sensor,
            "motion": motion_sensor,
            "light": light_switch,
            "climate": climate_control,
            "status": status_sensor,
        }

        # Add all entities to discovery manager
        for entity in self.entities.values():
            success = self.discovery_manager.add_entity(entity)
            if success:
                logger.info(f"Added entity: {entity.name}")
            else:
                logger.error(f"Failed to add entity: {entity.name}")

    def handle_command(self, command: dict):
        """Handle incoming commands."""
        command_type = command.get("type")
        entity_id = command.get("entity")
        value = command.get("value")

        logger.info(f"Processing command: {command_type} for {entity_id} = {value}")

        if command_type == "light" and entity_id == "light":
            # Handle light commands
            if value in ["ON", "OFF"]:
                # Publish state update with MQTT 5.0 properties
                self.publish_with_properties(
                    topic="device/mqtt_device_001/light/state",
                    payload=value,
                    properties={
                        "user_properties": [("command_response", "true")],
                        "correlation_data": command.get("correlation_id", ""),
                    },
                )
        elif command_type == "climate" and entity_id == "climate":
            # Handle climate commands
            if "temperature" in command:
                temp = command["temperature"]
                self.publish_with_properties(
                    topic="device/mqtt_device_001/climate/temperature",
                    payload=str(temp),
                    properties={"user_properties": [("command_response", "true")]},
                )

    def handle_config_update(self, config: dict):
        """Handle configuration updates."""
        logger.info(f"Applying configuration update: {config}")

        # Example: Update entity attributes
        if "entities" in config:
            for entity_id, updates in config["entities"].items():
                if entity_id in self.entities:
                    success = self.discovery_manager.update_entity(
                        self.entities[entity_id].unique_id, **updates
                    )
                    if success:
                        logger.info(f"Updated entity {entity_id}")
                    else:
                        logger.error(f"Failed to update entity {entity_id}")

    def publish_with_properties(
        self, topic: str, payload: str, properties: dict | None = None
    ):
        """Publish with MQTT 5.0 properties."""
        return self.publisher.publish(
            topic=topic, payload=payload, properties=properties or {}
        )

    async def publish_sensor_data(self):
        """Publish sensor data demonstrating full publishing capabilities."""
        import random

        while True:
            try:
                # Simulate sensor readings
                temperature = round(random.uniform(18.0, 25.0), 1)
                motion = random.choice(["detected", "clear"])

                # Create comprehensive sensor data
                sensor_data = {
                    "temperature": temperature,
                    "humidity": round(random.uniform(40.0, 70.0), 1),
                    "pressure": round(random.uniform(990.0, 1030.0), 1),
                    "timestamp": int(time.time()),
                    "device_id": "mqtt_device_001",
                }

                # Publish with MQTT 5.0 properties
                mqtt5_properties = {
                    "message_expiry_interval": 300,
                    "user_properties": [
                        ("sensor_type", "environmental"),
                        ("data_version", "2.0"),
                    ],
                    "content_type": "application/json",
                }

                # Publish temperature data
                success = self.publish_with_properties(
                    topic="device/mqtt_device_001/temperature",
                    payload=json.dumps(sensor_data),
                    properties=mqtt5_properties,
                )

                if success:
                    logger.info(f"Published sensor data: {sensor_data}")
                else:
                    logger.error("Failed to publish sensor data")

                # Publish motion data
                self.publish_with_properties(
                    topic="device/mqtt_device_001/motion",
                    payload=motion,
                    properties={"user_properties": [("sensor_type", "motion")]},
                )

                # Publish availability
                self.publish_with_properties(
                    topic="device/mqtt_device_001/availability",
                    payload="online",
                    properties={"message_expiry_interval": 600},
                )

                await asyncio.sleep(30)  # Publish every 30 seconds

            except Exception as e:
                logger.error(f"Error publishing sensor data: {e}")
                await asyncio.sleep(5)

    def demonstrate_discovery_management(self):
        """Demonstrate discovery lifecycle management capabilities."""
        logger.info("Demonstrating discovery management features...")

        # List all entities and devices
        entities = self.discovery_manager.list_entities()
        devices = self.discovery_manager.list_devices()

        logger.info(f"Managed entities: {len(entities)}")
        for entity in entities:
            logger.info(f"  - {entity['name']} ({entity['component']})")

        logger.info(f"Managed devices: {len(devices)}")
        for device in devices:
            logger.info(f"  - {device['name']} ({device['entity_count']} entities)")

        # Demonstrate entity status
        for entity_id, entity in self.entities.items():
            status = self.discovery_manager.get_entity_status(entity.unique_id)
            if status:
                logger.info(f"Entity {entity_id} status: {status}")

    async def run(self):
        """Run the full-featured MQTT application."""
        try:
            # Initialize everything
            await self.initialize()

            # Create comprehensive entities
            self.create_comprehensive_entities()

            # Demonstrate discovery management
            self.demonstrate_discovery_management()

            # Start publishing sensor data
            logger.info("Starting sensor data publishing...")
            await self.publish_sensor_data()

        except KeyboardInterrupt:
            logger.info("Shutting down...")
        except Exception as e:
            logger.error(f"Application error: {e}")
        finally:
            await self.cleanup()

    async def cleanup(self):
        """Clean up resources."""
        if self.discovery_manager:
            # Optionally clear all discoveries on shutdown
            # self.discovery_manager.clear_all_discoveries()
            pass

        if self.publisher:
            self.publisher.disconnect()
            logger.info("Disconnected from MQTT broker")


async def main():
    """Main entry point."""
    config_path = Path("config/config.yaml")

    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        logger.info(
            "Please copy config/config.yaml.example to config/config.yaml and configure it"
        )
        return

    app = FullFeaturedMQTTApplication(str(config_path))
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
