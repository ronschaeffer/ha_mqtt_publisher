"""CLI healthcheck for cron-style services using a HeartbeatFile.

Usage:
    python -m ha_mqtt_publisher.healthcheck_cli \
        --heartbeat /var/run/myapp/mqtt.heartbeat \
        --max-age 90000

Exits 0 if the heartbeat exists and is younger than --max-age seconds,
1 otherwise. Designed for use in Docker HEALTHCHECK directives where the
service is a periodic cron job rather than a long-running process.
"""

from __future__ import annotations

import argparse
import sys

from .health import HeartbeatFile


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="python -m ha_mqtt_publisher.healthcheck_cli",
        description="MQTT publish heartbeat healthcheck for cron-style services",
    )
    p.add_argument(
        "--heartbeat",
        required=True,
        help="Path to the heartbeat file written by the service after each successful publish",
    )
    p.add_argument(
        "--max-age",
        type=float,
        required=True,
        help="Maximum acceptable heartbeat age in seconds",
    )
    args = p.parse_args(argv)

    hb = HeartbeatFile(args.heartbeat, args.max_age)
    age = hb.age_seconds()
    if age is None:
        print(
            f"FAIL: heartbeat {args.heartbeat} does not exist", file=sys.stderr
        )
        return 1
    if age > args.max_age:
        print(
            f"FAIL: heartbeat is {age:.0f}s old (max allowed {args.max_age:.0f}s)",
            file=sys.stderr,
        )
        return 1
    print(f"OK: heartbeat is {age:.0f}s old (max allowed {args.max_age:.0f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
