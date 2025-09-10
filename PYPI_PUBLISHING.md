# Publishing to PyPI

## Pre-Publishing Checklist

- [x] Clean up all debug and test scripts
- [x] Update README.md with comprehensive documentation
- [x] Ensure setup.py has correct metadata
- [x] Create modern pyproject.toml configuration
- [x] Create requirements.txt and requirements-dev.txt
- [x] Add proper .gitignore
- [x] Update MANIFEST.in
- [x] Add py.typed marker for type hints
- [x] Create CHANGELOG.md
- [x] Test package builds successfully
- [x] Remove sensitive test configurations
- [ ] Update version number in setup.py if needed
- [ ] Create git tag for release

## Publishing Steps

### 1. Test on TestPyPI (Optional but Recommended)

```bash
# Install/upgrade build tools
pip install --upgrade build twine

# Build the distribution
python -m build

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --no-deps sellerlegend-api
```

### 2. Publish to PyPI

```bash
# Build fresh distributions
rm -rf dist/ build/ *.egg-info
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

### 3. Verify Installation

```bash
# In a fresh virtual environment
pip install sellerlegend-api

# Test import
python -c "from sellerlegend_api import SellerLegendClient; print('Success!')"
```

## API Credentials for PyPI

You'll need:
1. PyPI account at https://pypi.org
2. API token from https://pypi.org/manage/account/token/
3. Configure ~/.pypirc or use `twine upload -u __token__ -p <your-token>`

## Post-Publishing

1. Create GitHub release with tag
2. Update documentation site if applicable
3. Announce release to users
4. Monitor for issues

## Version Management

Current version: 1.0.0

For updates:
1. Update version in setup.py
2. Update CHANGELOG (if exists)
3. Commit changes
4. Tag with version: `git tag v1.0.1`
5. Push tags: `git push --tags`