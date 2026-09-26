"""Compact window selector for hunt tab header bar."""

import sys
import threading
import tkinter as tk
from typing import List, Dict, Any, Callable, Optional
import logging
from lib.ui_style_v2 import UIStyleV2 as UI

logger = logging.getLogger(__name__)


class CompactWindowSelector:
    """Window selector UI component for hunt tab header.

    Replaces combobox + refresh button with a read-only selected-window field.
    The dropdown arrow searches for and selects the first detected Cabal window.
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_window_selected: Callable[[Dict[str, Any]], None],
        window_controller: Any,  # AppWindowController instance
        root: Any,
    ):
        self.state_controller = getattr(root, 'state_controller', root) # Fallback to support both App and App.root
        self.parent = parent

        # REFACTOR(#5): Win event hook
        self._hook = None
        self._hook_thread = None
        self._hook_stop_event = threading.Event()

        self.on_window_selected = on_window_selected
        self.window_controller = window_controller
        self.root = root

        self.win_items: List[Dict[str, Any]] = []
        self.selected_window: Optional[Dict[str, Any]] = None

        self._build_ui()

    def _build_ui(self):
        """Build the compact window selector UI."""
        self.frame = tk.Frame(self.parent, bg=self.parent.cget("bg"))

        # Search frame (always visible)
        self.search_frame = tk.Frame(self.frame, bg=self.parent.cget("bg"))
        self.search_frame.pack(side="top", fill="x", expand=False)

        # Search label
        search_label = tk.Label(
            self.search_frame,
            text="Window:",
            bg=self.parent.cget("bg"),
            fg=UI.TEXT_SECONDARY,
            font=UI.FONT_TEXT,
        )
        search_label.pack(side="left", padx=(0, 5))

        # Selected window display
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            self.search_frame,
            textvariable=self.search_var,
            width=30,
            font=UI.FONT_TEXT,
            state="readonly",
            bg=UI.BG_ELEVATED,
            fg=UI.TEXT_MUTED,
            readonlybackground=UI.BG_ELEVATED,
            relief="flat",
        )
        self.search_entry.pack(side="left", padx=(0, 8), fill="x", expand=True)
        self._set_entry_status("Chưa chọn cửa sổ Cabal", UI.TEXT_MUTED, UI.BG_ELEVATED)

        # Select the first detected Cabal window.
        self.dropdown_btn = tk.Button(
            self.search_frame,
            text="▼",
            width=2,
            height=1,
            bg=UI.BG_SURFACE,
            fg=UI.TEXT_PRIMARY,
            relief="flat",
            command=self._on_select_clicked,
            cursor="hand2",
        )
        self.dropdown_btn.pack(side="left", padx=(0, 8))

        # Refresh button (icon only)
        self.refresh_btn = tk.Button(
            self.search_frame,
            text="",
            width=2,
            height=1,
            bg=UI.BG_SURFACE,
            fg=UI.TEXT_PRIMARY,
            relief="flat",
            command=self._on_refresh_clicked,
            cursor="hand2",
        )
        self.refresh_btn.pack(side="left")

        # FIX BUG #2: Bắt đầu auto-refresh window list
        self._schedule_auto_refresh()

    def _schedule_auto_refresh(self):
        """REFACTOR(#5): Đăng ký Win event hook thay vì polling."""
        if sys.platform != "win32":
            # Fallback polling cho non-Windows (dev env)
            self._schedule_polling_refresh()
            return

        def _hook_callback(hWinEventHook, event, hwnd, idObject, idChild,
                           dwEventThread, dwmsEventTime):
            # Lọc chỉ bắt window (OBJID_WINDOW = 0)
            if idObject != 0:
                return
            # Chạy trên hook thread → marshal về main thread
            try:
                self.parent.after(0, self._on_refresh)
            except Exception:
                pass

        try:
            import ctypes
            from ctypes import wintypes

            WINEVENTPROC = ctypes.WINFUNCTYPE(
                None, wintypes.HANDLE, wintypes.DWORD, wintypes.HWND,
                wintypes.LONG, wintypes.LONG, wintypes.DWORD, wintypes.DWORD
            )
            self._hook_callback_func = WINEVENTPROC(_hook_callback)

            self._hook = ctypes.windll.user32.SetWinEventHook(
                win32con.EVENT_OBJECT_CREATE,
                win32con.EVENT_OBJECT_SHOW,
                0,                     # hmodWinEventProc
                self._hook_callback_func,
                0, 0,                     # idProcess, idThread = all
                win32con.WINEVENT_OUTOFCONTEXT,
            )
            logger.info("[WindowSelector] Win event hook registered")
        except Exception as e:
            logger.warning(f"[WindowSelector] Hook failed: {e}, fallback to polling")
            self._schedule_polling_refresh()

    def _schedule_polling_refresh(self):
        """Fallback: polling 5s cho non-Windows."""
        if not self.selected_window:
            try:
                self._on_refresh()
            except Exception:
                pass
            self.parent.after(5000, self._schedule_polling_refresh)

    def get_frame(self) -> tk.Frame:
        """Return the main frame for grid/pack."""
        return self.frame

    def _on_refresh(self):
        """Refresh and select the first detected Cabal window."""
        try:
            self._update_ui_with_windows(
                self.window_controller._list_windows(), select_first=True
            )
        except Exception as error:
            self._handle_refresh_error(error)

    def _update_ui_with_windows(
        self, windows: List[Dict[str, Any]], select_first: bool = False
    ):
        """Update UI with fetched windows (Main Thread only)."""
        self.win_items = windows
        self.state_controller.win_items = windows

        if not windows:
            self.selected_window = None
            message = getattr(self.root, '_t', lambda x, **kwargs: x)("error_no_cabal_window_found")
            self._set_entry_status(message, UI.DANGER, UI.BG_SURFACE)
        elif select_first or self.selected_window is None:
            self._select_window(windows[0])

        self._set_loading_state(False)

    def _handle_refresh_error(self, error: Exception):
        """Handle errors during refresh (Main Thread only)."""
        logger.error("Failed to refresh Cabal windows: %s", error)
        self.win_items = []
        self.selected_window = None
        self.state_controller.win_items = []
        message = f"Không thể tìm cửa sổ Cabal: {error}"
        self._set_entry_status(message, UI.DANGER, UI.BG_SURFACE)
        self._set_loading_state(False)

    def _select_window(self, window: Dict[str, Any]):
        """Persist and display the detected Cabal window."""
        self.selected_window = window
        title = window.get("title") or "Cabal"
        self._set_entry_status(title, UI.ACCENT_GREEN, UI.ACCENT_GREEN_BG)
        self.on_window_selected(window)

    def _set_entry_status(self, text: str, foreground: str, background: str):
        """Show the current selection state in the locked window field."""
        self.search_var.set(text)
        self.search_entry.config(fg=foreground, readonlybackground=background)

    def _set_loading_state(self, loading: bool):
        """Prevent duplicate scans while window detection is running."""
        state = "disabled" if loading else "normal"
        _t = getattr(self.root, '_t', lambda x, **kwargs: x)
        self.refresh_btn.config(state=state, text=_t("ui.loading") if loading else "")
        self.dropdown_btn.config(state=state, text="⟳" if loading else "▼")

    def _on_refresh_clicked(self):
        """Refresh and select the first detected Cabal window."""
        self._refresh_windows_async(select_first=True)

    def _on_select_clicked(self):
        """Find and select the first detected Cabal window."""
        self._refresh_windows_async(select_first=True)

    def _refresh_windows_async(self, select_first: bool):
        """Fetch windows outside Tk's main thread and update the UI when complete."""
        self._set_loading_state(True)

        def fetch_windows_task():
            try:
                windows = self.window_controller._list_windows()
                self.root.after(
                    0, self._update_ui_with_windows, windows, select_first
                )
            except Exception as error:
                self.root.after(0, self._handle_refresh_error, error)

        import threading

        threading.Thread(target=fetch_windows_task, daemon=True).start()

    def set_search_text(self, text: str):
        """Set search entry text programmatically."""
        self._set_entry_status(
            text or "Chưa chọn cửa sổ Cabal",
            UI.ACCENT_GREEN if text else UI.TEXT_MUTED,
            UI.ACCENT_GREEN_BG if text else UI.BG_ELEVATED,
        )

    def get_selected_window(self) -> Optional[Dict[str, Any]]:
        """Return the automatically selected Cabal window, if any."""
        return self.selected_window

    def destroy(self):
        # REFACTOR(#5): Unhook
        if self._hook is not None:
            try:
                if sys.platform == "win32":
                    import ctypes
                    ctypes.windll.user32.UnhookWinEvent(self._hook)
            except Exception:
                pass
            self._hook = None
        if hasattr(self, 'frame') and hasattr(self.frame, 'destroy'):
            self.frame.destroy()
