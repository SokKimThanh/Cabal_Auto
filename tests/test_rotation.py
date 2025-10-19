#!/usr/bin/env python
"""Test script for Phase 3: Multi-Monster Rotation Logic"""

import sys
sys.path.insert(0, 'e:/Cabal_Auto')

from ui.auto_hunt import load_cfg, get_monster_rotation_targets

print("=" * 60)
print("Phase 3 Test: Monster Rotation Logic")
print("=" * 60)

# Load config
cfg = load_cfg()
print(f"\n1. Config loaded:")
print(f"   rotation_mode: {cfg.get('rotation_mode')}")
print(f"   current_monster_index: {cfg.get('current_monster_index')}")
print(f"   monster_list: {cfg.get('monster_list')}")

# Test get_monster_rotation_targets()
targets = get_monster_rotation_targets(cfg)
print(f"\n2. Monster rotation targets: {len(targets)} monsters")

if targets:
    for i, monster in enumerate(targets):
        name = monster['name']
        priority = monster['priority']
        template_count = len(monster['templates'])
        print(f"   [{i+1}] {name} (Priority: {priority}) - {template_count} templates")
        
        # Show first 2 templates
        for j, tmpl in enumerate(monster['templates'][:2]):
            tmpl_name = tmpl.get('name', 'unnamed')
            print(f"       └─ Template {j+1}: {tmpl_name}")
else:
    print("   No enabled monsters found")
    print("   INFO: This is expected if monster_list is empty or all disabled")

# Test both rotation modes
print(f"\n3. Testing rotation modes:")
for mode in ['sequence', 'priority']:
    cfg['rotation_mode'] = mode
    targets = get_monster_rotation_targets(cfg)
    print(f"   {mode.upper()} mode: {len(targets)} monsters")
    if targets:
        print(f"      First monster: {targets[0]['name']} (P{targets[0]['priority']})")

print("\n✅ Test completed successfully!")
