import re

with open("ui/tabs/hunt_tab.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the frame setup with new Treeview for Monster Rotation
replacement_ui = """        self.app.monster_frame = tk.LabelFrame(
            self, text=self.app._t("monster_rotation.title"), font=UI.FONT_SECTION, fg=UI.COLOR_TEXT, padx=10, pady=8
        )
        self.app.monster_frame.grid(
            row=0, column=0, sticky="new", padx=(0, 6), pady=(0, 12)
        )
        self.app.monster_frame.grid_columnconfigure(0, weight=1)

        # Rotation mode selection
        mode_bar = tk.Frame(self.app.monster_frame)
        mode_bar.pack(fill="x", pady=(0, 8))
        tk.Label(mode_bar, text=self.app._t("rotation_mode"), font=UI.FONT_LABEL).pack(side="left")

        self.app.rotation_mode_var = tk.StringVar(
            value=self.app.hunt_cfg.get("rotation_mode", "sequence")
        )
        self.app.rotation_mode_combo = ttk.Combobox(
            mode_bar,
            textvariable=self.app.rotation_mode_var,
            state="readonly",
            width=12,
            values=["sequence", "priority"],
        )
        self.app.rotation_mode_combo.pack(side="left", padx=(6, 0))
        self.app.rotation_mode_combo.bind(
            "<<ComboboxSelected>>", self.app._on_rotation_mode_changed
        )

        # Mode description
        self.app.rotation_desc_var = tk.StringVar()
        tk.Label(
            mode_bar, textvariable=self.app.rotation_desc_var, fg=UI.COLOR_SUBTEXT, font=UI.FONT_TEXT
        ).pack(side="left", padx=(8, 0))

        # Monster list with checkboxes (repurposed to treeview)
        list_container = tk.Frame(self.app.monster_frame)
        list_container.pack(fill="both", expand=True)

        # Listbox frame with scrollbar
        listbox_frame = tk.Frame(list_container)
        listbox_frame.pack(side="left", fill="both", expand=True)

        self.app.monster_rotation_listbox = tk.Listbox(
            listbox_frame,
            height=5,
            exportselection=False,
            selectmode="single",
            font=UI.FONT_TEXT,
        )
        self.app.monster_rotation_listbox.pack(side="left", fill="both", expand=True)

        monster_scroll = tk.Scrollbar(
            listbox_frame,
            orient="vertical",
            command=self.app.monster_rotation_listbox.yview,
        )
        monster_scroll.pack(side="right", fill="y")
        self.app.monster_rotation_listbox.config(yscrollcommand=monster_scroll.set)

        # Control buttons (right side)
        btn_container = tk.Frame(list_container)
        btn_container.pack(side="right", fill="y", padx=(8, 0))

        # Add monster button
        self.app.btn_add_monster = tk.Button(
            btn_container,
            text="+",
            command=self.app._on_monster_add_smart,
            font=UI.FONT_BUTTON,
            width=2,
            bg=UI.COLOR_PRIMARY,
            fg="white"
        )
        self.app.btn_add_monster.pack(pady=(0, 4))

        # Up button
        self.app.btn_move_up = tk.Button(
            btn_container,
            text="↑",
            command=self.app._on_monster_move_up,
            font=UI.FONT_BUTTON,
            width=2,
        )
        self.app.btn_move_up.pack(pady=(0, 4))

        # Down button
        self.app.btn_move_down = tk.Button(
            btn_container,
            text="↓",
            command=self.app._on_monster_move_down,
            font=UI.FONT_BUTTON,
            width=2,
        )
        self.app.btn_move_down.pack(pady=(0, 16))

        # Delete button
        self.app.btn_remove_monster = tk.Button(
            btn_container,
            text="X",
            command=self.app._on_monster_delete_from_list,
            font=UI.FONT_BUTTON,
            width=2,
            bg=UI.COLOR_DANGER,
            fg="white"
        )
        self.app.btn_remove_monster.pack()

        # Remove library manager button calls and old status labels
        self.app.monster_rotation_listbox.bind(
            "<<ListboxSelect>>", self.app._on_monster_list_select
        )
        self.app.monster_rotation_listbox.bind(
            "<Delete>", self.app._on_monster_delete_from_list
        )
        self.app.monster_rotation_listbox.bind(
            "<BackSpace>", self.app._on_monster_delete_from_list
        )"""

content = re.sub(r'        self\.app\.monster_frame = tk\.LabelFrame\(.*?        self\.app\.monster_rotation_listbox\.bind\(\n            "<BackSpace>", self\.app\._on_monster_delete_from_list\n        \)', replacement_ui, content, flags=re.DOTALL)

with open("ui/tabs/hunt_tab.py", "w", encoding="utf-8") as f:
    f.write(content)
