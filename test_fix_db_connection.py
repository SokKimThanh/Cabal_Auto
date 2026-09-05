#!/usr/bin/env python3
"""Test script to verify database connection fix"""

import sys
sys.path.insert(0, '.')

# Initialize database schema first
from lib.db import schema
import database

db_inst = database.get_db()
if db_inst and db_inst.conn:
    schema.setup_skills_schema(db_inst.conn)

from lib.features.skills.skill_preset_service import SkillPresetService

def test_preset_dialog_flow():
    """Simulate the flow that triggered the error"""
    print("Testing preset dialog flow...")
    
    service = SkillPresetService()
    
    # This was causing: sqlite3.ProgrammingError: Cannot operate on a closed database
    print("1. Calling list_presets_by_class()...")
    presets = service.list_presets_by_class("Barbarian")
    print(f"   ✓ Got {len(presets)} presets for Barbarian")
    
    print("2. Calling list_presets_by_class() again...")
    presets2 = service.list_presets_by_class("Sorceress")
    print(f"   ✓ Got {len(presets2)} presets for Sorceress")
    
    # Test getting preset skills
    if presets:
        preset_id = presets[0]['preset_id']
        print(f"3. Calling get_preset_skills({preset_id})...")
        skills = service.preset_repo.get_preset_skills(preset_id)
        print(f"   ✓ Got skills: {skills}")
    else:
        print("   (No presets yet, skipping skills test)")
    
    print("\n✅ All tests passed! Database connection issue is fixed.")

if __name__ == "__main__":
    try:
        test_preset_dialog_flow()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
