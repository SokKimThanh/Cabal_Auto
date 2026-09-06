"""Compact window selector for hunt tab header bar - Linear UI version."""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Callable, Optional
import logging

logger = logging.getLogger(__name__)


class CompactWindowSelector:
    """Window selector UI component for hunt tab header.
    
    Linear UI with:
    - Search entry + Dropdown button + Refresh button + Close button (same row)
    - Listbox below (expandable/collapsible)
    - Info label showing window count
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
        self.listbox = None
        self.listbox_frame = None
        
        self._build_ui()

    def _build_ui(self):
        """Build the linear window selector UI."""
        # Main container
        self.frame = tk.Frame(self.parent, bg=self.parent.cget("bg"))
        
        # ===== Top row: Controls (always visible) =====
        control_frame = tk.Frame(self.frame, bg=self.parent.cget("bg"), height=40)
        control_frame.pack(side="top", fill="x", padx=0, pady=0)
        control_frame.pack_propagate(False)  # Fixed height
        
        # Info label (window count) - leftmost
        self.info_label = tk.Label(
            control_frame,
            text="? windows",
            font=("Arial", 8, "bold"),
            bg=self.parent.cget("bg"),
            fg="#6b7280",
            width=14,
        )
        self.info_label.pack(side="left", padx=(10, 5))

        # Dropdown button (toggle listbox)
        self.dropdown_btn = tk.Button(
            control_frame,
            text="▼",
            width=2,
            bg="#2a2a2a",
            fg="#d1d5db",
            relief="flat",
            command=self._toggle_listbox,
            cursor="hand2",
            font=("Arial", 8),
        )
        self.dropdown_btn.pack(side="left", padx=(0, 5))
        
        # Refresh button
        self.refresh_btn = tk.Button(
            control_frame,
            text="🔄",
            width=2,
            bg="#2a2a2a",
            fg="#d1d5db",
            relief="flat",
            command=self._on_refresh_clicked,
            cursor="hand2",
            font=("Arial", 8),
        )
        self.refresh_btn.pack(side="left", padx=(0, 5))
        
        # Close button
        self.close_btn = tk.Button(
            control_frame,
            text="✕",
            width=2,
            bg="#2a2a2a",
            fg="#d1d5db",
            relief="flat",
            command=self._close_listbox,
            cursor="hand2",
            font=("Arial", 8),
        )
        self.close_btn.pack(side="left", padx=(0, 10))

        # ===== Bottom: Listbox (collapsible) =====
        self.listbox_frame = tk.Frame(self.frame, bg="#111111", height=0)
        self.listbox_frame.pack(side="top", fill="x", padx=5, pady=(0, 5))
        self.listbox_frame.pack_propagate(False)  # Don't auto-resize

        # Search entry inside listbox frame
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            self.listbox_frame,
            textvariable=self.search_var,
            width=40,
            font=("Arial", 9),
        )
        self.search_entry.pack(side="top", fill="x", padx=5, pady=(5, 0))
        self.search_entry.bind("<KeyRelease>", self._on_search_text_changed)
        self.search_entry.bind("<Escape>", lambda e: self._close_listbox())

        # Listbox container frame
        listbox_container = tk.Frame(self.listbox_frame, bg="#111111")
        listbox_container.pack(side="top", fill="both", expand=True, padx=0, pady=5)

        # Create listbox and scrollbar inside container
        scrollbar = tk.Scrollbar(listbox_container)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(
            listbox_container,
            height=0,
            width=50,
            yscrollcommand=scrollbar.set,
            font=("Courier New", 9),
            bg="#111111",
            fg="#d1d5db",
            selectmode="single",
            bd=0,
            highlightthickness=0,
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.bind("<<ListboxSelect>>", self._on_listbox_select)
        self.listbox.bind("<Escape>", lambda e: self._close_listbox())

        # Initially hidden (height=0)
        self.is_open = False

    def get_frame(self) -> tk.Frame:
        """Return the main frame for grid/pack."""
        return self.frame

    def _toggle_listbox(self):
        """Toggle listbox visibility."""
        if self.is_open:
            self._close_listbox()
        else:
            # Refresh before opening
            self._on_refresh()
            # Show listbox
            self.listbox_frame.pack_propagate(True)
            self.listbox.config(height=6)
            self.listbox_frame.config(height=150)
            self.is_open = True
            self.dropdown_btn.config(text="▲")
            self.listbox.focus()
            self._update_listbox()
            # Auto-select first
            if self.filtered_windows:
                self.listbox.selection_set(0)
                self.listbox.activate(0)
            logger.debug("[Toggle] Listbox opened")

    def _close_listbox(self):
        """Close listbox (collapse)."""
        if self.is_open:
            self.listbox.config(height=0)
            self.listbox_frame.config(height=0)
            self.listbox_frame.pack_propagate(False)
            self.is_open = False
            self.dropdown_btn.config(text="▼")
            logger.debug("[Toggle] Listbox closed")

    def _on_refresh(self):
        """Refresh window list."""
        logger.debug("[Refresh] Starting refresh...")
        try:
            windows = self.window_controller._list_windows()
            self.win_items = windows
            self.root.win_items = windows
            
            # Update info label
            count = len(self.win_items)
            if count > 0:
                text = f"✓ {count} window(s)"
                fg_color = "#4ade80"
            else:
                text = "✗ 0 windows"
                fg_color = "#ef4444"
            
            self.info_label.config(text=text, fg=fg_color)
            self.info_label.update()  # Force update immediately
            logger.debug(f"[Refresh] Updated label: '{text}'")
            
            # Update listbox if open
            if self.is_open:
                self._update_listbox()
                if self.filtered_windows:
                    self.listbox.selection_set(0)
                    self.listbox.activate(0)
        except Exception as e:
            logger.error(f"[Refresh] Failed: {e}", exc_info=True)
            self.info_label.config(text=f"✗ Error: {e}", fg="#dc2626")
            self.info_label.update()
            self.win_items = []
            self.root.win_items = []

    def _on_refresh_clicked(self):
        """Handle refresh button click."""
        logger.debug("[Refresh] Button clicked")
        self.refresh_btn.config(state="disabled", text="⟳")
        self.refresh_btn.update()  # Show loading state immediately

        try:
            self._on_refresh()
            logger.debug(f"[Refresh] Found {len(self.win_items)} windows")
        except Exception as e:
            logger.error(f"[Refresh] Error: {e}")

        # Reset button after 300ms
        def reset_btn():
            self.refresh_btn.config(state="normal", text="🔄")
            logger.debug("[Refresh] Button reset")

        self.refresh_btn.after(300, reset_btn)

    def _update_listbox(self):
        """Update listbox with filtered windows."""
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

    def _on_listbox_select(self, event=None):
        """Handle window selection from listbox."""
        try:
            if not self.listbox:
                return
            sel = self.listbox.curselection()
            if not sel:
                return
            
            selected = self.filtered_windows[sel[0]]
            logger.debug(f"Selected: {selected['title']}")
            
            # Update search entry
            self.search_var.set(selected["title"])
            
            # Fire callback
            self.on_window_selected(selected)
            
            # Close listbox
            self._close_listbox()
        except Exception as e:
            logger.error(f"Selection failed: {e}")

    def _on_search_text_changed(self, event=None):
        """Update listbox as user types."""
        if self.is_open:
            self._update_listbox()
