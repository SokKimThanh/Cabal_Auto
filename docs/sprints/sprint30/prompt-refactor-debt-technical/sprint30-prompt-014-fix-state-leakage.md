# Sprint 30: Refactor Debt Technical - Fix State Leakage (Root Access)
**File:** `sprint30-prompt-014-fix-state-leakage.md`
**Previous Context:** `sprint30-prompt-re-excecute-order.md` (Issue #4)
**Estimated Time:** < 30 minutes

## 1. Title & Objective
**Title:** Fix State Leakage by Removing Root Access in AppStateController
**Objective:** Eliminate the remaining tight coupling where `AppStateController` uses `getattr(self.root, ...)` to fetch data, specifically for `hunt_orchestrator` and `skills`.

## 2. Context
Prompt 001 encapsulated simple states into `AppStateController`. However, a few minor leaks remain. The controller still reaches outside its bounds to read `self.root.hunt_orchestrator` to check if a hunt is running, and reads `self.root.skills` to fetch the skills list. State should flow inward, or be managed internally, not pulled from the UI Root window.

## 3. Files to Modify
- `ui/controllers/app_state_controller.py`
- `app_gui.py` (to update how these variables are passed or managed)

## 4. Detailed Implementation Guide

### Step 4.1: Fix `hunt_running` Dependency
Instead of `AppStateController` polling `getattr(self.root.hunt_orchestrator, "hunt_running", False)`, move the concept of "hunt is currently active" into the state controller itself (e.g., `self.is_hunting = False`).
When the user clicks "Start Hunt" in `HuntRunner` (or `HuntTab`), it should update this state variable via `self.state_controller.set_ui_var('is_hunting', True)`. The orchestrator can then sync with this state, or emit an event when it starts/stops.

### Step 4.2: Fix `skills` Dependency
Instead of fetching `getattr(self.root, "skills", [])`, the skills list should be managed by a dedicated service (e.g., `SkillService` or `SkillPresetController`).
Refactor the code so that `AppStateController` is initialized with the skills list, or queries it directly from the Database/Service layer, rather than relying on the UI window to hold the `skills` array.

## 5. Acceptance Criteria
- [ ] No occurrences of `getattr(self.root, "hunt_orchestrator"` in `AppStateController`.
- [ ] No occurrences of `getattr(self.root, "skills"` in `AppStateController`.
- [ ] The application operates normally, and the hunt start/stop mechanics work correctly.
