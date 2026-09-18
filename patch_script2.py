import re

with open('ui/views/icon_manager_frame.py', 'r') as f:
    content = f.read()

# Remove the methods moved to CategoryManagerComponent
methods_to_remove = [
    '    def _load_categories_tree(self):',
    '    def _set_cat_form_state(self, state):',
    '    def _on_cat_tree_select(self, event):',
    '    def _on_cat_add(self):',
    '    def _on_cat_save(self):',
    '    def _on_cat_cancel(self):',
    '    def _on_cat_delete(self):',
    '    def _on_cat_tree_interaction(self, event):'
]

# They are all at the bottom of the file in the original script, right after _process_tree_selection
# We will use regex to remove them, or simple string splitting.
# Let's find the start of `    def _load_categories_tree(self):`
start_idx = content.find('    def _load_categories_tree(self):')
end_idx = content.find('    def _on_tree_open(self, event):', start_idx)

if start_idx != -1 and end_idx != -1:
    # Let's also remove `_on_cat_tree_interaction` which is located before `_on_tree_select`
    interaction_start = content.find('    def _on_cat_tree_interaction(self, event):')
    interaction_end = content.find('    def _on_tree_select(self, event):', interaction_start)

    if interaction_start != -1 and interaction_end != -1:
        content = content[:interaction_start] + content[interaction_end:]

    # Recalculate start_idx and end_idx as string length changed
    start_idx = content.find('    def _load_categories_tree(self):')
    end_idx = content.find('    def _on_tree_open(self, event):', start_idx)

    if start_idx != -1 and end_idx != -1:
        content = content[:start_idx] + content[end_idx:]

with open('ui/views/icon_manager_frame.py', 'w') as f:
    f.write(content)
