import tkinter as tk
from tkinter import ttk
from lib.ui_style_v2 import UIStyleV2 as UI


class HelpTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=12)
        self.app = app
        self._panels = {}
        self._build_ui()

    def _build_ui(self):
        title = ttk.Label(
            self,
            text=self.app._t("tab_help") if hasattr(self.app, "_t") else "Help & Support",
            font=UI.FONT_TITLE,
        )
        title.pack(anchor="w", pady=(0, 16))

        # Add collapsible panels
        self._create_collapsible_panel(
            "hunt",
            self.app._t("help_hunt_title") if hasattr(self.app, "_t") else "1. Hunt Screen Reminders",
            self.app._t("help_hunt_desc") if hasattr(self.app, "_t") else "Hunt description..."
        )

        self._create_collapsible_panel(
            "setup",
            self.app._t("help_setup_title") if hasattr(self.app, "_t") else "2. Setup Screen Reminders",
            self.app._t("help_setup_desc") if hasattr(self.app, "_t") else "Setup description..."
        )

        self._create_collapsible_panel(
            "stats",
            self.app._t("help_stats_title") if hasattr(self.app, "_t") else "3. Stats & Logs Reminders",
            self.app._t("help_stats_desc") if hasattr(self.app, "_t") else "Stats description..."
        )

    def _create_collapsible_panel(self, panel_id, title_text, desc_text):
        container = tk.Frame(self, bg=UI.BG_BASE)
        container.pack(fill="x", pady=(0, UI.SPACE_MD))

        # Top bar with title and toggle button
        top_bar = tk.Frame(container, bg=UI.BG_SURFACE)
        top_bar.pack(fill="x")

        # Let the entire top bar act as a button
        title_btn = tk.Button(
            top_bar,
            text=f"▶ {title_text}",
            font=UI.FONT_BOLD,
            anchor="w",
            padx=UI.SPACE_MD,
            pady=UI.SPACE_SM,
            **UI.get_button_style('secondary')
        )
        title_btn.pack(fill="x")

        # Content frame (hidden by default)
        content_frame = tk.Frame(container, bg=UI.BG_BASE, padx=UI.SPACE_MD, pady=UI.SPACE_SM)


        # Content text with wraplength binding to container
        content_lbl = tk.Label(
            content_frame,
            text=desc_text,
            font=UI.FONT_BODY,
            fg=UI.TEXT_PRIMARY,
            bg=UI.BG_BASE,
            justify="left",
            anchor="w"
        )
        content_lbl.pack(fill="both", expand=True)

        def on_resize(event, lbl=content_lbl):
            # Dynamic wrap length based on event width with some padding
            if event.width > 20:
                lbl.config(wraplength=event.width - 20)

        container.bind('<Configure>', on_resize)


        is_open = tk.BooleanVar(value=False)
        self._panels[panel_id] = {
            "btn": title_btn,
            "content": content_frame,
            "is_open": is_open,
            "title": title_text
        }

        # Toggle action
        def toggle(*args, pid=panel_id):
            p = self._panels[pid]
            state = not p["is_open"].get()
            p["is_open"].set(state)
            if state:
                p["content"].pack(fill="x")
                p["btn"].config(text=f"▼ {p['title']}")
            else:
                p["content"].pack_forget()
                p["btn"].config(text=f"▶ {p['title']}")

        title_btn.config(command=toggle)
