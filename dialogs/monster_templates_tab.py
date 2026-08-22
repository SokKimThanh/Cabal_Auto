# -*- coding: utf-8 -*-
"""
Monster Templates Tab Component.
Handles template management, list table, preview canvas, and threshold slider.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import time
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

PROJECT_ROOT = Path(__file__).resolve().parent.parent

try:
    from PIL import Image, ImageTk, ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    Image = None
    ImageTk = None
    ImageGrab = None
    PIL_AVAILABLE = False

try:
    from lib.ui_style import UIStyle as UI
except ImportError:
    from mock.fallbacks import UIStyle as UI

try:
    from ui.components import create_icon_label, create_icon_button
    from ui.components.icon_button import create_add_button, create_delete_button, create_refresh_button
except ImportError:
    from mock.fallbacks import create_icon_label, create_icon_button, create_add_button, create_delete_button, create_refresh_button


class MonsterTemplatesTab(tk.Frame):
    """Component hiển thị tab Quản lý Templates."""

    def __init__(self, parent: tk.Widget, monster_data: Dict[str, Any], get_monster_name_func: Callable[[], str]):
        super().__init__(parent, bg=UI.BG_PANEL)
        self.monster_data = monster_data
        self.get_monster_name_func = get_monster_name_func
        self._is_capturing = False
        self._is_browsing = False

        self._setup_ui()
        self.refresh_templates()

    def _setup_ui(self) -> None:
        tmpl_container = tk.Frame(self, bg=UI.BG_PANEL)
        tmpl_container.pack(fill="both", expand=True, padx=10, pady=10)

        left_sub = tk.Frame(tmpl_container, bg=UI.BG_PANEL, width=340)
        left_sub.pack(side="left", fill="both", expand=True, padx=(0, 5))

        right_sub = tk.Frame(tmpl_container, bg=UI.BG_PANEL, width=380)
        right_sub.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # Left Sub-panel
        left_tb = tk.Frame(left_sub, bg=UI.BG_PANEL)
        left_tb.pack(fill="x", pady=(0, 5))

        self.btn_add = create_add_button(
            left_tb, command=self._on_browse, text="Thêm", padding={"padx": 10, "pady": 4}
        )
        self.btn_add.pack(side="left", padx=2)

        self.btn_delete = create_delete_button(
            left_tb, command=self._on_delete_template, text="Xóa", padding={"padx": 10, "pady": 4}
        )
        self.btn_delete.pack(side="left", padx=2)

        self.template_badge = tk.Label(
            left_tb, text="0 tpl", font=UI.FONT_SMALL, fg="white", bg=UI.COLOR_PRIMARY, padx=6, pady=2
        )
        self.template_badge.pack(side="right", padx=2)

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
        self.template_listbox.heading("icon", text="Hình")
        self.template_listbox.heading("threshold", text="Ngưỡng")
        self.template_listbox.heading("path", text="Đường dẫn")

        self.template_listbox.column("icon", width=45, anchor="center", stretch=False)
        self.template_listbox.column("threshold", width=65, anchor="center")
        self.template_listbox.column("path", width=180, anchor="w")

        self.template_listbox.pack(side="left", fill="both", expand=True)
        tree_scroll.config(command=self.template_listbox.yview)
        self.template_listbox.bind("<<TreeviewSelect>>", self._on_template_select)

        # Right Sub-panel
        right_tb = tk.Frame(right_sub, bg=UI.BG_PANEL)
        right_tb.pack(fill="x", pady=(0, 5))

        self.capture_button = create_icon_button(
            right_tb, icon_name="capture", text=None, command=self._on_capture, button_type="blue"
        )
        self.capture_button.pack(side="left", padx=2)

        self.open_folder_button = create_refresh_button(
            right_tb, command=self._on_open_folder, text=None
        )
        self.open_folder_button.pack(side="left", padx=2)

        preview_frame = tk.Frame(right_sub, bg="white", relief="sunken", bd=1)
        preview_frame.pack(fill="both", expand=True, pady=5)

        self.preview_label = tk.Label(
            preview_frame, text="Chưa chọn\ntemplate", font=UI.FONT_SMALL, fg=UI.COLOR_SUBTEXT, bg="white"
        )
        self.preview_label.pack(fill="both", expand=True)

        slider_frame = tk.Frame(right_sub, bg=UI.BG_PANEL)
        slider_frame.pack(fill="x", pady=(5, 0))

        create_icon_label(
            slider_frame, icon_name="settings", text="Ngưỡng:", font=UI.FONT_SMALL, bg=UI.BG_PANEL
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

    def refresh_templates(self) -> None:
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

        self.template_badge.config(text=f"{len(templates)} tpl")

    def _on_template_select(self, event: Any = None) -> None:
        selection = self.template_listbox.selection()
        if not selection:
            self.preview_label.config(text="Chưa chọn\ntemplate", image="")
            self.preview_label.image = None
            return

        idx = int(selection[0].split("_")[-1])
        templates = self.monster_data.get("templates", [])
        if idx >= len(templates):
            self.preview_label.config(text="Chưa chọn\ntemplate", image="")
            self.preview_label.image = None
            return

        tmpl = templates[idx]
        thresh = tmpl.get("threshold", 0.7)
        self.threshold_scale.set(thresh)
        self.threshold_value_label.config(text=f"{thresh:.2f}")

        rel_path = tmpl.get("path", "")
        resolved_path = PROJECT_ROOT / rel_path if rel_path and not Path(rel_path).is_absolute() else Path(rel_path) if rel_path else None

        if resolved_path and resolved_path.exists() and PIL_AVAILABLE and Image and ImageTk:
            try:
                with Image.open(resolved_path) as raw_img:
                    img = raw_img.copy()
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.preview_label.config(image=photo, text="")
                self.preview_label.image = photo
            except Exception:
                self.preview_label.config(text=f"Lỗi ảnh\n{tmpl.get('name')}", image="")
                self.preview_label.image = None
        else:
            self.preview_label.config(text=f"Không tìm thấy\n{tmpl.get('name')}", image="")
            self.preview_label.image = None

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

    def _on_browse(self) -> None:
        if self._is_browsing:
            return
        self._is_browsing = True
        try:
            file_path = filedialog.askopenfilename(
                title="Chọn Ảnh Template",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")],
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
                self.refresh_templates()
        finally:
            self._is_browsing = False

    def _on_capture(self) -> None:
        if self._is_capturing or not PIL_AVAILABLE or ImageGrab is None:
            return
        self._is_capturing = True
        try:
            base = re.sub(r'[<>:"/\\|?*]', "_", self.get_monster_name_func() or "monster")
            ts = int(time.time())
            filename = f"{base}_capture_{ts}.png"
            assets_dir = Path("assets/images/monsters")
            assets_dir.mkdir(parents=True, exist_ok=True)

            tmpl = {
                "name": filename,
                "path": f"assets/images/monsters/{filename}",
                "threshold": 0.85,
            }
            self.monster_data.setdefault("templates", []).append(tmpl)
            self.refresh_templates()
        finally:
            self._is_capturing = False

    def _on_open_folder(self) -> None:
        assets_dir = Path("assets/images/monsters")
        assets_dir.mkdir(parents=True, exist_ok=True)
        try:
            if os.name == "nt":
                os.startfile(str(assets_dir.resolve()))
            elif os.name == "posix":
                subprocess.run(["xdg-open", str(assets_dir.resolve())], check=False)
        except Exception as e:
            messagebox.showinfo("Thư mục Template", str(assets_dir.resolve()), parent=self)

    def _on_delete_template(self) -> None:
        selection = self.template_listbox.selection()
        if not selection:
            return
        idx = int(selection[0].split("_")[-1])
        templates = self.monster_data.get("templates", [])
        if idx < len(templates):
            del templates[idx]
            self.refresh_templates()
