import copy
import time
import tkinter as tk
from tkinter import messagebox
from typing import Any, Dict

from lib.features.hunt.hunt_config import save_hunt_config
from lib.system.bot_manager import BotManager
from ui.utils.overlay_controller import OverlayController as UtilsOverlayController


class OverlayController:
    """Controller for overlay UI lifecycle."""

    def __init__(self, parent: Any):
        self.parent = parent
        self.parent._overlay_enabled = getattr(self.parent, "_overlay_enabled", False)

    def _t(self, key: str, **kwargs) -> str:
        if hasattr(self.parent, "_t"):
            return self.parent._t(key, **kwargs)
        return key

    def open_settings(self, *_args) -> None:
        from ui.utils.overlay_settings import OverlaySettingsDialog

        hunt_cfg = getattr(self.parent, "hunt_cfg", {})
        overlay_cfg = copy.deepcopy(hunt_cfg.get("overlay", {}))

        def on_apply(new_config: Dict[str, Any]) -> None:
            self.parent.hunt_cfg["overlay"] = new_config
            save_hunt_config(self.parent.hunt_cfg)

        dialog = OverlaySettingsDialog(
            parent=self.parent,
            current_config=overlay_cfg,
            lang=getattr(self.parent, "lang", "vi"),
            on_apply=on_apply,
        )
        dialog.show()

    def toggle_overlay(self, *_args) -> None:
        """
        Toggle overlay display (Ctrl+Shift+O).
        Phase 5: Show/hide transparent overlay on game window.
        """
        print("[Vision] Toggle overlay - Starting...")

        try:
            # Import PyWin32 overlay module (Phase 5 refactor)
            try:
                print("[Overlay] Attempting to import OverlayWindowPyWin32...")
                from ui.windows.overlay_window import OverlayWindowPyWin32

                print("[Overlay] ✅ Import successful!")
            except ImportError as import_err:
                # PyWin32 not installed - show translated error
                print(f"[Overlay] ❌ ImportError caught: {import_err}")
                print(f"[Overlay] Error type: {type(import_err)}")
                import traceback

                traceback.print_exc()
                messagebox.showerror(
                    self._t("overlay_missing_dependency_title"),
                    self._t("overlay_missing_dependency_message"),
                )
                self.parent._overlay_enabled = False
                return
            except Exception as other_err:
                # Other errors during import
                print(f"[Overlay] ❌ Unexpected error during import: {other_err}")
                import traceback

                traceback.print_exc()
                messagebox.showerror(
                    self._t("error"), f"Cannot import overlay module:\n{other_err}"
                )
                self.parent._overlay_enabled = False
                return

            # Toggle state
            self.parent._overlay_enabled = not self.parent._overlay_enabled

            if self.parent._overlay_enabled:
                # ========================================
                # STEP 1: ALWAYS REFRESH LIVE POSITION FIRST
                # ========================================
                target_hwnd = self.parent.hunt_cfg.get("window_hwnd")
                window_bounds = None

                # Get CURRENT window position from LIVE game window (not from config cache)
                if target_hwnd:
                    try:
                        from lib.system.window_manager import WindowManager

                        wm = WindowManager()
                        current_window = wm.get_window_info(target_hwnd)

                        if current_window:
                            # Update with LIVE position
                            window_bounds = current_window.rect

                            # Handle minimized window
                            if current_window.is_minimized:
                                print(f"[Overlay] ⚠️ Game is minimized, restoring...")
                                wm.restore(target_hwnd)
                                time.sleep(0.3)

                                # Get updated position after restore
                                current_window = wm.get_window_info(target_hwnd)
                                if current_window:
                                    window_bounds = current_window.rect
                                    print(
                                        f"[Overlay] ✅ Window restored to: {window_bounds}"
                                    )

                            from lib.features.hunt.config_validator import (
                                normalize_window_bounds_value,
                            )

                            if window_bounds and not normalize_window_bounds_value(
                                window_bounds
                            ):
                                print(
                                    f"[Overlay] ⚠️ Detected minimized or invalid rect, clearing: {window_bounds}"
                                )
                                window_bounds = None

                            if window_bounds:
                                from lib.features.hunt.window_selection_service import (
                                    WindowSelectionService,
                                )

                                # Save LIVE position to config
                                WindowSelectionService.update_bounds(
                                    self.parent.hunt_cfg, window_bounds
                                )
                                save_hunt_config(self.parent.hunt_cfg)
                                print(
                                    f"[Overlay] ✅ Refreshed LIVE position: {window_bounds}"
                                )
                        else:
                            print(
                                f"[Overlay] ⚠️ Could not get current window info for HWND:{target_hwnd}"
                            )
                    except Exception as e:
                        print(f"[Overlay] ❌ Error refreshing position: {e}")

                # ========================================
                # STEP 2: AUTO-DETECT IF NO VALID POSITION
                # ========================================
                if window_bounds is None:
                    print(
                        "[Overlay] No valid window position, attempting auto-detect..."
                    )

                    # Try to find CABAL window
                    try:
                        from lib.system.window_manager import WindowManager

                        wm = WindowManager()

                        # Search for CABAL window
                        windows = wm.list_windows()
                        cabal_window = None

                        for w in windows:
                            if "CABAL" in w.title.upper():
                                cabal_window = w
                                print(
                                    f"[Overlay] Found CABAL window: {w.title} [HWND:{w.hwnd}]"
                                )
                                break

                        if cabal_window:
                            # Bring game window to foreground FIRST if minimized/hidden
                            try:
                                if cabal_window.is_minimized:
                                    print(f"[Overlay] Game is minimized, restoring...")
                                    wm.restore(cabal_window.hwnd)
                                    time.sleep(0.3)  # Wait for window to restore

                                    # Get updated window info after restore
                                    restored_window = wm.get_window_info(
                                        cabal_window.hwnd
                                    )
                                    if restored_window:
                                        cabal_window = restored_window
                                        print(
                                            f"[Overlay] Window restored, new rect: {cabal_window.rect}"
                                        )
                                    else:
                                        print(
                                            f"[Overlay] ⚠️ Could not get window info after restore"
                                        )

                                if not cabal_window.is_foreground:
                                    print(
                                        f"[Overlay] Bringing game window to foreground..."
                                    )
                                    wm.set_foreground(cabal_window.hwnd)
                                    print(f"[Overlay] ✅ Game window focused")
                            except Exception as e:
                                print(
                                    f"[Overlay] Failed to restore/foreground window: {e}"
                                )

                            # Use detected window (after restore)
                            window_bounds = cabal_window.rect
                            target_hwnd = cabal_window.hwnd

                            from lib.features.hunt.config_validator import (
                                normalize_window_bounds_value,
                            )

                            if not normalize_window_bounds_value(window_bounds):
                                messagebox.showerror(
                                    "Invalid Window Position",
                                    f"Game window appears to be minimized or invalid.\n\n"
                                    f"Current position: {window_bounds}\n\n"
                                    f"Please restore the game window and try again.",
                                    parent=self.parent,
                                )
                                self.parent._overlay_enabled = False
                                return

                            from lib.features.hunt.window_selection_service import (
                                WindowSelectionService,
                            )

                            # Save to config for next time
                            WindowSelectionService.update_bounds(
                                self.parent.hunt_cfg, window_bounds
                            )
                            self.parent.hunt_cfg["window_hwnd"] = target_hwnd
                            self.parent.hunt_cfg["window_title"] = cabal_window.title

                            # save_hunt_config is already defined at module level (line 566)
                            save_hunt_config(self.parent.hunt_cfg)

                            print(
                                f"[Overlay] Auto-configured window: {cabal_window.title}"
                            )

                        else:
                            # Still no window found - show warning
                            messagebox.showwarning(
                                self._t("overlay_no_window_title"),
                                self._t("overlay_no_window_message")
                                + "\n\n💡 Tip: Open CABAL game window first!",
                            )
                            self.parent._overlay_enabled = False
                            return

                    except Exception as e:
                        print(f"[Overlay] Auto-detect failed: {e}")
                        import traceback

                        traceback.print_exc()
                        # Show original warning
                        messagebox.showwarning(
                            self._t("overlay_no_window_title"),
                            self._t("overlay_no_window_message"),
                        )
                        self.parent._overlay_enabled = False
                        return

                # ========================================
                # STEP 3: VALIDATE WE HAVE VALID POSITION
                # ========================================
                if window_bounds is None:
                    messagebox.showwarning(
                        self._t("overlay_no_window_title"),
                        self._t("overlay_no_window_message"),
                    )
                    self.parent._overlay_enabled = False
                    return

                # ========================================
                # STEP 4: CREATE OR UPDATE OVERLAY
                # ========================================
                # Get overlay config from hunt_cfg (or use defaults)
                overlay_cfg = self.parent.hunt_cfg.get("overlay", {})
                alpha = float(
                    overlay_cfg.get("alpha", 0.7)
                )  # Default 70% for testing (more visible)
                fps_limit = int(overlay_cfg.get("fps_limit", 15))

                # Create overlay if not exists
                if self.parent._overlay_window is None:
                    print(
                        f"[Overlay] Creating NEW overlay with alpha={alpha}, fps={fps_limit}"
                    )
                    print(f"[Overlay] Target rect: {window_bounds}")
                    print(f"[Overlay] Target HWND: {target_hwnd}")

                    # Create PyWin32 overlay window
                    self.parent._overlay_window = OverlayWindowPyWin32(
                        target_rect=window_bounds,
                        alpha=alpha,
                        fps_limit=fps_limit,
                        enable_click_through=True,
                    )

                    # Create window
                    self.parent._overlay_window.create()

                    print(
                        f"[Overlay] Window created with HWND: {self.parent._overlay_window.hwnd}"
                    )
                    print(
                        f"[Overlay] {self._t('overlay_created').format(hwnd=target_hwnd, rect=window_bounds)}"
                    )
                else:
                    # Overlay already exists, just update position
                    print(
                        f"[Overlay] Overlay exists, updating to LIVE position: {window_bounds}"
                    )
                    self.parent._overlay_window.update_target_rect(window_bounds)

                # Show overlay
                self.parent._overlay_window.show()

                # ========================================
                # PHASE 7: Initialize Monster Tracking
                # ========================================
                try:
                    # Initialize VisionEngine if needed
                    if self.parent._vision_engine is None:
                        from lib.vision.vision_engine import VisionEngine

                        self.parent._vision_engine = VisionEngine()
                        print("[MonsterTracking] VisionEngine initialized")

                    # Initialize ScreenCapture if needed
                    if self.parent._screen_capture is None:
                        from lib.system.screen_capture import ScreenCapture

                        self.parent._screen_capture = ScreenCapture()
                        print("[MonsterTracking] ScreenCapture initialized")

                    # Initialize BotManager if needed
                    if self.parent._bot_manager is None:
                        # Get configuration from hunt_cfg
                        tracking_cfg = self.parent.hunt_cfg.get("monster_tracking", {})
                        stable_frames = int(tracking_cfg.get("stable_frames", 3))
                        lost_timeout = float(tracking_cfg.get("lost_timeout", 3.0))
                        auto_start = bool(
                            tracking_cfg.get("auto_start_with_hunt", False)
                        )

                        self.parent._bot_manager = BotManager(
                            vision_engine=self.parent._vision_engine,
                            screen_capture=self.parent._screen_capture,
                            stable_frames=stable_frames,
                            lost_timeout=lost_timeout,
                            enable_auto_start=auto_start,
                        )
                        print(
                            f"[MonsterTracking] BotManager initialized (stable_frames={stable_frames}, lost_timeout={lost_timeout})"
                        )

                    # Start detection to create detector instance
                    if not self.parent._bot_manager.is_detection_running():
                        tracking_cfg = self.parent.hunt_cfg.get("monster_tracking", {})
                        confidence = float(
                            tracking_cfg.get("confidence_threshold", 0.7)
                        )

                        success = self.parent._bot_manager.start_detection(
                            confidence_threshold=confidence, target_rect=window_bounds
                        )
                        if success:
                            print(
                                f"[MonsterTracking] Detection started (confidence={confidence})"
                            )
                        else:
                            print("[MonsterTracking] Failed to start detection")

                    # Create OverlayController to connect detector → overlay
                    # Only create if we have a detector instance
                    if (
                        self.parent._overlay_controller is None
                        and self.parent._bot_manager._detector is not None
                    ):
                        # Get configuration
                        tracking_cfg = self.parent.hunt_cfg.get("monster_tracking", {})
                        max_boxes = int(tracking_cfg.get("max_detections_display", 20))
                        show_stats = bool(tracking_cfg.get("show_stats", True))
                        stats_interval = float(
                            tracking_cfg.get("stats_update_interval", 0.5)
                        )

                        # Get window tracker if available
                        window_tracker = getattr(self, "_window_tracker", None)

                        self.parent._overlay_controller = UtilsUtilsOverlayController(
                            overlay=self.parent._overlay_window,
                            detector=self.parent._bot_manager._detector,
                            max_boxes=max_boxes,
                            show_stats=show_stats,
                            stats_update_interval=stats_interval,
                            window_tracker=window_tracker,
                        )

                        # Start controller to activate callbacks
                        self.parent._overlay_controller.start()
                        print(
                            f"[MonsterTracking] OverlayController started (max_boxes={max_boxes}, show_stats={show_stats})"
                        )

                    print("[MonsterTracking] Monster tracking active")

                except Exception as e:
                    print(f"[MonsterTracking] Error initializing tracking: {e}")
                    import traceback

                    traceback.print_exc()

                # ALWAYS re-add test detection boxes to fix white screen issue
                from ui.windows.overlay_window import DetectionBox

                test_boxes = [
                    DetectionBox(
                        x=100,
                        y=100,
                        w=200,
                        h=150,
                        label="TEST OVERLAY - Visible?",
                        color=(255, 0, 0),  # Red
                        confidence=1.0,
                    ),
                    DetectionBox(
                        x=350,
                        y=250,
                        w=150,
                        h=100,
                        label="Detection Test",
                        color=(0, 255, 0),  # Green
                        confidence=0.95,
                    ),
                ]
                self.parent._overlay_window.update_detections(test_boxes)
                print(f"[Overlay] Test detection boxes updated")

                # Start window tracker instead of position sync
                self.parent._start_overlay_window_tracker()

                # Update menu/config
                self.parent.hunt_cfg.setdefault("overlay", {})["enabled"] = True
                save_hunt_config(self.parent.hunt_cfg)

                print(f"[Overlay] {self._t('overlay_enabled')}")

            else:
                # ========================================
                # PHASE 7: Stop Monster Tracking
                # ========================================
                try:
                    # Stop overlay controller
                    if self.parent._overlay_controller is not None:
                        self.parent._overlay_controller.stop()
                        self.parent._overlay_controller = None
                        print("[MonsterTracking] OverlayController stopped")

                    # Stop detection
                    if self.parent._bot_manager is not None:
                        self.parent._bot_manager.stop_detection()
                        print("[MonsterTracking] Detection stopped")

                except Exception as e:
                    print(f"[MonsterTracking] Error stopping tracking: {e}")

                # Hide overlay
                if self.parent._overlay_window is not None:
                    self.parent._overlay_window.hide()

                # Stop window tracker
                self.parent._stop_overlay_window_tracker()

                # Update config
                self.parent.hunt_cfg.setdefault("overlay", {})["enabled"] = False
                save_hunt_config(self.parent.hunt_cfg)

                print(f"[Overlay] {self._t('overlay_disabled')}")

        except Exception as e:
            print(f"[Overlay] Toggle error: {e}")
            import traceback

            traceback.print_exc()
            messagebox.showerror(
                self._t("overlay_error_title"),
                self._t("overlay_toggle_failed").format(error=str(e)),
            )
            self.parent._overlay_enabled = False
