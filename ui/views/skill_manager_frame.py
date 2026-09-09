import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Dict, Any

from ui.components.base.responsive_grid_base import ResponsiveGridBase
from lib.ui_style_v2 import UIStyleV2 as UIStyle

class SkillManagerFrame(ResponsiveGridBase):
    def __init__(self, parent, app=None, *args, **kwargs):
        super().__init__(parent, app=app, bg=UIStyle.BG_BASE, *args, **kwargs)
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
            bg=UIStyle.BG_BASE,
            fg=UIStyle.TEXT_PRIMARY
        )
        title_lbl.pack(pady=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8)

        # Treeview Area
        table_frame = tk.Frame(content_frame, bg=UIStyle.BG_BASE)
        table_frame.pack(fill="both", expand=True, padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8, pady=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8)

        self.tree_scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        self.tree_scroll_y.pack(side="right", fill="y")

        self.tree_scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        self.tree_scroll_x.pack(side="bottom", fill="x")

        self.columns = ("ID", "Name", "Type", "Class", "Alias")
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

        # 5 core columns for DB skills: ID, Name, Type, Class, Alias
        self.tree.heading("ID", text=self.app._t("col_skill_id", default="ID"))
        self.tree.column("ID", width=70, anchor="center")

        self.tree.heading("Name", text=self.app._t("col_skill_name", default="Name"))
        self.tree.column("Name", width=180, anchor="w")

        self.tree.heading("Type", text=self.app._t("col_skill_type", default="Type"))
        self.tree.column("Type", width=100, anchor="center")

        self.tree.heading("Class", text=self.app._t("col_skill_class", default="Class ID"))
        self.tree.column("Class", width=80, anchor="center")

        self.tree.heading("Alias", text=self.app._t("col_skill_alias", default="Alias"))
        self.tree.column("Alias", width=120, anchor="w")

        self.tree.pack(fill="both", expand=True)

        # Bottom Bar for Actions
        bottom_bar = tk.Frame(content_frame, bg=UIStyle.BG_SURFACE, height=50)
        bottom_bar.pack(side="bottom", fill="x", pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

        add_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_add_skill", default=" Thêm"),
            command=self._add_skill,
            **UIStyle.get_button_style("primary")
        )
        add_btn.pack(side="left", padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8, pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

        edit_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_edit_skill", default=" Sửa"),
            command=self._edit_skill,
            **UIStyle.get_button_style("primary")
        )
        edit_btn.pack(side="left", padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8, pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

        del_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_del_skill", default=" Xóa"),
            command=self._delete_skill,
            **{**UIStyle.get_button_style("primary"), "bg": UIStyle.DANGER, "activebackground": "#ef4444", "fg": "#ffffff", "activeforeground": "#ffffff"}
        )
        del_btn.pack(side="left", padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8, pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

        ref_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_refresh_skill", default=" Làm mới"),
            command=self._load_skills,
            **UIStyle.get_button_style("secondary")
        )
        ref_btn.pack(side="right", padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8, pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

    def _load_skills(self):
        try:
            if hasattr(self.app, "db_skill_service"):
                svc = self.app.db_skill_service
                self.skills = svc.get_skills_by_filter()
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
                values = (
                    s.get("skill_id", ""),
                    s.get("name", "Unknown"),
                    s.get("type", ""),
                    s.get("class_id", ""),
                    s.get("alias", "")
                )
                self.tree.insert("", "end", iid=str(s.get("skill_id", str(id(s)))), values=values)

    def _add_skill(self):
        from ui.dialogs.skill_edit_dialog import SkillEditDialog

        def _on_save(data: dict):
            if hasattr(self.app, "db_skill_service"):
                svc = self.app.db_skill_service
                success_id = svc.create_skill(data)
                if success_id:
                    messagebox.showinfo(
                        self.app._t("success_title", default="Thành công"),
                        self.app._t("msg_add_skill_success", default="Thêm kỹ năng thành công."),
                        parent=self
                    )
                    self._load_skills()
                else:
                    messagebox.showerror(
                        self.app._t("error_title", default="Lỗi"),
                        self.app._t("err_add_skill", default="Không thể thêm kỹ năng."),
                        parent=self
                    )

        SkillEditDialog(
            parent=self.winfo_toplevel(),
            app=self.app,
            title=self.app._t("title_add_skill", default="Thêm Kỹ năng"),
            skill_data=None,
            on_save=_on_save
        )

    def _edit_skill(self):
        from ui.dialogs.skill_edit_dialog import SkillEditDialog

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
            if str(s.get("skill_id", "")) == s_id:
                target_skill = s
                break

        if target_skill:
            def _on_save(data: dict):
                if hasattr(self.app, "db_skill_service"):
                    svc = self.app.db_skill_service
                    skill_id = data.get("skill_id")
                    if skill_id is None:
                        # Fallback for unexpected missing id
                        return

                    success = svc.update_skill(skill_id, data)
                    if success:
                        messagebox.showinfo(
                            self.app._t("success_title", default="Thành công"),
                            self.app._t("msg_edit_skill_success", default="Cập nhật kỹ năng thành công."),
                            parent=self
                        )
                        self._load_skills()
                    else:
                        messagebox.showerror(
                            self.app._t("error_title", default="Lỗi"),
                            self.app._t("err_edit_skill", default="Không thể cập nhật kỹ năng."),
                            parent=self
                        )

            SkillEditDialog(
                parent=self.winfo_toplevel(),
                app=self.app,
                title=self.app._t("title_edit_skill", default="Sửa Kỹ năng"),
                skill_data=target_skill,
                on_save=_on_save
            )

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
            if str(s.get("skill_id", "")) == s_id:
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
                if hasattr(self.app, "db_skill_service"):
                    svc = self.app.db_skill_service
                    skill_id = target_skill.get("skill_id")
                    if skill_id is not None:
                        success = svc.delete_skill(skill_id)
                        if success:
                            messagebox.showinfo(
                                self.app._t("success_title", default="Thành công"),
                                self.app._t("msg_del_skill_success", default="Xóa kỹ năng thành công."),
                                parent=self
                            )
                            self._load_skills()
                        else:
                            messagebox.showerror(
                                self.app._t("error_title", default="Lỗi"),
                                self.app._t("err_del_skill", default="Không thể xóa kỹ năng."),
                                parent=self
                            )

    def on_view_shown(self):
        self._load_skills()

    def on_view_hidden(self):
        pass
