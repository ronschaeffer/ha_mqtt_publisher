from pathlib import Path
import sys


def test_sys_path():
    project_root = str(Path(__file__).parent.parent)
    assert project_root in sys.path, "Project root should be in sys.path"


def test_import_module():
    try:
        # Use the import in the test
        import ha_mqtt_publisher as pkg

        assert pkg is not None
    except ImportError as e:
        raise AssertionError("Should be able to import ha_mqtt_publisher module") from e
