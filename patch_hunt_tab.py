import re

with open("ui/tabs/hunt_tab.py", "r", encoding="utf-8") as f:
    content = f.read()

# I am returning the icon buttons to the right-hand panel instead of basic text tk.Buttons
# And bringing back the status string to address the reviewer's feedback

replacement = """        # Control buttons (right side)
        btn_container = tk.Frame(list_container)
        btn_container.pack(side="right", fill="y", padx=(8, 0))

        # Add monster button
        self.app.btn_add_monster = self.app._create_icon_button(
            btn_container,
            icon_emoji="➕",
            command=self.app._on_monster_add_smart,
            style="compact",
            bg_color=UI.BTN_ACCENT_BG if hasattr(UI, 'BTN_ACCENT_BG') else UI.COLOR_PRIMARY,
            hover_color=UI.BTN_ACCENT_HOVER if hasattr(UI, 'BTN_ACCENT_HOVER') else UI.COLOR_PRIMARY_TEXT,
        )
        self.app.btn_add_monster.pack(pady=(0, 4))
        self.app._create_tooltip(
            self.app.btn_add_monster, self.app._t("tooltip_add_monster_normal")
        )

        # Priority reorder buttons
        self.app.btn_move_up = self.app._create_icon_button(
            btn_container,
            icon_emoji="↑",
            command=self.app._on_monster_move_up,
            style="compact",
            bg_color=UI.BTN_INFO_BG if hasattr(UI, 'BTN_INFO_BG') else UI.COLOR_INFO,
            hover_color=UI.BTN_INFO_HOVER if hasattr(UI, 'BTN_INFO_HOVER') else UI.COLOR_PRIMARY,
        )
        self.app.btn_move_up.pack(pady=(0, 4))

        self.app.btn_move_down = self.app._create_icon_button(
            btn_container,
            icon_emoji="↓",
            command=self.app._on_monster_move_down,
            style="compact",
            bg_color=UI.BTN_INFO_BG if hasattr(UI, 'BTN_INFO_BG') else UI.COLOR_INFO,
            hover_color=UI.BTN_INFO_HOVER if hasattr(UI, 'BTN_INFO_HOVER') else UI.COLOR_PRIMARY,
        )
        self.app.btn_move_down.pack(pady=(0, 12))

        # Delete button
        self.app.btn_remove_monster = self.app._create_icon_button(
            btn_container,
            icon_emoji="✖",
            command=self.app._on_monster_delete_from_list,
            style="compact",
            bg_color=UI.COLOR_DANGER,
            hover_color=UI.COLOR_WARNING,
        )
        self.app.btn_remove_monster.pack()

        # Current monster status (Restored)
        self.app.monster_status_var = tk.StringVar()
        tk.Label(
            self.app.monster_frame,
            textvariable=self.app.monster_status_var,
            fg=UI.COLOR_PRIMARY,
            font=(UI.FONT_FAMILY, UI.SIZE_TEXT, "bold"),
        ).pack(fill="x", pady=(8, 0))

        # Re-attach bindings
        self.app.monster_rotation_listbox.bind(
            "<<ListboxSelect>>", self.app._on_monster_list_select
        )
        self.app.monster_rotation_listbox.bind(
            "<Delete>", self.app._on_monster_delete_from_list
        )
        self.app.monster_rotation_listbox.bind(
            "<BackSpace>", self.app._on_monster_delete_from_list
        )"""

content = re.sub(r'        # Control buttons \(right side\).*?        self\.app\.monster_rotation_listbox\.bind\(\n            "<BackSpace>", self\.app\._on_monster_delete_from_list\n        \)', replacement, content, flags=re.DOTALL)

with open("ui/tabs/hunt_tab.py", "w", encoding="utf-8") as f:
    f.write(content)
