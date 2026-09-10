import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Callable, Optional

from lib.ui_style_v2 import UIStyleV2 as UIStyle

class SkillEditDialog(tk.Toplevel):
    def __init__(self, parent, app, title: str, skill_data: Optional[Dict[str, Any]], on_save: Callable[[Dict[str, Any]], None]):
        super().__init__(parent)
        self.app = app
        self.title(title)
        self.skill_data = skill_data or {}
        self.on_save = on_save

        self.transient(parent)
        self.grab_set()

        self.config(bg=UIStyle.THEME_BG_APP)
        self.geometry("400x500")
        self.resizable(False, False)

        # Keep references to input variables
        self.var_name = tk.StringVar(value=self.skill_data.get("name", ""))
        self.var_type = tk.StringVar(value=self.skill_data.get("type", "Attack"))

        # Need a string var for combobox selection
        self.var_class_id_str = tk.StringVar()

        self.var_alias = tk.StringVar(value=self.skill_data.get("alias", ""))

        self.var_icon_x = tk.IntVar(value=self.skill_data.get("icon_x", 0))
        self.var_icon_y = tk.IntVar(value=self.skill_data.get("icon_y", 0))
        self.var_icon_w = tk.IntVar(value=self.skill_data.get("icon_w", 0))
        self.var_icon_h = tk.IntVar(value=self.skill_data.get("icon_h", 0))

        self._build_ui()

        # Center the dialog
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        main_frame = tk.Frame(self, bg=UIStyle.THEME_BG_APP, padx=UIStyle.SPACE_LG, pady=UIStyle.SPACE_LG)
        main_frame.pack(fill="both", expand=True)

        # ----- Primary Information -----
        primary_frame = tk.LabelFrame(main_frame, text="Primary Information", bg=UIStyle.THEME_BG_APP, fg=UIStyle.TEXT_PRIMARY)
        primary_frame.pack(fill="x", pady=(0, UIStyle.SPACE_MD))

        # Name
        name_frame = tk.Frame(primary_frame, bg=UIStyle.THEME_BG_APP)
        name_frame.pack(fill="x", padx=UIStyle.SPACE_SM, pady=UIStyle.SPACE_SM)
        tk.Label(name_frame, text="Name (*):", bg=UIStyle.THEME_BG_APP, fg=UIStyle.TEXT_PRIMARY, width=15, anchor="w").pack(side="left")
        tk.Entry(name_frame, textvariable=self.var_name).pack(side="left", fill="x", expand=True)

        # Type
        type_frame = tk.Frame(primary_frame, bg=UIStyle.THEME_BG_APP)
        type_frame.pack(fill="x", padx=UIStyle.SPACE_SM, pady=UIStyle.SPACE_SM)
        tk.Label(type_frame, text="Type:", bg=UIStyle.THEME_BG_APP, fg=UIStyle.TEXT_PRIMARY, width=15, anchor="w").pack(side="left")
        type_combo = ttk.Combobox(type_frame, textvariable=self.var_type, values=["Attack", "Buff", "Passive"], state="readonly")
        type_combo.pack(side="left", fill="x", expand=True)
        if not self.var_type.get():
            self.var_type.set("Attack")

        # Class ID
        class_frame = tk.Frame(primary_frame, bg=UIStyle.THEME_BG_APP)
        class_frame.pack(fill="x", padx=UIStyle.SPACE_SM, pady=UIStyle.SPACE_SM)
        tk.Label(class_frame, text="Class ID:", bg=UIStyle.THEME_BG_APP, fg=UIStyle.TEXT_PRIMARY, width=15, anchor="w").pack(side="left")

        # Load classes if we can
        class_values = ["0 - None"]
        if hasattr(self.app, "db_class_service"):
            try:
                classes = self.app.db_class_service.get_all_classes()
                for c in classes:
                    class_values.append(f"{c.get('class_id')} - {c.get('name')}")
            except Exception as e:
                print(f"[SkillEditDialog] Error loading classes: {e}")

        # Combobox for classes
        class_combo = ttk.Combobox(class_frame, textvariable=self.var_class_id_str, values=class_values, state="readonly")
        class_combo.pack(side="left", fill="x", expand=True)

        # Set default selection based on current skill_data
        current_class_id = self.skill_data.get("class_id")

        # Determine the initial value based on skill data
        initial_value = "0 - None"
        if current_class_id:
            # Find the string matching this class_id
            for val in class_values:
                try:
                    if int(val.split(" - ")[0]) == current_class_id:
                        initial_value = val
                        break
                except ValueError:
                    continue

        self.var_class_id_str.set(initial_value)

        # ----- Advanced Information -----
        adv_frame = tk.LabelFrame(main_frame, text="Advanced Information", bg=UIStyle.THEME_BG_APP, fg=UIStyle.TEXT_PRIMARY)
        adv_frame.pack(fill="x", pady=(0, UIStyle.SPACE_MD))

        # Alias
        alias_frame = tk.Frame(adv_frame, bg=UIStyle.THEME_BG_APP)
        alias_frame.pack(fill="x", padx=UIStyle.SPACE_SM, pady=UIStyle.SPACE_SM)
        tk.Label(alias_frame, text="Alias:", bg=UIStyle.THEME_BG_APP, fg=UIStyle.TEXT_PRIMARY, width=15, anchor="w").pack(side="left")
        tk.Entry(alias_frame, textvariable=self.var_alias).pack(side="left", fill="x", expand=True)

        # Icon Frame
        icon_frame = tk.Frame(adv_frame, bg=UIStyle.THEME_BG_APP)
        icon_frame.pack(fill="x", padx=UIStyle.SPACE_SM, pady=UIStyle.SPACE_SM)

        tk.Label(icon_frame, text="Icon X:", bg=UIStyle.THEME_BG_APP, fg=UIStyle.TEXT_PRIMARY, width=8, anchor="w").grid(row=0, column=0, pady=2)
        tk.Spinbox(icon_frame, from_=0, to=9999, textvariable=self.var_icon_x, width=5).grid(row=0, column=1, pady=2, padx=(0, 10))

        tk.Label(icon_frame, text="Icon Y:", bg=UIStyle.THEME_BG_APP, fg=UIStyle.TEXT_PRIMARY, width=8, anchor="w").grid(row=0, column=2, pady=2)
        tk.Spinbox(icon_frame, from_=0, to=9999, textvariable=self.var_icon_y, width=5).grid(row=0, column=3, pady=2)

        tk.Label(icon_frame, text="Icon W:", bg=UIStyle.THEME_BG_APP, fg=UIStyle.TEXT_PRIMARY, width=8, anchor="w").grid(row=1, column=0, pady=2)
        tk.Spinbox(icon_frame, from_=0, to=999, textvariable=self.var_icon_w, width=5).grid(row=1, column=1, pady=2, padx=(0, 10))

        tk.Label(icon_frame, text="Icon H:", bg=UIStyle.THEME_BG_APP, fg=UIStyle.TEXT_PRIMARY, width=8, anchor="w").grid(row=1, column=2, pady=2)
        tk.Spinbox(icon_frame, from_=0, to=999, textvariable=self.var_icon_h, width=5).grid(row=1, column=3, pady=2)


        # ----- Actions -----
        action_frame = tk.Frame(main_frame, bg=UIStyle.THEME_BG_APP)
        action_frame.pack(fill="x", side="bottom", pady=(UIStyle.SPACE_MD, 0))

        save_btn = tk.Button(action_frame, text="Save", bg=UIStyle.ACCENT_GREEN, fg="white", relief="flat", command=self._on_save_click, width=10)
        save_btn.pack(side="right", padx=(UIStyle.SPACE_SM, 0))

        cancel_btn = tk.Button(action_frame, text="Cancel", bg=UIStyle.BG_ELEVATED, fg=UIStyle.TEXT_PRIMARY, relief="flat", command=self.destroy, width=10)
        cancel_btn.pack(side="right")

    def _on_save_click(self):
        name = self.var_name.get().strip()
        if not name:
            messagebox.showerror("Validation Error", "Name is required.", parent=self)
            return

        class_id = None
        class_selection = self.var_class_id_str.get()
        if class_selection and class_selection != "0 - None":
            try:
                # Extract the ID from "ID - Name"
                extracted_id = int(class_selection.split(" - ")[0])
                if extracted_id > 0:
                    class_id = extracted_id
            except ValueError:
                pass

        data = {
            "name": name,
            "type": self.var_type.get(),
            "class_id": class_id,
            "alias": self.var_alias.get().strip(),
            "icon_x": self.var_icon_x.get(),
            "icon_y": self.var_icon_y.get(),
            "icon_w": self.var_icon_w.get(),
            "icon_h": self.var_icon_h.get()
        }

        # Include original skill_id if editing
        if "skill_id" in self.skill_data:
            data["skill_id"] = self.skill_data["skill_id"]

        self.on_save(data)
        self.destroy()
