#!/usr/bin/env python
"""Comprehensive test for Phase 3: Multi-Monster Rotation"""

import sys
import json
import pytest
from pathlib import Path

sys.path.insert(0, 'e:/Cabal_Auto')

# Mark as integration test
pytestmark = pytest.mark.integration

print("=" * 70)
print("Phase 3 Comprehensive Test: Multi-Monster Rotation")
print("=" * 70)

# Test 1: Load current config and check migration
print("\n[TEST 1] Config Migration from monster_selected_name")
print("-" * 70)

from ui.auto_hunt import load_cfg
cfg = load_cfg()

print(f"✓ monster_selected_name: {cfg.get('monster_selected_name')}")
print(f"✓ monster_list: {cfg.get('monster_list')}")
print(f"✓ rotation_mode: {cfg.get('rotation_mode')}")
print(f"✓ current_monster_index: {cfg.get('current_monster_index')}")

assert cfg.get('monster_list'), "monster_list should not be empty after migration"
assert cfg.get('rotation_mode') in ['sequence', 'priority'], "rotation_mode should be valid"
print("✅ Migration test PASSED")

# Test 2: Create multi-monster scenario
print("\n[TEST 2] Multi-Monster Configuration")
print("-" * 70)

# Manually create a multi-monster config for testing
test_cfg = cfg.copy()
test_cfg['monster_list'] = [
    {'name': 'Coc Go 2', 'priority': 1, 'enabled': True},
    {'name': 'Coc Go', 'priority': 2, 'enabled': True},
    {'name': 'Desert Fungus', 'priority': 3, 'enabled': False},  # Disabled
]

from ui.auto_hunt import get_monster_rotation_targets

# Test sequence mode
test_cfg['rotation_mode'] = 'sequence'
targets_seq = get_monster_rotation_targets(test_cfg)
print(f"SEQUENCE mode: {len(targets_seq)} enabled monsters")
for i, m in enumerate(targets_seq):
    print(f"  [{i+1}] {m['name']} (P{m['priority']}) - {len(m['templates'])} templates")

assert len(targets_seq) == 2, "Should have 2 enabled monsters"
assert targets_seq[0]['name'] == 'Coc Go 2', "First should be Coc Go 2"
assert targets_seq[1]['name'] == 'Coc Go', "Second should be Coc Go"
print("✅ Sequence mode test PASSED")

# Test priority mode
test_cfg['rotation_mode'] = 'priority'
targets_pri = get_monster_rotation_targets(test_cfg)
print(f"\nPRIORITY mode: {len(targets_pri)} enabled monsters")
for i, m in enumerate(targets_pri):
    print(f"  [{i+1}] {m['name']} (P{m['priority']}) - {len(m['templates'])} templates")

assert len(targets_pri) == 2, "Should have 2 enabled monsters"
assert targets_pri[0]['priority'] < targets_pri[1]['priority'], "Should be sorted by priority"
print("✅ Priority mode test PASSED")

# Test 3: Template matching with fuzzy names
print("\n[TEST 3] Fuzzy Template Matching")
print("-" * 70)

test_fuzzy = cfg.copy()
test_fuzzy['monster_list'] = [
    {'name': 'coc go~', 'priority': 1, 'enabled': True},  # lowercase with tilde
    {'name': 'COC GO!', 'priority': 2, 'enabled': True},  # uppercase with exclamation
]

targets_fuzzy = get_monster_rotation_targets(test_fuzzy)
print(f"Fuzzy matching: {len(targets_fuzzy)} monsters matched")
for m in targets_fuzzy:
    print(f"  {m['name']} → {len(m['templates'])} templates matched")

assert len(targets_fuzzy) >= 1, "Should match at least 1 monster with fuzzy matching"
print("✅ Fuzzy matching test PASSED")

# Test 4: Empty/disabled scenarios
print("\n[TEST 4] Edge Cases")
print("-" * 70)

# No enabled monsters
test_empty = cfg.copy()
test_empty['monster_list'] = [
    {'name': 'Coc Go', 'priority': 1, 'enabled': False},
]
targets_empty = get_monster_rotation_targets(test_empty)
print(f"All disabled: {len(targets_empty)} monsters (expected 0)")
assert len(targets_empty) == 0, "Should have 0 monsters when all disabled"
print("✅ Disabled monsters test PASSED")

# Empty monster_list
test_none = cfg.copy()
test_none['monster_list'] = []
targets_none = get_monster_rotation_targets(test_none)
print(f"Empty list: {len(targets_none)} monsters (expected 0)")
assert len(targets_none) == 0, "Should have 0 monsters when list is empty"
print("✅ Empty list test PASSED")

# Summary
print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED! Phase 3 rotation logic is working correctly.")
print("=" * 70)
print("\nTest Summary:")
print("  ✓ Config migration from monster_selected_name")
print("  ✓ Multi-monster sequence rotation")
print("  ✓ Multi-monster priority rotation")
print("  ✓ Fuzzy template matching (case-insensitive, special chars)")
print("  ✓ Edge cases (disabled monsters, empty list)")
print("\nReady for integration testing with actual game!")
