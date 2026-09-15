import tkinter as tk
from typing import Optional

class UIHelper:
    """Global utility namespace for UI helpers (tooltips, icons)."""

    _tooltips = {}
    _icon_cache = {}

    @classmethod
    def create_tooltip(cls, widget: tk.Widget, text: str):
        """Create a simple tooltip for a widget."""

        def on_enter(event):
            try:
                # Destroy existing if any
                on_leave(event, force=True)
                tooltip = tk.Toplevel()
                tooltip.wm_overrideredirect(True)
                tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

                # We can't import UIStyleV2 easily without circular imports in some cases,
                # so we'll use a hardcoded color or try to import it locally.
                try:
                    from lib.ui_style_v2 import UIStyleV2 as UI
                    bg_color = UI.ACCENT_AMBER
                except ImportError:
                    bg_color = "#fff3cd"

                label = tk.Label(
                    tooltip,
                    text=text,
                    background=bg_color,
                    relief="solid",
                    borderwidth=1,
                    padx=5,
                    pady=3,
                )
                label.pack()
                cls._tooltips[id(widget)] = tooltip
            except Exception:
                # Last-resort: attach to widget (legacy)
                try:
                    widget._tooltip = tooltip
                except Exception:
                    pass

        def on_leave(event, force=False):
            try:
                if not force:
                    # Check if pointer is still within the widget's bounding box
                    x, y = widget.winfo_pointerxy()
                    wx = widget.winfo_rootx()
                    wy = widget.winfo_rooty()
                    ww = widget.winfo_width()
                    wh = widget.winfo_height()
                    if wx <= x <= wx + ww and wy <= y <= wy + wh:
                        # Pointer is still inside the widget
                        return

                if id(widget) in cls._tooltips:
                    try:
                        cls._tooltips[id(widget)].destroy()
                    except Exception:
                        pass
                    try:
                        del cls._tooltips[id(widget)]
                    except Exception:
                        pass
                    return

                # Fallback to widget attribute
                tooltip = getattr(widget, "_tooltip", None)
                if tooltip is not None:
                    try:
                        tooltip.destroy()
                    except Exception:
                        pass
                    try:
                        delattr(widget, "_tooltip")
                    except Exception:
                        pass
            except Exception:
                pass

        widget.bind("<Enter>", on_enter, add="+")
        widget.bind("<Leave>", on_leave, add="+")

    @classmethod
    def destroy_widget_tooltip(cls, widget: tk.Widget):
        """Safely destroy a tooltip for a widget."""
        try:
            if id(widget) in cls._tooltips:
                try:
                    cls._tooltips[id(widget)].destroy()
                except Exception:
                    pass
                try:
                    del cls._tooltips[id(widget)]
                except Exception:
                    pass
                return
            tooltip = getattr(widget, "_tooltip", None)
            if tooltip is not None:
                try:
                    tooltip.destroy()
                except Exception:
                    pass
                try:
                    delattr(widget, "_tooltip")
                except Exception:
                    pass
        except Exception:
            pass

    @classmethod
    def icon(cls, name: str, fallback: str, size: int = 16, color: Optional[str] = None):
        """Fetch an icon image with caching to prevent GC."""
        try:
            key = f"{name}_{size}_{color or 'default'}"
            if key in cls._icon_cache:
                return cls._icon_cache[key]

            try:
                from ui.helpers.icon_helper import get_icon_helper
                helper = get_icon_helper()
                img = helper.get_icon(name, fallback=fallback, size=size, color=color)
            except Exception:
                img = fallback

            cls._icon_cache[key] = img
            return img
        except Exception:
            return fallback
