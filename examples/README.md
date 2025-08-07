# MQTT Publisher Examples

This directory contains comprehensive examples demonstrating how to use the mqtt_publisher package.

## Prerequisites

1. **Install dependencies**:

   ```bash
   poetry install
   ```

2. **Set up configuration**:

   ```bash
   # Copy and edit the configuration template
   cp config/config.yaml.example config/config.yaml

   # Copy and edit the environment template
   cp .env.example .env
   ```

3. **Configure MQTT broker settings** in your `.env` file:
   ```bash
   MQTT_BROKER_URL=your-broker.example.com
   MQTT_USERNAME=your_username
   MQTT_PASSWORD=your_password
   MQTT_CLIENT_ID=mqtt_publisher_example
   ```

## Examples Overview

### 1. Enhanced Features Example (`enhanced_features_example.py`)

Demonstrates the core MQTT publisher functionality including:

- Automatic port type conversion
- Configuration builder pattern
- Enhanced validation with helpful error messages
- Dictionary-based configuration
- Error handling examples

**Run it**:

```bash
poetry run python examples/enhanced_features_example.py
```

**What it shows**:

- Basic MQTT publisher usage
- Configuration validation
- Different security modes
- Error handling patterns

### 2. Home Assistant Discovery Example (`ha_discovery_complete_example.py`)

Complete demonstration of Home Assistant MQTT Discovery integration:

- Device and sensor creation
- Discovery configuration publishing
- Real-time data publishing
- Status sensor management

**Run it**:

```bash
poetry run python examples/ha_discovery_complete_example.py
```

**What it shows**:

- Creating HA-compatible devices and sensors
- Publishing discovery configurations
- Sensor data with proper JSON formatting
- Device status management
- Integration with Home Assistant

**Home Assistant Integration**:
After running this example, check your Home Assistant installation for:

- Device: "MQTT Publisher Example"
- Sensors: Temperature, Humidity, System Status, Message Count
- All sensors grouped under the device

## Configuration Templates

The `config/` directory contains several configuration templates:

- `config.yaml.example` - Basic MQTT configuration
- `config_ha_discovery.yaml.example` - Enhanced config with HA discovery
- `ha_mqtt_discovery.yaml.example` - HA discovery component templates
- `ha_mqtt_discovery.json.example` - HA discovery JSON templates

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Make sure to run examples with `poetry run`
2. **MQTT Connection Failed**: Check broker URL, credentials, and network connectivity
3. **Configuration File Not Found**: Copy and edit the `.example` files
4. **Permission Denied**: Check MQTT broker authentication settings

### Debug Steps

1. **Test MQTT connection**:

   ```bash
   # Install mosquitto clients
   sudo apt install mosquitto-clients

   # Test connection
   mosquitto_pub -h your-broker.com -p 8883 -u username -P password -t test -m "hello"
   ```

2. **Check configuration loading**:

   ```bash
   poetry run python -c "from mqtt_publisher.config import Config; print(Config('config/config.yaml').get_all())"
   ```

3. **Validate environment variables**:
   ```bash
   poetry run python -c "import os; print('MQTT_BROKER_URL:', os.getenv('MQTT_BROKER_URL'))"
   ```

## Example Output

When running the Home Assistant discovery example, you should see output like:

```
🚀 Starting Home Assistant MQTT Discovery Example
✅ Loaded project environment from: /path/to/.env
📱 Created device: MQTT Publisher Example
🔗 Connecting to MQTT broker: your-broker.com:8883
✅ Connected to MQTT broker
📡 Published discovery configurations for 4 entities
🟢 Published online status
📊 Published sensor data (iteration 1/5) - Temp: 20.0°C, Humidity: 45%
...
🎉 Example completed successfully!
```

## Next Steps

After running these examples:

1. Modify the configuration for your specific use case
2. Create your own sensors and devices
3. Integrate with your Home Assistant installation
4. Build upon the examples for your IoT projects

## Need Help?

- Check the main project README.md
- Review the configuration templates
- Examine the test files for more usage patterns
- Open an issue on the project repository
