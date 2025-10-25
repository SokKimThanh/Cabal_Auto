"""Hotkey Handler Package.

Contains hotkey handlers for various application features.

Sprint 24 - Code Reorganization
"""

from .monster_editor_handler import MonsterEditorHandler, create_monster_editor_handler

__all__ = [
    'MonsterEditorHandler',
    'create_monster_editor_handler',
]
