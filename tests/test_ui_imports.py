"""
Test script to verify all UI imports after reorganization.

This script tests all the new import paths to ensure they work correctly.
"""

import sys
from pathlib import Path
import pytest

pytest.importorskip("tkinter", reason="Skipping UI imports because tkinter is not available in headless environment")

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test all new import paths."""
    
    print("Testing UI imports after reorganization...")
    print("=" * 60)
    
    # Test 1: Components
    print("\n1. Testing ui.components...")
    try:
        from ui.components import create_icon_button, create_icon_label
        print("   ✅ ui.components imports OK")
    except ImportError as e:
        pytest.fail(f"ui.components import failed: {e}")
    
    # Test 2: Helpers
    print("\n2. Testing ui.helpers...")
    try:
        from ui.helpers import IconHelper, get_button_config, attach_i18n_tooltip, get_icon_helper
        print("   ✅ ui.helpers imports OK")
    except ImportError as e:
        pytest.fail(f"ui.helpers import failed: {e}")
    
    # Test 3: Helpers - individual modules
    print("\n3. Testing ui.helpers submodules...")
    try:
        from ui.helpers.button_styles import get_button_config
        from ui.helpers.icon_helper import IconHelper
        from ui.helpers.tooltip import attach_i18n_tooltip
        from ui.helpers.capture_helper import capture_region_and_save
        print("   ✅ ui.helpers.* imports OK")
    except ImportError as e:
        pytest.fail(f"ui.helpers.* import failed: {e}")
    
    # Test 4: Windows
    print("\n4. Testing ui.windows...")
    try:
        from ui.windows.library_manager import LibraryManagerWindow
        from ui.windows.monster_manager_win import MonsterManagerWin
        from ui.windows.setup_wizard import show_setup_wizard
        try:
            from ui.windows.overlay_window import OverlayWindowPyWin32
        except RuntimeError as e:
            if "Windows" in str(e):
                print("   ℹ️  ui.windows.overlay_window platform guarded (Windows only)")
            else:
                raise
        print("   ✅ ui.windows imports OK")
    except ImportError as e:
        pytest.fail(f"ui.windows import failed: {e}")
    
    # Test 5: Utils
    print("\n5. Testing ui.utils...")
    try:
        try:
            from ui.utils.overlay_controller import OverlayController
        except RuntimeError as e:
            if "Windows" in str(e):
                print("   ℹ️  ui.utils.overlay_controller platform guarded (Windows only)")
            else:
                raise
        try:
            from ui.utils.window_tracker import WindowTracker
        except (ImportError, RuntimeError) as e:
            if "pywin32" in str(e) or "Windows" in str(e):
                print("   ℹ️  ui.utils.window_tracker platform guarded (Windows only)")
            else:
                raise
        from ui.utils.overlay_settings import OverlaySettingsDialog
        print("   ✅ ui.utils imports OK")
    except ImportError as e:
        pytest.fail(f"ui.utils import failed: {e}")
    
    # Test 6: Main UI package
    print("\n6. Testing ui package exports...")
    try:
        from ui import (
            create_icon_button,
            create_icon_label,
            IconHelper,
            get_button_config,
            attach_i18n_tooltip,
        )
        print("   ✅ ui package exports OK")
    except ImportError as e:
        pytest.fail(f"ui package exports failed: {e}")
    
    print("\n" + "=" * 60)
    print("✅ All imports working correctly!")
    print("\nUI Package Structure:")
    print("  ui/")
    print("  ├── components/    - UI components (button, label)")
    print("  ├── helpers/       - Helper utilities (icon, button_styles, tooltip)")
    print("  ├── windows/       - Main windows & dialogs")
    print("  └── utils/         - Utility functions (overlay, window_tracker)")
    print("\n" + "=" * 60)


def test_entry_points_smoke():
    """Smoke test to exercise main UI entry points and verify no lib.ui dependencies remain."""

    print("\nTesting UI entry points smoke tests...")
    print("=" * 60)

    entry_points = [
        ("ui.windows.auto_hunt", "AutoHunt UI"),
        ("ui.windows.library_manager", "Library Manager"),
        ("ui.windows.monster_manager_win", "Quick Monster Editor"),
        ("ui.windows.setup_wizard", "Setup Wizard"),
        ("ui.windows.setup_wizard_vision", "Setup Wizard Vision"),
        ("ui.components.icon_button", "Icon Button Component"),
        ("ui.helpers.icon_helper", "Icon Helper"),
        ("ui.helpers.button_styles", "Button Styles"),
        ("ui.helpers.tooltip", "Tooltip Helper"),
        ("ui.helpers.capture_helper", "Capture Helper"),
    ]

    for mod_path, name in entry_points:
        try:
            __import__(mod_path)
            print(f"   ✅ {name} ({mod_path}) imported OK")
        except (ImportError, RuntimeError) as e:
            if "Windows" in str(e) or "pywin32" in str(e):
                print(f"   ℹ️  {name} ({mod_path}) platform guarded (Windows only)")
            else:
                pytest.fail(f"{name} ({mod_path}) import failed: {e}")

    # Check sys.modules for any unexpected lib.ui modules
    stale_modules = [m for m in sys.modules if m.startswith('lib.ui.') or m == 'lib.ui']
    if stale_modules:
        print(f"   ❌ Stale lib.ui modules found in sys.modules: {stale_modules}")
        assert False, f"Stale lib.ui modules loaded: {stale_modules}"
    else:
        print("   ✅ No stale lib.ui modules loaded in sys.modules")

    print("\n" + "=" * 60)


def test_old_imports():
    """Test that old imports have been completely removed."""
    
    print("\nTesting removed imports...")
    print("=" * 60)
    
    # Test that lib.ui is cleanly removed
    print("\n7. Testing lib.ui removal...")
    try:
        import lib.ui
        assert False, "lib.ui is still accessible - removal incomplete!"
    except ImportError:
        print("   ✅ lib.ui removed (clean)")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    try:
        test_imports()
        test_entry_points_smoke()
        test_old_imports()
        print("\n🎉 All tests passed! UI reorganization successful!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Some tests failed: {e}")
        sys.exit(1)
