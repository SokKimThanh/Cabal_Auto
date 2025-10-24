"""
Test script to verify all UI imports after reorganization.

This script tests all the new import paths to ensure they work correctly.
"""

import sys
from pathlib import Path

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
        print(f"   ❌ ui.components import failed: {e}")
        return False
    
    # Test 2: Helpers
    print("\n2. Testing ui.helpers...")
    try:
        from ui.helpers import IconHelper, get_button_config, attach_i18n_tooltip, get_icon_helper
        print("   ✅ ui.helpers imports OK")
    except ImportError as e:
        print(f"   ❌ ui.helpers import failed: {e}")
        return False
    
    # Test 3: Helpers - individual modules
    print("\n3. Testing ui.helpers submodules...")
    try:
        from ui.helpers.button_styles import get_button_config
        from ui.helpers.icon_helper import IconHelper
        from ui.helpers.tooltip import attach_i18n_tooltip
        from ui.helpers.capture_helper import capture_region_and_save
        print("   ✅ ui.helpers.* imports OK")
    except ImportError as e:
        print(f"   ❌ ui.helpers.* import failed: {e}")
        return False
    
    # Test 4: Windows
    print("\n4. Testing ui.windows...")
    try:
        from ui.windows.library_manager import LibraryManagerWindow
        from ui.windows.quick_monster_editor import QuickMonsterEditor
        from ui.windows.setup_wizard import show_setup_wizard
        from ui.windows.overlay_window import OverlayWindowPyWin32
        print("   ✅ ui.windows imports OK")
    except ImportError as e:
        print(f"   ❌ ui.windows import failed: {e}")
        return False
    
    # Test 5: Utils
    print("\n5. Testing ui.utils...")
    try:
        from ui.utils.overlay_controller import OverlayController
        from ui.utils.window_tracker import WindowTracker
        from ui.utils.overlay_settings import OverlaySettingsDialog
        print("   ✅ ui.utils imports OK")
    except ImportError as e:
        print(f"   ❌ ui.utils import failed: {e}")
        return False
    
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
        print(f"   ❌ ui package exports failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All imports working correctly!")
    print("\nUI Package Structure:")
    print("  ui/")
    print("  ├── components/    - UI components (button, label)")
    print("  ├── helpers/       - Helper utilities (icon, button_styles, tooltip)")
    print("  ├── windows/       - Main windows & dialogs")
    print("  └── utils/         - Utility functions (overlay, window_tracker)")
    print("\n" + "=" * 60)
    
    return True


def test_old_imports():
    """Test that old imports are properly deprecated."""
    
    print("\nTesting deprecated imports...")
    print("=" * 60)
    
    # Test that lib.ui is properly marked as deprecated
    print("\n7. Testing lib.ui deprecation...")
    try:
        import lib.ui
        print("   ℹ️  lib.ui still accessible (deprecated)")
        
        # Check if __init__ has deprecation notice
        if hasattr(lib.ui, '__doc__') and lib.ui.__doc__:
            if 'DEPRECATED' in lib.ui.__doc__:
                print("   ✅ lib.ui properly marked as DEPRECATED")
            else:
                print("   ⚠️  lib.ui missing deprecation notice")
        else:
            print("   ⚠️  lib.ui missing documentation")
    except ImportError:
        print("   ✅ lib.ui removed (clean)")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    success = test_imports()
    test_old_imports()
    
    if success:
        print("\n🎉 All tests passed! UI reorganization successful!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
