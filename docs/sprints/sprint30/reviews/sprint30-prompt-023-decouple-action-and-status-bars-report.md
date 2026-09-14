# Review Prompt 023: Decouple Action and Status Bars

## Verification Steps
1. Inspect `ui/components/action_bar_view.py` and `ui/components/status_bar_view.py` to ensure they no longer rely on `self.app`.
2. Verify that these views now accept specific dependencies (like `AppStateController`, `HuntController`) via their constructors.
3. Confirm that events triggered from these bars (e.g., language change, manual scan) emit via `EventBus` or direct controller calls.
4. Run the app and verify the UI updates (language switches, status changes) still propagate seamlessly.

## Checklist
- [ ] `self.app` dependencies removed from ActionBar and StatusBar.
- [ ] Dependencies properly injected via constructor.
- [ ] Events triggered using `EventBus` or Controllers.
- [ ] UI updates function without regressions.
