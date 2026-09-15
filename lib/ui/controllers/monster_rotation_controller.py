from typing import Dict, Any

from lib.events.event_bus import (
    EventBus, MonsterRotationUpdatedEvent, MonsterMoveUpEvent, MonsterMoveDownEvent,
    MonsterDeleteEvent, MonsterAddSmartEvent
)
from lib.ui.dialog_service import DialogService


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

    def bind_events(self):
        EventBus.bind(MonsterMoveUpEvent, self._on_monster_move_up)
        EventBus.bind(MonsterMoveDownEvent, self._on_monster_move_down)
        EventBus.bind(MonsterDeleteEvent, self._on_monster_delete_from_list)
        EventBus.bind(MonsterAddSmartEvent, self._on_monster_add_smart)

    def unbind_events(self):
        EventBus.unbind(MonsterMoveUpEvent, self._on_monster_move_up)
        EventBus.unbind(MonsterMoveDownEvent, self._on_monster_move_down)
        EventBus.unbind(MonsterDeleteEvent, self._on_monster_delete_from_list)
        EventBus.unbind(MonsterAddSmartEvent, self._on_monster_add_smart)

    def _mark_unsaved(self):
        self.state_controller.has_unsaved_changes = True


    def _on_monster_move_up(self, event: MonsterMoveUpEvent):
        idx = event.index
        if idx == 0 or idx >= len(self.state_controller.monster_rotation):
            return

        # Swap in RAM
        self.state_controller.monster_rotation[idx], self.state_controller.monster_rotation[idx - 1] = (
            self.state_controller.monster_rotation[idx - 1],
            self.state_controller.monster_rotation[idx],
        )

        # Re-assign priority to be continuous 1..N
        for i, entry in enumerate(self.state_controller.monster_rotation):
            entry["priority"] = i + 1

        self._mark_unsaved()
        EventBus.trigger(MonsterRotationUpdatedEvent(selected_index=idx - 1))

    def _on_monster_move_down(self, event: MonsterMoveDownEvent):
        idx = event.index
        if idx == len(self.state_controller.monster_rotation) - 1 or idx < 0:
            return

        # Swap in RAM
        self.state_controller.monster_rotation[idx], self.state_controller.monster_rotation[idx + 1] = (
            self.state_controller.monster_rotation[idx + 1],
            self.state_controller.monster_rotation[idx],
        )

        # Re-assign priority to be continuous 1..N
        for i, entry in enumerate(self.state_controller.monster_rotation):
            entry["priority"] = i + 1

        self._mark_unsaved()
        EventBus.trigger(MonsterRotationUpdatedEvent(selected_index=idx + 1))

    def _on_monster_delete_from_list(self, event: MonsterDeleteEvent):
        selection = event.indices
        if not selection:
            return

        selected_indices = sorted(
            (idx for idx in selection if 0 <= idx < len(self.state_controller.monster_rotation)),
            reverse=True,
        )
        if not selected_indices:
            return

        for idx in selected_indices:
            del self.state_controller.monster_rotation[idx]

        # Re-assign priority to be continuous 1..N
        for i, entry in enumerate(self.state_controller.monster_rotation):
            entry["priority"] = i + 1

        self._mark_unsaved()

        new_sel = None
        if len(self.state_controller.monster_rotation) > 0:
            first_deleted = selected_indices[-1]
            new_sel = min(first_deleted, len(self.state_controller.monster_rotation) - 1)
        EventBus.trigger(MonsterRotationUpdatedEvent(selected_index=new_sel))
    def _on_monster_add_smart(self, event: MonsterAddSmartEvent):
        record = event.record
        monster_id = record["monster_id"]
        dungeon_id = record.get("dungeon_id")

        # Deduplicate by (monster_id, dungeon_id)
        for entry in self.state_controller.monster_rotation:
            if (
                entry.get("monster_id") == monster_id
                and entry.get("dungeon_id") == dungeon_id
            ):

                if hasattr(self.state_controller, "app") and hasattr(self.state_controller.app, "_t"):
                    title = self.state_controller.app._t("info_title", ns="ui")
                    msg = self.state_controller.app._t("monster_already_in_list").format(name=record.get("name", "Unknown"))
                else:
                    title = "Info"
                    msg = f"Monster {record.get('name', 'Unknown')} is already in rotation list"

                DialogService.show_info(title, msg)

                return

        # Add with new priority
        new_priority = len(self.state_controller.monster_rotation) + 1
        new_entry = {
            "monster_id": monster_id,
            "name": record.get("name", "Unknown"),
            "priority": new_priority,
            "dungeon_id": dungeon_id,
        }

        self.state_controller.monster_rotation.append(new_entry)
        self._mark_unsaved()
        EventBus.trigger(MonsterRotationUpdatedEvent())
