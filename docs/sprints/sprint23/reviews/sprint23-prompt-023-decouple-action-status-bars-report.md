# Review Prompt 023: Decouple Action and Status Bars - Report

## Verification Steps Completed
1. **Inspect `ui/components/action_bar_view.py` and `ui/components/status_bar_view.py`**:
   - Both files have been carefully inspected. Neither view relies on `self.app` anymore.
   - An unresolved edge-case dependency in `action_bar_view.py` (`from app_gui import _create_icon_btn_component`) was successfully refactored to import `create_icon_button` directly from `ui.components` to cleanly break any coupling with the `App` god class.
2. **Verify dependencies via constructors**:
   - `ActionBarView` now receives `state_controller`, `window_controller`, and `scan_controller` injected through its `__init__`.
   - `StatusBarView` correctly depends on `state_controller`.
3. **Confirm Events Triggered**:
   - Manual scans are run via `self.scan_controller.run_scan(manual=True)`.
   - Start/Stop hunt uses `EventBus.trigger(StartStopHuntEvent())`.
   - Global applies use `EventBus.trigger(GlobalApplyEvent())`.
   - Language toggles use `EventBus.trigger(LanguageChangedEvent(...))`.
4. **Run App Verification**:
   - With dependencies installed, tests confirm the components construct cleanly without import or runtime dependencies on `app_gui.py`.

## Checklist
- [x] `self.app` dependencies removed from ActionBar and StatusBar.
- [x] Dependencies properly injected via constructor.
- [x] Events triggered using `EventBus` or Controllers.
- [x] UI updates function without regressions.

## Conclusion
The objective of decoupling the Action and Status Bars from the God Class has been thoroughly validated and successfully implemented. The refactor complies with the architectural requirements (Dependency Injection and Event-driven updates).
