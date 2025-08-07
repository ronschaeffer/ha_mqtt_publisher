"""Tests for version synchronization functionality."""

import os
from pathlib import Path

# Test the version sync script by importing it as a module
import sys
import tempfile
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

try:
    import sync_versions
except ImportError:
    pytest.skip("sync_versions script not available", allow_module_level=True)


class TestVersionSync:
    """Test version synchronization between pyproject.toml and __init__.py"""

    def setup_method(self):
        """Set up test environment with temporary files"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Create test directory structure
        self.src_dir = self.temp_path / "src" / "mqtt_publisher"
        self.src_dir.mkdir(parents=True)

        # Create test pyproject.toml
        self.pyproject_content = """[tool.poetry]
name = "test-package"
version = "1.2.3"
description = "Test package"
"""
        (self.temp_path / "pyproject.toml").write_text(self.pyproject_content)

        # Create test __init__.py
        self.init_content = '''"""Test package"""

__version__ = "1.0.0"
__author__ = "test"
'''
        (self.src_dir / "__init__.py").write_text(self.init_content)

    def teardown_method(self):
        """Clean up test environment"""
        self.temp_dir.cleanup()

    @patch("scripts.sync_versions.Path.cwd")
    def test_get_pyproject_version_success(self, mock_cwd):
        """Test successful version extraction from pyproject.toml"""
        from scripts.sync_versions import get_pyproject_version

        mock_cwd.return_value = self.temp_path

        with patch("scripts.sync_versions.Path") as mock_path:
            mock_path.return_value = self.temp_path / "pyproject.toml"
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.read_text.return_value = self.pyproject_content

            version = get_pyproject_version()
            assert version == "1.2.3"

    @patch("scripts.sync_versions.Path")
    def test_get_pyproject_version_file_not_found(self, mock_path):
        """Test error when pyproject.toml doesn't exist"""
        from scripts.sync_versions import get_pyproject_version

        mock_path.return_value.exists.return_value = False

        with pytest.raises(FileNotFoundError, match="pyproject.toml not found"):
            get_pyproject_version()

    @patch("scripts.sync_versions.Path")
    def test_get_pyproject_version_no_version(self, mock_path):
        """Test error when version not found in pyproject.toml"""
        from scripts.sync_versions import get_pyproject_version

        mock_path.return_value.exists.return_value = True
        mock_path.return_value.read_text.return_value = "[tool.poetry]\nname = 'test'"

        with pytest.raises(ValueError, match="Version not found in pyproject.toml"):
            get_pyproject_version()

    @patch("scripts.sync_versions.Path.cwd")
    def test_update_init_version_success(self, mock_cwd):
        """Test successful version update in __init__.py"""
        from scripts.sync_versions import update_init_version

        mock_cwd.return_value = self.temp_path

        with (
            patch("scripts.sync_versions.Path") as mock_path,
            patch("builtins.print") as mock_print,
        ):
            init_path = self.src_dir / "__init__.py"
            mock_path.return_value = init_path
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.read_text.return_value = self.init_content

            result = update_init_version("1.2.3")

            assert result is True
            mock_path.return_value.write_text.assert_called_once()
            mock_print.assert_called_with("✅ Updated __init__.py version to 1.2.3")

    @patch("scripts.sync_versions.Path")
    def test_update_init_version_already_synced(self, mock_path):
        """Test when __init__.py version is already correct"""
        from scripts.sync_versions import update_init_version

        synced_content = '''"""Test package"""

__version__ = "1.2.3"
__author__ = "test"
'''

        mock_path.return_value.exists.return_value = True
        mock_path.return_value.read_text.return_value = synced_content

        with patch("builtins.print") as mock_print:
            result = update_init_version("1.2.3")

            assert result is False
            mock_print.assert_called_with("i  __init__.py already at version 1.2.3")

    @patch("scripts.sync_versions.Path")
    def test_update_init_version_file_not_found(self, mock_path):
        """Test error when __init__.py doesn't exist"""
        from scripts.sync_versions import update_init_version

        mock_path.return_value.exists.return_value = False

        with pytest.raises(FileNotFoundError, match="__init__.py not found"):
            update_init_version("1.2.3")

    def test_version_regex_patterns(self):
        """Test version regex patterns work correctly"""
        from scripts.sync_versions import update_init_version

        test_cases = [
            ('__version__ = "1.0.0"', "2.0.0", '__version__ = "2.0.0"'),
            ("__version__ = '1.0.0'", "2.0.0", '__version__ = "2.0.0"'),
            ('__version__ = "1.0.0-beta"', "2.0.0", '__version__ = "2.0.0"'),
        ]

        for original, new_version, expected in test_cases:
            content = f'"""Test"""\n\n{original}\n__author__ = "test"'

            with patch("scripts.sync_versions.Path") as mock_path:
                mock_path.return_value.exists.return_value = True
                mock_path.return_value.read_text.return_value = content

                # Call the function to test regex replacement
                update_init_version(new_version)

                # Check that write_text was called with correct content
                written_content = mock_path.return_value.write_text.call_args[0][0]
                assert expected in written_content


class TestVersionSyncIntegration:
    """Integration tests for the complete version sync workflow"""

    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Create complete project structure
        self.src_dir = self.temp_path / "src" / "mqtt_publisher"
        self.src_dir.mkdir(parents=True)

        # Create realistic project files
        pyproject_content = """[tool.poetry]
name = "mqtt-publisher"
version = "0.1.5"
description = "MQTT Publisher"

[build-system]
requires = ["poetry-core"]
"""
        (self.temp_path / "pyproject.toml").write_text(pyproject_content)

        init_content = '''"""MQTT Publisher Package"""

__version__ = "0.1.2"
__author__ = "test"

from .publisher import MQTTPublisher

__all__ = ["MQTTPublisher"]
'''
        (self.src_dir / "__init__.py").write_text(init_content)

    def teardown_method(self):
        """Clean up"""
        self.temp_dir.cleanup()

    @patch("scripts.sync_versions.Path.cwd")
    def test_main_function_success(self, mock_cwd):
        """Test main function completes successfully"""
        from scripts.sync_versions import main

        mock_cwd.return_value = self.temp_path

        with patch("builtins.print") as mock_print:
            result = main()

            assert result == 0

            # Check that appropriate messages were printed
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any(
                "📦 Current pyproject.toml version: 0.1.5" in call
                for call in print_calls
            )
            assert any(
                "Updated __init__.py version to 0.1.5" in call for call in print_calls
            )

    @patch("scripts.sync_versions.get_pyproject_version")
    def test_main_function_error_handling(self, mock_get_version):
        """Test main function error handling"""
        from scripts.sync_versions import main

        mock_get_version.side_effect = ValueError("Test error")

        with patch("builtins.print") as mock_print:
            result = main()

            assert result == 1
            mock_print.assert_called_with("❌ Error: Test error")


class TestVersionSyncEdgeCases:
    """Test edge cases and error conditions"""

    def test_complex_version_formats(self):
        """Test handling of various version formats"""
        from scripts.sync_versions import update_init_version

        version_formats = [
            "1.0.0",
            "2.1.0-alpha.1",
            "3.0.0-beta+build.1",
            "1.0.0-rc.1",
            "0.1.0-dev",
        ]

        for version in version_formats:
            content = '__version__ = "0.0.1"\n'

            with patch("scripts.sync_versions.Path") as mock_path:
                mock_path.return_value.exists.return_value = True
                mock_path.return_value.read_text.return_value = content

                result = update_init_version(version)
                assert result is True

    def test_malformed_init_file(self):
        """Test handling of malformed __init__.py files"""
        from scripts.sync_versions import update_init_version

        malformed_contents = [
            # No version at all
            '"""Package"""\n\nfrom .module import something',
            # Multiple version lines (should update first one)
            '__version__ = "1.0.0"\n# __version__ = "2.0.0"',
            # Version in comment (should not match)
            '# __version__ = "1.0.0"\nprint("hello")',
        ]

        for content in malformed_contents:
            with patch("scripts.sync_versions.Path") as mock_path:
                mock_path.return_value.exists.return_value = True
                mock_path.return_value.read_text.return_value = content

                # Should either update or not find version to update
                # but should not crash
                try:
                    update_init_version("2.0.0")
                except Exception as e:
                    pytest.fail(
                        f"Should not raise exception for content: {content!r}, got: {e}"
                    )


if __name__ == "__main__":
    pytest.main([__file__])
