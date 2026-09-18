import tkinter as tk
from typing import Any, Callable

from lib.ui_style_v2 import UIStyleV2 as UI
from ui.utils.component_registry import get_component_registry

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
            ("btn_build_manager", "build_manager", UI.FONT_SECTION, "build_manager", "build_manager"),
            ("btn_skill_manager", "skill_manager", UI.FONT_SECTION, "skill_manager", "⚔️"),
            ("btn_monster_manager", "monster_manager", UI.FONT_SECTION, "monster_manager", "🐉"),
            ("btn_class_manager", "class_manager", UI.FONT_SECTION, "class_manager", "class_manager"),
            ("btn_icon_manager", "icon_manager", UI.FONT_SECTION, "icon_manager", "icon_manager"),
            ("btn_scan_history", "scan_history", UI.FONT_SECTION, "scan_history", "scan_history"),
            ("sidebar_activity_logs", "logs", UI.FONT_SECTION, "logs", "logs"),
            ("tab_stats", "stats", UI.FONT_SECTION, "stats", "stats"),
            ("btn_language_manager", "language_manager", UI.FONT_SECTION, "language_manager", "language_manager"),
            ("sidebar_support", "help", UI.FONT_SECTION, "help", "help"),
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

            # Auto-register sidebar buttons to the Component Registry
            if isinstance(icon, str):
                # Create a human readable name from the view_target, e.g., 'class_manager' -> 'Class Manager'
                human_name = ' '.join(word.capitalize() for word in view_target.split('_'))
                get_component_registry().register_component(
                    name=f"Sidebar: {human_name}",
                    mod="ui",
                    comp="sidebar_button",
                    element_id=icon
                )

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

                btn._icon_name = icon
                if is_image_icon and icon_img and not isinstance(icon_img, str):
                    btn.config(image=icon_img)
                    btn.image = icon_img
                else:
                    # Fix misalignment for certain emoji characters like 🛠️ by not adding spaces around them
                    btn.config(text=f"{icon}")

                apply_button_hover_effects(
                    btn, hover_color=UI.BG_SURFACE
                )

                btn.pack(fill="both", expand=True)
                self._sidebar_widgets.append(SidebarWidgetDef(widget=btn, key=key, view_target=view_target, icon=icon))

                                # Check if icon has a database tooltip key, otherwise use fallback
                tooltip_key_to_use = key
                if hasattr(self.icon_helper, "get_icon_tooltip_key"):
                    db_tooltip_key = self.icon_helper.get_icon_tooltip_key(icon)
                    if db_tooltip_key:
                        tooltip_key_to_use = db_tooltip_key

                # Add tooltip
                # Follow memory rule: Database-backed tooltip key takes precedence over widget key
                tooltip_key = key
                if hasattr(icon_helper, "get_icon_tooltip_key"):
                    # Use the raw icon string which acts as the icon name
                    db_tooltip_key = icon_helper.get_icon_tooltip_key(icon)
                    if db_tooltip_key:
                        tooltip_key = db_tooltip_key

                attach_i18n_tooltip(
                    btn,
                    key=tooltip_key,
                    ns="global",
                    lang_provider=lambda: getattr(self.app, "lang", "en"),
                )

    def set_active_tab(self, active_view: str):
        for item in self._sidebar_widgets:
            if isinstance(item.widget, tk.Button):
                is_active = item.view_target == active_view or (item.view_target == "hunt" and active_view == "window_selector")
                item.widget._sidebar_active = is_active

                target_bg = UI.BG_SURFACE if is_active else UI.BG_ELEVATED
                target_fg = UI.ACCENT_GREEN if is_active else UI.TEXT_PRIMARY

                item.widget.config(bg=target_bg, fg=target_fg)

                # Fetch fresh icon (may be image or text/emoji)
                if hasattr(self, "icon_helper") and hasattr(item.widget, "_icon_name"):
                    new_icon = self.icon_helper.get_icon(item.widget._icon_name, size=24, color=target_fg)

                    if new_icon and not isinstance(new_icon, str):
                        item.widget.config(image=new_icon, text="")
                        item.widget.image = new_icon
                    else:
                        item.widget.config(image="", text=f"{new_icon if isinstance(new_icon, str) else item.icon}")
                        item.widget.image = None
                else:
                    item.widget.config(image="", text=f"{item.icon}")
                    item.widget.image = None

    def update_translations(self):
        """Update i18n text for sidebar elements."""
        for item in self._sidebar_widgets:
            # We only really update tooltip, text labels for sidebar are not dynamic texts but tooltips are
            pass # handled by tooltip update
