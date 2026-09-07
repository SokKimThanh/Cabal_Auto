import tkinter as tk
from tkinter import ttk
from lib.ui_style_v2 import UIStyleV2 as UI

from lib.features.monsters.monster_repo import get_target_monster_info
from ui.panels.skill_panel import SkillPanel
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
        if not hasattr(self, "hunt_status_badge"):
            return

        if state == "running":
            self.hunt_status_badge.set_status("hunting")
        elif state == "error":
            self.hunt_status_badge.set_status("waiting")  # Fallback for error
        elif state == "idle":
            self.hunt_status_badge.set_status("waiting")
        elif state == "stopped":
            self.hunt_status_badge.set_status("ready")

    def clear_target_photo(self):
        if hasattr(self, "target_image_label") and self.target_image_label:
            self.target_image_label.configure(
                image="", text=self.app._t("target_card.no_image"), bg=UI.BG_SURFACE
            )
        if hasattr(self, "_current_target_photo") and self._current_target_photo:
            del self._current_target_photo
            self._current_target_photo = None

    def set_target_photo(self, photo_image=None):
        self.clear_target_photo()
        if photo_image:
            self._current_target_photo = photo_image
            self.target_image_label.configure(image=photo_image, text="")

    def show_recovery(self):
        if hasattr(self, "recovery_frame"):
            self.recovery_frame.config(bg=UI.ACCENT_AMBER)
            self.recovery_frame.pack(fill="x", pady=(4, 4), after=self.hp_percent_label)
            if hasattr(self, "recovery_btn"):
                self.recovery_btn.config(
                    state="normal", text=self.app._t("target_card.recovery_btn")
                )

    def hide_recovery(self):
        if hasattr(self, "recovery_frame"):
            self.recovery_frame.pack_forget()

    def _on_recovery_click(self):
        from lib.features.hunt.window_selection_service import WindowRecoveryController

        if not hasattr(self, "app") or not hasattr(self.app, "hunt_cfg"):
            return

        hwnd = self.app.hunt_cfg.get("window_hwnd")
        if not hwnd:
            return

        if hasattr(self, "recovery_btn"):
            self.recovery_btn.config(state="disabled")

        def _on_progress(step):
            if hasattr(self, "recovery_btn"):
                text = self.app._t("target_card.recovery_retry").format(step=step)
                self.recovery_btn.config(text=text)

        def _on_failure():
            if hasattr(self, "recovery_frame"):
                self.recovery_frame.config(
                    bg=getattr(
                        UI, "STATE_ERROR", getattr(UI, "COLOR_DANGER", "#F44336")
                    )
                )
            if hasattr(self, "recovery_btn"):
                self.recovery_btn.config(state="normal")
            if hasattr(self.app, "show_toast"):
                self.app.show_toast(self.app._t("target_card.recovery_failed"))

        WindowRecoveryController.instance().start_async_recovery(
            hwnd=int(hwnd),
            schedule_after_ms=self.after,
            on_progress=_on_progress,
            on_failure=_on_failure,
            delay_ms=500,
        )

    def update_status(self, status_string: str):
        if not hasattr(self, "status_label"):
            return
        self.status_label.config(text=status_string)
        if status_string == "APPROACHING":
            self.status_label.config(fg=UI.ACCENT_AMBER)
        elif status_string == "ATTACKING":
            self.status_label.config(fg=UI.DANGER)
        elif status_string == "TARGET_DEAD":
            self.status_label.config(fg=UI.TEXT_MUTED)
        else:
            self.status_label.config(fg=UI.ACCENT_BLUE)

    def update_hp_display(
        self, hp_percent: float, current_hp: int = 0, max_hp: int = 10000
    ):
        """Update Canvas HP bar with color and text."""
        if not hasattr(self, "hp_canvas"):
            return

        # Death case
        if hp_percent == 0.0:
            self.hp_canvas.itemconfig(self.hp_fill, fill="#52525B", outline="#52525B")
            self.hp_canvas.itemconfig(
                self.hp_text,
                text=(
                    self.app._t("target_card.target_dead")
                    if hasattr(self.app, "_t")
                    else "[ Đã Tiêu Diệt ]"
                ),
            )
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
            if hasattr(self, "hp_progressbar"):
                self.hp_progressbar.config(value=0.0)
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
        self.hp_canvas.coords(self.hp_text, width / 2, 12)
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
            self._pending_clear_id = self.after(
                delay_ms, lambda: self.clear_target_card(0)
            )
            return

        self.clear_target_photo()
        if hasattr(self, "target_name_label"):
            self.target_name_label.config(text=self.app._t("target_card.unknown_mob"))
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
        self.update_status(self.app._t("target_card.status_idle"))
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
            if isinstance(self.hunt_status_label, tk.Label): self.hunt_status_label.config(fg=UI.ACCENT_AMBER)
            if hasattr(self.app, "_create_tooltip"):
                self.app._create_tooltip(
                    self.hunt_status_label, self.app._t("target_card.unknown_mob")
                )
        else:
            if isinstance(self.hunt_status_label, tk.Label): self.hunt_status_label.config(fg=UI.ACCENT_GREEN)
            if hasattr(self.app, "_destroy_widget_tooltip"):
                self.app._destroy_widget_tooltip(self.hunt_status_label)
            self.hunt_status_label.unbind("<Enter>")
            self.hunt_status_label.unbind("<Leave>")

        try:
            scale_factor = (
                getattr(self, "tk", None)
                and getattr(self, "tk", None).call("tk", "scaling") * 72 / 100.0
            )
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
                    default_path = os.path.join(
                        "assets", "images", "default_monster.png"
                    )
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

        # Layout: 4-Panel Workspace Redesign (ResponsiveGridBase Version)

        try:
            scale_factor = (
                getattr(self, "tk", None)
                and getattr(self, "tk", None).call("tk", "scaling") * 72 / 100.0
            )
            if scale_factor is None:
                scale_factor = 1.0
        except Exception:
            scale_factor = 1.0

        # Main static container for the entire tab
        self.main_container = tk.Frame(self, bg=UI.BG_BASE)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Pinned top section (Stacking Priority) - Must NOT be in the scrollable area
        from ui.panels.monster_target_panel import MonsterTargetPanel
        self.pinned_container = tk.Frame(self.main_container, bg=UI.BG_BASE)
        self.pinned_container.pack(side=tk.TOP, fill=tk.X, padx=UI.SPACE_MD, pady=(UI.SPACE_MD, 0))

        self.monster_target_panel = MonsterTargetPanel(
            self.pinned_container,
            self.app,
            scale_factor,
            hunt_tab=self,
        )
        self.monster_target_panel.pack(fill=tk.X, expand=True)

        # Responsive Scrollable Grid for the rest of the panels
        from ui.components.base.responsive_grid_base import ResponsiveGridBase
        self.scrollable_workspace = ResponsiveGridBase(self.main_container, bg=UI.BG_BASE)
        self.scrollable_workspace.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=UI.SPACE_MD, pady=UI.SPACE_MD)

        content_frame = self.scrollable_workspace.get_content_frame()
        content_frame.config(bg=UI.BG_BASE)

        # Set up a 2-column grid layout inside the responsive area (60% / 40%)
        content_frame.columnconfigure(0, weight=6)
        content_frame.columnconfigure(1, weight=4)

        # Left Column Container (60%)
        self.left_col_frame = tk.Frame(content_frame, bg=UI.BG_BASE)
        self.left_col_frame.grid(row=0, column=0, sticky="nsew", padx=(0, UI.SPACE_MD))

        # Right Column Container (40%)
        self.right_col_frame = tk.Frame(content_frame, bg=UI.BG_BASE)
        self.right_col_frame.grid(row=0, column=1, sticky="nsew")

        # Stack panels inside the columns
        from ui.panels.skill_panel import SkillPanel
        self.skill_panel_controller = SkillPanel(self.left_col_frame, self.app, scale_factor, hunt_tab=self)
        # Note: SkillPanel handles its own packing internally in some implementations,
        # but normally it needs to be packed if it's just a frame.
        if isinstance(self.skill_panel_controller, tk.Widget):
            self.skill_panel_controller.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        from ui.panels.target_status_panel import TargetStatusPanel
        self.target_status_panel = TargetStatusPanel(self.right_col_frame, self.app, scale_factor, hunt_tab=self)
        self.target_status_panel.pack(side=tk.TOP, fill=tk.BOTH, pady=(0, UI.SPACE_MD))

        from ui.panels.skill_stats_panel import SkillStatsPanel
        self.skill_stats_panel = SkillStatsPanel(self.right_col_frame, self.app, scale_factor, hunt_tab=self)
        self.skill_stats_panel.pack(side=tk.TOP, fill=tk.BOTH)
