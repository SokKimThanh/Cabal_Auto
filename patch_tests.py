import re

with open("tests/unit/dialogs/test_monster_picker.py", "r", encoding="utf-8") as f:
    content = f.read()

replacement1 = """        dialog.tree.update_idletasks()
        dialog.tree.event_generate('<Return>')"""

content = content.replace("        dialog.tree.event_generate('<Return>')", replacement1)

replacement2 = """        dialog.tree.update_idletasks()
        dialog._on_confirm()"""

content = content.replace("        dialog.tree.event_generate('<Double-1>')", replacement2)

with open("tests/unit/dialogs/test_monster_picker.py", "w", encoding="utf-8") as f:
    f.write(content)
