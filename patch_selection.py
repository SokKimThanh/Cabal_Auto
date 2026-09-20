with open('ui/views/icon_manager_frame.py', 'r') as f:
    content = f.read()

# Replace `self._current_available_element_selection = target_node` with setting it to None so the event fires,
# OR we can just directly extract the label update logic. Let's just fix `_sync_available_elements_selection`.
# Instead of self._current_available_element_selection = target_node, we can set it to None, call selection_set,
# and let the event handler take care of setting `self._current_available_element_selection` and updating the UI label.

old_block = """
        if target_node:
            self._current_available_element_selection = target_node
            self.available_elements_tree.selection_set(target_node)
            self.available_elements_tree.see(target_node)
        else:
            self._current_available_element_selection = None
            if self.available_elements_tree.selection():
                self.available_elements_tree.selection_remove(*self.available_elements_tree.selection())
            # Clear label variables if there is no mapping
            if hasattr(self, 'var_usage_element'):
                self.var_usage_element.set("")
            if hasattr(self, 'var_usage_mod'):
                self.var_usage_mod.set("")
            if hasattr(self, 'var_usage_comp'):
                self.var_usage_comp.set("")
"""

new_block = """
        if target_node:
            # We must NOT set self._current_available_element_selection to target_node before selection_set.
            # If we do, the `_on_available_element_select` event handler will return early and fail to update the labels.
            # By setting it to None or bypassing the check, we force the UI labels to synchronize correctly.
            self._current_available_element_selection = None
            self.available_elements_tree.selection_set(target_node)
            self.available_elements_tree.see(target_node)
        else:
            self._current_available_element_selection = None
            if self.available_elements_tree.selection():
                self.available_elements_tree.selection_remove(*self.available_elements_tree.selection())
            # Clear label variables if there is no mapping
            if hasattr(self, 'var_usage_element'):
                self.var_usage_element.set("")
            if hasattr(self, 'var_usage_mod'):
                self.var_usage_mod.set("")
            if hasattr(self, 'var_usage_comp'):
                self.var_usage_comp.set("")
            if hasattr(self, 'var_current_mapping_element'):
                self.var_current_mapping_element.set("UI Element ID đang chọn: (Chưa chọn)")
"""

content = content.replace(old_block, new_block)
with open('ui/views/icon_manager_frame.py', 'w') as f:
    f.write(content)
