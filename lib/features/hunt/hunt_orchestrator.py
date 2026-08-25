import time
import threading
from pathlib import Path
from typing import Callable, Optional, Dict, Any

from lib.system.hunt_logger import get_hunt_logger
from lib.system.win_input import tap
from lib.features.skills.skill_stats import SkillStats

class HuntOrchestrator:
    def __init__(
        self,
        on_status_update: Callable[[str], None],
        on_state_change: Callable[[str], None], # "running", "idle", "error"
        locate_target: Callable[[Dict[str, Any]], tuple], # (box, match_info)
        prepare_skill_runtime: Callable[[Dict[str, Any]], list],
        try_cast_skills: Callable,
        bring_window_to_front: Callable[[str], bool],
        bring_window_to_front_by_hwnd: Callable[[int], bool],
        bring_window_to_front_by_pid: Callable[[int], bool],
        iconify_app: Callable[[], None],
        update_skill_stats_display: Callable[[dict], None],
        get_hunt_selected: Callable[[], Dict[str, Any]],
        schedule_ui_task: Callable[[Callable], None]
    ):
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
            logger = get_hunt_logger()
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
                    if cfg.get("bring_to_front_each_cycle"):
                        ok = False
                        try:
                            hunt_selected = self.get_hunt_selected()
                            if hunt_selected and hunt_selected.get("hwnd"):
                                ok = self.bring_window_to_front_by_hwnd(
                                    int(hunt_selected["hwnd"])
                                )
                            elif cfg.get("window_pid"):
                                ok = self.bring_window_to_front_by_pid(
                                    int(cfg.get("window_pid"))
                                )
                        except Exception:
                            ok = False
                        if not ok:
                            self.bring_window_to_front(
                                cfg.get("window_title", "Cabal")
                            )

                    # periodic detection with multi-template support
                    if now - last_search >= float(cfg.get("search_interval", 0.5)):
                        box, match_info = self.locate_target(cfg)
                        if box is not None:
                            have_target = True
                            last_seen = now
                            if match_info and last_match_info != match_info:
                                template_name = (
                                    match_info.get("name")
                                    or Path(match_info.get("path", "")).stem
                                )
                                threshold = match_info.get("threshold", 0.8)
                                confidence = match_info.get("confidence", 0.0)
                                monster_name = match_info.get("monster_name", "")
                                logger.log_match(
                                    template_name,
                                    box,
                                    threshold,
                                    confidence,
                                    monster_name,
                                )

                                status_msg = (
                                    f"Target: {template_name} (conf: {confidence:.3f})"
                                )
                                self.schedule_ui_task(lambda msg=status_msg: self.on_status_update(msg))
                                last_match_info = match_info
                        else:
                            have_target = False
                            if last_match_info:
                                duration = (
                                    now - attack_started if mode == "attack" else 0
                                )
                                template_name = (
                                    last_match_info.get("name")
                                    or Path(last_match_info.get("path", "")).stem
                                )
                                monster_name = last_match_info.get("monster_name", "")
                                logger.log_lost(template_name, monster_name, duration)

                                self.schedule_ui_task(lambda: self.on_state_change("running"))
                                last_match_info = None
                        last_search = now

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
                            time.sleep(float(cfg.get("target_cycle_delay", 0.1)))
                        else:
                            time.sleep(0.1)
                        continue

                    # mode == 'attack'
                    if (
                        have_target
                        or (now - last_seen) <= lost_timeout
                        or (now - attack_started) <= attack_min_duration
                    ):
                        target_active = (
                            have_target
                            or (now - last_seen) <= lost_timeout
                            or (now - attack_started) <= attack_min_duration
                        )
                        if skill_runtime and has_attack_skills:
                            if target_active:
                                tap(
                                    cfg.get("target_key", "z")
                                )
                                time.sleep(0.05)
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
