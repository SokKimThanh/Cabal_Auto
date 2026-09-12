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
        schedule_ui_task: callable,
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

    def _hunt_locate_target(self):
        """Locates a target based on the current configuration."""
        from lib.features.hunt.target_locator import TargetLocatorService
        from lib.features.hunt.config_validator import get_valid_hunt_area

        cfg = self.hunt_cfg
        safe_area = get_valid_hunt_area(cfg)
        bounds = safe_area.get("window_bounds")
        if not bounds:
            return None, 0, ""

        if ScreenCapture is None:
            print("[HuntRunner] ScreenCapture unavailable; cannot locate targets.")
            return None, 0, ""

        box, info = TargetLocatorService.locate_target(cfg, current_window_bounds=bounds)
        if box and info:
            left, top, w, h = box
            best_pt = (
                int(left - bounds[0] + w / 2),
                int(top - bounds[1] + h / 2),
            )
            best_val = info.get("confidence", 0)
            best_name = info.get("monster_name", info.get("name", ""))
            return best_pt, best_val, best_name



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
        rotation = cfg.get("monster_rotation", [])
        from lib.features.monsters.monster_repo import load_monster_library

        monster_lib = load_monster_library()

        for m_entry in rotation:
            m_id = m_entry.get("monster_id") if isinstance(m_entry, dict) else m_entry
            monster = monster_lib.get(str(m_id))
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

    def _update_status(self, text: str) -> None:
        self.schedule_ui_task(lambda: self.set_status(text))
