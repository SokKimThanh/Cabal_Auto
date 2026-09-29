import time
import tkinter as tk
from tkinter import ttk
from lib.ui_style_v2 import UIStyleV2 as UI
from lib.events.event_bus import EventBus, HuntStatusUpdatedEvent, HuntStateChangedEvent
from ui.components.icon_button import create_icon_label
from ui.helpers.icon_helper import get_icon_helper

class HuntStatusTicker(tk.Frame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=UI.BG_BASE, **kwargs)
        self.app = app
        self._icon_helper = get_icon_helper()
        # Ensure image reference is kept
        self._icon_ref = None

        # Container for ticker
        self.container = tk.Frame(self, bg=UI.BG_SURFACE)
        self.container.pack(fill=tk.X, expand=True, padx=UI.SPACE_MD, pady=UI.SPACE_SM)

        # Layout: Icon on the left, message on the right
        self.icon_label = create_icon_label(
            self.container,
            icon_name="info",
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
        self._last_status_time = time.time()
        # Briefly flash text slightly brighter, or just keep the current state color
        # In this implementation we will rely on _update_state_ui for color
        # but we can also set it to a default color if we want.
        # It's better to maintain the color set by the current state.

    def _set_icon(self, icon_name: str, color: str):
        img = self._icon_helper.get_icon(icon_name, size=16, color=color)
        if isinstance(img, str):
            self.icon_label.config(image="", text=img, fg=color)
        else:
            self._icon_ref = img
            self.icon_label.config(image=img, text="", fg=color)

    def _update_state_ui(self, state: str):
        if state == "running":
            self._set_icon("db-sync", UI.TEXT_PRIMARY)
            self.msg_label.config(fg=UI.TEXT_PRIMARY)
        elif state == "error":
            self._set_icon("warning", UI.COLOR_DANGER)
            self.msg_label.config(fg=UI.COLOR_DANGER)
            if time.time() - getattr(self, "_last_status_time", 0) > 0.5:
                self.msg_label.config(text=self.app._t("hunt_status_ticker.error"))
        elif state == "searching":
            self._set_icon("search", UI.ACCENT_AMBER)
            self.msg_label.config(fg=UI.ACCENT_AMBER)
        else: # idle or waiting
            self._set_icon("info", UI.TEXT_MUTED)
            self.msg_label.config(fg=UI.TEXT_MUTED)
