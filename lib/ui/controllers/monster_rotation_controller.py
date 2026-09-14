from typing import Dict, Any
from lib.events.event_bus import EventBus, MonsterRotationUpdatedEvent

class MonsterRotationController:
    def __init__(self, state_controller):
        self.state_controller = state_controller

    def promote_detected_monster(self, runtime_item: Dict[str, Any]) -> None:
        """
        Promotes a detected monster item to the active rotation list.
        Calculates priority, checks for duplicates, and triggers UI update event.
        """
        if not runtime_item:
            return

        # Only db_match items with valid monster_id can be promoted
        if runtime_item.get("resolution_state") != "db_match" or not runtime_item.get("monster_id"):
            return

        monster_id = runtime_item["monster_id"]
        dungeon_id = runtime_item.get("dungeon_id")

        # Check for duplicates
        for existing in self.state_controller.monster_rotation:
            if existing.get("monster_id") == monster_id and existing.get("dungeon_id") == dungeon_id:
                return  # Already exists

        # Calculate new priority
        max_priority = 0
        for m in self.state_controller.monster_rotation:
            if m.get("priority", 0) > max_priority:
                max_priority = m.get("priority", 0)

        new_priority = max_priority + 1

        # Add to rotation
        new_entry = {
            "monster_id": monster_id,
            "name": runtime_item.get("name", "Unknown"),
            "priority": new_priority,
            "dungeon_id": dungeon_id,
        }
        self.state_controller.monster_rotation.append(new_entry)

        # Normalize priorities 1..N
        self.state_controller.monster_rotation.sort(key=lambda x: x.get("priority", 999))
        for i, m in enumerate(self.state_controller.monster_rotation, 1):
            m["priority"] = i

        self.state_controller.has_unsaved_changes = True

        # Trigger event for UI to update
        EventBus.trigger(MonsterRotationUpdatedEvent())

    def on_monster_rotation_updated(self):
        if hasattr(self.state_controller.root, "_update_unsaved_indicator"):
            self.state_controller.root._update_unsaved_indicator()
        self.refresh_monster_rotation_list()
        if hasattr(self.state_controller.root, "_last_snapshot"):
            self.update_detected_monsters_list(self.state_controller.root._last_snapshot)

    def update_detected_monsters_list(self, snapshot):
        if "detected_monsters_listbox" not in self.state_controller.ui_widgets or not self.state_controller.ui_widgets["detected_monsters_listbox"]:
            return

        listbox = self.state_controller.ui_widgets["detected_monsters_listbox"]
        current_selection = listbox.curselection()
        selected_idx = current_selection[0] if current_selection else None

        import tkinter as tk
        yview = listbox.yview()
        listbox.delete(0, tk.END)

        if not hasattr(self.state_controller.root, "_detected_snapshot_items"):
            self.state_controller.root._detected_snapshot_items = []
        self.state_controller.root._detected_snapshot_items.clear()

        configured_keys = {
            (m.get("monster_id"), m.get("dungeon_id"))
            for m in getattr(self.state_controller, "monster_rotation", [])
            if m.get("monster_id")
        }

        for _idx, item in enumerate(snapshot):
            self.state_controller.root._detected_snapshot_items.append(item)

            name = item.get("name", "Unknown")
            resolution_state = item.get("resolution_state", "unmapped_visual")
            monster_id = item.get("monster_id")

            if resolution_state == "db_match":
                status = "✓ "
                if (monster_id, item.get("dungeon_id")) in configured_keys:
                    status += f"[{self.state_controller.root._t('monster_promoted')}] "
                elif item.get("confidence", 0) > 0:
                    status += f"({item['confidence']:.2f}) "
                display_text = (
                    f"{status}{name} #{monster_id} - {self.state_controller.root._t('monster_db_match')}"
                )
            elif resolution_state == "db_miss":
                display_text = f"⚠ {name} - {self.state_controller.root._t('monster_db_missing')}"
            else:
                display_text = f"❓ {self.state_controller.root._t('monster_unidentified')} ({item.get('template_label', '')})"

            listbox.insert(tk.END, display_text)

        if selected_idx is not None and selected_idx < len(self.state_controller.root._detected_snapshot_items):
            listbox.selection_set(selected_idx)

        listbox.yview_moveto(yview[0])

    def refresh_monster_rotation_list(self):
        if "monster_rotation_listbox" not in self.state_controller.ui_widgets or not self.state_controller.ui_widgets["monster_rotation_listbox"]:
            return

        import tkinter as tk
        listbox = self.state_controller.ui_widgets["monster_rotation_listbox"]
        listbox.delete(0, tk.END)

        from database import get_monster_by_id_api, find_monster_by_name_api

        self.state_controller.monster_rotation.sort(key=lambda x: x.get("priority", 999))

        for _idx, entry in enumerate(self.state_controller.monster_rotation):
            monster_id = entry.get("monster_id")
            name = entry.get("name")
            dungeon_id = entry.get("dungeon_id")

            cache_key = f"{monster_id}_{name}_{dungeon_id}"

            if cache_key not in self.state_controller._monster_session_manager._metadata_cache:
                db_record = (
                    get_monster_by_id_api(str(monster_id)) if monster_id else None
                )
                if not db_record and name:
                    db_record = find_monster_by_name_api(name, dungeon_id)
                self.state_controller._monster_session_manager._metadata_cache[cache_key] = db_record
            else:
                db_record = self.state_controller._monster_session_manager._metadata_cache[cache_key]

            if db_record:
                level = db_record.get("level", "--")
                hp = db_record.get("hp", "--")
                display_str = f"[#{monster_id}] {name} - Lv.{level} | HP: {hp}"
            else:
                display_str = (
                    f"[{self.state_controller.root._t('monster_rotation_unknown')}] {name} - Lv.-- | HP: --"
                )

            listbox.insert(tk.END, display_str)

    def on_monster_move_up(self):
        listbox = self.state_controller.ui_widgets.get('monster_rotation_listbox')
        if not listbox: return
        selection = listbox.curselection()
        if not selection or selection[0] == 0:
            return

        idx = selection[0]
        self.state_controller.monster_rotation[idx], self.state_controller.monster_rotation[idx - 1] = (
            self.state_controller.monster_rotation[idx - 1],
            self.state_controller.monster_rotation[idx],
        )

        for i, entry in enumerate(self.state_controller.monster_rotation):
            entry["priority"] = i + 1

        if hasattr(self.state_controller.root, "_mark_unsaved"):
            self.state_controller.root._mark_unsaved()
        self.refresh_monster_rotation_list()
        listbox.selection_set(idx - 1)

    def on_monster_move_down(self):
        listbox = self.state_controller.ui_widgets.get('monster_rotation_listbox')
        if not listbox: return
        selection = listbox.curselection()
        if not selection or selection[0] == len(self.state_controller.monster_rotation) - 1:
            return

        idx = selection[0]
        self.state_controller.monster_rotation[idx], self.state_controller.monster_rotation[idx + 1] = (
            self.state_controller.monster_rotation[idx + 1],
            self.state_controller.monster_rotation[idx],
        )

        for i, entry in enumerate(self.state_controller.monster_rotation):
            entry["priority"] = i + 1

        if hasattr(self.state_controller.root, "_mark_unsaved"):
            self.state_controller.root._mark_unsaved()
        self.refresh_monster_rotation_list()
        listbox.selection_set(idx + 1)

    def on_monster_delete_from_list(self, _evt=None):
        listbox = self.state_controller.ui_widgets.get('monster_rotation_listbox')
        if not listbox: return
        selection = listbox.curselection()
        if not selection:
            return

        selected_indices = sorted(
            (idx for idx in selection if 0 <= idx < len(self.state_controller.monster_rotation)),
            reverse=True,
        )
        if not selected_indices:
            return
        first_deleted_index = min(selected_indices)
        for idx in selected_indices:
            del self.state_controller.monster_rotation[idx]

        for i, entry in enumerate(self.state_controller.monster_rotation):
            entry["priority"] = i + 1

        if hasattr(self.state_controller.root, "_mark_unsaved"):
            self.state_controller.root._mark_unsaved()
        self.refresh_monster_rotation_list()

        if len(self.state_controller.monster_rotation) > 0:
            new_sel = min(first_deleted_index, len(self.state_controller.monster_rotation) - 1)
            listbox.selection_set(new_sel)

    def on_monster_add_smart(self):
        def on_monster_selected(record):
            monster_id = record["monster_id"]
            dungeon_id = record.get("dungeon_id")

            for entry in self.state_controller.monster_rotation:
                if (
                    entry.get("monster_id") == monster_id
                    and entry.get("dungeon_id") == dungeon_id
                ):
                    from lib.ui.dialog_service import DialogService
                    DialogService.show_info(
                        self.state_controller.root._t("info_title", ns="ui"),
                        self.state_controller.root._t("monster_already_in_list").format(name=record.get("name", "Unknown")),
                        parent=self.state_controller.root,
                    )
                    return

            new_priority = len(self.state_controller.monster_rotation) + 1
            new_entry = {
                "monster_id": monster_id,
                "name": record.get("name", "Unknown"),
                "priority": new_priority,
                "dungeon_id": dungeon_id,
            }

            self.state_controller.monster_rotation.append(new_entry)
            if hasattr(self.state_controller.root, "_mark_unsaved"):
                self.state_controller.root._mark_unsaved()

            self.refresh_monster_rotation_list()

        from dialogs.monster_picker import MonsterPickerDialog
        MonsterPickerDialog(
            self.state_controller.root, getattr(self.state_controller.root, "lang", "vi"), on_monster_selected, self.state_controller.root._t
        )
