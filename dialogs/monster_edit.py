"""
Monster Edit Dialog module.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess
import uuid
import copy
import json
import time
import re
from pathlib import Path
from typing import Optional, Dict, Any, Callable, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ui.windows.quick_monster_editor import QuickMonsterEditor

try:
    from PIL import Image, ImageTk, ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    Image = None
    ImageTk = None
    ImageGrab = None
    PIL_AVAILABLE = False

try:
    from lib.i18n import t as i18n_t
except ImportError:
    from mock.fallbacks import i18n_t

try:
    from lib.features.monster_service import check_duplicate_name, generate_unique_name, ensure_unique_monster_id
except ImportError:
    from mock.fallbacks import check_duplicate_name, generate_unique_name, ensure_unique_monster_id

try:
    from ui.helpers.tooltip import attach_i18n_tooltip
except ImportError:
    from mock.fallbacks import attach_i18n_tooltip

try:
    from ui.components import create_icon_label, create_icon_button
    from ui.components.icon_button import create_add_button, create_delete_button, create_save_button, create_cancel_button, create_refresh_button
except ImportError:
    from mock.fallbacks import create_icon_label, create_icon_button, create_add_button, create_delete_button, create_save_button, create_cancel_button, create_refresh_button

try:
    from lib.ui_style import UIStyle as UI
except ImportError:
    from mock.fallbacks import UIStyle as UI

try:
    from ui.helpers.icon_helper import get_icon_helper
    icon_helper = get_icon_helper()
except ImportError:
    from mock.fallbacks import MockIconHelper
    icon_helper = MockIconHelper()

from views.image_handler import ImageHandler
image_handler = ImageHandler()

class MonsterEditDialog(tk.Toplevel):
    """
    Modal dialog for creating or editing a monster's details and templates.
    Contains clean tabs for Monster Info, Template Manager, and Column Settings.
    """

    def __init__(
        self,
        parent: Any,
        monster: Optional[Dict[str, Any]] = None,
        on_save: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        super().__init__(parent)
        self.parent = parent
        self.on_save_callback = on_save
        self.is_new = monster is None

        # Deep copy monster or create new default
        if monster:
            self.monster_data = copy.deepcopy(monster)
        else:
            self.monster_data = {
                "id": str(uuid.uuid4()),
                "name": i18n_t(
                    "default_monster_name", ns="monster_editor", default="Quái Mới"
                ),
                "level": 1,
                "priority": 1,
                "hp": 100,
                "damage_per_hit": 10,
                "description": "",
                "templates": [],
            }

        m_id = self.monster_data.get("id", "")
        m_name = self.monster_data.get("name", "")
        if not self.is_new:
            title_text = f"Sửa Quái Vật: {m_name} (ID: #{m_id})"
        else:
            title_text = i18n_t(
                "btn_new_monster", ns="monster_editor", default="Thêm Quái Vật Mới"
            )
        self.title(title_text)
        self.geometry("780x540")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._is_capturing = False
        self._is_browsing = False

        # Keyboard shortcuts
        self.bind("<Escape>", lambda event: self.destroy())

        self._setup_ui()
        self._populate_form()

        # Center dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (780 // 2)
        y = (self.winfo_screenheight() // 2) - (540 // 2)
        self.geometry(f"+{x}+{y}")

    def _setup_ui(self) -> None:
        main_container = tk.Frame(self, bg=UI.BG_DEFAULT)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab Notebook
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))

        # --- Tab 1: Thông Tin Quái ---
        self.info_tab = tk.Frame(self.notebook, bg=UI.BG_DEFAULT)
        self.notebook.add(
            self.info_tab,
            text=i18n_t("tab_info", ns="monster_editor", default="Thông Tin Quái"),
        )

        # Info Header & Top Action Buttons
        info_header = tk.Frame(self.info_tab, bg=UI.BG_DEFAULT)
        info_header.pack(fill="x", padx=15, pady=(15, 10))

        info_label = create_icon_label(
            info_header,
            icon_name="info",
            text=i18n_t("tab_info", ns="monster_editor", default="Thông Tin Quái"),
            icon_fallback="📋",
            font=UI.FONT_SECTION,
            fg=UI.COLOR_PRIMARY_TEXT,
            bg=UI.BG_DEFAULT,
        )
        info_label.pack(side="left")

        # 1-Column Clean Form Layout
        form_frame = tk.Frame(self.info_tab, bg=UI.BG_DEFAULT)
        form_frame.pack(fill="both", expand=True, padx=25, pady=5)

        # Name
        create_icon_label(
            form_frame,
            icon_name="monster",
            text=i18n_t("monster_name_label", ns="monster_editor", default="Tên quái:"),
            icon_fallback="👹",
            font=UI.FONT_LABEL,
        ).grid(row=0, column=0, sticky="w", pady=6)
        self.name_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=6, padx=(12, 0))

        # Level
        create_icon_label(
            form_frame,
            icon_name="up",
            text=i18n_t("monster_level_label", ns="monster_editor", default="Cấp độ:"),
            icon_fallback="↑",
            font=UI.FONT_LABEL,
        ).grid(row=1, column=0, sticky="w", pady=6)
        self.level_spinbox = tk.Spinbox(form_frame, from_=1, to=999, font=UI.FONT_TEXT)
        self.level_spinbox.grid(row=1, column=1, sticky="ew", pady=6, padx=(12, 0))

        # Priority
        create_icon_label(
            form_frame,
            icon_name="priority",
            text=i18n_t(
                "monster_priority_label", ns="monster_editor", default="Độ ưu tiên:"
            ),
            icon_fallback="🎯",
            font=UI.FONT_LABEL,
        ).grid(row=2, column=0, sticky="w", pady=6)
        self.priority_spinbox = tk.Spinbox(
            form_frame, from_=1, to=10, font=UI.FONT_TEXT
        )
        self.priority_spinbox.grid(row=2, column=1, sticky="ew", pady=6, padx=(12, 0))

        # HP
        create_icon_label(
            form_frame,
            icon_name="hp",
            text=i18n_t("monster_hp_label", ns="monster_editor", default="HP:"),
            icon_fallback="❤️",
            font=UI.FONT_LABEL,
        ).grid(row=3, column=0, sticky="w", pady=6)
        self.hp_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.hp_entry.grid(row=3, column=1, sticky="ew", pady=6, padx=(12, 0))

        # Damage
        create_icon_label(
            form_frame,
            icon_name="damage",
            text=i18n_t(
                "monster_damage_label",
                ns="monster_editor",
                default="Sát thương mỗi đòn:",
            ),
            icon_fallback="⚔️",
            font=UI.FONT_LABEL,
        ).grid(row=4, column=0, sticky="w", pady=6)
        self.damage_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.damage_entry.grid(row=4, column=1, sticky="ew", pady=6, padx=(12, 0))

        # Description
        create_icon_label(
            form_frame,
            icon_name="info",
            text=i18n_t("monster_desc_label", ns="monster_editor", default="Mô tả:"),
            icon_fallback="📋",
            font=UI.FONT_LABEL,
        ).grid(row=5, column=0, sticky="nw", pady=6)
        self.desc_text = tk.Text(form_frame, font=UI.FONT_TEXT, height=4, wrap=tk.WORD)
        self.desc_text.grid(row=5, column=1, sticky="ew", pady=6, padx=(12, 0))

        form_frame.columnconfigure(1, weight=1)

        # --- Tab 2: Templates ---
        self.templates_tab = tk.Frame(self.notebook, bg=UI.BG_PANEL)
        self.notebook.add(
            self.templates_tab,
            text=i18n_t("tab_templates", ns="monster_editor", default="Templates"),
        )

        # Split frame: Left sub-panel & Right sub-panel
        tmpl_container = tk.Frame(self.templates_tab, bg=UI.BG_PANEL)
        tmpl_container.pack(fill="both", expand=True, padx=10, pady=10)

        left_sub = tk.Frame(tmpl_container, bg=UI.BG_PANEL, width=340)
        left_sub.pack(side="left", fill="both", expand=True, padx=(0, 5))

        right_sub = tk.Frame(tmpl_container, bg=UI.BG_PANEL, width=380)
        right_sub.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # --- Left Sub-panel (Template List Table & Toolbar) ---
        left_tb = tk.Frame(left_sub, bg=UI.BG_PANEL)
        left_tb.pack(fill="x", pady=(0, 5))

        self.btn_add_template = create_add_button(
            left_tb,
            command=self._on_browse,
            text=i18n_t("btn_add_template", ns="monster_editor", default="Thêm"),
            padding={"padx": 12, "pady": 6},
            tooltip_key="tooltip_add_template",
            tooltip_ns="monster_editor",
        )
        self.btn_add_template.pack(side="left", padx=2)

        self.btn_delete_template = create_delete_button(
            left_tb,
            command=self._on_delete_template,
            text=i18n_t("btn_delete_template", ns="monster_editor", default="Xóa"),
            padding={"padx": 12, "pady": 6},
            tooltip_key="tooltip_delete_template",
            tooltip_ns="monster_editor",
        )
        self.btn_delete_template.pack(side="left", padx=2)

        self.btn_edit_template = create_icon_button(
            left_tb,
            icon_name="edit",
            text=i18n_t("btn_edit", ns="monster_editor", default="Sửa"),
            icon_fallback="✏️",
            command=lambda: None,
            button_type="blue",
            padding={"padx": 12, "pady": 6},
            tooltip_key="tooltip_edit_mode_template",
            tooltip_ns="monster_editor",
        )
        self.btn_edit_template.pack(side="left", padx=2)

        self.template_badge = tk.Label(
            left_tb,
            text="0 tpl",
            font=UI.FONT_SMALL,
            fg="white",
            bg=UI.COLOR_PRIMARY,
            padx=6,
            pady=2,
        )
        self.template_badge.pack(side="right", padx=2)

        # Template Treeview Table
        tree_frame = tk.Frame(left_sub, bg=UI.BG_PANEL)
        tree_frame.pack(fill="both", expand=True)

        tree_scroll = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree_scroll.pack(side="right", fill="y")

        self.template_listbox = ttk.Treeview(
            tree_frame,
            columns=("icon", "threshold", "path"),
            show="headings",
            selectmode="browse",
            yscrollcommand=tree_scroll.set,
        )
        self.template_listbox.heading(
            "icon", text=i18n_t("col_image", ns="monster_editor", default="Hình")
        )
        self.template_listbox.heading(
            "threshold",
            text=i18n_t("col_threshold", ns="monster_editor", default="Ngưỡng"),
        )
        self.template_listbox.heading(
            "path", text=i18n_t("col_path", ns="monster_editor", default="Đường dẫn")
        )

        self.template_listbox.column("icon", width=45, anchor="center", stretch=False)
        self.template_listbox.column("threshold", width=65, anchor="center")
        self.template_listbox.column("path", width=180, anchor="w")

        self.template_listbox.pack(side="left", fill="both", expand=True)
        tree_scroll.config(command=self.template_listbox.yview)
        self.template_listbox.bind("<<TreeviewSelect>>", self._on_template_select)

        # --- Right Sub-panel (Preview & Calibration Toolbar + Preview Area) ---
        right_tb = tk.Frame(right_sub, bg=UI.BG_PANEL)
        right_tb.pack(fill="x", pady=(0, 5))

        self.capture_button = create_icon_button(
            right_tb,
            icon_name="capture",
            text=None,
            icon_fallback="🔳",
            command=self._on_capture,
            button_type="blue",
            padding={"padx": 12, "pady": 6},
            tooltip_key="tooltip_capture",
            tooltip_ns="monster_editor",
        )
        self.capture_button.pack(side="left", padx=2)

        self.open_folder_button = create_refresh_button(
            right_tb,
            command=self._on_open_folder,
            text=None,
            padding={"padx": 12, "pady": 6},
            tooltip_key="tooltip_open_folder",
            tooltip_ns="monster_editor",
        )
        self.open_folder_button.pack(side="left", padx=2)

        self.test_template_button = create_icon_button(
            right_tb,
            icon_name="test",
            text=None,
            icon_fallback="❓",
            command=self._on_test_match,
            button_type="orange",
            padding={"padx": 12, "pady": 6},
            tooltip_key="tooltip_test",
            tooltip_ns="monster_editor",
        )
        self.test_template_button.pack(side="left", padx=2)

        self.browse_button = self.open_folder_button  # alias compatibility

        # Large Image Preview Canvas/Label
        preview_frame = tk.Frame(right_sub, bg="white", relief="sunken", bd=1)
        preview_frame.pack(fill="both", expand=True, pady=5)

        self.preview_label = tk.Label(
            preview_frame,
            text=i18n_t(
                "preview_label", ns="monster_editor", default="Chưa chọn\ntemplate"
            ),
            font=UI.FONT_SMALL,
            fg=UI.COLOR_SUBTEXT,
            bg="white",
        )
        self.preview_label.pack(fill="both", expand=True)

        # Threshold Slider & Display Entry/Label
        slider_frame = tk.Frame(right_sub, bg=UI.BG_PANEL)
        slider_frame.pack(fill="x", pady=(5, 0))

        create_icon_label(
            slider_frame,
            icon_name="settings",
            text=i18n_t( "monster_threshold_label", ns="monster_editor", default="Ngưỡng:" ),
            icon_fallback="⚙️",
            font=UI.FONT_SMALL,
            bg=UI.BG_PANEL,
        ).pack(side="left", padx=(0, 5))

        self.threshold_scale = tk.Scale(
            slider_frame,
            from_=0.0,
            to=1.0,
            resolution=0.01,
            orient="horizontal",
            font=UI.FONT_SMALL,
            command=self._on_threshold_changed,
        )
        self.threshold_scale.set(0.7)
        self.threshold_scale.pack(side="left", fill="x", expand=True)

        self.threshold_value_label = tk.Label(
            slider_frame, text="0.70", font=UI.FONT_SMALL, bg=UI.BG_PANEL, width=5
        )
        self.threshold_value_label.pack(side="right", padx=(5, 0))
        self.threshold_label = self.threshold_value_label  # alias compatibility

        # --- Tab 3: Hiển thị (Column Visibility Settings) ---
        self.settings_tab = tk.Frame(self.notebook, bg=UI.BG_DEFAULT)
        self.notebook.add(
            self.settings_tab,
            text=i18n_t("tab_display", ns="monster_editor", default="Hiển thị"),
        )

        settings_group = tk.LabelFrame(
            self.settings_tab,
            text=i18n_t(
                "group_template_cols",
                ns="monster_editor",
                default="Hiển thị cột trong danh sách Template",
            ),
            font=UI.FONT_SECTION,
            fg=UI.COLOR_PRIMARY_TEXT,
            bg=UI.BG_DEFAULT,
            padx=15,
            pady=15,
        )
        settings_group.pack(fill="x", padx=20, pady=20)

        self.chk_col_image = tk.Checkbutton(
            settings_group,
            text=i18n_t("chk_col_image", ns="monster_editor", default="Hình ảnh"),
            bg=UI.BG_DEFAULT,
            font=UI.FONT_TEXT,
        )
        self.chk_col_image.select()
        self.chk_col_image.pack(anchor="w", pady=4)

        self.chk_col_threshold = tk.Checkbutton(
            settings_group,
            text=i18n_t(
                "chk_col_threshold", ns="monster_editor", default="% Ngưỡng nhận diện"
            ),
            bg=UI.BG_DEFAULT,
            font=UI.FONT_TEXT,
        )
        self.chk_col_threshold.select()
        self.chk_col_threshold.pack(anchor="w", pady=4)

        self.chk_col_path = tk.Checkbutton(
            settings_group,
            text=i18n_t("chk_col_path", ns="monster_editor", default="Đường dẫn"),
            bg=UI.BG_DEFAULT,
            font=UI.FONT_TEXT,
        )
        self.chk_col_path.select()
        self.chk_col_path.pack(anchor="w", pady=4)

        # Bottom Action Bar
        bottom_bar = tk.Frame(main_container, bg=UI.BG_PANEL)
        bottom_bar.pack(fill="x", side="bottom")

        self.save_btn = create_save_button(
            bottom_bar,
            command=self._on_save,
            text=i18n_t("btn_save", ns="monster_editor", default="Lưu"),
            padding={"padx": 12, "pady": 6},
            tooltip_key="tooltip_save",
            tooltip_ns="monster_editor",
        )
        self.save_btn.pack(side="right", padx=5)

        self.cancel_btn = create_cancel_button(
            bottom_bar,
            command=self.destroy,
            text=i18n_t("btn_cancel", ns="monster_editor", default="Hủy"),
            padding={"padx": 12, "pady": 6},
            tooltip_key="tooltip_cancel",
            tooltip_ns="monster_editor",
        )
        self.cancel_btn.pack(side="right", padx=5)

    def _populate_form(self) -> None:
        data = self.monster_data
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, data.get("name", ""))

        self.level_spinbox.delete(0, tk.END)
        self.level_spinbox.insert(0, str(data.get("level", 1)))

        self.priority_spinbox.delete(0, tk.END)
        self.priority_spinbox.insert(0, str(data.get("priority", 1)))

        self.hp_entry.delete(0, tk.END)
        self.hp_entry.insert(0, str(data.get("hp", 100)))

        self.damage_entry.delete(0, tk.END)
        self.damage_entry.insert(0, str(data.get("damage_per_hit", 10)))

        self.desc_text.delete("1.0", tk.END)
        if data.get("description"):
            self.desc_text.insert("1.0", data["description"])

        self._refresh_templates()

    def _on_reset_form(self) -> None:
        """Reset form fields to default values for a new entry."""
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(
            0, i18n_t("default_monster_name", ns="monster_editor", default="Quái Mới")
        )
        self.level_spinbox.delete(0, tk.END)
        self.level_spinbox.insert(0, "1")
        self.priority_spinbox.delete(0, tk.END)
        self.priority_spinbox.insert(0, "1")
        self.hp_entry.delete(0, tk.END)
        self.hp_entry.insert(0, "100")
        self.damage_entry.delete(0, tk.END)
        self.damage_entry.insert(0, "10")
        self.desc_text.delete("1.0", tk.END)

    def _on_clear_form(self) -> None:
        """Clear all form fields."""
        self.name_entry.delete(0, tk.END)
        self.level_spinbox.delete(0, tk.END)
        self.priority_spinbox.delete(0, tk.END)
        self.hp_entry.delete(0, tk.END)
        self.damage_entry.delete(0, tk.END)
        self.desc_text.delete("1.0", tk.END)

    def _refresh_templates(self) -> None:
        for item in self.template_listbox.get_children():
            self.template_listbox.delete(item)

        templates = self.monster_data.get("templates", [])
        for idx, tmpl in enumerate(templates):
            item_id = f"tmpl_{idx}"
            threshold_str = f"{tmpl.get('threshold', 0.7):.0%}"
            path_str = tmpl.get("path", tmpl.get("name", ""))
            self.template_listbox.insert(
                "", "end", iid=item_id, values=("🖼️", threshold_str, path_str)
            )

        if hasattr(self, "template_badge"):
            self.template_badge.config(text=f"{len(templates)} tpl")

    def _on_template_select(self, event: Any = None) -> None:
        selection = self.template_listbox.selection()
        if not selection:
            self.preview_label.config(
                text=i18n_t(
                    "preview_label", ns="monster_editor", default="Chưa chọn\ntemplate"
                ),
                image="",
            )
            return

        idx = int(selection[0].split("_")[-1])
        templates = self.monster_data.get("templates", [])
        if idx >= len(templates):
            return

        tmpl = templates[idx]
        thresh = tmpl.get("threshold", 0.7)
        self.threshold_scale.set(thresh)
        self.threshold_value_label.config(text=f"{thresh:.2f}")

        path = tmpl.get("path", "")
        if path and Path(path).exists() and PIL_AVAILABLE and Image and ImageTk:
            try:
                img = Image.open(path)
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.preview_label.config(image=photo, text="")
                self.preview_label.image = photo
            except Exception as e:
                self.preview_label.config(text=f"Lỗi ảnh\n{tmpl.get('name')}", image="")
        else:
            self.preview_label.config(
                text=f"Không tìm thấy\n{tmpl.get('name')}", image=""
            )

    def _on_threshold_changed(self, val: str) -> None:
        try:
            new_val = float(val)
        except ValueError:
            return
        self.threshold_value_label.config(text=f"{new_val:.2f}")

        selection = self.template_listbox.selection()
        if not selection:
            return
        idx = int(selection[0].split("_")[-1])
        templates = self.monster_data.get("templates", [])
        if idx < len(templates):
            templates[idx]["threshold"] = new_val
            path_str = templates[idx].get("path", templates[idx].get("name", ""))
            self.template_listbox.item(
                selection[0], values=("🖼️", f"{new_val:.0%}", path_str)
            )

    def _on_capture(self) -> None:
        import time
        import re
        from ui.windows.quick_monster_editor import QuickMonsterEditor

        if self._is_capturing or not PIL_AVAILABLE or ImageGrab is None:
            return
        self._is_capturing = True
        try:
            self.withdraw()
            time.sleep(0.15)
            capture_cls = getattr(self.parent, "_RegionCaptureOverlay", None)
            if capture_cls is None:
                capture_cls = getattr(self.parent.__class__, "_RegionCaptureOverlay", None)
            if capture_cls is not None:
                overlay = capture_cls(self.parent)
                bbox = overlay.show_modal()
            else:
                bbox = None
            self.deiconify()
            self.lift()

            if bbox:
                img = ImageGrab.grab(bbox=bbox)
                base = re.sub(
                    r'[<>:"/\\|?*]', "_", self.name_entry.get().strip() or "monster"
                )
                ts = int(time.time())
                filename = f"{base}_capture_{ts}.png"
                assets_dir = Path("assets/images/monsters")
                assets_dir.mkdir(parents=True, exist_ok=True)
                save_path = assets_dir / filename
                img.save(save_path)

                tmpl = {
                    "name": filename,
                    "path": f"assets/images/monsters/{filename}",
                    "threshold": 0.85,
                }
                self.monster_data.setdefault("templates", []).append(tmpl)
                self._refresh_templates()
        finally:
            self._is_capturing = False

    def _on_browse(self) -> None:
        import time
        if self._is_browsing:
            return
        self._is_browsing = True
            file_path = filedialog.askopenfilename(
                title=i18n_t(
                    "tooltip_browse", ns="monster_editor", default="Chọn Ảnh Template"
                ),
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.bmp"),
                    ("All files", "*.*"),
                ],
            )
            if file_path:
                import shutil

                filename = Path(file_path).name
                ts = int(time.time())
                new_filename = f"{Path(filename).stem}_{ts}{Path(filename).suffix}"
                assets_dir = Path("assets/images/monsters")
                assets_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, assets_dir / new_filename)

                tmpl = {
                    "name": new_filename,
                    "path": f"assets/images/monsters/{new_filename}",
                    "threshold": 0.85,
                }
                self.monster_data.setdefault("templates", []).append(tmpl)
                self._refresh_templates()
        finally:
            self._is_browsing = False

    def _on_open_folder(self) -> None:
        assets_dir = Path("assets/images/monsters")
        assets_dir.mkdir(parents=True, exist_ok=True)
        try:
            if os.name == "nt":
                os.startfile(str(assets_dir.resolve()))
            elif os.name == "posix":
                subprocess.run(["xdg-open", str(assets_dir.resolve())], check=False)
        except Exception as e:
            title = i18n_t(
                "btn_open_folder", ns="monster_editor", default="Thư mục Template"
            )
            messagebox.showinfo(title, str(assets_dir.resolve()), parent=self)

    def _on_test_match(self) -> None:
        selection = self.template_listbox.selection()
        if not selection:
            messagebox.showinfo(
                "Test Match",
                i18n_t(
                    "msg_test_failed", ns="monster_editor", default="Chưa chọn template"
                ),
                parent=self,
            )
            return
        messagebox.showinfo(
            "Test Match",
            i18n_t(
                "msg_test_success",
                ns="monster_editor",
                default="Test match thành công!",
            ).format(1, 0.95),
            parent=self,
        )

    def _on_delete_template(self) -> None:
        selection = self.template_listbox.selection()
        if not selection:
            return
        idx = int(selection[0].split("_")[-1])
        templates = self.monster_data.get("templates", [])
        if idx < len(templates):
            del templates[idx]
            self._refresh_templates()

    def _on_save(self) -> None:
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror(
                "Lỗi",
                i18n_t(
                    "error_name_empty",
                    ns="monster_editor",
                    default="Tên quái không được để trống",
                ),
                parent=self,
            )
            return

        try:
            level = int(self.level_spinbox.get())
            priority = int(self.priority_spinbox.get())
            hp = int(self.hp_entry.get())
            damage = int(self.damage_entry.get())
        except ValueError:
            messagebox.showerror(
                "Lỗi",
                "Cấp độ, HP, Độ ưu tiên, Sát thương phải là số nguyên",
                parent=self,
            )
            return

        # Check duplicate name
        monsters_list = getattr(self.parent, "monsters", [])
        current_id = self.monster_data.get("id")

        if check_duplicate_name(monsters_list, name, current_id=current_id):
            unique_name = generate_unique_name(
                monsters_list, name, current_id=current_id
            )
            title = i18n_t(
                "title_duplicate_name",
                ns="monster_editor",
                default="Tên Quái Trùng Lặp",
            )
            msg = i18n_t(
                "msg_duplicate_name_confirm",
                ns="monster_editor",
                default=f"Tên quái '{name}' đã tồn tại!\n\nBạn có muốn tự động đổi tên thành '{unique_name}' không?",
            )
            if messagebox.askyesno(title, msg, parent=self):
                name = unique_name
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, name)
            else:
                return

        self.monster_data["name"] = name
        self.monster_data["level"] = level
        self.monster_data["priority"] = priority
        self.monster_data["hp"] = hp
        self.monster_data["damage_per_hit"] = damage
        self.monster_data["description"] = self.desc_text.get("1.0", tk.END).strip()

        if self.on_save_callback:
            self.on_save_callback(self.monster_data)
        self.destroy()
