#!/bin/bash

# Semantic versioning release script for mqtt_publisher
# Usage: ./release.sh [--major|--minor|--patch]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository"
    exit 1
fi

# Check if working directory is clean
if ! git diff-index --quiet HEAD --; then
    print_error "Working directory is not clean. Please commit or stash changes."
    exit 1
fi

# Check if we're on main branch
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$current_branch" != "main" ]; then
    print_warning "Not on main branch (currently on $current_branch)"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Default to patch if no argument provided
BUMP_TYPE=${1:-patch}

# Remove leading dashes if present
BUMP_TYPE=${BUMP_TYPE#--}

# Validate bump type
if [[ ! "$BUMP_TYPE" =~ ^(major|minor|patch)$ ]]; then
    print_error "Invalid bump type: $BUMP_TYPE"
    echo "Usage: $0 [major|minor|patch]"
    exit 1
fi

print_status "Preparing $BUMP_TYPE release..."

# Get current version from pyproject.toml
current_version=$(poetry version --short)
print_status "Current version: $current_version"

# Bump version
print_status "Bumping $BUMP_TYPE version..."
poetry version $BUMP_TYPE
new_version=$(poetry version --short)

print_success "Version bumped from $current_version to $new_version"

# Synchronize version across all files
print_status "Synchronizing version across all project files..."
if command -v python3 &> /dev/null; then
    python3 scripts/sync_versions.py
else
    poetry run python scripts/sync_versions.py
fi

# Create git tag
tag_name="v$new_version"
print_status "Creating git tag: $tag_name"

# Commit version bump
git add pyproject.toml src/mqtt_publisher/__init__.py
git commit -m "chore: bump version to $new_version"

# Create and push tag
git tag -a "$tag_name" -m "Release $tag_name"

print_success "Created tag: $tag_name"

# Ask for confirmation before pushing
echo
print_warning "Ready to push tag $tag_name to origin."
print_warning "This will trigger the release workflow and publish to PyPI."
echo
read -p "Push tag and trigger release? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Pushing changes and tag to origin..."
    git push origin main
    git push origin "$tag_name"
    print_success "Release $tag_name pushed to origin!"
    echo
    print_status "🚀 Release workflow should now be running on GitHub Actions"
    print_status "📦 Package will be published to PyPI shortly"
    echo
    print_status "Monitor the release at:"
    print_status "https://github.com/ronschaeffer/mqtt_publisher/actions"
else
    print_warning "Release cancelled. Tag created locally but not pushed."
    print_status "To push later: git push origin main && git push origin $tag_name"
fi
