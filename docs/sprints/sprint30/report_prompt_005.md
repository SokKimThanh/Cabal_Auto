# Report: Update Downstream Consumers for State Encapsulation (Prompt 005)

## 1. Overview
This report analyzes the current state of the codebase against the objectives and acceptance criteria defined in `docs/sprints/sprint30/prompt-refactor-debt-technical/sprint30-prompt-005-update-consumers.md`.

## 2. Acceptance Criteria Evaluation

### [x] Codebase search for `app.monster_select_var` and similar old bindings yields zero results.
**Status: Pass**
Extensive codebase searches using `grep` confirm that legacy primitive variables and legacy tkinter vars targeted in previous prompts (like `app.monster_select_var`, `app.click_running`, `app.hunt_selected`, `app.win_items`) have been successfully removed from direct `app` references.

### [ ] `app_gui.py` boots without crashing and successfully constructs the UI using the new encapsulated variables.
**Status: Partial / Technical Debt Identified**
While the specific legacy bindings are gone, the codebase is still heavily violating the "God Class" pattern by dynamically attaching **new** `tk.StringVar`, `tk.BooleanVar` and `tk.Listbox` instances directly to the `self.app` object inside various UI components.

**Examples of ongoing violations:**
- `ui/panels/monster_target_panel.py`:
  - Direct assignment: `self.app.monster_rotation_listbox = tk.Listbox(...)`
  - Direct assignment: `self.app.detected_monsters_listbox = tk.Listbox(...)`
  - Direct assignment: `self.app.monster_status_var = tk.StringVar()`
  - Direct assignment: `self.app.training_mode_hint_var = tk.StringVar()`
  - Directly mutating internal dict: `self.app.state_controller.ui_vars['target_policy'] = tk.StringVar(...)`
- `ui/tabs/hunt_tab.py`:
  - `self.app.hunt_mode_var = tk.StringVar(...)`
  - `self.app.target_key_var = tk.StringVar(...)`
  - `self.app.attack_press_var = tk.StringVar(...)`
  - (and 7 other `hunt_cfg` related variables)
- `ui/tabs/setup_tab.py`:
  - `self.app.global_hotkey_enabled_var = tk.BooleanVar(...)`
  - `self.app.setup_target_key_var = tk.StringVar(...)`
  - (and 9 other setup variables)

### [ ] Hunt functionalities function correctly with the new Service imports.
**Status: In Progress**
Functionalities rely on these UI components. Until the UI components correctly utilize `AppStateController.ui_vars` and `AppStateController.ui_widgets` rather than attaching widgets to `self.app`, the encapsulation is incomplete.

## 3. Next Steps / Action Plan
To fully satisfy the spirit of Prompt 005 (State Encapsulation) and prevent `App` from acting as a Service Locator, the following fixes will be applied:

1. **Centralize Variable Initialization:** All stray `tk.StringVar`, `tk.BooleanVar`, and Widget references (like `Listbox`) currently created in tabs and panels and assigned to `self.app` will be formally declared inside `AppStateController.__init__` within `self.ui_vars` and `self.ui_widgets`.
2. **Refactor Consumers:**
   - Change direct `self.app.xxx_var` assignments to use `self.app.state_controller.ui_vars["xxx"]` (for initialization) and getters/setters (for logic).
   - Change direct `self.app.xxx_listbox` assignments to use `self.app.state_controller.ui_widgets["xxx_listbox"]`.
   - Fix direct dictionary manipulation `self.app.state_controller.ui_vars['xxx'] = ...` to use standard instantiation and updating.
