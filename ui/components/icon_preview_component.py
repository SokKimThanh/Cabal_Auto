import tkinter as tk
from pathlib import Path
from lib.ui_style_v2 import UIStyleV2 as UIStyle
from ui.components.empty_state import EmptyState
from lib.managers.icon_file_manager import get_icons_directory
from ui.helpers.tooltip import attach_i18n_tooltip
from PIL import Image, ImageTk
import logging

class IconPreviewComponent(tk.Frame):
    def __init__(self, parent, app, icon_helper, **kwargs):
        super().__init__(parent, bg=UIStyle.BG_SURFACE, **kwargs)
        self.app = app
        self.icon_helper = icon_helper

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_propagate(False)
        self.config(height=200)

        self._build_ui()

    def i18n_t(self, key, default=""):
        if hasattr(self.app, 't'):
            return self.app.t(key, default=default)
        return default

    def _build_ui(self):
        # Empty State
        self.empty_preview = EmptyState(
            self,
            icon="🖼️",
            message=self.i18n_t("msg_no_icon_selected", default="Chưa chọn icon nào hoặc dữ liệu trống"),
            submessage=self.i18n_t("msg_no_icon_sub", default="Vui lòng chọn icon từ danh sách hoặc nhấn Đồng bộ nếu danh sách trống")
        )
        self.empty_preview.grid(row=0, column=0, sticky="nsew")

        # Preview Label (Hidden by default)
        self.lbl_preview = tk.Label(
            self,
            bg=UIStyle.BG_ELEVATED,
            text="",
            font=UIStyle.get_font("body"),
            relief="groove"
        )

    def render(self, icon_data):
        if not icon_data:
            self.empty_preview.tkraise()
            self.lbl_preview.grid_remove()
            self.lbl_preview.config(image='', text="")
            self.lbl_preview.image = None
            return

        self.lbl_preview.tkraise()
        self.lbl_preview.grid(row=0, column=0, padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_MD, sticky="nsew")

        icon_key = icon_data.get("icon_key", "")
        fallback_emoji = icon_data.get("fallback_emoji", "")
        filepath = icon_data.get("filepath", "")
        tooltip_key = icon_data.get("tooltip_translation_key", "")

        # Kiểm tra trạng thái tồn tại của file
        status = self.icon_helper.evaluate_icon_status({"filepath": filepath, "fallback_emoji": fallback_emoji})

        giant_icon = None
        # Chỉ load ảnh nếu status là GREEN (ảnh tồn tại)
        if status == "GREEN" and filepath:
            try:
                target_path = Path(filepath)
                if not target_path.is_absolute():
                    target_path = get_icons_directory() / filepath

                if target_path.exists():
                    img = Image.open(target_path)
                    img = img.resize((128, 128), Image.Resampling.LANCZOS)
                    giant_icon = ImageTk.PhotoImage(img)
            except Exception as e:
                logging.getLogger(__name__).warning(f"Preview load failed: {e}")

        if giant_icon is None:
            giant_icon = fallback_emoji or "❓"

        if giant_icon and not isinstance(giant_icon, str):
            self.lbl_preview.config(image=giant_icon, text="")
            self.lbl_preview.image = giant_icon # keep a reference!
        else:
            self.lbl_preview.config(image='', text=giant_icon, font=("Segoe UI Emoji", 48))
            self.lbl_preview.image = None

        # Tooltip handling
        if hasattr(self.lbl_preview, "_i18n_tooltip") and getattr(self.lbl_preview, "_i18n_tooltip"):
            old_tip = getattr(self.lbl_preview, "_i18n_tooltip")
            if hasattr(old_tip, "_hide"):
                old_tip._hide()
            self.lbl_preview.unbind("<Enter>")
            self.lbl_preview.unbind("<Leave>")
            self.lbl_preview.unbind("<ButtonPress>")

        if tooltip_key:
            attach_i18n_tooltip(
                self.lbl_preview,
                key=tooltip_key,
                ns=None,
                lang_provider=lambda: getattr(self.app, 'lang', 'vi') if self.app else 'vi'
            )
        else:
            setattr(self.lbl_preview, "_i18n_tooltip", None)
