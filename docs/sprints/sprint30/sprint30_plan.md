# Sprint 30: Technical Debt Refactoring (AppStateController)

## Overview
This sprint focuses on refactoring `ui/controllers/app_state_controller.py` to resolve critical architectural debt identified in `docs/ui_architecture_review.md`. Currently, this file violates the "Single Responsibility Principle" by leaking business logic (Hunt & Skill casting) and acts as an enabler for the "God Class" anti-pattern by dynamically attaching dozens of attributes to the root `Tk` app instance (`self.root`).

## Objectives
1. **Encapsulate State:** Move all variables currently attached to `self.root` (e.g., `app.click_running`, `app.hunt_selected`) into the `AppStateController` itself as explicit instance variables (`self.click_running`).
2. **Lifecycle Management:** Initialize all state variables explicitly in the `__init__` method.
3. **Remove "Service Locator" anti-pattern:** Eliminate heavy reliance on `getattr(app, ...)` and `hasattr(app, ...)`.
4. **Extract Business Logic:** Relocate specific hunt and skill algorithms (`_try_cast_skills`, `_validate_hunt_prerequisites`, `_hunt_locate_target`, `_hunt_from_ui`) to dedicated domain services, so the controller strictly manages UI State and Events.

## Execution Strategy
To minimize regression risks and adhere to the < 30-minute session constraint, the refactoring is broken down into the following execution prompts:

1. **`sprint30-prompt-001-encapsulate-simple-state.md`**: Move simple primitive/boolean application states to the controller.
2. **`sprint30-prompt-002-encapsulate-tkinter-vars.md`**: Refactor and group `tk.StringVar` and other UI widget bindings into managed dictionaries or data classes inside the controller.
3. **`sprint30-prompt-003-extract-hunt-logic.md`**: Extract Hunt Core logic (validation, locating targets) to external services.
4. **`sprint30-prompt-004-extract-skill-logic.md`**: Extract Skill logic (`_try_cast_skills`, `_prepare_skill_runtime`) to a runtime manager.
5. **`sprint30-prompt-005-update-consumers.md`**: Update the downstream UI classes (e.g., `app_gui.py`, frames) to consume the new `app.state_controller.property` format instead of the God Class `app.property` format.

All prompts are located in `docs/sprints/sprint30/prompt-refactor-debt-technical/`.