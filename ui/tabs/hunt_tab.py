import tkinter as tk
from tkinter import ttk
from lib.ui_style import UIStyle as UI
try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


class HuntTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=12)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        """Streamlined Hunt tab with only essential controls.

        Window selection moved to topbar for quick access via combobox.
        Beginner-friendly: Monster rotation → Skill slots → Quick actions
        """

        # Initialize mode var for compatibility (actual mode selector is in Setup tab)
        self.app.hunt_mode_var = tk.StringVar(
            value=self.app.hunt_cfg.get("ui_mode", "beginner")
        )

        # Initialize vars for compatibility with hunt loop (values read from hunt_cfg)
        self.app.target_key_var = tk.StringVar(
            value=str(self.app.hunt_cfg.get("target_key", "TAB"))
        )
        # attack_keys removed: per-skill keys from skill_slots are used instead
        self.app.attack_press_var = tk.StringVar(
            value=str(self.app.hunt_cfg.get("attack_press_ms", 60))
        )
        self.app.target_cycle_var = tk.StringVar(
            value=str(self.app.hunt_cfg.get("target_cycle_delay", 0.2))
        )
        self.app.search_interval_var = tk.StringVar(
            value=str(self.app.hunt_cfg.get("search_interval", 0.25))
        )
        self.app.attack_interval_var = tk.StringVar(
            value=str(self.app.hunt_cfg.get("attack_interval", 0.15))
        )
        self.app.lost_timeout_var = tk.StringVar(
            value=str(self.app.hunt_cfg.get("lost_timeout_sec", 1.2))
        )
        self.app.attack_duration_var = tk.StringVar(
            value=str(self.app.hunt_cfg.get("attack_min_duration_sec", 1.5))
        )
        self.app.template_var = tk.StringVar(
            value=str(
                self.app.hunt_cfg.get("template_path", "assets/images/target_frame.png")
            )
        )

        region = self.app.hunt_cfg.get("region") or ["", "", "", ""]
        self.app.reg_l = tk.StringVar(value=str(region[0]) if region[0] != "" else "")
        self.app.reg_t = tk.StringVar(value=str(region[1]) if region[1] != "" else "")
        self.app.reg_w = tk.StringVar(value=str(region[2]) if region[2] != "" else "")
        self.app.reg_h = tk.StringVar(value=str(region[3]) if region[3] != "" else "")

        self.app.bring_front_var = tk.BooleanVar(
            value=bool(self.app.hunt_cfg.get("bring_to_front_each_cycle", False))
        )

        # Layout: Split into two primary panels: Monster Rotation and Active Target & Status
        self.grid_columnconfigure(0, weight=1, minsize=776)
        self.grid_columnconfigure(1, weight=1, minsize=776)
        self.grid_rowconfigure(0, weight=1, minsize=552)
        self.grid_rowconfigure(1, weight=0, minsize=120)

        # Section 1: Active Target & Status Panel
        self.app.active_target_status_frame = tk.LabelFrame(
            self, text=self.app._t("hunt_active_target_status"), padx=10, pady=8
        )
        self.app.active_target_status_frame.grid(
            row=0, column=1, sticky="nsew", padx=(6, 0), pady=(0, 12)
        )
        self.app.active_target_status_frame.grid_columnconfigure(0, weight=1)

        # Sub-section: Hunt Status Bar (current hunt state + current target)
        status_frame = tk.Frame(self.app.active_target_status_frame, relief="groove", bd=1, height=32)
        status_frame.pack(fill="x", pady=(0, 12))
        status_frame.grid_propagate(False)  # Keep consistent height even before labels have text
        tk.Label(
            status_frame,
            textvariable=self.app.hunt_status,
            font=("Arial", 10, "bold"),
            fg="#2E7D32",
            anchor="w",
        ).pack(side="left", padx=8, pady=6)
        tk.Label(
            status_frame,
            textvariable=self.app.hunt_target_info,
            font=("Arial", 9),
            fg="#555",
            anchor="e",
        ).pack(side="right", padx=8, pady=6)

        # Section 2: Monster Selection (Phase 3: Multi-Monster Support)
        # Sprint 22 Patch 2: Dynamic title based on training mode
        self.app.monster_frame = tk.LabelFrame(
            self, text=self.app._t("hunt_monsters"), padx=10, pady=8
        )
        self.app.monster_frame.grid(
            row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 12)
        )
        self.app.monster_frame.grid_columnconfigure(0, weight=1)

        # Rotation mode selection
        mode_bar = tk.Frame(self.app.monster_frame)
        mode_bar.pack(fill="x", pady=(0, 8))
        tk.Label(mode_bar, text=self.app._t("rotation_mode")).pack(side="left")

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
            mode_bar, textvariable=self.app.rotation_desc_var, fg="#666", font=("Arial", 8)
        ).pack(side="left", padx=(8, 0))

        # Monster list with checkboxes
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
            font=("Arial", 9),
        )
        self.app.monster_rotation_listbox.pack(side="left", fill="both", expand=True)

        monster_scroll = tk.Scrollbar(
            listbox_frame,
            orient="vertical",
            command=self.app.monster_rotation_listbox.yview,
        )
        monster_scroll.pack(side="right", fill="y")
        self.app.monster_rotation_listbox.config(yscrollcommand=monster_scroll.set)

        # Control buttons (right side) - Using compact icon buttons (all 20px for consistency)
        btn_container = tk.Frame(list_container)
        btn_container.pack(side="right", fill="y", padx=(8, 0))

        # Add monster button - Compact style (20px: 16px icon + 2×2px padding)
        self.app.btn_add_monster = self.app._create_icon_button(
            btn_container,
            icon_emoji="➕",
            command=self.app._on_monster_add_smart,
            style="compact",
            bg_color=UI.BTN_ACCENT_BG,
            hover_color=UI.BTN_ACCENT_HOVER,
        )
        self.app.btn_add_monster.pack(pady=(0, UI.BTN_SPACING))
        self.app._create_tooltip(
            self.app.btn_add_monster, self.app._t("tooltip_add_monster_normal")
        )

        # Priority reorder buttons - Compact style (20px: 16px icon + 2×2px padding)
        # Both buttons use blue color for consistency
        self.app.btn_move_up = self.app._create_icon_button(
            btn_container,
            icon_emoji="↑",
            command=self.app._on_monster_move_up,
            style="compact",
            bg_color=UI.BTN_INFO_BG,  # Blue for UP
            hover_color=UI.BTN_INFO_HOVER,
        )
        self.app.btn_move_up.pack(pady=(0, UI.BTN_SPACING // 2))
        self.app._create_tooltip(self.app.btn_move_up, self.app._t("tooltip_move_up"))

        self.app.btn_move_down = self.app._create_icon_button(
            btn_container,
            icon_emoji="↓",
            command=self.app._on_monster_move_down,
            style="compact",
            bg_color=UI.BTN_INFO_BG,  # Blue for DOWN
            hover_color=UI.BTN_INFO_HOVER,
        )
        self.app.btn_move_down.pack(pady=(0, UI.BTN_SPACING * 1.5))
        self.app._create_tooltip(self.app.btn_move_down, self.app._t("tooltip_move_down"))

        # Library Manager buttons removed per request

        # Current monster status
        self.app.monster_status_var = tk.StringVar()
        tk.Label(
            self.app.monster_frame,
            textvariable=self.app.monster_status_var,
            fg="#2196F3",
            font=("Arial", 8, "bold"),
        ).pack(fill="x", pady=(8, 0))

        # Bind click to toggle checkbox
        self.app.monster_rotation_listbox.bind("<Double-Button-1>", self.app._on_monster_toggle)
        self.app.monster_rotation_listbox.bind(
            "<<ListboxSelect>>", self.app._on_monster_list_select
        )
        self.app.monster_rotation_listbox.bind(
            "<Delete>", self.app._on_monster_delete_from_list
        )  # Sprint 22 Patch 2: Delete key
        self.app.monster_rotation_listbox.bind(
            "<BackSpace>", self.app._on_monster_delete_from_list
        )  # Also backspace

        # Sprint 22 Patch 2: Context menu for right-click delete
        self.app.monster_context_menu = tk.Menu(self.app.monster_rotation_listbox, tearoff=0)
        self.app.monster_context_menu.add_command(
            label=self.app._t("monster_delete"),  # "Delete" / "Xóa"
            command=self.app._on_monster_delete_from_list,
        )
        self.app.monster_rotation_listbox.bind(
            "<Button-3>", self.app._show_monster_context_menu
        )  # Right-click

        # Sprint 22 Patch 2: Hint for switching back to normal mode
        self.app.training_mode_hint_var = tk.StringVar()
        self.app.training_mode_hint_label = tk.Label(
            self.app.monster_frame,
            textvariable=self.app.training_mode_hint_var,
            fg="#FF6F00",  # Orange
            font=("Arial", 8, "italic"),
            wraplength=400,
            justify="left",
        )
        self.app.training_mode_hint_label.pack(fill="x", pady=(4, 0))

        # Legacy monster estimate (keep for compatibility)
        self.app.monster_estimate_var.set("")

        # Section 2.5: Training Mode Toggle (Sprint 22 Patch 2 - Hidden, auto-detect from training_monster_list)
        # NOTE: Training mode checkbox removed to avoid user confusion.
        # System auto-enables training mode when training_monster_list has items.
        # User adds training dummies via normal "Add Monster" dialog (filtered by training_mode flag).

        # Initialize training_mode_var for backward compatibility
        self.app.training_mode_var = tk.BooleanVar(value=False)  # Will be auto-updated

        # Training mode status indicator (kept for debug info)
        self.app.training_mode_status_var = tk.StringVar()
        # Status label hidden, only used internally

        self.skill_strip_frame = tk.Frame(self)
        self.skill_strip_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', pady=(0, 12))
        self.skill_strip_frame.grid_columnconfigure(0, weight=1)
        self.skill_strip_frame.grid_columnconfigure(1, weight=1)

        # Section 3: Skill slots selection
        skill_frame_outer = tk.LabelFrame(
            self.skill_strip_frame, text=self.app._t("skill_slots"), padx=10, pady=8
        )
        skill_frame_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        # Manage skills hint (button hidden, use Ctrl+K shortcut)
        hint_label = tk.Label(
            skill_frame_outer,
            text=f"ℹ️ {self.app._t('skill_manage_hint')}",
            fg="#666",
            font=("Arial", 8),
            cursor="hand2",
        )
        hint_label.pack(pady=(0, 6))
        hint_label.bind("<Button-1>", lambda e: self.app.skill_manager_controller.open_window())

        slot_frame = tk.Frame(skill_frame_outer)
        slot_frame.pack(fill="both", expand=True)
        slot_frame.grid_columnconfigure(1, weight=1)
        self.app.skill_slot_vars = []
        self.app.skill_slot_boxes = []
        self.app.skill_slot_key_labels = []
        for idx in range(self.app.skill_slot_count):
            var = tk.StringVar()
            self.app.skill_slot_vars.append(var)
            label = self.app._t("skill_slot_label").format(i=idx + 1)
            tk.Label(slot_frame, text=label).grid(row=idx, column=0, sticky="e", pady=2)
            cmb = ttk.Combobox(slot_frame, textvariable=var, state="readonly", width=24)
            cmb.grid(row=idx, column=1, sticky="we", padx=(4, 0), pady=2)
            cmb.bind("<<ComboboxSelected>>", self.app.on_skill_slot_changed)
            # Key label showing which key is assigned to the selected skill
            key_lbl = tk.Label(slot_frame, text="", width=6, anchor="w", fg="#333")
            key_lbl.grid(row=idx, column=2, padx=(6, 0))
            self.app.skill_slot_key_labels.append(key_lbl)
            # Clear button (moved to column 3)
            tk.Button(
                slot_frame,
                text=self.app._t("skill_slot_clear"),
                command=lambda v=var: self.app._clear_skill_slot(v),
            ).grid(row=idx, column=3, padx=(6, 0))
            self.app.skill_slot_boxes.append(cmb)

        self.app._refresh_monster_select_options()
        self.app._load_skill_slots_from_cfg()

        # Phase 3: Populate monster rotation list
        self.app._refresh_monster_rotation_list()

        # Section 3.5: Skill Performance Statistics (Sprint 22 Patch 1 - Training Mode)
        # Re-parented into the active target status panel.
        self.app.skill_stats_frame = tk.LabelFrame(
            self.skill_strip_frame, text=self.app._t("skill_stats_title"), padx=10, pady=8
        )
        self.app.skill_stats_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        stats_columns = ("skill", "casts", "last_cast", "cooldown", "success")
        self.app.skill_stats_tree = ttk.Treeview(
            self.app.skill_stats_frame,
            columns=stats_columns,
            show="headings",
            height=6,
        )
        stats_headings = {
            "skill": ("skill_name_col", 120),
            "casts": ("cast_count_col", 60),
            "last_cast": ("last_cast_col", 90),
            "cooldown": ("cooldown_col", 80),
            "success": ("success_rate_col", 80),
        }
        for col, (i18n_key, width) in stats_headings.items():
            self.app.skill_stats_tree.heading(col, text=self.app._t(i18n_key))
            # Let the skill name column absorb extra width on wider windows; keep the rest fixed.
            self.app.skill_stats_tree.column(
                col, width=width, anchor="center", stretch=(col == "skill")
            )

        stats_scroll = tk.Scrollbar(
            self.app.skill_stats_frame,
            orient="vertical",
            command=self.app.skill_stats_tree.yview,
        )
        self.app.skill_stats_tree.config(yscrollcommand=stats_scroll.set)
        self.app.skill_stats_tree.pack(side="left", fill="both", expand=True)
        stats_scroll.pack(side="right", fill="y")

        self.app.skill_stats_tree.tag_configure("excellent", foreground="#2E7D32")
        self.app.skill_stats_tree.tag_configure("good", foreground="#F57F17")
        self.app.skill_stats_tree.tag_configure("poor", foreground="#C62828")
        self.app.skill_stats_tree.tag_configure("placeholder", foreground="#999")
        self.app._show_skill_stats_placeholder()
