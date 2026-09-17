# Sprint 32 - Prompt 03: Refactor IconManagerFrame Tree Logic

## Context
We are refactoring `IconManagerFrame` to decouple UI rendering from business logic. The backend logic is being moved to `ImageLibraryModel` and `IconTreeModel`.

**Focus for this session:** Tree Data Construction and Filtering.

## Current State
`IconManagerFrame.load_tree_data()` is currently doing too much. It grabs data, builds filter arguments, filters the data, and then constructs a massive rendering queue (`_render_queue`) inline, before passing it to `_process_incremental_queue`.

## Goal
The UI Frame should not build the data structure for the tree. It should only render it.

## Requirements
1. **Delegate Data Fetching:** `load_tree_data()` should pull the pre-filtered and pre-structured data from `self.tree_model.get_filtered_tree_data(...)`.
2. **Isolate Rendering:** Extract the actual Tkinter Treeview rendering logic (the creation of the `_render_queue` and the call to `_process_incremental_queue`) into a separate, dedicated method named `_render_tree(filtered_data)`.
3. **Clean Controller Method:** `load_tree_data()` should essentially look like:
   ```python
   def load_tree_data(self):
       # 1. get filters from UI vars
       # 2. self.tree_model.set_filters(...)
       # 3. tree_data = self.tree_model.get_filtered_tree_data()
       # 4. self._render_tree(tree_data)
   ```
4. **No Logic in Model:** The Tkinter UI specific logic (`_process_incremental_queue`, batching) MUST stay in the `IconManagerFrame`. Do not move `Tkinter` imports or Tkinter logic into `IconTreeModel`.

## Output
Modify `ui/views/icon_manager_frame.py` to extract `_render_tree`. Run tests after making the changes.
