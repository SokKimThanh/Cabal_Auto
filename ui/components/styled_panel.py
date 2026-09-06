"""Styled panel component matching dark theme design"""

import tkinter as tk
from lib.ui_style_v2 import UIStyleV2 as UI


class StyledPanel(tk.Frame):
    """A panel with border, background, and padding that matches the dark theme"""

    def __init__(self, parent, **kwargs):
        # Extract custom kwargs before passing to Frame
        self.title = kwargs.pop("title", None)
        self.show_border = kwargs.pop("show_border", True)

        if self.show_border:
            kwargs.update({
                "highlightbackground": UI.BORDER_PRIMARY,
                "highlightthickness": 1
            })

        # Initialize frame with dark theme
        super().__init__(parent, bg=UI.BG_SURFACE, **kwargs)

    def get_content_frame(self):
        """Return frame for adding widgets"""
        return self
