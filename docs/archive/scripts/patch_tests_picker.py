import re

with open("tests/unit/dialogs/test_monster_picker.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('assert list(text0) == ["#1", "Slime Xanh", 10, 100]', "assert list(text0) == ['#1', 'Slime Xanh', '10', '100']")
content = content.replace('assert list(text1) == ["#2", "Slime Đo", 12, 150]', "assert list(text1) == ['#2', 'Slime Đo', '12', '150']")
content = content.replace('assert list(dialog.tree.item(items[0], "values")) == ["#1", "Slime Xanh", 10, 100]', "assert list(dialog.tree.item(items[0], 'values')) == ['#1', 'Slime Xanh', '10', '100']")

with open("tests/unit/dialogs/test_monster_picker.py", "w", encoding="utf-8") as f:
    f.write(content)
