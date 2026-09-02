import threading
import time
import uuid
from typing import Dict, List, Any, Optional

class RuntimeMonsterQueue:
    def __init__(
        self,
        capacity: int = 50,
        ttl_sec: float = 1.0,
        publish_callback: Optional[Any] = None
    ):
        self.capacity = capacity
        self.ttl_sec = ttl_sec
        self.publish_callback = publish_callback

        self.items: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()

        self.last_publish_time = 0.0
        self.publish_interval = 1.0 / 5.0  # Max 5 FPS

    def _calculate_iou(self, boxA: tuple, boxB: tuple) -> float:
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[0] + boxA[2], boxB[0] + boxB[2])
        yB = min(boxA[1] + boxA[3], boxB[1] + boxB[3])

        interArea = max(0, xB - xA) * max(0, yB - yA)
        if interArea == 0:
            return 0.0

        boxAArea = boxA[2] * boxA[3]
        boxBArea = boxB[2] * boxB[3]
        return interArea / float(boxAArea + boxBArea - interArea)

    def add_or_update(
        self,
        monster_id: int,
        name: str,
        bbox: tuple,
        confidence: float,
        template_id: str,
        resolution_state: str,
        dungeon_id: Optional[str] = None
    ) -> None:
        now = time.time()

        center_x = bbox[0] + bbox[2] // 2
        center_y = bbox[1] + bbox[3] // 2

        with self._lock:
            # Deduplicate
            best_match_key = None
            for key, item in self.items.items():
                if item["monster_id"] == monster_id:
                    iou = self._calculate_iou(bbox, item["bbox"])
                    # Proximity fallback (distance between centers)
                    dist = ((center_x - item["center"][0]) ** 2 + (center_y - item["center"][1]) ** 2) ** 0.5

                    if iou > 0.5 or dist < 50:
                        best_match_key = key
                        break

            if best_match_key:
                # Update existing
                item = self.items[best_match_key]
                item["last_seen"] = now
                item["bbox"] = bbox
                item["center"] = (center_x, center_y)
                item["confidence"] = confidence
                item["template_id"] = template_id
                item["resolution_state"] = resolution_state
            else:
                # Create new
                runtime_id = str(uuid.uuid4())
                new_item = {
                    "runtime_id": runtime_id,
                    "monster_id": monster_id,
                    "name": name,
                    "dungeon_id": dungeon_id,
                    "bbox": bbox,
                    "center": (center_x, center_y),
                    "confidence": confidence,
                    "template_id": template_id,
                    "resolution_state": resolution_state,
                    "first_seen": now,
                    "last_seen": now,
                }

                # Check capacity
                if len(self.items) >= self.capacity:
                    # Drop lowest confidence
                    lowest_key = min(self.items.keys(), key=lambda k: self.items[k]["confidence"])
                    if confidence > self.items[lowest_key]["confidence"]:
                        del self.items[lowest_key]
                        self.items[runtime_id] = new_item
                else:
                    self.items[runtime_id] = new_item

            self._prune_stale_items(now)

    def _prune_stale_items(self, now: float) -> None:
        stale_keys = [k for k, v in self.items.items() if (now - v["last_seen"]) > self.ttl_sec]
        for k in stale_keys:
            del self.items[k]

    def get_snapshot(self) -> tuple:
        with self._lock:
            self._prune_stale_items(time.time())
            return tuple(item.copy() for item in self.items.values())

    def get_attack_queue(
        self,
        target_policy: str,
        configured_rotation_ids: List[int]
    ) -> tuple:
        snapshot = self.get_snapshot()

        attack_queue = []
        for item in snapshot:
            if item["monster_id"] <= 0 or item["resolution_state"] != "db_match":
                continue

            if target_policy == "configured_only":
                if item["monster_id"] in configured_rotation_ids:
                    attack_queue.append(item)
            elif target_policy == "all_resolved":
                attack_queue.append(item)
            elif target_policy == "any_target":
                pass

        # Sort by confidence or proximity (here we'll just sort by confidence desc)
        attack_queue.sort(key=lambda x: x["confidence"], reverse=True)
        return tuple(attack_queue)

    def maybe_publish(self, schedule_ui_task_fn: Any) -> None:
        if not self.publish_callback or not schedule_ui_task_fn:
            return

        now = time.time()
        if now - self.last_publish_time >= self.publish_interval:
            snapshot = self.get_snapshot()
            schedule_ui_task_fn(lambda: self.publish_callback(snapshot))
            self.last_publish_time = now
