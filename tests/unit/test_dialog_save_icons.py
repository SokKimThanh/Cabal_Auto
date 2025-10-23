"""Test Monster/Skill Dialog Save Icons and Tooltips.

This test verifies:
1. MonsterDialog save button displays save.ico icon
2. SkillDialog save button displays save.ico icon
3. Both dialogs have i18n tooltips (EN/VI)
4. Icon fallback works when .ico unavailable

Note: GUI tests are marked with @pytest.mark.gui and skip on non-Windows.
For automated testing, only test_icon_availability runs.
For manual GUI testing, run: python tests/unit/test_dialog_save_icons.py
"""

import sys
from pathlib import Path
import pytest

# Mark as GUI test (skips in CI)
pytestmark = [pytest.mark.gui, pytest.mark.windows]

# Skip entire module on non-Windows (prevents GUI import errors)
if sys.platform != "win32":
    pytest.skip("Requires Windows environment with GUI", allow_module_level=True)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import tkinter as tk
from lib.ui.library_manager import MonsterDialog, SkillDialog
from lib.ui.icon_helper import get_icon_helper
from lib.i18n import t as i18n_t


def test_icon_availability():
    """Test save.ico availability - automated test (no GUI)."""
    print("=" * 60)
    print("TEST: Save Icon Availability (Automated)")
    print("=" * 60)
    
    icon_helper = get_icon_helper()
    
    # Test save icon
    save_icon = icon_helper.get_icon('save')
    
    # Assert icon exists
    assert save_icon is not None, "Save icon should be loaded"
    print("✅ Save icon loaded successfully")
    print(f"   Type: {type(save_icon)}")
    
    # Check if it's PhotoImage
    if hasattr(save_icon, 'width') and hasattr(save_icon, 'height'):
        width = save_icon.width()
        height = save_icon.height()
        print(f"   Size: {width}x{height}")
        assert width > 0 and height > 0, "Icon should have valid dimensions"
    
    # Check fallback
    save_fallback = icon_helper.get_icon('nonexistent_icon', fallback='💾')
    assert save_fallback == '💾', "Should return fallback for missing icon"
    print(f"   Fallback text: {save_fallback}")
    
    # Check file paths
    project_root = Path(__file__).parent.parent.parent
    
    ico_path = project_root / 'assets' / 'images' / 'icons' / 'save.ico'
    png_path = project_root / 'assets' / 'images' / 'icons' / 'save.png'
    
    print(f"\n📁 Icon Files:")
    print(f"   save.ico: {'✅ EXISTS' if ico_path.exists() else '❌ NOT FOUND'} ({ico_path})")
    if ico_path.exists():
        file_size = ico_path.stat().st_size
        print(f"            Size: {file_size:,} bytes")
        assert file_size > 0, "Icon file should not be empty"
    
    print(f"   save.png: {'✅ EXISTS' if png_path.exists() else '❌ NOT FOUND'} ({png_path})")
    if png_path.exists():
        file_size = png_path.stat().st_size
        print(f"            Size: {file_size:,} bytes")
        assert file_size > 0, "PNG file should not be empty"
    
    # At least one icon format should exist
    assert ico_path.exists() or png_path.exists(), "At least one icon format (ico/png) should exist"
    
    print("\n✅ Icon availability test completed\n")


@pytest.mark.gui
@pytest.mark.manual
def test_monster_dialog_icon():
    """Test MonsterDialog save button icon - MANUAL GUI TEST ONLY.
    
    This test opens real GUI dialogs and requires user interaction.
    Run manually with: python tests/unit/test_dialog_save_icons.py
    """
    print("=" * 60)
    print("TEST: MonsterDialog Save Icon & Tooltip (Manual GUI)")
    print("=" * 60)
    
    root = tk.Tk()
    root.withdraw()
    
    # Get icon helper
    icon_helper = get_icon_helper()
    
    # Test in EN
    print("\n[EN] Opening MonsterDialog (Add Monster)...")
    dialog_en = MonsterDialog(
        root, 
        lang='en', 
        mode='add',
        icon_helper=icon_helper,
        i18n_registry=i18n_t
    )
    
    if dialog_en.result:
        print(f"✅ Monster added: {dialog_en.result.get('name')}")
    else:
        print("ℹ️  Dialog cancelled")
    
    # Test in VI
    print("\n[VI] Opening MonsterDialog (Thêm Quái)...")
    dialog_vi = MonsterDialog(
        root, 
        lang='vi', 
        mode='add',
        icon_helper=icon_helper,
        i18n_registry=i18n_t
    )
    
    if dialog_vi.result:
        print(f"✅ Quái đã thêm: {dialog_vi.result.get('name')}")
    else:
        print("ℹ️  Đã hủy")
    
    root.destroy()
    print("\n✅ MonsterDialog test completed\n")


@pytest.mark.gui
@pytest.mark.manual
def test_skill_dialog_icon():
    """Test SkillDialog save button icon - MANUAL GUI TEST ONLY.
    
    This test opens real GUI dialogs and requires user interaction.
    Run manually with: python tests/unit/test_dialog_save_icons.py
    """
    print("=" * 60)
    print("TEST 2: SkillDialog Save Icon & Tooltip")
    print("=" * 60)
    
    root = tk.Tk()
    root.withdraw()
    
    # Get icon helper
    icon_helper = get_icon_helper()
    
    # Test in EN
    print("\n[EN] Opening SkillDialog (Add Skill)...")
    dialog_en = SkillDialog(
        root, 
        lang='en', 
        mode='add',
        icon_helper=icon_helper,
        i18n_registry=i18n_t
    )
    
    if dialog_en.result:
        print(f"✅ Skill added: {dialog_en.result.get('name')}")
    else:
        print("ℹ️  Dialog cancelled")
    
    # Test in VI
    print("\n[VI] Opening SkillDialog (Thêm Kỹ Năng)...")
    dialog_vi = SkillDialog(
        root, 
        lang='vi', 
        mode='add',
        icon_helper=icon_helper,
        i18n_registry=i18n_t
    )
    
    if dialog_vi.result:
        print(f"✅ Kỹ năng đã thêm: {dialog_vi.result.get('name')}")
    else:
        print("ℹ️  Đã hủy")
    
    root.destroy()
    print("\n✅ SkillDialog test completed\n")


# =============================================================================
# MANUAL TESTING ONLY - Run with: python tests/unit/test_dialog_save_icons.py
# =============================================================================

def manual_test_icon_availability_detailed():
    """Detailed icon availability test for manual running."""
    print("=" * 60)
    print("MANUAL TEST: Save Icon Availability (Detailed)")
    print("=" * 60)
    
    icon_helper = get_icon_helper()
    
    # Test save icon
    save_icon = icon_helper.get_icon('save')
    
    if save_icon:
        print("✅ Save icon loaded successfully")
        print(f"   Type: {type(save_icon)}")
        
        # Check if it's PhotoImage
        if hasattr(save_icon, 'width') and hasattr(save_icon, 'height'):
            print(f"   Size: {save_icon.width()}x{save_icon.height()}")
    else:
        print("❌ Save icon not found")
    
    # Check fallback
    save_fallback = icon_helper.get_icon('save', fallback='💾')
    if isinstance(save_fallback, str):
        print(f"   Fallback text: {save_fallback}")
    else:
        print(f"   Icon loaded (not fallback)")
    
    # Check file paths
    project_root = Path(__file__).parent.parent.parent
    
    ico_path = project_root / 'assets' / 'images' / 'icons' / 'save.ico'
    png_path = project_root / 'assets' / 'images' / 'icons' / 'save.png'
    
    print(f"\n📁 Icon Files:")
    print(f"   save.ico: {'✅ EXISTS' if ico_path.exists() else '❌ NOT FOUND'} ({ico_path})")
    if ico_path.exists():
        print(f"            Size: {ico_path.stat().st_size:,} bytes")
    
    print(f"   save.png: {'✅ EXISTS' if png_path.exists() else '❌ NOT FOUND'} ({png_path})")
    if png_path.exists():
        print(f"            Size: {png_path.stat().st_size:,} bytes")
    
    print("\n✅ Icon availability test completed\n")


def main():
    """Run manual GUI tests - NOT for pytest automation."""
    print("\n" + "=" * 60)
    print("Dialog Save Icons & Tooltips - MANUAL TEST SUITE")
    print("=" * 60 + "\n")
    print("⚠️  This is a MANUAL test suite requiring user interaction")
    print("⚠️  For automated testing, run: pytest tests/unit/test_dialog_save_icons.py")
    print()
    
    try:
        # Test 1: Icon availability (detailed)
        manual_test_icon_availability_detailed()
        
        # Test 2: MonsterDialog
        response = input("📋 Test MonsterDialog GUI? (y/n): ")
        if response.lower() == 'y':
            test_monster_dialog_icon()
        
        # Test 3: SkillDialog
        response = input("📋 Test SkillDialog GUI? (y/n): ")
        if response.lower() == 'y':
            test_skill_dialog_icon()
        
        print("=" * 60)
        print("✅ ALL MANUAL TESTS COMPLETED")
        print("=" * 60)
        print("\nWhat to check:")
        print("1. ✅ Save button shows disk icon (not emoji)")
        print("2. ✅ Tooltip appears on hover")
        print("3. ✅ Tooltip text:")
        print("   - EN: 'Save monster' or 'Save skill'")
        print("   - VI: 'Lưu quái' or 'Lưu kỹ năng'")
        print("4. ✅ Icon fallback to 💾 if .ico missing")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
