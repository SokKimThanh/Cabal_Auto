import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Dict, Any

from ui.components.base.responsive_grid_base import ResponsiveGridBase
from lib.ui_style_v2 import UIStyleV2 as UIStyle

class SkillManagerFrame(ResponsiveGridBase):
    def __init__(self, parent, app=None, *args, **kwargs):
        super().__init__(parent, app=app, *args, **kwargs)
        self.app = app
        self.skills = []

        self._setup_ui()
        self._load_skills()

    def _setup_ui(self):
        content_frame = self.get_content_frame()

        # Title Label
        title_lbl = tk.Label(
            content_frame,
            text=self.app._t("skill_manager_title", default="Quản lý Kỹ năng"),
            font=(UIStyle.resolve_font_family("title") if hasattr(UIStyle, "resolve_font_family") else "IBM Plex Sans", 16, "bold"),
            bg=UIStyle.THEME_BG_APP,
            fg=UIStyle.THEME_FG_TEXT if hasattr(UIStyle, "THEME_FG_TEXT") else UIStyle.TEXT_PRIMARY
        )
        title_lbl.pack(pady=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8)

        # Treeview Area
        table_frame = tk.Frame(content_frame, bg=UIStyle.THEME_BG_APP)
        table_frame.pack(fill="both", expand=True, padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8, pady=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8)

        self.tree_scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        self.tree_scroll_y.pack(side="right", fill="y")

        self.tree_scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        self.tree_scroll_x.pack(side="bottom", fill="x")

        self.columns = ("ID", "Name", "Category", "Hotkey", "Cooldown", "Priority", "Status")
        self.tree = ttk.Treeview(
            table_frame,
            columns=self.columns,
            show="headings",
            selectmode="browse",
            yscrollcommand=self.tree_scroll_y.set,
            xscrollcommand=self.tree_scroll_x.set
        )

        self.tree_scroll_y.config(command=self.tree.yview)
        self.tree_scroll_x.config(command=self.tree.xview)

        # 7 core columns: ID, Name, Category, Hotkey, Cooldown, Priority, Status
        self.tree.heading("ID", text=self.app._t("col_skill_id", default="ID"))
        self.tree.column("ID", width=70, anchor="center")

        self.tree.heading("Name", text=self.app._t("col_skill_name", default="Name"))
        self.tree.column("Name", width=180, anchor="w")

        self.tree.heading("Category", text=self.app._t("col_skill_category", default="Category"))
        self.tree.column("Category", width=100, anchor="center")

        self.tree.heading("Hotkey", text=self.app._t("col_skill_hotkey", default="Hotkey"))
        self.tree.column("Hotkey", width=80, anchor="center")

        self.tree.heading("Cooldown", text=self.app._t("col_skill_cooldown", default="Cooldown"))
        self.tree.column("Cooldown", width=90, anchor="center")

        self.tree.heading("Priority", text=self.app._t("col_skill_priority", default="Priority"))
        self.tree.column("Priority", width=80, anchor="center")

        self.tree.heading("Status", text=self.app._t("col_skill_status", default="Status"))
        self.tree.column("Status", width=90, anchor="center")

        self.tree.pack(fill="both", expand=True)

        # Bottom Bar for Actions
        bottom_bar = tk.Frame(content_frame, bg=UIStyle.THEME_BG_PANEL, height=50)
        bottom_bar.pack(side="bottom", fill="x", pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

        add_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_add_skill", default=" Thêm"),
            command=self._add_skill,
            bg=UIStyle.ACCENT_GREEN,
            fg="white",
            relief="flat"
        )
        add_btn.pack(side="left", padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8, pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

        edit_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_edit_skill", default=" Sửa"),
            command=self._edit_skill,
            bg=UIStyle.ACCENT_GREEN,
            fg="white",
            relief="flat"
        )
        edit_btn.pack(side="left", padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8, pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

        del_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_del_skill", default=" Xóa"),
            command=self._delete_skill,
            bg=UIStyle.DANGER,
            fg="white",
            relief="flat"
        )
        del_btn.pack(side="left", padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8, pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

        ref_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_refresh_skill", default=" Làm mới"),
            command=self._load_skills,
            bg=UIStyle.BG_ELEVATED,
            fg=UIStyle.TEXT_PRIMARY,
            relief="flat"
        )
        ref_btn.pack(side="right", padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8, pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

    def _load_skills(self):
        try:
            if hasattr(self.app, "skill_service"):
                svc = self.app.skill_service
                if hasattr(svc, "get_skills_by_filter"):
                    self.skills = svc.get_skills_by_filter()
                elif hasattr(svc, "get_all_skills"):
                    self.skills = svc.get_all_skills()
                elif hasattr(svc, "get_skills"):
                    self.skills = svc.get_skills()
                elif hasattr(svc, "skills"):
                    self.skills = svc.skills
                elif hasattr(svc, "_skills"):
                    self.skills = svc._skills
                else:
                    self.skills = []
            else:
                self.skills = []

            if not isinstance(self.skills, list):
                self.skills = []
        except Exception as e:
            self.skills = []
            print(f"Error loading skills: {e}")
        self._refresh_tree()

    def _refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for s in self.skills:
            if isinstance(s, dict):
                s_status = "Active" if s.get("enabled", True) else "Disabled"
                values = (
                    s.get("id", s.get("skill_id", "")),
                    s.get("name", "Unknown"),
                    s.get("category", s.get("type", "")),
                    s.get("hotkey", s.get("key", s.get("slot", ""))),
                    s.get("cooldown", 0),
                    s.get("priority", 0),
                    s_status
                )
                self.tree.insert("", "end", iid=str(s.get("id", s.get("skill_id", str(id(s))))), values=values)

    def _save_skills(self):
        try:
            if hasattr(self.app, "skill_service"):
                svc = self.app.skill_service
                if hasattr(svc, "save_skills"):
                    svc.save_skills(self.skills)
                elif hasattr(svc, "save_skill_library"):
                    svc.save_skill_library(self.skills)
                elif hasattr(svc, "update_skill") or hasattr(svc, "create_skill"):
                    # Individual saves would be handled per row action
                    pass
        except Exception as e:
            messagebox.showerror(
                self.app._t("err_title", default="Lỗi"),
                self.app._t("err_save_skills", default="Không thể lưu danh sách kỹ năng: ") + str(e),
                parent=self
            )

    def _add_skill(self):
        prompt = self.app._t("prompt_add_skill", default="Nhập thông tin (Tên Kỹ Năng, Loại (Attack/Buff), Phím Tắt, Cooldown(s), Priority):")
        result = simpledialog.askstring(
            self.app._t("title_add_skill", default="Thêm Kỹ năng"),
            prompt,
            parent=self
        )
        if result:
            parts = [x.strip() for x in result.split(",")]
            if len(parts) >= 1:
                name = parts[0]
                category = parts[1] if len(parts) > 1 else "Attack"
                hotkey = parts[2] if len(parts) > 2 else ""
                cooldown = float(parts[3]) if len(parts) > 3 else 0.0
                priority = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 1

                # generate id
                max_id = 0
                for s in self.skills:
                    try:
                        s_id = s.get("id", s.get("skill_id", 0))
                        if isinstance(s_id, int):
                            if s_id > max_id:
                                max_id = s_id
                        elif isinstance(s_id, str) and s_id.isdigit():
                            if int(s_id) > max_id:
                                max_id = int(s_id)
                    except ValueError:
                        pass

                new_id = f"S{max_id + 1}"

                new_skill = {
                    "id": new_id,
                    "name": name,
                    "category": category,
                    "type": category,
                    "hotkey": hotkey,
                    "key": hotkey,
                    "cooldown": cooldown,
                    "priority": priority,
                    "enabled": True
                }

                self.skills.append(new_skill)
                # Ensure it saves as dict mapping ID to dict if needed? The normalizer takes list.
                # If skills is stored as a list of dicts, saving it back should work if save_skills takes list.
                self._save_skills()
                self._refresh_tree()

    def _edit_skill(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                self.app._t("warn_title", default="Cảnh báo"),
                self.app._t("warn_no_sel_skill", default="Vui lòng chọn kỹ năng để sửa"),
                parent=self
            )
            return

        s_id = selected[0]
        target_skill = None
        for s in self.skills:
            if str(s.get("id", s.get("skill_id", ""))) == s_id:
                target_skill = s
                break

        if target_skill:
            name = target_skill.get("name", "")
            cat = target_skill.get("category", target_skill.get("type", ""))
            hotkey = target_skill.get("hotkey", target_skill.get("key", ""))
            cd = target_skill.get("cooldown", 0)
            prio = target_skill.get("priority", 0)

            initial = f"{name}, {cat}, {hotkey}, {cd}, {prio}"
            prompt = self.app._t("prompt_edit_skill", default="Sửa thông tin (Tên Kỹ Năng, Loại (Attack/Buff), Phím Tắt, Cooldown(s), Priority):")
            result = simpledialog.askstring(
                self.app._t("title_edit_skill", default="Sửa Kỹ năng"),
                prompt,
                initialvalue=initial,
                parent=self
            )

            if result:
                parts = [x.strip() for x in result.split(",")]
                if len(parts) >= 1:
                    target_skill["name"] = parts[0]
                    target_skill["category"] = parts[1] if len(parts) > 1 else target_skill.get("category", "Attack")
                    target_skill["type"] = target_skill["category"]
                    target_skill["hotkey"] = parts[2] if len(parts) > 2 else target_skill.get("hotkey", "")
                    target_skill["key"] = target_skill["hotkey"]

                    try:
                        target_skill["cooldown"] = float(parts[3]) if len(parts) > 3 else target_skill.get("cooldown", 0.0)
                    except ValueError:
                        pass

                    target_skill["priority"] = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else target_skill.get("priority", 1)

                    self._save_skills()
                    self._refresh_tree()

    def _delete_skill(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                self.app._t("warn_title", default="Cảnh báo"),
                self.app._t("warn_no_sel_skill", default="Vui lòng chọn kỹ năng để xóa"),
                parent=self
            )
            return

        s_id = selected[0]
        target_skill = None
        for s in self.skills:
            if str(s.get("id", s.get("skill_id", ""))) == s_id:
                target_skill = s
                break

        if target_skill:
            name = target_skill.get('name', 'Unknown')
            confirm = messagebox.askyesno(
                self.app._t("confirm_del_title", default="Xác nhận xóa"),
                self.app._t("confirm_del_msg", default=f"Bạn có chắc muốn xóa kỹ năng '{name}' không?"),
                parent=self
            )

            if confirm:
                self.skills.remove(target_skill)
                self._save_skills()
                self._refresh_tree()

    def on_view_shown(self):
        self._load_skills()

    def on_view_hidden(self):
        pass
