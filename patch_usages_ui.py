import re

with open("ui/views/icon_manager_frame.py", "r", encoding="utf-8") as f:
    content = f.read()

# Make sure to import component registry
if "from ui.utils.component_registry import get_component_registry" not in content:
    content = re.sub(r"(from ui.helpers.tooltip import attach_i18n_tooltip)", r"\1\nfrom ui.utils.component_registry import get_component_registry", content)

# 7.2 Add Form logic replacement
old_form = """        # 7.2 Add Form
        add_frame = tk.Frame(usage_container, bg=UIStyle.BG_SURFACE)
        add_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        tk.Label(add_frame, text="Mod:", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).pack(side="left")
        self.var_usage_mod = tk.StringVar(value="ui")
        ttk.Entry(add_frame, textvariable=self.var_usage_mod, width=10).pack(side="left", padx=(0,5))

        tk.Label(add_frame, text="Comp:", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).pack(side="left")
        self.var_usage_comp = tk.StringVar(value="button")
        ttk.Entry(add_frame, textvariable=self.var_usage_comp, width=10).pack(side="left", padx=(0,5))

        tk.Label(add_frame, text="ID:", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).pack(side="left")
        self.var_usage_element = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.var_usage_element, width=20).pack(side="left", padx=(0,5))

        self.btn_add_usage = tk.Button(add_frame, text="Gắn (Map)", command=self._on_add_usage, **(UIStyle.get_button_style("primary") if hasattr(UIStyle, "get_button_style") else {}))
        self.btn_add_usage.pack(side="left", padx=2)

        self.btn_del_usage = tk.Button(add_frame, text="Gỡ (Unmap)", command=self._on_del_usage, **(UIStyle.get_button_style("danger") if hasattr(UIStyle, "get_button_style") else {}))
        self.btn_del_usage.pack(side="left", padx=2)"""

new_form = """        # 7.2 Add Form
        add_frame = tk.Frame(usage_container, bg=UIStyle.BG_SURFACE)
        add_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # Row 1: Search preset
        search_frame = tk.Frame(add_frame, bg=UIStyle.BG_SURFACE)
        search_frame.pack(side="top", fill="x", pady=(0, 5))

        tk.Label(search_frame, text="Gợi ý (Preset):", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).pack(side="left")
        self.combo_usage_preset = ttk.Combobox(search_frame, state="readonly", width=40)
        self.combo_usage_preset.pack(side="left", padx=5)

        # Populate preset
        registry = get_component_registry()
        self.combo_usage_preset['values'] = registry.get_component_names()

        def on_preset_selected(event):
            selected_name = self.combo_usage_preset.get()
            comp_data = registry.get_component(selected_name)
            if comp_data:
                self.var_usage_mod.set(comp_data.get("mod", "ui"))
                self.var_usage_comp.set(comp_data.get("comp", "button"))
                self.var_usage_element.set(comp_data.get("id", ""))

        self.combo_usage_preset.bind("<<ComboboxSelected>>", on_preset_selected)

        # Row 2: Manual inputs and buttons
        input_frame = tk.Frame(add_frame, bg=UIStyle.BG_SURFACE)
        input_frame.pack(side="top", fill="x")

        tk.Label(input_frame, text="Mod:", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).pack(side="left")
        self.var_usage_mod = tk.StringVar(value="ui")
        ttk.Entry(input_frame, textvariable=self.var_usage_mod, width=10).pack(side="left", padx=(0,5))

        tk.Label(input_frame, text="Comp:", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).pack(side="left")
        self.var_usage_comp = tk.StringVar(value="button")
        ttk.Entry(input_frame, textvariable=self.var_usage_comp, width=10).pack(side="left", padx=(0,5))

        tk.Label(input_frame, text="ID:", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).pack(side="left")
        self.var_usage_element = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.var_usage_element, width=20).pack(side="left", padx=(0,5))

        self.btn_add_usage = tk.Button(input_frame, text="Gắn (Map)", command=self._on_add_usage, **(UIStyle.get_button_style("primary") if hasattr(UIStyle, "get_button_style") else {}))
        self.btn_add_usage.pack(side="left", padx=2)

        self.btn_del_usage = tk.Button(input_frame, text="Gỡ (Unmap)", command=self._on_del_usage, **(UIStyle.get_button_style("danger") if hasattr(UIStyle, "get_button_style") else {}))
        self.btn_del_usage.pack(side="left", padx=2)"""

content = content.replace(old_form, new_form)

with open("ui/views/icon_manager_frame.py", "w", encoding="utf-8") as f:
    f.write(content)
