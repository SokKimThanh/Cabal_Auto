import tkinter as tk
from tkinter import ttk
from lib.ui_style import UIStyle as UI

from lib.features.monsters.monster_repo import get_target_monster_info
import os

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

    def update_hunt_status_color(self, state: str):
        if not hasattr(self, "hunt_status_label"):
            return

        if state == "running":
            self.hunt_status_label.config(fg=UI.COLOR_ACCENT)
        elif state == "error":
            self.hunt_status_label.config(fg=UI.COLOR_DANGER)
        elif state == "idle":
            self.hunt_status_label.config(fg=UI.COLOR_ACCENT)
        elif state == "stopped":
            self.hunt_status_label.config(fg=UI.COLOR_WARNING)

    def clear_target_photo(self):
        if hasattr(self, 'target_image_label') and self.target_image_label:
            self.target_image_label.configure(image="", text="[ NO IMAGE ]", bg=UI.BG_MUTED)
        if hasattr(self, '_current_target_photo') and self._current_target_photo:
            del self._current_target_photo
            self._current_target_photo = None

    def set_target_photo(self, photo_image=None):
        self.clear_target_photo()
        if photo_image:
            self._current_target_photo = photo_image
            self.target_image_label.configure(image=photo_image, text="")


    def update_status(self, status_string: str):
        if not hasattr(self, "status_label"):
            return
        self.status_label.config(text=status_string)
        if status_string == "APPROACHING":
            self.status_label.config(fg=getattr(UI, 'STATE_WARN', getattr(UI, 'COLOR_WARNING', '#FFC107')))
        elif status_string == "ATTACKING":
            self.status_label.config(fg=getattr(UI, 'STATE_ERROR', getattr(UI, 'COLOR_DANGER', '#F44336')))
        elif status_string == "TARGET_DEAD":
            self.status_label.config(fg=getattr(UI, 'STATE_MUTED', getattr(UI, 'COLOR_MUTED', '#9E9E9E')))
        else:
            self.status_label.config(fg=getattr(UI, 'COLOR_ACCENT', '#2196F3'))

    def update_hp_display(self, hp_percent: float, current_hp: int = 0, max_hp: int = 10000):
        """Update Canvas HP bar with color and text."""
        if not hasattr(self, "hp_canvas"):
            return

        # Death case
        if hp_percent == 0.0:
            self.hp_canvas.itemconfig(self.hp_fill, fill="#52525B", outline="#52525B")
            self.hp_canvas.itemconfig(self.hp_text, text=self.app._t("target_card.target_dead") if hasattr(self.app, "_t") else "[ Đã Tiêu Diệt ]")
            # Cancel any pending clear (race guard)
            if hasattr(self, "_pending_clear_id") and self._pending_clear_id:
                try:
                    self.after_cancel(self._pending_clear_id)
                except tk.TclError:
                    pass
            # Schedule new clear
            self._pending_clear_id = self.after(200, self.clear_target_card)

            if hasattr(self, "hp_percent_label"):
                self.hp_percent_label.config(text="0.0%")
            return

        # Normal rendering
        width = self.hp_canvas.winfo_width()
        if width < 2:
            width = 200  # Default if not rendered yet

        fill_width = int(width * hp_percent / 100)

        # Update bar position
        self.hp_canvas.coords(self.hp_fill, 0, 0, fill_width, 24)

        # Color by percent
        if hp_percent > 60:
            color = "#00E86D"  # Green
        elif hp_percent >= 30:
            color = "#FFB800"  # Orange
        else:
            color = "#FF3D3D"  # Red

        self.hp_canvas.itemconfig(self.hp_fill, fill=color, outline=color)

        # Update text
        text = f"{current_hp:,} / {max_hp:,} ({hp_percent:.1f}%)"
        self.hp_canvas.coords(self.hp_text, width/2, 12)
        self.hp_canvas.itemconfig(self.hp_text, text=text)

        # Update label for compatibility
        if hasattr(self, "hp_percent_label"):
            self.hp_percent_label.config(text=f"{hp_percent:.1f}%")

    def clear_target_card(self, delay_ms: int = 0):
        if delay_ms > 0:
            clear_id = getattr(self, "_pending_clear_id", None)
            if clear_id:
                try:
                    self.after_cancel(clear_id)
                except tk.TclError:
                    pass
            self._pending_clear_id = self.after(delay_ms, lambda: self.clear_target_card(0))
            return

        self.clear_target_photo()
        if hasattr(self, "target_name_label"):
            self.target_name_label.config(text="Unknown Target")
        if hasattr(self, "target_level_label"):
            self.target_level_label.config(text="-")
        if hasattr(self, "target_hp_label"):
            self.target_hp_label.config(text="-")
        if hasattr(self, "target_def_label"):
            self.target_def_label.config(text="-")
        if hasattr(self, "hp_canvas"):
            self.hp_canvas.coords(self.hp_fill, 0, 0, 0, 24)
            self.hp_canvas.itemconfig(self.hp_text, text="")
        if hasattr(self, "hp_progressbar"):
            self.hp_progressbar.config(value=0)
        self.update_status("IDLE")
        if hasattr(self.app, "hunt_target_info"):
            self.app.hunt_target_info.set("")

    def update_target_card(self, name_or_id: str):
        if hasattr(self, "_pending_clear_id") and self._pending_clear_id:
            self.after_cancel(self._pending_clear_id)
            self._pending_clear_id = None
        info = get_target_monster_info(name_or_id)

        self.target_name_label.config(text=info["name"])
        self.target_level_label.config(text=str(info["level"]))
        self.target_hp_label.config(text=str(info["hp"]))
        self.target_def_label.config(text=str(info["defense"]))

        if hasattr(self.app, "hunt_target_info"):
            self.app.hunt_target_info.set(f"Target: #{info['id']}")

        if info.get("is_placeholder"):
            self.hunt_status_label.config(fg=getattr(UI, 'STATE_WARN', getattr(UI, 'COLOR_WARNING', '#FFC107')))
            if hasattr(self.app, "_create_tooltip"):
                self.app._create_tooltip(self.hunt_status_label, self.app._t("target_card.unknown_mob"))
        else:
            self.hunt_status_label.config(fg=UI.COLOR_ACCENT)
            if hasattr(self.app, "_destroy_widget_tooltip"):
                self.app._destroy_widget_tooltip(self.hunt_status_label)
            self.hunt_status_label.unbind("<Enter>")
            self.hunt_status_label.unbind("<Leave>")

        try:
            scale_factor = getattr(self, "tk", None) and getattr(self, "tk", None).call('tk', 'scaling') * 72 / 100.0
            if scale_factor is None:
                scale_factor = 1.0
        except Exception:
            scale_factor = 1.0

        self.set_target_photo(None)

        if Image and ImageTk:
            def _load_and_set_photo():
                photo = None
                img_size = int(120 * scale_factor)
                if info.get("image_path") and os.path.exists(info["image_path"]):
                    try:
                        with Image.open(info["image_path"]) as img:
                            img = img.resize((img_size, img_size))
                            photo = ImageTk.PhotoImage(img)
                    except Exception:
                        pass

                if not photo:
                    default_path = os.path.join("assets", "images", "default_monster.png")
                    if os.path.exists(default_path):
                        try:
                            with Image.open(default_path) as img:
                                img = img.resize((img_size, img_size))
                                photo = ImageTk.PhotoImage(img)
                        except Exception:
                            pass

                self.set_target_photo(photo)

            self.app.schedule_ui_task(_load_and_set_photo)

    def _show_monster_context_menu(self, event):
        """Show rotation actions while preserving an existing multi-selection."""
        listbox = event.widget
        index = listbox.nearest(event.y)
        if index < 0 or index >= listbox.size():
            return
        if index not in listbox.curselection():
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(index)
            listbox.activate(index)
        self.app.monster_context_menu.tk_popup(event.x_root, event.y_root)
        return "break"

    def _select_all_monsters(self, _event=None):
        """Select every configured rotation row for bulk deletion."""
        if self.app.monster_rotation_listbox.size():
            self.app.monster_rotation_listbox.selection_set(0, tk.END)
        return "break"

    def _update_target_policy_layout(self):
        policy = self.app.target_policy_var.get()

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
        self.grid_columnconfigure(0, weight=1, uniform="panel")
        self.grid_columnconfigure(1, weight=1, uniform="panel")
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # Section 1: Active Target Card Panel (UX5.1)
        self.app.active_target_status_frame = tk.LabelFrame(
            self, text=self.app._t("hunt_active_target_status"), padx=4, pady=4
        )
        self.app.active_target_status_frame.grid(
            row=0, column=1, sticky="new", padx=(6, 0), pady=(0, 4)
        )
        self.app.active_target_status_frame.grid_columnconfigure(0, weight=1)

        # Header Bar
        status_frame = tk.Frame(self.app.active_target_status_frame, relief="groove", bd=1, height=32)
        status_frame.pack(fill="x", pady=(0, 4))

        self.hunt_status_label = tk.Label(
            status_frame,
            textvariable=self.app.hunt_status,
            font=UI.FONT_SECTION,
            fg=UI.COLOR_ACCENT,
            anchor="w",
        )
        self.hunt_status_label.pack(side="left", padx=8, pady=6)

        self.hunt_target_info_label = tk.Label(
            status_frame,
            textvariable=self.app.hunt_target_info,
            font=UI.FONT_LABEL,
            fg=UI.COLOR_SUBTEXT,
            anchor="e",
        )
        self.hunt_target_info_label.pack(side="right", padx=8, pady=6)

        # Target Card Container
        card_container = tk.Frame(self.app.active_target_status_frame, bg=UI.BG_MUTED)
        card_container.pack(fill="both", expand=True, padx=4, pady=4)

        try:
            scale_factor = getattr(self, "tk", None) and getattr(self, "tk", None).call('tk', 'scaling') * 72 / 100.0
            if scale_factor is None:
                scale_factor = 1.0
        except Exception:
            scale_factor = 1.0

        # Left Column (Image)
        self.target_image_label = tk.Label(
            card_container,
            text="[ NO IMAGE ]",
            bg=UI.BG_MUTED,
            width=20,  # rough width for text mode
            height=10
        )
        self.target_image_label.pack(side="left", padx=8, pady=8)

        # Right Column (Stats)
        stats_frame = tk.Frame(card_container, bg=UI.BG_MUTED)
        stats_frame.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        self.target_name_label = tk.Label(
            stats_frame,
            text="Unknown Target",
            font=(UI.FONT_FAMILY, int(14 * scale_factor), "bold"),
            bg=UI.BG_MUTED,
            anchor="w",
            wraplength=int(250 * scale_factor),
            justify="left"
        )
        self.target_name_label.pack(fill="x", anchor="w", pady=(0, 8))

        self.status_label = tk.Label(
            stats_frame,
            text="IDLE",
            font=(UI.FONT_FAMILY, int(12 * scale_factor), "bold"),
            bg=UI.BG_MUTED,
            fg=UI.COLOR_ACCENT,
            anchor="w"
        )
        self.status_label.pack(fill="x", anchor="w", pady=(0, 4))

        # ProgressBar (Replaced with Canvas for UX5.2)
        self.hp_canvas = tk.Canvas(stats_frame, height=24, bg=UI.BG_MUTED, highlightthickness=0)
        self.hp_canvas.pack(fill="x", pady=(0, 2))

        def _on_hp_canvas_resize(event):
            """Canvas resize handler for responsive width."""
            width = event.width
            if hasattr(self, "hp_bg"):
                self.hp_canvas.coords(self.hp_bg, 0, 0, width, 24)
            if hasattr(self, "hp_text"):
                self.hp_canvas.coords(self.hp_text, width / 2, 12)

        self.hp_canvas.bind('<Configure>', _on_hp_canvas_resize)

        # Pre-init Canvas objects
        self.hp_bg = self.hp_canvas.create_rectangle(0, 0, 1, 24, fill="#27272A", outline="#27272A")
        self.hp_fill = self.hp_canvas.create_rectangle(0, 0, 0, 24, fill="#00E86D", outline="#00E86D")
        self.hp_text = self.hp_canvas.create_text(0, 12, text="", fill="white", anchor="center")

        self.hp_percent_label = tk.Label(stats_frame, text="-", bg=UI.BG_MUTED, fg=UI.COLOR_SUBTEXT, anchor="w")
        self.hp_percent_label.pack(fill="x", anchor="w", pady=(0, 4))

        def create_stat_row(parent, label_key):
            row = tk.Frame(parent, bg=UI.BG_MUTED)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=self.app._t(label_key) + ":", bg=UI.BG_MUTED, fg=UI.COLOR_SUBTEXT, width=12, anchor="w").pack(side="left")
            val_lbl = tk.Label(row, text="-", bg=UI.BG_MUTED, anchor="w")
            val_lbl.pack(side="left", fill="x", expand=True)
            return val_lbl

        self.target_level_label = create_stat_row(stats_frame, "target_card.level")
        self.target_hp_label = create_stat_row(stats_frame, "target_card.max_hp")
        self.target_def_label = create_stat_row(stats_frame, "target_card.defense")

        # Section 2: Monster Selection (Phase 3: Multi-Monster Support)
        # Sprint 22 Patch 2: Dynamic title based on training mode
        self.app.monster_frame = tk.LabelFrame(
            self, text=self.app._t("monster_rotation_title"), font=UI.FONT_SECTION, fg=UI.COLOR_TEXT, padx=10, pady=8
        )
        self.app.monster_frame.grid(
            row=0, column=0, sticky="new", padx=(0, 6), pady=(0, 12)
        )
        self.app.monster_frame.grid_columnconfigure(0, weight=1)

        # Segmented control for target policy
        mode_bar = tk.Frame(self.app.monster_frame)
        mode_bar.pack(fill="x", pady=(0, 8))

        self.app.target_policy_var = tk.StringVar(
            value=self.app.hunt_cfg.get("target_policy", "configured_only")
        )

        def _on_policy_change(*args):
            # Only change if hunt is not running
            if self.app.click_running:
                # Revert to current hunt config policy
                self.app.target_policy_var.set(self.app.hunt_cfg.get("target_policy", "configured_only"))
                return

            new_policy = self.app.target_policy_var.get()
            if new_policy not in ["configured_only", "all_resolved", "any_target"]:
                new_policy = "configured_only"
                self.app.target_policy_var.set(new_policy)

            self.app.hunt_cfg["target_policy"] = new_policy
            self.app.has_unsaved_changes = True
            if hasattr(self.app, "_update_unsaved_indicator"):
                self.app._update_unsaved_indicator()
            self._update_target_policy_layout()

        if hasattr(self.app.target_policy_var, "trace_add"):
            self.app.target_policy_var.trace_add("write", _on_policy_change)

        policies = [
            ("configured_only", self.app._t("hunt_policy_configured")),
            ("all_resolved", self.app._t("hunt_policy_auto_detect")),
            ("any_target", self.app._t("hunt_policy_any_target"))
        ]

        self.policy_radios = []
        for val, text in policies:
            rb = ttk.Radiobutton(
                mode_bar,
                text=text,
                value=val,
                variable=self.app.target_policy_var,
                style="Toolbutton"
            )
            rb.pack(side="left", padx=2)
            self.policy_radios.append(rb)

        # Container for policy-specific views
        self.policy_content_frame = tk.Frame(self.app.monster_frame)
        self.policy_content_frame.pack(fill="both", expand=True)

        # 1. Configured Only view (and Configured part of All Resolved)
        # Note: We need a reusable container for configured list
        self.configured_container = tk.Frame(self.policy_content_frame)

        # 2. All Resolved view
        self.detected_container = tk.Frame(self.policy_content_frame)

        # 3. Any Target view
        self.any_target_container = tk.Frame(self.policy_content_frame)
        any_target_label = tk.Label(
            self.any_target_container,
            text=self.app._t("any_target_warning"),
            fg=UI.COLOR_WARNING,
            font=UI.FONT_TEXT
        )
        any_target_label.pack(pady=20)

        # Build detected list view
        tk.Label(self.detected_container, text=self.app._t("detected_monsters_title"), font=UI.FONT_LABEL).pack(anchor="w")
        detected_listbox_frame = tk.Frame(self.detected_container)
        detected_listbox_frame.pack(fill="both", expand=True)
        self.app.detected_monsters_listbox = tk.Listbox(
            detected_listbox_frame,
            height=5,
            exportselection=False,
            selectmode="single",
            font=UI.FONT_TEXT,
        )
        self.app.detected_monsters_listbox.pack(side="left", fill="both", expand=True)
        detected_scroll = tk.Scrollbar(detected_listbox_frame, command=self.app.detected_monsters_listbox.yview)
        detected_scroll.pack(side="right", fill="y")
        self.app.detected_monsters_listbox.config(yscrollcommand=detected_scroll.set)

        detected_btn_container = tk.Frame(self.detected_container)
        detected_btn_container.pack(side="right", fill="y", padx=(8, 0))
        self.app.btn_promote_monster = self.app._create_icon_button(
            detected_btn_container,
            icon_emoji="➕",
            command=lambda: getattr(self.app, 'promote_detected_monster', lambda x: None)(self.app.detected_monsters_listbox.curselection()),
            style="compact",
            bg_color=UI.BTN_ACCENT_BG if hasattr(UI, 'BTN_ACCENT_BG') else UI.COLOR_PRIMARY,
            hover_color=UI.BTN_ACCENT_HOVER if hasattr(UI, 'BTN_ACCENT_HOVER') else UI.COLOR_PRIMARY_TEXT,
        )
        self.app.btn_promote_monster.pack(pady=(0, 4))
        self.app._create_tooltip(
            self.app.btn_promote_monster, self.app._t("monster_promote")
        )

        # Bindings for promotion
        self.app.detected_monsters_listbox.bind("<Double-1>", lambda e: getattr(self.app, 'promote_detected_monster', lambda x: None)(self.app.detected_monsters_listbox.curselection()))
        self.app.detected_monsters_listbox.bind("<Return>", lambda e: getattr(self.app, 'promote_detected_monster', lambda x: None)(self.app.detected_monsters_listbox.curselection()))

        # Basic Drag-and-Drop setup
        def on_drag_start(event):
            listbox = event.widget
            if listbox.size() == 0:
                return
            idx = listbox.nearest(event.y)
            if idx < 0 or idx >= listbox.size():
                return
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(idx)
            listbox.activate(idx)
            # Payload is the idx (to look up the snapshot item)
            listbox._dnd_data = idx
            listbox.config(cursor="hand2")

        def on_drag_motion(event):
            event.widget.config(cursor="hand2")

        def on_drag_release(event):
            event.widget.config(cursor="")
            # Check if released over configured listbox
            x, y = event.widget.winfo_pointerxy()
            target = event.widget.winfo_containing(x, y)
            if target == getattr(self.app, 'monster_rotation_listbox', None):
                if hasattr(event.widget, '_dnd_data'):
                    idx = event.widget._dnd_data
                    getattr(self.app, 'promote_detected_monster', lambda x: None)((idx,))

        self.app.detected_monsters_listbox.bind("<ButtonPress-1>", on_drag_start)
        self.app.detected_monsters_listbox.bind("<B1-Motion>", on_drag_motion)
        self.app.detected_monsters_listbox.bind("<ButtonRelease-1>", on_drag_release)

        tk.Label(self.configured_container, text=self.app._t("configured_monsters_title"), font=UI.FONT_LABEL).pack(anchor="w")

        # Monster list for rotation selection
        list_container = tk.Frame(self.configured_container)
        list_container.pack(fill="both", expand=True)

        # Listbox frame with scrollbar
        listbox_frame = tk.Frame(list_container)
        listbox_frame.pack(side="left", fill="both", expand=True)

        self.app.monster_rotation_listbox = tk.Listbox(
            listbox_frame,
            height=5,
            exportselection=False,
            selectmode="extended",
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
            self.app.btn_add_monster, self.app._t("monster_rotation_add")
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
        self.app._create_tooltip(
            self.app.btn_remove_monster, self.app._t("monster_rotation_remove")
        )

        # Current monster status (Restored)
        self.app.monster_status_var = tk.StringVar()
        tk.Label(
            self.app.monster_frame,
            textvariable=self.app.monster_status_var,
            fg=UI.COLOR_PRIMARY,
            font=(UI.FONT_FAMILY, UI.SIZE_TEXT, "bold"),
        ).pack(fill="x", pady=(8, 0))

        # Re-attach bindings
        # Preserve selection behavior when the handler exists, while avoiding
        # startup errors in app states where the method is not available.
        if hasattr(self.app, "_on_monster_list_select"):
            self.app.monster_rotation_listbox.bind(
                "<<ListboxSelect>>", self.app._on_monster_list_select
            )
        self.app.monster_rotation_listbox.bind(
            "<Delete>", self.app._on_monster_delete_from_list
        )
        self.app.monster_rotation_listbox.bind(
            "<BackSpace>", self.app._on_monster_delete_from_list
        )  # Also backspace

        # Sprint 22 Patch 2: Context menu for right-click delete
        self.app.monster_context_menu = tk.Menu(self.app.monster_rotation_listbox, tearoff=0)
        self.app.monster_context_menu.add_command(
            label=self.app._t("monster_delete"),  # "Delete" / "Xóa"
            command=self.app._on_monster_delete_from_list,
        )
        self.app._create_tooltip(
            self.app.monster_context_menu,
            self.app._t("monster_rotation_delete_hint"),
        )
        self.app.monster_rotation_listbox.bind(
            "<Button-3>", self._show_monster_context_menu
        )  # Right-click
        self.app.monster_rotation_listbox.bind(
            "<Control-a>", self._select_all_monsters
        )
        self.app.monster_rotation_listbox.bind(
            "<Control-A>", self._select_all_monsters
        )
        tk.Label(
            self.configured_container,
            text=self.app._t("monster_rotation_delete_hint"),
            fg=UI.COLOR_SUBTEXT,
            font=UI.FONT_TEXT,
            anchor="w",
        ).pack(fill="x", pady=(4, 0))

        # Sprint 22 Patch 2: Hint for switching back to normal mode
        self.app.training_mode_hint_var = tk.StringVar()
        self.app.training_mode_hint_label = tk.Label(
            self.app.monster_frame,
            textvariable=self.app.training_mode_hint_var,
            fg="#FF6F00",  # Orange
            font=(UI.FONT_FAMILY, UI.SIZE_TEXT, "italic"),
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
        self.skill_strip_frame.grid_columnconfigure(0, weight=1, uniform='skill_col')
        self.skill_strip_frame.grid_columnconfigure(1, weight=2, uniform='skill_col')

        # Option (a): Đây là bản thiết kế lại/thay thế cho panel đã làm ở CB3B.
        # Panel cũ từ CB3B (nếu có ở nơi khác) sẽ được loại bỏ, tránh tồn tại 2 bản UI cho cùng chức năng.
        # Section 3: Dual-Lane Skill Strip (Combo & Buffs)

        border_color = getattr(UI, "BORDER_COLOR", "#E0E0E0")
        skill_frame_outer = tk.Frame(
            self.skill_strip_frame,
            highlightbackground=border_color,
            highlightthickness=1,
            highlightcolor=border_color,
            bg=UI.BG_PANEL
        )
        skill_frame_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        # Setup Auto Combo Control Frame
        ctrl_frame = tk.Frame(skill_frame_outer, bg=UI.BG_PANEL)
        ctrl_frame.pack(side="top", fill="x", padx=4, pady=(4, 0))

        # Ensure combo config exists
        if "combo" not in self.app.hunt_cfg:
            self.app.hunt_cfg["combo"] = {"enabled": False, "combo_start_key": "Alt+3"}

        self.app.auto_combo_var = tk.BooleanVar(value=self.app.hunt_cfg["combo"].get("enabled", False))

        def on_auto_combo_toggle():
            is_enabled = self.app.auto_combo_var.get()
            self.app.hunt_cfg["combo"]["enabled"] = is_enabled
            if is_enabled:
                self.app.combo_start_key_cmb.config(state="readonly")
            else:
                self.app.combo_start_key_cmb.config(state="disabled")

        auto_combo_cb = tk.Checkbutton(
            ctrl_frame,
            text=self.app._t("skill_strip.auto_combo") if self.app._t("skill_strip.auto_combo") != "skill_strip.auto_combo" else "Bật Auto Combo",
            variable=self.app.auto_combo_var,
            command=on_auto_combo_toggle,
            bg=UI.BG_PANEL,
            font=UI.FONT_TEXT
        )
        auto_combo_cb.pack(side="left", padx=(4, 8))

        tk.Label(
            ctrl_frame,
            text=self.app._t("skill_strip.combo_start_key") if self.app._t("skill_strip.combo_start_key") != "skill_strip.combo_start_key" else "Phím Mở Combo",
            bg=UI.BG_PANEL,
            font=UI.FONT_TEXT
        ).pack(side="left")

        self.app.combo_start_key_cmb = ttk.Combobox(
            ctrl_frame,
            values=["Alt+1", "Alt+2", "Alt+3", "Alt+4", "Alt+5"],
            state="normal" if self.app.auto_combo_var.get() else "disabled",
            width=8
        )
        self.app.combo_start_key_cmb.set(self.app.hunt_cfg["combo"].get("combo_start_key", "Alt+3"))
        self.app.combo_start_key_cmb.pack(side="left", padx=4)

        def on_combo_key_change(event):
            self.app.hunt_cfg["combo"]["combo_start_key"] = self.app.combo_start_key_cmb.get()

        self.app.combo_start_key_cmb.bind("<<ComboboxSelected>>", on_combo_key_change)
        # self.app.combo_start_key_cmb.bind("<KeyRelease>", on_combo_key_change)

        # Lanes container
        lanes_frame = tk.Frame(skill_frame_outer, bg=UI.BG_PANEL)
        lanes_frame.pack(fill="both", expand=True, padx=4, pady=4)

        self.app.skill_slot_vars = []
        self.app.skill_slot_boxes = []
        self.app.skill_slot_key_labels = []
        self.app.skill_slot_stats_labels = []
        for i in range(4):
            lanes_frame.grid_columnconfigure(i, weight=1, uniform='card_col')

        # To support high DPI
        try:
            scale_factor = getattr(self, "tk", None) and getattr(self, "tk", None).call('tk', 'scaling') * 72 / 100.0
            if scale_factor is None:
                scale_factor = 1.0
        except Exception:
            scale_factor = 1.0

        card_font = (UI.FONT_FAMILY, int(max(8, 9 * scale_factor)))
        badge_pad = int(max(2, 4 * scale_factor))

        def update_card_stats(lbl, skill_name):
            skills_by_name = {
                s.get("name"): s
                for s in getattr(self.app, "skills", [])
                if isinstance(s, dict) and s.get("name")
            }
            skill = skills_by_name.get(skill_name, {})
            cast_time = skill.get("cast_time")
            cd = skill.get("cooldown")

            cast_str = f"{cast_time}s" if cast_time is not None else "--s"
            cd_str = f"{cd}s" if cd is not None else "--s"
            lbl.config(text=f"⚡ {cast_str} | ⏳ {cd_str}")

        self.update_card_stats = update_card_stats

        # Build cards
        for idx in range(self.app.skill_slot_count):
            is_combo_lane = idx < 4
            row = 0 if is_combo_lane else 1
            col = idx if is_combo_lane else (idx - 4)

            card = tk.Frame(lanes_frame, bg=UI.BG_DEFAULT, highlightbackground="#D0D0D0", highlightthickness=1)
            card.grid(row=row, column=col, sticky="ew", padx=2, pady=2)

            var = tk.StringVar()
            self.app.skill_slot_vars.append(var)

            # Title
            t_combo = self.app._t('skill_strip.combo_lane')
            t_buff = self.app._t('skill_strip.buff_lane')
            title_text = f"{t_combo if t_combo != 'skill_strip.combo_lane' else 'Combo Chain'} {col + 1}" if is_combo_lane else f"{t_buff if t_buff != 'skill_strip.buff_lane' else 'Buff Lane'} {col + 1}"

            tk.Label(card, text=title_text, bg=UI.BG_DEFAULT, fg=UI.COLOR_SUBTEXT, font=(UI.FONT_FAMILY, int(8 * scale_factor))).pack(anchor="w", padx=2, pady=(2, 0))

            # Combobox
            cmb = ttk.Combobox(card, textvariable=var, state="readonly")
            cmb.pack(fill="x", padx=badge_pad, pady=badge_pad)

            stats_lbl = tk.Label(card, text="⚡ --s | ⏳ --s", fg=UI.COLOR_SUBTEXT, bg=UI.BG_DEFAULT, font=card_font)

            def _on_cmb_selected(event, v=var, lbl=stats_lbl):
                if hasattr(self.app, "on_skill_slot_changed"):
                    self.app.on_skill_slot_changed(event)
                update_card_stats(lbl, v.get().strip())

            cmb.bind("<<ComboboxSelected>>", _on_cmb_selected)
            self.app.skill_slot_boxes.append(cmb)

            # Badges area
            badge_frame = tk.Frame(card, bg=UI.BG_DEFAULT)
            badge_frame.pack(fill="x", padx=2, pady=(0, 2))

            key_lbl = tk.Label(badge_frame, text="", width=6, anchor="w", fg="#333", bg=UI.BG_DEFAULT, font=card_font)
            key_lbl.pack(side="left")
            self.app.skill_slot_key_labels.append(key_lbl)

            stats_lbl.pack(side="right")
            self.app.skill_slot_stats_labels.append(stats_lbl)

            # Tooltip
            if hasattr(self.app, "_create_tooltip"):
                self.app._create_tooltip(card, self.app._t("skill_strip.tooltip_placeholder"))

        self.app._refresh_monster_select_options()
        # Replaced _load_skill_slots_from_cfg with equivalent logic inline
        saved = (
            self.app.hunt_cfg.get("skill_slots", []) if hasattr(self.app, "hunt_cfg") else []
        )

        normalized_slots = []
        for slot in saved:
            if isinstance(slot, dict):
                normalized_slots.append(slot.get("name", ""))
            elif isinstance(slot, str):
                normalized_slots.append(slot)
            else:
                normalized_slots.append("")

        self.app.skill_slot_saved_names = [name for name in normalized_slots if name]

        if hasattr(self.app, "_refresh_skill_slots_options"):
            self.app._refresh_skill_slots_options()

        if hasattr(self.app, "skill_slot_vars"):
            for idx, var in enumerate(self.app.skill_slot_vars):
                name = ""
                if idx < len(normalized_slots):
                    name = normalized_slots[idx]
                var.set(name)

        if hasattr(self.app, "_update_attack_keys_from_slots"):
            self.app._update_attack_keys_from_slots()

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
            height=3,
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
        if hasattr(self.app, "skill_stats_tree"):
            self.app.skill_stats_tree.insert(
                "",
                "end",
                values=(self.app._t("skill_stats_empty"), "", "", "", ""),
                tags=("placeholder",),
            )

        # Render the default configured-only view after all policy containers exist.
        self._update_target_policy_layout()
