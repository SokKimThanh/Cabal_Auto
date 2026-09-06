"""Empty state component for panels with no data"""

import tkinter as tk
from lib.ui_style_v2 import UIStyleV2 as UI


class EmptyState(tk.Frame):
    """Display empty state with icon, message, and guidance"""

    def __init__(self, parent, icon="•", message="No data", submessage="", **kwargs):
        super().__init__(parent, bg=UI.BG_BASE, **kwargs)

        # Vertical padding
        tk.Frame(self, bg=UI.BG_BASE, height=20).pack()

        # Icon (large, muted)
        icon_label = tk.Label(
            self,
            text=icon,
            font=(UI.FONT_FAMILY_UI_FALLBACK, 48),
            bg=UI.BG_BASE,
            fg=UI.TEXT_MUTED,
            # Note: fg_opacity parameter doesn't exist in standard tkinter label,
            # so we just use the TEXT_MUTED color.
        )
        icon_label.pack(pady=(20, 10))

        # Main message
        msg_label = tk.Label(
            self,
            text=message,
            font=UI.FONT_SECTION,
            bg=UI.BG_BASE,
            fg=UI.TEXT_PRIMARY
        )
        msg_label.pack(pady=5)

        # Sub-message
        if submessage:
            sub_label = tk.Label(
                self,
                text=submessage,
                font=UI.FONT_SMALL,
                bg=UI.BG_BASE,
                fg=UI.TEXT_MUTED,
                wraplength=300
            )
            sub_label.pack(pady=10)
