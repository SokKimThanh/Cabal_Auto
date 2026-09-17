# Refactor IconManagerFrame

## Context
If we already have:
- `IconTreeModel`
- `ImageLibraryModel`

The direction for refactoring `IconManagerFrame` is clear.

### Current State
`IconManagerFrame`
├── UI
├── Tree events
├── Tree rendering
├── Preview
├── Import image
├── Search image
├── File validation
├── Cache refresh
├── DB update
└── Form state

### Goal
`IconManagerFrame`
├── UI
├── Event binding
├── Render data
└── Model calls

## Step 1: Extract Tree completely

There should no longer be:
- `load_tree_data()`
- `build_tree()`
- `filter_tree()`

inside the Frame.

Change to:
```python
tree_data = self.tree_model.get_filtered_tree_data(...)
```

The Frame should only:
```python
_render_tree(tree_data)
```

## Step 2: Extract Image Library

Functions like:
- `_scan_image_folder()`
- `_search_images()`
- `_refresh_images()`

should disappear from the Frame.

Replace with:
```python
self.image_library_model.scan_async()
self.image_library_model.search()
self.image_library_model.refresh()
```

The Frame should only:
```python
_update_image_listbox(results)
```

## Step 3: Extract Import

This is usually the biggest part.

Instead of:
```python
_on_import_image_clicked()
    validate
    copy
    duplicate
    update db
    refresh
```

change to:
```python
_on_import_image_clicked()
    result = image_library_model.import_image(...)
```

The Frame only shows:
- messagebox
- preview

## Step 4: Group Preview into a single zone

Currently there are often multiple places:
- `_update_preview()`
- `_refresh_preview()`
- `_load_preview()`

It's very easy to call them haphazardly.

Should only keep:
```python
_render_preview(icon)
```

Everywhere else:
```python
self._render_preview(selected_icon)
```

## Step 5: Extract Form State

Currently it seems to be doing:
```python
if self._current_state == "ADD"
if self._current_state == "EDIT"
```
scattered throughout the file.

Should group them into:
```python
_enter_add_mode()
_enter_edit_mode()
_enter_view_mode()
```

Put all `enable/disable widget` inside those methods.

## After Refactoring

`IconManagerFrame` should generally only have:
```python
class IconManagerFrame:
    def _setup_ui()
    def _bind_events()
    def _render_tree()
    def _render_preview()
    def _render_image_library()
    def _render_form()
    def _on_tree_select()
    def _on_image_selected()
    def _enter_add_mode()
    def _enter_edit_mode()
    def _enter_view_mode()
```

While:
- load data
- cache
- filesystem
- search
- import
- duplicate check
- dependency
- safe delete

will reside in:
- `IconTreeModel`
- `ImageLibraryModel`

## Execution Priority

1. Import Image Logic
2. Image Scan/Search
3. Tree Logic
4. Preview Logic
5. Form State

Because currently the Import + FileSystem section is where `IconManagerFrame` is most likely to turn into a God Class. After moving everything to `ImageLibraryModel`, the UI file will become much lighter.
