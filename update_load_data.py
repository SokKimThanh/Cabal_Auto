import re

with open('ui/views/icon_manager_frame.py', 'r') as f:
    content = f.read()

import_search = "from lib.ui_style_v2 import UIStyleV2 as UIStyle"
import_replace = """from lib.ui_style_v2 import UIStyleV2 as UIStyle
from lib.db.services.icon_service import IconService
from ui.helpers.icon_helper import get_icon_helper
from database import get_db"""

content = content.replace(import_search, import_replace)

init_search = """        self.app = app
        self._setup_ui()"""
init_replace = """        self.app = app
        self.db = get_db()
        self.icon_service = IconService(self.db.conn)
        self.icon_helper = get_icon_helper()

        self._setup_ui()
        self.load_tree_data()"""

content = content.replace(init_search, init_replace)


methods_search = """    def apply_filters(self):
        pass"""

methods_replace = """    def apply_filters(self):
        self.load_tree_data()

    def load_tree_data(self):
        # Clear current tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get filter values
        search_term = self.search_var.get().strip().lower()
        selected_category = self.category_var.get()
        if selected_category == "All":
            selected_category = ""

        selected_status_raw = self.status_var.get()
        # Parse status filter
        status_filter = ""
        if "Xanh" in selected_status_raw:
            status_filter = "GREEN"
        elif "Vàng" in selected_status_raw:
            status_filter = "YELLOW"
        elif "Đỏ" in selected_status_raw:
            status_filter = "RED"

        # Fetch all icons (using search and category from DB)
        all_icons = self.icon_service.get_all_icons(search_term=search_term, category=selected_category)

        # Populate Category dropdown dynamically if it's the first time
        if not hasattr(self, '_categories_loaded') or not self._categories_loaded:
            # We fetch all without filters just to get unique categories
            all_raw = self.icon_service.get_all_icons()
            categories = set(icon.get("category", "General") for icon in all_raw if icon.get("category"))
            sorted_cats = ["All"] + sorted(list(categories))
            self.category_combo['values'] = sorted_cats
            self._categories_loaded = True

        # Group by category and filter by status
        grouped_data = {}
        for icon in all_icons:
            # Check status logic
            status = self.icon_helper.evaluate_icon_status(icon)

            # Apply status filter in Python
            if status_filter and status != status_filter:
                continue

            cat = icon.get("category", "General")
            if cat not in grouped_data:
                grouped_data[cat] = []
            grouped_data[cat].append((icon, status))

        # Render Treeview
        for cat_name, items in sorted(grouped_data.items()):
            # Insert Category Node
            cat_id = f"cat_{cat_name}"
            self.tree.insert('', 'end', iid=cat_id, text=f"📁 {cat_name}", open=True)

            for icon, status in sorted(items, key=lambda x: x[0].get("name", "").lower()):
                icon_id = icon.get("id")
                icon_key = icon.get("icon_key", "")
                icon_name = icon.get("name", "")

                # Format status column with emoji
                status_color = "⚪" # Default
                if status == "GREEN":
                    status_color = "🟢"
                elif status == "YELLOW":
                    status_color = "🟡"
                elif status == "RED":
                    status_color = "🔴"

                self.tree.insert(
                    cat_id,
                    'end',
                    iid=icon_key,
                    text=icon_name,
                    values=(icon_id, icon_key, status_color)
                )

        # Recheck scrollbar
        self._check_scrollbar()"""

content = content.replace(methods_search, methods_replace)

with open('ui/views/icon_manager_frame.py', 'w') as f:
    f.write(content)
