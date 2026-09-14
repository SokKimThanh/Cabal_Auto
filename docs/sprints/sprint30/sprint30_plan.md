# Sprint 30: Technical Debt Refactoring

## Overview
This sprint focuses on resolving critical architectural debt identified in `docs/ui_architecture_review.md`. The refactoring is split into multiple phases. Phase 1 stabilizes application state management to prevent regressions, Phase 2 breaks down the central God Class (`app_gui.py`), and Phase 3 deals with advanced cleanup of the `AppStateController` to strictly enforce MVC patterns.

## Phase 1: State Encapsulation (`AppStateController`)
The current controller violates the "Single Responsibility Principle" by leaking business logic and enables the "God Class" anti-pattern by dynamically attaching dozens of attributes to the root `Tk` app instance (`self.root`).

**Objectives:**
- Move all state variables into `AppStateController` properties.
- Initialize all state in `__init__`.
- Extract Hunt/Skill core logic to domain services.

**Execution Prompts (Sequential):**
1. **`sprint30-prompt-001-encapsulate-simple-state.md`**: Move simple primitive/boolean application states to the controller.
2. **`sprint30-prompt-002-encapsulate-tkinter-vars.md`**: Group `tk.StringVar` and widget bindings inside the controller.
3. **`sprint30-prompt-003-extract-hunt-logic.md`**: Extract Hunt Core logic (validation, locating targets) to services.
4. **`sprint30-prompt-004-extract-skill-logic.md`**: Extract Skill logic (`_try_cast_skills`) to a runtime manager.
5. **`sprint30-prompt-005-update-consumers.md`**: Update downstream classes to consume `app.state_controller.property`.

---

## Phase 2: Decomposing the God Class (`app_gui.py`)
`App` in `app_gui.py` is over 3000 lines, acting as a God Class that manages windows, state, UI creation, routing, and dialogs. This phase breaks it down into single-responsibility components.

**Objectives:**
- Decompose UI initialization into `AppShell`.
- Abstract navigation into a `NavigationController` (resolving Hardcoded View Registry).
- Isolate the Sidebar component.
- Centralize threaded tasks and timer loops.
- Isolate MessageBox/Dialog logic.

**Execution Prompts (Sequential):**
6. **`sprint30-prompt-006-app-gui-extract-shell.md`**: Extract root window setup, theme initialization, and UI grid zones into `AppShell`.
7. **`sprint30-prompt-007-app-gui-navigation.md`**: Extract the `_views` registry and screen switching logic into a `NavigationController`.
8. **`sprint30-prompt-008-app-gui-sidebar.md`**: Extract `_build_sidebar` into a standalone UI component.
9. **`sprint30-prompt-009-app-gui-dialog-service.md`**: Centralize scattered `messagebox` calls into a `DialogService`.
10. **`sprint30-prompt-010-app-gui-task-scheduler.md`**: Implement `TaskScheduler` / `TimerManager` to prevent memory leaks from unmanaged `self.after` and `Thread` calls.

---

## Post-Phase 1 Cleanup (Prompts 19-21)
While reviewing the initial God Class decomposition, several zombie methods and surface-level clutter were identified. These will be handled before or alongside Phase 2:
19. **`sprint30-prompt-019-clean-imports-and-fallback.md`**: Remove useless try/excepts and extract fallback UI components.
20. **`sprint30-prompt-020-move-hotkey-diagnostics.md`**: Move `_update_hotkey_diagnostics_ui` into `HotkeyController`.
21. **`sprint30-prompt-021-move-training-mode-buttons.md`**: Move `_update_training_mode_buttons` into `MonsterTargetPanel`.
## Phase 3: Advanced AppStateController Cleanup
Further analysis revealed lingering code smells in the `AppStateController`, specifically around UI leaks, missing component lifecycle initialization, and God Object tendencies regarding Preset Management and Config generation.

**Objectives:**
- Enforce strict 100% attribute initialization in `__init__`.
- Abstract hardcoded Magic Numbers/Strings into Constants and extract Hunt Config logic.
- Extract Skill Preset business logic to its own Controller.
- Remove all Tkinter Widget manipulation (`.config`) from the State Controller and use an Event-driven approach.

**Execution Prompts (Sequential):**
15. **`sprint30-prompt-015-clean-app-state-init.md`**: Fix Component Lifecycle by removing `getattr` and declaring all vars in `__init__`.
16. **`sprint30-prompt-016-extract-hunt-config-controller.md`**: Extract `build_hunt_config_from_state` into a separate controller and replace hardcoded configurations with constants.
17. **`sprint30-prompt-017-extract-skill-preset-controller.md`**: Extract preset management logic (like `load_preset_for_class`) into `SkillPresetController`.
18. **`sprint30-prompt-018-remove-ui-code-from-state.md`**: Remove UI leakage (calls to `.config` on Tkinter labels) and replace it with Event emission to fully comply with MVC/MVVM.

All prompts are located in `docs/sprints/sprint30/prompt-refactor-debt-technical/`.

## Risk Mitigation Summary (Auto-Updated)
Based on a thorough review of the current application state against the refactoring prompts, the following key risk areas have been identified and documented inside the individual prompts:
1. **State Preservation:** Heavy dynamic variable usage requires careful translation to dictionaries (e.g. `self.ui_vars`) and maintaining initialization order so downstream consumers do not crash.
2. **God Class Entanglement:** Business logic currently relies on direct UI variables or `app._t()` for translation. Breaking this requires injecting `i18n_t` and passing simple configurations instead of full `app` references.
3. **Tkinter Lifecycle:** Extracting UI components (`AppShell`, `SidebarComponent`, `DialogService`) carries risks related to garbage collection of images (icons), thread-safety for dialogs, and preserving grid layout geometries.
4. **Execution Blast Radius:** Updating downstream consumers (Prompt 005, 018) is highly sensitive. Thorough `grep` validations are mandatory.
