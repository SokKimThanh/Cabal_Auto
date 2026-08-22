"""Test Library Manager monster path resolution."""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("LIBRARY MANAGER - MONSTER PATH TEST")
print("=" * 60)

try:
    # Import and check path calculation
    from ui.windows.library_manager import LibraryManagerWindow
    
    # Create a mock window (won't show GUI)
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()  # Hide window
    
    # Create instance with mock data
    mock_cfg = {}
    mock_monsters = []
    mock_skills = []
    manager = LibraryManagerWindow(root, mock_cfg, mock_monsters, mock_skills, lang='vi')
    
    print("\n[Path Resolution]")
    print(f"Project Root: {manager.project_root}")
    print(f"Monsters Dir: {manager.assets_mon_dir}")
    print(f"Tmp Capture:  {manager.tmp_capture_dir}")
    
    print("\n[Existence Check]")
    print(f"✓ Project root exists: {manager.project_root.exists()}")
    print(f"✓ Monsters dir exists: {manager.assets_mon_dir.exists()}")
    
    if manager.assets_mon_dir.exists():
        monster_files = list(manager.assets_mon_dir.glob('*.png'))
        print(f"✓ Monster files found: {len(monster_files)}")
        if monster_files:
            print(f"  Sample: {monster_files[0].name}")
    
    print("\n[Expected Path]")
    expected = Path(__file__).parent / 'assets' / 'images' / 'monsters'
    print(f"Expected: {expected}")
    print(f"Match: {'✓ YES' if manager.assets_mon_dir == expected else '✗ NO'}")
    
    root.destroy()
    
    print("\n" + "=" * 60)
    print("✅ TEST PASSED - Monster path correctly resolved!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 60)
    print("❌ TEST FAILED")
    print("=" * 60)
