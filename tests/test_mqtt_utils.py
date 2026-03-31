from ha_mqtt_publisher import mqtt_utils


class DummyProps:
    pass


def test_extract_reason_code_from_int_positional():
    assert mqtt_utils.extract_reason_code(1, 2, 3) == 3


def test_extract_reason_code_from_int_like_object():
    class R:
        def __int__(self):
            return 7

    rc = mqtt_utils.extract_reason_code(R())
    assert mqtt_utils.reason_code_to_int(rc) == 7


def test_extract_reason_code_from_kwargs():
    assert mqtt_utils.extract_reason_code(foo=1, reason_code=42) == 42


def test_extract_properties_from_kwargs():
    props = DummyProps()
    assert mqtt_utils.extract_properties(properties=props) is props


def test_extract_properties_from_positional():
    props = DummyProps()
    # case where last arg is not int-like
    assert mqtt_utils.extract_properties(0, props) is props


def test_safe_on_connect_decorator_with_v1_signature():
    called = {}

    @mqtt_utils.safe_on_connect
    def on_connect(client, userdata, rc, properties):
        called["rc"] = rc
        called["properties"] = properties

    on_connect("c", "u", 0)
    assert called["rc"] == 0
    assert called["properties"] is None


def test_safe_on_connect_decorator_with_v2_signature():
    called = {}

    @mqtt_utils.safe_on_connect
    def on_connect(client, userdata, rc, properties):
        called["rc"] = rc
        called["properties"] = properties

    props = DummyProps()
    on_connect("c", "u", 0, props)
    assert called["rc"] == 0
    assert called["properties"] is props


def test_safe_on_connect_decorator_with_extra_args():
    called = {}

    @mqtt_utils.safe_on_connect
    def on_connect(client, userdata, rc, properties):
        called["rc"] = rc
        called["properties"] = properties

    class Reason:
        def __int__(self):
            return 5

    props = DummyProps()
    on_connect("c", "u", "foo", Reason(), props)
    assert mqtt_utils.reason_code_to_int(called["rc"]) == 5
    assert called["properties"] is props


def test_reason_code_to_int_with_int():
    assert mqtt_utils.reason_code_to_int(0) == 0
    assert mqtt_utils.reason_code_to_int(5) == 5
    assert mqtt_utils.reason_code_to_int(None) is None


def test_reason_code_to_int_with_value_attr():
    """Simulates paho 2.x ReasonCode which has .value and .getName."""

    class FakeReasonCode:
        def __init__(self, val):
            self.value = val

        def getName(self):
            return "Success" if self.value == 0 else "Error"

    assert mqtt_utils.reason_code_to_int(FakeReasonCode(0)) == 0
    assert mqtt_utils.reason_code_to_int(FakeReasonCode(5)) == 5


def test_extract_reason_code_with_paho_like_reason_code():
    """extract_reason_code should find paho-style ReasonCode objects."""

    class FakeReasonCode:
        def __init__(self, val):
            self.value = val

        def getName(self):
            return "Normal disconnection"

    rc = FakeReasonCode(0)
    assert mqtt_utils.extract_reason_code("flags", rc, "props") is rc
