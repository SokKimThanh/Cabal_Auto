"""
Display Settings Dialog module.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ui.windows.quick_monster_editor import QuickMonsterEditor

try:
    from lib.i18n import t as i18n_t
except ImportError:
    from mock.fallbacks import i18n_t

try:
    from ui.components import create_icon_label
    from ui.components.icon_button import create_save_button, create_cancel_button
except ImportError:
    from mock.fallbacks import create_icon_label, create_save_button, create_cancel_button

try:
    from lib.ui_style import UIStyle as UI
except ImportError:
    from mock.fallbacks import UIStyle as UI

class DisplaySettingsDialog(tk.Toplevel):
    """Standalone settings dialog for window modes and column visibility."""

    def __init__(self, parent: QuickMonsterEditor):
        super().__init__(parent)
        self.parent = parent
        title = i18n_t(
            "settings_dialog_title", ns="monster_editor", default="Cài Đặt Hiển Thị"
        )
        self.title(title)
        self.geometry("380x300")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._setup_ui()

        # Keyboard shortcuts
        self.bind("<Escape>", lambda event: self.destroy())
        self.bind("<Return>", lambda event: self._on_save())

        # Center
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (380 // 2)
        y = (self.winfo_screenheight() // 2) - (300 // 2)
        self.geometry(f"+{x}+{y}")

    def _setup_ui(self) -> None:
        main_frame = tk.Frame(self, bg=UI.BG_PANEL, padx=15, pady=15)
        main_frame.pack(fill="both", expand=True)

        header = create_icon_label(
            main_frame,
            icon_name="settings",
            text=i18n_t(
                "settings_dialog_title", ns="monster_editor", default="Cài Đặt Hiển Thị"
            ),
            icon_fallback="⚙️",
            font=UI.FONT_SECTION,
            fg=UI.COLOR_PRIMARY_TEXT,
            bg=UI.BG_PANEL,
        )
        header.pack(anchor="w", pady=(0, 15))

        # Game Window Mode Group
        mode_frame = tk.LabelFrame(
            main_frame,
            text=i18n_t(
                "label_game_mode", ns="monster_editor", default="Game Window Mode"
            ),
            font=UI.FONT_LABEL,
            bg=UI.BG_PANEL,
            padx=10,
            pady=10,
        )
        mode_frame.pack(fill="x", pady=(0, 10))

        self.mode_var = tk.StringVar(value=self.parent.game_window_mode_var.get())
        cb = ttk.Combobox(
            mode_frame,
            textvariable=self.mode_var,
            values=["none", "below", "above"],
            state="readonly",
        )
        cb.pack(fill="x", pady=5)

        # Template Column Visibility Group
        cols_frame = tk.LabelFrame(
            main_frame,
            text=i18n_t(
                "group_template_cols",
                ns="monster_editor",
                default="Hiển thị cột trong danh sách Template",
            ),
            font=UI.FONT_LABEL,
            bg=UI.BG_PANEL,
            padx=10,
            pady=10,
        )
        cols_frame.pack(fill="x", pady=(0, 15))

        self.chk_image_var = tk.BooleanVar(
            value=self.parent.template_col_visibility.get("image", True)
        )
        self.chk_threshold_var = tk.BooleanVar(
            value=self.parent.template_col_visibility.get("threshold", True)
        )
        self.chk_path_var = tk.BooleanVar(
            value=self.parent.template_col_visibility.get("path", True)
        )

        chk_img = tk.Checkbutton(
            cols_frame,
            text=i18n_t("chk_col_image", ns="monster_editor", default="Hình ảnh"),
            variable=self.chk_image_var,
            bg=UI.BG_PANEL,
            font=UI.FONT_TEXT,
        )
        chk_img.pack(anchor="w", pady=2)

        chk_thresh = tk.Checkbutton(
            cols_frame,
            text=i18n_t(
                "chk_col_threshold", ns="monster_editor", default="% Ngưỡng nhận diện"
            ),
            variable=self.chk_threshold_var,
            bg=UI.BG_PANEL,
            font=UI.FONT_TEXT,
        )
        chk_thresh.pack(anchor="w", pady=2)

        chk_path = tk.Checkbutton(
            cols_frame,
            text=i18n_t("chk_col_path", ns="monster_editor", default="Đường dẫn"),
            variable=self.chk_path_var,
            bg=UI.BG_PANEL,
            font=UI.FONT_TEXT,
        )
        chk_path.pack(anchor="w", pady=2)

        # Bottom Buttons
        btn_box = tk.Frame(main_frame, bg=UI.BG_PANEL)
        btn_box.pack(fill="x", side="bottom")

        save_btn = create_save_button(
            btn_box,
            command=self._on_save,
            text=i18n_t("btn_save", ns="monster_editor", default="Lưu"),
            padding={"padx": 12, "pady": 6},
            tooltip_key="tooltip_save",
            tooltip_ns="monster_editor",
        )
        save_btn.pack(side="right", padx=5)

        cancel_btn = create_cancel_button(
            btn_box,
            command=self.destroy,
            text=i18n_t("btn_cancel", ns="monster_editor", default="Hủy"),
            padding={"padx": 12, "pady": 6},
            tooltip_key="tooltip_cancel",
            tooltip_ns="monster_editor",
        )
        cancel_btn.pack(side="right", padx=5)

    def _on_save(self) -> None:
        self.parent.game_window_mode_var.set(self.mode_var.get())
        self.parent.template_col_visibility["image"] = self.chk_image_var.get()
        self.parent.template_col_visibility["threshold"] = self.chk_threshold_var.get()
        self.parent.template_col_visibility["path"] = self.chk_path_var.get()
        self.parent._show_status_message(
            i18n_t(
                "msg_save_success",
                ns="monster_editor",
                default="Đã lưu cài đặt hiển thị",
            )
        )
        self.destroy()
