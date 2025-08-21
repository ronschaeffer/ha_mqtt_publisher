#!/usr/bin/env python3
"""
Example: Migrating twickenham_events to use library publish_device_level_discovery

This example shows how twickenham_events can switch from its custom
publish_device_level_discovery function to the library version with
enhanced features using proper Entity objects.
"""

from ha_mqtt_publisher import Config, MQTTPublisher
from ha_mqtt_publisher.ha_discovery import (
    Device,
    Sensor,
    create_command_entities,
    create_standard_buttons,
    publish_device_level_discovery,
)


def build_twickenham_entities(config: Config, device: Device, base_prefix: str = "twickenham_events"):
    """Build all twickenham-specific entities using Entity objects."""
    
    # Get topic configurations
    status_topic = config.get_mqtt_topics().get("status", f"{base_prefix}/status")
    all_upcoming_topic = config.get_mqtt_topics().get(
        "all_upcoming", f"{base_prefix}/events/all_upcoming"
    )
    next_topic = config.get_mqtt_topics().get("next", f"{base_prefix}/events/next")
    today_topic = config.get_mqtt_topics().get("today", f"{base_prefix}/events/today")
    
    # Core application entities using Entity objects
    entities = []
    
    # Status sensor
    entities.append(Sensor(
        config=config,
        device=device,
        name="Status",
        unique_id=f"{base_prefix}_status",
        state_topic=status_topic,
        value_template="{{ value_json.status }}",
        json_attributes_topic=status_topic,
        icon="mdi:information",
        entity_category="diagnostic",
    ))
    
    # Last run sensor
    entities.append(Sensor(
        config=config,
        device=device,
        name="Last Run",
        unique_id=f"{base_prefix}_last_run",
        state_topic=status_topic,
        value_template="{{ value_json.last_run_iso | default(value_json.last_updated) }}",
        device_class="timestamp",
        entity_category="diagnostic",
    ))
    
    # Upcoming events sensor
    entities.append(Sensor(
        config=config,
        device=device,
        name="Upcoming Events",
        unique_id=f"{base_prefix}_upcoming",
        state_topic=all_upcoming_topic,
        value_template="{{ value_json.count if (value_json.count is defined) else 0 }}",
        json_attributes_topic=all_upcoming_topic,
        icon="mdi:calendar-multiple",
    ))
    
    # Next event sensor
    entities.append(Sensor(
        config=config,
        device=device,
        name="Next Event",
        unique_id=f"{base_prefix}_next",
        state_topic=next_topic,
        value_template="{{ value_json.fixture if (value_json.fixture is defined and value_json.fixture) else '' }}",
        json_attributes_topic=next_topic,
        json_attributes_template="{{ {'start_time': (value_json.start_time | default(None)), 'date': (value_json.date | default(None)), 'fixture_short': (value_json.fixture_short | default(None)), 'crowd': (value_json.crowd | default(None)), 'emoji': (value_json.emoji | default(None)), 'icon': (value_json.icon | default(None)), 'event_index': (value_json.event_index | default(None)), 'event_count': (value_json.event_count | default(None))} | tojson }}",
        icon="mdi:calendar-clock",
    ))
    
    # Today events sensor
    entities.append(Sensor(
        config=config,
        device=device,
        name="Today Events",
        unique_id=f"{base_prefix}_today",
        state_topic=today_topic,
        value_template="{{ value_json.events_today if value_json.events_today is defined else 0 }}",
        json_attributes_topic=today_topic,
        icon="mdi:calendar-today",
    ))
    
    # Event count sensor
    entities.append(Sensor(
        config=config,
        device=device,
        name="Event Count",
        unique_id=f"{base_prefix}_event_count",
        state_topic=status_topic,
        value_template="{{ value_json.event_count }}",
        state_class="measurement",
        entity_category="diagnostic",
    ))
    
    # Add command system entities
    command_topics = {
        "ack_topic": f"{base_prefix}/commands/ack",
        "result_topic": f"{base_prefix}/commands/result",
        "last_ack_topic": f"{base_prefix}/commands/last_ack",
        "last_result_topic": f"{base_prefix}/commands/last_result",
    }
    entities.extend(create_command_entities(config, device, base_prefix, command_topics))
    
    # Add standard buttons
    entities.extend(create_standard_buttons(config, device, base_prefix, f"{base_prefix}/cmd"))
    
    return entities


def migrate_twickenham_to_library_version(config: Config, publisher: MQTTPublisher):
    """
    Example migration function showing how twickenham_events would migrate
    to use the library's enhanced publish_device_level_discovery.
    """
    # Create device instance
    device = Device(
        config,
        identifiers=["twickenham_events"],
        name="Twickenham Events",
        manufacturer="Twickenham Rugby",
        model="Event Tracker",
        sw_version="0.3.3",
    )
    
    # Build all entities
    entities = build_twickenham_entities(config, device)
    
    # Publish with enhanced discovery function (Entity-based approach)
    topic = publish_device_level_discovery(
        config=config,
        publisher=publisher,
        device=device,
        entities=entities,
        availability_topic="twickenham_events/availability",
        migrate_from_per_entity=True,  # Clean up old per-entity discovery
        retain=True,
    )
    
    print(f"✅ Published enhanced device discovery to: {topic}")
    print(f"📊 Total entities: {len(entities)}")
    print("🔄 Migration from per-entity to device bundle complete")
    
    return topic, entities


if __name__ == "__main__":
    # Example usage
    config = Config()
    config.load_from_dict({
        "app": {
            "name": "Twickenham Events",
            "unique_id_prefix": "twickenham_events",
        },
        "mqtt": {
            "broker_url": "localhost",
            "client_id": "twickenham_events_example",
        },
        "home_assistant": {
            "discovery_prefix": "homeassistant",
        },
    })
    
    with MQTTPublisher(**config.get_mqtt_config()) as publisher:
        migrate_twickenham_to_library_version(config, publisher)
