# Prompt 017: Move Training Mode UI Logic

## Objective
The `_update_training_mode_buttons` function in `app_gui.py` is nearly 100 lines long and manipulates UI widgets (`btn_add_monster`, `btn_move_up`, `btn_move_down`) that are actually instantiated inside `ui/panels/monster_target_panel.py`. This is zombie code that needs to be relocated to the panel.

## Tasks
1. **Move Logic to `MonsterTargetPanel`:**
   - In `ui/panels/monster_target_panel.py`, add a new method `update_training_mode_buttons()`.
   - Migrate the logic from `app_gui.py`'s `_update_training_mode_buttons` to this new method.
   - Adjust the widget references to point to the correct instances in the panel (e.g., `self.btn_add`, `self.btn_move_up`, `self.btn_move_down` instead of `self.app.btn_add_monster`).
2. **Setup Event Binding:**
   - In `MonsterTargetPanel.__init__`, bind to changes on the `training_mode` UI variable so that `update_training_mode_buttons()` is called automatically when the state changes.
   - Ensure the method also gets called during the panel's initialization to set the correct initial state.
3. **Clean up `app_gui.py`:**
   - Remove the `_update_training_mode_buttons` method from `app_gui.py` entirely.
   - Remove the fallback initializations like `self.btn_add_monster = None` from `app_gui.__init__`.
4. **Verify:**
   - Toggling training mode should still disable/enable the add and reorder buttons in the UI correctly.
