"""Status badge component with color variants"""

import tkinter as tk
from lib.ui_style_v2 import UIStyleV2 as UI


class StatusBadge(tk.Frame):
    """Status badge with icon and text"""

    STATUS_STYLES = {
        "waiting": {
            "bg": "#292218",  # Dark brown
            "fg": UI.TEXT_PRIMARY,  # White text for high contrast
            "icon": "record",
            "label": "Đang chờ",
        },
        "ready": {
            "bg": UI.ACCENT_GREEN_BG,  # Green bg
            "fg": UI.TEXT_PRIMARY,  # White text for high contrast
            "icon": "record",
            "label": "Sẵn sàng",
        },
        "hunting": {
            "bg": "#1e2d3d",  # Dark blue
            "fg": UI.TEXT_PRIMARY,  # White text for high contrast
            "icon": "record",
            "label": "Đang săn",
            "animate": True,
        },
    }

    def __init__(self, parent, status="waiting", **kwargs):
        super().__init__(parent, **kwargs)
        self.status = status
        self.config(bg=UI.BG_BASE, highlightthickness=0)

        style = self.STATUS_STYLES.get(status, self.STATUS_STYLES["waiting"])

        # Badge background
        self.badge = tk.Frame(self, bg=style["bg"], highlightthickness=0)
        self.badge.pack(fill="both", expand=True, padx=2, pady=2)

        from ui.components.icon_button import create_icon_label

        # Icon + text
        self.icon_label = create_icon_label(
            parent=self.badge,
            element_id=f"badge_{self.status}",
            icon_name=style["icon"],
            icon_fallback="●",
            text=style["label"],
            font=UI.FONT_SMALL,
            bg=style["bg"],
            fg=style["fg"],
            padx=8,
            pady=4,
        )
        self.icon_label.pack()

        # Pulse animation for hunting state
        if style.get("animate"):
            self._animate_pulse()

    def _animate_pulse(self):
        """Pulse animation for hunting state"""
        self.pulse_step = 0
        if hasattr(self, "_pulse_id") and self._pulse_id:
            self.after_cancel(self._pulse_id)
        self._pulse_step()

    def _pulse_step(self):
        """Single pulse step"""
        # Simplified pulse - just change opacity by swapping colors
        # Real implementation would need more complex rendering
        if hasattr(self, "icon_label") and self.icon_label.winfo_exists():
            current_fg = self.icon_label.cget("fg")
            style = self.STATUS_STYLES.get(self.status, self.STATUS_STYLES["waiting"])

            if current_fg == style["fg"]:
                self.icon_label.config(fg="#5a9fd4")  # slightly dimmed
            else:
                self.icon_label.config(fg=style["fg"])

            self._pulse_id = self.after(500, self._pulse_step)

    def set_status(self, status):
        """Update badge status"""
        if status in self.STATUS_STYLES:
            self.status = status
            style = self.STATUS_STYLES[status]

            if hasattr(self, "_pulse_id") and self._pulse_id:
                self.after_cancel(self._pulse_id)
                self._pulse_id = None

            # Reconfigure existing widgets instead of recreating
            if hasattr(self, "badge") and self.badge.winfo_exists():
                self.badge.config(bg=style["bg"])

            if hasattr(self, "icon_label") and self.icon_label.winfo_exists():
                self.icon_label.config(
                    text=style["label"],
                    bg=style["bg"],
                    fg=style["fg"],
                )

            # Restart animation if needed
            if style.get("animate"):
                self._animate_pulse()
