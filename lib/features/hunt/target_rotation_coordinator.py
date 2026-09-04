from typing import List, Dict, Optional, Any
import copy
import logging

class TargetRotationCoordinator:
    """
    Coordinates target acquisition based on configured policies.
    Owns the active desired pointer for the hunt session.
    """

    MATCHED = "MATCHED"
    MISMATCH = "MISMATCH"
    UNKNOWN = "UNKNOWN"

    def __init__(self, target_policy: str, monster_rotation: List[Dict]):
        self.target_policy = target_policy
        self.configured_rotation = self._normalize_rotation(monster_rotation)
        self.runtime_queue: List[Dict] = []

        self.current_index = 0
        self.active_runtime_candidate: Optional[Dict] = None

    def _normalize_rotation(self, rotation: List[Any]) -> List[Dict]:
        """Validates and sorts the rotation snapshot by priority."""
        valid = []
        for i, entry in enumerate(rotation):
            if isinstance(entry, dict) and "monster_id" in entry:
                try:
                    m_id = int(entry["monster_id"])
                    if m_id > 0:
                        new_entry = {
                            "monster_id": m_id,
                            "name": str(entry.get("name", "")).strip(),
                            "priority": int(entry.get("priority", i)),
                            "dungeon_id": entry.get("dungeon_id"),
                            "original_index": i
                        }
                        valid.append(new_entry)
                except (ValueError, TypeError):
                    pass

        # Sort by priority, then by original index for tie-breaking
        return sorted(valid, key=lambda x: (x["priority"], x["original_index"]))

    def is_rotation_valid(self) -> bool:
        if self.target_policy == "configured_only":
            return len(self.configured_rotation) > 0
        return True # other modes can be empty init

    def get_desired_target(self) -> Optional[Dict]:
        """Returns the current desired target for status/UI."""
        if self.target_policy == "configured_only":
            if not self.configured_rotation:
                return None
            return self.configured_rotation[self.current_index]
        elif self.target_policy == "all_resolved":
            return self.active_runtime_candidate
        elif self.target_policy == "any_target":
            return {"name": "Any Target", "monster_id": None}
        return None

    def update_runtime_queue(self, new_queue: List[Dict]):
        """Updates the transient attack queue from CB2D (all_resolved)."""
        # Reconcile valid candidates
        valid_candidates = []
        for c in new_queue:
            if c.get("match_type") == "db_match":
                try:
                    m_id = int(c.get("monster_id", 0))
                    if m_id > 0:
                        c_copy = copy.deepcopy(c)
                        c_copy["monster_id"] = m_id
                        valid_candidates.append(c_copy)
                except (ValueError, TypeError):
                    pass
        self.runtime_queue = valid_candidates

        # In all_resolved mode, try to pick the first candidate if we don't have one
        if self.target_policy == "all_resolved":
            if self.active_runtime_candidate:
                # Check if it's still in the queue (TTL)
                active_id = self.active_runtime_candidate["monster_id"]
                if not any(c["monster_id"] == active_id for c in self.runtime_queue):
                    self.active_runtime_candidate = None

            if not self.active_runtime_candidate and self.runtime_queue:
                self.active_runtime_candidate = self.runtime_queue[0]

    def evaluate_target(self, resolved_id: Any, is_alive: bool) -> str:
        """Evaluates a resolved target ID against the active policy."""
        if not is_alive:
            return self.UNKNOWN

        if self.target_policy == "any_target":
            return self.MATCHED

        # Parse ID
        try:
            r_id = int(resolved_id) if resolved_id is not None else 0
        except (ValueError, TypeError):
            r_id = 0

        if r_id <= 0:
            return self.UNKNOWN

        if self.target_policy == "configured_only":
            desired = self.get_desired_target()
            if not desired:
                return self.UNKNOWN
            if desired["monster_id"] == r_id:
                return self.MATCHED
            else:
                return self.MISMATCH

        elif self.target_policy == "all_resolved":
            # Target OCR/DB must match an active runtime candidate with TTL
            if not self.active_runtime_candidate:
                return self.MISMATCH

            # Check if r_id matches any candidate in the current runtime queue
            # to verify it's still present and hasn't TTL'd out
            in_queue = any(c["monster_id"] == r_id for c in self.runtime_queue)

            # Specifically check against our ACTIVE candidate
            if in_queue and self.active_runtime_candidate["monster_id"] == r_id:
                return self.MATCHED
            return self.MISMATCH

        return self.UNKNOWN

    def advance_pointer(self) -> Optional[Dict]:
        """Advances pointer after completion gate."""
        prev = self.get_desired_target()

        if self.target_policy == "configured_only":
            if self.configured_rotation:
                self.current_index = (self.current_index + 1) % len(self.configured_rotation)

        elif self.target_policy == "all_resolved":
            # Remove current active, pick next
            if self.active_runtime_candidate:
                active_id = self.active_runtime_candidate["monster_id"]
                self.runtime_queue = [c for c in self.runtime_queue if c["monster_id"] != active_id]
                self.active_runtime_candidate = None

            if self.runtime_queue:
                self.active_runtime_candidate = self.runtime_queue[0]

        # any_target does not advance a specific ID pointer
        return prev
