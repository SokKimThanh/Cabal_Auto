# Sprint 30: Refactor Debt Technical - Fix Integration Tests Fragility
**File:** `sprint30-prompt-013-fix-integration-tests.md`
**Previous Context:** `sprint30-prompt-re-excecute-order.md` (Issue #3)
**Estimated Time:** < 45 minutes

## 1. Title & Objective
**Title:** Fix Test Fragility and OpenCV Dependency in Integration Tests
**Objective:** Resolve the broken integration tests (specifically `test_orchestrator_loop.py`). Fix the missing `opencv-python` dependency in the test environment, remove dummy `assert True` statements, and implement reliable assertion logic based on Mock call counts.

## 2. Context
Prompt 004 extracted the `SkillCasterService`, which successfully decoupled business logic from the UI. However, it severely broke the integration tests for the `HuntOrchestrator` thread loop. The tests are currently failing because `opencv-python` is missing in the testing CI, and the assertions were temporarily replaced with `assert True` to bypass fragility.

## 3. Files to Modify
- `requirements.txt` (or test requirements file)
- `tests/integration/test_orchestrator_loop.py`

## 4. Detailed Implementation Guide

### Step 4.1: Fix Test Dependencies
Ensure `opencv-python` (or `opencv-python-headless` for CI environments) is explicitly listed in `requirements.txt` or a dedicated `requirements-test.txt`.

### Step 4.2: Remove `assert True`
Open `tests/integration/test_orchestrator_loop.py` and remove any dummy `assert True` statements that were added during Sprint 30 Prompt 004.

### Step 4.3: Implement Robust Mock Assertions
Instead of trying to monkeypatch the exact internal state of the `HuntOrchestrator` using complex sequence loops, leverage `unittest.mock.MagicMock`.
- Mock the callback functions injected into `HuntOrchestrator` (e.g., `try_cast_skills_mock`, `locate_target_mock`).
- Start the orchestrator thread, wait for a fixed, very short duration (using mocked time if possible, or `time.sleep` as a last resort).
- Stop the orchestrator.
- Assert that the mock callbacks were called the expected number of times using `try_cast_skills_mock.assert_called()` or `call_count > 0`.

## 5. Acceptance Criteria
- [ ] Running `pytest` does not throw `ModuleNotFoundError: No module named 'cv2'`.
- [ ] `test_orchestrator_loop.py` contains no `assert True` statements.
- [ ] Integration tests pass reliably without race conditions.
