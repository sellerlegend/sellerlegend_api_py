#!/usr/bin/env python3
"""
Release automation script for SellerLegend Python SDK

This script automates the release process:
1. Bumps version in pyproject.toml and setup.py
2. Commits the version bump
3. Creates and pushes a git tag
4. Builds the distribution
5. Uploads to PyPI

Usage:
    python release.py [patch|minor|major]

    patch: 1.0.1 -> 1.0.2 (default)
    minor: 1.0.1 -> 1.1.0
    major: 1.0.1 -> 2.0.0
"""

import os
import sys
import re
import subprocess
from pathlib import Path


def run_command(cmd, capture_output=False):
    """Run a shell command and handle errors."""
    print(f"Running: {cmd}")
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, shell=True, check=True)
            return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e}")
        if capture_output and e.stderr:
            print(f"stderr: {e.stderr}")
        sys.exit(1)


def get_current_version():
    """Extract current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("Error: pyproject.toml not found")
        sys.exit(1)

    content = pyproject_path.read_text()
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not match:
        print("Error: Version not found in pyproject.toml")
        sys.exit(1)

    return match.group(1)


def bump_version(current_version, bump_type="patch"):
    """Bump version based on type (major, minor, patch)."""
    parts = current_version.split(".")
    if len(parts) != 3:
        print(f"Error: Invalid version format: {current_version}")
        sys.exit(1)

    major, minor, patch = map(int, parts)

    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        print(f"Error: Invalid bump type: {bump_type}")
        sys.exit(1)

    return f"{major}.{minor}.{patch}"


def update_version_in_file(file_path, old_version, new_version):
    """Update version string in a file."""
    if not file_path.exists():
        print(f"Warning: {file_path} not found, skipping")
        return False

    content = file_path.read_text()

    # For pyproject.toml and setup.py, look for version = "x.x.x"
    pattern = r'(version\s*=\s*")[^"]+(")'
    replacement = f'\\g<1>{new_version}\\g<2>'

    new_content = re.sub(pattern, replacement, content)

    if new_content != content:
        file_path.write_text(new_content)
        print(f"Updated version in {file_path}")
        return True
    else:
        print(f"Warning: Version not found or already up to date in {file_path}")
        return False


def check_git_status():
    """Check if git working directory is clean."""
    status = run_command("git status --porcelain", capture_output=True)
    if status:
        print("Error: Git working directory is not clean. Please commit or stash changes first.")
        print("Uncommitted changes:")
        print(status)
        sys.exit(1)


def check_prerequisites():
    """Check if required tools are installed."""
    # Check for git
    try:
        run_command("git --version", capture_output=True)
    except:
        print("Error: git is not installed")
        sys.exit(1)

    # Check for Python build tools
    try:
        run_command("python -m build --version", capture_output=True)
    except:
        print("Error: build package is not installed. Run: pip install build")
        sys.exit(1)

    # Check for twine
    try:
        run_command("python -m twine --version", capture_output=True)
    except:
        print("Error: twine is not installed. Run: pip install twine")
        sys.exit(1)

    # Check for PyPI credentials
    pypirc = Path.home() / ".pypirc"
    if not pypirc.exists():
        print("Warning: ~/.pypirc not found. You'll need to enter PyPI credentials manually.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)


def main():
    """Main release process."""
    # Parse arguments
    bump_type = "patch"  # default
    if len(sys.argv) > 1:
        bump_type = sys.argv[1].lower()
        if bump_type not in ["patch", "minor", "major"]:
            print(f"Error: Invalid bump type: {bump_type}")
            print("Usage: python release.py [patch|minor|major]")
            sys.exit(1)

    print("=" * 60)
    print("SellerLegend Python SDK - Release Script")
    print("=" * 60)

    # Check prerequisites
    print("\n1. Checking prerequisites...")
    check_prerequisites()

    # Check git status
    print("\n2. Checking git status...")
    check_git_status()

    # Get current version
    print("\n3. Getting current version...")
    current_version = get_current_version()
    print(f"Current version: {current_version}")

    # Calculate new version
    new_version = bump_version(current_version, bump_type)
    print(f"New version: {new_version} ({bump_type} bump)")

    # Confirm with user
    print("\n" + "=" * 60)
    print(f"Ready to release version {new_version}")
    print("This will:")
    print(f"  1. Update version {current_version} -> {new_version}")
    print(f"  2. Commit the version bump")
    print(f"  3. Create and push tag v{new_version}")
    print(f"  4. Build the distribution")
    print(f"  5. Upload to PyPI")
    print("=" * 60)
    response = input("\nProceed? (y/n): ")
    if response.lower() != 'y':
        print("Release cancelled")
        sys.exit(0)

    # Update versions
    print(f"\n4. Updating version to {new_version}...")
    files_updated = False

    # Update pyproject.toml
    if update_version_in_file(Path("pyproject.toml"), current_version, new_version):
        files_updated = True

    # Update setup.py
    if update_version_in_file(Path("setup.py"), current_version, new_version):
        files_updated = True

    if not files_updated:
        print("Error: No files were updated. Check version format in files.")
        sys.exit(1)

    # Commit version bump
    print("\n5. Committing version bump...")
    run_command(f'git add pyproject.toml setup.py')
    commit_message = f'Bump version to {new_version}'
    run_command(f'git commit -m "{commit_message}"')

    # Create and push tag
    print(f"\n6. Creating and pushing tag v{new_version}...")
    tag_message = f'Release v{new_version}'
    run_command(f'git tag -a v{new_version} -m "{tag_message}"')

    # Push commits and tags
    print("\n7. Pushing to GitHub...")
    run_command('git push origin main')
    run_command(f'git push origin v{new_version}')

    # Clean previous builds
    print("\n8. Cleaning previous builds...")
    run_command('rm -rf dist/ build/ *.egg-info')

    # Build distribution
    print("\n9. Building distribution...")
    run_command('python -m build')

    # Upload to PyPI
    print("\n10. Uploading to PyPI...")
    run_command('python -m twine upload dist/*')

    print("\n" + "=" * 60)
    print(f"✅ Successfully released version {new_version}!")
    print(f"View on PyPI: https://pypi.org/project/sellerlegend-api/{new_version}/")
    print(f"View on GitHub: https://github.com/sellerlegend/sellerlegend_api_py/releases/tag/v{new_version}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nRelease cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)