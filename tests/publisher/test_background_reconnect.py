"""Background reconnect after connect() exhausts max_retries.

Regression for services that start before the broker is listening (e.g. after
a host reboot): they used to give up after max_retries and never connect.
"""

from unittest.mock import Mock, patch

from ha_mqtt_publisher.publisher import MQTTPublisher


def _publisher(**extra):
    pub = MQTTPublisher(
        broker_url="test.broker.com", client_id="test_client", max_retries=2, **extra
    )
    pub.client = Mock()
    pub.client.connect.side_effect = ConnectionRefusedError("refused")
    return pub


def test_hands_off_to_background_loop_after_retries():
    pub = _publisher()
    with patch("time.sleep"):
        assert pub.connect() is False
    pub.client.reconnect_delay_set.assert_called_once_with(min_delay=1, max_delay=60)
    pub.client.connect_async.assert_called_once_with(
        "test.broker.com", 1883, keepalive=60
    )
    pub.client.loop_start.assert_called_once()
    assert pub._background_reconnect_active is True


def test_disabled_keeps_old_give_up_behaviour():
    pub = _publisher(background_reconnect=False)
    with patch("time.sleep"):
        assert pub.connect() is False
    pub.client.connect_async.assert_not_called()
    pub.client.loop_start.assert_not_called()
    assert pub._background_reconnect_active is False


def test_config_dict_can_disable():
    pub = MQTTPublisher(
        config={
            "broker_url": "b",
            "broker_port": 1883,
            "client_id": "c",
            "background_reconnect": False,
        }
    )
    assert pub.background_reconnect is False


def test_on_connect_clears_background_flag():
    pub = _publisher()
    with patch("time.sleep"):
        pub.connect()
    pub._on_connect(pub.client, None, {}, 0, None)
    assert pub._connected is True
    assert pub._background_reconnect_active is False


def test_second_connect_waits_instead_of_reconnecting():
    pub = _publisher()
    with patch("time.sleep"):
        pub.connect()
    pub.client.connect.reset_mock()
    pub._connected = True  # background loop got through
    assert pub.connect() is True
    pub.client.connect.assert_not_called()


def test_disconnect_stops_background_loop():
    pub = _publisher()
    with patch("time.sleep"):
        pub.connect()
    pub.disconnect()
    pub.client.loop_stop.assert_called_once()
    assert pub._background_reconnect_active is False


def test_context_manager_failure_leaves_no_background_loop():
    pub = _publisher()
    with patch("time.sleep"):
        try:
            with pub:
                raise AssertionError("should not enter")
        except ConnectionError:
            pass
    pub.client.loop_stop.assert_called_once()
    assert pub._background_reconnect_active is False


def test_mqtt_config_passes_background_reconnect_through():
    from ha_mqtt_publisher.config import MQTTConfig

    cfg = MQTTConfig.from_dict(
        {"mqtt": {"broker_url": "b", "background_reconnect": "false"}}
    )
    assert cfg["background_reconnect"] is False
    assert MQTTConfig.to_publisher_kwargs(cfg)["background_reconnect"] is False
    unset = MQTTConfig.from_dict({"mqtt": {"broker_url": "b"}})
    assert "background_reconnect" not in unset
