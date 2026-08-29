import re

with open("lib/i18n/monster_editor_translations.py", "r", encoding="utf-8") as f:
    content = f.read()

# I will add the new VI keys below 'monster_desc_label': 'Mô tả:',
vi_keys = """        'monster_desc_label': 'Mô tả:',
        'monster_id_label': 'ID:',
        'monster_primary_atk_min_label': 'Công chính (Min):',
        'monster_primary_atk_max_label': 'Công chính (Max):',
        'monster_sec_atk_min_label': 'Công phụ (Min):',
        'monster_sec_atk_max_label': 'Công phụ (Max):',
        'monster_atk_rate_label': 'Tốc đánh:',
        'monster_def_label': 'Thủ:',
        'monster_def_rate_label': 'Tỷ lệ thủ:',
        'monster_acc_label': 'Chính xác:',
        'monster_boss_type_label': 'Loại Boss:',
        'monster_dungeon_label': 'Dungeon:',"""

content = content.replace("'monster_desc_label': 'Mô tả:',", vi_keys)

# Add EN keys below 'monster_desc_label': 'Description:',
en_keys = """        'monster_desc_label': 'Description:',
        'monster_id_label': 'ID:',
        'monster_primary_atk_min_label': 'Primary Atk (Min):',
        'monster_primary_atk_max_label': 'Primary Atk (Max):',
        'monster_sec_atk_min_label': 'Secondary Atk (Min):',
        'monster_sec_atk_max_label': 'Secondary Atk (Max):',
        'monster_atk_rate_label': 'Atk Rate:',
        'monster_def_label': 'Defense:',
        'monster_def_rate_label': 'Def Rate:',
        'monster_acc_label': 'Accuracy:',
        'monster_boss_type_label': 'Boss Type:',
        'monster_dungeon_label': 'Dungeon:',"""

content = content.replace("'monster_desc_label': 'Description:',", en_keys)

with open("lib/i18n/monster_editor_translations.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated translations")
