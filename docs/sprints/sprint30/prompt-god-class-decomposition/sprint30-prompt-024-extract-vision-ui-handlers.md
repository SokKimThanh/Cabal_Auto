# Sprint 30 - Prompt 024: Extract Vision UI Handlers

## Goal
Move Vision and Template-related UI handler methods out of `app_gui.py`.

## Context (Nợ Kỹ Thuật)
`app_gui.App` đang chứa trực tiếp các hàm logic UI về Vision như `_scan_region`, `_add_template`, `_manage_templates`. Việc này làm lẫn lộn giữa chức năng cửa sổ Tkinter chính và các tiện ích xử lý ảnh (Vision capabilities).

## Required Actions

1. **Create/Identify Vision Controller**
   - Create a new `VisionUIController` or utilize an existing `OverlayController` inside `ui/controllers/`.
   - This controller should manage the interaction between the Vision UI prompts and the underlying OpenCV/template engines.

2. **Extract Methods from `app_gui.py`**
   - Locate `_scan_region`, `_add_template`, and `_manage_templates` inside `app_gui.py`.
   - Move the entire logic of these methods into the new Controller.
   - Adjust references to `self` to point to the correct UI dependencies (e.g., using `DialogService` for popups instead of direct Tkinter calls).

3. **Wire Up Handlers**
   - If these handlers were called by buttons or menus, update those UI components to call the new Controller methods instead.
   - Ensure that any state updates resulting from these vision handlers are propagated via `AppStateController` or `EventBus`.

## Acceptance Criteria
- `_scan_region`, `_add_template`, and `_manage_templates` are completely removed from `app_gui.App`.
- Vision scanning and template adding functionality still works flawlessly.
