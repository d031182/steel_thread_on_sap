#!/usr/bin/env python3
"""
Pre-Commit Hook Installation Script
Purpose: Install and configure pre-commit hooks for the project
Usage: python scripts/install_pre_commit.py
"""

import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Verify Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}")
    return True


def check_git_repo():
    """Verify we're in a git repository"""
    git_dir = Path('.git')
    if not git_dir.exists():
        print("❌ Not a git repository")
        return False
    print("✅ Git repository detected")
    return True


def install_pre_commit():
    """Install pre-commit package"""
    print("\n📦 Installing pre-commit package...")
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 'pre-commit'],
            check=True,
            capture_output=True,
            text=True
        )
        print("✅ pre-commit package installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install pre-commit: {e.stderr}")
        return False


def install_hooks():
    """Install pre-commit hooks into .git/hooks"""
    print("\n🔧 Installing pre-commit hooks...")
    try:
        result = subprocess.run(
            ['pre-commit', 'install'],
            check=True,
            capture_output=True,
            text=True
        )
        print("✅ Pre-commit hooks installed")
        if result.stdout:
            print(f"   {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install hooks: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ pre-commit command not found. Please install pre-commit first.")
        return False


def test_hooks():
    """Test pre-commit hooks on all files"""
    print("\n🧪 Testing pre-commit hooks (optional)...")
    print("   This may take a moment on first run...")
    try:
        result = subprocess.run(
            ['pre-commit', 'run', '--all-files'],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print("✅ All pre-commit hooks passed")
        else:
            print("⚠️  Some hooks found issues (expected on first run)")
            print("   Run 'pre-commit run --all-files' to see details")
        return True
    except subprocess.TimeoutExpired:
        print("⏱️  Hook testing timed out (not critical)")
        return True
    except Exception as e:
        print(f"⚠️  Could not test hooks: {e}")
        return True


def main():
    """Main installation workflow"""
    print("=" * 60)
    print("🚀 Pre-Commit Hook Installation")
    print("=" * 60)
    print()
    
    # Validation checks
    if not check_python_version():
        return 1
    
    if not check_git_repo():
        return 1
    
    # Installation steps
    if not install_pre_commit():
        return 1
    
    if not install_hooks():
        return 1
    
    # Optional testing
    test_hooks()
    
    print()
    print("=" * 60)
    print("✨ Pre-commit setup complete!")
    print("=" * 60)
    print()
    print("📚 Next steps:")
    print("   1. Make changes to your code")
    print("   2. Stage files: git add .")
    print("   3. Commit: git commit -m 'your message'")
    print("   4. Pre-commit hooks will run automatically")
    print()
    print("💡 Useful commands:")
    print("   - Run hooks manually: pre-commit run --all-files")
    print("   - Skip hooks (not recommended): git commit --no-verify")
    print("   - Update hooks: pre-commit autoupdate")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())