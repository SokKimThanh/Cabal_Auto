import re

with open("ui/tabs/hunt_tab.py", "r", encoding="utf-8") as f:
    content = f.read()

replacement = """        # Re-attach bindings
        # We removed self.app._on_monster_list_select because it was deleted during refactoring.
        # It's an empty method anyway, so we just remove the binding.
        self.app.monster_rotation_listbox.bind(
            "<Delete>", self.app._on_monster_delete_from_list
        )
        self.app.monster_rotation_listbox.bind(
            "<BackSpace>", self.app._on_monster_delete_from_list
        )"""

content = re.sub(r'        # Re-attach bindings\n        self\.app\.monster_rotation_listbox\.bind\(\n            "<<ListboxSelect>>", self\.app\._on_monster_list_select\n        \)\n        self\.app\.monster_rotation_listbox\.bind\(\n            "<Delete>", self\.app\._on_monster_delete_from_list\n        \)\n        self\.app\.monster_rotation_listbox\.bind\(\n            "<BackSpace>", self\.app\._on_monster_delete_from_list\n        \)', replacement, content, flags=re.DOTALL)

with open("ui/tabs/hunt_tab.py", "w", encoding="utf-8") as f:
    f.write(content)
