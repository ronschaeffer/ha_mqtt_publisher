import sys
from pathlib import Path


def test_sys_path():
    project_root = str(Path(__file__).parent.parent)
    assert project_root in sys.path, "Project root should be in sys.path"


def test_import_module():
    try:
        # Use the import in the test
        import mqtt_publisher

        assert mqtt_publisher is not None
    except ImportError:
        assert False, "Should be able to import mqtt_publisher module"
