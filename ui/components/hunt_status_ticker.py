import tkinter as tk
from tkinter import ttk
from lib.events.event_bus import EventBus, HuntStatusUpdatedEvent, HuntStateChangedEvent
from lib.ui_style_v2 import UIStyleV2 as UI

class HuntStatusTicker(tk.Frame):
    MODULE_NAME = "hunt_status_ticker"

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=UI.BG_BASE, **kwargs)
        self.app = app

        self.grid_columnconfigure(1, weight=1)

        # Icon/Status indicator
        self.icon_label = tk.Label(
            self,
            text="ℹ",
            font=UI.get_font(role="body", weight="bold"),
            fg=UI.TEXT_MUTED,
            bg=UI.BG_BASE,
            padx=UI.SPACE_SM
        )
        self.icon_label.grid(row=0, column=0, sticky="w")

        # Text Message
        self.message_label = tk.Label(
            self,
            text=self.app._t("hunt.status_ready") if hasattr(self.app, "_t") else "Ready",
            font=UI.get_font(role="body"),
            fg=UI.TEXT_PRIMARY,
            bg=UI.BG_BASE,
            anchor="w"
        )
        self.message_label.grid(row=0, column=1, sticky="ew")

        # Initial style setup
        self._set_style("waiting")

        # Bind events
        self._bind_events()

    def _bind_events(self):
        EventBus.bind(HuntStatusUpdatedEvent, self._on_status_msg)
        EventBus.bind(HuntStateChangedEvent, self._on_state_changed)

    def _on_status_msg(self, event: HuntStatusUpdatedEvent):
        # Must run in UI thread
        msg = event.status
        self.after(0, lambda m=msg: self._update_ui_msg(m))

    def _on_state_changed(self, event: HuntStateChangedEvent):
        # Must run in UI thread
        state = event.state
        self.after(0, lambda s=state: self._update_ui_state(s))

    def _update_ui_msg(self, msg: str):
        # If it's an error message
        if msg.lower().startswith("error"):
            self.icon_label.config(text="⚠", fg=UI.COLOR_DANGER)
            self.message_label.config(text=msg, fg=UI.COLOR_DANGER)
        elif "retrying" in msg.lower() or "timeout" in msg.lower():
            self.icon_label.config(text="↻", fg=UI.ACCENT_AMBER)
            self.message_label.config(text=msg, fg=UI.ACCENT_AMBER)
        else:
            self.message_label.config(text=msg)

            # Reset icon based on current tracked state if it wasn't an error
            # For simplicity, if we receive a standard message, we'll keep the text color normal
            # unless it overrides based on some local logic.
            # Usually the color is set by HuntStateChangedEvent but we can just set text primary here.
            self.message_label.config(fg=UI.TEXT_PRIMARY)

    def _update_ui_state(self, state: str):
        self._set_style(state)

    def _set_style(self, state: str):
        if state == "hunting":
            self.icon_label.config(text="⚡", fg=UI.ACCENT_BLUE)
            self.message_label.config(fg=UI.ACCENT_BLUE)
            if hasattr(self.app, "_t"):
                self.message_label.config(text=self.app._t("hunt.state_hunting"))
        elif state == "waiting" or state == "ready" or state == "stopped":
            self.icon_label.config(text="ℹ", fg=UI.TEXT_MUTED)
            self.message_label.config(fg=UI.TEXT_PRIMARY)
            if hasattr(self.app, "_t"):
                self.message_label.config(text=self.app._t("hunt.status_ready"))
        elif state == "error":
            self.icon_label.config(text="⚠", fg=UI.COLOR_DANGER)
            self.message_label.config(fg=UI.COLOR_DANGER)
        elif state == "scanning":
            self.icon_label.config(text="↻", fg=UI.ACCENT_AMBER)
            self.message_label.config(fg=UI.ACCENT_AMBER)
            if hasattr(self.app, "_t"):
                self.message_label.config(text=self.app._t("hunt.state_scanning"))
        else:
            self.icon_label.config(text="ℹ", fg=UI.TEXT_MUTED)
            self.message_label.config(fg=UI.TEXT_PRIMARY)
