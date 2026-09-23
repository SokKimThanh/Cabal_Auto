
from lib.events.event_bus import EventBus, SceneMonstersDetectedEvent
from lib.vision.target_bar_detector import TargetBarDetector
from lib.events.event_bus import (
    EventBus,
    HuntStatusUpdatedEvent,
    HuntStateChangedEvent,
    TargetHpUpdatedEvent,
    TargetStatusUpdatedEvent,
    TargetInfoUpdatedEvent,
    ClearTargetUIEvent,
    SkillStatsUpdatedEvent
)

import time
import threading
from pathlib import Path
from typing import Callable, Dict, Any

from lib.system.hunt_logger import get_hunt_logger
from lib.system.win_input import tap as global_tap
from lib.features.skills.skill_stats import SkillStats
from lib.system.input_backend import (
    InputBackend,
    ForegroundSendInputBackend,
    BackgroundWindowMessageBackend,
)
from lib.system.input_capability import InputCapabilityManager, InputCapabilityState
from lib.vision.target_name_reader import TargetNameReader
from database import find_monster_by_name_api
from lib.i18n import t


class HuntOrchestrator:
    def __init__(
        self,
        locate_target: Callable[[Dict[str, Any]], tuple],  # (box, match_info)
        prepare_skill_runtime: Callable[[Dict[str, Any]], list],
        try_cast_skills: Callable,
        bring_window_to_front: Callable[[str], bool],
        bring_window_to_front_by_hwnd: Callable[[int], bool],
        bring_window_to_front_by_pid: Callable[[int], bool],
        iconify_app: Callable[[], None],
        get_hunt_selected: Callable[[], Dict[str, Any]],
        on_scene_monsters_detected: Callable[[tuple], None] = None,
    ):
        self.on_scene_monsters_detected = on_scene_monsters_detected
        self.locate_target = locate_target
        self.prepare_skill_runtime = prepare_skill_runtime
        self.try_cast_skills = try_cast_skills
        self.bring_window_to_front = bring_window_to_front
        self.bring_window_to_front_by_hwnd = bring_window_to_front_by_hwnd
        self.bring_window_to_front_by_pid = bring_window_to_front_by_pid
        self.iconify_app = iconify_app
        self.get_hunt_selected = get_hunt_selected

        self.hunt_running = False
        self.hunt_thread = None
        self.input_backend = None
        self.input_capability_manager = None
        self.input_mode = "foreground"
        self.background_input_fallback = False

    def start_hunt(self, cfg: Dict[str, Any]):
        if self.hunt_running:
            return

        self.input_mode = cfg.get("input_mode", "foreground")
        fb = cfg.get("background_input_fallback", "stop")
        # Handle both boolean True/False and string values
        self.background_input_fallback = (
            True if fb in (True, "foreground", "true") else False
        )

        logger = get_hunt_logger()
        hunt_selected = self.get_hunt_selected()
        hwnd = int(hunt_selected.get("hwnd", 0)) if hunt_selected else 0

        self.input_backend = None
        self.input_capability_manager = None

        if self.input_mode == "background":
            if not hwnd:
                if not self.background_input_fallback:
                    logger.log_error(
                        "input_capability",
                        "Background mode requested but no HWND found. Stopped.",
                    )
                    EventBus.trigger(HuntStatusUpdatedEvent(t('hunt_status.error_bg_unsupported', default='Error: Background input unsupported (no HWND). Stopped.')))
                    EventBus.trigger(HuntStateChangedEvent("error"))
                    return
                else:
                    logger.log_error(
                        "input_capability",
                        "No HWND found. Falling back to foreground input.",
                    )
                    self.input_backend = ForegroundSendInputBackend()
            else:
                self.input_capability_manager = InputCapabilityManager(
                    hwnd, self.input_mode, logger
                )
                state, is_ready = (
                    self.input_capability_manager.check_and_verify_capability()
                )

                if not is_ready:
                    if not self.background_input_fallback:
                        logger.log_error(
                            "input_capability",
                            f"Background input capability is {state.value}. Fallback disabled. Hunt aborted.",
                        )
                        EventBus.trigger(HuntStatusUpdatedEvent(
                                t('hunt_status.error_bg_state', default=f"Error: Background input {state.value}. Stopped.", state=state.value)
                            ))
                        EventBus.trigger(HuntStateChangedEvent("error"))
                        return
                    else:
                        logger.log_error(
                            "input_capability",
                            f"Background input {state.value}. Falling back to foreground.",
                        )
                        self.input_backend = ForegroundSendInputBackend()
                else:
                    self.input_backend = BackgroundWindowMessageBackend(hwnd)
        else:
            self.input_backend = ForegroundSendInputBackend()

        self.hunt_running = True
        EventBus.trigger(HuntStateChangedEvent("running"))

        def worker():

            hunt_selected = self.get_hunt_selected()
            hwnd = int(hunt_selected.get("hwnd", 0)) if hunt_selected else None

            target_bar_detector = TargetBarDetector(hwnd=hwnd)
            target_name_reader = TargetNameReader(hwnd=hwnd)
            from lib.vision.target_hp_reader import TargetHPReader

            target_hp_reader = TargetHPReader(target_bar_detector)
            consecutive_false_readings = 0
            logger = get_hunt_logger()

            # Setup scene monster detection logic
            from lib.features.hunt.runtime_monster_queue import RuntimeMonsterQueue
            from lib.features.hunt.scene_monster_detector import SceneMonsterDetector
            from lib.features.hunt.target_rotation_coordinator import (
                TargetRotationCoordinator,
            )

            # We need vision_engine. It's stored in self.bot_manager if available.
            # In a real app we'd pass this in clearly, but we'll try to extract it from bot_manager.
            def safe_publish(snapshot):
                # Remove raw frame to prevent Memory Thrashing over EventBus
                clean_snapshot = snapshot.copy() if isinstance(snapshot, dict) else snapshot
                if isinstance(clean_snapshot, dict) and "frame" in clean_snapshot:
                    del clean_snapshot["frame"]
                EventBus.trigger(SceneMonstersDetectedEvent(clean_snapshot))

            runtime_queue = RuntimeMonsterQueue(
                publish_callback=safe_publish
            )
            scene_detector = None
            if (
                hasattr(self, "bot_manager")
                and self.bot_manager
                and hasattr(self.bot_manager, "vision_engine")
            ):
                scene_detector = SceneMonsterDetector(
                    self.bot_manager.vision_engine, runtime_queue
                )

            self.runtime_queue = runtime_queue  # expose for tests

            target_policy = cfg.get("target_policy", "configured_only")
            target_coordinator = TargetRotationCoordinator(
                target_policy, cfg.get("monster_rotation", [])
            )

            # Check if start is valid
            if not target_coordinator.is_rotation_valid():
                logger.log_error(
                    "hunt_loop", "Invalid rotation or empty rotation for policy."
                )
                EventBus.trigger(HuntStatusUpdatedEvent(
                        t('hunt_status.error_invalid_rotation', default="Error: Invalid rotation or empty rotation for policy.")
                    ))
                self.hunt_running = False
                EventBus.trigger(HuntStateChangedEvent("error"))
                return

            cycle_attempts = 0
            last_cycle_time = 0.0
            target_cycle_min_interval_sec = float(
                cfg.get("target_cycle_min_interval_sec", 0.20)
            )
            target_cycle_max_attempts = int(cfg.get("target_cycle_max_attempts", 20))
            target_death_confirm_sec = float(cfg.get("target_death_confirm_sec", 0.35))
            target_acquire_timeout_sec = float(
                cfg.get("target_acquire_timeout_sec", 8.0)
            )
            death_confirm_started = 0.0
            death_confirm_mode = False
            last_ocr_time = 0.0
            search_started = time.time()
            cached_target_id = None
            cached_target_name = None

            try:
                # Focus the target window; minimize GUI only if focus succeeded
                if getattr(self.input_backend, "mode", "foreground") != "background":
                    try:
                        focused = False
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
                    from lib.features.hunt.window_selection_service import (
                        validate_selected_cabal_window,
                    )

                    hunt_selected = self.get_hunt_selected()
                    if hunt_selected:
                        validation = validate_selected_cabal_window(hunt_selected, [])
                        if not validation.is_valid:
                            logger.log_error(
                                "window_validation_failed",
                                f"Validation failed: {validation.code}",
                            )
                            self.hunt_running = False
                            EventBus.trigger(HuntStateChangedEvent("error"))
                            break
                    if (
                        cfg.get("bring_to_front_each_cycle")
                        and getattr(self.input_backend, "mode", "foreground")
                        != "background"
                    ):
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
                            if getattr(
                                self.bot_manager.screen_capture, "hwnd", None
                            ) != hunt_selected.get("hwnd"):
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
                        logger.log_error(
                            "vision_capture", f"Failed to capture frame: {e}"
                        )

                    # Process scene monsters
                    if frame is not None and scene_detector is not None:
                        scene_detector.process_frame(frame)
                        runtime_queue.maybe_publish(lambda func: EventBus.trigger(Event()))

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
                            if not have_target:
                                target_hp_reader.reset()
                            # Update HP
                            hp_percent = target_hp_reader.calculate_target_hp_percent(
                                frame
                            )
                            EventBus.trigger(TargetHpUpdatedEvent(hp_percent))

                            if mode == "search":
                                EventBus.trigger(TargetStatusUpdatedEvent("APPROACHING"))
                            elif mode == "attack":
                                EventBus.trigger(TargetStatusUpdatedEvent("ATTACKING"))

                            if not have_target or (now - last_ocr_time) > 2.0:
                                last_ocr_time = now
                                name_str = target_name_reader.read_name(frame)
                                if name_str:
                                    desired = target_coordinator.get_desired_target()
                                    dungeon_id = (
                                        desired.get("dungeon_id") if desired else None
                                    )
                                    monster = find_monster_by_name_api(
                                        name_str, dungeon_id
                                    )
                                    if not monster:
                                        monster = {
                                            "id": 0,
                                            "name": name_str,
                                            "hp": None,
                                            "defense": None,
                                        }

                                    if cached_target_id != monster[
                                        "id"
                                    ] or cached_target_name != monster.get("name"):
                                        cached_target_id = monster["id"]
                                        cached_target_name = monster.get("name")
                                        m_id = monster.get("id", 0)
                                        m_name = monster.get("name", "Unknown")
                                        m_hp = monster.get("hp", "Unknown")
                                        fmt = f"[ID: #{m_id}] {m_name} (HP: {m_hp})"

                                        EventBus.trigger(TargetInfoUpdatedEvent(fmt, target_id=m_id, name=m_name, hp=str(m_hp)))

                            have_target = True
                            last_seen = now
                            consecutive_false_readings = 0
                        else:
                            consecutive_false_readings += 1
                            if consecutive_false_readings >= int(
                                cfg.get("target_lost_debounce_frames", 3)
                            ):
                                have_target = False
                                cached_target_id = None
                                cached_target_name = None
                                EventBus.trigger(ClearTargetUIEvent())
                    else:
                        consecutive_false_readings += 1
                        if consecutive_false_readings >= int(
                            cfg.get("target_lost_debounce_frames", 3)
                        ):
                            have_target = False
                            cached_target_id = None
                            cached_target_name = None
                            EventBus.trigger(ClearTargetUIEvent())

                    if hasattr(self, "runtime_attack_queue"):
                        target_coordinator.update_runtime_queue(
                            self.runtime_attack_queue
                        )
                    if (
                        skill_stats
                        and (now - last_stats_update) >= stats_update_interval
                    ):
                        try:
                            all_stats = skill_stats.get_all_stats()
                            EventBus.trigger(SkillStatsUpdatedEvent(all_stats))
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
                            backend=self.input_backend,
                        )

                    if mode == "search":
                        if (now - search_started) > target_acquire_timeout_sec:
                            logger.log_error(
                                "hunt_loop",
                                f"Target acquire timeout ({target_acquire_timeout_sec}s). Backing off.",
                            )
                            EventBus.trigger(HuntStatusUpdatedEvent(
                                    t('hunt_status.target_acquire_timeout', default="Target acquire timeout. Retrying...")
                                ))
                            search_started = now
                            backoff_wait = 1.0
                            while backoff_wait > 0 and self.hunt_running:
                                time.sleep(0.1)
                                backoff_wait -= 0.1
                            continue

                        if have_target:
                            eval_result = target_coordinator.evaluate_target(
                                cached_target_id, have_target
                            )
                            if eval_result == TargetRotationCoordinator.MATCHED:
                                logger.log_state_change(
                                    "search",
                                    "attack",
                                    f"target_found MATCHED {cached_target_id}",
                                )
                                mode = "attack"
                                attack_started = now
                                cycle_attempts = 0
                                search_started = now
                                death_confirm_mode = False
                                continue
                            elif eval_result in (
                                TargetRotationCoordinator.MISMATCH,
                                TargetRotationCoordinator.UNKNOWN,
                            ):
                                # CYCLE_TARGET
                                if (
                                    not training_mode_active
                                    and (now - last_cycle_time)
                                    >= target_cycle_min_interval_sec
                                ):
                                    logger.log_info(
                                        f"Target decision: {eval_result} for ID {cached_target_id}"
                                    )
                                    if cycle_attempts >= target_cycle_max_attempts:
                                        logger.log_error(
                                            "hunt_loop",
                                            f"Max cycle attempts reached ({target_cycle_max_attempts}). Backing off.",
                                        )
                                        EventBus.trigger(HuntStatusUpdatedEvent(t('hunt_status.max_cycle_attempts', default=f"Max cycle attempts ({target_cycle_max_attempts}). Retrying...", max_attempts=target_cycle_max_attempts)))
                                        backoff_wait = 1.0
                                        while backoff_wait > 0 and self.hunt_running:
                                            time.sleep(0.1)
                                            backoff_wait -= 0.1
                                        cycle_attempts = 0
                                        last_cycle_time = now
                                    else:
                                        if self.input_backend:
                                            self.input_backend.tap(
                                                cfg.get("target_key", "z")
                                            )
                                        else:
                                            global_tap(cfg.get("target_key", "z"))
                                        last_cycle_time = now
                                        cycle_attempts += 1
                                        time.sleep(
                                            float(cfg.get("search_tap_delay_sec", 0.08))
                                        )
                                continue

                        if not training_mode_active:
                            if (now - last_cycle_time) >= target_cycle_min_interval_sec:
                                if self.input_backend:
                                    self.input_backend.tap(cfg.get("target_key", "z"))
                                else:
                                    global_tap(cfg.get("target_key", "z"))
                                last_cycle_time = now
                                time.sleep(float(cfg.get("search_tap_delay_sec", 0.08)))
                        else:
                            time.sleep(0.1)
                        continue

                    # mode == 'attack'
                    if have_target:
                        target_active = True
                        death_confirm_mode = False
                    else:
                        if not death_confirm_mode:
                            death_confirm_mode = True
                            death_confirm_started = now
                            target_active = True
                        else:
                            if (
                                now - death_confirm_started
                            ) <= target_death_confirm_sec:
                                target_active = True
                            else:
                                target_active = False

                    if target_active:
                        if skill_runtime and has_attack_skills:
                            # DO NOT send target key in attack mode
                            # just call try_cast_skills
                            self.try_cast_skills(
                                skill_runtime,
                                now,
                                target_active,
                                attack_phase=True,
                                skill_stats=skill_stats,
                                backend=self.input_backend,
                            )
                            if not cfg.get("combo", {}).get("enabled", False):
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
                                if self.input_backend:
                                    self.input_backend.tap(
                                        k, int(cfg.get("attack_press_ms", 100))
                                    )
                                else:
                                    global_tap(k, int(cfg.get("attack_press_ms", 100)))
                            except Exception:
                                pass
                            time.sleep(float(cfg.get("attack_interval", 0.2)))
                    else:
                        # ADVANCE_ROTATION
                        prev_target = target_coordinator.advance_pointer()
                        next_target = target_coordinator.get_desired_target()
                        logger.log_state_change(
                            "attack",
                            "search",
                            f"target dead/lost. Advanced {prev_target} -> {next_target}",
                        )
                        mode = "search"
                        search_started = now

                        EventBus.trigger(TargetStatusUpdatedEvent("TARGET_DEAD"))
                        EventBus.trigger(TargetHpUpdatedEvent(0.0))

                        # Clear UI cache on advance
                        cached_target_id = None
                        cached_target_name = None

                        # 0.2s delay for clear target ui
                        if getattr(self, "clear_target_ui", None):
                            # Schedule a delayed clear; fall back to no-arg callback if delay is unsupported.
                            def _safe_clear():
                                try:
                                    self.clear_target_ui(delay_ms=200)
                                except TypeError:
                                    self.clear_target_ui()

                            EventBus.trigger(ClearTargetUIEvent())

                        time.sleep(0.05)
                    time.sleep(0.02)
            except Exception as e:
                logger.log_error("hunt_loop", f"Hunt error: {str(e)}", e)
                logger.log_hunt_stop("error")
                EventBus.trigger(HuntStateChangedEvent("error"))
            finally:
                if getattr(self, "input_backend", None):
                    try:
                        self.input_backend.close()
                    except Exception:
                        pass

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
                EventBus.trigger(HuntStateChangedEvent("idle"))

        self.hunt_thread = threading.Thread(target=worker, daemon=True)
        self.hunt_thread.start()

    def stop_hunt(self):
        self.hunt_running = False
