import tkinter as tk
from tkinter import ttk
import threading
import time
import logging
import cv2
import sys

from lib.ui_style_v2 import UIStyleV2 as UI
from lib.events.ui_dispatcher import UIDispatcher
from lib.system.window_manager import WindowManager

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

try:
    from lib.system.screen_capture import ScreenCapture
except ImportError:
    ScreenCapture = None

logger = logging.getLogger(__name__)

class WindowInfoPanel(ttk.LabelFrame):
    def __init__(self, parent, app, scale_factor=1.0):
        # We try to use i18n
        self.app = app
        title_text = self._t("window_info.panel_title") if hasattr(self.app, "_t") else "Window Source"
        super().__init__(parent, text=title_text, padding=(int(10 * scale_factor), int(8 * scale_factor)))
        self.scale_factor = scale_factor

        self.is_destroyed = False
        self._loop_thread = None
        self._screen_capture = None
        self._last_hwnd = None

        self._build_ui()
        self._start_loop()

    def _t(self, key):
        if hasattr(self.app, "_t"):
            return self.app._t(key)
        return key

    def _build_ui(self):
        # Left container (Info)
        info_frame = tk.Frame(self, bg=UI.BG_BASE)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Helper to create label row
        def make_row(parent, label_key):
            row = tk.Frame(parent, bg=UI.BG_BASE)
            row.pack(fill=tk.X, pady=2)
            lbl_title = tk.Label(row, text=self._t(label_key) + ":", width=12, anchor="w", font=UI.get_font("text", UI.SIZE_SMALL), fg=UI.TEXT_SECONDARY, bg=UI.BG_BASE)
            lbl_title.pack(side=tk.LEFT)
            lbl_value = tk.Label(row, text="—", font=UI.get_font("mono", UI.SIZE_SMALL), fg=UI.TEXT_PRIMARY, bg=UI.BG_BASE)
            lbl_value.pack(side=tk.LEFT, padx=4)
            return lbl_value

        self.lbl_title_val = make_row(info_frame, "window_info.title")
        self.lbl_handle_val = make_row(info_frame, "window_info.handle")
        self.lbl_bounds_val = make_row(info_frame, "window_info.bounds")

        # Status row
        status_row = tk.Frame(info_frame, bg=UI.BG_BASE)
        status_row.pack(fill=tk.X, pady=2)
        lbl_status_title = tk.Label(status_row, text=self._t("window_info.status") + ":", width=12, anchor="w", font=UI.get_font("text", UI.SIZE_SMALL), fg=UI.TEXT_SECONDARY, bg=UI.BG_BASE)
        lbl_status_title.pack(side=tk.LEFT)
        self.lbl_status_val = tk.Label(status_row, text=self._t("window_info.not_selected"), font=UI.get_font("mono", UI.SIZE_SMALL, "bold"), fg=UI.TEXT_MUTED, bg=UI.BG_BASE)
        self.lbl_status_val.pack(side=tk.LEFT, padx=4)

        # Action row
        action_row = tk.Frame(info_frame, bg=UI.BG_BASE)
        action_row.pack(fill=tk.X, pady=6)

        from ui.components.icon_button import create_icon_button
        self.btn_reselect = create_icon_button(
            action_row,
            icon_name="refresh",
            text=self._t("window_info.reselect"),
            command=self._on_reselect_clicked,
            button_type="neutral"
        )
        self.btn_reselect.pack(side=tk.LEFT)

        # Right container (Thumbnail)
        thumb_frame = tk.Frame(self, bg=UI.BG_ELEVATED, width=160, height=90, highlightbackground=UI.BORDER_SUBTLE, highlightthickness=1)
        thumb_frame.pack_propagate(False)
        thumb_frame.pack(side=tk.RIGHT, padx=10, pady=2)

        self.lbl_thumbnail = tk.Label(thumb_frame, bg=UI.BG_ELEVATED)
        self.lbl_thumbnail.pack(expand=True, fill=tk.BOTH)

    def _on_reselect_clicked(self):
        if hasattr(self.app, "window_controller") and hasattr(self.app.window_controller, "on_hunt_find_windows"):
            self.app.window_controller.on_hunt_find_windows()

    def _start_loop(self):
        self._loop_thread = threading.Thread(target=self._loop_worker, daemon=True)
        self._loop_thread.start()

    def _loop_worker(self):
        while not self.is_destroyed:
            try:
                self._update_info()
            except Exception as e:
                logger.error(f"[WindowInfoPanel] Error in update loop: {e}")
            time.sleep(1.0)

    def _update_info(self):
        if not hasattr(self.app, "state_controller"):
            return

        hunt_selected = self.app.state_controller.hunt_selected

        if not hunt_selected:
            UIDispatcher.post(lambda: self._update_ui_state(None, None, hunt_selected))
            return

        hwnd = hunt_selected.get("hwnd")
        if not hwnd:
            UIDispatcher.post(lambda: self._update_ui_state(None, None, hunt_selected))
            return

        hwnd = int(hwnd)
        wm = WindowManager()

        if sys.platform == "win32":
            import win32gui
            is_valid = win32gui.IsWindow(hwnd)
        else:
            is_valid = True

        if not is_valid:
            UIDispatcher.post(lambda: self._update_ui_state("LOST", None, hunt_selected))
            return

        info = wm.get_window_info(hwnd)
        if not info:
            UIDispatcher.post(lambda: self._update_ui_state("LOST", None, hunt_selected))
            return

        # Update thumbnail
        thumbnail_img = None
        if not info.is_minimized:
            try:
                if self._last_hwnd != hwnd or self._screen_capture is None:
                    if self._screen_capture:
                        self._screen_capture.stop()
                    if ScreenCapture is not None:
                        self._screen_capture = ScreenCapture(target_fps=1)
                        self._screen_capture.start(info.title)
                        self._last_hwnd = hwnd

                if self._screen_capture is not None:
                    frame = self._screen_capture.get_frame(timeout=0.1)
                else:
                    frame = None

                if frame is not None and Image is not None:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(frame_rgb)
                    # Resize to fit thumbnail (e.g., 160x90)
                    pil_img.thumbnail((160, 90), Image.Resampling.LANCZOS)
                    thumbnail_img = pil_img
            except Exception as e:
                logger.debug(f"[WindowInfoPanel] Capture failed: {e}")

        UIDispatcher.post(lambda: self._update_ui_state("CONNECTED", info, hunt_selected, thumbnail_img))

    def _update_ui_state(self, status, info, hunt_selected=None, thumbnail_img=None):
        if self.is_destroyed:
            return

        is_hunting = False
        try:
            if hasattr(self.app, "state_controller"):
                is_hunting = bool(self.app.state_controller.get_ui_var('is_hunting'))
        except Exception:
            pass

        if status == "CONNECTED" and info:
            self.lbl_title_val.config(text=info.title)
            self.lbl_handle_val.config(text=f"{info.hwnd} / PID: {info.pid}")
            rect = info.rect
            self.lbl_bounds_val.config(text=f"X:{rect['left']} Y:{rect['top']} W:{rect['width']} H:{rect['height']}")
            self.lbl_status_val.config(text=self._t("window_info.connected"), fg=UI.ACCENT_GREEN)
        elif status == "LOST":
            self.lbl_title_val.config(text=hunt_selected.get("title", "—") if hunt_selected else "—")
            self.lbl_handle_val.config(text=str(hunt_selected.get("hwnd", "—")) if hunt_selected else "—")
            self.lbl_bounds_val.config(text="—")
            self.lbl_status_val.config(text=self._t("window_info.lost"), fg=UI.DANGER)
            thumbnail_img = None
        else:
            self.lbl_title_val.config(text="—")
            self.lbl_handle_val.config(text="—")
            self.lbl_bounds_val.config(text="—")
            self.lbl_status_val.config(text=self._t("window_info.not_selected"), fg=UI.TEXT_MUTED)
            thumbnail_img = None

        if hasattr(self, "btn_reselect"):
            if getattr(self.btn_reselect, "winfo_exists", lambda: False)():
                if is_hunting:
                    self.btn_reselect.config(state=tk.DISABLED)
                else:
                    self.btn_reselect.config(state=tk.NORMAL)

        if thumbnail_img and ImageTk is not None:
            photo = ImageTk.PhotoImage(thumbnail_img)
            self.lbl_thumbnail.config(image=photo, text="")
            self.lbl_thumbnail.image = photo
        else:
            self.lbl_thumbnail.config(image="", text="No Signal" if status == "LOST" else "")
            self.lbl_thumbnail.image = None

    def destroy(self):
        self.is_destroyed = True
        if self._screen_capture:
            self._screen_capture.stop()
            self._screen_capture = None
        super().destroy()
