"""Lightweight example showing usage of ha_mqtt_publisher.message_handler

Run this locally to simulate message handling without a live MQTT broker.
"""

import json
import types

from ha_mqtt_publisher.message_handler import handle_command_message


class DummyClient:
    def publish(self, topic, payload, qos=0, retain=False):
        print(
            f"PUBLISH -> topic={topic!r} payload={payload!r} qos={qos} retain={retain}"
        )


class DummyProcessor:
    def handle_raw(self, data):
        print(f"Processor.handle_raw called with: {data!r}")


def run_demo():
    client = DummyClient()
    processor = DummyProcessor()
    cfg = {"app.unique_id_prefix": "demoapp"}

    # Simulate a PRESS command
    msg1 = types.SimpleNamespace(topic="demoapp/cmd/light", payload=b"PRESS")
    handle_command_message(
        client,
        cfg,
        processor,
        msg1,
        ack_topic="demo/ack",
        last_ack_topic="demo/last_ack",
        result_topic="demo/result",
        last_result_topic="demo/last_result",
    )

    # Simulate a JSON command
    msg2 = types.SimpleNamespace(
        topic="demoapp/cmd/door", payload=json.dumps({"name": "Open"}).encode()
    )
    handle_command_message(
        client,
        cfg,
        processor,
        msg2,
        ack_topic="demo/ack",
        last_ack_topic="demo/last_ack",
        result_topic="demo/result",
        last_result_topic="demo/last_result",
    )

    # Simulate a result arriving
    msg3 = types.SimpleNamespace(
        topic="demo/result",
        payload=json.dumps({"id": "abc", "completed_ts": 123}).encode(),
    )
    handle_command_message(
        client,
        cfg,
        processor,
        msg3,
        ack_topic="demo/ack",
        last_ack_topic="demo/last_ack",
        result_topic="demo/result",
        last_result_topic="demo/last_result",
    )


if __name__ == "__main__":
    run_demo()
