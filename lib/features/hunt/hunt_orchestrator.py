from lib.vision.target_bar_detector import TargetBarDetector
import time
import threading
from pathlib import Path
from typing import Callable, Dict, Any

from lib.system.hunt_logger import get_hunt_logger
from lib.system.win_input import tap
from lib.features.skills.skill_stats import SkillStats
from lib.vision.target_name_reader import TargetNameReader
from database import find_monster_by_name_api


class HuntOrchestrator:
    def __init__(
        self,
        on_status_update: Callable[[str], None],
        on_state_change: Callable[[str], None],  # "running", "idle", "error"
        locate_target: Callable[[Dict[str, Any]], tuple],  # (box, match_info)
        prepare_skill_runtime: Callable[[Dict[str, Any]], list],
        try_cast_skills: Callable,
        bring_window_to_front: Callable[[str], bool],
        bring_window_to_front_by_hwnd: Callable[[int], bool],
        bring_window_to_front_by_pid: Callable[[int], bool],
        iconify_app: Callable[[], None],
        update_skill_stats_display: Callable[[dict], None],
        get_hunt_selected: Callable[[], Dict[str, Any]],
        schedule_ui_task: Callable[[Callable], None],
        clear_target_ui: Callable[[], None] = None,
        set_target_info: Callable[[str], None] = None
    ):
        self.clear_target_ui = clear_target_ui
        self.set_target_info = set_target_info
        self.on_status_update = on_status_update
        self.on_state_change = on_state_change
        self.locate_target = locate_target
        self.prepare_skill_runtime = prepare_skill_runtime
        self.try_cast_skills = try_cast_skills

        self.bring_window_to_front = bring_window_to_front
        self.bring_window_to_front_by_hwnd = bring_window_to_front_by_hwnd
        self.bring_window_to_front_by_pid = bring_window_to_front_by_pid
        self.iconify_app = iconify_app
        self.update_skill_stats_display = update_skill_stats_display
        self.get_hunt_selected = get_hunt_selected
        self.schedule_ui_task = schedule_ui_task

        self.hunt_running = False
        self.hunt_thread = None

    def start_hunt(self, cfg: Dict[str, Any]):
        if self.hunt_running:
            return

        self.hunt_running = True
        self.schedule_ui_task(lambda: self.on_state_change("running"))

        def worker():

            target_bar_detector = TargetBarDetector()
            target_name_reader = TargetNameReader()
            consecutive_false_readings = 0
            logger = get_hunt_logger()

            # Setup scene monster detection logic
            from lib.features.hunt.runtime_monster_queue import RuntimeMonsterQueue
            from lib.features.hunt.scene_monster_detector import SceneMonsterDetector

            # We need vision_engine. It's stored in self.bot_manager if available.
            # In a real app we'd pass this in clearly, but we'll try to extract it from bot_manager.
            runtime_queue = RuntimeMonsterQueue(publish_callback=None) # We don't have UX3B publish callback here
            scene_detector = None
            if hasattr(self, 'bot_manager') and self.bot_manager and hasattr(self.bot_manager, 'vision_engine'):
                scene_detector = SceneMonsterDetector(self.bot_manager.vision_engine, runtime_queue)

            self.runtime_queue = runtime_queue # expose for tests

            cached_target_id = None
            cached_target_name = None
            last_ocr_time = 0.0
            try:
                # Focus the target window; minimize GUI only if focus succeeded
                try:
                    focused = False
                    hunt_selected = self.get_hunt_selected()
                    if hunt_selected and hunt_selected.get("hwnd"):
                        focused = self.bring_window_to_front_by_hwnd(
                            int(hunt_selected["hwnd"])
                        )
                    elif cfg.get("window_pid"):
                        focused = self.bring_window_to_front_by_pid(
                            int(cfg["window_pid"])
                        )
                    if not focused:
                        focused = self.bring_window_to_front(
                            cfg.get("window_title", "Cabal")
                        )
                    if focused:
                        try:
                            self.iconify_app()
                        except Exception:
                            pass
                    time.sleep(0.15)
                except Exception:
                    pass

                logger.log_hunt_start(cfg)

                last_search = 0.0
                have_target = False
                mode = "search"
                last_seen = 0.0
                attack_started = 0.0
                lost_timeout = float(cfg.get("lost_timeout_sec", 0.8))
                attack_min_duration = float(cfg.get("attack_min_duration_sec", 1.5))
                skill_runtime = self.prepare_skill_runtime(cfg)
                has_attack_skills = any(
                    skill.get("type", "attack") != "buff" for skill in skill_runtime
                )
                last_match_info = None

                training_mode_active = cfg.get("training_mode_enabled", False)
                skill_stats = SkillStats() if training_mode_active else None
                last_stats_update = 0.0
                stats_update_interval = 0.5

                while self.hunt_running:
                    now = time.time()

                    # Periodic window validation
                    from lib.features.hunt.window_selection_service import validate_selected_cabal_window

                    hunt_selected = self.get_hunt_selected()
                    if hunt_selected:
                        validation = validate_selected_cabal_window(hunt_selected, [])
                        if not validation.is_valid:
                            logger.log_error("window_validation_failed", f"Validation failed: {validation.code}")
                            self.hunt_running = False
                            self.schedule_ui_task(lambda: self.on_state_change("error"))
                            break
                    if cfg.get("bring_to_front_each_cycle"):
                        ok = False
                        try:
                            hunt_selected = self.get_hunt_selected()
                            if hunt_selected and hunt_selected.get("hwnd"):
                                ok = self.bring_window_to_front_by_hwnd(
                                    int(hunt_selected["hwnd"])
                                )
                            elif cfg.get("window_hwnd"):
                                ok = self.bring_window_to_front_by_hwnd(
                                    int(cfg.get("window_hwnd"))
                                )
                            elif cfg.get("window_pid"):
                                ok = self.bring_window_to_front_by_pid(
                                    int(cfg.get("window_pid"))
                                )
                        except Exception:
                            ok = False

                    # Screen capture for this tick
                    frame = None
                    try:
                        if self.bot_manager and self.bot_manager.screen_capture:
                            if getattr(self.bot_manager.screen_capture, 'hwnd', None) != hunt_selected.get("hwnd"):
                                # Ensure we are capturing the right window
                                import win32gui
                                hwnd = int(hunt_selected.get("hwnd", 0))
                                if hwnd:
                                    title = win32gui.GetWindowText(hwnd)
                                    self.bot_manager.screen_capture.start(title)

                            frame = self.bot_manager.screen_capture.get_latest_frame()
                            if frame is not None:
                                frame = frame.copy()  # return a copy to readers
                    except Exception as e:
                        logger.log_error("vision_capture", f"Failed to capture frame: {e}")

                    # Process scene monsters
                    if frame is not None and scene_detector is not None:
                        scene_detector.process_frame(frame)

                    # Expose attack queue for other services (CB2C)
                    # Use 'configured_only' as default, pulling configured IDs from cfg
                    configured_ids = []
                    for m_entry in cfg.get("monster_rotation", []):
                        if isinstance(m_entry, dict) and "monster_id" in m_entry:
                            configured_ids.append(m_entry["monster_id"])
                        elif isinstance(m_entry, int):
                            configured_ids.append(m_entry)

                    target_policy = cfg.get("target_policy", "configured_only")
                    runtime_attack_queue = list(
                        runtime_queue.get_attack_queue(target_policy, configured_ids)
                    )
                    runtime_state_lock = getattr(self, "_runtime_state_lock", None)
                    if runtime_state_lock is None:
                        runtime_state_lock = threading.Lock()
                        self._runtime_state_lock = runtime_state_lock
                    with runtime_state_lock:
                        self.runtime_attack_queue = runtime_attack_queue

                    # Target detection logic using TargetBarDetector
                    if frame is not None:
                        is_alive = target_bar_detector.is_target_alive(frame)

                        if is_alive:
                            if not have_target or (now - last_ocr_time) > 2.0:
                                last_ocr_time = now
                                name_str = target_name_reader.read_name(frame)
                                if name_str:
                                    monster = find_monster_by_name_api(name_str, None)
                                    if not monster:
                                        monster = {"id": 0, "name": name_str, "hp": None}

                                    if cached_target_id != monster["id"] or cached_target_name != monster.get("name"):
                                        cached_target_id = monster["id"]
                                        cached_target_name = monster.get("name")
                                        m_id = monster.get("id", 0)
                                        m_name = monster.get("name", "Unknown")
                                        m_hp = monster.get("hp", "Unknown")
                                        fmt = f"[ID: #{m_id}] {m_name} (HP: {m_hp})"

                                        if getattr(self, 'set_target_info', None):
                                            self.schedule_ui_task(
                                                lambda text=fmt: self.set_target_info(text)
                                            )

                            have_target = True
                            last_seen = now
                            consecutive_false_readings = 0
                        else:
                            consecutive_false_readings += 1
                            if consecutive_false_readings >= int(cfg.get("target_lost_debounce_frames", 3)):
                                have_target = False
                                cached_target_id = None
                                cached_target_name = None
                                if getattr(self, 'clear_target_ui', None):
                                    self.schedule_ui_task(self.clear_target_ui)
                    else:
                        consecutive_false_readings += 1
                        if consecutive_false_readings >= int(cfg.get("target_lost_debounce_frames", 3)):
                            have_target = False
                            cached_target_id = None
                            cached_target_name = None
                            if getattr(self, 'clear_target_ui', None):
                                self.schedule_ui_task(self.clear_target_ui)

                    if (
                        skill_stats
                        and (now - last_stats_update) >= stats_update_interval
                    ):
                        try:
                            all_stats = skill_stats.get_all_stats()
                            self.schedule_ui_task(lambda stats=all_stats: self.update_skill_stats_display(stats))
                            last_stats_update = now
                        except Exception:
                            pass

                    if skill_runtime:
                        self.try_cast_skills(
                            skill_runtime,
                            now,
                            have_target,
                            attack_phase=False,
                            skill_stats=skill_stats,
                        )

                    if mode == "search":
                        if have_target:
                            logger.log_state_change("search", "attack", "target_found")
                            mode = "attack"
                            attack_started = now
                            continue

                        if not training_mode_active:
                            tap(cfg.get("target_key", "z"))
                            time.sleep(float(cfg.get("search_tap_delay_sec", 0.08)))
                        else:
                            time.sleep(0.1)
                        continue

                    # mode == 'attack'
                    if (
                        have_target
                        or (now - last_seen) <= lost_timeout
                    ):
                        target_active = (
                            have_target
                            or (now - last_seen) <= lost_timeout
                        )
                        if skill_runtime and has_attack_skills:
                            # DO NOT send target key in attack mode
                            # just call try_cast_skills
                            self.try_cast_skills(
                                skill_runtime,
                                now,
                                target_active,
                                attack_phase=True,
                                skill_stats=skill_stats,
                            )
                            if not target_active:
                                logger.log_state_change(
                                    "attack", "search", "lost_timeout"
                                )
                                mode = "search"
                                time.sleep(0.05)
                                continue
                            time.sleep(float(cfg.get("attack_interval", 0.2)))
                            continue

                        fallback_keys = [
                            s.get("key")
                            for s in cfg.get("skill_slots", [])
                            if s.get("key")
                        ]
                        if not fallback_keys:
                            fallback_keys = ["1"]
                        for k in fallback_keys:
                            if not self.hunt_running:
                                break
                            try:
                                tap(k, int(cfg.get("attack_press_ms", 100)))
                            except Exception:
                                pass
                            time.sleep(float(cfg.get("attack_interval", 0.2)))
                    else:
                        logger.log_state_change("attack", "search", "lost_timeout")
                        mode = "search"
                        time.sleep(0.05)
                    time.sleep(0.02)
            except Exception as e:
                logger.log_error("hunt_loop", f"Hunt error: {str(e)}", e)
                logger.log_hunt_stop("error")
                self.schedule_ui_task(lambda: self.on_state_change("error"))
            finally:
                try:
                    already_logged = bool(getattr(logger, "_stop_logged", False))
                except Exception:
                    already_logged = False
                if not already_logged:
                    logger.log_hunt_stop("manual_stop")
                    try:
                        setattr(logger, "_stop_logged", True)
                    except Exception:
                        pass
                self.hunt_running = False
                self.schedule_ui_task(lambda: self.on_state_change("idle"))

        self.hunt_thread = threading.Thread(target=worker, daemon=True)
        self.hunt_thread.start()

    def stop_hunt(self):
        self.hunt_running = False
