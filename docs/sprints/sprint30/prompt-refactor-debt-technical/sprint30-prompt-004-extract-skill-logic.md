# Sprint 30: Refactor Debt Technical - AppStateController
**File:** `sprint30-prompt-004-extract-skill-logic.md`
**Previous Context:** `sprint30-prompt-003-extract-hunt-logic.md`
**Estimated Time:** < 30 minutes

## 1. Title & Objective
**Title:** Extract Skill Cast Logic from AppStateController
**Objective:** Relocate the `_try_cast_skills`, `_prepare_skill_runtime`, and `_get_skill_runtime_object` methods into a proper `SkillManager` or `CastDeliveryManager`, completely removing them from the UI State Controller.

## 2. Context
The `AppStateController` currently manages active skill casting, timings, combos, and hardware backend integrations (e.g., `backend.tap()`). This is severe architectural debt, as a UI State controller should never interact with hardware input simulation or calculate cooldown timestamps.

## 3. Files to Modify
- `ui/controllers/app_state_controller.py`
- `lib/features/skills/cast_delivery.py` (or create `lib/features/skills/skill_caster_service.py`)

## 4. Detailed Implementation Guide

### Step 4.1: Create/Update Caster Service
Examine `lib/features/skills/cast_delivery.py` or similar files.
Create a class (e.g., `SkillCasterService` or integrate into `CastDeliveryManager`) that handles the logic currently residing in `_try_cast_skills`.

### Step 4.2: Move Methods
Move the following methods from `AppStateController` to the new service:
1. `_get_skill_runtime_object(self, cfg)`
2. `_prepare_skill_runtime(self, cfg)`
3. `_try_cast_skills(self, skill_runtime, now, target_active, attack_phase, skill_stats, backend)`

### Step 4.3: Refactor the Moved Methods
In their new home, these methods must not reference `self.root` or `app`.
Pass `combo_enabled`, `hunt_cfg`, and other necessary parameters explicitly into the methods or the service's constructor.
For example, the instantiation of `CabalComboDetector` should happen in the service, not attached to `self.combo_detector` on the `AppStateController`.

### Step 4.4: Cleanup Controller
Delete these methods entirely from `AppStateController`. The caller (likely `HuntOrchestrator` or similar background loop) should be updated to call the new `SkillCasterService` instead of `app.state_controller._try_cast_skills`. Note: Do not update callers in this prompt unless they are trivial; Prompt 05 handles downstream consumers.

## 5. Pitfalls & Notes
- Pay close attention to `self.skill_runtime_obj` and `self._last_combo_mode` which are dynamically assigned in `_try_cast_skills`. These states belong inside the `SkillCasterService`, not the UI state.
- Ensure `backend.tap` and `tap` imports remain intact in the new service file.

## 6. Acceptance Criteria
- [ ] `_try_cast_skills`, `_prepare_skill_runtime`, and `_get_skill_runtime_object` are removed from `AppStateController`.
- [ ] A dedicated service now handles skill casting without referencing `app` or `AppStateController`.
- [ ] No combo detector state (`self.combo_detector`) is stored in the UI State Controller.

## 7. Identified Risks & Current State Assessment (Auto-Updated)
**Current State Analysis:**
- `AppStateController` contains `_try_cast_skills`, `_prepare_skill_runtime`, and `_get_skill_runtime_object`.
- `_try_cast_skills` instantiates and stores `self.combo_detector` and heavily interacts with backend hardware APIs (`backend.tap` or `tap`).

**Identified Risks & Pitfalls:**
- **Lost Internal State:** `_try_cast_skills` dynamically stores `self.skill_runtime_obj` and `self._last_combo_mode` on the UI controller. When moving this to `SkillCasterService`, these states must be properly encapsulated as class variables of the new service, initialized in its constructor.
- **Hardware Integration Coupling:** The extracted `SkillCasterService` needs to properly receive or import the `backend` or `tap` inputs. The current UI controller relies on `app.bot_manager.screen_capture` for combo detection; this coupling needs to be untangled by injecting `bot_manager` or `screen_capture` via arguments to the service rather than accessing `app`.
- **Legacy Compatibility:** The current logic updates legacy dictionaries (e.g., `s["_last_cast"] = now`). Maintain this compatibility in the new service or clearly document why it is removed to prevent downstream hunt loops from breaking.
