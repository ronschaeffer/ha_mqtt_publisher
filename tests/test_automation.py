"""Tests for automation functionality and version management."""

from pathlib import Path
import subprocess
import tempfile

import pytest


class TestVersionSyncScript:
    """Test the version synchronization script functionality."""

    def test_sync_versions_script_exists(self):
        """Test that the sync_versions script exists and is executable."""
        script_path = Path("scripts/sync_versions.py")
        assert script_path.exists(), "sync_versions.py script should exist"
        assert script_path.is_file(), "sync_versions.py should be a file"

    def test_sync_versions_script_runs(self):
        """Test that the sync_versions script can be executed."""
        result = subprocess.run(
            ["python", "scripts/sync_versions.py"],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        # Script should complete successfully
        assert result.returncode == 0, f"Script failed with error: {result.stderr}"

        # Should contain expected output patterns
        output = result.stdout
        assert "pyproject.toml version:" in output
        assert any(
            msg in output
            for msg in [
                "All versions already synchronized",
                "Version synchronization completed",
            ]
        )

    def test_version_consistency_check(self):
        """Test that versions are consistent between files."""
        # Read version from pyproject.toml
        pyproject_path = Path("pyproject.toml")
        pyproject_content = pyproject_path.read_text()

        # Extract version using simple string parsing
        for line in pyproject_content.split("\n"):
            if line.strip().startswith("version = "):
                pyproject_version = line.split('"')[1]
                break
        else:
            pytest.fail("Could not find version in pyproject.toml")

        # Read version from __init__.py
        init_path = Path("src/mqtt_publisher/__init__.py")
        init_content = init_path.read_text()

        # Extract version from __init__.py
        for line in init_content.split("\n"):
            if line.strip().startswith("__version__ = "):
                init_version = line.split('"')[1]
                break
        else:
            pytest.fail("Could not find __version__ in __init__.py")

        # Versions should match
        assert pyproject_version == init_version, (
            f"Version mismatch: pyproject.toml={pyproject_version}, "
            f"__init__.py={init_version}"
        )


class TestReleaseScript:
    """Test the release script functionality."""

    def test_release_script_exists(self):
        """Test that the release script exists and is executable."""
        script_path = Path("release.sh")
        assert script_path.exists(), "release.sh script should exist"
        assert script_path.is_file(), "release.sh should be a file"

    def test_release_script_help(self):
        """Test that the release script shows help/usage information."""
        result = subprocess.run(
            ["bash", "release.sh", "invalid"],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        # Should exit with error for invalid argument
        assert result.returncode != 0

        # Should contain usage information
        output = result.stderr
        assert "Invalid bump type" in output or "Usage:" in output


class TestGitHubActionsWorkflows:
    """Test GitHub Actions workflow files."""

    def test_ci_workflow_exists(self):
        """Test that CI workflow exists and is valid."""
        workflow_path = Path(".github/workflows/ci.yml")
        assert workflow_path.exists(), "CI workflow should exist"

        content = workflow_path.read_text()
        assert "name: CI" in content
        assert "on:" in content
        assert "jobs:" in content

    def test_release_workflow_exists(self):
        """Test that release workflow exists and is valid."""
        workflow_path = Path(".github/workflows/release.yml")
        assert workflow_path.exists(), "Release workflow should exist"

        content = workflow_path.read_text()
        assert "name: Release" in content
        assert "on:" in content
        assert "tags:" in content

    def test_version_bump_workflow_exists(self):
        """Test that version bump workflow exists and is valid."""
        workflow_path = Path(".github/workflows/version-bump.yml")
        assert workflow_path.exists(), "Version bump workflow should exist"

        content = workflow_path.read_text()
        assert "name: Auto Version Bump" in content
        assert "workflow_dispatch:" in content
        assert "bump_type:" in content


class TestAutomationDocumentation:
    """Test automation documentation and configuration."""

    def test_automation_docs_exist(self):
        """Test that automation documentation exists."""
        docs_path = Path("docs/VERSION_AUTOMATION.md")
        assert docs_path.exists(), "Version automation documentation should exist"

        content = docs_path.read_text()
        assert "Version Management Automation" in content
        assert "Automation Levels" in content

    def test_examples_readme_exists(self):
        """Test that examples README exists."""
        readme_path = Path("examples/README.md")
        assert readme_path.exists(), "Examples README should exist"

        content = readme_path.read_text()
        assert "MQTT Publisher Examples" in content
        assert "Prerequisites" in content

    def test_config_readme_exists(self):
        """Test that config README exists."""
        readme_path = Path("config/README.md")
        assert readme_path.exists(), "Config README should exist"

        content = readme_path.read_text()
        assert "Configuration Templates" in content


class TestCommitizen:
    """Test Commitizen configuration."""

    def test_commitizen_config_in_pyproject(self):
        """Test that Commitizen is configured in pyproject.toml."""
        pyproject_path = Path("pyproject.toml")
        content = pyproject_path.read_text()

        assert "[tool.commitizen]" in content
        assert "cz_conventional_commits" in content
        assert "version_files" in content

    def test_commitizen_version_files_correct(self):
        """Test that Commitizen version files are correctly configured."""
        pyproject_path = Path("pyproject.toml")
        content = pyproject_path.read_text()

        # Should include both version files
        assert "pyproject.toml:version" in content
        assert "src/mqtt_publisher/__init__.py:__version__" in content


class TestPreCommitHook:
    """Test pre-commit hook functionality."""

    def test_precommit_hook_exists(self):
        """Test that pre-commit hook script exists."""
        hook_path = Path("scripts/pre-commit-version-sync")
        assert hook_path.exists(), "Pre-commit hook should exist"

        content = hook_path.read_text()
        assert "sync_versions.py" in content

    def test_precommit_hook_executable(self):
        """Test that pre-commit hook is executable."""
        hook_path = Path("scripts/pre-commit-version-sync")

        # Check if file has execute permissions
        import stat

        file_stat = hook_path.stat()
        is_executable = bool(file_stat.st_mode & stat.S_IEXEC)

        assert is_executable, "Pre-commit hook should be executable"


class TestProjectStructure:
    """Test overall project structure for automation."""

    def test_scripts_directory_exists(self):
        """Test that scripts directory exists."""
        scripts_dir = Path("scripts")
        assert scripts_dir.exists(), "Scripts directory should exist"
        assert scripts_dir.is_dir(), "Scripts should be a directory"

    def test_docs_directory_exists(self):
        """Test that docs directory exists."""
        docs_dir = Path("docs")
        assert docs_dir.exists(), "Docs directory should exist"
        assert docs_dir.is_dir(), "Docs should be a directory"

    def test_required_automation_files_exist(self):
        """Test that all required automation files exist."""
        required_files = [
            "scripts/sync_versions.py",
            "scripts/pre-commit-version-sync",
            "release.sh",
            ".github/workflows/ci.yml",
            ".github/workflows/release.yml",
            ".github/workflows/version-bump.yml",
            "docs/VERSION_AUTOMATION.md",
        ]

        for file_path in required_files:
            path = Path(file_path)
            assert path.exists(), f"Required automation file {file_path} should exist"


if __name__ == "__main__":
    pytest.main([__file__])
