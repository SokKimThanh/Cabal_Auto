import re

with open("dialogs/monster_picker.py", "r", encoding="utf-8") as f:
    content = f.read()

# Clear map before rendering
replacement = """    def _render_results(self, records):
        self.tree.delete(*self.tree.get_children())
        self.status_var.set("")
        self.btn_confirm.config(state="disabled")
        self._item_map.clear()"""

content = re.sub(r'    def _render_results\(self, records\):\n        self\.tree\.delete\(\*self\.tree\.get_children\(\)\)\n        self\.status_var\.set\(""\)\n        self\.btn_confirm\.config\(state="disabled"\)', replacement, content)

with open("dialogs/monster_picker.py", "w", encoding="utf-8") as f:
    f.write(content)
