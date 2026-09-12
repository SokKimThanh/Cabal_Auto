import tkinter as tk
from tkinter import ttk
from lib.ui_style_v2 import UIStyleV2 as UI
from ui.components.styled_panel import StyledPanel
from ui.components.empty_state import EmptyState


class MonsterTargetPanel(ttk.LabelFrame):
    def __init__(self, parent, app, scale_factor=1.0, hunt_tab=None):
        padding = (int(10 * scale_factor), int(8 * scale_factor))
        super().__init__(parent, text="🎯 Target Setup", padding=padding)
        self.app = app
        self.scale_factor = scale_factor
        self.hunt_tab = hunt_tab
        self._build_ui()

    def _scale_font(self, base_size: int) -> int:
        return max(8, int(base_size * self.scale_factor))

    def _update_target_policy_layout(self):
        policy = self.app.state_controller.get_ui_var('target_policy')
        # Hide all containers
        self.configured_container.pack_forget()
        self.detected_container.pack_forget()
        self.any_target_container.pack_forget()

        if policy == "configured_only":
            self.configured_container.pack(fill="both", expand=True)
        elif policy == "all_resolved":
            self.detected_container.pack(fill="both", expand=True, pady=(0, 10))
            self.configured_container.pack(fill="both", expand=True)
        elif policy == "any_target":
            self.any_target_container.pack(fill="both", expand=True)

    def _build_ui(self):
        # We also maintain monster frame panel properties if needed for backward compatibility
        self.app.monster_frame_panel = StyledPanel(self, show_border=False)
        self.app.monster_frame = self.app.monster_frame_panel.get_content_frame()
        self.app.monster_frame.pack(fill="both", expand=True)

        mode_bar = tk.Frame(self.app.monster_frame, bg=UI.BG_SURFACE)
        mode_bar.pack(fill="x", padx=10, pady=(0, 8))

        self.app.state_controller.ui_vars['target_policy'] = tk.StringVar(
            value=self.app.state_controller.hunt_cfg.get("target_policy", "configured_only")
        )

        def _on_policy_change(*args):
            if getattr(self.app, "click_running", False):
                self.app.state_controller.set_ui_var('target_policy',
                    self.app.state_controller.hunt_cfg.get("target_policy", "configured_only")
                )
                return
            new_policy = self.app.state_controller.get_ui_var('target_policy')
            if new_policy not in ["configured_only", "all_resolved", "any_target"]:
                new_policy = "configured_only"
                self.app.state_controller.set_ui_var('target_policy', new_policy)
            self.app.state_controller.hunt_cfg["target_policy"] = new_policy
            self.app.state_controller.has_unsaved_changes = True
            if hasattr(self.app, "_update_unsaved_indicator"):
                self.app._update_unsaved_indicator()
            self._update_target_policy_layout()

        if hasattr(self.app.state_controller.ui_vars.get('target_policy'), "trace_add"):
            self.app.state_controller.ui_vars['target_policy'].trace_add("write", _on_policy_change)

        policies = [
            ("configured_only", self.app._t("hunt_policy_configured")),
            ("all_resolved", self.app._t("hunt_policy_auto_detect")),
            ("any_target", self.app._t("hunt_policy_any_target")),
        ]

        self.policy_radios = []
        for val, text in policies:
            rb = tk.Radiobutton(
                mode_bar,
                text=text,
                value=val,
                variable=self.app.state_controller.ui_vars['target_policy'],
                indicatoron=0,
                bg=UI.BG_SURFACE,
                fg=UI.TEXT_SECONDARY,
                selectcolor=UI.BG_ELEVATED,
                activebackground=UI.BG_ELEVATED,
                activeforeground=UI.TEXT_PRIMARY,
                relief="flat",
                bd=0,
                padx=16,
                pady=6,
                cursor="hand2"
            )
            rb.pack(side="left", padx=2, pady=4)
            self.policy_radios.append(rb)

        self.policy_content_frame = tk.Frame(self.app.monster_frame, bg=UI.BG_SURFACE)
        self.policy_content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.configured_container = tk.Frame(self.policy_content_frame, bg=UI.BG_SURFACE)
        self.detected_container = tk.Frame(self.policy_content_frame, bg=UI.BG_SURFACE)
        self.any_target_container = tk.Frame(self.policy_content_frame, bg=UI.BG_SURFACE)

        # Render default view after containers exist.
        self._update_target_policy_layout()

        tk.Label(
            self.configured_container,
            text=self.app._t("configured_monsters_title"),
            font=UI.FONT_LABEL,
            bg=UI.BG_SURFACE,
            fg=UI.TEXT_PRIMARY,
        ).pack(anchor="w")

        list_container = tk.Frame(self.configured_container, bg=UI.BG_SURFACE)
        list_container.pack(fill="both", expand=True)

        listbox_frame = tk.Frame(list_container, bg=UI.BG_SURFACE)
        listbox_frame.pack(side="left", fill="both", expand=True)

        self.app.monster_rotation_listbox = tk.Listbox(
            listbox_frame,
            height=5,
            exportselection=False,
            selectmode="extended",
            font=UI.FONT_TEXT,
            bg=UI.BG_ELEVATED,
            fg=UI.TEXT_PRIMARY,
            selectbackground=UI.ACCENT_GREEN_BG,
            selectforeground=UI.ACCENT_GREEN,
            highlightthickness=0,
            relief="flat",
        )
        self.app.monster_rotation_listbox.pack(side="left", fill="both", expand=True)

        monster_scroll = ttk.Scrollbar(
            listbox_frame,
            orient="vertical",
            command=self.app.monster_rotation_listbox.yview,
        )
        monster_scroll.pack(side="right", fill="y")
        self.app.monster_rotation_listbox.config(yscrollcommand=monster_scroll.set)

        # Create a toolbar frame with a subtle background and rounded-like appearance
        btn_container = tk.Frame(
            list_container,
            bg=UI.BG_ELEVATED,
            highlightbackground=UI.BORDER_SUBTLE,
            highlightthickness=1,
            padx=4, pady=4
        )
        btn_container.pack(side="right", fill="y", padx=(8, 0))

        self.app.btn_add = tk.Button(
            btn_container,
            text="➕",
            command=self.app._on_monster_add_smart,
            bg=UI.BG_ELEVATED,
            fg=UI.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2"
        )
        self.app.btn_add.pack(pady=(0, 4))
        self.app._create_tooltip(
            self.app.btn_add, self.app._t("monster_rotation_add")
        )

        self.app.btn_move_up = tk.Button(
            btn_container,
            text="↑",
            command=self.app._on_monster_move_up,
            bg=UI.BG_ELEVATED,
            fg=UI.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2"
        )
        self.app.btn_move_up.pack(pady=(0, 4))

        self.app.btn_move_down = tk.Button(
            btn_container,
            text="↓",
            command=self.app._on_monster_move_down,
            bg=UI.BG_ELEVATED,
            fg=UI.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2"
        )
        self.app.btn_move_down.pack(pady=(0, 12))

        self.app.btn_remove_monster = self.app._create_icon_button(
            btn_container,
            icon_emoji="✖",
            command=self.app._on_monster_delete_from_list,
            style="compact",
            bg_color=UI.DANGER,
            hover_color=UI.ACCENT_AMBER,
        )
        self.app.btn_remove_monster.pack()
        self.app._create_tooltip(
            self.app.btn_remove_monster, self.app._t("monster_rotation_remove")
        )


        # 2. Detected UI (All Resolved view)
        tk.Label(
            self.detected_container,
            text=self.app._t("detected_monsters_title"),
            font=UI.FONT_LABEL,
            bg=UI.BG_SURFACE,
            fg=UI.TEXT_PRIMARY,
        ).pack(anchor="w")

        detected_listbox_frame = tk.Frame(self.detected_container, bg=UI.BG_SURFACE)
        detected_listbox_frame.pack(fill="both", expand=True)
        self.app.detected_monsters_listbox = tk.Listbox(
            detected_listbox_frame,
            height=5,
            exportselection=False,
            selectmode="single",
            font=UI.FONT_TEXT,
            bg=UI.BG_ELEVATED,
            fg=UI.TEXT_PRIMARY,
            selectbackground=UI.ACCENT_GREEN_BG,
            selectforeground=UI.ACCENT_GREEN,
            highlightthickness=0,
            relief="flat",
        )
        self.app.detected_monsters_listbox.pack(side="left", fill="both", expand=True)

        detected_scroll = ttk.Scrollbar(
            detected_listbox_frame, command=self.app.detected_monsters_listbox.yview
        )
        detected_scroll.pack(side="right", fill="y")
        self.app.detected_monsters_listbox.config(yscrollcommand=detected_scroll.set)

        detected_btn_container = tk.Frame(self.detected_container, bg=UI.BG_SURFACE)
        detected_btn_container.pack(side="right", fill="y", padx=(8, 0))
        self.app.btn_promote_monster = tk.Button(
            detected_btn_container,
            text="➕",
            command=lambda: getattr(
                self.app, "promote_detected_monster", lambda x: None
            )(self.app.detected_monsters_listbox.curselection()),
            bg=UI.BG_ELEVATED,
            fg=UI.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2"
        )
        self.app.btn_promote_monster.pack(pady=(0, 4))
        self.app._create_tooltip(
            self.app.btn_promote_monster, self.app._t("monster_promote")
        )

        self.app.detected_monsters_listbox.bind(
            "<Double-1>",
            lambda e: getattr(self.app, "promote_detected_monster", lambda x: None)(
                self.app.detected_monsters_listbox.curselection()
            ),
        )
        self.app.detected_monsters_listbox.bind(
            "<Return>",
            lambda e: getattr(self.app, "promote_detected_monster", lambda x: None)(
                self.app.detected_monsters_listbox.curselection()
            ),
        )

        def on_drag_start(event):
            listbox = event.widget
            if listbox.size() == 0:
                return
            idx = listbox.nearest(event.y)
            if idx < 0 or idx >= listbox.size():
                return
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(idx)
            # Find the active rotation listbox based on visibility
            target = getattr(self.app, "monster_rotation_listbox", None)
            if not target:
                return
            item_text = listbox.get(idx)
            # Optional: Visual drag indicator code could go here
            event.widget.drag_data = {"item": item_text, "source_idx": idx}

        def on_drag_motion(event):
            if not hasattr(event.widget, "drag_data"):
                return
            target = getattr(self.app, "monster_rotation_listbox", None)
            if target:
                target.config(cursor="plus")
                # Highlight potential drop target
                target_y = event.y_root - target.winfo_rooty()
                if 0 <= target_y <= target.winfo_height():
                    nearest = target.nearest(target_y)
                    target.selection_clear(0, tk.END)
                    target.selection_set(nearest)

        def on_drop(event):
            if not hasattr(event.widget, "drag_data"):
                return
            target = getattr(self.app, "monster_rotation_listbox", None)
            if target:
                target.config(cursor="")
                target_y = event.y_root - target.winfo_rooty()
                target_x = event.x_root - target.winfo_rootx()
                if (
                    0 <= target_y <= target.winfo_height()
                    and 0 <= target_x <= target.winfo_width()
                ):
                    promote_fn = getattr(self.app, "promote_detected_monster", None)
                    if promote_fn:
                        promote_fn((event.widget.drag_data["source_idx"],))
                target.selection_clear(0, tk.END)
            del event.widget.drag_data

        # Apply drag bindings
        self.app.detected_monsters_listbox.bind("<ButtonPress-1>", on_drag_start)
        self.app.detected_monsters_listbox.bind("<B1-Motion>", on_drag_motion)
        self.app.detected_monsters_listbox.bind("<ButtonRelease-1>", on_drop)

        # 3. Any Target view
        self.any_target_empty = EmptyState(
            self.any_target_container,
            icon="🎯",
            message=self.app._t("any_target_warning"),
            submessage=self.app._t(
                "any_target_warning_submessage",
                default="Tất cả mục tiêu trong màn hình sẽ bị tấn công.",
            ),
        )
        self.any_target_empty.pack(fill="both", expand=True)


        self.app.monster_status_var = tk.StringVar()
        tk.Label(
            self.app.monster_frame,
            textvariable=self.app.monster_status_var,
            fg=UI.TEXT_PRIMARY,
            bg=UI.BG_SURFACE,
            font=UI.FONT_TEXT,
        ).pack(fill="x", pady=(8, 0), padx=10)

        if hasattr(self.app, "_on_monster_list_select"):
            self.app.monster_rotation_listbox.bind(
                "<<ListboxSelect>>", self.app._on_monster_list_select
            )
        self.app.monster_rotation_listbox.bind(
            "<Delete>", self.app._on_monster_delete_from_list
        )
        self.app.monster_rotation_listbox.bind(
            "<BackSpace>", self.app._on_monster_delete_from_list
        )

        self.app.monster_context_menu = tk.Menu(
            self.app.monster_rotation_listbox, tearoff=0
        )
        self.app.monster_context_menu.add_command(
            label=self.app._t("monster_delete"),
            command=self.app._on_monster_delete_from_list,
        )
        self.app._create_tooltip(
            self.app.monster_context_menu,
            self.app._t("monster_rotation_delete_hint"),
        )

        def _show_monster_context_menu(event):
            try:
                self.app.monster_rotation_listbox.selection_clear(0, tk.END)
                self.app.monster_rotation_listbox.selection_set(
                    self.app.monster_rotation_listbox.nearest(event.y)
                )
                self.app.monster_context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.app.monster_context_menu.grab_release()

        def _select_all_monsters(event):
            self.app.monster_rotation_listbox.selection_set(0, tk.END)
            return "break"

        self.app.monster_rotation_listbox.bind(
            "<Button-3>", _show_monster_context_menu
        )
        self.app.monster_rotation_listbox.bind("<Control-a>", _select_all_monsters)
        self.app.monster_rotation_listbox.bind("<Control-A>", _select_all_monsters)

        self.configured_empty = EmptyState(
            self.configured_container,
            icon="🎯",
            message=self.app._t("monster_target.empty_list"),
            submessage=self.app._t("monster_target.empty_list_submessage"),
        )
        self.configured_empty.pack(fill="both", expand=True, pady=(4, 0))

        def _update_configured_empty_state(*args):
            if hasattr(self.app, "monster_rotation_listbox"):
                if self.app.monster_rotation_listbox.size() > 0:
                    self.configured_empty.pack_forget()
                else:
                    self.configured_empty.pack(fill="both", expand=True, pady=(4, 0))

        # Use a polling loop to check listbox size dynamically since we don't have direct bindings here
        def _poll_configured_empty_state():
            _update_configured_empty_state()
            self.after(1000, _poll_configured_empty_state)

        self.after(100, _poll_configured_empty_state)


        self.app.training_mode_hint_var = tk.StringVar()
        self.app.training_mode_hint_label = tk.Label(
            self.app.monster_frame,
            textvariable=self.app.training_mode_hint_var,
            fg=UI.ACCENT_AMBER,
            bg=UI.BG_SURFACE,
            font=UI.FONT_TEXT,
            wraplength=400,
            justify="left",
        )
        self.app.training_mode_hint_label.pack(fill="x", pady=(4, 0), padx=10)

        # Legacy wiring to HuntTab is applied after refreshing the rotation list below.
        if hasattr(self.app, "_refresh_monster_rotation_list"):
            self.app._refresh_monster_rotation_list()

        if getattr(self, "hunt_tab", None):
            for prop in ["target_image_label", "target_name_label", "status_label",
                         "target_level_label", "target_hp_label", "target_def_label",
                         "hp_canvas", "hp_percent_label", "recovery_frame", "hp_bg", "hp_fill", "hp_text",
                         "hunt_status_badge", "hunt_status_label", "skill_stats_tree"]:
                if hasattr(self.app, prop):
                    setattr(self.hunt_tab, prop, getattr(self.app, prop))
