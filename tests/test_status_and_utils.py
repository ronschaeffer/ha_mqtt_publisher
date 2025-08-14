from ha_mqtt_publisher.status import StatusPayload
from ha_mqtt_publisher.topic_map import TopicMap
from ha_mqtt_publisher.validator import validate_retained


class SpyClient:
    def __init__(self):
        self.subs = []
        self.unsubs = []
        self.cb = None

    def subscribe(self, topic, qos=0, callback=None):
        self.subs.append((topic, qos))
        # store callback and simulate immediate retained message
        if callback:

            class Msg:
                def __init__(self, t, p):
                    self.topic = t
                    self.payload = p

            callback(None, None, Msg(topic, b'{"hello":true}'))
        return True

    def unsubscribe(self, topic):
        self.unsubs.append(topic)
        return True


def test_status_payload_marks_run_and_caps_errors():
    s = StatusPayload(status="ok")
    s.mark_run()
    assert s.last_run_ts and s.last_run_iso

    for i in range(25):
        s.add_error("x", f"e{i}")
    s.cap_errors(10)
    assert len(s.errors) == 10


def test_topic_map_shapes_paths():
    tm = TopicMap(base="demo")
    assert tm.status == "demo/status"
    assert tm.availability == "demo/availability"
    assert tm.commands == "demo/cmd"
    assert tm.cmd("refresh") == "demo/cmd/refresh"


def test_validate_retained_collects_payloads():
    c = SpyClient()
    out = validate_retained(
        c, ["a/b", "x/y"]
    )  # only the first will get payload in our spy
    # one of the two topics should be present with the simulated payload
    assert any(v == b'{"hello":true}' for v in out.values())
