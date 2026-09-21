import tkinter as tk
from tkinter import ttk
from lib.ui_style_v2 import UIStyleV2 as UI
from lib.events.event_bus import EventBus, HuntStatusUpdatedEvent, HuntStateChangedEvent

class HuntStatusTicker(tk.Frame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=UI.BG_BASE, **kwargs)
        self.app = app

        # Container for ticker
        self.container = tk.Frame(self, bg=UI.BG_SURFACE)
        self.container.pack(fill=tk.X, expand=True, padx=UI.SPACE_MD, pady=UI.SPACE_SM)

        # Layout: Icon on the left, message on the right
        self.icon_label = tk.Label(
            self.container,
            text="ℹ️",
            bg=UI.BG_SURFACE,
            fg=UI.TEXT_MUTED,
            font=UI.get_font(role="body", size=14)
        )
        self.icon_label.pack(side=tk.LEFT, padx=(UI.SPACE_SM, 0), pady=UI.SPACE_XS)

        self.msg_label = tk.Label(
            self.container,
            text=self.app._t("hunt_status_ticker.idle"),
            bg=UI.BG_SURFACE,
            fg=UI.TEXT_MUTED,
            font=UI.get_font(role="body"),
            anchor="w"
        )
        self.msg_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=UI.SPACE_SM, pady=UI.SPACE_XS)

        # Bind events
        EventBus.bind(HuntStatusUpdatedEvent, self._on_status_msg)
        EventBus.bind(HuntStateChangedEvent, self._on_state_changed)

    def destroy(self):
        EventBus.unbind(HuntStatusUpdatedEvent, self._on_status_msg)
        EventBus.unbind(HuntStateChangedEvent, self._on_state_changed)
        super().destroy()

    def _on_status_msg(self, event: HuntStatusUpdatedEvent):
        # Must execute on the main thread
        self.after(0, lambda: self._update_status_ui(event.status))

    def _on_state_changed(self, event: HuntStateChangedEvent):
        # Must execute on the main thread
        self.after(0, lambda: self._update_state_ui(event.state))

    def _update_status_ui(self, status: str):
        self.msg_label.config(text=status)
        # Briefly flash text slightly brighter, or just keep the current state color
        # In this implementation we will rely on _update_state_ui for color
        # but we can also set it to a default color if we want.
        # It's better to maintain the color set by the current state.

    def _update_state_ui(self, state: str):
        if state == "running":
            self.icon_label.config(text="🔄", fg=UI.TEXT_PRIMARY)
            self.msg_label.config(fg=UI.TEXT_PRIMARY)
        elif state == "error":
            self.icon_label.config(text="⚠️", fg=UI.COLOR_DANGER)
            self.msg_label.config(fg=UI.COLOR_DANGER)
            self.msg_label.config(text=self.app._t("hunt_status_ticker.error"))
        elif state == "searching":
            self.icon_label.config(text="🔍", fg=UI.ACCENT_AMBER)
            self.msg_label.config(fg=UI.ACCENT_AMBER)
        else: # idle or waiting
            self.icon_label.config(text="ℹ️", fg=UI.TEXT_MUTED)
            self.msg_label.config(fg=UI.TEXT_MUTED)
