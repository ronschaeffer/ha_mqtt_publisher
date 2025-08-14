import threading

from ha_mqtt_publisher import AvailabilityPublisher
from ha_mqtt_publisher.service_runner import run_service_loop, run_service_once


class DummyClient:
    def __init__(self):
        self.calls = []

    def publish(self, topic, payload, qos=0, retain=False):
        self.calls.append((topic, payload, qos, retain))
        return True


def test_run_service_once_marks_availability_online_offline():
    client = DummyClient()
    ap = AvailabilityPublisher(mqtt_client=client, topic="x/availability")

    called = {"setup": 0, "cycle": 0, "teardown": 0}

    def setup():
        called["setup"] += 1

    def cycle():
        called["cycle"] += 1

    def teardown():
        called["teardown"] += 1

    run_service_once(setup=setup, cycle=cycle, teardown=teardown, availability=ap)

    assert called == {"setup": 1, "cycle": 1, "teardown": 1}
    # Expect two availability publishes
    assert (
        client.calls[0][0].endswith("/availability") and client.calls[0][1] == "online"
    )
    assert (
        client.calls[-1][0].endswith("/availability")
        and client.calls[-1][1] == "offline"
    )


def test_run_service_loop_stops_with_event_and_publishes_availability():
    client = DummyClient()
    ap = AvailabilityPublisher(mqtt_client=client, topic="y/availability")

    stop = threading.Event()
    ticks = {"count": 0}

    def on_tick():
        ticks["count"] += 1
        # stop after first tick
        stop.set()

    run_service_loop(
        interval_s=0.01,
        on_tick=on_tick,
        availability=ap,
        stop_event=stop,
        install_signals=False,
    )

    assert ticks["count"] >= 1
    assert client.calls[0][1] == "online"
    assert client.calls[-1][1] == "offline"
