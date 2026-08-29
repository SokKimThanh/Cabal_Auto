import re

with open("dialogs/monster_edit.py", "r", encoding="utf-8") as f:
    content = f.read()

new_form_layout = """
        # Compact Two-Column Clean Form Layout
        form_frame = tk.Frame(self.info_tab, bg=UI.BG_DEFAULT)
        form_frame.pack(fill="both", expand=True, padx=25, pady=5)

        # Configure columns for 2-column layout (Label Widget Label Widget)
        form_frame.columnconfigure(1, weight=1, minsize=100)
        form_frame.columnconfigure(3, weight=1, minsize=100)

        # ID (read-only)
        create_icon_label(
            form_frame, icon_name="id", text=i18n_t("monster_id_label", ns="monster_editor", default="ID:"), icon_fallback="🔑", font=UI.FONT_LABEL
        ).grid(row=0, column=0, sticky="w", pady=4)
        self.id_val_label = tk.Label(form_frame, text="<New>", font=UI.FONT_TEXT, bg=UI.BG_DEFAULT, fg=UI.COLOR_SECONDARY_TEXT)
        self.id_val_label.grid(row=0, column=1, sticky="w", pady=4, padx=(12, 0))

        # Name
        create_icon_label(
            form_frame, icon_name="monster", text=i18n_t("monster_name_label", ns="monster_editor", default="Tên quái:"), icon_fallback="👹", font=UI.FONT_LABEL
        ).grid(row=0, column=2, sticky="w", pady=4, padx=(20, 0))
        self.name_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.name_entry.grid(row=0, column=3, sticky="ew", pady=4, padx=(12, 0))

        # Level
        create_icon_label(
            form_frame, icon_name="up", text=i18n_t("monster_level_label", ns="monster_editor", default="Cấp độ:"), icon_fallback="↑", font=UI.FONT_LABEL
        ).grid(row=1, column=0, sticky="w", pady=4)
        self.level_spinbox = tk.Spinbox(form_frame, from_=1, to=999, font=UI.FONT_TEXT)
        self.level_spinbox.grid(row=1, column=1, sticky="ew", pady=4, padx=(12, 0))

        # Priority
        create_icon_label(
            form_frame, icon_name="priority", text=i18n_t("monster_priority_label", ns="monster_editor", default="Độ ưu tiên:"), icon_fallback="🎯", font=UI.FONT_LABEL
        ).grid(row=1, column=2, sticky="w", pady=4, padx=(20, 0))
        self.priority_spinbox = tk.Spinbox(form_frame, from_=1, to=10, font=UI.FONT_TEXT)
        self.priority_spinbox.grid(row=1, column=3, sticky="ew", pady=4, padx=(12, 0))

        # HP
        create_icon_label(
            form_frame, icon_name="hp", text=i18n_t("monster_hp_label", ns="monster_editor", default="HP:"), icon_fallback="❤️", font=UI.FONT_LABEL
        ).grid(row=2, column=0, sticky="w", pady=4)
        self.hp_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.hp_entry.grid(row=2, column=1, sticky="ew", pady=4, padx=(12, 0))

        # Attack Rate
        create_icon_label(
            form_frame, icon_name="speed", text=i18n_t("monster_atk_rate_label", ns="monster_editor", default="Tốc đánh:"), icon_fallback="⚡", font=UI.FONT_LABEL
        ).grid(row=2, column=2, sticky="w", pady=4, padx=(20, 0))
        self.atk_rate_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.atk_rate_entry.grid(row=2, column=3, sticky="ew", pady=4, padx=(12, 0))

        # Primary Attack Min/Max
        create_icon_label(
            form_frame, icon_name="damage", text=i18n_t("monster_primary_atk_min_label", ns="monster_editor", default="Công chính (Min):"), icon_fallback="⚔️", font=UI.FONT_LABEL
        ).grid(row=3, column=0, sticky="w", pady=4)
        self.primary_atk_min_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.primary_atk_min_entry.grid(row=3, column=1, sticky="ew", pady=4, padx=(12, 0))

        create_icon_label(
            form_frame, icon_name="damage", text=i18n_t("monster_primary_atk_max_label", ns="monster_editor", default="Công chính (Max):"), icon_fallback="⚔️", font=UI.FONT_LABEL
        ).grid(row=3, column=2, sticky="w", pady=4, padx=(20, 0))
        self.primary_atk_max_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.primary_atk_max_entry.grid(row=3, column=3, sticky="ew", pady=4, padx=(12, 0))

        # Secondary Attack Min/Max
        create_icon_label(
            form_frame, icon_name="damage", text=i18n_t("monster_sec_atk_min_label", ns="monster_editor", default="Công phụ (Min):"), icon_fallback="🗡️", font=UI.FONT_LABEL
        ).grid(row=4, column=0, sticky="w", pady=4)
        self.sec_atk_min_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.sec_atk_min_entry.grid(row=4, column=1, sticky="ew", pady=4, padx=(12, 0))

        create_icon_label(
            form_frame, icon_name="damage", text=i18n_t("monster_sec_atk_max_label", ns="monster_editor", default="Công phụ (Max):"), icon_fallback="🗡️", font=UI.FONT_LABEL
        ).grid(row=4, column=2, sticky="w", pady=4, padx=(20, 0))
        self.sec_atk_max_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.sec_atk_max_entry.grid(row=4, column=3, sticky="ew", pady=4, padx=(12, 0))

        # Defense & Defense Rate
        create_icon_label(
            form_frame, icon_name="shield", text=i18n_t("monster_def_label", ns="monster_editor", default="Thủ:"), icon_fallback="🛡️", font=UI.FONT_LABEL
        ).grid(row=5, column=0, sticky="w", pady=4)
        self.def_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.def_entry.grid(row=5, column=1, sticky="ew", pady=4, padx=(12, 0))

        create_icon_label(
            form_frame, icon_name="shield", text=i18n_t("monster_def_rate_label", ns="monster_editor", default="Tỷ lệ thủ:"), icon_fallback="🛡️", font=UI.FONT_LABEL
        ).grid(row=5, column=2, sticky="w", pady=4, padx=(20, 0))
        self.def_rate_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.def_rate_entry.grid(row=5, column=3, sticky="ew", pady=4, padx=(12, 0))

        # Accuracy & Dungeon Placeholder
        create_icon_label(
            form_frame, icon_name="aim", text=i18n_t("monster_acc_label", ns="monster_editor", default="Chính xác:"), icon_fallback="🎯", font=UI.FONT_LABEL
        ).grid(row=6, column=0, sticky="w", pady=4)
        self.acc_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.acc_entry.grid(row=6, column=1, sticky="ew", pady=4, padx=(12, 0))

        create_icon_label(
            form_frame, icon_name="dungeon", text=i18n_t("monster_dungeon_label", ns="monster_editor", default="Dungeon:"), icon_fallback="🏰", font=UI.FONT_LABEL
        ).grid(row=6, column=2, sticky="w", pady=4, padx=(20, 0))
        self.dungeon_combo = ttk.Combobox(form_frame, font=UI.FONT_TEXT, state="readonly", values=[""])
        self.dungeon_combo.grid(row=6, column=3, sticky="ew", pady=4, padx=(12, 0))

        # Boss Type Placeholder & Damage (Legacy compat)
        create_icon_label(
            form_frame, icon_name="boss", text=i18n_t("monster_boss_type_label", ns="monster_editor", default="Loại Boss:"), icon_fallback="👑", font=UI.FONT_LABEL
        ).grid(row=7, column=0, sticky="w", pady=4)
        self.boss_type_combo = ttk.Combobox(form_frame, font=UI.FONT_TEXT, state="readonly", values=[""])
        self.boss_type_combo.grid(row=7, column=1, sticky="ew", pady=4, padx=(12, 0))

        create_icon_label(
            form_frame, icon_name="damage", text=i18n_t("monster_damage_label", ns="monster_editor", default="Sát thương mỗi đòn:"), icon_fallback="⚔️", font=UI.FONT_LABEL
        ).grid(row=7, column=2, sticky="w", pady=4, padx=(20, 0))
        self.damage_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.damage_entry.grid(row=7, column=3, sticky="ew", pady=4, padx=(12, 0))

        # Description (Legacy compat)
        create_icon_label(
            form_frame, icon_name="info", text=i18n_t("monster_desc_label", ns="monster_editor", default="Mô tả:"), icon_fallback="📋", font=UI.FONT_LABEL
        ).grid(row=8, column=0, sticky="nw", pady=4)
        self.desc_text = tk.Text(form_frame, font=UI.FONT_TEXT, height=3, wrap=tk.WORD)
        self.desc_text.grid(row=8, column=1, columnspan=3, sticky="ew", pady=4, padx=(12, 0))
"""

search_pattern = r"""        # 1-Column Clean Form Layout
        form_frame = tk.Frame\(self\.info_tab, bg=UI\.BG_DEFAULT\)
        form_frame\.pack\(fill="both", expand=True, padx=25, pady=5\)
.*?form_frame\.columnconfigure\(1, weight=1\)"""

# Use re.DOTALL to match across lines
content_new = re.sub(search_pattern, new_form_layout.strip(), content, flags=re.DOTALL)

with open("dialogs/monster_edit.py", "w", encoding="utf-8") as f:
    f.write(content_new)

print("Updated dialogs/monster_edit.py layout.")
