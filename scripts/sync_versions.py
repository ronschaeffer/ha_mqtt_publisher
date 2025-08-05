#!/usr/bin/env python3
"""
Synchronize version across all project files.
This ensures pyproject.toml and __init__.py versions stay in sync.
"""

import re
import sys
from pathlib import Path


def get_pyproject_version():
    """Get version from pyproject.toml"""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found")

    content = pyproject_path.read_text()
    match = re.search(r'^version = "([^"]+)"', content, re.MULTILINE)
    if not match:
        raise ValueError("Version not found in pyproject.toml")

    return match.group(1)


def update_init_version(version):
    """Update version in __init__.py"""
    init_path = Path("src/mqtt_publisher/__init__.py")
    if not init_path.exists():
        raise FileNotFoundError("__init__.py not found")

    content = init_path.read_text()
    updated_content = re.sub(
        r'^__version__ = "[^"]+"',
        f'__version__ = "{version}"',
        content,
        flags=re.MULTILINE,
    )

    if content != updated_content:
        init_path.write_text(updated_content)
        print(f"✅ Updated __init__.py version to {version}")
        return True
    else:
        print(f"i  __init__.py already at version {version}")
        return False


def main():
    """Synchronize versions across all files"""
    try:
        version = get_pyproject_version()
        print(f"📦 Current pyproject.toml version: {version}")

        updated = update_init_version(version)

        if updated:
            print("🔄 Version synchronization completed")
            return 0
        else:
            print("✅ All versions already synchronized")
            return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
