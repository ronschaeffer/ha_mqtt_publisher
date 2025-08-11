import json

import pytest

from ha_mqtt_publisher.ha_mqtt_discovery.topic import HADiscoveryProcessor


@pytest.fixture
def config_file():
    """Provide path to test configuration file."""
    return "tests/ha_mqtt_discovery_topic/fixtures/test_config.yaml"


@pytest.fixture
def processor(config_file):
    """Create HADiscoveryProcessor instance with test config."""
    return HADiscoveryProcessor(config_file)


def test_load_config(processor):
    """Test loading configuration from file."""
    assert processor.config["device"]["name"] == "Test Device"


def test_discovery_topic(processor):
    """Test discovery topic generation."""
    topic = processor.discovery_topic("sensor", "next")
    assert topic.startswith("homeassistant/sensor/node1/next-")
    assert topic.endswith("/config")


def test_component_payload(processor):
    """Test component payload generation."""
    payload = processor.get_component_payload("temperature")
    assert payload["name"] == "Temperature"
    assert payload["unique_id"].startswith("temp_sensor-")
    assert payload["device"]["name"] == "Test Device"
    assert payload["unit_of_measurement"] == "°C"


def test_topic_defaults(processor):
    """Test topic defaults retrieval."""
    defaults = processor.get_topic_defaults()
    assert defaults["qos"] == 1
    assert defaults["retain"] is True


def test_process_component(processor):
    """Test complete component processing."""
    topic, payload = processor.process_component("humidity")
    payload_dict = json.loads(payload)

    assert topic.startswith("homeassistant/sensor/node1/test_device_humidity-")
    assert topic.endswith("/config")
    assert payload_dict["name"] == "Humidity"
    assert payload_dict["unit_of_measurement"] == "%"


def test_device_discovery(processor):
    """Test device discovery message generation."""
    topic, payload = processor.get_device_discovery_message()
    payload_dict = json.loads(payload)

    assert topic.startswith("homeassistant/device/test_device-")
    assert topic.endswith("/config")
    # Update assertions to match actual payload structure from config
    assert payload_dict == {
        "name": "Test Device",
        "identifiers": [f"test_device_id-{processor._uuid}"],
        "manufacturer": "Test Manufacturer",
        "model": "Test Model",
    }


def test_uuid_generation(config_file):
    """Test UUID generation when enabled."""
    # Create temporary config with UUIDs enabled
    processor = HADiscoveryProcessor(config_file)
    processor.generate_uuids = True
    processor._uuid = "test-uuid"  # Set fixed UUID for testing

    topic, payload = processor.process_component("temperature")
    payload_dict = json.loads(payload)

    assert "test-uuid" in topic
    assert "test-uuid" in payload_dict["unique_id"]
    assert "test-uuid" in payload_dict["device"]["identifiers"][0]


def test_invalid_component(processor):
    """Test handling of invalid component name."""
    with pytest.raises(ValueError):
        processor.get_component_payload("nonexistent")


def test_missing_config():
    """Test handling of missing config file."""
    with pytest.raises(RuntimeError):
        HADiscoveryProcessor("nonexistent.yaml")
