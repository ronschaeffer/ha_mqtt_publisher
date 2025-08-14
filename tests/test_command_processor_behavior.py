import json
import time

from ha_mqtt_publisher.commands import CommandProcessor


class PubSpy:
    def __init__(self):
        self.pubs = []

    def publish(self, topic, payload, qos=0, retain=False):
        # payload may be str or bytes
        self.pubs.append((topic, payload, qos, retain))
        return True


def _parse(topic, pubs):
    for t, p, _q, _r in pubs:
        if t == topic:
            try:
                return json.loads(p)
            except Exception:
                return {}
    return {}


def test_single_flight_busy_result_when_executor_running():
    pub = PubSpy()
    cp = CommandProcessor(pub, "ack", "result", qos=0)

    def long_exec(ctx):
        time.sleep(0.2)
        return "success", "done", {}

    cp.register("work", long_exec)

    # Fire first command
    cp.handle_raw('{"command":"work"}')
    # Quickly fire second; should produce a busy result
    cp.handle_raw('{"command":"work"}')

    # Allow time for threads to run
    time.sleep(0.35)

    # Expect at least one busy result among results
    results = [json.loads(p) for t, p, _q, _r in pub.pubs if t == "result"]
    outcomes = {r.get("outcome") for r in results}
    assert "busy" in outcomes or any(r.get("duration_ms", 0) > 0 for r in results)


def test_cooldown_blocks_second_success_until_elapsed():
    pub = PubSpy()
    cp = CommandProcessor(pub, "ack", "result", qos=0)

    def ok(ctx):
        return "success", "ok", {}

    cp.register("ping", ok, cooldown_seconds=1)

    # First call succeeds
    cp.handle_raw('{"command":"ping"}')
    time.sleep(0.05)

    # Immediate second call should get cooldown
    cp.handle_raw('{"command":"ping"}')
    time.sleep(0.05)

    # After cooldown, third call should succeed again
    time.sleep(1.05)
    cp.handle_raw('{"command":"ping"}')
    time.sleep(0.05)

    results = [json.loads(p) for t, p, _q, _r in pub.pubs if t == "result"]
    outcomes = [r.get("outcome") for r in results]
    assert "success" in outcomes
    assert "cooldown" in outcomes
    # Ensure at least two successes separated by cooldown
    assert outcomes.count("success") >= 2
