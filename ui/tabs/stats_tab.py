from tkinter import ttk


class StatsTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=12)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        # Stats Treeview with dark theme
        columns = ("stat", "value")
        self.tree = ttk.Treeview(
            self, columns=columns, show="headings", style="Treeview"
        )

        self.tree.heading(
            "stat", text=self.app._t("stat_name") if hasattr(self.app, "_t") else "Stat"
        )
        self.tree.heading(
            "value",
            text=self.app._t("stat_value") if hasattr(self.app, "_t") else "Value",
        )

        self.tree.column("stat", width=200, anchor="w")
        self.tree.column("value", width=100, anchor="e")

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Populate some empty states
        self.tree.insert("", "end", values=("Target Found", "0"))
        self.tree.insert("", "end", values=("Target Lost", "0"))
        self.tree.insert("", "end", values=("Skills Cast", "0"))
