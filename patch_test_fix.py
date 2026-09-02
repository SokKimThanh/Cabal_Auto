import re

with open("tests/unit/dialogs/test_monster_picker.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("with pytest.raises(tk.TclError):\n            dialog.winfo_exists()", "assert dialog.winfo_exists() == 0")

with open("tests/unit/dialogs/test_monster_picker.py", "w", encoding="utf-8") as f:
    f.write(content)
