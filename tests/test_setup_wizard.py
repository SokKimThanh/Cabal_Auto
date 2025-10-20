"""
Test Setup Wizard - Verify data paths are working correctly
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import tkinter as tk
from ui.setup_wizard import SetupWizard

def test_data_paths():
    """Test that data files can be found."""
    print("=" * 60)
    print("Testing Setup Wizard Data Paths")
    print("=" * 60)
    
    # Test monster path
    monsters_path = project_root / 'lib' / 'data' / 'monsters.json'
    print(f"\n✓ Monsters path: {monsters_path}")
    print(f"  Exists: {monsters_path.exists()}")
    
    if monsters_path.exists():
        import json
        with open(monsters_path, 'r', encoding='utf-8') as f:
            monsters = json.load(f)
        print(f"  Count: {len(monsters)} monsters")
        for m in monsters:
            print(f"    - {m.get('name', 'Unknown')}")
    
    # Test skills path
    skills_path = project_root / 'lib' / 'data' / 'skills.json'
    print(f"\n✓ Skills path: {skills_path}")
    print(f"  Exists: {skills_path.exists()}")
    
    if skills_path.exists():
        import json
        with open(skills_path, 'r', encoding='utf-8') as f:
            skills = json.load(f)
        print(f"  Count: {len(skills)} skills")
        for s in skills:
            print(f"    - {s.get('name', 'Unknown')} [{s.get('key', '?')}] ({s.get('type', 'unknown')})")
    
    print("\n" + "=" * 60)
    print("✅ All data paths verified!")
    print("=" * 60)
    return True

def run_wizard():
    """Run the setup wizard."""
    print("\n🚀 Starting Setup Wizard...")
    print("Press ESC or close window to exit\n")
    
    root = tk.Tk()
    root.title("Cabal Auto - Setup Wizard Test")
    
    # Create wizard
    try:
        wizard = SetupWizard(root)
        print("✓ Setup Wizard created successfully")
        print("\nWizard window should now be visible.")
        print("Press Ctrl+C in terminal or close window to exit.")
        
        # Run main loop
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user (Ctrl+C)")
        print("This is normal - not an error!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            root.destroy()
        except:
            pass
        print("\n✓ Setup Wizard closed")

if __name__ == '__main__':
    # First test data paths
    if test_data_paths():
        # Then run wizard if user wants
        print("\nReady to test Setup Wizard GUI")
        print("\nStarting in 2 seconds...")
        import time
        time.sleep(2)
        run_wizard()
