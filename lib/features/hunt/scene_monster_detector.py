import threading
import time
from typing import Dict, Any, Optional

from lib.vision.vision_engine import VisionEngine
from lib.features.hunt.runtime_monster_queue import RuntimeMonsterQueue
from database import get_monster_by_id_api

class SceneMonsterDetector:
    def __init__(self, vision_engine: VisionEngine, runtime_queue: RuntimeMonsterQueue):
        self.vision_engine = vision_engine
        self.runtime_queue = runtime_queue

        # Cache for DB lookups
        self._db_cache: Dict[str, Optional[Dict[str, Any]]] = {}
        self._lock = threading.RLock()

    def _resolve_monster_meta(self, monster_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            if monster_id in self._db_cache:
                return self._db_cache[monster_id]

            monster = get_monster_by_id_api(monster_id)
            self._db_cache[monster_id] = monster
            return monster

    def process_frame(self, frame: Any) -> None:
        """
        Process a single frame to detect scene monsters and update the runtime queue.
        Must be called from a worker thread.
        """
        if frame is None or getattr(frame, 'size', 0) == 0:
            return

        # 1. Gather valid template IDs
        # Only process templates that have a valid mapped monster_id
        valid_template_ids = []
        for tmpl in self.vision_engine.templates.values():
            if tmpl.enabled and hasattr(tmpl, "monster_id") and tmpl.monster_id is not None:
                valid_template_ids.append(tmpl.id)

        # 2. Run detection pipeline
        # Force use_fast_hsv=False as we don't want generic blobs
        detections = self.vision_engine.detect_monster_pipeline(
            frame,
            template_ids=valid_template_ids,
            use_fast_hsv=False
        )

        # 3. Process detections and enqueue
        for det in detections:
            tmpl = self.vision_engine.templates.get(det.template_id)
            if not tmpl:
                continue

            monster_id = getattr(tmpl, "monster_id", None)
            dungeon_id = getattr(tmpl, "dungeon_id", None)

            if monster_id is None:
                # Should not happen given valid_template_ids filtering, but safe fallback
                self.runtime_queue.add_or_update(
                    monster_id=0,
                    name="Unknown target",
                    bbox=det.bbox(),
                    confidence=det.score,
                    template_id=det.template_id,
                    resolution_state="unmapped_visual",
                    dungeon_id=dungeon_id
                )
                continue

            monster_meta = self._resolve_monster_meta(str(monster_id))

            if monster_meta:
                self.runtime_queue.add_or_update(
                    monster_id=int(monster_id),
                    name=monster_meta.get("name", f"Monster {monster_id}"),
                    bbox=det.bbox(),
                    confidence=det.score,
                    template_id=det.template_id,
                    resolution_state="db_match",
                    dungeon_id=dungeon_id
                )
            else:
                self.runtime_queue.add_or_update(
                    monster_id=0,
                    name="Unknown target",
                    bbox=det.bbox(),
                    confidence=det.score,
                    template_id=det.template_id,
                    resolution_state="db_miss",
                    dungeon_id=dungeon_id
                )
