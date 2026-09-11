import tkinter as tk
from tkinter import ttk
from lib.ui_style_v2 import UIStyleV2 as UI
from ui.components.base.responsive_grid_base import ResponsiveGridBase
from ui.components.empty_state import EmptyState

class ScanHistoryFrame(ResponsiveGridBase):
    def __init__(self, parent, app):
        super().__init__(parent, bg=UI.BG_BASE)
        self.app = app

        self.current_page = 1
        self.page_size = 20
        self.total_records = 0
        self.total_pages = 1

        # Grid config for main content area to allow treeview to expand
        self.get_content_frame().grid_rowconfigure(1, weight=1)
        self.get_content_frame().grid_columnconfigure(0, weight=1)

        self._build_top_bar()
        self._build_body()
        self._build_footer()

        # Initialize Empty State
        self.empty_state = EmptyState(
            self.get_content_frame(),
            message="Chưa có dữ liệu scan nào." if not hasattr(self.app, "_t") else self.app._t("scan_history_empty_message"),
            submessage="Hãy thực hiện quét vùng trên màn hình để lưu dữ liệu." if not hasattr(self.app, "_t") else self.app._t("scan_history_empty_submessage"),
            icon="🕒"
        )
        # Assuming translation keys aren't added for empty state messages yet, passing fallback string for translation binder or using it directly.
        # Can be refined with TranslationBinder if needed.

        # Initial data load
        self.refresh_filters_and_data()

    def _build_top_bar(self):
        self.top_bar = tk.Frame(self.get_content_frame(), bg=UI.BG_BASE)
        self.top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Class Filter
        class_lbl = tk.Label(self.top_bar, text="Class:", bg=UI.BG_BASE, fg=UI.TEXT_PRIMARY, font=UI.FONT_BODY)
        class_lbl.pack(side="left", padx=(0, 5))

        self.class_var = tk.StringVar(value="0 - None")
        self.class_cb = ttk.Combobox(
            self.top_bar,
            textvariable=self.class_var,
            state="readonly",
            width=20
        )
        self.class_cb.pack(side="left", padx=(0, 15))
        self.class_cb.bind("<<ComboboxSelected>>", lambda e: self.on_filter_change())

        # Monster Filter
        monster_lbl = tk.Label(self.top_bar, text="Monster:", bg=UI.BG_BASE, fg=UI.TEXT_PRIMARY, font=UI.FONT_BODY)
        monster_lbl.pack(side="left", padx=(0, 5))

        self.monster_var = tk.StringVar(value=" - All")
        self.monster_cb = ttk.Combobox(
            self.top_bar,
            textvariable=self.monster_var,
            state="readonly",
            width=20
        )
        self.monster_cb.pack(side="left", padx=(0, 15))
        self.monster_cb.bind("<<ComboboxSelected>>", lambda e: self.on_filter_change())

        # Refresh Button
        self.btn_refresh = tk.Button(
            self.top_bar,
            text="Refresh" if not hasattr(self.app, "_t") else self.app._t("btn_refresh"),
            bg=UI.BG_SURFACE,
            fg=UI.TEXT_PRIMARY,
            command=self.refresh_filters_and_data,
            relief="flat"
        )
        if hasattr(self.app, "bind_text"):
            self.app.bind_text(self.btn_refresh, "btn_refresh")
        self.btn_refresh.pack(side="right")

    def _build_body(self):
        # We need a frame to contain the treeview and its scrollbars using grid
        self.tree_container = tk.Frame(self.get_content_frame(), bg=UI.BG_BASE)
        self.tree_container.grid_rowconfigure(0, weight=1)
        self.tree_container.grid_columnconfigure(0, weight=1)

        columns = ("scan_id", "timestamp", "class_name", "skill_name", "monster_name", "status")
        self.tree = ttk.Treeview(
            self.tree_container,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        # Define headings
        self.tree.heading("scan_id", text="Scan ID")
        self.tree.heading("timestamp", text="Thời gian")
        self.tree.heading("class_name", text="Tên Class")
        self.tree.heading("skill_name", text="Tên Kỹ Năng")
        self.tree.heading("monster_name", text="Tên Quái")
        self.tree.heading("status", text="Status")

        # Define columns
        self.tree.column("scan_id", width=80, anchor="center")
        self.tree.column("timestamp", width=150, anchor="center")
        self.tree.column("class_name", width=120, anchor="w")
        self.tree.column("skill_name", width=150, anchor="w")
        self.tree.column("monster_name", width=150, anchor="w")
        self.tree.column("status", width=100, anchor="center")

        # Scrollbars
        self.vsb = ttk.Scrollbar(self.tree_container, orient="vertical", command=self.tree.yview)
        self.hsb = ttk.Scrollbar(self.tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")

        # Bind to hide/show scrollbars
        self.tree.bind("<Configure>", self._update_scrollbars)

    def _update_scrollbars(self, event=None):
        if self.tree.yview() == (0.0, 1.0):
            self.vsb.grid_remove()
        else:
            self.vsb.grid(row=0, column=1, sticky="ns")

        if self.tree.xview() == (0.0, 1.0):
            self.hsb.grid_remove()
        else:
            self.hsb.grid(row=1, column=0, sticky="ew")

    def _build_footer(self):
        self.footer = tk.Frame(self.get_content_frame(), bg=UI.BG_BASE)
        # grid footer later depending on empty state
        self.footer.grid(row=2, column=0, sticky="ew", pady=(10, 0))

        self.btn_prev = tk.Button(
            self.footer,
            text="Prev" if not hasattr(self.app, "_t") else self.app._t("btn_prev"),
            command=self.prev_page,
            bg=UI.BG_SURFACE,
            fg=UI.TEXT_PRIMARY,
            relief="flat"
        )
        if hasattr(self.app, "bind_text"):
            self.app.bind_text(self.btn_prev, "btn_prev")

        self.page_lbl = tk.Label(self.footer, text="Page 1", bg=UI.BG_BASE, fg=UI.TEXT_PRIMARY, font=UI.FONT_BODY)

        self.btn_next = tk.Button(
            self.footer,
            text="Next" if not hasattr(self.app, "_t") else self.app._t("btn_next"),
            command=self.next_page,
            bg=UI.BG_SURFACE,
            fg=UI.TEXT_PRIMARY,
            relief="flat"
        )
        if hasattr(self.app, "bind_text"):
            self.app.bind_text(self.btn_next, "btn_next")

        # Put pagination on the right
        self.btn_next.pack(side="right", padx=(5, 0))
        self.page_lbl.pack(side="right", padx=(5, 5))
        self.btn_prev.pack(side="right", padx=(0, 5))

    def refresh_filters_and_data(self):
        self._load_filters()
        self.current_page = 1
        self.load_data()

    def _load_filters(self):
        # Load Classes
        classes = self.app.db_class_service.get_all_classes()
        class_values = ["0 - None"]
        for c in classes:
            class_values.append(f"{c['class_id']} - {c['name']}")

        current_class = self.class_var.get()
        self.class_cb['values'] = class_values
        if current_class not in class_values:
            self.class_var.set("0 - None")

        # Load Scanned Monsters
        monsters = self.app.db_scan_service.get_distinct_scanned_monsters()
        monster_values = [" - All"]
        for m in monsters:
            monster_values.append(f"{m['monster_id']} - {m['name']}")

        current_monster = self.monster_var.get()
        self.monster_cb['values'] = monster_values
        if current_monster not in monster_values:
            self.monster_var.set(" - All")

    def on_filter_change(self):
        self.current_page = 1
        self.load_data()

    def load_data(self):
        class_id_str = self.class_var.get()
        monster_id_str = self.monster_var.get()

        class_id = None
        try:
            cid = int(class_id_str.split(" - ")[0])
            if cid > 0:
                class_id = cid
        except (ValueError, IndexError):
            pass

        monster_id = None
        try:
            mid = monster_id_str.split(" - ")[0]
            if mid and mid.strip():
                monster_id = mid
        except IndexError:
            pass

        records, self.total_records = self.app.db_scan_service.get_scans_with_details(
            class_id=class_id,
            monster_id=monster_id,
            page=self.current_page,
            page_size=self.page_size
        )

        self.tree.delete(*self.tree.get_children())

        if self.total_records == 0:
            self._show_empty_state()
        else:
            self._hide_empty_state()
            for r in records:
                self.tree.insert("", "end", values=(
                    r.get("scan_id", ""),
                    r.get("timestamp", ""),
                    r.get("class_name") or "-",
                    r.get("skill_name") or "-",
                    r.get("monster_name") or "-",
                    r.get("status", "")
                ))

            # Update pagination
            self.total_pages = (self.total_records + self.page_size - 1) // self.page_size
            self.page_lbl.config(text=f"Page {self.current_page} / {self.total_pages}")
            self.btn_prev.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
            self.btn_next.config(state=tk.NORMAL if self.current_page < self.total_pages else tk.DISABLED)

            # Check scrollbars
            self.after(50, self._update_scrollbars)

    def _show_empty_state(self):
        self.tree_container.grid_remove()
        self.footer.grid_remove()
        self.empty_state.grid(row=1, column=0, sticky="nsew")

    def _hide_empty_state(self):
        self.empty_state.grid_remove()
        self.tree_container.grid(row=1, column=0, sticky="nsew")
        self.footer.grid(row=2, column=0, sticky="ew", pady=(10, 0))

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_data()
