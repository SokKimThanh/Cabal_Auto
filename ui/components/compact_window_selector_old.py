"""Compact window selector for hunt tab header bar."""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Callable, Optional
import logging

logger = logging.getLogger(__name__)


class CompactWindowSelector:
    """Window selector UI component for hunt tab header.

    Replaces combobox + refresh button with:
    - Search entry field
    - Dropdown listbox with filtered windows
    - Refresh icon button
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_window_selected: Callable[[Dict[str, Any]], None],
        window_controller: Any,  # AppWindowController instance
        root: tk.Tk,
    ):
        self.parent = parent
        self.on_window_selected = on_window_selected
        self.window_controller = window_controller
        self.root = root

        self.win_items: List[Dict[str, Any]] = []
        self.filtered_windows: List[Dict[str, Any]] = []
        self.is_open = False
        self.listbox = None  # Will be created when dropdown opens
        self.dropdown_window = None

        self._build_ui()

    def _build_ui(self):
        """Build the compact window selector UI."""
        # Main frame - will contain search bar and dropdown
        self.frame = tk.Frame(self.parent, bg=self.parent.cget("bg"))

        # Search frame (always visible)
        self.search_frame = tk.Frame(self.frame, bg=self.parent.cget("bg"))
        self.search_frame.pack(side="top", fill="x", expand=False)

        # Search label
        search_label = tk.Label(
            self.search_frame,
            text="Window:",
            bg=self.parent.cget("bg"),
            fg="#9ca3af",
            font=("Arial", 9),
        )
        search_label.pack(side="left", padx=(0, 5))

        # Search entry
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            self.search_frame,
            textvariable=self.search_var,
            width=30,
            font=("Arial", 9),
        )
        self.search_entry.pack(side="left", padx=(0, 8), fill="x", expand=True)
        self.search_entry.bind("<Return>", self._on_search_enter)
        self.search_entry.bind("<KeyRelease>", self._on_search_text_changed)
        self.search_entry.bind("<FocusIn>", self._on_search_focus_in)
        self.search_entry.bind("<Escape>", lambda e: self._close_dropdown())

        # Dropdown button
        self.dropdown_btn = tk.Button(
            self.search_frame,
            text="▼",
            width=2,
            height=1,
            bg="#2a2a2a",
            fg="#d1d5db",
            relief="flat",
            command=self._toggle_dropdown,
            cursor="hand2",
        )
        self.dropdown_btn.pack(side="left", padx=(0, 8))

        # Refresh button (icon only)
        self.refresh_btn = tk.Button(
            self.search_frame,
            text="🔄",
            width=2,
            height=1,
            bg="#2a2a2a",
            fg="#d1d5db",
            relief="flat",
            command=self._on_refresh_clicked,
            cursor="hand2",
        )
        self.refresh_btn.pack(side="left")

        # Info label
        self.info_label = tk.Label(
            self.frame,
            text="Click refresh to load windows",
            font=("Arial", 8),
            bg=self.parent.cget("bg"),
            fg="#6b7280",
        )
        self.info_label.pack(side="bottom", fill="x", pady=(2, 0))

    def get_frame(self) -> tk.Frame:
        """Return the main frame for grid/pack."""
        return self.frame

    def _on_refresh(self):
        """Refresh window list synchronously."""
        logger.debug("CompactWindowSelector._on_refresh() called")
        try:
            # Refresh window list
            windows = self.window_controller._list_windows()
            self._update_ui_with_windows(windows)
        except Exception as e:
            self._handle_refresh_error(e)

    def _update_ui_with_windows(self, windows):
        """Update UI with fetched windows (Main Thread only)."""
        self.win_items = windows
        if hasattr(self.root, 'win_items'):
            self.root.win_items = windows
        logger.debug(f"  Found {len(self.win_items)} windows")

        # Update UI label
        self.info_label.config(
            text=f"✓ Found {len(self.win_items)} window(s)",
            fg="#4ade80"
        )

        # If dropdown is open, immediately update listbox
        if self.is_open and self.listbox:
            self._update_listbox()
            # Auto-select first window if available
            if self.filtered_windows:
                self.listbox.selection_set(0)
                self.listbox.activate(0)
                self.listbox.see(0)

        # Reset button state if it was loading
        if self.refresh_btn.cget("state") == "disabled":
            self.refresh_btn.config(state="normal", text="🔄")

    def _handle_refresh_error(self, e):
        """Handle errors during refresh (Main Thread only)."""
        logger.error(f"  Failed to refresh: {e}")
        self.info_label.config(
            text=f"Error: {e}",
            fg="#dc2626"
        )
        self.win_items = []
        if hasattr(self.root, 'win_items'):
            self.root.win_items = []

        # Reset button state if it was loading
        if self.refresh_btn.cget("state") == "disabled":
            self.refresh_btn.config(state="normal", text="🔄")

    def _on_refresh_clicked(self):
        """Handle refresh button click (Asynchronous)."""
        # Show loading state
        self.refresh_btn.config(state="disabled", text="⟳")  # Spinning icon
        self.refresh_btn.update()

        import threading

        def fetch_windows_task():
            try:
                windows = self.window_controller._list_windows()

                # Log the windows to console per user request
                logger.info("=== Window List Refresh Results ===")
                for i, w in enumerate(windows):
                    logger.info(f"[{i}] {w.get('title', 'Unknown')} (PID: {w.get('pid', 'N/A')})")
                logger.info(f"Total windows found: {len(windows)}")
                logger.info("===================================")

                self.root.after(0, self._update_ui_with_windows, windows)
                logger.debug(f"[Refresh] Thread found {len(windows)} windows")
            except Exception as e:
                logger.error(f"[Refresh] Thread error: {e}")
                self.root.after(0, self._handle_refresh_error, e)

        # Start thread
        threading.Thread(target=fetch_windows_task, daemon=True).start()

    def _on_search_focus_in(self, event=None):
        """Show dropdown when search box focused."""
        # Only auto-open if dropdown is not already open
        # Also ignore focus events that come from Toplevel closing
        if not self.is_open and not self.dropdown_window:
            self._toggle_dropdown()

    def _on_search_text_changed(self, event=None):
        """Filter listbox as user types."""
        if self.is_open:
            self._update_listbox()

    def _on_search_enter(self, event=None):
        """Select first item on Enter."""
        if self.listbox and self.listbox.size() > 0:
            self.listbox.selection_set(0)
            self._on_listbox_select()

    def _toggle_dropdown(self):
        """Toggle dropdown visibility using Toplevel popup window."""
        if self.is_open:
            if self.dropdown_window:
                self.dropdown_window.destroy()
                self.dropdown_window = None
            self.is_open = False
            self.dropdown_btn.config(text="▼")
        else:
            if not self.win_items:
                self._on_refresh()

            # Create Toplevel popup window for dropdown
            self.dropdown_window = tk.Toplevel(self.parent)
            self.dropdown_window.wm_overrideredirect(True)  # No window decorations
            self.dropdown_window.configure(bg="#1a1a1a")
            # Make popup grab all events (modal-like behavior)
            self.dropdown_window.grab_set()

            # Position dropdown below search frame
            self.frame.update_idletasks()
            parent_x = self.parent.winfo_rootx()
            parent_y = self.parent.winfo_rooty()
            frame_width = self.frame.winfo_width()
            search_height = self.search_frame.winfo_height()

            # Calculate dropdown position (below search_frame)
            dropdown_x = parent_x
            dropdown_y = parent_y + search_height

            # Create scrollbar and listbox in Toplevel
            scrollbar = tk.Scrollbar(self.dropdown_window)
            scrollbar.pack(side="right", fill="y")

            self.listbox = tk.Listbox(
                self.dropdown_window,
                height=6,
                width=50,
                yscrollcommand=scrollbar.set,
                font=("Courier New", 9),
                bg="#111111",
                fg="#d1d5db",
                selectmode="single",
            )
            self.listbox.pack(side="left", fill="both", expand=True)
            scrollbar.config(command=self.listbox.yview)
            self.listbox.bind("<<ListboxSelect>>", self._on_listbox_select)
            # Allow Escape key to close dropdown
            self.listbox.bind("<Escape>", lambda e: self._close_dropdown())

            # Position and resize Toplevel window
            self.dropdown_window.geometry(f"{frame_width}x150+{dropdown_x}+{dropdown_y}")

            self._update_listbox()

            self.is_open = True
            self.dropdown_btn.config(text="▲")
            self.search_entry.focus()

    def _update_listbox(self):
        """Update listbox with filtered windows."""
        # Only update if listbox exists (dropdown is open)
        if not self.listbox:
            return

        search_text = self.search_var.get().lower()

        # Filter windows
        self.filtered_windows = [
            w for w in self.win_items
            if search_text in w["title"].lower()
            or search_text in w.get("proc", "").lower()
        ]

        # Update listbox
        self.listbox.delete(0, tk.END)
        for w in self.filtered_windows:
            label = f"{w['title']}  [PID:{w['pid']}]"
            self.listbox.insert(tk.END, label)

        if self.filtered_windows:
            self.listbox.selection_set(0)
            self.listbox.activate(0)

    def _close_dropdown(self):
        """Close dropdown window safely."""
        if self.is_open:
            if self.dropdown_window:
                try:
                    self.dropdown_window.grab_release()
                except Exception:
                    pass
                try:
                    self.dropdown_window.destroy()
                except Exception:
                    pass
                self.dropdown_window = None
            self.is_open = False
            self.dropdown_btn.config(text="▼")
            self.listbox = None

    def _on_listbox_select(self, event=None):
        """Handle window selection from listbox."""
        try:
            if not self.listbox:
                return
            sel = self.listbox.curselection()
            if not sel:
                return

            selected = self.filtered_windows[sel[0]]
            logger.debug(f"Selected window: {selected['title']}")

            # Update search entry with selection
            self.search_var.set(selected["title"])

            # Call callback
            self.on_window_selected(selected)

            # Temporarily unbind FocusIn to prevent re-opening
            self.search_entry.unbind("<FocusIn>")

            # Close dropdown using helper method
            self._close_dropdown()

            # Restore FocusIn binding after a short delay
            self.search_entry.after(100, lambda: self.search_entry.bind("<FocusIn>", self._on_search_focus_in))

        except Exception as e:
            logger.error(f"Error on window select: {e}")

    def set_search_text(self, text: str):
        """Set search entry text programmatically."""
        self.search_var.set(text)

    def get_selected_window(self) -> Optional[Dict[str, Any]]:
        """Get currently selected window dict."""
        try:
            if not self.listbox:
                return None
            sel = self.listbox.curselection()
            if sel:
                return self.filtered_windows[sel[0]]
        except Exception:
            pass
        return None
        return None
