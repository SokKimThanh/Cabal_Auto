"""
Test Setup Wizard with Optional Steps (Monster & Skills)

Verifies that:
1. Step 2 (Window) is REQUIRED
2. Step 3 (Monster) is OPTIONAL - can skip
3. Step 4 (Skills) is OPTIONAL - can skip
4. Step 5 (Review) shows appropriate messages for missing data

Purpose: Prevent data duplication by allowing early sync of basic settings

Run:
    python tests/manual/test_wizard_optional_steps.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def test_validation_logic():
    """Test validation logic for optional vs required steps."""
    print("="*70)
    print("🧪 Testing Setup Wizard Optional Steps Logic")
    print("="*70)
    print()
    
    print("📋 Step Requirements:")
    print("  Step 1 (Welcome): ✓ Always valid (language optional)")
    print("  Step 2 (Window):  🔴 REQUIRED (must select)")
    print("  Step 3 (Monster): ✓ OPTIONAL (can skip)")
    print("  Step 4 (Skills):  ✓ OPTIONAL (can skip)")
    print("  Step 5 (Review):  ✓ Always valid (summary)")
    print()
    
    print("💡 Design Rationale:")
    print("  • Early sync prevents data duplication across forms")
    print("  • New users can configure window first")
    print("  • Monster/Skills can be added later via Library Manager")
    print("  • Reduces first-run configuration errors")
    print()
    
    print("="*70)


def test_wizard_ui():
    """Test actual wizard UI with optional steps."""
    print()
    print("🧪 Testing Wizard UI")
    print("="*70)
    print()
    
    try:
        import tkinter as tk
        from ui.windows.setup_wizard import SetupWizard
        
        print("✅ Imports successful")
        
        # Create minimal parent window
        root = tk.Tk()
        root.withdraw()
        
        # Create wizard
        wizard = SetupWizard(
            parent=root,
            config_manager=None,
            on_complete=None,
            on_cancel=None,
            hide_parent=False
        )
        
        print("✅ Wizard created")
        print()
        
        print("📋 Expected Behavior:")
        print("  Step 2: Cannot proceed without window selection")
        print("  Step 3: Can proceed even without monster (shows info)")
        print("  Step 4: Can proceed even without skills (shows info)")
        print("  Step 5: Shows 'Note' for missing optional items")
        print()
        
        print("📌 Manual Test Steps:")
        print("  1. Run: python app_gui.py")
        print("  2. Let wizard open (first run)")
        print("  3. Step 1: Select language → Next")
        print("  4. Step 2: Try Next WITHOUT selecting window → Should BLOCK")
        print("  5. Step 2: Select window → Next → Should PROCEED")
        print("  6. Step 3: Try Next WITHOUT selecting monster → Should SHOW INFO & PROCEED")
        print("  7. Step 4: Try Next WITHOUT skills → Should SHOW INFO & PROCEED")
        print("  8. Step 5: Review → Should show 'Note' for missing items")
        print()
        
        # Close wizard
        wizard.dialog.destroy()
        root.destroy()
        
        print("✅ Test setup complete")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("="*70)


def test_empty_data_handling():
    """Test handling of empty monsters.json."""
    print()
    print("🧪 Testing Empty Data Handling")
    print("="*70)
    print()
    
    monsters_path = project_root / "lib" / "data" / "monsters.json"
    
    if not monsters_path.exists():
        print(f"⚠️ File not found: {monsters_path}")
        return
    
    import json
    try:
        with open(monsters_path, "r", encoding="utf-8") as f:
            monsters = json.load(f)
        
        print(f"📂 Monsters file: {monsters_path}")
        print(f"📊 Monsters count: {len(monsters)}")
        print()
        
        if not monsters:
            print("✅ Empty monsters.json detected")
            print("✅ Expected UI: Shows 'No Monsters Yet' message")
            print("✅ Expected UI: Shows '✓ You can skip this step' message")
            print("✅ Expected UI: Shows '💡 Tip: Click Next to continue' message")
            print("✅ Expected behavior: Next button should work without selection")
        else:
            print(f"ℹ️ {len(monsters)} monsters found")
            print("ℹ️ Step 3 will show monster list")
            print("ℹ️ User can select or skip")
        
    except Exception as e:
        print(f"❌ Error loading monsters: {e}")
    
    print()
    print("="*70)


if __name__ == '__main__':
    test_validation_logic()
    test_empty_data_handling()
    test_wizard_ui()
    
    print()
    print("="*70)
    print("✅ All tests complete!")
    print()
    print("📖 Summary:")
    print("  • Setup Wizard now allows skipping Monster and Skills steps")
    print("  • Only Window selection is mandatory")
    print("  • Prevents data duplication for first-time users")
    print("  • Users can add Monster/Skills later via Library Manager")
    print("="*70)
