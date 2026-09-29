"""Skill picker dialog — FIX BUG #6.

Cấu trúc tương tự MonsterPickerDialog nhưng cho skill.
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Any, List, Optional
from lib.ui_style_v2 import UIStyleV2 as UI


class SkillPickerDialog(tk.Toplevel):
    def __init__(
        self,
        parent,
        skills: List[Dict[str, Any]],
        on_select: Callable[[Dict[str, Any]], None],
        t_func: Callable,
        excluded_skill_ids: Optional[set] = None,
    ):
        super().__init__(parent)
        self.parent = parent
        self.all_skills = skills
        self.on_select = on_select
        self._t = t_func
        self.excluded = excluded_skill_ids or set()
        self.show_all = tk.BooleanVar(value=False)

        self.title(self._t("skill_picker.title", default="Chọn kỹ năng"))
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.bind("<Escape>", lambda e: self._on_cancel())

        self._setup_ui()
        self._render_results(self.all_skills)

    def _setup_ui(self):
        main = tk.Frame(self, padx=16, pady=16)
        main.pack(fill="both", expand=True)

        # Header
        tk.Label(
            main,
            text=self._t("skill_picker.instruction", default="Chọn kỹ năng để thêm vào lane"),
            font=UI.FONT_LABEL, fg=UI.TEXT_PRIMARY, anchor="w",
        ).pack(fill="x", pady=(0, 8))

        # Search
        search_frame = tk.Frame(main)
        search_frame.pack(fill="x", pady=(0, 8))
        tk.Label(search_frame, text=self._t("skill_picker.search", default="Tìm:"),
                 font=UI.FONT_LABEL, fg=UI.TEXT_PRIMARY).pack(side="left", padx=(0, 8))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._filter_results())
        tk.Entry(search_frame, textvariable=self.search_var, font=UI.FONT_TEXT).pack(
            side="left", fill="x", expand=True
        )

        # Show all checkbox
        tk.Checkbutton(
            main,
            text=self._t("skill_picker.show_all", default="Hiển thị tất cả skill (bỏ lọc class)"),
            variable=self.show_all,
            command=self._filter_results,
            font=UI.FONT_TEXT,
        ).pack(anchor="w", pady=(0, 4))

        # Treeview
        tree_frame = tk.LabelFrame(main, text=self._t("skill_picker.results", default="Kết quả"),
                                    font=UI.FONT_LABEL, padx=8, pady=8)
        tree_frame.pack(fill="both", expand=True, pady=(0, 8))

        self.tree = ttk.Treeview(tree_frame, columns=("id", "name", "type"),
                                  show="headings", selectmode="browse")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text=self._t("skill_name", default="Tên"))
        self.tree.heading("type", text=self._t("skill_type", default="Loại"))
        self.tree.column("id", width=60, stretch=False)
        self.tree.column("name", width=300, stretch=True)
        self.tree.column("type", width=100, stretch=False)
        self.tree.pack(side="left", fill="both", expand=True)
        ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview).pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=lambda *a: None)

        self.tree.bind("<Double-1>", lambda e: self._on_confirm())
        self.tree.bind("<Return>", lambda e: self._on_confirm())
        self.tree.bind("<<TreeviewSelect>>", self._on_select_change)

        self.status_var = tk.StringVar()
        tk.Label(main, textvariable=self.status_var, font=UI.FONT_TEXT,
                 fg=UI.ACCENT_AMBER).pack(fill="x", pady=(0, 4))

        # Buttons
        btn_frame = tk.Frame(main)
        btn_frame.pack(fill="x", pady=(8, 0))
        tk.Button(btn_frame, text=self._t("skill_picker.cancel", default="Hủy"),
                  command=self._on_cancel, width=10).pack(side="right", padx=(8, 0))
        self.btn_confirm = tk.Button(btn_frame, text=self._t("skill_picker.confirm", default="Chọn"),
                                     command=self._on_confirm, state="disabled",
                                     width=10, bg=UI.BTN_PRIMARY_BG, fg=UI.BTN_PRIMARY_FG)
        self.btn_confirm.pack(side="right")

        self._item_map = {}

    def _filter_results(self):
        query = self.search_var.get().strip().lower()
        show_all = self.show_all.get()

        filtered = []
        for s in self.all_skills:
            # Nếu không show all → lọc theo class đã được filter từ trước (list đã filter sẵn)
            # Nếu show all → dùng all_skills_all nếu có, không thì dùng all_skills
            if query and query not in (s.get("name", "").lower()):
                continue
            filtered.append(s)

        self._render_results(filtered)

    def _render_results(self, records):
        self.tree.delete(*self.tree.get_children())
        self.status_var.set("")
        self.btn_confirm.config(state="disabled")
        self._item_map.clear()

        if not records:
            self.status_var.set(self._t("skill_picker.empty", default="Không có skill"))
            return

        for s in records:
            skill_id = s.get("skill_id")
            name = s.get("name", "Unknown")
            type_ = s.get("type", s.get("skill_type", "—"))

            is_excluded = skill_id in self.excluded

            item_id = self.tree.insert(
                "", "end",
                values=(f"#{skill_id}", name, type_),
                tags=("excluded",) if is_excluded else (),
            )
            self._item_map[item_id] = s

        self.tree.tag_configure("excluded", foreground=UI.TEXT_MUTED)

    def _on_select_change(self, event):
        sel = self.tree.selection()
        if sel and self._item_map.get(sel[0], {}).get("skill_id") not in self.excluded:
            self.btn_confirm.config(state="normal")
        else:
            self.btn_confirm.config(state="disabled")

    def _on_confirm(self):
        sel = self.tree.selection()
        if not sel:
            return
        record = self._item_map.get(sel[0])
        if not record:
            return
        if record.get("skill_id") in self.excluded:
            self.status_var.set(self._t("skill_picker.duplicate",
                                        default="Skill này đã có trong lane"))
            return
        self.on_select(record)
        self._close()

    def _on_cancel(self):
        self._close()

    def _close(self):
        self.grab_release()
        self.destroy()
