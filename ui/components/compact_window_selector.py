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
        print(f"[CompactWindowSelector] __init__ called")
        self.parent = parent
        self.on_window_selected = on_window_selected
        self.window_controller = window_controller
        self.root = root
        
        self.win_items: List[Dict[str, Any]] = []
        self.filtered_windows: List[Dict[str, Any]] = []
        self.is_open = False
        
        self._build_ui()
        print(f"[CompactWindowSelector] __init__ complete")

    def _build_ui(self):
        """Build the compact window selector UI."""
        # Main frame
        self.frame = tk.Frame(self.parent, bg=self.parent.cget("bg"))
        
        # Search frame (always visible)
        self.search_frame = tk.Frame(self.frame, bg=self.parent.cget("bg"))
        self.search_frame.pack(fill="x", expand=False)
        
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
            command=self._on_refresh,
            cursor="hand2",
        )
        self.refresh_btn.pack(side="left")
        
        # Dropdown listbox (hidden until toggled)
        self.dropdown_frame = tk.Frame(self.frame, bg="#1a1a1a", relief="solid", bd=1)
        
        scrollbar = tk.Scrollbar(self.dropdown_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox = tk.Listbox(
            self.dropdown_frame,
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
        
        # Info label
        self.info_label = tk.Label(
            self.frame,
            text="Click refresh to load windows",
            font=("Arial", 8),
            bg=self.parent.cget("bg"),
            fg="#6b7280",
        )
        self.info_label.pack(fill="x", pady=(2, 0))

    def get_frame(self) -> tk.Frame:
        """Return the main frame for grid/pack."""
        return self.frame

    def _on_refresh(self):
        """Refresh window list."""
        print(f"[CompactWindowSelector] _on_refresh() called")
        logger.debug("CompactWindowSelector._on_refresh() called")
        try:
            self.win_items = self.window_controller._list_windows()
            # Update app.win_items for validation
            self.root.win_items = self.win_items
            print(f"[CompactWindowSelector] Found {len(self.win_items)} windows")
            logger.debug(f"  Found {len(self.win_items)} windows")
            self._update_listbox()
            self.info_label.config(
                text=f"✓ Found {len(self.win_items)} window(s)",
                fg="#4ade80"
            )
            print(f"[CompactWindowSelector] Info label updated, listbox has {self.listbox.size()} items")
        except Exception as e:
            print(f"[CompactWindowSelector] Failed to refresh: {e}")
            logger.error(f"  Failed to refresh: {e}")
            self.info_label.config(
                text=f"Error: {e}",
                fg="#dc2626"
            )
            self.win_items = []
            self.root.win_items = []

    def _on_search_focus_in(self, event=None):
        """Show dropdown when search box focused."""
        if not self.is_open:
            self._toggle_dropdown()

    def _on_search_text_changed(self, event=None):
        """Filter listbox as user types."""
        if self.is_open:
            self._update_listbox()

    def _on_search_enter(self, event=None):
        """Select first item on Enter."""
        if self.listbox.size() > 0:
            self.listbox.selection_set(0)
            self._on_listbox_select()

    def _toggle_dropdown(self):
        """Toggle dropdown visibility."""
        print(f"[CompactWindowSelector] _toggle_dropdown() called, is_open={self.is_open}")
        if self.is_open:
            self.dropdown_frame.pack_forget()
            self.is_open = False
            self.dropdown_btn.config(text="▼")
        else:
            if not self.win_items:
                print(f"[CompactWindowSelector] No items, calling _on_refresh()")
                self._on_refresh()
            self.dropdown_frame.pack(fill="both", expand=True, pady=(2, 0))
            self._update_listbox()
            self.is_open = True
            self.dropdown_btn.config(text="▲")
            self.search_entry.focus()
            print(f"[CompactWindowSelector] Dropdown opened with {self.listbox.size()} items")

    def _update_listbox(self):
        """Update listbox with filtered windows."""
        search_text = self.search_var.get().lower()
        print(f"[CompactWindowSelector] _update_listbox() called, search='{search_text}', items={len(self.win_items)}")
        
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
        
        print(f"[CompactWindowSelector] Listbox updated: {self.listbox.size()} items shown")
        
        if self.filtered_windows:
            self.listbox.selection_set(0)
            self.listbox.activate(0)

    def _on_listbox_select(self, event=None):
        """Handle window selection from listbox."""
        try:
            sel = self.listbox.curselection()
            if not sel:
                return
            
            selected = self.filtered_windows[sel[0]]
            logger.debug(f"Selected window: {selected['title']}")
            
            # Update search entry with selection
            self.search_var.set(selected["title"])
            
            # Close dropdown
            if self.is_open:
                self._toggle_dropdown()
            
            # Call callback
            self.on_window_selected(selected)
            
        except Exception as e:
            logger.error(f"Error on window select: {e}")

    def set_search_text(self, text: str):
        """Set search entry text programmatically."""
        self.search_var.set(text)

    def get_selected_window(self) -> Optional[Dict[str, Any]]:
        """Get currently selected window dict."""
        try:
            sel = self.listbox.curselection()
            if sel:
                return self.filtered_windows[sel[0]]
        except Exception:
            pass
        return None
