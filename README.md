HA MQTT Publisher

A Python library for MQTT publishing and subscribing, plus safe, typed Home Assistant (HA) MQTT Discovery helpers. It focuses on clean configuration, strict-but-extensible validation for HA fields, and practical defaults so you can ship stable, HA-friendly topics and entities.

Key capabilities
- MQTT client usage: username/password, TLS, keepalive, client_id, LWT
- HA Discovery: device/entity builders, status sensor, one-time discovery publishing, deterministic object_id
- Strict validation by default with optional extra_allowed extensions
- YAML- and env-driven configuration

Installation
- Python 3.9+ is recommended.
- Install: pip install ha-mqtt-publisher

Configuration overview
Provide a simple YAML file to configure MQTT and optional HA behavior.

Example config.yaml
	mqtt:
		host: localhost
		port: 1883
		username: user
		password: pass
		client_id: ha-mqtt-bridge-1
		tls: false
		keepalive: 60
		base_topic: mqtt_publisher
		lwt:
			topic: system/ha_mqtt_publisher/status
			payload_available: online
			payload_not_available: offline
			qos: 1
			retain: true

	home_assistant:
		discovery_prefix: homeassistant
		strict_validation: true
		discovery_state_file: .ha_discovery_state.json
		extra_allowed: {}

Environment variables can override keys such as MQTT_HOST, MQTT_USERNAME, MQTT_PASSWORD, MQTT_PORT, etc.

Publishing quick start
This example uses paho-mqtt directly with configuration from YAML.

	import json
	import ssl
	from pathlib import Path
	import paho.mqtt.client as mqtt
	import yaml

	cfg = yaml.safe_load(Path("config.yaml").read_text())
	m = cfg["mqtt"]

	client = mqtt.Client(client_id=m.get("client_id"))
	if m.get("tls"):
			client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
	if m.get("username"):
			client.username_pw_set(m["username"], m.get("password"))

	lwt = m.get("lwt", {})
	if lwt:
			client.will_set(
					lwt.get("topic", "system/ha_mqtt_publisher/status"),
					payload=lwt.get("payload_not_available", "offline"),
					qos=int(lwt.get("qos", 1)),
					retain=bool(lwt.get("retain", True)),
			)

	client.connect(m["host"], int(m.get("port", 1883)), int(m.get("keepalive", 60)))

	topic = f"{m.get('base_topic','mqtt_publisher')}/demo/hello"
	client.publish(topic, json.dumps({"msg": "hello"}), qos=1, retain=True)

	client.loop_start()
	# ... work ...
	client.loop_stop()
	client.disconnect()

Subscribing quick start
	import paho.mqtt.client as mqtt
	from pathlib import Path
	import yaml

	cfg = yaml.safe_load(Path("config.yaml").read_text())
	m = cfg["mqtt"]

	def on_message(_c, _u, msg):
			print(msg.topic, msg.payload.decode("utf-8"))

	client = mqtt.Client(client_id=m.get("client_id", "ha-mqtt-sub"))
	if m.get("username"):
			client.username_pw_set(m["username"], m.get("password"))
	client.on_message = on_message
	client.connect(m["host"], int(m.get("port", 1883)), int(m.get("keepalive", 60)))
	client.subscribe(f"{m.get('base_topic','mqtt_publisher')}/#", qos=1)
	client.loop_forever()

Home Assistant discovery
The discovery layer lets you declare devices and entities and publishes discovery topics/payloads with strong validation and helpful defaults.

Imports
	from ha_mqtt_publisher.ha_discovery import (
			Device,
			StatusSensor,
			create_sensor,
			publish_discovery_configs,
	)
	from ha_mqtt_publisher.ha_discovery.constants import (
			EntityCategory,
			AvailabilityMode,
			SensorStateClass,
			SensorDeviceClass,
			BINARY_SENSOR_DEVICE_CLASSES,
			SENSOR_DEVICE_CLASSES,
	)

Minimal example
	import paho.mqtt.client as mqtt
	from ha_mqtt_publisher.ha_discovery import (
			Device,
			StatusSensor,
			create_sensor,
			publish_discovery_configs,
	)
	from ha_mqtt_publisher.ha_discovery.constants import (
			SensorDeviceClass, SensorStateClass, EntityCategory
	)

	device = Device(
			identifiers=["ha_mqtt_publisher_demo"],
			name="HA MQTT Publisher Demo",
			manufacturer="HA MQTT Publisher",
			model="Example",
			sw_version="1.0.0",
	)

	temperature = create_sensor(
			name="Room Temperature",
			unique_id="room_temp_1",
			device=device,
			unit_of_measurement="°C",
			device_class=SensorDeviceClass("temperature"),
			state_class=SensorStateClass("measurement"),
			entity_category=None,
	)

	status = StatusSensor(
			name="Bridge Status",
			unique_id="bridge_status",
			device=device,
			entity_category=EntityCategory("diagnostic"),
	)

	client = mqtt.Client()
	client.connect("localhost", 1883, 60)

	publish_discovery_configs(
			client=client,
			discovery_prefix="homeassistant",
			entities=[temperature, status],
			availability_mode="all",
			state_file=".ha_discovery_state.json",
	)

	client.publish(temperature.state_topic, "23.4", qos=1, retain=True)
	client.publish(status.state_topic, "online", qos=1, retain=True)

Validation and extensibility
- Strict validation: invalid HA values raise by default (toggleable via configuration)
- extra_allowed: extend allowed sets for new HA values without waiting for a release
	- entity_categories, availability_modes, sensor_state_classes,
		sensor_device_classes, binary_sensor_device_classes

Selected constants
	from ha_mqtt_publisher.ha_discovery.constants import (
			ENTITY_CATEGORIES, AVAILABILITY_MODES,
			SENSOR_STATE_CLASSES, SENSOR_DEVICE_CLASSES,
			BINARY_SENSOR_DEVICE_CLASSES,
	)

Development
- Create a virtual environment and install dev deps
	- pip install -U pip && pip install -e .[dev]
- Lint and format
	- ruff check . && ruff format .
- Run tests
	- pytest -q

FAQ
- Do I need HA as a dependency? No, we publish HA-compatible payloads over MQTT.
- Should I re-publish discovery every run? Not necessary; the optional state file enables one-time publishing per unique_id.

License
MIT
