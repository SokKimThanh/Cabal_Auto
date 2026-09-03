import re

with open("app_gui.py", "r", encoding="utf-8") as f:
    content = f.read()

replacement_move = """    def _on_monster_move_up(self):
        selection = self.monster_rotation_listbox.curselection()
        if not selection or selection[0] == 0:
            return

        idx = selection[0]
        # Swap in RAM
        self.monster_rotation[idx], self.monster_rotation[idx - 1] = (
            self.monster_rotation[idx - 1],
            self.monster_rotation[idx],
        )

        # Re-assign priority to be continuous 1..N
        for i, entry in enumerate(self.monster_rotation):
            entry["priority"] = i + 1

        self._mark_unsaved()
        self._refresh_monster_rotation_list()
        self.monster_rotation_listbox.selection_set(idx - 1)

    def _on_monster_move_down(self):
        selection = self.monster_rotation_listbox.curselection()
        if not selection or selection[0] == len(self.monster_rotation) - 1:
            return

        idx = selection[0]
        # Swap in RAM
        self.monster_rotation[idx], self.monster_rotation[idx + 1] = (
            self.monster_rotation[idx + 1],
            self.monster_rotation[idx],
        )

        # Re-assign priority to be continuous 1..N
        for i, entry in enumerate(self.monster_rotation):
            entry["priority"] = i + 1

        self._mark_unsaved()
        self._refresh_monster_rotation_list()
        self.monster_rotation_listbox.selection_set(idx + 1)

    def _on_monster_delete_from_list(self, _evt=None):
        selection = self.monster_rotation_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        del self.monster_rotation[idx]

        # Re-assign priority to be continuous 1..N
        for i, entry in enumerate(self.monster_rotation):
            entry["priority"] = i + 1

        self._mark_unsaved()
        self._refresh_monster_rotation_list()

        if len(self.monster_rotation) > 0:
            new_sel = min(idx, len(self.monster_rotation) - 1)
            self.monster_rotation_listbox.selection_set(new_sel)"""

content = re.sub(r'    def _on_monster_move_up\(self\):.*?    def _on_monster_add_smart', replacement_move + "\n\n    def _on_monster_add_smart", content, flags=re.DOTALL)

with open("app_gui.py", "w", encoding="utf-8") as f:
    f.write(content)
