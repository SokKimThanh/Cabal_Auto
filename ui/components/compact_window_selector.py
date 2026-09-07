"""Compact window selector for hunt tab header bar - Linear UI version."""

 # NOTE: Avoid mutating sys.path at import-time; ensure the app is launched from the project root so absolute imports resolve.

import tkinter as tk
from typing import List, Dict, Any, Callable, Optional
import logging
from lib.ui_style_v2 import UIStyleV2 as UI

logger = logging.getLogger(__name__)


class CompactWindowSelector:
    """Window selector UI component for hunt tab header.
    
    Simple UI with:
    - Info label showing window count/status
    - Refresh button (🔄) to manually fetch windows
    - Dropdown button (▼) to auto-select first window
    
    No listbox - auto-selects first window when dropdown is clicked.
    """

    @staticmethod
    def check_active_threads():
        """Print all active threads (debugging helper)."""
        import threading
        print("\n" + "="*60)
        print("🧵 ACTIVE THREADS:")
        print("="*60)
        for thread in threading.enumerate():
            print(f"  • {thread.name:30s} | Daemon: {str(thread.daemon):5s} | Alive: {thread.is_alive()}")
        print("="*60 + "\n")

    def __init__(
        self,
        parent: tk.Widget,
        on_window_selected: Callable[[Dict[str, Any]], None],
        window_controller: Any,  # AppWindowController instance
        root: tk.Tk,
        on_save_config: Optional[Callable[[], None]] = None,  # Callback to save config
    ):
        self.parent = parent
        self.on_window_selected = on_window_selected
        self.window_controller = window_controller
        self.root = root
        self.on_save_config = on_save_config
        
        self.win_items: List[Dict[str, Any]] = []
        self.dropdown_open = False  # Track dropdown state
        
        self._build_ui()

    def _build_ui(self):
        """Build simple window selector UI (no listbox - auto-select first window)."""
        # The caller owns geometry management for the component frame.
        self.frame = tk.Frame(self.parent, bg=self.parent.cget("bg"))
        
        # ===== Top row: Controls (always visible) =====
        control_frame = tk.Frame(self.frame, bg=self.parent.cget("bg"))
        control_frame.pack(side="top", fill="x", padx=0, pady=0)
        
        # Info label box with background
        info_box = tk.Frame(
            control_frame,
            bg="#1a1a1a",
            relief="solid",
            bd=1,
            highlightthickness=0
        )
        info_box.pack(side="left", padx=8, pady=6, fill="y", expand=False)
        
        self.info_label = tk.Label(
            info_box,
            text="? windows",
            font=("Arial", 11, "bold"),
            bg="#1a1a1a",
            fg="#ff6b6b",
            anchor="w",
            padx=12,
            pady=8,
        )
        self.info_label.pack(side="left", fill="y", expand=False)

        # ===== Button frame (right side) =====
        button_frame = tk.Frame(control_frame, bg=self.parent.cget("bg"))
        button_frame.pack(side="right", padx=8, pady=0)

        # Refresh button
        self.refresh_btn = tk.Button(
            button_frame,
            text="🔄",
            width=3,
            bg="#333333",
            fg="#ffffff",
            relief="flat",
            command=self._on_refresh_clicked,
            cursor="hand2",
            font=("Arial", 10, "bold"),
            padx=6,
            pady=4,
            activebackground="#444444",
            activeforeground="#ffffff"
        )
        self.refresh_btn.pack(side="left", padx=(0, 6), pady=0)
        logger.debug("Refresh button created")
        
        # Dropdown button (select first window)
        self.dropdown_btn = tk.Button(
            button_frame,
            text="✕",  # Start in closed state
            width=3,
            bg="#333333",
            fg="#ffffff",
            relief="flat",
            command=self._on_dropdown_clicked,
            cursor="hand2",
            font=("Arial", 10, "bold"),
            padx=6,
            pady=4,
            activebackground="#444444",
            activeforeground="#ffffff"
        )
        self.dropdown_btn.pack(side="left", padx=(0, 6), pady=0)

        # Save/Apply button (save hunt config)
        self.save_btn = tk.Button(
            button_frame,
            text="💾",
            width=3,
            bg="#2d5016",
            fg="#4ade80",
            relief="flat",
            command=self._on_save_clicked,
            cursor="hand2",
            font=("Arial", 10, "bold"),
            padx=6,
            pady=4,
            activebackground="#3d6b1f",
            activeforeground="#4ade80"
        )
        self.save_btn.pack(side="left", padx=0, pady=0)
        logger.debug("Save button created")

    def get_frame(self) -> tk.Frame:
        """Return the main frame for grid/pack."""
        return self.frame

    def _on_dropdown_clicked(self):
        """Handle dropdown button click - fetch windows and auto-select first."""
        logger.info("Dropdown button clicked")
        
        # Toggle dropdown state
        self.dropdown_open = not self.dropdown_open
        
        # Update button icon based on state
        if self.dropdown_open:
            self.dropdown_btn.config(text="▼")  # Open state
        else:
            self.dropdown_btn.config(text="✕")  # Closed state
        
        # Fetch windows
        self._on_refresh()

    def _on_save_clicked(self):
        """Handle save button click - save hunt configuration."""
        logger.info("Save button clicked")
        if self.on_save_config:
            try:
                self.on_save_config()
                logger.info("Hunt config saved successfully")
                # Optional: Show visual feedback
                self.save_btn.config(text="✓")
                self.root.after(1000, lambda: self.save_btn.config(text="💾"))
            except Exception as e:
                logger.error(f"Error saving config: {e}", exc_info=True)
        else:
            logger.warning("No save callback configured")

    def _on_refresh(self):
        """Refresh window list (triggered internally without button loading state)."""
        try:
            windows = self.window_controller._list_windows()
            logger.debug(f"Sync refresh: Got {len(windows)} windows")
            self._update_ui_with_windows(windows)
        except Exception as e:
            logger.error(f"Error in sync refresh: {e}", exc_info=True)
            self._handle_refresh_error(e)

    def _update_ui_with_windows(self, windows):
        """Update UI with fetched windows (Main Thread only)."""
        logger.info(f"Received {len(windows)} windows")
        
        self.win_items = windows
        logger.debug(f"Saved windows: {[w.get('title', 'Unknown')[:30] for w in windows]}")
        
        count = len(self.win_items)
        if count > 0:
            text = f"✓ {count} window(s) found"
            fg_color = "#4ade80"  # Green
            
            # Auto-select first window
            selected = self.win_items[0]
            logger.debug(f"Auto-selecting first window: {selected['title']}")
            self.on_window_selected(selected)
        else:
            text = "⚠ Chưa mở game | Không có window"
            fg_color = "#ff6b6b"  # Bright red

        self.info_label.config(text=text, fg=fg_color)
        logger.debug(f"Updated info_label to: {text}")

        if self.refresh_btn.cget("state") == "disabled":
            self.refresh_btn.config(state="normal", text="🔄")
        logger.debug("Refresh complete")

    def _handle_refresh_error(self, e):
        """Handle errors during refresh (Main Thread only)."""
        logger.error(f"Refresh failed: {e}", exc_info=True)
        self.info_label.config(text=f"✗ Error", fg=UI.DANGER if "UI" in globals() else "#f87171")
        self.win_items = []
        if self.refresh_btn.cget("state") == "disabled":
            self.refresh_btn.config(state="normal", text="🔄")

    def _on_refresh_clicked(self):
        """Handle refresh button click (Asynchronous)."""
        logger.info("Refresh button clicked")
        self.refresh_btn.config(state="disabled", text="⟳")
        self.refresh_btn.update()

        import threading

        def fetch_windows_task():
            try:
                windows = self.window_controller._list_windows()
                logger.debug(f"Refresh: Found {len(windows)} windows")
                self.root.after(0, self._update_ui_with_windows, windows)
            except Exception as e:
                logger.error(f"Refresh error: {e}", exc_info=True)
                self.root.after(0, self._handle_refresh_error, e)

        # Start thread with a name
        thread = threading.Thread(target=fetch_windows_task, daemon=True, name="WindowRefreshThread")
        thread.start()
        logger.debug(f"Refresh thread started: {thread.name}")
