"""
Test monster deletion with sync
================================
Test that deleting monster from monsters.json also removes from hunt_config.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.data.sync_manager import DataSyncManager

def test_delete_sync():
    """Test delete synchronization."""
    print("=" * 60)
    print("Testing Monster Delete Sync")
    print("=" * 60)
    
    sync = DataSyncManager()
    
    # Step 1: Show initial state
    print("\n[Step 1] Initial state:")
    monsters = sync.load_monsters()
    config = sync.load_hunt_config()
    print(f"  Monsters: {len(monsters)}")
    for m in monsters:
        print(f"    - {m.get('name')} (ID: {m.get('id')})")
    print(f"  monster_list: {config.get('monster_list', [])}")
    print(f"  training_monster_list: {config.get('training_monster_list', [])}")
    
    # Step 2: Validate
    print("\n[Step 2] Validating consistency...")
    result = sync.validate_data_consistency()
    print(f"  Valid: {result.get('valid')}")
    if not result.get('valid'):
        print(f"  Orphaned in hunt: {result.get('orphaned_in_hunt')}")
        print(f"  Orphaned in training: {result.get('orphaned_in_training')}")
    
    # Step 3: Delete monster (simulate by calling sync delete)
    if monsters:
        test_id = monsters[0].get('id')
        if test_id:
            print(f"\n[Step 3] Simulating delete of monster ID: {test_id}")
            success = sync.delete_monster(test_id)
            print(f"  Delete sync: {'Success' if success else 'Failed'}")
            
            # Check hunt config
            config = sync.load_hunt_config()
            print(f"  monster_list after delete: {config.get('monster_list', [])}")
            print(f"  training_monster_list after delete: {config.get('training_monster_list', [])}")
    
    # Step 4: Test with empty monsters.json
    print("\n[Step 4] Testing with empty monsters.json...")
    print("  Saving empty monster list...")
    sync.save_monsters([])
    
    # Sync all (should clear hunt config lists)
    print("  Running full sync...")
    sync.sync_all_monsters([])
    
    # Check result
    config = sync.load_hunt_config()
    print(f"  monster_list: {config.get('monster_list', [])}")
    print(f"  training_monster_list: {config.get('training_monster_list', [])}")
    print(f"  ✓ Both lists should be empty")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == '__main__':
    test_delete_sync()
