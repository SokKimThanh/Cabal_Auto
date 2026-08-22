# -*- coding: utf-8 -*-
"""
Database API Helper Module.
Provides high-level standalone functions that delegate to the MonsterDatabase instance.
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from database import MonsterDatabase

_db_instance: Optional["MonsterDatabase"] = None


def set_api_db_instance(db_inst: Optional["MonsterDatabase"]) -> None:
    global _db_instance
    _db_instance = db_inst


def get_api_db_instance() -> Optional["MonsterDatabase"]:
    return _db_instance
