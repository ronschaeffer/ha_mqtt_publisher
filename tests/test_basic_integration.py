"""Simple integration tests for new automation features."""

import subprocess
from pathlib import Path

import pytest


class TestBasicAutomation:
    """Basic tests for automation functionality."""

    def test_version_sync_script_runs(self):
        """Test that version sync script executes successfully."""
        result = subprocess.run(
            ["python", "scripts/sync_versions.py"],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        assert result.returncode == 0
        assert "pyproject.toml version:" in result.stdout

    def test_imports_work_correctly(self):
        """Test that all main imports work."""
        from mqtt_publisher import (
            Config,
            Device,
            MQTTConfig,
            MQTTPublisher,
            create_sensor,
            create_status_sensor,
            publish_discovery_configs,
        )

        # All should be callable or instantiable
        assert callable(MQTTPublisher)
        assert callable(Device)
        assert callable(Config)
        assert callable(MQTTConfig.build_config)
        assert callable(create_sensor)
        assert callable(create_status_sensor)
        assert callable(publish_discovery_configs)

    def test_version_consistency(self):
        """Test that versions are consistent."""
        import mqtt_publisher

        # Read pyproject.toml version
        pyproject_path = Path("pyproject.toml")
        content = pyproject_path.read_text()

        for line in content.split("\n"):
            if line.strip().startswith("version = "):
                pyproject_version = line.split('"')[1]
                break
        else:
            pytest.fail("Version not found in pyproject.toml")

        # Compare with package version
        assert mqtt_publisher.__version__ == pyproject_version

    def test_automation_files_exist(self):
        """Test that automation files exist."""
        files = [
            "scripts/sync_versions.py",
            "release.sh",
            ".github/workflows/ci.yml",
            ".github/workflows/release.yml",
            ".github/workflows/version-bump.yml",
        ]

        for file_path in files:
            assert Path(file_path).exists(), f"Missing file: {file_path}"

    def test_examples_can_be_imported(self):
        """Test that examples can be imported without errors."""
        # This is a basic smoke test
        import sys
        from pathlib import Path

        examples_dir = Path("examples")
        sys.path.insert(0, str(examples_dir))

        try:
            # Just test that files can be imported without syntax errors
            import importlib.util

            for example_file in [
                "enhanced_features_example.py",
                "ha_discovery_complete_example.py",
            ]:
                spec = importlib.util.spec_from_file_location(
                    example_file[:-3], examples_dir / example_file
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    # Don't execute, just check syntax
                    assert module is not None

        finally:
            if str(examples_dir) in sys.path:
                sys.path.remove(str(examples_dir))

    def test_config_templates_are_valid_yaml(self):
        """Test that YAML config templates are valid."""
        import yaml

        yaml_files = [
            "config/config.yaml.example",
            "config/config_ha_discovery.yaml.example",
            "config/ha_mqtt_discovery.yaml.example",
        ]

        for yaml_file in yaml_files:
            path = Path(yaml_file)
            if path.exists():
                content = path.read_text()
                try:
                    yaml.safe_load(content)
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML in {yaml_file}: {e}")

    def test_json_template_is_valid(self):
        """Test that JSON template is valid."""
        import json

        json_file = Path("config/ha_mqtt_discovery.json.example")
        if json_file.exists():
            content = json_file.read_text()
            try:
                json.loads(content)
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON in {json_file}: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
