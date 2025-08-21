"""Repository shim to expose in-repo src/ packages when running tests.

Adds the repository's ``src`` directory to the package ``__path__`` so
``import mqtt_publisher`` resolves the local source without installing the package.
Also maps the real publisher module under ``mqtt_publisher.publisher`` to
preserve legacy imports used by downstream projects/tests.
"""

import importlib
import os
import sys

_this_dir = os.path.dirname(__file__)
_src = os.path.join(_this_dir, "src")
if os.path.isdir(_src):
    # insert package src directory so mqtt_publisher.publisher etc resolve
    __path__.insert(0, _src)


# Best-effort mapping: the repo provides `ha_mqtt_publisher.publisher` which
# implements the publisher API; some tests import `mqtt_publisher.publisher`.
# If so, import the real publisher and register it under the `mqtt_publisher`
# package namespace so legacy imports succeed.
try:
    # import real implementation if available
    real_pub = importlib.import_module("ha_mqtt_publisher.publisher")
    # register module under expected name
    sys.modules.setdefault("mqtt_publisher.publisher", real_pub)
    pkg = sys.modules.get(__name__)
    if pkg is not None:
        pkg.publisher = real_pub  # type: ignore[attr-defined]

    # map ha_discovery: prefer mqtt_publisher.src.mqtt_publisher.ha_discovery if present,
    # otherwise fall back to ha_mqtt_publisher.ha_discovery
    try:
        ha_disc = importlib.import_module("mqtt_publisher.ha_discovery")
    except Exception:
        try:
            ha_disc = importlib.import_module("ha_mqtt_publisher.ha_discovery")
            sys.modules.setdefault("mqtt_publisher.ha_discovery", ha_disc)
            if pkg is not None:
                pkg.ha_discovery = ha_disc  # type: ignore[attr-defined]
        except Exception:
            pass
except Exception:
    # ignore - let import errors surface when tests import the module explicitly
    pass
