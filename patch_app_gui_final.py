import re

with open("app_gui.py", "r") as f:
    content = f.read()
"""Deprecated developer-only patch script.

This repository must not ship one-off source-rewriting helpers alongside
product code. The original implementation of this file modified `app_gui.py`
in place; it has been disabled to prevent accidental or intentional mutation
of repository sources during normal execution, CI, or packaging.
"""

raise SystemExit(
    "patch_app_gui_final.py is disabled. Remove this patch helper or move it "
    "to a separate developer-only tooling area excluded from distribution and CI."
)

# Add promote method to App
search = """    def _refresh_monster_rotation_list(self):"""

replace = """    def promote_detected_monster(self, selection):
        if not selection:
            return

        idx = selection[0]
        if not hasattr(self, '_detected_snapshot_items') or idx >= len(self._detected_snapshot_items):
            return

        runtime_item = self._detected_snapshot_items[idx]

        # Only db_match items with valid monster_id can be promoted
        if runtime_item.get("resolution_state") != "db_match" or not runtime_item.get("monster_id"):
            return

        monster_id = runtime_item["monster_id"]
        dungeon_id = runtime_item.get("dungeon_id")

        # Check for duplicates
        for existing in self.monster_rotation:
            if existing.get("monster_id") == monster_id and existing.get("dungeon_id") == dungeon_id:
                # Already exists
                return

        # Calculate new priority
        max_priority = 0
        for m in self.monster_rotation:
            if m.get("priority", 0) > max_priority:
                max_priority = m.get("priority", 0)

        new_priority = max_priority + 1

        # Add to rotation
        new_entry = {
            "monster_id": monster_id,
            "name": runtime_item.get("name", "Unknown"),
            "priority": new_priority,
            "dungeon_id": dungeon_id
        }
        self.monster_rotation.append(new_entry)

        # Normalize priorities 1..N
        self.monster_rotation.sort(key=lambda x: x.get("priority", 999))
        for i, m in enumerate(self.monster_rotation, 1):
            m["priority"] = i

        self.has_unsaved_changes = True
        if hasattr(self, "_update_unsaved_indicator"):
            self._update_unsaved_indicator()

        self._refresh_monster_rotation_list()

        # We also need to refresh the detected list to show the 'Added' status
        if hasattr(self, '_last_snapshot'):
            self._update_detected_monsters_list(self._last_snapshot)

    def on_scene_monsters_detected(self, snapshot):
        # Throttle/ensure running on main thread is done by HuntOrchestrator
        self._last_snapshot = snapshot
        if self.hunt_cfg.get("target_policy", "configured_only") == "all_resolved":
            self._update_detected_monsters_list(snapshot)

    def _update_detected_monsters_list(self, snapshot):
        if not hasattr(self, "detected_monsters_listbox"):
            return

        current_selection = self.detected_monsters_listbox.curselection()
        selected_idx = current_selection[0] if current_selection else None

        # We need to maintain scroll position if possible
        yview = self.detected_monsters_listbox.yview()

        self.detected_monsters_listbox.delete(0, tk.END)
        self._detected_snapshot_items = []

        configured_keys = {(m.get("monster_id"), m.get("dungeon_id")) for m in getattr(self, 'monster_rotation', []) if m.get("monster_id")}

        for idx, item in enumerate(snapshot):
            self._detected_snapshot_items.append(item)

            name = item.get("name", "Unknown")
            resolution_state = item.get("resolution_state", "unmapped_visual")
            monster_id = item.get("monster_id")

            if resolution_state == "db_match":
                status = "✓ "
                if (monster_id, item.get("dungeon_id")) in configured_keys:
                    status += f"[{self._t('monster_promoted')}] "
                elif item.get("confidence", 0) > 0:
                    status += f"({item['confidence']:.2f}) "
                display_text = f"{status}{name} #{monster_id} - {self._t('monster_db_match')}"
            elif resolution_state == "db_miss":
                display_text = f"⚠ {name} - {self._t('monster_db_missing')}"
            else:
                display_text = f"❓ {self._t('monster_unidentified')} ({item.get('template_label', '')})"

            self.detected_monsters_listbox.insert(tk.END, display_text)

        if selected_idx is not None and selected_idx < len(self._detected_snapshot_items):
            self.detected_monsters_listbox.selection_set(selected_idx)

        self.detected_monsters_listbox.yview_moveto(yview[0])


    def _refresh_monster_rotation_list(self):"""

content = content.replace(search, replace)

with open("app_gui.py", "w") as f:
    f.write(content)
