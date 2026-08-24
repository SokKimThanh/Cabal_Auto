"""
Monster Manager - Core CRUD engine for monster data management.

This module provides the core functionality for creating, reading, updating,
and deleting monster data. It is independent from the Library Manager and
handles all monster-related operations including template management.

Thread-safe operations with event emission for UI updates.

Author: SokKimThanh
Created: 2025-10-24
Status: Skeleton
"""
from __future__ import annotations
from typing import Dict, List, Any, Optional, Callable
import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class MonsterManager:
    """
    Core CRUD engine for monster data management.
    
    Features:
    - Thread-safe CRUD operations
    - JSON file I/O with validation
    - Template management (add/remove/test)
    - Event emission for UI updates
    - Error handling with logging
    
    Events Emitted:
    - monster_created(monster_id, data)
    - monster_updated(monster_id, changes)
    - monster_deleted(monster_id)
    - template_added(monster_id, template_id)
    - template_tested(monster_id, template_id, result)
    """
    
    def __init__(self, data_path: str = "lib/data/monsters.json"):
        """
        Initialize MonsterManager.
        
        Args:
            data_path: Path to monsters JSON file
        """
        self.data_path = data_path
        self.monsters: Dict[str, Dict[str, Any]] = {}
        self.callbacks: Dict[str, List[Callable]] = {}
        self._load_data()
    
    def _load_data(self) -> None:
        """Load monster data from JSON file."""
        try:
            if os.path.exists(self.data_path):
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    self.monsters = json.load(f)
                logger.info(f"Successfully loaded {len(self.monsters)} monsters from {self.data_path}")
            else:
                logger.info(f"Monster data file not found at {self.data_path}. Starting with empty database.")
                self.monsters = {}
        except json.JSONDecodeError as e:
            logger.error(f"Malformed JSON in monster data file {self.data_path}: {e}")
            self.monsters = {}
        except Exception as e:
            logger.error(f"Error loading monster data from {self.data_path}: {e}")
            self.monsters = {}
    
    def _save_data(self) -> bool:
        """
        Save monster data to JSON file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        # TODO: Implement JSON saving with atomic write
        pass
    
    def _emit_event(self, event_name: str, *args, **kwargs) -> None:
        """
        Emit event to registered callbacks.
        
        Args:
            event_name: Name of the event
            *args: Positional arguments for callback
            **kwargs: Keyword arguments for callback
        """
        # TODO: Implement event emission
        pass
    
    def register_callback(self, event_name: str, callback: Callable) -> None:
        """
        Register callback for event.
        
        Args:
            event_name: Name of the event to listen to
            callback: Function to call when event occurs
        """
        if event_name not in self.callbacks:
            self.callbacks[event_name] = []
        self.callbacks[event_name].append(callback)
    
    def list_monsters(self, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List all monsters with optional filtering.
        
        Args:
            filter_dict: Optional filter criteria (e.g., {'level_min': 50})
        
        Returns:
            List of monster dictionaries
        """
        # TODO: Implement monster listing with filters
        pass
    
    def get_monster(self, monster_id: str) -> Optional[Dict[str, Any]]:
        """
        Get monster by ID.
        
        Args:
            monster_id: Unique monster identifier
        
        Returns:
            Monster dictionary or None if not found
        """
        return self.monsters.get(monster_id)
    
    def create_monster(self, monster_data: Dict[str, Any]) -> str:
        """
        Create new monster.
        
        Args:
            monster_data: Monster properties (name, level, templates, etc.)
        
        Returns:
            str: Generated monster_id
        
        Raises:
            ValueError: If monster_data is invalid
        
        Events:
            Emits monster_created(monster_id, data)
        """
        if not self._validate_monster_data(monster_data):
            raise ValueError("Invalid monster data")

        monster_id = str(uuid.uuid4())

        # Store a copy of the data
        self.monsters[monster_id] = monster_data.copy()

        self._save_data()
        self._emit_event("monster_created", monster_id, self.monsters[monster_id])

        return monster_id
    
    def update_monster(self, monster_id: str, data: Dict[str, Any]) -> bool:
        """
        Update existing monster.
        
        Args:
            monster_id: Monster to update
            data: Fields to update
        
        Returns:
            bool: True if successful, False if monster not found
        
        Events:
            Emits monster_updated(monster_id, changes)
        """
        # TODO: Implement monster update
        pass
    
    def delete_monster(self, monster_id: str) -> bool:
        """
        Delete monster by ID.
        
        Args:
            monster_id: Monster to delete
        
        Returns:
            bool: True if successful, False if not found
        
        Events:
            Emits monster_deleted(monster_id)
        """
        # TODO: Implement monster deletion
        pass
    
    def add_template(
        self,
        monster_id: str,
        template_path: str,
        threshold: float = 0.7
    ) -> bool:
        """
        Add template to monster.
        
        Args:
            monster_id: Monster to add template to
            template_path: Path to template image file
            threshold: Recognition threshold (0.0 - 1.0)
        
        Returns:
            bool: True if successful, False otherwise
        
        Raises:
            ValueError: If threshold is invalid or file doesn't exist
        
        Events:
            Emits template_added(monster_id, template_id)
        """
        # TODO: Implement template addition
        # Validate file exists
        # Validate threshold range
        # Generate template_id
        # Add to monster's templates list
        # Emit event
        pass
    
    def remove_template(self, monster_id: str, template_id: str) -> bool:
        """
        Remove template from monster.
        
        Args:
            monster_id: Monster ID
            template_id: Template ID to remove
        
        Returns:
            bool: True if successful, False otherwise
        """
        # TODO: Implement template removal
        pass
    
    def test_template(
        self,
        monster_id: str,
        template_id: str
    ) -> Dict[str, Any]:
        """
        Test template recognition against current screen.
        
        Args:
            monster_id: Monster ID
            template_id: Template ID to test
        
        Returns:
            Dict with keys:
            - success (bool): True if found
            - confidence (float): Match confidence
            - location (tuple): (x, y) coordinates
            - matches (int): Number of matches found
        
        Events:
            Emits template_tested(monster_id, template_id, result)
        """
        # TODO: Implement template testing
        # Use vision_engine to match template
        # Return results
        # Emit event
        pass
    
    def _validate_monster_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate monster data structure.
        
        Args:
            data: Monster data to validate
        
        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(data, dict):
            return False
        if "name" not in data or not isinstance(data["name"], str):
            return False
        if not data["name"].strip():
            return False
        return True


# Singleton instance
_monster_manager_instance: Optional[MonsterManager] = None


def get_monster_manager() -> MonsterManager:
    """
    Get singleton MonsterManager instance.
    
    Returns:
        MonsterManager: Singleton instance
    """
    global _monster_manager_instance
    if _monster_manager_instance is None:
        _monster_manager_instance = MonsterManager()
    return _monster_manager_instance
