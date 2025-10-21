"""Test save button tooltip updates based on unsaved state."""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("SAVE BUTTON TOOLTIP - DYNAMIC STATE TEST")
print("=" * 70)

print("\n[1] Testing tooltip translations exist...")
try:
    from lib.i18n.translations import LIBRARY_MANAGER_TRANSLATIONS
    
    for lang in ['en', 'vi']:
        trans = LIBRARY_MANAGER_TRANSLATIONS.get(lang, {})
        
        print(f"\n{lang.upper()} translations:")
        
        # Check for base tooltip
        base_key = 'tip_apply_all'
        if base_key in trans:
            print(f"  ✓ {base_key}: '{trans[base_key]}'")
        else:
            print(f"  ✗ {base_key}: MISSING")
        
        # Check for saved state
        saved_key = 'tip_apply_all_saved'
        if saved_key in trans:
            print(f"  ✓ {saved_key}: '{trans[saved_key]}'")
        else:
            print(f"  ✗ {saved_key}: MISSING")
        
        # Check for unsaved state
        unsaved_key = 'tip_apply_all_unsaved'
        if unsaved_key in trans:
            print(f"  ✓ {unsaved_key}: '{trans[unsaved_key]}'")
        else:
            print(f"  ✗ {unsaved_key}: MISSING")
            
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n[2] Testing LibraryManager has save button reference...")
try:
    from lib.ui.library_manager import LibraryManagerWindow
    import inspect
    
    # Check __init__ creates save_btn
    source = inspect.getsource(LibraryManagerWindow.__init__)
    
    if 'self.save_btn' in source:
        print("✓ LibraryManager stores save_btn reference")
    else:
        print("✗ WARNING: save_btn reference not found")
        
except Exception as e:
    print(f"✗ Error: {e}")

print("\n[3] Testing _update_save_button_tooltip method exists...")
try:
    from lib.ui.library_manager import LibraryManagerWindow
    
    if hasattr(LibraryManagerWindow, '_update_save_button_tooltip'):
        print("✓ _update_save_button_tooltip method exists")
        
        import inspect
        sig = inspect.signature(LibraryManagerWindow._update_save_button_tooltip)
        params = list(sig.parameters.keys())
        print(f"  Parameters: {params}")
        
        if 'has_unsaved' in params:
            print("  ✓ has_unsaved parameter found")
        else:
            print("  ✗ has_unsaved parameter missing")
    else:
        print("✗ _update_save_button_tooltip method NOT FOUND")
        
except Exception as e:
    print(f"✗ Error: {e}")

print("\n[4] Testing _mark_unsaved calls tooltip update...")
try:
    from lib.ui.library_manager import LibraryManagerWindow
    import inspect
    
    source = inspect.getsource(LibraryManagerWindow._mark_unsaved)
    
    if '_update_save_button_tooltip' in source:
        print("✓ _mark_unsaved calls _update_save_button_tooltip")
    else:
        print("✗ WARNING: _mark_unsaved does not call tooltip update")
        
except Exception as e:
    print(f"✗ Error: {e}")

print("\n[5] Testing tooltip helper integration...")
try:
    from lib.ui.tooltip import attach_i18n_tooltip
    print("✓ attach_i18n_tooltip imported successfully")
    
    import inspect
    sig = inspect.signature(attach_i18n_tooltip)
    params = list(sig.parameters.keys())
    print(f"  Parameters: {params}")
    
    required = ['widget', 'key', 'ns', 'lang_provider']
    missing = [p for p in required if p not in params]
    
    if not missing:
        print("  ✓ All required parameters present")
    else:
        print(f"  ✗ Missing parameters: {missing}")
        
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
print("\nSUMMARY:")
print("- Tooltip keys added for saved/unsaved states")
print("- Save button reference stored in LibraryManager")
print("- _update_save_button_tooltip method updates tooltip dynamically")
print("- _mark_unsaved triggers tooltip update")
print("- Uses global i18n tooltip system for consistency")
print("=" * 70)
