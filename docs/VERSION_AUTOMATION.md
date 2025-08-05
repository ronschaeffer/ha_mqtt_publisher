# Version Management Automation

This project supports multiple levels of version automation, from manual to fully automated.

## Automation Levels

### 1. Manual Versioning (Current)
```bash
# Edit pyproject.toml manually
poetry version patch
python scripts/sync_versions.py
git commit -am "chore: bump version"
```

### 2. Semi-Automated (Recommended)
```bash
# Use the release script
./release.sh patch   # or minor, major
```

### 3. GitHub Actions (Remote)
- Go to Actions → "Auto Version Bump"
- Select version type (patch/minor/major)
- Choose whether to create GitHub release
- Run workflow

### 4. Commitizen (Advanced)
```bash
# Install commitizen
poetry install --with automation

# Bump version with changelog
poetry run cz bump

# Or interactive
poetry run cz bump --interactive
```

## Features

### ✅ Current Automation
- **Version synchronization**: Keeps `pyproject.toml` and `__init__.py` in sync
- **Semantic versioning**: Support for major.minor.patch
- **Automated tagging**: Creates git tags for releases
- **PyPI publishing**: Automatic publishing on tag push
- **Release workflow**: GitHub Actions for complete release process

### 🚀 Enhanced Features Available

#### Pre-commit Hook (Optional)
Install the version sync pre-commit hook:
```bash
# Copy hook to git hooks directory
cp scripts/pre-commit-version-sync .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

#### Changelog Generation (Optional)
```bash
# Manual changelog update
echo "## [$(poetry version --short)] - $(date +%Y-%m-%d)" >> CHANGELOG.md

# Or use commitizen for automatic changelog
poetry run cz changelog
```

#### Automated Version Detection
The system can detect version bumps automatically based on:
- Commit message conventions (feat:, fix:, BREAKING CHANGE:)
- Pull request labels
- File changes

## Usage Examples

### Daily Development
```bash
# Make changes, commit
git commit -m "fix: resolve MQTT connection issue"

# When ready to release
./release.sh patch
```

### Feature Releases
```bash
# After completing a feature
git commit -m "feat: add Home Assistant discovery support"

# Bump minor version
./release.sh minor
```

### Breaking Changes
```bash
# After making breaking changes
git commit -m "feat!: restructure API for better usability"

# Bump major version
./release.sh major
```

### CI/CD Integration
```bash
# In GitHub Actions or CI pipeline
python scripts/sync_versions.py
poetry version patch
git tag "v$(poetry version --short)"
git push --tags
```

## Configuration

### Version Files Managed
- `pyproject.toml` - Primary version source
- `src/mqtt_publisher/__init__.py` - Package version
- Git tags - Release marking
- CHANGELOG.md - Version history (optional)

### Commitizen Configuration
Located in `pyproject.toml`:
```toml
[tool.commitizen]
name = "cz_conventional_commits"
version = "0.1.2"
tag_format = "v$version"
version_files = [
    "pyproject.toml:version",
    "src/mqtt_publisher/__init__.py:__version__"
]
```

## Best Practices

1. **Use semantic versioning**: 
   - Patch: Bug fixes, small changes
   - Minor: New features, backward compatible
   - Major: Breaking changes

2. **Commit message format**:
   ```
   type(scope): description
   
   feat: new feature
   fix: bug fix
   docs: documentation
   chore: maintenance
   ```

3. **Release workflow**:
   - Develop on feature branches
   - Merge to main
   - Run `./release.sh type`
   - Tag automatically triggers PyPI release

4. **Version consistency**:
   - Always use `./release.sh` or `python scripts/sync_versions.py`
   - Never edit version files manually without syncing
   - Use pre-commit hook to prevent version drift

## Troubleshooting

### Version Mismatch
```bash
# Fix version synchronization
python scripts/sync_versions.py
git add src/mqtt_publisher/__init__.py
git commit -m "fix: synchronize version"
```

### Failed Release
```bash
# Check current state
git status
poetry version --short

# Reset if needed
git reset --soft HEAD~1  # Reset last commit
git tag -d v0.1.3        # Delete local tag
```

### PyPI Upload Issues
```bash
# Manual upload if GitHub Actions fails
poetry build
poetry publish --username __token__ --password $PYPI_TOKEN
```
