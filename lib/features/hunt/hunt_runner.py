from typing import Optional
from lib.system.win_input import tap
import pyautogui
import threading
import time
from tkinter import messagebox

from lib.vision.template_matcher import locate_template
from lib.vision.vision_engine import VisionEngine

try:
    from lib.system.screen_capture import ScreenCapture
except ImportError:
    ScreenCapture = None
from lib.features.skills.skill_stats import SkillStats
from lib.system.bot_manager import BotManager
from lib.system.hunt_logger import get_hunt_logger


class HuntRunner:
    def __init__(self, app, hunt_cfg):
        self.app = app
        self.hunt_cfg = hunt_cfg

        # State variables
        self.hunt_running = False
        self.hunt_thread = None
        self.hunt_stop_event = threading.Event()
        self.hunt_status = app.hunt_status
        self.hunt_target_info = app.hunt_target_info

        # Vision engine
        self.vision_engine = VisionEngine()

        # Bot manager (handles screen scanning and logic state)
        self.bot_manager = BotManager(self.vision_engine, ScreenCapture)

        # UI mode for features
        self.ui_mode = hunt_cfg.get("ui_mode", "beginner")

    def _validate_hunt_prerequisites(self) -> str:
        """Validate all required conditions before starting a hunt.
        Returns error message string if validation fails, None otherwise."""
        # 1. Window checks
        win_title = self.hunt_cfg.get("hunt_area", {}).get("window_title")
        if not win_title:
            return "Please select a target window in Setup tab first."

        # Sprint 21 Phase 3: Defensive check for window existence
        from lib.system.window_manager import find_window_by_title

        hwnd = find_window_by_title(win_title)
        if not hwnd:
            return f"Cannot find window: '{win_title}'. Please ensure the game/application is running."

        # Bring window to front automatically before validating bounds
        try:
            import ctypes

            ctypes.windll.user32.SetForegroundWindow(hwnd)
            time.sleep(0.1)  # small delay for window manager
        except Exception as e:
            print(f"[Hunt] Warning: Could not bring window to front: {e}")

        # 2. Check bounds
        bounds = self.hunt_cfg.get("hunt_area", {}).get("window_bounds")
        if not bounds or not isinstance(bounds, list) or len(bounds) != 4:
            return "Invalid hunt area bounds. Please reset them in Setup tab."

        # 3. Target (Monster) Selection Checks
        monster_rot = self.hunt_cfg.get("monster_rotation", [])
        if not monster_rot:
            return "No target selected. Please select at least one monster in the Hunt tab."

        return None

    def on_hunt_start(self):
        if self.hunt_running:
            return

        err = self._validate_hunt_prerequisites()
        if err:
            if hasattr(self.app, "notebook"):
                self.app.notebook.select(
                    self.app.tab_setup if "window" in err.lower() else self.app.tab_hunt
                )
            messagebox.showwarning("Cannot Start Hunt", err, parent=self.app)
            return

        self.hunt_running = True
        self.hunt_stop_event.clear()

        # Disable UI
        if hasattr(self.app, "btn_start"):
            self.app.btn_start.config(state="disabled")
        if hasattr(self.app, "btn_stop"):
            self.app.btn_stop.config(state="normal")
        self.hunt_status.set("Starting hunt...")
        self.hunt_target_info.set("Target: None")

        # Overlay integration
        if (
            hasattr(self.app, "overlay_ctrl")
            and self.app.overlay_ctrl
            and self.app.overlay_ctrl.is_overlay_active()
        ):
            self.app.overlay_ctrl.set_status("Hunting...")
            self.app.overlay_ctrl.set_mode_indicator(True)
            self.app.overlay_ctrl.clear_target()

        self._prepare_skill_runtime()
        logger = get_hunt_logger()
        logger.log_info(f"Hunt started (Mode: {self.ui_mode})")

        def worker():
            win_title = self.hunt_cfg.get("hunt_area", {}).get("window_title")
            from lib.system.window_manager import find_window_by_title

            while self.hunt_running and not self.hunt_stop_event.is_set():
                try:
                    # Defensive check: Ensure window still exists
                    hwnd = find_window_by_title(win_title)
                    if not hwnd:
                        logger.log_warning(
                            f"Target window '{win_title}' lost. Pausing bot."
                        )
                        self._update_status("Window Lost - Waiting...")
                        if hasattr(self.app, "overlay_ctrl") and self.app.overlay_ctrl:
                            self.app.overlay_ctrl.set_status("Window Lost")
                            self.app.overlay_ctrl.clear_target()
                        time.sleep(2.0)
                        continue

                    bounds = self.hunt_cfg.get("hunt_area", {}).get("window_bounds")

                    target_pt, score, name = self._hunt_locate_target()

                    if target_pt:
                        if self.ui_mode in ["intermediate", "advanced"]:
                            self.hunt_status.set(
                                f"Attacking: {name} ({score*100:.0f}%)"
                            )
                        else:
                            self.hunt_status.set(f"Attacking: {name}")

                        # Update overlay if active
                        if (
                            hasattr(self.app, "overlay_ctrl")
                            and self.app.overlay_ctrl
                            and self.app.overlay_ctrl.is_overlay_active()
                        ):
                            self.app.overlay_ctrl.set_status(f"Attacking {name}")
                            # Target point is relative to the bounds.
                            # The overlay handles translation internally when given screen coordinates
                            screen_x = bounds[0] + target_pt[0]
                            screen_y = bounds[1] + target_pt[1]
                            self.app.overlay_ctrl.draw_target_box(screen_x, screen_y)

                        # Attack Sequence
                        click_cfg = self.app.cfg.get("click", {})

                        # Apply jitter to coordinates to avoid detection
                        jitter_x = (
                            target_pt[0]
                            + bounds[0]
                            + int(click_cfg.get("jitter", 3) * (time.time() % 1 - 0.5))
                        )
                        jitter_y = (
                            target_pt[1]
                            + bounds[1]
                            + int(click_cfg.get("jitter", 3) * (time.time() % 1 - 0.5))
                        )

                        logger.log_info(f"Clicking target at ({jitter_x}, {jitter_y})")
                        try:
                            # 1. Select Target (Mouse Click)
                            if pyautogui is not None:
                                pyautogui.click(x=jitter_x, y=jitter_y)
                            else:
                                import ctypes
                                ctypes.windll.user32.SetCursorPos(int(jitter_x), int(jitter_y))
                                ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
                                time.sleep(0.05)
                                ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)

                            # 2. Wait for target selection to register
                            delay = click_cfg.get("delay_after_click", 0.5)
                            time.sleep(delay)

                            # 3. Cast Skills Loop
                            skills_cfg = self.hunt_cfg.get("skills", {})
                            cast_duration = float(
                                click_cfg.get("cast_duration_sec", 3.0)
                            )
                            start_time = time.time()

                            logger.log_info(
                                f"Starting attack cycle ({cast_duration}s)..."
                            )
                            while (
                                time.time() - start_time < cast_duration
                                and not self.hunt_stop_event.is_set()
                            ):
                                # Try casting skills based on priority and cooldown
                                cast_count = self._try_cast_skills(skills_cfg)

                                # Break if no skills were cast (all on cooldown)
                                if cast_count == 0:
                                    # Wait a short bit before trying again
                                    time.sleep(0.1)

                        except Exception as e:
                            print(f"Error clicking target: {e}")
                            logger.log_error(f"Attack cycle error: {e}")

                        # Wait before next scan
                        time.sleep(click_cfg.get("interval_sec", 2.0))
                    else:
                        self.hunt_status.set("Searching...")
                        if (
                            hasattr(self.app, "overlay_ctrl")
                            and self.app.overlay_ctrl
                            and self.app.overlay_ctrl.is_overlay_active()
                        ):
                            self.app.overlay_ctrl.set_status("Searching...")
                            self.app.overlay_ctrl.clear_target()

                        # Move randomly if enabled
                        options = self.hunt_cfg.get("options", {})
                        if options.get("random_movement", False):
                            # TODO: Implement random movement logic
                            pass

                        time.sleep(0.5)
                except Exception as e:
                    print(f"Error in hunt worker loop: {e}")
                    time.sleep(1.0)

            # Clean up on exit
            if hasattr(self.app, "overlay_ctrl") and self.app.overlay_ctrl:
                self.app.overlay_ctrl.set_mode_indicator(False)
                self.app.overlay_ctrl.clear_target()

            self.app.after(0, self._on_hunt_worker_finished)

        self.hunt_thread = threading.Thread(target=worker, daemon=True)
        self.hunt_thread.start()

    def on_hunt_stop(self):
        if not self.hunt_running:
            return

        self.hunt_stop_event.set()
        self.hunt_running = False

        logger = get_hunt_logger()
        logger.log_info("Hunt stopped")

        # Reset UI
        self.hunt_status.set("Stopped")
        self.hunt_target_info.set("Target: None")

        if hasattr(self.app, "btn_start"):
            self.app.btn_start.config(state="normal")
        if hasattr(self.app, "btn_stop"):
            self.app.btn_stop.config(state="disabled")

        if (
            hasattr(self.app, "overlay_ctrl")
            and self.app.overlay_ctrl
            and self.app.overlay_ctrl.is_overlay_active()
        ):
            self.app.overlay_ctrl.set_status("Idle")
            self.app.overlay_ctrl.set_mode_indicator(False)
            self.app.overlay_ctrl.clear_target()

    def _on_hunt_worker_finished(self):
        self.hunt_running = False
        if hasattr(self.app, "btn_start"):
            self.app.btn_start.config(state="normal")
        if hasattr(self.app, "btn_stop"):
            self.app.btn_stop.config(state="disabled")
        self.hunt_status.set("Stopped")

    def _hunt_locate_target(self):
        """Locates a target based on the current configuration."""
        cfg = self.hunt_cfg
        bounds = cfg.get("hunt_area", {}).get("window_bounds")
        if not bounds:
            return None, 0, ""

        if ScreenCapture is None:
            print("ScreenCapture unavailable, returning mock target.")
            return (int(bounds[2] / 2), int(bounds[3] / 2)), 1.0, "Mock Target"

        # Capture region
        screenshot = ScreenCapture.capture_region(
            bounds[0], bounds[1], bounds[2], bounds[3]
        )
        if screenshot is None:
            return None, 0, ""

        best_pt = None
        best_val = -1
        best_name = ""

        # Try fast vision pipeline first
        try:
            # Look for target HUD directly if enabled
            if cfg.get("options", {}).get("fast_hud_detection", True):
                from lib.vision.matcher_service import MatcherService

                matcher = MatcherService(use_grayscale=False)
                # Implement HUD detection here (e.g. detect red health bar)
                # For now, fallback to template matching
                pass
        except Exception as e:
            print(f"Fast pipeline error: {e}")

        # Fallback to template matching
        rotation_ids = cfg.get("monster_rotation", [])
        from lib.features.monsters.monster_repo import load_monster_library

        monster_lib = load_monster_library()

        for m_id in rotation_ids:
            monster = monster_lib.get(m_id)
            if not monster:
                continue

            # Find best match for this monster's templates
            templates = monster.get("templates", [])
            for tmpl in templates:
                if not isinstance(tmpl, dict):
                    continue
                path = tmpl.get("path")
                if not path:
                    continue

                box, val = locate_template(path, region=tuple(bounds), threshold=0.7)
                if box and val > best_val:
                    left, top, w, h = box
                    best_val = val
                    best_pt = (
                        int(left - bounds[0] + w / 2),
                        int(top - bounds[1] + h / 2),
                    )
                    best_name = monster.get("name", m_id)
        if best_pt:
            return best_pt, best_val, best_name
        return None, 0, ""

    def _prepare_skill_runtime(self):
        """Prepares skill tracking objects for the hunt."""
        skills_cfg = self.hunt_cfg.get("skills", {})
        from lib.features.skills.skill_repo import load_skill_library

        skill_lib = load_skill_library()

        # Initialize skill tracking runtime variables
        self.skill_runtime = {}

        # Default global cooldown
        self.global_cooldown = 1.0

        for slot_id, slot_data in skills_cfg.items():
            if not isinstance(slot_data, dict):
                continue

            skill_id = slot_data.get("id")
            if not skill_id:
                continue

            # Load skill properties
            skill_def = skill_lib.get(skill_id, {})

            # Prepare runtime entry
            self.skill_runtime[slot_id] = {
                "id": skill_id,
                "name": skill_def.get("name", skill_id),
                "key": slot_data.get("key", slot_id),
                "cast_time": float(skill_def.get("cast_time", 1.0)),
                "cooldown": float(skill_def.get("cooldown", 2.0)),
                "type": skill_def.get("type", "attack"),
                "last_cast": 0.0,
            }

            # Reset stats
            SkillStats.reset_stats(slot_id)

    def _try_cast_skills(self, skills_cfg):
        """Attempts to cast available skills based on cooldowns. Returns number of skills cast."""

        cast_count = 0
        now = time.time()

        # Sort slots by priority if available, otherwise by slot ID
        slots = sorted(list(self.skill_runtime.keys()))

        for slot_id in slots:
            runtime = self.skill_runtime[slot_id]
            if now - runtime["last_cast"] >= runtime["cooldown"]:
                key = runtime["key"]
                cast_success = False

                try:
                    tap(key, 60)
                    cast_success = True
                except Exception:
                    try:
                        import keyboard
                        keyboard.press_and_release(key.lower())
                        cast_success = True
                    except (ImportError, Exception):
                        cast_success = False

                if cast_success:
                    cast_count += 1
                    runtime["last_cast"] = time.time()
                    from lib.features.skills.skill_stats import SkillStats
                    SkillStats.record_cast(slot_id, success=True, time_taken=0.1)
                    time.sleep(runtime["cast_time"])
                    break
        return cast_count
