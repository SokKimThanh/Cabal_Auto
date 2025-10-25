"""
Test Monster Editor Auto-Creation
==================================
Check if opening Monster Editor automatically creates monster data.
"""

import json
import time
from pathlib import Path

def check_monsters_file():
    """Read and display monsters.json content."""
    monsters_file = Path('lib/data/monsters.json')
    
    if not monsters_file.exists():
        print("❌ monsters.json does not exist")
        return None
    
    with open(monsters_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data

def main():
    print("=" * 60)
    print("Testing Monster Editor Auto-Creation")
    print("=" * 60)
    
    # Check initial state
    print("\n[Step 1] Initial state:")
    initial_data = check_monsters_file()
    print(f"  monsters.json: {len(initial_data) if initial_data is not None else 0} monsters")
    if initial_data:
        for m in initial_data:
            print(f"    - {m.get('name')} (ID: {m.get('id')})")
    else:
        print("    Empty list")
    
    print("\n[Step 2] Instructions:")
    print("  1. Open the app (already running)")
    print("  2. Press Ctrl+Shift+M to open Monster Editor")
    print("  3. Close Monster Editor")
    print("  4. Press Enter here to continue check...")
    
    input("\nPress Enter when ready to check after opening/closing editor...")
    
    # Check final state
    print("\n[Step 3] After opening editor:")
    final_data = check_monsters_file()
    print(f"  monsters.json: {len(final_data) if final_data is not None else 0} monsters")
    if final_data:
        for m in final_data:
            print(f"    - {m.get('name')} (ID: {m.get('id')})")
    else:
        print("    Empty list")
    
    # Compare
    print("\n[Step 4] Analysis:")
    initial_count = len(initial_data) if initial_data is not None else 0
    final_count = len(final_data) if final_data is not None else 0
    
    if initial_count == final_count:
        print(f"  ✅ No auto-creation detected")
        print(f"  Count: {initial_count} → {final_count} (unchanged)")
    else:
        print(f"  ⚠️ Data changed!")
        print(f"  Count: {initial_count} → {final_count}")
        
        if final_count > initial_count:
            print(f"  Added {final_count - initial_count} monster(s)")
            if final_data:
                new_monsters = final_data[initial_count:]
                for m in new_monsters:
                    print(f"    + {m.get('name')} (ID: {m.get('id')})")
        else:
            print(f"  Removed {initial_count - final_count} monster(s)")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == '__main__':
    main()
