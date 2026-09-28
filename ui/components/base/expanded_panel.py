import tkinter as tk
from tkinter import ttk
from lib.ui_style_v2 import UIStyleV2 as UI
from ui.components.base.responsive_grid_base import ResponsiveGridBase

class ExpandedPanel(tk.Frame):
    """
    A standard expandable/collapsible panel component.
    Wraps its body content in a ResponsiveGridBase to prevent layout breakage when expanded.
    """
    def __init__(self, parent, title="Panel", expanded=False, **kwargs):
        super().__init__(parent, bg=UI.BG_BASE, **kwargs)
        self.is_expanded = expanded
        self.title_text = title

        # Header Frame
        self.header_frame = tk.Frame(self, bg=UI.BG_SURFACE, cursor="hand2")
        self.header_frame.pack(fill=tk.X)
        self.header_frame.bind("<Button-1>", self._toggle)

        # Title Label
        self.title_label = tk.Label(
            self.header_frame,
            text=self._get_title_text(),
            bg=UI.BG_SURFACE,
            fg=UI.TEXT_PRIMARY,
            font=UI.get_font(role="header")
        )
        self.title_label.pack(side=tk.LEFT, padx=UI.SPACE_SM, pady=UI.SPACE_SM)
        self.title_label.bind("<Button-1>", self._toggle)

        # Content Container (ResponsiveGridBase)
        self.body_container = ResponsiveGridBase(self, bg=UI.BG_BASE)
        self.body_frame = self.body_container.get_content_frame()

        if self.is_expanded:
            self.body_container.pack(fill=tk.BOTH, expand=True)

    def _get_title_text(self):
        symbol = "▼" if self.is_expanded else "▶"
        return f"{symbol} {self.title_text}"

    def _toggle(self, event=None):
        self.is_expanded = not self.is_expanded
        self.title_label.config(text=self._get_title_text())

        if self.is_expanded:
            self.body_container.pack(fill=tk.BOTH, expand=True)
        else:
            self.body_container.pack_forget()

    def get_content_frame(self):
        """Returns the frame where child widgets should be placed."""
        return self.body_frame
