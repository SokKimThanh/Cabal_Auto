"""
Test DataSyncManager functionality
===================================
Test script to verify monster sync operations.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.data.sync_manager import DataSyncManager

def test_sync_manager():
    """Test sync manager operations."""
    print("=" * 60)
    print("Testing DataSyncManager")
    print("=" * 60)
    
    sync = DataSyncManager()
    
    # Test 1: Load monsters
    print("\n[Test 1] Loading monsters...")
    monsters = sync.load_monsters()
    print(f"  Loaded {len(monsters)} monsters")
    for m in monsters:
        print(f"    - {m.get('name')} (ID: {m.get('id')})")
    
    # Test 2: Load hunt config
    print("\n[Test 2] Loading hunt config...")
    config = sync.load_hunt_config()
    print(f"  monster_list: {config.get('monster_list', [])}")
    print(f"  training_monster_list: {config.get('training_monster_list', [])}")
    
    # Test 3: Validate consistency
    print("\n[Test 3] Validating consistency...")
    result = sync.validate_data_consistency()
    print(f"  Valid: {result.get('valid')}")
    print(f"  Monsters: {result.get('monsters_count')}")
    print(f"  Hunt IDs: {result.get('hunt_ids_count')}")
    print(f"  Training IDs: {result.get('training_ids_count')}")
    print(f"  Orphaned in hunt: {result.get('orphaned_in_hunt')}")
    print(f"  Orphaned in training: {result.get('orphaned_in_training')}")
    
    # Test 4: Get monster by ID
    if monsters:
        print("\n[Test 4] Get monster by ID...")
        test_id = monsters[0].get('id')
        if test_id:
            monster = sync.get_monster_by_id(test_id)
            if monster:
                print(f"  Found: {monster.get('name')} (ID: {monster.get('id')})")
            else:
                print(f"  Not found: {test_id}")
    
    # Test 5: Add to hunt list
    if monsters:
        print("\n[Test 5] Add monster to hunt list...")
        test_id = monsters[0].get('id')
        if test_id:
            success = sync.add_monster_to_hunt(test_id, is_training=False)
            print(f"  Add to hunt list: {'Success' if success else 'Failed'}")
            
            # Reload and check
            config = sync.load_hunt_config()
            print(f"  monster_list now: {config.get('monster_list', [])}")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == '__main__':
    test_sync_manager()
