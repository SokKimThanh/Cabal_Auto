# -*- coding: utf-8 -*-
"""
Screen Region Capture Overlay Component for Monster Editor.
Provides transparent modal canvas for click-and-drag area capture.
"""

from __future__ import annotations
import tkinter as tk
from typing import Optional, Tuple


class RegionCaptureOverlay(tk.Toplevel):
    """Overlay window for selecting a screen region."""

    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        self.parent = parent
        self.withdraw()
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        try:
            self.attributes("-alpha", 0.25)
        except Exception:
            pass
        self.configure(bg="black")
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
        self.canvas = tk.Canvas(
            self, bg="black", highlightthickness=0, cursor="crosshair"
        )
        self.canvas.pack(fill="both", expand=True)
        self._start: Optional[Tuple[int, int, int, int]] = None
        self._rect: Optional[int] = None
        self._bbox: Optional[Tuple[int, int, int, int]] = None

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Escape>", lambda e: self._cancel())

    def show_modal(self) -> Optional[Tuple[int, int, int, int]]:
        self.deiconify()
        self.grab_set()
        self.focus_force()
        self.wait_window(self)
        return self._bbox

    def _on_press(self, event: tk.Event) -> None:
        self._start = (event.x, event.y, event.x_root, event.y_root)
        if self._rect is not None:
            self.canvas.delete(self._rect)
            self._rect = None
        self._rect = self.canvas.create_rectangle(
            event.x, event.y, event.x, event.y, outline="#00E5FF", width=2
        )

    def _on_drag(self, event: tk.Event) -> None:
        if self._start and self._rect:
            x0, y0, _, _ = self._start
            x1, y1 = event.x, event.y
            self.canvas.coords(self._rect, x0, y0, x1, y1)

    def _on_release(self, event: tk.Event) -> None:
        if not self._start:
            self.destroy()
            return
        x0, y0, xr0, yr0 = self._start
        x1, y1 = event.x, event.y
        dx = xr0 - x0
        dy = yr0 - y0
        left = int(min(x0 + dx, x1 + dx))
        top = int(min(y0 + dy, y1 + dy))
        right = int(max(x0 + dx, x1 + dx))
        bottom = int(max(y0 + dy, y1 + dy))
        if right - left < 5 or bottom - top < 5:
            self._bbox = None
        else:
            self._bbox = (left, top, right, bottom)
        self.destroy()

    def _cancel(self) -> None:
        self._bbox = None
        self.destroy()
