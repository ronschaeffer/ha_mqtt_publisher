# Configuration Templates

This directory contains configuration templates for the MQTT Publisher package.

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

3. **`ha_mqtt_discovery.yaml.example`** - YAML template for HA discovery components

   - Device and component definitions
   - Discovery topic structure
   - Component configuration options

4. **`ha_mqtt_discovery.json.example`** - JSON template for HA discovery components
   - Same structure as YAML but in JSON format
   - Useful for programmatic generation

## Quick Start

1. **For basic MQTT usage**:

   ```bash
   cp config/config.yaml.example config/config.yaml
   # Edit config.yaml with your MQTT broker settings
   ```

2. **For Home Assistant integration**:

   ```bash
   cp config/config_ha_discovery.yaml.example config/config.yaml
   # Edit config.yaml with your settings and HA preferences
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
