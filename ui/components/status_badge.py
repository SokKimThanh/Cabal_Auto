"""Status badge component with color variants"""

import tkinter as tk
from lib.ui_style_v2 import UIStyleV2 as UI
from lib.ui.animation_manager import UIAnimationManager


class StatusBadge(tk.Frame):
    """Status badge with icon and text"""

    STATUS_STYLES = {
        "waiting": {
            "bg": "#292218",  # Dark brown
            "fg": UI.TEXT_PRIMARY,  # White text for high contrast
            "icon": "record",
        },
        "ready": {
            "bg": UI.ACCENT_GREEN_BG,  # Green bg
            "fg": UI.TEXT_PRIMARY,  # White text for high contrast
            "icon": "record",
        },
        "hunting": {
            "bg": "#1e2d3d",  # Dark blue
            "fg": UI.TEXT_PRIMARY,  # White text for high contrast
            "icon": "record",
            "animate": True,
        },
    }

    def __init__(self, parent, app=None, status="waiting", **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.status = status
        self.animation_manager = UIAnimationManager()
        self.config(bg=UI.BG_BASE, highlightthickness=0)

        style = self._get_style(status)

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

    def _get_style(self, status):
        """Retrieve style with dynamic i18n label."""
        style = dict(self.STATUS_STYLES.get(status, self.STATUS_STYLES["waiting"]))

        defaults = {
            "waiting": "Waiting",
            "ready": "Ready",
            "hunting": "Hunting",
        }

        if self.app and hasattr(self.app, "_t"):
            style["label"] = self.app._t(f"target_status.badge_{status}", default=defaults.get(status, status))
        else:
            style["label"] = defaults.get(status, status)

        return style

    def _animate_pulse(self):
        """Pulse animation for hunting state"""
        if hasattr(self, 'animation_manager'):
            self.animation_manager.cancel_tween(f"badge_pulse_{id(self)}")

        def update_func(val):
            if hasattr(self, "icon_label") and self.icon_label.winfo_exists():
                if val >= 1:
                    current_fg = self.icon_label.cget("fg")
                    style = self._get_style(self.status)

                    if current_fg == style["fg"]:
                        self.icon_label.config(fg="#5a9fd4")  # slightly dimmed
                    else:
                        self.icon_label.config(fg=style["fg"])

                    # Loop animation
                    self._animate_pulse()

        self.animation_manager.register_tween(
            target_id=f"badge_pulse_{id(self)}",
            widget=self,
            start_val=0,
            end_val=1,
            duration_ms=500,
            update_func=update_func
        )

    def set_status(self, status):
        """Update badge status"""
        if status in self.STATUS_STYLES:
            self.status = status
            style = self._get_style(status)

            if hasattr(self, 'animation_manager'):
                self.animation_manager.cancel_tween(f"badge_pulse_{id(self)}")

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
