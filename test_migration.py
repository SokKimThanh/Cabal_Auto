"""Test migration of Coc go from monster_list to training_monster_list."""

# Test string detection
test_names = ["Coc go~", "Cọc gỗ", "Boss A", "coc_go_2", "COCGO", "Dragon"]

print("=== Testing Coc Go Detection ===")
for name in test_names:
    name_lower = name.lower()
    is_coc_go = 'coc' in name_lower and 'go' in name_lower
    print(f"{name:15} -> {'✅ COC GO' if is_coc_go else '❌ Normal'}")

