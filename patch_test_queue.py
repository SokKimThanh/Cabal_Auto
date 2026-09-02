import re

with open("tests/unit/test_monster_rotation_queue.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("patch('app_gui.get_monster_by_id_api'", "patch('database.get_monster_by_id_api'")
content = content.replace("patch('app_gui.find_monster_by_name_api'", "patch('database.find_monster_by_name_api'")

with open("tests/unit/test_monster_rotation_queue.py", "w", encoding="utf-8") as f:
    f.write(content)
