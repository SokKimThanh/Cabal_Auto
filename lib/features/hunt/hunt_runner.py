import time
import threading

try:
    import pyautogui
except Exception:
    pyautogui = None

from tkinter import messagebox
from lib.vision.template_matcher import locate_template
from lib.vision.vision_engine import VisionEngine

try:
    from lib.system.screen_capture import ScreenCapture
except ImportError:
    ScreenCapture = None
from lib.system.win_input import tap
from lib.system.bot_manager import BotManager
from lib.features.skills.skill_stats import SkillStats
from lib.system.hunt_logger import get_hunt_logger


class HuntRunner:
    def __init__(
        self,
        hunt_cfg: dict,
        set_status: callable,
        set_target_info: callable,
        get_overlay_ctrl: callable,
        get_notebook: callable,
        tab_setup,
        tab_hunt,
        schedule_ui_task: callable
    ):
        self.hunt_cfg = hunt_cfg
        self.set_status = set_status
        self.set_target_info = set_target_info
        self.get_overlay_ctrl = get_overlay_ctrl
        self.get_notebook = get_notebook
        self.tab_setup = tab_setup
        self.tab_hunt = tab_hunt
        self.schedule_ui_task = schedule_ui_task

        # Vision engine
        self.vision_engine = VisionEngine()

        # Bot manager (handles screen scanning and logic state)
        self.screen_capture = ScreenCapture() if ScreenCapture is not None else None
        self.bot_manager = BotManager(
            vision_engine=self.vision_engine, screen_capture=self.screen_capture
        )

        # UI mode for features
        self.ui_mode = hunt_cfg.get("ui_mode", "beginner")

    def _validate_hunt_prerequisites(self) -> str:
        """Validate all required conditions before starting a hunt.
        Returns error message string if validation fails, None otherwise."""
        from lib.features.hunt.config_validator import get_valid_hunt_area

        safe_area = get_valid_hunt_area(self.hunt_cfg)

        # 1. Window checks
        win_title = safe_area.get("window_title")
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
        bounds = safe_area.get("window_bounds")
        if bounds is None:
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
            notebook = self.get_notebook()
            if notebook:
                notebook.select(self.tab_setup if "window" in err.lower() else self.tab_hunt)
            messagebox.showwarning("Cannot Start Hunt", err, parent=None)
            return

        self.hunt_running = True
        self.hunt_stop_event.clear()

        self.schedule_ui_task(lambda: self.set_status("Starting hunt..."))
        self.schedule_ui_task(lambda: self.set_target_info("Target: None"))

        # Overlay integration
        overlay_ctrl = self.get_overlay_ctrl()
        if overlay_ctrl and overlay_ctrl.is_overlay_active():
            overlay_ctrl.set_status("Hunting...")
            overlay_ctrl.set_mode_indicator(True)
            overlay_ctrl.clear_target()

        self._prepare_skill_runtime()
        logger = get_hunt_logger()
        logger.log_info(f"Hunt started (Mode: {self.ui_mode})")


    def on_hunt_stop(self):
        if not self.hunt_running:
            return

        self.hunt_stop_event.set()
        self.hunt_running = False

        logger = get_hunt_logger()
        logger.log_info("Hunt stopped")

        # Reset UI
        self.hunt_status.set("Stopped")
        self.schedule_ui_task(lambda: self.set_target_info("Target: None"))


        overlay_ctrl = self.get_overlay_ctrl()
        if overlay_ctrl and overlay_ctrl.is_overlay_active():
            overlay_ctrl.set_status("Idle")
            overlay_ctrl.set_mode_indicator(False)
            overlay_ctrl.clear_target()

    def _on_hunt_worker_finished(self):
        self.hunt_running = False
        self.hunt_status.set("Stopped")

    def _hunt_locate_target(self):
        """Locates a target based on the current configuration."""
        from lib.features.hunt.config_validator import get_valid_hunt_area

        cfg = self.hunt_cfg
        safe_area = get_valid_hunt_area(cfg)
        bounds = safe_area.get("window_bounds")
        if not bounds:
            return None, 0, ""

        if ScreenCapture is None:
            print("[HuntRunner] ScreenCapture unavailable; cannot locate targets.")
            return None, 0, ""

        best_pt = None
        best_val = -1
        best_name = ""

        # Try fast vision pipeline first
        try:
            # Look for target HUD directly if enabled
            if cfg.get("options", {}).get("fast_hud_detection", True):
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

    def _update_status(self, text: str) -> None:
        self.schedule_ui_task(lambda: self.set_status(text))
