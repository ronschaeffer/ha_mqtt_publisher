ha_mqtt_publisher.message_handler

Overview

This module provides a small helper, `handle_command_message`, for common MQTT command/result handling patterns used by Home Assistant-style automations. It publishes transient `ack` messages, mirrors the last retained ack/result to `last_ack`/`last_result` topics, and delegates raw command payloads to a provided processor.

Import

```python
from ha_mqtt_publisher.message_handler import handle_command_message
```

Function signature (summary)

- handle_command_message(client, config, processor, msg, ack_topic, last_ack_topic, result_topic, last_result_topic)

Parameters (short):

- client: MQTT client-like object with a `publish(topic, payload, qos=..., retain=...)` method.
- config: dict-like config (only `app.unique_id_prefix` is read by the helper; it defaults to `twickenham_events`).
- processor: object with a `handle_raw(data)` method — called with the raw payload or decoded text depending on input.
- msg: object with `topic` and `payload` attributes (e.g. `paho.mqtt.client.MQTTMessage` or a simple namespace).
- ack_topic / last_ack_topic / result_topic / last_result_topic: topic names used for ack/result publishing and retained mirrors.

Example and usage notes

- `PRESS` payloads and empty payloads are treated as a simple press/button command. The helper publishes a temporary `busy` ack and then calls `processor.handle_raw(command)`.
- JSON command payloads will be attempted to parse; the JSON string is passed through to `processor.handle_raw` (decoded to text).
- When a message arrives on `result_topic` the helper mirrors the object to `last_result_topic` (retained) and publishes an `idle` ack.

See also: `examples/message_handler_example.py` for a runnable demonstration.

Running the example

From the repository root you can run the example without installing the package by adding `src` to PYTHONPATH:

```bash
PYTHONPATH=src python3 examples/message_handler_example.py
```

Alternatively install the package in editable mode and run normally:

```bash
python3 -m pip install --user -e .
python3 examples/message_handler_example.py
```
