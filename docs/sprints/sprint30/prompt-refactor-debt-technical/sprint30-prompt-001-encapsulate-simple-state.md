# Sprint 30: Refactor Debt Technical - AppStateController
**File:** `sprint30-prompt-001-encapsulate-simple-state.md`
**Previous Context:** N/A (Initial Step)
**Estimated Time:** < 30 minutes

## 1. Title & Objective
**Title:** Encapsulate Simple State Variables in AppStateController
**Objective:** Stop attaching primitive application states (booleans, numbers, simple lists/dicts) to the `app` (`self.root`) instance. Move them to be explicit properties of the `AppStateController` itself to fix the "God Class" and "Component Lifecycle" anti-patterns.

## 2. Context
Currently, `ui/controllers/app_state_controller.py` executes lines like:
```python
self.root = root
app = root
app.click_running = False
app.hunt_thread = None
app.win_items = []
# etc...
```
This violates encapsulation. We need to define these as `self.click_running = False`, `self.hunt_thread = None`, etc., inside `__init__`.

## 3. Files to Modify
- `ui/controllers/app_state_controller.py`

## 4. Detailed Implementation Guide

### Step 4.1: Update `__init__`
In `ui/controllers/app_state_controller.py` inside `__init__`, modify the assignment of simple variables.
Find all instances of `app.XXX = YYY` where `YYY` is a simple type (bool, int, list, dict, None) and change them to `self.XXX = YYY`.

**Important Variables to convert in this pass:**
- `click_running`, `click_thread`, `hunt_thread`
- `win_items`, `hunt_selected`, `_skip_auto_bring`
- `_current_class_id`
- `_global_start_hotkey`, `_global_stop_hotkey`, `_global_library_hotkey`, `_global_vision_hotkey`, `_global_monster_hotkey`, `_hotkey_fallback_bound`, `_hotkey_import_diag`
- Phase 5: `_overlay_window`, `_overlay_enabled`, `_overlay_update_thread`, `_overlay_stop_event`
- Phase 7: `_vision_engine`, `_screen_capture`, `_bot_manager`, `_overlay_controller`
- `monster_selected_index`, `skill_selected_index`, `skill_preview_image`
- Preset state: `_active_preset_id`, `_preset_mode`, `skill_slots`, `_callbacks`, `_combo_mode_active`
- Simple UI caches: `skill_slot_vars`, `skill_slot_boxes`, `skill_slot_count`, `_image_refs`, `_tooltips`, `monster_template_working`, `monster_template_selected_index`, `_thumbnail_cache`

*Do not touch `tk.StringVar` or complex UI widget assignments (e.g. `app.monster_select_var`, `app.skill_listbox`) in this prompt. We will handle them in the next prompt.*

### Step 4.2: Update Getter/Setter Methods
Inside the `AppStateController` class methods (e.g., `set_current_class`, `load_preset_for_class`, `set_skill_slot`, etc.), update references from `self.root.XXX` or `app.XXX` to `self.XXX`.
- Pay special attention to `self.root._current_class_id`, `self.root._callbacks`, `self.root._combo_mode_active`.

## 5. Pitfalls & Notes
- Be careful with `app._callbacks` in `register_callback` and `_emit_event`. Change `self.root._callbacks` to `self._callbacks`.
- Do not modify how settings are written to `hunt_cfg` at this time (e.g., `self.root.hunt_cfg["last_active_class_id"]` can remain for now if `hunt_cfg` is heavily tied to the app).
- Ensure all properties exist on `self` immediately after `__init__` completes.

## 6. Acceptance Criteria
- [ ] No primitive state variables are attached to `app` or `self.root` in the `__init__` block (except UI Widgets/StringVars).
- [ ] Methods inside `AppStateController` correctly access `self.variable_name`.
- [ ] The app boots without crashing regarding these variables.