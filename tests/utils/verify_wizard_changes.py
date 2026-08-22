# -*- coding: utf-8 -*-
"""
Verify Setup Wizard Changes - User Level and Rotation Builder
This script verifies that all the new components are working correctly.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_translations():
    """Test that all translations are available."""
    print("\n=== Testing Translations ===")
    
    try:
        from lib.i18n.translations import SETUP_WIZARD_TRANSLATIONS
        
        # Check English translations
        en_keys = [
            'user_level_group', 'user_level_new', 'user_level_new_desc',
            'user_level_experienced', 'user_level_experienced_desc',
            'tip_user_level_new', 'tip_user_level_experienced',
            'open_rotation_builder', 'tip_rotation_builder',
            'rotation_builder_disabled_hint'
        ]
        
        for key in en_keys:
            if key not in SETUP_WIZARD_TRANSLATIONS['en']:
                print(f"❌ Missing EN translation: {key}")
                return False
            print(f"✓ EN: {key} = '{SETUP_WIZARD_TRANSLATIONS['en'][key][:50]}...'")
        
        # Check Vietnamese translations
        for key in en_keys:
            if key not in SETUP_WIZARD_TRANSLATIONS['vi']:
                print(f"❌ Missing VI translation: {key}")
                return False
            print(f"✓ VI: {key} = '{SETUP_WIZARD_TRANSLATIONS['vi'][key][:50]}...'")
        
        print("✓ All translations present!")
        return True
        
    except Exception as e:
        print(f"❌ Translation test failed: {e}")
        return False


def test_wizard_structure():
    """Test that SetupWizard has all necessary attributes and methods."""
    print("\n=== Testing Wizard Structure ===")
    
    try:
        from ui.setup_wizard import SetupWizard
        
        # Check for new attributes
        required_methods = [
            '_on_user_level_change',
            '_update_rotation_builder_button_state',
            '_open_rotation_builder'
        ]
        
        for method_name in required_methods:
            if not hasattr(SetupWizard, method_name):
                print(f"❌ Missing method: {method_name}")
                return False
            print(f"✓ Method exists: {method_name}")
        
        print("✓ All required methods present!")
        return True
        
    except Exception as e:
        print(f"❌ Structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_import_library_manager():
    """Test that LibraryManagerWindow can be imported."""
    print("\n=== Testing Library Manager Import ===")
    
    try:
        from ui.windows.library_manager import LibraryManagerWindow
        print("✓ LibraryManagerWindow imported successfully!")
        return True
    except Exception as e:
        print(f"❌ Library Manager import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("SETUP WIZARD CHANGES VERIFICATION")
    print("=" * 60)
    
    results = []
    
    results.append(("Translations", test_translations()))
    results.append(("Wizard Structure", test_wizard_structure()))
    results.append(("Library Manager Import", test_import_library_manager()))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("✓ ALL TESTS PASSED!")
        print("\nNext steps:")
        print("1. Run: python tests\\test_setup_wizard_skill_rotation.py")
        print("2. Go through wizard steps 1-4")
        print("3. In Step 1: Try both 'New User' and 'Experienced User' options")
        print("4. In Step 4: Check that rotation builder button is:")
        print("   - ENABLED for New Users")
        print("   - DISABLED for Experienced Users")
        print("5. Click the rotation builder button (when enabled) to open Library Manager")
    else:
        print("❌ SOME TESTS FAILED - Please fix issues above")
    
    sys.exit(0 if all_passed else 1)
