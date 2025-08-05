"""Tests specifically for the automation scripts."""

import subprocess
from pathlib import Path

import pytest


class TestAutomationScripts:
    """Test the automation scripts work correctly."""

    def test_sync_versions_dry_run(self):
        """Test version sync script in dry run mode."""
        result = subprocess.run(
            ["python", "scripts/sync_versions.py"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        output = result.stdout

        # Should report current version
        assert "pyproject.toml version:" in output

        # Should indicate sync status
        assert any(
            msg in output
            for msg in [
                "All versions already synchronized",
                "Version synchronization completed",
            ]
        )

    def test_release_script_shows_usage_on_invalid_input(self):
        """Test release script shows usage with invalid input."""
        result = subprocess.run(
            ["bash", "release.sh", "invalid-type"],
            capture_output=True,
            text=True,
        )

        # Should exit with error
        assert result.returncode != 0

        # Should show error information (either about git state or invalid type)
        output = result.stdout + result.stderr
        assert any(
            msg in output
            for msg in [
                "Invalid bump type",
                "Working directory is not clean",
                "Usage:",
                "Error",
            ]
        )

    def test_pre_commit_hook_is_executable(self):
        """Test pre-commit hook script exists and is executable."""
        hook_path = Path("scripts/pre-commit-version-sync")
        assert hook_path.exists()

        # Check execute permission
        import stat

        file_stat = hook_path.stat()
        is_executable = bool(file_stat.st_mode & stat.S_IEXEC)
        assert is_executable

    def test_scripts_directory_structure(self):
        """Test scripts directory has expected structure."""
        scripts_dir = Path("scripts")
        assert scripts_dir.exists()
        assert scripts_dir.is_dir()

        expected_files = [
            "sync_versions.py",
            "pre-commit-version-sync",
        ]

        for filename in expected_files:
            file_path = scripts_dir / filename
            assert file_path.exists(), f"Missing script: {filename}"

    def test_version_sync_handles_missing_files_gracefully(self):
        """Test version sync script handles missing files gracefully."""
        # Run in a temporary directory without the required files
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                ["python", str(Path("scripts/sync_versions.py").absolute())],
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            # Should exit with error
            assert result.returncode == 1

            # Should have helpful error message
            assert "Error:" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__])
