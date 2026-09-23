from dialogs.monster_picker import MonsterPickerDialog
from lib.ui.dialog_service import DialogService
from lib.events.event_bus import EventBus, MonsterMoveUpEvent, MonsterMoveDownEvent, MonsterDeleteEvent, MonsterAddSmartEvent, MonsterRotationUpdatedEvent, SceneMonstersDetectedEvent
import tkinter as tk
from tkinter import ttk
from lib.ui_style_v2 import UIStyleV2 as UI
from ui.helpers import UIHelper
from ui.components.styled_panel import StyledPanel
from ui.components.empty_state import EmptyState


class MonsterTargetPanel(ttk.LabelFrame):
    MODULE_NAME = "monster_target_panel"
    SCREEN_NAME = "main"

    def __init__(self, parent, app, scale_factor=1.0, hunt_tab=None):
        padding = (int(10 * scale_factor), int(8 * scale_factor))
        super().__init__(parent, text="🎯 Target Setup", padding=padding)
        # Fix typography hierarchy per Task 10
        self.configure(labelanchor="n")
        lbl = tk.Label(self, text="🎯 Target Setup", font=UI.get_font("title", weight="bold"), bg=UI.BG_BASE, fg=UI.TEXT_PRIMARY)
        self.configure(labelwidget=lbl)
        self.app = app
        self.scale_factor = scale_factor
        self.hunt_tab = hunt_tab
        self._build_ui()
        if hasattr(self.app.state_controller.ui_vars.get('training_mode'), 'trace_add'):
            self.app.state_controller.ui_vars['training_mode'].trace_add('write', self.update_training_mode_buttons)

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
        self.monster_frame_panel = StyledPanel(self, show_border=False)
        self.monster_frame = self.monster_frame_panel.get_content_frame()
        self.monster_frame.pack(fill="both", expand=True)

        mode_bar = tk.Frame(self.monster_frame, bg=UI.BG_SURFACE)
        mode_bar.pack(fill="x", padx=10, pady=(0, 8))

        self.app.state_controller.set_ui_var('target_policy', self.app.state_controller.hunt_cfg.get("target_policy", "configured_only"))

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

        # Hunt Area Set Button
        def _on_draw_hunt_area():
            from ui.helpers.capture_helper import CaptureHelper
            def _on_drawn(region):
                if region:
                    if "rois" not in self.app.state_controller.hunt_cfg:
                        self.app.state_controller.hunt_cfg["rois"] = {}
                    self.app.state_controller.hunt_cfg["rois"]["hunt_area"] = list(region)

                    from lib.features.hunt.hunt_config import save_hunt_config
                    success = save_hunt_config(self.app.state_controller.hunt_cfg)
                    if not success:
                        print("Failed to save hunt area via save_hunt_config")

            CaptureHelper.start_region_selection(self.winfo_toplevel(), _on_drawn)

        from ui.components.icon_button import create_icon_button

        self.btn_set_hunt_area = create_icon_button(
            parent=mode_bar,
            element_id="btn_set_hunt_area",
            icon_name="crop",
            text=self.app._t("hunt_area.set") if hasattr(self.app, "_t") else "Set Hunt Area",
            command=_on_draw_hunt_area,
            button_type="neutral"
        )
        self.btn_set_hunt_area.pack(side="right", padx=10, pady=4)

        self.policy_content_frame = tk.Frame(self.monster_frame, bg=UI.BG_SURFACE)
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

        self.monster_rotation_listbox = tk.Listbox(
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
        self.monster_rotation_listbox.pack(side="left", fill="both", expand=True)
        # Register in app for legacy controller access for now, but not in UI state widgets
        self.app.state_controller.ui_widgets["monster_rotation_listbox"] = self.monster_rotation_listbox

        monster_scroll = ttk.Scrollbar(
            listbox_frame,
            orient="vertical",
            command=self.monster_rotation_listbox.yview,
        )
        monster_scroll.pack(side="right", fill="y")
        self.monster_rotation_listbox.config(yscrollcommand=monster_scroll.set)

        # Create a toolbar frame with a subtle background and rounded-like appearance
        btn_container = tk.Frame(
            list_container,
            bg=UI.BG_ELEVATED,
            highlightbackground=UI.BORDER_SUBTLE,
            highlightthickness=1,
            padx=4, pady=4
        )
        btn_container.pack(side="right", fill="y", padx=(8, 0))

        from ui.components.icon_button import create_icon_button

        self.btn_add = create_icon_button(
            parent=btn_container,
            element_id="btn_target_add",
            icon_name="add",
            text="➕", # fallback
            command=self._on_monster_add_smart,
            button_type="default",
            tooltip_key="monster_rotation_add"
        )
        self.btn_add.pack(pady=(0, 4))

        self.btn_move_up = create_icon_button(
            parent=btn_container,
            element_id="btn_target_up",
            icon_name="up",
            text="↑", # fallback
            command=self._on_monster_move_up,
            button_type="default"
        )
        self.btn_move_up.pack(pady=(0, 4))

        self.btn_move_down = create_icon_button(
            parent=btn_container,
            element_id="btn_target_down",
            icon_name="down",
            text="↓", # fallback
            command=self._on_monster_move_down,
            button_type="default"
        )
        self.btn_move_down.pack(pady=(0, 12))

        self.btn_remove_monster = create_icon_button(
            parent=btn_container,
            element_id="btn_target_remove",
            icon_name="delete",
            text="✖", # fallback
            command=self._on_monster_delete_from_list,
            button_type="danger",
            tooltip_key="monster_rotation_remove"
        )
        self.btn_remove_monster.pack()


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
        self.detected_monsters_listbox = tk.Listbox(
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
        self.detected_monsters_listbox.pack(side="left", fill="both", expand=True)
        self.app.state_controller.ui_widgets["detected_monsters_listbox"] = self.detected_monsters_listbox

        detected_scroll = ttk.Scrollbar(
            detected_listbox_frame, command=self.detected_monsters_listbox.yview
        )
        detected_scroll.pack(side="right", fill="y")
        self.detected_monsters_listbox.config(yscrollcommand=detected_scroll.set)

        detected_btn_container = tk.Frame(self.detected_container, bg=UI.BG_SURFACE)
        detected_btn_container.pack(side="right", fill="y", padx=(8, 0))
        def promote_current_selection():
            selection = self.detected_monsters_listbox.curselection()
            if not selection:
                return
            idx = selection[0]
            if not hasattr(self.app, "_detected_snapshot_items") or idx >= len(self.app._detected_snapshot_items):
                return
            runtime_item = self.app._detected_snapshot_items[idx]
            if hasattr(self.app, "monster_rotation_controller"):
                self.app.monster_rotation_controller.promote_detected_monster(runtime_item)

        from ui.components.icon_button import create_icon_button
        self.btn_promote_monster = create_icon_button(
            parent=detected_btn_container,
            element_id="btn_target_promote",
            icon_name="add",
            text="➕", # fallback
            command=promote_current_selection,
            button_type="default",
            tooltip_key="monster_rotation_promote"
        )
        self.btn_promote_monster.pack(pady=(0, 4))

        self.detected_monsters_listbox.bind("<Double-1>", lambda e: promote_current_selection())
        self.detected_monsters_listbox.bind("<Return>", lambda e: promote_current_selection())

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
                    idx = event.widget.drag_data["source_idx"]
                    if hasattr(self.app, "_detected_snapshot_items") and idx < len(self.app._detected_snapshot_items):
                        runtime_item = self.app._detected_snapshot_items[idx]
                        if hasattr(self.app, "monster_rotation_controller"):
                            self.app.monster_rotation_controller.promote_detected_monster(runtime_item)
                target.selection_clear(0, tk.END)
            del event.widget.drag_data

        # Apply drag bindings
        self.detected_monsters_listbox.bind("<ButtonPress-1>", on_drag_start)
        self.detected_monsters_listbox.bind("<B1-Motion>", on_drag_motion)
        self.detected_monsters_listbox.bind("<ButtonRelease-1>", on_drop)

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

        tk.Label(
            self.monster_frame,
            textvariable=self.app.state_controller.ui_vars['monster_status'],
            fg=UI.TEXT_PRIMARY,
            bg=UI.BG_SURFACE,
            font=UI.FONT_TEXT,
        ).pack(fill="x", pady=(8, 0), padx=10)

        self.monster_rotation_listbox.bind(
            "<Delete>", self._on_monster_delete_from_list
        )
        self.monster_rotation_listbox.bind(
            "<BackSpace>", self._on_monster_delete_from_list
        )

        self.monster_context_menu = tk.Menu(
            self.monster_rotation_listbox, tearoff=0
        )
        self.monster_context_menu.add_command(
            label=self.app._t("monster_delete"),
            command=self._on_monster_delete_from_list,
        )
        UIHelper.create_tooltip(
            self.monster_context_menu,
            self.app._t("monster_rotation_delete_hint"),
        )

        def _show_monster_context_menu(event):
            try:
                self.monster_rotation_listbox.selection_clear(0, tk.END)
                self.monster_rotation_listbox.selection_set(
                    self.monster_rotation_listbox.nearest(event.y)
                )
                self.monster_context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.monster_context_menu.grab_release()

        def _select_all_monsters(event):
            self.monster_rotation_listbox.selection_set(0, tk.END)
            return "break"

        self.monster_rotation_listbox.bind(
            "<Button-3>", _show_monster_context_menu
        )
        self.monster_rotation_listbox.bind("<Control-a>", _select_all_monsters)
        self.monster_rotation_listbox.bind("<Control-A>", _select_all_monsters)

        self.configured_empty = EmptyState(
            self.configured_container,
            icon="🎯",
            message=self.app._t("monster_target.empty_list"),
            submessage=self.app._t("monster_target.empty_list_submessage"),
        )
        self.configured_empty.pack(fill="both", expand=True, pady=(4, 0))

        def _update_configured_empty_state(*args):
            if hasattr(self, "monster_rotation_listbox") and self.monster_rotation_listbox:
                if (self.monster_rotation_listbox.size() or 0) > 0:
                    self.configured_empty.pack_forget()
                else:
                    self.configured_empty.pack(fill="both", expand=True, pady=(4, 0))

        # Replaced polling with a direct reference to be called in refresh
        self._update_configured_empty_state_ref = _update_configured_empty_state
        _update_configured_empty_state()

        EventBus.bind(SceneMonstersDetectedEvent, self._update_detected_monsters_list)
        EventBus.bind(MonsterRotationUpdatedEvent, self._refresh_monster_rotation_list)



        self.training_mode_hint_label = tk.Label(
            self.monster_frame,
            textvariable=self.app.state_controller.ui_vars['training_mode_hint'],
            fg=UI.ACCENT_AMBER,
            bg=UI.BG_SURFACE,
            font=UI.FONT_TEXT,
            wraplength=400,
            justify="left",
        )
        self.training_mode_hint_label.pack(fill="x", pady=(4, 0), padx=10)

        # Bind training mode state changes
        if hasattr(self.app.state_controller.ui_vars.get('training_mode'), "trace_add"):
            self.app.state_controller.ui_vars['training_mode'].trace_add(
                "write", self.update_training_mode_buttons
            )

        # Initial call to set correct state
        self.update_training_mode_buttons()

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



    def _on_monster_add_smart(self, _evt=None):
        def on_monster_selected(record):
            EventBus.trigger(MonsterAddSmartEvent(record))

        MonsterPickerDialog(
            self, getattr(self.app, "lang", "vi"), on_monster_selected, getattr(self.app, "_t")
        )


    def _on_monster_move_up(self, _evt=None):
        selection = self.monster_rotation_listbox.curselection()
        if selection:
            EventBus.trigger(MonsterMoveUpEvent(selection[0]))

    def _on_monster_move_down(self, _evt=None):
        selection = self.monster_rotation_listbox.curselection()
        if selection:
            EventBus.trigger(MonsterMoveDownEvent(selection[0]))

    def _on_monster_delete_from_list(self, _evt=None):
        selection = self.monster_rotation_listbox.curselection()
        if selection:
            EventBus.trigger(MonsterDeleteEvent(list(selection)))


    def _update_detected_monsters_list(self, event):
        snapshot = event.snapshot
        self._last_snapshot = snapshot

        if getattr(self.app.state_controller, "hunt_cfg", {}).get("target_policy", "configured_only") != "all_resolved":
            return

        if not hasattr(self, "detected_monsters_listbox"):
            return


        current_selection = self.detected_monsters_listbox.curselection()
        selected_idx = current_selection[0] if current_selection else None

        yview = self.detected_monsters_listbox.yview()
        self.detected_monsters_listbox.delete(0, tk.END)
        self._detected_snapshot_items = []

        configured_keys = {
            (m.get("monster_id"), m.get("dungeon_id"))
            for m in getattr(self.app.state_controller, "monster_rotation", [])
            if m.get("monster_id")
        }

        for _idx, item in enumerate(snapshot):
            self._detected_snapshot_items.append(item)
            name = item.get("name", "Unknown")
            resolution_state = item.get("resolution_state", "unmapped_visual")
            monster_id = item.get("monster_id")

            if resolution_state == "db_match":
                status = "✓ "
                if (monster_id, item.get("dungeon_id")) in configured_keys:
                    status += f"[{self.app._t('monster_promoted')}] "
                elif item.get("confidence", 0) > 0:
                    status += f"({item['confidence']:.2f}) "
                display_text = (
                    f"{status}{name} #{monster_id} - {self.app._t('monster_db_match')}"
                )
            elif resolution_state == "db_miss":
                display_text = f"⚠ {name} - {self.app._t('monster_db_missing')}"
            else:
                display_text = f"❓ {self.app._t('monster_unidentified')} ({item.get('template_label', '')})"

            self.detected_monsters_listbox.insert(tk.END, display_text)

        if selected_idx is not None and selected_idx < self.detected_monsters_listbox.size():
            self.detected_monsters_listbox.selection_set(selected_idx)
        self.detected_monsters_listbox.yview_moveto(yview[0])



    def _refresh_monster_rotation_list(self, event=None):
        if not hasattr(self, "monster_rotation_listbox"):
            return

        if hasattr(self.app, "_update_unsaved_indicator"):
            self.app._update_unsaved_indicator()

        self.monster_rotation_listbox.delete(0, tk.END)

        from database import get_monster_by_id_api, find_monster_by_name_api

        self.app.state_controller.monster_rotation.sort(key=lambda x: x.get("priority", 999))

        for _idx, entry in enumerate(self.app.state_controller.monster_rotation):
            monster_id = entry.get("monster_id")
            name = entry.get("name")
            dungeon_id = entry.get("dungeon_id")

            cache_key = f"{monster_id}_{name}_{dungeon_id}"
            manager = self.app.state_controller._monster_session_manager

            if cache_key not in manager._metadata_cache:
                db_record = get_monster_by_id_api(str(monster_id)) if monster_id else None
                if not db_record and name:
                    db_record = find_monster_by_name_api(name, dungeon_id)
                manager._metadata_cache[cache_key] = db_record
            else:
                db_record = manager._metadata_cache[cache_key]

            if db_record:
                level = db_record.get("level", "--")
                hp = db_record.get("hp", "--")
                display_str = f"[#{monster_id}] {name} - Lv.{level} | HP: {hp}"
            else:
                display_str = f"[{self.app._t('monster_rotation_unknown')}] {name} - Lv.-- | HP: --"

            self.monster_rotation_listbox.insert(tk.END, display_str)

        if event and hasattr(event, "selected_index") and event.selected_index is not None:
            self.monster_rotation_listbox.selection_set(event.selected_index)

        if hasattr(self, "_update_configured_empty_state_ref"):
            self._update_configured_empty_state_ref()

        if hasattr(self, "_last_snapshot"):
            # Mock an event
            class DummyEvent:
                def __init__(self, snapshot):
                    self.snapshot = snapshot
            self._update_detected_monsters_list(DummyEvent(self._last_snapshot))

    def destroy(self):
        EventBus.unbind(SceneMonstersDetectedEvent, self._update_detected_monsters_list)
        EventBus.unbind(MonsterRotationUpdatedEvent, self._refresh_monster_rotation_list)
        super().destroy()

    def update_training_mode_buttons(self, *args):
        """Update monster control buttons based on training mode state.

        Training Mode ON:
        - Add button: Shows finish.ico if dummy set, else add.ico with training tooltip
        - Add button: Disabled if training dummy already in list
        - Up/Down buttons: Disabled (no rotation needed)

        Training Mode OFF:
        - Add button: Shows add.ico with normal tooltip
        - Add button: Always enabled
        - Up/Down buttons: Enabled
        """
        if not hasattr(self, "btn_add"):
            return

        is_training = self.app.state_controller.get_ui_var('training_mode')
        has_training_dummy = any(
            m.get("training_mode", False) for m in self.app.state_controller.monster_rotation
        )

        from ui.components.icon_button import update_button_state

        if is_training:
            # Training mode: Update add button
            if has_training_dummy:
                # Dummy already set - show accept icon and disable
                update_button_state(
                    self.btn_add,
                    enabled=False,
                    icon_name="accept",
                    icon_fallback="✓",
                    tooltip_text=self.app._t("tooltip_add_monster_locked")
                )
            else:
                # No dummy yet - show add icon and enable
                update_button_state(
                    self.btn_add,
                    enabled=True,
                    icon_name="add",
                    icon_fallback="➕",
                    tooltip_text=self.app._t("tooltip_add_monster_training")
                )

            # Disable priority reorder buttons with locked icon
            for btn in [self.btn_move_up, self.btn_move_down]:
                update_button_state(
                    btn,
                    enabled=False,
                    icon_name="locked",
                    icon_fallback="🔒",
                    tooltip_text=self.app._t("tooltip_reorder_locked")
                )
        else:
            # Normal mode: Restore defaults
            update_button_state(
                self.btn_add,
                enabled=True,
                icon_name="add",
                icon_fallback="➕",
                tooltip_text=self.app._t("tooltip_add_monster_normal")
            )

            # Enable priority reorder buttons
            update_button_state(
                self.btn_move_up,
                enabled=True,
                icon_name="up",
                icon_fallback="↑",
                tooltip_text=self.app._t("tooltip_move_up")
            )
            update_button_state(
                self.btn_move_down,
                enabled=True,
                icon_name="down",
                icon_fallback="↓",
                tooltip_text=self.app._t("tooltip_move_down")
            )
