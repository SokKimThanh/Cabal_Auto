import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Any
from database import get_all_monsters_api, search_monsters_api
from lib.ui_style import UIStyle as UI

class MonsterPickerDialog(tk.Toplevel):
    def __init__(self, parent, lang, on_select: Callable[[Dict[str, Any]], None], t_func: Callable):
        super().__init__(parent)
        self.parent = parent
        self.lang = lang
        self.on_select = on_select
        self._t = t_func

        self.title(self._t("monster_picker_title"))

        # Don't hardcode minsize, make it responsive
        self.geometry("600x450")
        self.resizable(True, True)

        self.transient(parent)
        self.grab_set()

        # Center dialog
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.bind("<Escape>", lambda e: self._on_cancel())

        self._setup_ui()
        self._cache = {}
        self._search_timer = None
        self._item_map = {}
        self._item_map = {}

        self._load_initial_data()

    def _setup_ui(self):
        main_frame = tk.Frame(self, padx=16, pady=16)
        main_frame.pack(fill="both", expand=True)

        # Header
        lbl_instruction = tk.Label(
            main_frame,
            text=self._t("monster_picker_instruction"),
            font=UI.FONT_LABEL,
            fg=UI.COLOR_TEXT,
            anchor="w"
        )
        lbl_instruction.pack(fill="x", pady=(0, 8))

        # Search Bar
        search_frame = tk.Frame(main_frame)
        search_frame.pack(fill="x", pady=(0, 8))

        lbl_search = tk.Label(
            search_frame,
            text=self._t("monster_picker_search_label"),
            font=UI.FONT_LABEL,
            fg=UI.COLOR_TEXT
        )
        lbl_search.pack(side="left", padx=(0, 8))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=UI.FONT_TEXT
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.focus_set()

        # Treeview
        tree_frame = tk.LabelFrame(
            main_frame,
            text=self._t("monster_picker_results"),
            font=UI.FONT_LABEL,
            fg=UI.COLOR_TEXT,
            padx=8, pady=8
        )
        tree_frame.pack(fill="both", expand=True, pady=(0, 8))

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("id", "name", "level", "hp"),
            show="headings",
            selectmode="browse"
        )

        self.tree.heading("id", text="ID", anchor="w")
        self.tree.heading("name", text=self._t("monster_name") if self._t else "Name", anchor="w")
        self.tree.heading("level", text=self._t("monster_level") if self._t else "Lv", anchor="center")
        self.tree.heading("hp", text=self._t("monster_hp") if self._t else "HP", anchor="e")

        self.tree.column("id", width=50, stretch=False)
        self.tree.column("name", width=250, stretch=True)
        self.tree.column("level", width=50, stretch=False, anchor="center")
        self.tree.column("hp", width=80, stretch=False, anchor="e")

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind("<Double-1>", lambda e: self._on_confirm())
        self.tree.bind("<Return>", lambda e: self._on_confirm())
        self.tree.bind("<<TreeviewSelect>>", self._on_select_change)

        # Status Label for errors/empty
        self.status_var = tk.StringVar()
        self.status_label = tk.Label(
            main_frame,
            textvariable=self.status_var,
            font=UI.FONT_TEXT,
            fg=UI.COLOR_WARNING
        )
        self.status_label.pack(fill="x", pady=(0, 4))

        # Bottom Buttons
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(8, 0))

        self.btn_cancel = tk.Button(
            btn_frame,
            text=self._t("monster_picker_cancel"),
            font=UI.FONT_BUTTON,
            command=self._on_cancel,
            width=10
        )
        self.btn_cancel.pack(side="right", padx=(8, 0))

        self.btn_confirm = tk.Button(
            btn_frame,
            text=self._t("monster_picker_confirm"),
            font=UI.FONT_BUTTON,
            command=self._on_confirm,
            state="disabled",
            width=10,
            bg=UI.COLOR_PRIMARY,
            fg="white"
        )
        self.btn_confirm.pack(side="right")

    def _load_initial_data(self):
        try:
            results = get_all_monsters_api(100)
            self._cache[""] = results
            self._render_results(results)
        except Exception as e:
            import logging
            logging.error(f"[MonsterPicker] Error loading data: {e}", exc_info=True)
            self._render_error()

    def _on_search_change(self, *args):
        if self._search_timer:
            self.after_cancel(self._search_timer)
        self._search_timer = self.after(300, self._perform_search)

    def _perform_search(self):
        query = self.search_var.get().strip().lower()
        if not query:
            results = self._cache.get("", [])
            self._render_results(results)
            return

        if query in self._cache:
            self._render_results(self._cache[query])
            return

        try:
            results = search_monsters_api(query, limit=50)
            self._cache[query] = results
            self._render_results(results)
        except Exception as e:
            import logging
            logging.error(f"[MonsterPicker] Error loading data: {e}", exc_info=True)
            self._render_error()

    def _render_results(self, records):
        self.tree.delete(*self.tree.get_children())
        self.status_var.set("")
        self.btn_confirm.config(state="disabled")
        self._item_map.clear()

        if not records:
            self.status_var.set(self._t("monster_picker_empty"))
            return

        for r in records:
            id_val = r.get("id")
            name_val = r.get("name", "Unknown")
            lvl_val = r.get("level", "--")
            hp_val = r.get("hp", "--")
            dungeon_id = r.get("dungeonId")

            try:
                monster_id = int(id_val) if id_val is not None else 0
            except (ValueError, TypeError):
                monster_id = 0

            item_id = self.tree.insert("", "end", values=(f"#{id_val}", name_val, lvl_val, hp_val))
            # Attach canonical record to the item for retrieval later
            canonical_record = {
                "monster_id": monster_id,
                "name": str(name_val).strip(),
                "dungeon_id": str(dungeon_id) if dungeon_id else None
            }
            # Store canonical mapping
            self._item_map[item_id] = canonical_record

    def _render_error(self):
        self.tree.delete(*self.tree.get_children())
        self.status_var.set(self._t("monster_picker_load_failed"))
        self.btn_confirm.config(state="disabled")

    def _on_select_change(self, event):
        selected = self.tree.selection()
        if selected:
            self.btn_confirm.config(state="normal")
        else:
            self.btn_confirm.config(state="disabled")

    def _on_confirm(self):
        selected = self.tree.selection()
        if not selected:
            return

        item_id = selected[0]
        if hasattr(self, '_item_map') and item_id in self._item_map:
            canonical_record = self._item_map[item_id]
            # Valid canonical record
            if canonical_record["monster_id"] > 0:
                self.on_select(canonical_record)
                self._close()

    def _on_cancel(self):
        self._close()

    def _close(self):
        self.grab_release()
        self.destroy()
