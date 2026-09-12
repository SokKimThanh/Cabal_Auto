import time
import logging
from typing import Dict, Any, List

from lib.system.win_input import tap
from lib.features.skills.cast_delivery import CastOutcome

class SkillCasterService:
    def __init__(self):
        self.skill_runtime_obj = None
        self._last_combo_mode = None
        self.combo_detector = None

    def get_skill_runtime_object(self, cfg: Dict[str, Any]):
        from lib.features.skills.runtime import SkillRuntime
        return SkillRuntime(cfg.get("skill_slots", []))

    def prepare_skill_runtime(self, cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
        runtime: List[Dict[str, Any]] = []
        for slot in cfg.get("skill_slots", []) or []:
            if not isinstance(slot, dict):
                continue
            runtime.append(
                {
                    "id": slot.get("id", slot.get("name", "")),
                    "name": slot.get("name", ""),
                    "key": slot.get("key", ""),
                    "type": slot.get("type", "attack"),
                    "cooldown": float(slot.get("cooldown", 0.0)),
                    "cast_time": float(slot.get("cast_time", 0.0)),
                    "_last_cast": 0.0,
                }
            )
        return runtime

    def try_cast_skills(
        self,
        skill_runtime,
        now: float,
        target_active: bool,
        attack_phase: bool = False,
        skill_stats=None,
        backend=None,
        hunt_cfg: Dict[str, Any] = None,
        bot_manager=None,
    ) -> None:
        if hunt_cfg is None:
            hunt_cfg = {}

        combo_enabled = hunt_cfg.get("combo", {}).get("enabled", False)

        # Get next skill from SkillRuntime object
        if self.skill_runtime_obj is None:
            self.skill_runtime_obj = self.get_skill_runtime_object(hunt_cfg)

        # Sync pointer if mode changed
        last_combo_mode = getattr(self, "_last_combo_mode", combo_enabled)
        if combo_enabled != last_combo_mode:
            self.skill_runtime_obj.sync_combo_pointer(to_combo=combo_enabled)
            self._last_combo_mode = combo_enabled

        if not attack_phase:
            buff_key = self.skill_runtime_obj.get_buff_to_cast(now)
            if buff_key:
                if backend:
                    backend.tap(buff_key, int(hunt_cfg.get("attack_press_ms", 60)))
                else:
                    tap(buff_key, int(hunt_cfg.get("attack_press_ms", 60)))
                self.skill_runtime_obj.mark_cast(buff_key, now)

                # Also update old dict for legacy compatibility
                for s in skill_runtime:
                    if s.get("key") == buff_key:
                        s["_last_cast"] = now
                        cast_time = float(s.get("cast_time", 0.0))
                        if cast_time > 0:
                            time.sleep(cast_time)
            return

        if not target_active:
            return

        next_skill = (
            self.skill_runtime_obj.get_attack_to_cast(now)
            if not combo_enabled
            else self.skill_runtime_obj.get_next_combo_skill(now)
        )

        if not next_skill:
            return

        # Reserve the skill
        res = self.skill_runtime_obj.reserve_next_skill(
            "attack", now, is_combo=combo_enabled
        )
        if not res:
            return

        outcome = CastOutcome.ACCEPTED

        if combo_enabled:
            from lib.features.combo.combo_timing_detector import CabalComboDetector

            # Create or reuse detector
            if self.combo_detector is None:
                self.combo_detector = CabalComboDetector(hwnd=0)

            def do_press():
                if backend:
                    backend.tap(res.key, int(hunt_cfg.get("attack_press_ms", 60)))
                else:
                    tap(res.key, int(hunt_cfg.get("attack_press_ms", 60)))

            self.combo_detector.key_press_callback = do_press

            if bot_manager and getattr(bot_manager, "screen_capture", None):
                timeout_sec = float(
                    hunt_cfg.get("combo", {}).get("hit_zone_timeout_sec", 2.0)
                )
                detected = self.combo_detector.wait_for_hit_zone(
                    bot_manager.screen_capture, timeout_sec=timeout_sec
                )
                if not detected:
                    logging.getLogger(__name__).warning(
                        "Combo timeout reached. Falling back to static cast."
                    )
                    do_press()
            else:
                do_press()
        else:
            if backend:
                backend.tap(res.key, int(hunt_cfg.get("attack_press_ms", 60)))
            else:
                tap(res.key, int(hunt_cfg.get("attack_press_ms", 60)))

        cast_ts = time.time()

        # Commit cast
        self.skill_runtime_obj.commit_cast(res.token, outcome, cast_ts)

        # Record stats
        if skill_stats:
            try:
                skill_stats.record_cast(
                    res.skill_name or res.key, success=True, timestamp=cast_ts
                )
            except Exception:
                pass

        # Also update old dict
        for s in skill_runtime:
            if s.get("key") == res.key:
                s["_last_cast"] = cast_ts
                cast_time = float(s.get("cast_time", 0.0))
                if cast_time > 0 and not combo_enabled:
                    time.sleep(cast_time)
                break
