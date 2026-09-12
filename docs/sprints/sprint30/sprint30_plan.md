# Sprint 30: Technical Debt Refactoring

## Overview
This sprint focuses on resolving critical architectural debt identified in `docs/ui_architecture_review.md`. The refactoring is split into two mandatory, sequential phases. Phase 1 stabilizes application state management to prevent regressions, while Phase 2 breaks down the central God Class (`app_gui.py`).

**Important:** Phase 2 must not be started until Phase 1 is fully complete and verified.

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

All prompts are located in `docs/sprints/sprint30/prompt-refactor-debt-technical/`.