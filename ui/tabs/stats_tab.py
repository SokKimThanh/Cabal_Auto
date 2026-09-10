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

        if hasattr(self.app, "bind_text"):
            class TreeviewHeadingBinder:
                def __init__(self, tree, column):
                    self.tree = tree
                    self.column = column
                def set_text(self, text):
                    try:
                        self.tree.heading(self.column, text=text)
                    except Exception:
                        pass

            self.app.bind_text(TreeviewHeadingBinder(self.tree, "stat"), "stat_name")
            self.app.bind_text(TreeviewHeadingBinder(self.tree, "value"), "stat_value")
        else:
            self.tree.heading("stat", text="Stat")
            self.tree.heading("value", text="Value")

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
