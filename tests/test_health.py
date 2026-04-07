"""Tests for ha_mqtt_publisher.health module."""

from __future__ import annotations

import os
import time
from unittest.mock import MagicMock

import pytest

from ha_mqtt_publisher.health import (
    HealthState,
    HealthTracker,
    HeartbeatFile,
    make_fastapi_router,
)


class TestHealthState:
    def test_defaults(self):
        s = HealthState()
        assert s.connected is False
        assert s.last_publish_success_at is None
        assert s.publish_success_count == 0
        assert s.publish_failure_count == 0

    def test_to_dict_includes_age_when_published(self):
        s = HealthState()
        s.connected = True
        s.last_publish_success_at = time.time() - 5
        d = s.to_dict()
        assert d["connected"] is True
        assert d["last_publish_success_age_seconds"] is not None
        assert 4 < d["last_publish_success_age_seconds"] < 6

    def test_to_dict_age_none_when_no_publish(self):
        s = HealthState()
        d = s.to_dict()
        assert d["last_publish_success_age_seconds"] is None


class TestHealthTracker:
    def test_unhealthy_when_disconnected(self):
        t = HealthTracker(max_publish_age_seconds=60)
        assert t.is_healthy is False

    def test_healthy_when_connected_no_publish(self):
        t = HealthTracker(max_publish_age_seconds=60)
        t.state.connected = True
        assert t.is_healthy is True

    def test_healthy_when_connected_recent_publish(self):
        t = HealthTracker(max_publish_age_seconds=60)
        t.state.connected = True
        t.state.last_publish_success_at = time.time()
        assert t.is_healthy is True

    def test_unhealthy_when_publish_too_old(self):
        t = HealthTracker(max_publish_age_seconds=10)
        t.state.connected = True
        t.state.last_publish_success_at = time.time() - 30
        assert t.is_healthy is False

    def test_unhealthy_when_disconnected_even_if_recent_publish(self):
        t = HealthTracker(max_publish_age_seconds=60)
        t.state.connected = False
        t.state.last_publish_success_at = time.time()
        assert t.is_healthy is False

    def test_status_dict_includes_healthy_flag(self):
        t = HealthTracker(max_publish_age_seconds=60)
        t.state.connected = True
        d = t.status_dict()
        assert d["healthy"] is True
        assert d["max_publish_age_seconds"] == 60

    def test_attach_patches_publisher_methods(self):
        from ha_mqtt_publisher import MQTTPublisher

        pub = MQTTPublisher(
            broker_url="localhost",
            broker_port=1883,
            client_id="test_attach_patch",
        )
        t = HealthTracker(max_publish_age_seconds=10)
        t.attach(pub)
        # methods should be re-bound to wrapper functions
        assert pub.publish.__name__ == "wrapped_publish"
        assert pub._on_connect.__name__ == "wrapped_on_connect"
        assert pub._on_disconnect.__name__ == "wrapped_on_disconnect"

    def test_attach_twice_raises(self):
        from ha_mqtt_publisher import MQTTPublisher

        pub = MQTTPublisher(
            broker_url="localhost",
            broker_port=1883,
            client_id="test_attach_twice",
        )
        t = HealthTracker(max_publish_age_seconds=10)
        t.attach(pub)
        with pytest.raises(RuntimeError, match="already attached"):
            t.attach(pub)

    def test_attach_records_failed_publish(self):
        from ha_mqtt_publisher import MQTTPublisher

        pub = MQTTPublisher(
            broker_url="localhost",
            broker_port=1883,
            client_id="test_attach_fail",
        )
        t = HealthTracker(max_publish_age_seconds=10)
        t.attach(pub)
        # Not connected, so publish() returns False without touching paho.
        ok = pub.publish("topic", "payload")
        assert ok is False
        assert t.state.publish_failure_count == 1
        assert t.state.publish_success_count == 0
        assert t.state.last_failure_reason == "not connected to broker"


class TestHeartbeatFile:
    def test_does_not_exist(self, tmp_path):
        hb = HeartbeatFile(tmp_path / "hb", 60)
        assert hb.age_seconds() is None
        assert hb.is_fresh() is False

    def test_touch_creates_file(self, tmp_path):
        hb = HeartbeatFile(tmp_path / "hb", 60)
        hb.touch()
        assert (tmp_path / "hb").exists()
        assert hb.age_seconds() is not None
        assert hb.age_seconds() < 1
        assert hb.is_fresh() is True

    def test_touch_creates_parent_dirs(self, tmp_path):
        hb = HeartbeatFile(tmp_path / "a" / "b" / "hb", 60)
        hb.touch()
        assert (tmp_path / "a" / "b" / "hb").exists()

    def test_stale(self, tmp_path):
        hb = HeartbeatFile(tmp_path / "hb", 1)
        hb.touch()
        # Mtime trick: subtract 5s from the file
        st = (tmp_path / "hb").stat()
        os.utime(tmp_path / "hb", (st.st_atime, st.st_mtime - 5))
        assert hb.is_fresh() is False
        assert hb.age_seconds() > 1


class TestMakeFastApiRouter:
    def test_router_returns_200_when_healthy(self):
        try:
            from fastapi import FastAPI
            from fastapi.testclient import TestClient
        except ImportError:
            pytest.skip("fastapi not installed")
        t = HealthTracker(max_publish_age_seconds=60)
        t.state.connected = True
        app = FastAPI()
        app.include_router(make_fastapi_router(t))
        client = TestClient(app)
        r = client.get("/health")
        assert r.status_code == 200
        r = client.get("/health/mqtt")
        assert r.status_code == 200
        assert r.json()["healthy"] is True

    def test_router_returns_503_when_unhealthy(self):
        try:
            from fastapi import FastAPI
            from fastapi.testclient import TestClient
        except ImportError:
            pytest.skip("fastapi not installed")
        t = HealthTracker(max_publish_age_seconds=60)
        # not connected -> unhealthy
        app = FastAPI()
        app.include_router(make_fastapi_router(t))
        client = TestClient(app)
        r = client.get("/health/mqtt")
        assert r.status_code == 503
        assert r.json()["healthy"] is False
