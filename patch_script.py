import re

with open('ui/views/icon_manager_frame.py', 'r') as f:
    content = f.read()

# Import CategoryManagerComponent
content = content.replace(
    'from ui.components.empty_state import EmptyState',
    'from ui.components.empty_state import EmptyState\nfrom ui.components.category_manager_component import CategoryManagerComponent'
)

# Update _build_categories_panel
new_panel = """    def _build_categories_panel(self, parent_frame):
        self.category_manager = CategoryManagerComponent(
            parent_frame,
            app=self.app,
            icon_service=self.icon_service,
            tree_model=self.tree_model,
            on_category_changed=self._on_category_changed
        )
        self.category_manager.pack(fill="both", expand=True)
        self.category_manager.start()

    def _on_category_changed(self):
        self._populate_category_combo()
        self.load_tree_data()
"""

# We need to replace the old _build_categories_panel
start_idx = content.find('def _build_categories_panel(self, parent_frame):')
if start_idx != -1:
    # Find the end of the method (next method def or end of class)
    end_idx = content.find('    def _build_preview_zone(self):', start_idx)
    if end_idx != -1:
        content = content[:start_idx] + new_panel + '\n' + content[end_idx:]

with open('ui/views/icon_manager_frame.py', 'w') as f:
    f.write(content)
