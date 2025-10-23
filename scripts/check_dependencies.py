#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dependency Checker - Verify all required packages are installed
Sprint 23 Phase 5 - Overlay Window Dependencies

Usage:
    python scripts/check_dependencies.py
    python scripts/check_dependencies.py --install
"""

import sys
import subprocess
from pathlib import Path

REQUIRED_PACKAGES = {
    'opencv-python': 'opencv-python>=4.8.0',
    'numpy': 'numpy>=1.24.0',
    'pillow': 'pillow>=10.0.0',
    'pyautogui': 'pyautogui>=0.9.50',
    'keyboard': 'keyboard>=0.13.5',
    'pywin32': 'pywin32>=306',  # Required for overlay window
    'pytest': 'pytest>=8.0.0',
}

def check_package(package_name):
    """Check if a package is installed."""
    try:
        __import__(package_name.replace('-', '_'))
        return True
    except ImportError:
        return False

def install_package(pip_spec):
    """Install a package using pip."""
    print(f"  Installing: {pip_spec}")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', pip_spec])
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Failed to install {pip_spec}: {e}")
        return False

def main():
    """Check and optionally install dependencies."""
    auto_install = '--install' in sys.argv or '-i' in sys.argv
    
    print("=" * 60)
    print("Cabal_Auto Dependency Check")
    print("=" * 60)
    print(f"Python: {sys.version}")
    print(f"Executable: {sys.executable}")
    print("=" * 60)
    
    missing = []
    installed = []
    
    for package, pip_spec in REQUIRED_PACKAGES.items():
        status = check_package(package)
        
        if status:
            print(f"✓ {package:20s} - Installed")
            installed.append(package)
        else:
            print(f"✗ {package:20s} - MISSING")
            missing.append((package, pip_spec))
    
    print("=" * 60)
    print(f"Summary: {len(installed)}/{len(REQUIRED_PACKAGES)} packages installed")
    
    if missing:
        print(f"\n⚠ Missing {len(missing)} package(s):")
        for package, pip_spec in missing:
            print(f"  - {pip_spec}")
        
        if auto_install:
            print("\n🔧 Auto-installing missing packages...")
            for package, pip_spec in missing:
                if install_package(pip_spec):
                    print(f"  ✓ {package} installed successfully")
                else:
                    print(f"  ✗ {package} installation failed")
        else:
            print("\n💡 To install missing packages, run:")
            print(f"   python {__file__} --install")
            print("\n   Or manually:")
            print(f"   pip install {' '.join([spec for _, spec in missing])}")
            return 1
    else:
        print("\n✅ All dependencies are installed!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
