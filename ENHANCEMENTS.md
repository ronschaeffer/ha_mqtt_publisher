# MQTT Publisher Enhancement Documentation

## 🚀 Enhanced Features

The MQTT Publisher library has been enhanced with improved configuration handling, validation, and user experience based on real-world usage feedback.

### ✨ New Features

#### 1. **Automatic Port Type Conversion**

String port values are automatically converted to integers, preventing common connection failures.

```python
from mqtt_publisher import MQTTPublisher

# String ports are automatically converted
publisher = MQTTPublisher(
    broker_url="mqtt.example.com",
    broker_port="8883",  # ✅ Automatically converted to int
    client_id="my_client"
)
```

#### 2. **Configuration Builder Pattern**

The new `MQTTConfig` utility class provides convenient methods to build and validate MQTT configurations.

```python
from mqtt_publisher import MQTTConfig, MQTTPublisher

# Build configuration with automatic validation
config = MQTTConfig.build_config(
    broker_url="mqtt.example.com",
    broker_port="8883",  # Auto-converted to int
    client_id="my_client",
    security="username",
    username="user",
    password="password",
    max_retries="3"  # Auto-converted to int
)

# Use the configuration
publisher = MQTTPublisher(config=config)
```

#### 3. **Enhanced Constructor with Config Dict Support**

The `MQTTPublisher` constructor now accepts either individual parameters or a complete configuration dictionary.

```python
# Option 1: Individual parameters (existing behavior)
publisher = MQTTPublisher(
    broker_url="mqtt.example.com",
    broker_port=8883,
    client_id="my_client"
)

# Option 2: Configuration dictionary (new)
config = {"broker_url": "mqtt.example.com", "broker_port": 8883, "client_id": "my_client"}
publisher = MQTTPublisher(config=config)
```

#### 4. **YAML-like Configuration Support**

Build MQTT configurations from nested dictionaries (perfect for YAML configs).

```python
# Simulate YAML configuration
yaml_config = {
    "mqtt": {
        "broker_url": "mqtt.example.com",
        "broker_port": 8883,
        "client_id": "my_client",
        "security": "username",
        "auth": {
            "username": "user",
            "password": "password"
        },
        "tls": {
            "verify": True,
            "ca_cert": "/path/to/ca.pem"
        }
    }
}

# Convert to MQTT config
mqtt_config = MQTTConfig.from_dict(yaml_config)
publisher = MQTTPublisher(config=mqtt_config)
```

#### 5. **Comprehensive Configuration Validation**

Enhanced validation with detailed, helpful error messages that guide users to fix configuration issues.

```python
try:
    config = MQTTConfig.build_config(
        broker_port="70000",  # Invalid port
        security="username"
        # Missing broker_url, client_id, and auth
    )
except ValueError as e:
    print(e)
    # Output:
    # MQTT configuration errors:
    # - broker_url is required
    # - broker_port must be integer 1-65535, got: 70000
    # - client_id is required
    # - username and password required when security='username'
```

#### 6. **Enhanced Error Messages for Connection Issues**

Specific guidance for common connection problems, especially TLS/port mismatches.

```python
publisher = MQTTPublisher(
    broker_url="mqtt.example.com",
    broker_port=1883,
    client_id="my_client",
    tls={"verify": True}  # TLS enabled with non-TLS port
)
# Logs warning: "TLS enabled but using non-TLS port 1883. Consider port 8883 for TLS"
```

#### 7. **Smart Configuration Warnings**

The library now provides helpful warnings for questionable but potentially valid configurations without preventing initialization.

**Configuration Warnings** (logged but non-fatal):

- TLS enabled but using non-TLS port 1883
- TLS disabled but using TLS port 8883

**Configuration Errors** (fatal):

- Missing required fields (broker_url, client_id)
- Invalid port ranges
- Missing authentication when required by security mode
- Missing TLS configuration when required by security mode

### 🔧 Migration Guide

#### From Individual Parameters to Config Dict

**Before:**

```python
publisher = MQTTPublisher(
    broker_url="mqtt.example.com",
    broker_port=8883,
    client_id="my_client",
    security="username",
    auth={"username": "user", "password": "pass"}
)
```

**After (recommended):**

```python
config = MQTTConfig.build_config(
    broker_url="mqtt.example.com",
    broker_port="8883",  # String is fine now
    client_id="my_client",
    security="username",
    username="user",
    password="pass"
)
publisher = MQTTPublisher(config=config)
```

#### Working with YAML Configurations

```python
import yaml
from mqtt_publisher import MQTTConfig, MQTTPublisher

# Load YAML configuration
with open("config.yaml") as f:
    config_data = yaml.safe_load(f)

# Convert to MQTT configuration
mqtt_config = MQTTConfig.from_dict(config_data)

# Create publisher
publisher = MQTTPublisher(config=mqtt_config)
```

### 📋 Configuration Best Practices

#### Port Configuration

- Use port `1883` for non-TLS connections
- Use port `8883` for TLS connections
- Port values are automatically converted from strings to integers

#### Security Modes

- `"none"`: No authentication
- `"username"`: Username/password authentication
- `"tls"`: TLS encryption + username/password
- `"tls_with_client_cert"`: TLS + client certificates

#### Common Configuration Patterns

**Development/Testing:**

```python
config = MQTTConfig.build_config(
    broker_url="localhost",
    broker_port=1883,
    client_id="dev_client",
    security="none"
)
```

**Production with Username/Password:**

```python
config = MQTTConfig.build_config(
    broker_url="mqtt.example.com",
    broker_port=8883,
    client_id="prod_client",
    security="username",
    username="user",
    password="secure_password"
)
```

**Production with TLS + Client Certificates:**

```python
config = MQTTConfig.build_config(
    broker_url="mqtt.example.com",
    broker_port=8884,
    client_id="secure_client",
    security="tls_with_client_cert",
    username="user",
    password="password",
    tls={
        "ca_cert": "/path/to/ca.pem",
        "client_cert": "/path/to/client.pem",
        "client_key": "/path/to/client.key",
        "verify": True
    }
)
```

### 🧪 Testing the Enhanced Features

The enhanced features include comprehensive test coverage. Run the tests with:

```bash
# Test MQTTConfig functionality
pytest tests/test_mqtt_config.py -v

# Test enhanced MQTTPublisher features
pytest tests/test_mqtt_publisher_enhanced.py -v

# Run all tests
pytest tests/ -v
```

### 📚 Examples

See `examples/enhanced_features_example.py` for a complete demonstration of all new features:

```bash
python examples/enhanced_features_example.py
```

This example demonstrates:

- Automatic port type conversion
- Configuration builder pattern
- YAML-like configuration handling
- Validation error handling
- Configuration warnings

### 🔄 Backward Compatibility

All enhancements are fully backward compatible. Existing code will continue to work without modifications:

```python
# This still works exactly as before
publisher = MQTTPublisher(
    broker_url="mqtt.example.com",
    broker_port=8883,
    client_id="my_client"
)
```

The new features are opt-in and provide additional convenience and robustness for new implementations.
