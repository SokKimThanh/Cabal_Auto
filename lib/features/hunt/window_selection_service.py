import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from lib.features.hunt.config_validator import normalize_window_bounds_value
from lib.system.window_manager import WindowManager
from lib.i18n import t as i18n_t
from lib.i18n import GLOBAL_NS as I18N_GLOBAL

@dataclass
class WindowValidationResult:
    is_valid: bool
    code: str
    window: Optional[Dict[str, Any]] = None

def validate_selected_cabal_window(
    selected: Any,
    known_items: List[Dict[str, Any]],
    allowed_processes: List[str] = ["cabal.exe", "cabalmain.exe"],
) -> WindowValidationResult:
    if not isinstance(selected, dict) or not isinstance(selected.get("hwnd"), int):
        return WindowValidationResult(False, "no_window_selected")

    hwnd = selected["hwnd"]
    wm = WindowManager()
    info = wm.get_window_info(hwnd)

    if info is None or not wm.is_window_valid(hwnd):
        return WindowValidationResult(False, "window_unavailable")

    if info.pid != selected.get("pid"):
        return WindowValidationResult(False, "window_changed")

    if info.process_name.lower() not in allowed_processes:
        return WindowValidationResult(False, "no_cabal_window")

    if (
        not info.is_visible
        or not info.is_enabled
        or info.is_minimized
        or info.is_offscreen
    ):
        return WindowValidationResult(False, "window_unavailable")

    if known_items:
        if hwnd not in {item["hwnd"] for item in known_items}:
            return WindowValidationResult(False, "window_changed")

    win_dict = {
        "hwnd": int(info.hwnd),
        "pid": int(info.pid),
        "title": (info.title or "").strip(),
        "proc": info.process_name,
        "bounds": normalize_window_bounds_value(info.rect),
        "is_minimized": info.is_minimized,
    }
    return WindowValidationResult(True, "ok", win_dict)

class WindowRecoveryController:
    _instance = None

    def __init__(self):
        self._retry_in_progress = False
        self._retry_step = 0
        self._retry_max = 3
        self._hwnd = None
        self._on_progress = None
        self._on_failure = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def start_async_recovery(
        self,
        hwnd: int,
        schedule_after_ms=None,
        on_progress=None,
        on_failure=None,
        delay_ms: int = 500,
    ):
        if self._retry_in_progress:
            return

        self._retry_in_progress = True
        self._retry_step = 0
        self._hwnd = hwnd
        self._on_progress = on_progress
        self._on_failure = on_failure
        self._schedule_after_ms = schedule_after_ms
        self._delay_ms = delay_ms

        self._execute_retry_step()

    def _execute_retry_step(self):
        self._retry_step += 1

        if self._on_progress:
            self._on_progress(self._retry_step)

        wm = WindowManager()
        success = wm.restore(self._hwnd) and wm.set_foreground(self._hwnd)

        if success:
            self._retry_in_progress = False
            return

        if self._retry_step >= self._retry_max:
            self._retry_in_progress = False
            if self._on_failure:
                self._on_failure()
            return

        if callable(getattr(self, "_schedule_after_ms", None)):
            self._schedule_after_ms(
                getattr(self, "_delay_ms", 500), self._execute_retry_step
            )
        else:
            self._retry_in_progress = False
            if self._on_failure:
                self._on_failure()

class WindowSelectionService:
    @staticmethod
    def resolve_bounds(
        config: Any, current_bounds: Optional[List[int]] = None
    ) -> Optional[List[int]]:
        bounds = normalize_window_bounds_value(current_bounds)
        if bounds is not None:
            return bounds

        if not isinstance(config, dict):
            return None

        hunt_area = config.get("hunt_area")
        if isinstance(hunt_area, dict):
            bounds = normalize_window_bounds_value(hunt_area.get("window_bounds"))
            if bounds is not None:
                return bounds

        return normalize_window_bounds_value(config.get("window_bounds"))

    @staticmethod
    def update_bounds(config: Any, bounds: Any) -> Optional[List[int]]:
        if not isinstance(config, dict):
            return None

        normalized = normalize_window_bounds_value(bounds)
        config["window_bounds"] = normalized

        hunt_area = config.get("hunt_area")
        if not isinstance(hunt_area, dict):
            hunt_area = {}
            config["hunt_area"] = hunt_area

        hunt_area["window_bounds"] = normalized
        return normalized

    @staticmethod
    def validate_prerequisites(hunt_selected: Any, win_items: List[Dict[str, Any]], hunt_cfg: Dict[str, Any], current_window_bounds: Optional[List[int]] = None) -> Optional[str]:
        logger = logging.getLogger(__name__)

        if not isinstance(hunt_selected, dict):
            logger.warning("Validation failed: no_window_selected")
            return i18n_t("error_no_window_selected", ns=I18N_GLOBAL)

        validation = validate_selected_cabal_window(hunt_selected, win_items)
        if not validation.is_valid:
            if validation.code == "no_window_selected":
                logger.warning("Validation failed: no_window_selected")
                return i18n_t("error_no_window_selected", ns=I18N_GLOBAL)
            elif validation.code == "window_unavailable":
                logger.warning("Validation failed: window_unavailable")
                return i18n_t("error_window_unavailable", ns=I18N_GLOBAL)
            elif validation.code == "window_changed":
                logger.warning("Validation failed: window_changed")
                return i18n_t("error_window_changed", ns=I18N_GLOBAL)
            elif validation.code == "no_cabal_window":
                logger.warning("Validation failed: no_cabal_window")
                return i18n_t("error_no_cabal_window", ns=I18N_GLOBAL)
            else:
                logger.warning("Validation failed: no_cabal_window")
                return i18n_t("error_no_cabal_window", ns=I18N_GLOBAL)

        bounds = WindowSelectionService.resolve_bounds(hunt_cfg, current_window_bounds)
        if not bounds:
            logger.warning("Validation failed: window_unavailable")
            return i18n_t("error_window_unavailable", ns=I18N_GLOBAL)

        templates = hunt_cfg.get("templates") or []
        template_path = str(hunt_cfg.get("template_path", "") or "").strip()
        if not templates and not template_path:
            logger.warning("Validation failed: no_templates")
            return i18n_t("error_no_templates", ns=I18N_GLOBAL)

        import os

        has_valid_template = False
        if templates:
            for t in templates:
                if isinstance(t, dict):
                    path = t.get("path")
                    if path and os.path.exists(path):
                        has_valid_template = True
                        break
        if not has_valid_template and template_path and os.path.exists(template_path):
            has_valid_template = True

        if not has_valid_template:
            logger.warning("Validation failed: invalid_template")
            return i18n_t("error_invalid_template", ns=I18N_GLOBAL)

        return None
