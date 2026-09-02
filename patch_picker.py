import re

with open("dialogs/monster_picker.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix 1: Make dialog resizable
content = content.replace('self.geometry("600x450")', 'self.geometry("600x450")\n        self.minsize(400, 300)\n        self.resizable(True, True)')

# Fix 2 & 6: Treeview configuration to use columns cleanly
treeview_fix = """        self.tree = ttk.Treeview(
            tree_frame,
            columns=("id", "name", "level", "hp"),
            show="headings",
            selectmode="browse"
        )

        self.tree.heading("id", text="ID", anchor="w")
        self.tree.heading("name", text=self._t("monster_name") if self._t else "Name", anchor="w")
        self.tree.heading("level", text="Lv", anchor="center")
        self.tree.heading("hp", text="HP", anchor="e")

        self.tree.column("id", width=50, stretch=False)
        self.tree.column("name", width=250, stretch=True)
        self.tree.column("level", width=50, stretch=False, anchor="center")
        self.tree.column("hp", width=80, stretch=False, anchor="e")"""

content = re.sub(r'        self\.tree = ttk\.Treeview\(.*?\n        # We don\'t really want to show column headers if there\'s only one display column\n        self\.tree\.configure\(show="tree"\)', treeview_fix, content, flags=re.DOTALL)

# Fix 3: Initialize _item_map in __init__
content = content.replace("self._search_timer = None", "self._search_timer = None\n        self._item_map = {}")

content = content.replace("""            # We can't attach arbitrarily to treeview, so we keep a local map of iid -> dict
            if not hasattr(self, '_item_map'):
                self._item_map = {}
            self._item_map[item_id] = canonical_record""", """            # Store canonical mapping
            self._item_map[item_id] = canonical_record""")

# Fix 4: Log exceptions
content = content.replace("""        except Exception as e:
            self._render_error()""", """        except Exception as e:
            import logging
            logging.error(f"[MonsterPicker] Error loading data: {e}", exc_info=True)
            self._render_error()""")

# Fix display text to match new columns
render_loop_replace = """            # [#<id>] <name> - Lv.<level> | HP: <hp>
            display_text = f"[#{id_val}] {name_val} - Lv.{lvl_val} | HP: {hp_val}"

            # Store raw data in tree item tags or values
            # Using iid to store the ID is a bad idea because it must be string, and we need canonical mapping.
            # Treeview stores values as tuple.
            item_id = self.tree.insert("", "end", text=display_text)"""

new_render_loop = """            item_id = self.tree.insert("", "end", values=(f"#{id_val}", name_val, lvl_val, hp_val))"""

content = content.replace(render_loop_replace, new_render_loop)

with open("dialogs/monster_picker.py", "w", encoding="utf-8") as f:
    f.write(content)
