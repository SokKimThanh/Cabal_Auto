"""
Data Synchronization Manager
============================
Manages data consistency across multiple JSON files.

Files managed:
- monsters.json: Monster definitions
- hunt_config.json: Hunt configuration with monster_list and training_monster_list

Author: SokKimThanh
Date: 2025-10-25
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import threading


class DataSyncManager:
    """Singleton manager for data synchronization across JSON files."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern - only one instance exists."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize sync manager with file paths."""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.data_dir = Path(__file__).parent
        self.monsters_file = self.data_dir / 'monsters.json'
        self.hunt_config_file = self.data_dir / 'hunt_config.json'
        
        print(f"[DataSyncManager] Initialized")
        print(f"  Monsters: {self.monsters_file}")
        print(f"  Hunt config: {self.hunt_config_file}")
    
    # ============================================
    # Load Operations
    # ============================================
    
    def get_monster_by_id(self, monster_id: str) -> Optional[Dict[str, Any]]:
        """
        Get monster data by ID.
        
        Args:
            monster_id: Monster ID to find
            
        Returns:
            Monster dictionary or None if not found
        """
        monsters = self.load_monsters()
        for monster in monsters:
            if monster.get('id') == monster_id:
                return monster
        return None
    
    def get_monsters_by_ids(self, monster_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get multiple monsters by IDs.
        
        Args:
            monster_ids: List of monster IDs
            
        Returns:
            List of monster dictionaries (only found monsters)
        """
        monsters = self.load_monsters()
        monster_map = {m.get('id'): m for m in monsters if m.get('id')}
        return [monster_map[mid] for mid in monster_ids if mid in monster_map]
    
    def load_monsters(self) -> List[Dict[str, Any]]:
        """Load monsters from monsters.json."""
        try:
            if not self.monsters_file.exists():
                return []
            
            with open(self.monsters_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"[DataSyncManager] Loaded {len(data)} monsters")
                return data
        except Exception as e:
            print(f"[DataSyncManager] Error loading monsters: {e}")
            return []
    
    def load_hunt_config(self) -> Dict[str, Any]:
        """Load hunt configuration."""
        try:
            from lib.features.hunt.config_migrator import migrate_hunt_config
            if not self.hunt_config_file.exists():
                return migrate_hunt_config({})
            
            with open(self.hunt_config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data = migrate_hunt_config(data)
                print(f"[DataSyncManager] Loaded hunt config")
                return data
        except Exception as e:
            print(f"[DataSyncManager] Error loading hunt config: {e}")
            from lib.features.hunt.config_migrator import migrate_hunt_config
            return migrate_hunt_config({})
    
    # ============================================
    # Save Operations
    # ============================================
    
    def save_monsters(self, monsters: List[Dict[str, Any]]) -> bool:
        """
        Save monsters to monsters.json.
        
        Args:
            monsters: List of monster dictionaries
            
        Returns:
            True if save successful
        """
        try:
            target_path = getattr(self, 'monsters_path', None) or self.monsters_file
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(monsters, f, indent=2, ensure_ascii=False)
            
            print(f"[DataSyncManager] Saved {len(monsters)} monsters")
            return True
        except Exception as e:
            print(f"[DataSyncManager] Error saving monsters: {e}")
            return False
    
    def save_hunt_config(self, config: Dict[str, Any]) -> bool:
        """
        Save hunt configuration.
        
        Args:
            config: Hunt configuration dictionary
            
        Returns:
            True if save successful
        """
        try:
            self.hunt_config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.hunt_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"[DataSyncManager] Saved hunt config")
            return True
        except Exception as e:
            print(f"[DataSyncManager] Error saving hunt config: {e}")
            return False
    
    # ============================================
    # Synchronization Operations
    # ============================================
    
    def add_monster_to_hunt(self, monster_id: str, is_training: bool = False) -> bool:
        """
        Add monster ID to hunt config list.
        
        Args:
            monster_id: ID of monster to add
            is_training: If True, add to training_monster_list, else monster_list
            
        Returns:
            True if add successful
        """
        try:
            # Load hunt config
            config = self.load_hunt_config()
            if not config:
                config = {}
            
            list_key = 'training_monster_list' if is_training else 'monster_list'
            
            # Ensure list exists
            if list_key not in config:
                config[list_key] = []
            
            # Add ID if not already present
            if monster_id not in config[list_key]:
                config[list_key].append(monster_id)
                print(f"[DataSyncManager] Added ID {monster_id} to {list_key}")
                return self.save_hunt_config(config)
            else:
                print(f"[DataSyncManager] ID {monster_id} already in {list_key}")
                return True
                
        except Exception as e:
            print(f"[DataSyncManager] Error adding monster to hunt: {e}")
            return False
    
    def delete_monster(self, monster_id: str) -> bool:
        """
        Delete monster and sync across all files.
        Alias for sync_monster_delete for cleaner API.
        
        Args:
            monster_id: ID of monster to delete
            
        Returns:
            True if sync successful
        """
        return self.sync_monster_delete(monster_id)
    
    def sync_monster_delete(self, monster_id: str) -> bool:
        """
        Synchronize monster deletion across all files.
        
        When a monster is deleted from monsters.json, also remove its ID from:
        - hunt_config.json: monster_list (array of IDs)
        - hunt_config.json: training_monster_list (array of IDs)
        
        Args:
            monster_id: ID of monster to delete
            
        Returns:
            True if sync successful
        """
        try:
            print(f"[DataSyncManager] Syncing delete for monster ID: {monster_id}")
            
            # Load hunt config
            config = self.load_hunt_config()
            if not config:
                print("[DataSyncManager] No hunt config to sync")
                return True
            
            # Track if any changes made
            changes_made = False
            
            # Remove ID from monster_list (now just array of IDs)
            if 'monster_list' in config:
                original_count = len(config['monster_list'])
                config['monster_list'] = [
                    mid for mid in config['monster_list']
                    if mid != monster_id
                ]
                removed = original_count - len(config['monster_list'])
                if removed > 0:
                    print(f"[DataSyncManager] Removed {removed} ID from monster_list")
                    changes_made = True
            
            # Remove ID from training_monster_list (now just array of IDs)
            if 'training_monster_list' in config:
                original_count = len(config['training_monster_list'])
                config['training_monster_list'] = [
                    mid for mid in config['training_monster_list']
                    if mid != monster_id
                ]
                removed = original_count - len(config['training_monster_list'])
                if removed > 0:
                    print(f"[DataSyncManager] Removed {removed} ID from training_monster_list")
                    changes_made = True
            
            # Save if changes made
            if changes_made:
                return self.save_hunt_config(config)
            
            print("[DataSyncManager] No changes needed in hunt config")
            return True
            
        except Exception as e:
            print(f"[DataSyncManager] Error syncing monster delete: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def sync_monster_update(self, monster: Dict[str, Any]) -> bool:
        """
        Synchronize monster update across all files.
        
        Since hunt_config now only stores IDs, this method just validates
        that the monster ID exists in the lists. No actual update needed.
        
        Args:
            monster: Updated monster dictionary with 'id' field
            
        Returns:
            True if sync successful
        """
        try:
            monster_id = monster.get('id')
            if not monster_id:
                print("[DataSyncManager] Monster has no ID, cannot sync")
                return False
            
            print(f"[DataSyncManager] Syncing update for monster: {monster.get('name', 'Unknown')}")
            print("[DataSyncManager] Hunt config stores IDs only, no update needed")
            
            # No changes needed since we only store IDs
            return True
            
        except Exception as e:
            print(f"[DataSyncManager] Error syncing monster update: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def sync_all_monsters(self, monsters: List[Dict[str, Any]]) -> bool:
        """
        Full synchronization - rebuild hunt config monster lists from monsters.json.
        
        Hunt config now stores only IDs. This method:
        - Keeps existing IDs that still exist in monsters.json
        - Removes IDs that no longer exist in monsters.json
        
        Args:
            monsters: Complete list of monsters from monsters.json
            
        Returns:
            True if sync successful
        """
        try:
            print(f"[DataSyncManager] Full sync of {len(monsters)} monsters")
            
            # Load hunt config
            config = self.load_hunt_config()
            if not config:
                print("[DataSyncManager] No hunt config to sync")
                return True
            
            # Build set of valid monster IDs
            valid_ids = {m.get('id') for m in monsters if m.get('id')}
            
            # Filter monster_list to keep only valid IDs
            if 'monster_list' in config:
                original_list = config['monster_list']
                config['monster_list'] = [mid for mid in original_list if mid in valid_ids]
                print(f"[DataSyncManager] Monster list: {len(original_list)} -> {len(config['monster_list'])} IDs")
            
            # Filter training_monster_list to keep only valid IDs
            if 'training_monster_list' in config:
                original_list = config['training_monster_list']
                config['training_monster_list'] = [mid for mid in original_list if mid in valid_ids]
                print(f"[DataSyncManager] Training list: {len(original_list)} -> {len(config['training_monster_list'])} IDs")
            
            # Save updated config
            return self.save_hunt_config(config)
            
        except Exception as e:
            print(f"[DataSyncManager] Error in full sync: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # ============================================
    # Validation Operations
    # ============================================
    
    def validate_data_consistency(self) -> Dict[str, Any]:
        """
        Validate data consistency across files.
        
        Returns:
            Dictionary with validation results:
            {
                'valid': bool,
                'monsters_count': int,
                'hunt_ids_count': int,
                'training_ids_count': int,
                'orphaned_in_hunt': List[str],  # IDs in hunt but not in monsters.json
                'orphaned_in_training': List[str]  # IDs in training but not in monsters.json
            }
        """
        try:
            print("[DataSyncManager] Validating data consistency...")
            
            # Load all data
            monsters = self.load_monsters()
            config = self.load_hunt_config()
            
            # Build monster ID set
            monster_ids = {m.get('id') for m in monsters if m.get('id')}
            
            # Check hunt monster_list (now array of IDs)
            hunt_ids = config.get('monster_list', [])
            orphaned_hunt = [mid for mid in hunt_ids if mid not in monster_ids]
            
            # Check training_monster_list (now array of IDs)
            training_ids = config.get('training_monster_list', [])
            orphaned_training = [mid for mid in training_ids if mid not in monster_ids]
            
            # Build result
            result = {
                'valid': len(orphaned_hunt) == 0 and len(orphaned_training) == 0,
                'monsters_count': len(monsters),
                'hunt_ids_count': len(hunt_ids),
                'training_ids_count': len(training_ids),
                'orphaned_in_hunt': orphaned_hunt,
                'orphaned_in_training': orphaned_training
            }
            
            print(f"[DataSyncManager] Validation result: {result}")
            return result
            
        except Exception as e:
            print(f"[DataSyncManager] Error validating consistency: {e}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    def fix_orphaned_references(self) -> bool:
        """
        Fix orphaned monster references in hunt config.
        
        Removes any IDs from hunt_config.json that don't exist in monsters.json.
        
        Returns:
            True if fix successful
        """
        try:
            print("[DataSyncManager] Fixing orphaned references...")
            
            # Validate first
            validation = self.validate_data_consistency()
            if validation.get('valid'):
                print("[DataSyncManager] No orphaned references found")
                return True
            
            # Load data
            monsters = self.load_monsters()
            config = self.load_hunt_config()
            
            # Build valid ID set
            valid_ids = {m.get('id') for m in monsters if m.get('id')}
            
            # Filter monster_list
            if 'monster_list' in config:
                original_count = len(config['monster_list'])
                config['monster_list'] = [mid for mid in config['monster_list'] if mid in valid_ids]
                removed = original_count - len(config['monster_list'])
                if removed > 0:
                    print(f"[DataSyncManager] Removed {removed} orphaned IDs from monster_list")
            
            # Filter training_monster_list
            if 'training_monster_list' in config:
                original_count = len(config['training_monster_list'])
                config['training_monster_list'] = [mid for mid in config['training_monster_list'] if mid in valid_ids]
                removed = original_count - len(config['training_monster_list'])
                if removed > 0:
                    print(f"[DataSyncManager] Removed {removed} orphaned IDs from training_monster_list")
            
            # Save fixed config
            return self.save_hunt_config(config)
            
        except Exception as e:
            print(f"[DataSyncManager] Error fixing orphaned references: {e}")
            return False


# Global singleton instance
_sync_manager = DataSyncManager()


# Convenience functions
def get_sync_manager() -> DataSyncManager:
    """Get singleton DataSyncManager instance."""
    return _sync_manager


def sync_monster_delete(monster_id: str) -> bool:
    """Convenience function for syncing monster deletion."""
    return get_sync_manager().sync_monster_delete(monster_id)


def sync_monster_update(monster: Dict[str, Any]) -> bool:
    """Convenience function for syncing monster update."""
    return get_sync_manager().sync_monster_update(monster)


def sync_all_monsters(monsters: List[Dict[str, Any]]) -> bool:
    """Convenience function for full synchronization."""
    return get_sync_manager().sync_all_monsters(monsters)


def validate_consistency() -> Dict[str, Any]:
    """Convenience function for validating data consistency."""
    return get_sync_manager().validate_data_consistency()


def fix_orphaned() -> bool:
    """Convenience function for fixing orphaned references."""
    return get_sync_manager().fix_orphaned_references()
