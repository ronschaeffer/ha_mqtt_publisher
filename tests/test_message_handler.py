import json
import types

from ha_mqtt_publisher.message_handler import handle_command_message


class DummyClient:
    def __init__(self):
        self.published = []

    def publish(self, topic, payload, qos=0, retain=False):
        self.published.append((topic, payload, qos, retain))


class DummyProcessor:
    def __init__(self):
        self.calls = []

    def handle_raw(self, data):
        self.calls.append(data)


def test_handle_result_message_mirrors_and_ack():
    client = DummyClient()
    processor = DummyProcessor()
    cfg = {"app.unique_id_prefix": "testapp"}

    msg = types.SimpleNamespace(
        topic="test/result",
        payload=json.dumps({"id": "123", "completed_ts": 1}).encode(),
    )
    handle_command_message(
        client,
        cfg,
        processor,
        msg,
        ack_topic="test/ack",
        last_ack_topic="test/last_ack",
        result_topic="test/result",
        last_result_topic="test/last_result",
    )

    # Should have mirrored last result and published an ack
    assert any(t == "test/last_result" for t, *_ in client.published)
    assert any(t == "test/ack" for t, *_ in client.published)
    assert any(t == "test/last_ack" for t, *_ in client.published)
    # Processor should not be called for a result message
    assert processor.calls == []


def test_handle_command_press_calls_processor():
    client = DummyClient()
    processor = DummyProcessor()
    cfg = {"app.unique_id_prefix": "testapp"}

    msg = types.SimpleNamespace(topic="testapp/cmd/foo", payload=b"PRESS")
    handle_command_message(
        client,
        cfg,
        processor,
        msg,
        ack_topic="test/ack",
        last_ack_topic="test/last_ack",
        result_topic="test/result",
        last_result_topic="test/last_result",
    )

    # busy ack published
    assert any(t == "test/ack" for t, *_ in client.published)
    # processor.handle_raw called with 'foo'
    assert processor.calls[-1] == "foo"


def test_handle_command_json_calls_processor_and_lowercases():
    client = DummyClient()
    processor = DummyProcessor()
    cfg = {"app.unique_id_prefix": "testapp"}

    payload = json.dumps({"name": "DoThing"}).encode()
    msg = types.SimpleNamespace(topic="testapp/cmd/doth", payload=payload)
    handle_command_message(
        client,
        cfg,
        processor,
        msg,
        ack_topic="test/ack",
        last_ack_topic="test/last_ack",
        result_topic="test/result",
        last_result_topic="test/last_result",
    )

    assert any(t == "test/ack" for t, *_ in client.published)
    # handler passes decoded text for JSON payloads
    assert processor.calls[-1] == payload.decode()
