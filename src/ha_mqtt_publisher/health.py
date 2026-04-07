"""Shared MQTT health/liveness tracking and exposure helpers.

Provides primitives for exposing MQTT publisher liveness to external healthchecks
(Docker HEALTHCHECK, Kubernetes probes, monitoring systems, etc.).

Three primitives are provided:

1. ``HealthTracker`` - Wraps a long-running ``MQTTPublisher`` and records
   connection state, publish success/failure, and last-success timestamps.
   Use with ``make_fastapi_router`` for HTTP-exposed liveness in services
   that already run a FastAPI app.

2. ``HeartbeatFile`` - Filesystem-based liveness for cron-style apps that
   have no long-running process. The job calls ``touch()`` after a successful
   publish; the Docker healthcheck CLI verifies the file is recent enough.

3. ``make_fastapi_router`` - Drop-in FastAPI APIRouter exposing
   ``GET /health`` (process liveness) and ``GET /health/mqtt``
   (MQTT broker liveness, returns 503 when unhealthy).

These exist because Docker HEALTHCHECK probes that only verify a local HTTP
``/health`` endpoint mark a container "healthy" even when its MQTT publisher
has been silently failing for hours - exactly the failure mode that took out
twickenham_events, flights and hounslow_bin_collection on 2026-04-07 when the
EMQX broker crashed.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import time
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .publisher import MQTTPublisher


@dataclass
class HealthState:
    """Snapshot of MQTT publisher health state."""

    connected: bool = False
    last_connect_at: Optional[float] = None
    last_disconnect_at: Optional[float] = None
    last_publish_success_at: Optional[float] = None
    last_publish_failure_at: Optional[float] = None
    last_failure_reason: Optional[str] = None
    publish_success_count: int = 0
    publish_failure_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        now = time.time()
        last_success_age: Optional[float] = None
        if self.last_publish_success_at is not None:
            last_success_age = now - self.last_publish_success_at
        return {
            "connected": self.connected,
            "last_connect_at": self.last_connect_at,
            "last_disconnect_at": self.last_disconnect_at,
            "last_publish_success_at": self.last_publish_success_at,
            "last_publish_failure_at": self.last_publish_failure_at,
            "last_publish_success_age_seconds": last_success_age,
            "last_failure_reason": self.last_failure_reason,
            "publish_success_count": self.publish_success_count,
            "publish_failure_count": self.publish_failure_count,
        }


class HealthTracker:
    """Tracks MQTT publisher liveness for use in health endpoints/checks.

    Wraps an :class:`MQTTPublisher` instance via ``attach()``, which patches the
    publisher's ``_on_connect``, ``_on_disconnect`` and ``publish`` methods so
    every connection/publish event updates the tracker's state.

    Example:
        tracker = HealthTracker(max_publish_age_seconds=300)
        publisher = MQTTPublisher(...)
        tracker.attach(publisher)
        publisher.connect()
        # ... later, in your FastAPI app:
        app.include_router(make_fastapi_router(tracker))

    A publisher is considered ``is_healthy`` when:
    - it is currently connected to the broker, AND
    - either it has not yet published anything (just connected), OR
      it published successfully within the last ``max_publish_age_seconds``.
    """

    def __init__(self, max_publish_age_seconds: float = 300.0) -> None:
        self.max_publish_age_seconds = max_publish_age_seconds
        self.state = HealthState()
        self._publisher: Optional[MQTTPublisher] = None

    def attach(self, publisher: MQTTPublisher) -> HealthTracker:
        """Instrument an MQTTPublisher to update this tracker on every event.

        Patches the publisher's _on_connect, _on_disconnect and publish methods
        in place. Safe to call exactly once per publisher.
        """
        if self._publisher is not None:
            raise RuntimeError("HealthTracker already attached to a publisher")
        self._publisher = publisher

        orig_on_connect = publisher._on_connect
        orig_on_disconnect = publisher._on_disconnect
        orig_publish = publisher.publish
        tracker = self

        def wrapped_on_connect(client, userdata, *args):
            result = orig_on_connect(client, userdata, *args)
            # publisher._connected is set inside the original handler
            if getattr(publisher, "_connected", False):
                tracker.state.connected = True
                tracker.state.last_connect_at = time.time()
            return result

        def wrapped_on_disconnect(client, userdata, *args):
            result = orig_on_disconnect(client, userdata, *args)
            tracker.state.connected = False
            tracker.state.last_disconnect_at = time.time()
            return result

        def wrapped_publish(
            topic, payload, qos=None, retain=None, properties=None
        ):
            ok = orig_publish(
                topic, payload, qos=qos, retain=retain, properties=properties
            )
            now = time.time()
            if ok:
                tracker.state.last_publish_success_at = now
                tracker.state.publish_success_count += 1
            else:
                tracker.state.last_publish_failure_at = now
                tracker.state.publish_failure_count += 1
                if not getattr(publisher, "_connected", False):
                    tracker.state.last_failure_reason = "not connected to broker"
                else:
                    tracker.state.last_failure_reason = "publish call failed"
            return ok

        publisher._on_connect = wrapped_on_connect  # type: ignore[method-assign]
        publisher._on_disconnect = wrapped_on_disconnect  # type: ignore[method-assign]
        publisher.publish = wrapped_publish  # type: ignore[method-assign]

        # The paho client already has the *original* callbacks bound from
        # MQTTPublisher.__init__, so re-wire them through the safe wrappers.
        try:
            from .mqtt_utils import safe_on_connect, safe_on_disconnect

            publisher.client.on_connect = safe_on_connect(wrapped_on_connect)
            publisher.client.on_disconnect = safe_on_disconnect(
                wrapped_on_disconnect
            )
        except Exception:  # pragma: no cover - defensive
            publisher.client.on_connect = wrapped_on_connect
            publisher.client.on_disconnect = wrapped_on_disconnect

        return self

    @property
    def is_healthy(self) -> bool:
        """True if connected and a successful publish happened recently enough."""
        if not self.state.connected:
            return False
        last = self.state.last_publish_success_at
        if last is None:
            # Connected but nothing published yet - treat as healthy.
            return True
        return (time.time() - last) <= self.max_publish_age_seconds

    def status_dict(self) -> dict[str, Any]:
        """Full status dict including computed ``healthy`` flag."""
        d = self.state.to_dict()
        d["healthy"] = self.is_healthy
        d["max_publish_age_seconds"] = self.max_publish_age_seconds
        return d


class HeartbeatFile:
    """Filesystem heartbeat for cron-style services with no long-running process.

    The job calls :meth:`touch` after a successful MQTT publish. A separate
    healthcheck process (e.g. Docker HEALTHCHECK) calls :meth:`is_fresh` to
    verify the heartbeat is recent enough.
    """

    def __init__(
        self, path: str | os.PathLike[str], max_age_seconds: float
    ) -> None:
        self.path = Path(path)
        self.max_age_seconds = max_age_seconds

    def touch(self) -> None:
        """Update the heartbeat file's mtime to now, creating it if needed."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch()

    def age_seconds(self) -> Optional[float]:
        """Age of the heartbeat in seconds, or None if it does not exist."""
        try:
            return time.time() - self.path.stat().st_mtime
        except FileNotFoundError:
            return None

    def is_fresh(self) -> bool:
        """True if the heartbeat exists and is younger than ``max_age_seconds``."""
        age = self.age_seconds()
        return age is not None and age <= self.max_age_seconds


def make_fastapi_router(tracker: HealthTracker, prefix: str = "/health") -> Any:
    """Create a FastAPI APIRouter exposing tracker state.

    Routes:
        GET {prefix}        -> 200 always (process liveness)
        GET {prefix}/mqtt   -> 200 if tracker.is_healthy else 503

    Requires FastAPI to be installed (``pip install ha-mqtt-publisher[fastapi]``).
    """
    try:
        from fastapi import APIRouter
        from fastapi.responses import JSONResponse
    except ImportError as e:  # pragma: no cover - import-guarded
        raise ImportError(
            "FastAPI is required for make_fastapi_router. "
            "Install with `pip install ha-mqtt-publisher[fastapi]` "
            "or `pip install fastapi`."
        ) from e

    router = APIRouter()

    @router.get(prefix)
    def liveness() -> dict[str, str]:
        return {"status": "ok"}

    @router.get(f"{prefix}/mqtt")
    def mqtt_health() -> JSONResponse:
        body = tracker.status_dict()
        status = 200 if tracker.is_healthy else 503
        return JSONResponse(content=body, status_code=status)

    return router


__all__ = [
    "HealthState",
    "HealthTracker",
    "HeartbeatFile",
    "make_fastapi_router",
]
