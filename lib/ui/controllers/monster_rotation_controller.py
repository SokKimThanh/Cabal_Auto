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
