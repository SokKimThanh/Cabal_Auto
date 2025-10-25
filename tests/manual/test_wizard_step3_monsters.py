"""
Quick test for Setup Wizard Step 3 Monster Loading

This test verifies that monsters are loaded correctly in Step 3.

Run:
    python tests/manual/test_wizard_step3_monsters.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def test_monster_path():
    """Test monster path calculation."""
    print("="*70)
    print("🧪 Testing Setup Wizard Monster Path Fix")
    print("="*70)
    print()
    
    # Test path calculation (same as in setup_wizard.py)
    setup_wizard_path = Path("ui/windows/setup_wizard.py")
    project_root = setup_wizard_path.parent.parent.parent
    monsters_path = project_root / "lib" / "data" / "monsters.json"
    
    print(f"📂 Setup Wizard location: {setup_wizard_path}")
    print(f"📂 Project root: {project_root}")
    print(f"📂 Monsters path: {monsters_path}")
    print()
    
    if monsters_path.exists():
        print(f"✅ File exists: {monsters_path}")
        
        # Try to load it
        import json
        try:
            with open(monsters_path, "r", encoding="utf-8") as f:
                monsters = json.load(f)
            
            print(f"✅ Loaded {len(monsters)} monsters")
            
            if monsters:
                print()
                print("📋 Sample monsters:")
                for i, monster in enumerate(monsters[:3]):
                    name = monster.get("name", "Unnamed")
                    hp = monster.get("hp", 0)
                    templates = len(monster.get("templates", []))
                    print(f"  {i+1}. {name} (HP: {hp:,.0f}, {templates} templates)")
        except Exception as e:
            print(f"❌ Error loading monsters: {e}")
    else:
        print(f"❌ File NOT found: {monsters_path}")
    
    print()
    print("="*70)


def test_wizard_with_step3():
    """Test actual wizard with Step 3."""
    print()
    print("🧪 Testing Wizard Step 3 Integration")
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
        
        # Check if monsters_data is loaded
        if hasattr(wizard, 'monsters_data'):
            print(f"✅ monsters_data attribute exists")
            print(f"   Initial value: {type(wizard.monsters_data)} (length: {len(wizard.monsters_data)})")
        else:
            print(f"❌ monsters_data attribute NOT found")
        
        print()
        print("📌 To fully test:")
        print("   1. Run the app: python app_gui.py")
        print("   2. Let wizard auto-open (first run)")
        print("   3. Navigate to Step 3")
        print("   4. Check if monsters appear in list")
        print()
        
        # Close wizard
        wizard.dialog.destroy()
        root.destroy()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("="*70)


if __name__ == '__main__':
    test_monster_path()
    test_wizard_with_step3()
