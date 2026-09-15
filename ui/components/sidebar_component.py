import tkinter as tk
from typing import Any, Callable

from lib.ui_style_v2 import UIStyleV2 as UI
from ui.helpers.icon_helper import get_icon_helper
from ui.helpers.tooltip import attach_i18n_tooltip

class SidebarWidgetDef:
    widget: Any
    key: str
    view_target: str
    icon: str

    def __init__(self, widget, key, view_target, icon):
        self.widget = widget
        self.key = key
        self.view_target = view_target
        self.icon = icon

class SidebarComponent(tk.Frame):
    def __init__(self, parent, app, on_navigate_callback: Callable[[str], None], *args, **kwargs):
        super().__init__(parent, bg=UI.BG_BASE, *args, **kwargs)
        self.app = app
        self.on_navigate_callback = on_navigate_callback
        self._sidebar_widgets = []
        self._image_refs = []  # Prevents garbage collection of icons

        self._build()

    def _build(self):
        try:
            dpi_percent = self.tk.call("tk", "scaling") * 72
            scale_factor = dpi_percent / 100.0
        except Exception:
            scale_factor = 1.0

        sidebar_menu_size = int(56 * scale_factor)

        # Build Sidebar Navigation
        sidebar_items = [
            ("tab_hunt", "hunt", UI.FONT_SECTION, "hunt", "🎯"),
            ("tab_setup", "setup", UI.FONT_SECTION, "setup", "⚙️"),
            ("btn_build_manager", "build_manager", UI.FONT_SECTION, "build_manager", "🛠️"),
            ("btn_skill_manager", "skill_manager", UI.FONT_SECTION, "skill_manager", "⚔️"),
            ("btn_monster_manager", "monster_manager", UI.FONT_SECTION, "monster_manager", "🐉"),
            ("btn_class_manager", "class_manager", UI.FONT_SECTION, "class_manager", "shield"),
            ("btn_icon_manager", "icon_manager", UI.FONT_SECTION, "icon_manager", "icon_manager"),
            ("btn_scan_history", "scan_history", UI.FONT_SECTION, "scan_history", "🕒"),
            ("sidebar_activity_logs", "logs", UI.FONT_SECTION, "logs", "📋"),
            ("tab_stats", "stats", UI.FONT_SECTION, "stats", "📊"),
            ("btn_language_manager", "language_manager", UI.FONT_SECTION, "language_manager", "🌐"),
            ("sidebar_support", "help", UI.FONT_SECTION, "help", "❓"),
        ]

        def apply_button_hover_effects(button, hover_color=None):
            """Apply hover effects to a Tkinter button"""
            default_bg = button.cget("bg")
            default_fg = button.cget("fg")

            hover_bg = hover_color or UI.BORDER_PRIMARY
            hover_fg = UI.TEXT_PRIMARY if hover_color else default_fg

            def on_enter(event):
                if not getattr(button, "_sidebar_active", False):
                    button.config(bg=hover_bg, fg=hover_fg, relief="flat")

            def on_leave(event):
                if not getattr(button, "_sidebar_active", False):
                    button.config(bg=default_bg, fg=default_fg, relief="flat")

            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)

        icon_helper = get_icon_helper()
        self.icon_helper = icon_helper

        for _item_idx, item in enumerate(sidebar_items):
            key, view_target, font, _unused_target, icon = item

            # command needs a lambda capturing the current view_target
            # using default argument `t=view_target` prevents late binding issues
            command = lambda t=view_target: self.on_navigate_callback(t)

            # Resolve icon: Use PhotoImage if it's a known non-emoji string, otherwise treat as emoji/text
            is_image_icon = False
            icon_img = None
            if isinstance(icon, str) and len(icon) > 2 and hasattr(icon_helper, "has_icon_file") and icon_helper.has_icon_file(icon):
                is_image_icon = True
                icon_img = icon_helper.get_icon(icon, size=24, color=UI.TEXT_PRIMARY)
                if icon_img:
                    self._image_refs.append(icon_img) # keep ref to avoid gc

            if command is None:
                lbl = tk.Label(
                    self,
                    bg=UI.BG_ELEVATED,
                    fg=UI.TEXT_SECONDARY,
                    font=font,
                    anchor="w",
                )
                if is_image_icon and icon_img and not isinstance(icon_img, str):
                    lbl.config(image=icon_img)
                    lbl.image = icon_img
                else:
                    lbl.config(text=f"{icon}")
                lbl.pack(fill="x", pady=(10, 4))
                self._sidebar_widgets.append(SidebarWidgetDef(widget=lbl, key=key, view_target=view_target, icon=icon))
            else:
                menu_cell = tk.Frame(
                    self,
                    bg=UI.BG_ELEVATED,
                    width=sidebar_menu_size,
                    height=sidebar_menu_size,
                )
                menu_cell.pack(pady=2)
                menu_cell.pack_propagate(False)

                btn = tk.Button(
                    menu_cell,
                    command=command,
                    bg=UI.BG_ELEVATED,
                    fg=UI.TEXT_PRIMARY,
                    font=UI.FONT_TITLE,
                    anchor="center",
                    padx=0,
                    pady=0,
                    relief="flat",
                    cursor="hand2",
                )

                if is_image_icon and icon_img and not isinstance(icon_img, str):
                    btn.config(image=icon_img)
                    btn.image = icon_img
                    btn._icon_name = icon
                else:
                    btn.config(text=f" {icon} ")

                apply_button_hover_effects(
                    btn, hover_color=UI.BG_SURFACE
                )

                btn.pack(fill="both", expand=True)
                self._sidebar_widgets.append(SidebarWidgetDef(widget=btn, key=key, view_target=view_target, icon=icon))

                # Add tooltip
                attach_i18n_tooltip(
                    btn,
                    key=key,
                    ns="global",
                    lang_provider=lambda: getattr(self.app, "lang", "en"),
                )

    def set_active_tab(self, active_view: str):
        for item in self._sidebar_widgets:
            if isinstance(item.widget, tk.Button):
                is_image = hasattr(item.widget, "image")

                if item.view_target == active_view or (item.view_target == "hunt" and active_view == "window_selector"):
                    item.widget._sidebar_active = True
                    item.widget.config(
                        bg=UI.BG_SURFACE, fg=UI.ACCENT_GREEN
                    )
                    if is_image and hasattr(item.widget, "_icon_name") and hasattr(self, "icon_helper"):
                        new_icon = self.icon_helper.get_icon(item.widget._icon_name, size=24, color=UI.ACCENT_GREEN)
                        item.widget.config(image=new_icon)
                        item.widget.image = new_icon
                    elif not is_image:
                        item.widget.config(text=f" {item.icon} ")
                else:
                    item.widget._sidebar_active = False
                    item.widget.config(
                        bg=UI.BG_ELEVATED, fg=UI.TEXT_PRIMARY
                    )
                    if is_image and hasattr(item.widget, "_icon_name") and hasattr(self, "icon_helper"):
                        new_icon = self.icon_helper.get_icon(item.widget._icon_name, size=24, color=UI.TEXT_PRIMARY)
                        item.widget.config(image=new_icon)
                        item.widget.image = new_icon
                    elif not is_image:
                        item.widget.config(text=f" {item.icon} ")

    def update_translations(self):
        """Update i18n text for sidebar elements."""
        for item in self._sidebar_widgets:
            # We only really update tooltip, text labels for sidebar are not dynamic texts but tooltips are
            pass # handled by tooltip update
