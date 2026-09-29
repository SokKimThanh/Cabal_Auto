"""Empty state component for panels with no data"""

import tkinter as tk
from lib.ui_style_v2 import UIStyleV2 as UI
from ui.components.icon_button import create_icon_label

class EmptyState(tk.Frame):
    """Display empty state with icon, message, and guidance"""

    def __init__(self, parent, icon="info", message="No data", submessage="", wraplength=300, **kwargs):
        super().__init__(parent, bg=UI.BG_BASE, **kwargs)

        # Use expand to center contents vertically
        container = tk.Frame(self, bg=UI.BG_BASE)
        container.pack(expand=True)

        # Icon (large, muted)
        icon_label = create_icon_label(
            container,
            icon_name=icon,
            icon_size=48,
            font=(UI.FONT_FAMILY_UI_FALLBACK, 48),
            bg=UI.BG_BASE,
            fg=UI.TEXT_MUTED,
        )
        icon_label.pack(pady=(10, 10))

        # Main message
        msg_label = tk.Label(
            container, text=message, font=UI.FONT_SECTION, bg=UI.BG_BASE, fg=UI.TEXT_PRIMARY
        )
        msg_label.pack(pady=5)

        # Sub-message
        if submessage:
            sub_label = tk.Label(
                container,
                text=submessage,
                font=UI.FONT_SMALL,
                bg=UI.BG_BASE,
                fg=UI.TEXT_MUTED,
                wraplength=wraplength,
            )
            sub_label.pack(pady=10)
