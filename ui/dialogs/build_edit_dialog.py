import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, List, Optional
from ui.components import create_icon_button
from lib.events.ui_element_registry import CommonUI
from lib.ui_style_v2 import UIStyleV2 as UIStyle

class BuildEditDialog(tk.Toplevel):
    MODULE_NAME = "build_manager"
    SCREEN_NAME = "edit_dialog"

    def __init__(self, parent, app, title: str, build_data: Optional[Dict[str, Any]], classes: List[Dict[str, Any]], on_save):
        super().__init__(parent)
        self.app = app
        self.title(title)
        self.build_data = build_data or {}
        self.classes = classes
        self.on_save = on_save

        self.transient(parent)
        self.grab_set()

        self.config(bg=UIStyle.BG_BASE)
        self.geometry("600x550")
        self.resizable(False, False)

        self._setup_ui()
        self._center_window()
        self._populate_data()
        self.focus_set()

    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _setup_ui(self):
        main_frame = tk.Frame(self, bg=UIStyle.BG_BASE)
        main_frame.pack(fill="both", expand=True, padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_MD)

        # Class Combobox
        tk.Label(main_frame, text="Class (*):", bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY).grid(row=0, column=0, sticky="e", pady=5, padx=5)
        self.class_var = tk.StringVar()
        self.class_cb = ttk.Combobox(main_frame, textvariable=self.class_var, state="readonly", width=30)

        self.class_options = [f"{c.get('id', c.get('class_id', ''))} - {c.get('name', 'Unknown')}" for c in self.classes]
        if not self.class_options:
            self.class_options = ["0 - None"]

        self.class_cb['values'] = self.class_options
        self.class_cb.grid(row=0, column=1, sticky="w", pady=5, padx=5)
        self.class_cb.bind("<<ComboboxSelected>>", self._on_class_changed)

        # Author
        tk.Label(main_frame, text="Author:", bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY).grid(row=1, column=0, sticky="e", pady=5, padx=5)
        self.author_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.author_var, width=33).grid(row=1, column=1, sticky="w", pady=5, padx=5)

        # Description
        tk.Label(main_frame, text="Description:", bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY).grid(row=2, column=0, sticky="ne", pady=5, padx=5)
        self.desc_text = tk.Text(main_frame, width=33, height=4, bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY, insertbackground=UIStyle.TEXT_PRIMARY)
        self.desc_text.grid(row=2, column=1, sticky="w", pady=5, padx=5)

        # Upvote Count (readonly but we can set initial)
        tk.Label(main_frame, text="Upvotes:", bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY).grid(row=3, column=0, sticky="e", pady=5, padx=5)
        self.upvote_var = tk.IntVar(value=0)
        upvote_spin = ttk.Spinbox(main_frame, from_=0, to=999999, increment=1, textvariable=self.upvote_var, width=10)
        upvote_spin.grid(row=3, column=1, sticky="w", pady=5, padx=5)


        # Skills Area
        skills_frame = tk.Frame(main_frame, bg=UIStyle.BG_BASE)
        skills_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=10)
        main_frame.rowconfigure(4, weight=1)
        skills_frame.columnconfigure(0, weight=1)
        skills_frame.columnconfigure(1, weight=1)
        skills_frame.rowconfigure(1, weight=1)

        tk.Label(skills_frame, text=self.app._t("lbl_attack_skills", default="Attack Skills"), bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY, font=("", 10, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(skills_frame, text=self.app._t("lbl_buff_skills", default="Buff Skills"), bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY, font=("", 10, "bold")).grid(row=0, column=1, sticky="w")

        atk_frame = tk.Frame(skills_frame, bg=UIStyle.BG_BASE)
        atk_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        atk_scroll = ttk.Scrollbar(atk_frame)
        atk_scroll.pack(side="right", fill="y")
        self.atk_listbox = tk.Listbox(atk_frame, selectmode=tk.MULTIPLE, yscrollcommand=atk_scroll.set, bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY, selectbackground=UIStyle.COLOR_PRIMARY, exportselection=False)
        self.atk_listbox.pack(side="left", fill="both", expand=True)
        atk_scroll.config(command=self.atk_listbox.yview)

        buff_frame = tk.Frame(skills_frame, bg=UIStyle.BG_BASE)
        buff_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        buff_scroll = ttk.Scrollbar(buff_frame)
        buff_scroll.pack(side="right", fill="y")
        self.buff_listbox = tk.Listbox(buff_frame, selectmode=tk.MULTIPLE, yscrollcommand=buff_scroll.set, bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY, selectbackground=UIStyle.COLOR_PRIMARY, exportselection=False)
        self.buff_listbox.pack(side="left", fill="both", expand=True)
        buff_scroll.config(command=self.buff_listbox.yview)

        btn_frame = tk.Frame(main_frame, bg=UIStyle.BG_BASE)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)

        create_icon_button(parent=btn_frame, icon_name="save", text="Save", command=self._on_save_click, button_type="green_light", element_id=CommonUI.BTN_SAVE).pack(side="left", padx=10)
        create_icon_button(parent=btn_frame, icon_name="cancel", text="Cancel", command=self.destroy, button_type="refresh", element_id=CommonUI.BTN_CANCEL).pack(side="left", padx=10)

    def _populate_data(self):
        if not self.build_data:
            if self.class_options:
                self.class_cb.set(self.class_options[0])
            return

        cid = self.build_data.get("class_id")
        if cid is not None:
            for opt in self.class_options:
                if opt.startswith(f"{cid} -"):
                    self.class_cb.set(opt)
                    break
        else:
            if self.class_options:
                self.class_cb.set(self.class_options[0])

        self.author_var.set(self.build_data.get("author", ""))
        self.desc_text.insert("1.0", self.build_data.get("description", ""))
        self.upvote_var.set(self.build_data.get("upvote_count", 0))
        self._load_skills()



    def _on_class_changed(self, event=None):
        self._load_skills(clear_selections=True)

    def _load_skills(self, clear_selections=False):
        self.atk_listbox.delete(0, tk.END)
        self.buff_listbox.delete(0, tk.END)
        self.skill_id_map = {"atk": [], "buff": []}

        class_str = self.class_var.get()
        class_id = None
        try:
            class_id = int(class_str.split(" - ")[0])
        except (ValueError, IndexError):
            pass

        if class_id is None or class_id == 0 or not hasattr(self.app, 'db_skill_service'):
            return

        # Fetch skills for this class
        all_skills = self.app.db_skill_service.get_skills_by_filter(class_id=class_id, limit=999)

        atk_skills = [s for s in all_skills if s.get("skill_type_id") == 1]
        buff_skills = [s for s in all_skills if s.get("skill_type_id") == 2]

        # Use aliases or names
        for s in atk_skills:
            name = f"{s['skill_id']} - {s.get('alias') or s.get('name')}"
            self.atk_listbox.insert(tk.END, name)
            self.skill_id_map["atk"].append(s['skill_id'])

        for s in buff_skills:
            name = f"{s['skill_id']} - {s.get('alias') or s.get('name')}"
            self.buff_listbox.insert(tk.END, name)
            self.skill_id_map["buff"].append(s['skill_id'])

        # Restore selections if not clearing and build data exists
        if not clear_selections and self.build_data:
            saved_atk_ids = self.build_data.get("attack_skill_ids", [])
            for i, sid in enumerate(self.skill_id_map["atk"]):
                if sid in saved_atk_ids:
                    self.atk_listbox.selection_set(i)

            saved_buff_ids = self.build_data.get("buff_skill_ids", [])
            for i, sid in enumerate(self.skill_id_map["buff"]):
                if sid in saved_buff_ids:
                    self.buff_listbox.selection_set(i)

    def _on_save_click(self):
        class_str = self.class_var.get()
        class_id = None
        try:
            class_id = int(class_str.split(" - ")[0])
        except (ValueError, IndexError):
            messagebox.showerror("Lỗi", "Vui lòng chọn Class hợp lệ.", parent=self)
            return

        if class_id == 0:
            messagebox.showerror("Lỗi", "Khóa ngoại class_id không được để trống/None.", parent=self)
            return

        atk_ids = [self.skill_id_map["atk"][i] for i in self.atk_listbox.curselection()]
        buff_ids = [self.skill_id_map["buff"][i] for i in self.buff_listbox.curselection()]

        data = {
            "class_id": class_id,
            "author": self.author_var.get().strip(),
            "description": self.desc_text.get("1.0", tk.END).strip(),
            "upvote_count": self.upvote_var.get(),
            "attack_skill_ids": atk_ids,
            "buff_skill_ids": buff_ids,
        }

        if "build_id" in self.build_data:
            data["build_id"] = self.build_data["build_id"]

        self.on_save(data)
        self.destroy()
