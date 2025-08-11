# Configuration Templates

This directory contains configuration templates for the MQTT Publisher package.

Note

- The library's configuration loader (`MQTTConfig.from_dict`) only parses the `mqtt.*` section.
- Any `ha_discovery.*` keys in YAML are not consumed by the library. Home Assistant discovery is configured programmatically via the `mqtt_publisher.ha_discovery` APIs (e.g., `Device`, `Entity`, `publish_discovery_configs`).
- The HA discovery templates here are for reference/examples or for your own higher-level app configuration; they are not read by the core library at runtime.

## Files Overview

### Core Configuration Templates

1. **`config.yaml.example`** - Basic MQTT configuration template

   - Standard MQTT broker settings
   - Authentication options
   - TLS configuration
   - Last Will and Testament

2. **`config_ha_discovery.yaml.example`** - Enhanced configuration with Home Assistant Discovery
   - All basic MQTT settings
   - Home Assistant integration settings
   - Device information
   - Topic structure for HA discovery

### Home Assistant Discovery Templates

3. (Archived) `ha_mqtt_discovery.yaml.example` — superseded by code-based HA discovery setup and the modern `config_ha_discovery.yaml.example`. See `.archive/` for the historical template.

4. (Archived) `ha_mqtt_discovery.json.example` — superseded; HA discovery is typically configured in code via `mqtt_publisher.ha_discovery`. See `.archive/` for the historical template.

## Quick Start

1. **For basic MQTT usage**:

   ```bash
   cp config/config.yaml.example config/config.yaml
   # Edit config.yaml with your MQTT broker settings
   ```

2. **For Home Assistant integration (reference only)**:

   Use `config_ha_discovery.yaml.example` as a guide for your application configuration. The library does not parse `ha_discovery.*` keys from YAML; configure discovery in code using the HA discovery classes.

   HA discovery quick start (Python):

   ```python
   from mqtt_publisher.config import Config
   from mqtt_publisher.ha_discovery import Device, create_sensor, publish_discovery_configs
   from mqtt_publisher import MQTTConfig, MQTTPublisher

   config = Config("config/config.yaml")

   # Define a device and a sensor
   device = Device(config, name="Example Device")
   temp = create_sensor(
      config=config,
      device=device,
      name="Temperature",
      unique_id="temp_example",
      state_topic=f"{config.get('mqtt.base_topic','mqtt_publisher')}/sensors/temperature",
      device_class="temperature",
      unit_of_measurement="°C",
      value_template="{{ value_json.value }}",
   )

   # Connect and publish discovery
   mqtt_cfg = MQTTConfig.from_dict({"mqtt": config.get("mqtt")})

   with MQTTPublisher(config=mqtt_cfg) as pub:
      publish_discovery_configs(config, pub, [temp], device)
      # Publish a sample reading
      pub.publish(temp.state_topic, "{\"value\": 22.3}")
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

## Environment Variable Support

All configuration files support environment variable substitution using `${VARIABLE}` syntax.

**Required environment variables**:

- `MQTT_BROKER_URL` - Your MQTT broker hostname
- `MQTT_USERNAME` - MQTT username
- `MQTT_PASSWORD` - MQTT password
- `MQTT_CLIENT_ID` - Unique client identifier

**Optional environment variables**:

- `MQTT_BROKER_PORT` - Broker port (default: 8883)
- `MQTT_USE_TLS` - Enable TLS (default: true)

## Configuration Hierarchy

The package uses a hierarchical configuration approach:

1. **Shared environment** (`/home/ron/projects/.env`) - Common settings across projects
2. **Project environment** (`.env`) - Project-specific overrides
3. **Configuration file** (`config/config.yaml`) - Structured settings
4. **System environment** - Highest priority overrides

## Security Modes

Choose the appropriate security mode for your setup:

- **`none`**: No authentication (port 1883, plain connection)
- **`username`**: Username/password authentication (any port)
- **`tls`**: TLS encryption + username/password (port 8883)
- **`tls_with_client_cert`**: TLS + client certificates (port 8884)

## Home Assistant Integration

When using Home Assistant discovery:

1. Ensure `discovery_prefix` matches your HA MQTT integration (usually `homeassistant`)
2. Device information will be used to group sensors in HA
3. All sensors will appear under the configured device
4. Status sensors provide connection monitoring

## Examples

See the `examples/` directory for complete usage examples with these configurations.
