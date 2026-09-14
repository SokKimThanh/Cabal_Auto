# Sprint 30 Phase 4 Prompt 023: Decouple Action and Status Bars

## Goal
Remove strict UI coupling and dependencies on the `App` class from `ActionBarView` and `StatusBarView`.

## Details
- Refactor `ActionBarView` and `StatusBarView` so they accept specific dependencies (e.g., `AppStateController`, `HuntController`, `TaskScheduler`) instead of taking the whole `app` God Class as an argument.
- Update `app_gui.py` to pass only these specific controllers during instantiation.
- Any actions triggered from these bars (like language changes `on_language_change` or manual scanning) should emit events via `EventBus` or call domain-specific controllers, not methods on `App`.

## Risks and Things to Avoid
- **Avoid referencing `self.app` inside Action and Status bars.**
- **Risk:** Circular dependencies if the newly injected Controllers attempt to reference the Bars back.
- **Risk:** UI updates for scanning status or language changes might freeze or desync if the EventBus listener is not attached on the main Tkinter thread.

## Acceptance Criteria
- `ui/components/action_bar_view.py` and `ui/components/status_bar_view.py` do not access `self.app`.
- UI updates triggered by these components correctly propagate through state management and controllers.
- `pylint` scores for modified files remain strictly at 10.0.
